"""Step 5: Create blind annotation sheets for human evaluation.

Usage:
    python scripts/05_make_annotation_sheets.py [--data data]

Blinding Protocol:
- Shuffles requirements so conditions (baseline vs grounded) are completely interleaved.
- Hides prompting condition ('baseline' / 'grounded') and evidence quotes from the sheets.
- Assigns anonymized item IDs ('I0001', 'I0002', ...).
- Stores the mapping in a separate key file (annotation_key.csv) to be kept private from raters.
- Creates:
    - annotations_template_A.csv: All items (scored by Rater A).
    - annotations_template_B.csv: 20% random subset (scored independently by Rater B for Cohen's kappa).
"""
import os
import sys
import argparse
import pandas as pd

# Ensure project root is on sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config


def create_annotation_sheets(data_dir: str = config.DATA_DIR):
    """Generate blind annotation sheets and separate secret key."""
    requirements_csv = os.path.join(data_dir, "requirements.csv")
    key_csv = os.path.join(data_dir, "annotation_key.csv")
    template_a = os.path.join(data_dir, "annotations_template_A.csv")
    template_b = os.path.join(data_dir, "annotations_template_B.csv")

    if not os.path.exists(requirements_csv):
        raise FileNotFoundError(
            f"Requirements file not found at: {requirements_csv}\n"
            "Please run Step 4 (scripts/04_generate.py) before Step 5."
        )

    df_req = pd.read_csv(requirements_csv)
    print(f"Loaded {len(df_req)} requirements from {requirements_csv}")

    # Deterministic shuffle to interleave conditions and randomize presentation order
    shuffled = df_req.sample(frac=1.0, random_state=config.SEED).reset_index(drop=True)

    # Assign anonymized item identifiers: I0001, I0002, ...
    shuffled.insert(0, "item_id", [f"I{i + 1:04d}" for i in range(len(shuffled))])

    # 1. Save secret key (item_id -> true condition, req_id, record_id)
    key_cols = ["item_id", "record_id", "req_id", "condition"]
    available_key_cols = [c for c in key_cols if c in shuffled.columns]
    shuffled[available_key_cols].to_csv(key_csv, index=False)
    print(f"[SECRET] Saved unblinding key to: {key_csv} (keep hidden from raters)")

    # 2. Build blind evaluation sheet (NO condition, NO evidence_quote)
    blind_sheet = pd.DataFrame({
        "item_id": shuffled["item_id"],
        "record_id": shuffled["record_id"],
        "requirement": shuffled["requirement"],
        "source_file": shuffled["record_id"].apply(lambda r: f"texts/{r}.txt"),
        "clarity": "",          # Score 1-3
        "verifiability": "",    # Score 1-3
        "traceability": "",     # Score 0-2
        "unsupported": "",      # Score 0/1
        "notes": "",            # Optional rater notes
    })

    # Save Rater A template (100% of items)
    blind_sheet.to_csv(template_a, index=False)
    print(f"Saved Rater A template ({len(blind_sheet)} items) to: {template_a}")

    # Save Rater B template (20% subset for inter-rater reliability)
    n_subset = max(1, int(round(len(blind_sheet) * config.DOUBLE_ANNOTATE_FRACTION)))
    subset_b = blind_sheet.sample(n=n_subset, random_state=config.SEED).sort_values("item_id").reset_index(drop=True)
    subset_b.to_csv(template_b, index=False)
    print(f"Saved Rater B template ({len(subset_b)} items, {config.DOUBLE_ANNOTATE_FRACTION * 100:.0f}%) to: {template_b}")

    print("\nAnnotation Workflow:")
    print("1. Rater A opens annotations_template_A.csv, scores all items, and saves as data/annotations_A.csv")
    print("2. Rater B independently scores annotations_template_B.csv and saves as data/annotations_B.csv")
    print("3. Follow scoring guidelines in rubric.md strictly.")
    print("4. When complete, run Step 6 (scripts/06_analyze.py) to compute kappa, tests, tables, and figures.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Step 5: Create blind annotation templates for human raters.")
    parser.add_argument(
        "--data",
        default=config.DATA_DIR,
        help=f"Data directory containing requirements.csv (defaults to {config.DATA_DIR})",
    )
    args = parser.parse_args()

    try:
        create_annotation_sheets(data_dir=args.data)
    except FileNotFoundError as err:
        print(f"\n[INFO] {err}\n")
        sys.exit(1)
