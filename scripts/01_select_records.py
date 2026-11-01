"""Step 1: Sample candidate ATRS records from the metadata index CSV.

Usage:
    python scripts/01_select_records.py [path/to/atrs_records.csv]

Detects column names flexibly (publisher, tool name, date, URL), drops duplicates,
randomly samples N_CANDIDATES records with SEED, and assigns record IDs (R001...).
Saves output to data/candidates.csv.
"""
import os
import sys
import json
import argparse
import pandas as pd

# Ensure project root is on sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config


def find_col(df: pd.DataFrame, *needles: str) -> str:
    """Find the first column name that contains any of the given substrings (case-insensitive)."""
    for needle in needles:
        for col in df.columns:
            if needle.lower() in col.lower():
                return col
    return None


def select_records(csv_path: str, output_path: str = None) -> pd.DataFrame:
    """Read ATRS metadata, select candidate records, and assign unique record IDs."""
    if not os.path.exists(csv_path):
        raise FileNotFoundError(
            f"ATRS metadata file not found at: {csv_path}\n"
            "Please download 'atrs_records.csv' or 'atrs_records.json' from the UK algorithmic transparency repository "
            "and place it in data/, or pass the path as a command-line argument."
        )

    print(f"Reading ATRS metadata from: {csv_path}")
    if csv_path.lower().endswith(".json"):
        with open(csv_path, "r", encoding="utf-8") as f:
            jdata = json.load(f)
        raw_df = pd.DataFrame(jdata["records"] if isinstance(jdata, dict) and "records" in jdata else jdata)
    else:
        raw_df = pd.read_csv(csv_path)
    print(f"Loaded {len(raw_df)} raw rows. Columns detected: {list(raw_df.columns)}")

    # Detect key columns
    body_col = find_col(raw_df, "publisher", "body", "organisation", "organization", "dept")
    tool_col = find_col(raw_df, "tool", "name", "title", "algorithm", "system")
    url_col = find_col(raw_df, "url", "link", "web", "source")
    date_col = find_col(raw_df, "date", "published", "updated", "created")

    if not url_col:
        raise ValueError(f"Could not identify a URL column in metadata. Columns: {list(raw_df.columns)}")
    if not tool_col:
        raise ValueError(f"Could not identify a Tool/Name column in metadata. Columns: {list(raw_df.columns)}")
    if not body_col:
        print("Warning: Could not identify Publisher/Body column; using 'Unknown' default.")

    print(f"Mapped columns -> Publisher: '{body_col}', Tool: '{tool_col}', URL: '{url_col}', Date: '{date_col}'")

    # Build standardized dataframe
    clean_df = pd.DataFrame({
        "publisher": raw_df[body_col] if body_col else "Unknown",
        "tool": raw_df[tool_col],
        "url": raw_df[url_col],
        "date": raw_df[date_col] if date_col else "",
    })

    # Drop rows without URL and drop duplicate URLs
    initial_count = len(clean_df)
    clean_df = clean_df.dropna(subset=["url"]).copy()
    clean_df["url"] = clean_df["url"].astype(str).str.strip()
    clean_df = clean_df[clean_df["url"].str.startswith("http")].drop_duplicates(subset=["url"]).reset_index(drop=True)
    print(f"Filtered {initial_count} -> {len(clean_df)} records with valid, unique URLs.")

    # Randomly sample candidates
    n_sample = min(config.N_CANDIDATES, len(clean_df))
    sampled = clean_df.sample(n=n_sample, random_state=config.SEED).reset_index(drop=True)

    # Assign deterministic record IDs: R001, R002, ...
    sampled.insert(0, "record_id", [f"R{i + 1:03d}" for i in range(len(sampled))])

    # Save to CSV
    target_path = output_path or os.path.join(config.DATA_DIR, "candidates.csv")
    os.makedirs(os.path.dirname(os.path.abspath(target_path)), exist_ok=True)
    sampled.to_csv(target_path, index=False)
    print(f"Successfully selected {len(sampled)} candidate records. Saved to: {target_path}")

    return sampled


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Step 1: Select ATRS candidate records from metadata index CSV.")
    parser.add_argument(
        "csv_path",
        nargs="?",
        default=os.path.join(config.DATA_DIR, "atrs_records.csv"),
        help="Path to ATRS metadata CSV (defaults to data/atrs_records.csv)",
    )
    parser.add_argument(
        "--out",
        default=os.path.join(config.DATA_DIR, "candidates.csv"),
        help="Output path for candidates.csv (defaults to data/candidates.csv)",
    )
    args = parser.parse_args()

    try:
        select_records(args.csv_path, args.out)
    except FileNotFoundError as err:
        print(f"\n[INFO] {err}\n")
        sys.exit(1)
