"""Generate synthetic demonstration data to test Steps 5 and 6 without requiring internet access or an API key.

Usage:
    python scripts/make_demo_data.py [--data demo_data]

Generates:
1. demo_data/texts/R001.txt ... R040.txt (Synthetic ATRS records with governance sections)
2. demo_data/records.csv (Completeness scores, median split into high/low groups)
3. demo_data/requirements.csv (Synthetic baseline & grounded requirements with quotes)
4. demo_data/annotation_key.csv (Mapping item_id -> condition, record_id, req_id)
5. demo_data/annotations_A.csv (Complete simulated ratings by Rater A)
6. demo_data/annotations_B.csv (20% simulated ratings by Rater B for Cohen's kappa)
7. demo_data/annotations_template_A.csv & template_B.csv (Blank sheets for testing Step 5)

NOTE: This is synthetic test data designed purely to validate pipeline execution.
Never report synthetic figures as empirical findings in the research manuscript.
"""
import os
import sys
import argparse
import numpy as np
import pandas as pd

# Ensure project root is on sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config


SAMPLE_REQUIREMENT_TEMPLATES = [
    ("The system shall log all risk-assessment scoring decisions with an automated timestamp and unique transaction ID.",
     "all risk-assessment scoring decisions are logged with an automated timestamp and unique transaction ID"),
    ("The system shall provide human caseworkers with an interactive override mechanism before any automated sanction is finalised.",
     "caseworkers retain the ability to override automated recommendations prior to final sanctions"),
    ("The system shall evaluate classification parity across demographic protected characteristics on a quarterly schedule.",
     "demographic classification parity is evaluated on a quarterly basis by the quality assurance team"),
    ("The system shall automatically redact personally identifiable data fields prior to exporting model telemetry to central analytics.",
     "telemetry data is stripped of direct personal identifiers before transmission to central storage"),
    ("The system shall display plain-language explanatory rationale for confidence score calculations to operational users.",
     "operational staff can view plain-language explanations of model confidence factors"),
    ("The system shall enforce role-based access control requiring two-factor authentication for retraining dataset modifications.",
     "changes to training datasets require dual-authorization and multi-factor authentication"),
    ("The system shall retain comprehensive model input-output audit trails for a minimum retention duration of seven years.",
     "audit logs and inference records are retained in secure storage for seven years"),
    ("The system shall generate automated alerts when model prediction distribution drift exceeds five percentage points.",
     "monitoring pipelines flag statistical distribution drift exceeding five percent"),
    ("The system shall allow service users to request human review of algorithmic tiering decisions via a dedicated web portal.",
     "citizens may request human review of automated tiering through the online service"),
    ("The system shall securely purge inference feature caches within 24 hours of decision confirmation.",
     "temporary feature caches are automatically cleared within 24 hours of processing"),
]

SAMPLE_SECTION_HEADERS = [
    "1. Organisational Owner and Responsibility",
    "2. Algorithmic Tool Description and Operational Scope",
    "3. Decision-Making Context and Legal Rationale",
    "4. Training Data and Model Technical Specification",
    "5. Risk Assessment and Impact Assessment Findings",
    "6. Bias, Fairness, and Performance Monitoring",
    "7. Human Oversight and Appeal Mechanisms",
    "8. Data Protection and Contact Details",
]


def create_demo_data(target_dir: str = "demo_data", n_records: int = config.N_FINAL, seed: int = config.SEED):
    """Generate complete synthetic dataset for pipeline validation."""
    os.makedirs(target_dir, exist_ok=True)
    texts_dir = os.path.join(target_dir, "texts")
    os.makedirs(texts_dir, exist_ok=True)

    rng = np.random.default_rng(seed)

    print(f"Creating synthetic demonstration data in: {target_dir}")

    # 1. Generate synthetic ATRS record texts & records.csv
    records = []
    for i in range(1, n_records + 1):
        rec_id = f"R{i:03d}"
        comp_val = 0.25 + 0.65 * ((i - 1) / max(1, n_records - 1))  # Evenly spaced completeness 0.25 - 0.90
        comp_val = round(float(comp_val + rng.normal(0, 0.02)), 3)
        comp_val = float(np.clip(comp_val, 0.20, 0.95))

        # Generate mock text
        n_words = int(400 + comp_val * 2000)
        text_lines = [f"UK Algorithmic Transparency Record: {rec_id} - Automated Public Service Assessment System", ""]
        for header in SAMPLE_SECTION_HEADERS:
            text_lines.append(header)
            text_lines.append(f"This section outlines operational commitments for {rec_id}.")
            for _, quote in SAMPLE_REQUIREMENT_TEMPLATES[:3]:
                if rng.random() < comp_val:
                    text_lines.append(f"In accordance with governance standards, {quote}.")
            text_lines.append("")

        while sum(len(line.split()) for line in text_lines) < n_words:
            text_lines.append("Additional operational guidelines stipulate continuous monitoring and adherence to UK public sector standards.")

        full_text = "\n".join(text_lines)
        with open(os.path.join(texts_dir, f"{rec_id}.txt"), "w", encoding="utf-8") as f:
            f.write(full_text)

        records.append({
            "record_id": rec_id,
            "publisher": f"Department for Public Services {i % 5 + 1}",
            "tool": f"Algorithmic Decision Support System {rec_id}",
            "url": f"https://www.gov.uk/government/publications/atrs-{rec_id.lower()}",
            "date": "2024-06-15",
            "words": len(full_text.split()),
            "section_coverage": round(min(1.0, 0.5 + 0.5 * comp_val), 3),
            "placeholder_ratio": round(max(0.01, 0.12 * (1.0 - comp_val)), 3),
            "completeness": comp_val,
        })

    df_records = pd.DataFrame(records).sort_values("completeness").reset_index(drop=True)
    median_comp = df_records["completeness"].median()
    df_records["group"] = np.where(df_records["completeness"] >= median_comp, "high", "low")
    df_records.to_csv(os.path.join(target_dir, "records.csv"), index=False)
    print(f"  [OK] Generated {len(df_records)} records in records.csv and mock texts in texts/")

    # 2. Generate requirements.csv for baseline and grounded conditions
    req_rows = []
    comp_map = df_records.set_index("record_id")["completeness"].to_dict()

    for _, rec in df_records.iterrows():
        rec_id = rec["record_id"]
        c_val = comp_map[rec_id]

        for cond in ["baseline", "grounded"]:
            code = "B" if cond == "baseline" else "G"
            n_reqs = rng.integers(8, 13)

            for k in range(1, n_reqs + 1):
                tmpl_req, tmpl_quote = SAMPLE_REQUIREMENT_TEMPLATES[(k - 1) % len(SAMPLE_REQUIREMENT_TEMPLATES)]

                if cond == "baseline":
                    # Baseline sometimes creates vague or non-shall requirements
                    if rng.random() < 0.35:
                        req_text = tmpl_req.replace("The system shall ", "The tool should provide adequate ")
                    else:
                        req_text = tmpl_req
                    evidence = ""
                    quote_match = "n/a"
                else:
                    req_text = tmpl_req
                    evidence = tmpl_quote
                    p_exact = 0.70 + 0.20 * c_val
                    p_near = 0.15
                    r_val = rng.random()
                    if r_val < p_exact:
                        quote_match = "exact"
                    elif r_val < p_exact + p_near:
                        quote_match = "near"
                    else:
                        quote_match = "no"

                req_rows.append({
                    "record_id": rec_id,
                    "condition": cond,
                    "req_id": f"{rec_id}-{code}{k:02d}",
                    "requirement": req_text,
                    "evidence_quote": evidence,
                    "auto_quote_match": quote_match,
                })

    df_reqs = pd.DataFrame(req_rows)
    df_reqs.to_csv(os.path.join(target_dir, "requirements.csv"), index=False)
    print(f"  [OK] Generated {len(df_reqs)} requirements in requirements.csv")

    # 3. Generate blind annotation key & templates using exact same seed as 05_make_annotation_sheets
    shuffled = df_reqs.sample(frac=1.0, random_state=seed).reset_index(drop=True)
    shuffled.insert(0, "item_id", [f"I{i + 1:04d}" for i in range(len(shuffled))])

    shuffled[["item_id", "record_id", "req_id", "condition"]].to_csv(
        os.path.join(target_dir, "annotation_key.csv"), index=False
    )
    print("  [OK] Generated annotation_key.csv")

    blind_sheet = pd.DataFrame({
        "item_id": shuffled["item_id"],
        "record_id": shuffled["record_id"],
        "requirement": shuffled["requirement"],
        "source_file": shuffled["record_id"].apply(lambda r: f"texts/{r}.txt"),
        "clarity": "",
        "verifiability": "",
        "traceability": "",
        "unsupported": "",
        "notes": "",
    })
    blind_sheet.to_csv(os.path.join(target_dir, "annotations_template_A.csv"), index=False)
    n_sub = max(1, int(round(len(blind_sheet) * config.DOUBLE_ANNOTATE_FRACTION)))
    subset_b = blind_sheet.sample(n=n_sub, random_state=seed).sort_values("item_id").reset_index(drop=True)
    subset_b.to_csv(os.path.join(target_dir, "annotations_template_B.csv"), index=False)
    print("  [OK] Generated blank annotation templates A and B")

    # 4. Generate realistic human annotations (Rater A and Rater B)
    # Reflects hypotheses:
    # Grounded -> higher clarity & verifiability, higher traceability, lower unsupported rate
    # High completeness -> higher quality, lower unsupported rate
    def sample_rater_scores(row, noise=0.0):
        is_grounded = (row["condition"] == "grounded")
        c_score = comp_map[row["record_id"]]

        # Clarity (1-3)
        mu_cl = 2.0 + (0.5 if is_grounded else 0.0) + 0.5 * (c_score - 0.5) + noise
        cl = int(np.clip(round(rng.normal(mu_cl, 0.45)), 1, 3))

        # Verifiability (1-3)
        mu_ve = 1.8 + (0.6 if is_grounded else 0.0) + 0.6 * (c_score - 0.5) + noise
        ve = int(np.clip(round(rng.normal(mu_ve, 0.45)), 1, 3))

        # Traceability (0-2)
        mu_tr = 0.8 + (0.9 if is_grounded else 0.0) + 0.7 * (c_score - 0.5) + noise
        tr = int(np.clip(round(rng.normal(mu_tr, 0.50)), 0, 2))

        # Unsupported (0/1)
        p_un = (0.07 if is_grounded else 0.35) - 0.20 * (c_score - 0.5) + noise
        p_un = float(np.clip(p_un, 0.02, 0.85))
        un = int(rng.random() < p_un)

        # Enforce logical consistency: if traceability is 0, probability of unsupported is high
        if tr == 0 and rng.random() < 0.90:
            un = 1

        return cl, ve, tr, un

    scores_a = []
    for _, row in shuffled.iterrows():
        cl, ve, tr, un = sample_rater_scores(row)
        scores_a.append({
            "item_id": row["item_id"],
            "record_id": row["record_id"],
            "requirement": row["requirement"],
            "source_file": f"texts/{row['record_id']}.txt",
            "clarity": cl,
            "verifiability": ve,
            "traceability": tr,
            "unsupported": un,
            "notes": "",
        })

    df_a = pd.DataFrame(scores_a)
    df_a.to_csv(os.path.join(target_dir, "annotations_A.csv"), index=False)
    print(f"  [OK] Generated complete Rater A annotations ({len(df_a)} items)")

    # Rater B scores 20% subset with small random variation to simulate realistic kappa (0.65 - 0.80)
    df_b = df_a[df_a["item_id"].isin(subset_b["item_id"])].copy().reset_index(drop=True)
    for idx in range(len(df_b)):
        # 15% chance to shift ordinal scores by +/- 1
        for col, min_v, max_v in [("clarity", 1, 3), ("verifiability", 1, 3), ("traceability", 0, 2)]:
            if rng.random() < 0.15:
                shift = rng.choice([-1, 1])
                df_b.loc[idx, col] = int(np.clip(df_b.loc[idx, col] + shift, min_v, max_v))
        # 10% chance to flip binary unsupported
        if rng.random() < 0.10:
            df_b.loc[idx, "unsupported"] = 1 - df_b.loc[idx, "unsupported"]

    df_b.to_csv(os.path.join(target_dir, "annotations_B.csv"), index=False)
    print(f"  [OK] Generated Rater B annotations ({len(df_b)} items, 20% subset)")

    print(f"\nSynthetic test data successfully generated in '{target_dir}'.")
    print("You can now test Step 6 with:")
    print(f"    python scripts/06_analyze.py --data {target_dir} --out demo_outputs")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate synthetic test data for pipeline testing.")
    parser.add_argument(
        "--data",
        default="demo_data",
        help="Target directory for synthetic data (defaults to demo_data)",
    )
    args = parser.parse_args()

    create_demo_data(target_dir=args.data)
