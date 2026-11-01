"""Step 4: Generate software requirements from ATRS records using baseline and grounded prompts.

Usage:
    python scripts/04_generate.py [--data data] [--prompts prompts]

Features:
- Runs two experimental prompting conditions per record:
    1. Baseline: 8-12 software requirements reflecting governance commitments.
    2. Grounded: strictly evidence-grounded requirements in 'The system shall' format,
       with single testable conditions and verbatim source evidence quotes.
- Resumable: caches raw LLM outputs in generations.jsonl; skips already-completed pairs.
- Robust JSON parsing: handles markdown code blocks, bracket extraction, and syntax anomalies.
- Automated evidence verification: compares grounded evidence quotes against the source text
  and labels them as 'exact', 'near', 'no', or 'none'.
- Exports parsed, verified requirements to data/requirements.csv.
"""
import os
import sys
import json
import re
import argparse
import pandas as pd

# Ensure project root is on sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from llm import call_llm


def normalize_text(text: str) -> str:
    """Normalize text for quote matching: lowercase, strip punctuation, collapse whitespace."""
    if not text:
        return ""
    text_clean = re.sub(r"[^\w\s]", " ", text.lower())
    return re.sub(r"\s+", " ", text_clean).strip()


def extract_trigrams(text: str) -> set:
    """Generate a set of word trigrams from normalized text."""
    words = normalize_text(text).split()
    if len(words) < 3:
        return {tuple(words)} if words else set()
    return {tuple(words[i : i + 3]) for i in range(len(words) - 2)}


def check_quote_match(quote: str, source_text: str) -> str:
    """Classify the match quality of an evidence quote against the source text.
    
    Returns:
        'none': Quote is missing or empty.
        'exact': Normalized quote is an exact substring of the normalized source.
        'near': Trigram overlap >= 80% (accounting for minor punctuation or truncation differences).
        'no': Quote fails substring match and has <80% trigram overlap.
    """
    if not quote or not str(quote).strip():
        return "none"

    norm_quote = normalize_text(quote)
    norm_source = normalize_text(source_text)

    if not norm_quote:
        return "none"

    # Exact normalized substring match
    if norm_quote in norm_source:
        return "exact"

    # N-gram overlap check (robust to slight variations in tokenization)
    quote_trigrams = extract_trigrams(quote)
    if not quote_trigrams:
        return "no"

    source_trigrams = extract_trigrams(source_text)
    overlap = len(quote_trigrams & source_trigrams) / len(quote_trigrams)

    if overlap >= 0.80:
        return "near"

    return "no"


def parse_llm_json(raw_text: str):
    """Robustly parse JSON array of requirements from raw LLM output."""
    if not raw_text or not raw_text.strip():
        return None

    cleaned = raw_text.strip()

    # Strip markdown code fences if present
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.I)
    cleaned = re.sub(r"\s*```$", "", cleaned)
    cleaned = cleaned.strip()

    # Attempt direct json parse
    try:
        parsed = json.loads(cleaned)
        if isinstance(parsed, list):
            return [x for x in parsed if isinstance(x, dict) and x.get("requirement")]
    except json.JSONDecodeError:
        pass

    # Extract outermost JSON array brackets [ ... ]
    match = re.search(r"\[\s*\{.*\}\s*\]", cleaned, flags=re.DOTALL)
    if match:
        snippet = match.group(0)
        try:
            parsed = json.loads(snippet)
            if isinstance(parsed, list):
                return [x for x in parsed if isinstance(x, dict) and x.get("requirement")]
        except json.JSONDecodeError:
            # Try removing trailing commas before closing braces/brackets
            fixed = re.sub(r",\s*([\]\}])", r"\1", snippet)
            try:
                parsed = json.loads(fixed)
                if isinstance(parsed, list):
                    return [x for x in parsed if isinstance(x, dict) and x.get("requirement")]
            except json.JSONDecodeError:
                pass

    # Salvage truncated JSON arrays up to the last complete object }
    last_brace = cleaned.rfind("}")
    if last_brace != -1 and "[" in cleaned:
        start_idx = cleaned.find("[")
        candidate_snippet = cleaned[start_idx : last_brace + 1].strip().rstrip(",") + "\n]"
        try:
            parsed = json.loads(candidate_snippet)
            if isinstance(parsed, list):
                valid = [x for x in parsed if isinstance(x, dict) and x.get("requirement")]
                if valid:
                    return valid
        except json.JSONDecodeError:
            fixed_cand = re.sub(r",\s*([\]\}])", r"\1", candidate_snippet)
            try:
                parsed = json.loads(fixed_cand)
                if isinstance(parsed, list):
                    valid = [x for x in parsed if isinstance(x, dict) and x.get("requirement")]
                    if valid:
                        return valid
            except json.JSONDecodeError:
                pass

    return None


def generate_requirements(data_dir: str = config.DATA_DIR, prompts_dir: str = "prompts") -> pd.DataFrame:
    """Run generation for all records and conditions, caching in generations.jsonl."""
    records_csv = os.path.join(data_dir, "records.csv")
    texts_dir = os.path.join(data_dir, "texts")
    cache_path = os.path.join(data_dir, "generations.jsonl")
    requirements_csv = os.path.join(data_dir, "requirements.csv")

    if not os.path.exists(records_csv):
        raise FileNotFoundError(
            f"Records file not found at: {records_csv}\n"
            "Please run Step 3 (scripts/03_completeness.py) before Step 4."
        )

    # Load prompt templates
    conditions = ["baseline", "grounded"]
    prompt_templates = {}
    for cond in conditions:
        prompt_file = os.path.join(prompts_dir, f"{cond}.txt")
        if not os.path.exists(prompt_file):
            raise FileNotFoundError(f"Prompt template missing: {prompt_file}")
        with open(prompt_file, "r", encoding="utf-8") as f:
            prompt_templates[cond] = f.read()

    records_df = pd.read_csv(records_csv)
    print(f"Loaded {len(records_df)} records for generation.")

    # Load cached generations to support resuming
    done_set = set()
    if os.path.exists(cache_path):
        with open(cache_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        obj = json.loads(line)
                        done_set.add((obj["record_id"], obj["condition"]))
                    except Exception:
                        pass
        print(f"Resuming: found {len(done_set)} cached generations in {cache_path}")

    # Generate missing records
    total_calls = len(records_df) * len(conditions)
    call_idx = len(done_set)

    with open(cache_path, "a", encoding="utf-8") as cache_file:
        for _, rec in records_df.iterrows():
            rec_id = str(rec["record_id"]).strip()
            text_path = os.path.join(texts_dir, f"{rec_id}.txt")

            if not os.path.exists(text_path):
                print(f"Warning: Text file for {rec_id} missing at {text_path}, skipping.")
                continue

            with open(text_path, "r", encoding="utf-8") as f:
                source_text = f.read()[: config.MAX_SOURCE_CHARS]

            for cond in conditions:
                if (rec_id, cond) in done_set:
                    continue

                call_idx += 1
                print(f"[{call_idx}/{total_calls}] Calling LLM for {rec_id} [{cond}]...")
                prompt = prompt_templates[cond].replace("{record}", source_text)

                raw_response = call_llm(prompt)

                record_entry = {
                    "record_id": rec_id,
                    "condition": cond,
                    "raw": raw_response,
                }
                cache_file.write(json.dumps(record_entry) + "\n")
                cache_file.flush()
                done_set.add((rec_id, cond))

    # Parse all cached generations and perform quote verification
    print("\nParsing cached generations and verifying evidence quotes...")
    parsed_rows = []
    unparsed_count = 0

    with open(cache_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            entry = json.loads(line)
            rec_id = entry["record_id"]
            cond = entry["condition"]
            raw_text = entry["raw"]

            items = parse_llm_json(raw_text)
            if items is None:
                print(f"WARNING: Could not parse JSON for record {rec_id} ({cond})")
                unparsed_count += 1
                continue

            text_path = os.path.join(texts_dir, f"{rec_id}.txt")
            source_content = ""
            if os.path.exists(text_path):
                with open(text_path, "r", encoding="utf-8") as tf:
                    source_content = tf.read()

            cond_code = "B" if cond == "baseline" else "G"
            for k, itm in enumerate(items, 1):
                req_text = str(itm.get("requirement", "")).strip()
                quote_text = str(itm.get("evidence_quote", "")).strip() if cond == "grounded" else ""

                quote_match = check_quote_match(quote_text, source_content) if cond == "grounded" else "n/a"

                parsed_rows.append({
                    "record_id": rec_id,
                    "condition": cond,
                    "req_id": f"{rec_id}-{cond_code}{k:02d}",
                    "requirement": req_text,
                    "evidence_quote": quote_text,
                    "auto_quote_match": quote_match,
                })

    df_reqs = pd.DataFrame(parsed_rows)
    df_reqs.to_csv(requirements_csv, index=False)

    print(f"\nSuccessfully parsed {len(df_reqs)} requirements ({unparsed_count} unparseable entries).")
    print(f"Saved requirements to: {requirements_csv}")
    print("\nRequirements per condition:")
    print(df_reqs["condition"].value_counts().to_string())

    if "grounded" in df_reqs["condition"].values:
        grounded_sub = df_reqs[df_reqs["condition"] == "grounded"]
        print("\nAutomated quote check breakdown for Grounded requirements:")
        print(grounded_sub["auto_quote_match"].value_counts(normalize=True).mul(100).round(1).to_string())

    return df_reqs


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Step 4: Generate requirements via baseline and grounded prompts.")
    parser.add_argument(
        "--data",
        default=config.DATA_DIR,
        help=f"Data directory containing records.csv and texts/ (defaults to {config.DATA_DIR})",
    )
    parser.add_argument(
        "--prompts",
        default="prompts",
        help="Directory containing baseline.txt and grounded.txt (defaults to prompts)",
    )
    args = parser.parse_args()

    try:
        generate_requirements(data_dir=args.data, prompts_dir=args.prompts)
    except FileNotFoundError as err:
        print(f"\n[INFO] {err}\n")
        sys.exit(1)
