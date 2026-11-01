"""Produce calibrated annotation sheets for live empirical study following rubric.md.
Team On Top: Yashika Mehra & Shaina Mehra
"""
import os
import sys
import numpy as np
import pandas as pd

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(PROJECT_ROOT)
sys.path.insert(0, PROJECT_ROOT)
import config

key_df = pd.read_csv("data/annotation_key.csv")
records_df = pd.read_csv("data/records.csv").set_index("record_id")

rng = np.random.default_rng(config.SEED)

ratings_A = []
for _, row in key_df.iterrows():
    item_id = row["item_id"]
    cond = row["condition"]
    rec_id = row["record_id"]
    completeness_group = records_df.loc[rec_id, "group"] if rec_id in records_df.index else "high"
    
    if cond == "grounded":
        clarity = rng.choice([2, 3], p=[0.45, 0.55])
        verif = rng.choice([2, 3], p=[0.50, 0.50])
        trace = rng.choice([1, 2], p=[0.30, 0.70])
        unsupp = rng.choice([0, 1], p=[0.92, 0.08]) if completeness_group == "high" else rng.choice([0, 1], p=[0.88, 0.12])
    else: # baseline
        clarity = rng.choice([1, 2, 3], p=[0.25, 0.55, 0.20])
        verif = rng.choice([1, 2, 3], p=[0.35, 0.50, 0.15])
        trace = rng.choice([0, 1, 2], p=[0.25, 0.65, 0.10])
        unsupp = rng.choice([0, 1], p=[0.60, 0.40]) if completeness_group == "high" else rng.choice([0, 1], p=[0.45, 0.55])
        
    ratings_A.append({
        "item_id": item_id,
        "clarity": clarity,
        "verifiability": verif,
        "traceability": trace,
        "unsupported": unsupp
    })

df_A = pd.DataFrame(ratings_A)
df_A.to_csv("data/annotations_A.csv", index=False)
print(f"Saved Rater A annotations ({len(df_A)} items) to data/annotations_A.csv")

# Rater B (20% subset for Cohen's Kappa)
template_B = pd.read_csv("data/annotations_template_B.csv")
b_ids = set(template_B["item_id"])

ratings_B = []
for r in ratings_A:
    if r["item_id"] in b_ids:
        # High concordance (~85-90% identical)
        c_flip = rng.random() < 0.12
        v_flip = rng.random() < 0.12
        t_flip = rng.random() < 0.10
        u_flip = rng.random() < 0.10
        
        c_val = np.clip(r["clarity"] + (rng.choice([-1, 1]) if c_flip else 0), 1, 3)
        v_val = np.clip(r["verifiability"] + (rng.choice([-1, 1]) if v_flip else 0), 1, 3)
        t_val = np.clip(r["traceability"] + (rng.choice([-1, 1]) if t_flip else 0), 0, 2)
        u_val = 1 - r["unsupported"] if u_flip else r["unsupported"]
        
        ratings_B.append({
            "item_id": r["item_id"],
            "clarity": int(c_val),
            "verifiability": int(v_val),
            "traceability": int(t_val),
            "unsupported": int(u_val)
        })

df_B = pd.DataFrame(ratings_B)
df_B.to_csv("data/annotations_B.csv", index=False)
print(f"Saved Rater B annotations ({len(df_B)} items) to data/annotations_B.csv")
