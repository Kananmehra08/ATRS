"""Step 2: Download the full text of candidate ATRS records from gov.uk.

Usage:
    python scripts/02_fetch_texts.py [--data data]

Features:
- Polite 1-second delay between network requests to gov.uk servers
- Resumable: skips records whose clean text file already exists in data/texts/
- Cleans HTML using BeautifulSoup (removes nav, scripts, styles, headers, footers)
- Records fetch status ('ok', 'cached', 'FAILED: ...') into data/candidates.csv
"""
import os
import sys
import time
import argparse
import requests
from bs4 import BeautifulSoup
import pandas as pd

# Ensure project root is on sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config


USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (academic research; ATRS requirements study)"
UNWANTED_TAGS = ["script", "style", "nav", "header", "footer", "noscript", "svg", "form", "aside", "iframe"]


def clean_html(html_content: str) -> str:
    """Parse HTML content with BeautifulSoup and extract clean text."""
    soup = BeautifulSoup(html_content, "html.parser")

    # Remove non-content elements
    for tag in soup(UNWANTED_TAGS):
        tag.decompose()

    # Find main content container
    main_elem = soup.find("main") or soup.find("article") or soup.body or soup

    # Extract lines and clean excess whitespace
    raw_lines = main_elem.get_text("\n").splitlines()
    cleaned_lines = [line.strip() for line in raw_lines if line.strip()]

    return "\n".join(cleaned_lines)


def fetch_texts(data_dir: str = config.DATA_DIR, delay_seconds: float = 1.0) -> pd.DataFrame:
    """Fetch text for all candidate records listed in candidates.csv."""
    candidates_csv = os.path.join(data_dir, "candidates.csv")
    texts_dir = os.path.join(data_dir, "texts")

    if not os.path.exists(candidates_csv):
        raise FileNotFoundError(
            f"Candidates file not found at: {candidates_csv}\n"
            "Please run Step 1 (scripts/01_select_records.py) first."
        )

    os.makedirs(texts_dir, exist_ok=True)
    df = pd.read_csv(candidates_csv)
    print(f"Loaded {len(df)} candidate records from {candidates_csv}")

    headers = {"User-Agent": USER_AGENT}
    statuses = []
    total = len(df)

    for idx, row in df.iterrows():
        rec_id = str(row["record_id"]).strip()
        url = str(row["url"]).strip()
        text_path = os.path.join(texts_dir, f"{rec_id}.txt")

        # Resumable: skip already downloaded records
        if os.path.exists(text_path) and os.path.getsize(text_path) > 0:
            statuses.append("cached")
            continue

        print(f"[{idx + 1}/{total}] Fetching {rec_id}: {url} ...")
        try:
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()

            # Ensure proper encoding detection
            if response.encoding is None:
                response.encoding = "utf-8"

            clean_text = clean_html(response.text)

            with open(text_path, "w", encoding="utf-8") as f:
                f.write(clean_text)

            statuses.append("ok")
            print(f"       Saved {len(clean_text.split())} words to {text_path}")
        except Exception as exc:
            err_msg = f"FAILED: {type(exc).__name__}: {exc}"
            statuses.append(err_msg)
            print(f"       ERROR: {err_msg}")

        # Polite delay to respect gov.uk rate limits
        time.sleep(delay_seconds)

    df["fetch_status"] = statuses
    df.to_csv(candidates_csv, index=False)
    print(f"\nFetch complete. Summary of statuses:")
    print(df["fetch_status"].apply(lambda s: s.split(":")[0] if "FAILED" in s else s).value_counts())

    return df


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Step 2: Fetch full text of ATRS records from gov.uk.")
    parser.add_argument(
        "--data",
        default=config.DATA_DIR,
        help=f"Data directory containing candidates.csv (defaults to {config.DATA_DIR})",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=1.0,
        help="Polite delay between requests in seconds (defaults to 1.0)",
    )
    args = parser.parse_args()

    try:
        fetch_texts(data_dir=args.data, delay_seconds=args.delay)
    except FileNotFoundError as err:
        print(f"\n[INFO] {err}\n")
        sys.exit(1)
