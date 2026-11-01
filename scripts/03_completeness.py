"""Step 3: Compute completeness scores for fetched ATRS records, select final sample, and perform median split.

Usage:
    python scripts/03_completeness.py [--data data]

Completeness scoring formula (0.0 to 1.0):
    Score = 0.4 * section_coverage + 0.4 * length_ratio (capped at 2500 words) + 0.2 * placeholder_score
    - Section coverage: presence of standard ATRS governance sections
    - Length ratio: min(words / 2500, 1.0)
    - Placeholder penalty: penalizes boilerplate like 'n/a', 'to be confirmed', 'not applicable'

Selection:
    Drops records under MIN_WORDS (300 words).
    Selects N_FINAL (40) records evenly spaced across the completeness distribution.
    Splits into 'high' and 'low' groups at the median completeness score.
    Saves to data/records.csv.
"""
import os
import sys
import argparse
import numpy as np
import pandas as pd

# Ensure project root is on sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config


ATRS_SECTIONS = [
    "owner",
    "responsib",
    "description",
    "rationale",
    "scope",
    "decision",
    "data",
    "risk",
    "mitigation",
    "impact assessment",
    "human oversight",
    "technical",
    "performance",
    "bias",
    "fairness",
    "legal",
    "contact",
]

PLACEHOLDER_PHRASES = [
    "not applicable",
    "n/a",
    "not yet",
    "to be completed",
    "not provided",
    "no information",
    "none",
    "tbc",
    "to be confirmed",
]


def score_record_completeness(text: str):
    """Compute words, section coverage, placeholder ratio, and composite completeness score."""
    lowered = text.lower()
    lines = [l.strip(" .:\t\r") for l in lowered.splitlines() if l.strip()]
    words = len(lowered.split())

    # 40% section coverage: fraction of standard ATRS section keywords present in the text
    matched_sections = sum(1 for section in ATRS_SECTIONS if section in lowered)
    section_coverage = matched_sections / len(ATRS_SECTIONS)

    # 40% length ratio: capped at 2500 words
    length_ratio = min(words / 2500.0, 1.0)

    # 20% placeholder penalty: frequency of empty / boilerplate entries
    ph_count = sum(
        1 for line in lines
        if any(line == ph or line.startswith(f"{ph} ") or line.startswith(f"{ph}:") for ph in PLACEHOLDER_PHRASES)
    )
    ph_ratio = ph_count / max(len(lines), 1)
    placeholder_score = max(0.0, 1.0 - min(ph_ratio * 5.0, 1.0))

    # Overall composite completeness score
    completeness = 0.4 * section_coverage + 0.4 * length_ratio + 0.2 * placeholder_score

    return words, section_coverage, ph_ratio, completeness


def process_completeness(data_dir: str = config.DATA_DIR) -> pd.DataFrame:
    """Read candidates, score text files, filter by word count, and select final sample."""
    candidates_csv = os.path.join(data_dir, "candidates.csv")
    texts_dir = os.path.join(data_dir, "texts")
    output_csv = os.path.join(data_dir, "records.csv")

    if not os.path.exists(candidates_csv):
        raise FileNotFoundError(
            f"Candidates file not found at: {candidates_csv}\n"
            "Please run Steps 1 and 2 before Step 3."
        )

    candidates = pd.read_csv(candidates_csv)
    print(f"Loaded {len(candidates)} candidates from {candidates_csv}")

    scored_rows = []
    short_records = 0
    missing_texts = 0

    for _, row in candidates.iterrows():
        rec_id = str(row["record_id"]).strip()
        text_file = os.path.join(texts_dir, f"{rec_id}.txt")

        if not os.path.exists(text_file) or os.path.getsize(text_file) == 0:
            missing_texts += 1
            continue

        with open(text_file, "r", encoding="utf-8") as f:
            content = f.read()

        words, cov, ph_ratio, score = score_record_completeness(content)

        if words < config.MIN_WORDS:
            short_records += 1
            continue

        record_dict = row.to_dict()
        record_dict.update({
            "words": words,
            "section_coverage": round(cov, 4),
            "placeholder_ratio": round(ph_ratio, 4),
            "completeness": round(score, 4),
        })
        scored_rows.append(record_dict)

    print(f"Text check: {len(scored_rows)} passed (>= {config.MIN_WORDS} words), "
          f"{short_records} dropped (too short), {missing_texts} missing text files.")

    if not scored_rows:
        raise ValueError("No records passed the completeness and minimum word count criteria.")

    df_scored = pd.DataFrame(scored_rows).sort_values("completeness").reset_index(drop=True)

    # Evenly space across the completeness spectrum to ensure representation of both extremes
    if len(df_scored) > config.N_FINAL:
        indices = np.linspace(0, len(df_scored) - 1, config.N_FINAL).round().astype(int)
        df_final = df_scored.iloc[indices].reset_index(drop=True)
        print(f"Sampled {config.N_FINAL} records evenly spaced from {len(df_scored)} qualified candidates.")
    else:
        df_final = df_scored
        print(f"Retained all {len(df_final)} qualified records (fewer than N_FINAL={config.N_FINAL}).")

    # Median split into 'high' and 'low' completeness groups
    median_val = df_final["completeness"].median()
    df_final["group"] = np.where(df_final["completeness"] >= median_val, "high", "low")

    os.makedirs(os.path.dirname(os.path.abspath(output_csv)), exist_ok=True)
    df_final.to_csv(output_csv, index=False)

    print(f"\nFinal dataset saved to: {output_csv}")
    print(f"Total records: {len(df_final)} (Completeness range: {df_final.completeness.min():.3f} - {df_final.completeness.max():.3f})")
    print(f"Median completeness: {median_val:.3f}")
    print("Group distribution:")
    print(df_final["group"].value_counts().to_string())

    return df_final


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Step 3: Score record completeness and select final sample.")
    parser.add_argument(
        "--data",
        default=config.DATA_DIR,
        help=f"Data directory containing candidates.csv and texts/ (defaults to {config.DATA_DIR})",
    )
    args = parser.parse_args()

    try:
        process_completeness(data_dir=args.data)
    except FileNotFoundError as err:
        print(f"\n[INFO] {err}\n")
        sys.exit(1)
