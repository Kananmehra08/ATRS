"""Step 6: Statistical analysis, generation of 4 CSV tables, 4 publication figures, and results summary.

Usage:
    python scripts/06_analyze.py [--data data] [--out outputs]

Research Questions Addressed:
- RQ1: Clarity and testability of generated requirements (paired Wilcoxon test, rank-biserial effect size).
- RQ2: Traceability to supporting evidence (distribution of levels, automated quote verification).
- RQ3: Requirement quality across completeness levels (Mann-Whitney U, Spearman rank correlation).
- RQ4: Rate of unsupported claims added by the LLM (paired Wilcoxon test, completeness breakdown).

Outputs:
- Tables:
    table1_RQ1_clarity_testability.csv
    table2_RQ2_traceability.csv
    table3_RQ3_completeness.csv
    table4_RQ4_unsupported.csv
    item_scores.csv
- Figures:
    fig1_RQ1.png
    fig2_RQ2.png
    fig3_RQ3.png
    fig4_RQ4.png
- Summary:
    results_summary.md
"""
import os
import sys
import glob
import argparse
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.metrics import cohen_kappa_score

# Ensure project root is on sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config


# Aesthetic color palette for figures
CONDITIONS = ["baseline", "grounded"]
PALETTE = {
    "baseline": "#5c6b73",     # Muted slate gray
    "grounded": "#1f6feb",     # Deep royal blue
    "full": "#2da44e",         # Forest green
    "partial": "#d4a72c",      # Warm amber
    "none": "#cf222e",         # Crimson red
}


def format_p_value(p: float) -> str:
    """Format a p-value for scientific reporting."""
    if pd.isna(p):
        return "n/a"
    if p < 0.001:
        return "<0.001"
    return f"{p:.3f}"


def df_to_markdown(df: pd.DataFrame) -> str:
    """Convert a pandas DataFrame to a clean GitHub-flavored markdown table without external dependencies."""
    headers = [str(c) for c in df.columns]
    col_widths = [len(h) for h in headers]
    rows_str = []

    for _, row in df.iterrows():
        row_str = [str(row[c]) if not pd.isna(row[c]) else "" for c in df.columns]
        for i, val in enumerate(row_str):
            col_widths[i] = max(col_widths[i], len(val))
        rows_str.append(row_str)

    # Pad strings
    header_line = "| " + " | ".join(h.ljust(col_widths[i]) for i, h in enumerate(headers)) + " |"
    sep_line = "| " + " | ".join("-" * col_widths[i] for i in range(len(headers))) + " |"
    data_lines = ["| " + " | ".join(val.ljust(col_widths[i]) for i, val in enumerate(r)) + " |" for r in rows_str]

    return "\n".join([header_line, sep_line] + data_lines)


def run_paired_wilcoxon(df_per_record: pd.DataFrame, metric: str) -> dict:
    """Compute paired Wilcoxon signed-rank test and matched-pairs rank-biserial correlation."""
    pivoted = df_per_record.pivot(index="record_id", columns="condition", values=metric).dropna()

    if "grounded" not in pivoted.columns or "baseline" not in pivoted.columns:
        return {"n": len(pivoted), "median_diff": np.nan, "p": np.nan, "r_rb": np.nan}

    diffs = (pivoted["grounded"] - pivoted["baseline"]).values
    median_diff = float(np.median(diffs))

    # Wilcoxon test on non-zero differences
    non_zero = diffs[diffs != 0]
    if len(non_zero) == 0:
        return {"n": len(pivoted), "median_diff": median_diff, "p": 1.0, "r_rb": 0.0}

    ranks = stats.rankdata(np.abs(non_zero))
    w_plus = ranks[non_zero > 0].sum()
    w_minus = ranks[non_zero < 0].sum()
    total_ranks = w_plus + w_minus

    r_rb = float((w_plus - w_minus) / total_ranks) if total_ranks > 0 else 0.0

    try:
        w_res = stats.wilcoxon(non_zero, zero_method="wilcox", alternative="two-sided")
        p_val = float(w_res.pvalue)
    except Exception:
        p_val = np.nan

    return {
        "n": len(pivoted),
        "median_diff": median_diff,
        "p": p_val,
        "r_rb": r_rb,
    }


def analyze(data_dir: str = config.DATA_DIR, out_dir: str = config.OUT_DIR):
    """Run full statistical evaluation, export 4 CSV tables, 4 figures, and summary report."""
    os.makedirs(out_dir, exist_ok=True)

    records_csv = os.path.join(data_dir, "records.csv")
    key_csv = os.path.join(data_dir, "annotation_key.csv")
    requirements_csv = os.path.join(data_dir, "requirements.csv")

    for f_path in [records_csv, key_csv, requirements_csv]:
        if not os.path.exists(f_path):
            raise FileNotFoundError(f"Required dataset missing: {f_path}")

    records_df = pd.read_csv(records_csv)
    key_df = pd.read_csv(key_csv)
    requirements_df = pd.read_csv(requirements_csv)

    # Load human annotation files (annotations_A.csv, annotations_B.csv)
    annotation_files = sorted(glob.glob(os.path.join(data_dir, "annotations_*.csv")))
    annotation_files = [f for f in annotation_files if "template" not in os.path.basename(f)]

    if not annotation_files:
        raise FileNotFoundError(
            f"No completed annotation files (e.g. annotations_A.csv) found in {data_dir}.\n"
            "Please complete the annotation sheets or run scripts/make_demo_data.py for synthetic testing."
        )

    ann_list = []
    for f in annotation_files:
        base = os.path.basename(f)
        rater_id = base.replace("annotations_", "").replace(".csv", "")
        df_ann = pd.read_csv(f)
        df_ann["rater"] = rater_id
        ann_list.append(df_ann)

    all_ann = pd.concat(ann_list, ignore_index=True)
    metrics = ["clarity", "verifiability", "traceability", "unsupported"]
    for m in metrics:
        all_ann[m] = pd.to_numeric(all_ann[m], errors="coerce")

    summary_lines = [
        "# ATRS Requirements Generation Study: Empirical Results Summary",
        f"Evaluated on {len(records_df)} ATRS records ({len(requirements_df)} total requirements).",
        "",
        "## Inter-Rater Reliability (Cohen's Kappa)",
    ]

    # 1. Inter-rater Agreement on double-annotated items
    unique_raters = sorted(all_ann["rater"].unique())
    if len(unique_raters) >= 2:
        r1, r2 = unique_raters[0], unique_raters[1]
        summary_lines.append(f"Double-annotated subset evaluated between Rater **{r1}** and Rater **{r2}**:")

        for m in metrics:
            wide_m = all_ann.pivot_table(index="item_id", columns="rater", values=m)[[r1, r2]].dropna()
            if len(wide_m) >= 5:
                # Quadratic weighting for ordinal scales (clarity 1-3, verifiability 1-3, traceability 0-2)
                weights = None if m == "unsupported" else "quadratic"
                kappa = cohen_kappa_score(wide_m[r1].round().astype(int), wide_m[r2].round().astype(int), weights=weights)
                scale_desc = "unweighted" if m == "unsupported" else "quadratic weighted"
                summary_lines.append(f"- **{m.capitalize()}** ({scale_desc}): $\\kappa = {kappa:.3f}$ ($n = {len(wide_m)}$ items)")
    else:
        summary_lines.append(f"Single rater detected ({unique_raters[0]}); double-annotation kappa skipped.")

    # 2. Item-level aggregation across raters
    items = all_ann.groupby("item_id")[metrics].mean().reset_index()
    items = items.merge(key_df, on="item_id", how="left")

    # Composite requirement quality metric (0.0 to 1.0)
    items["composite"] = (
        (items["clarity"] / 3.0) +
        (items["verifiability"] / 3.0) +
        (items["traceability"] / 2.0)
    ) / 3.0

    items_out_path = os.path.join(out_dir, "item_scores.csv")
    items.to_csv(items_out_path, index=False)

    # Per-record condition means
    per_record = items.groupby(["record_id", "condition"])[metrics + ["composite"]].mean().reset_index()
    per_record = per_record.merge(records_df[["record_id", "completeness", "group"]], on="record_id", how="left")

    # =========================================================================
    # RQ1: Clarity and Testability
    # =========================================================================
    rq1_rows = []
    for m in ["clarity", "verifiability"]:
        row = {"metric": m}
        for cond in CONDITIONS:
            sub = per_record[per_record["condition"] == cond][m]
            row[f"{cond}_mean"] = round(float(sub.mean()), 3)
            row[f"{cond}_sd"] = round(float(sub.std()), 3)
        stat = run_paired_wilcoxon(per_record, m)
        row["median_diff"] = round(stat["median_diff"], 3)
        row["wilcoxon_p"] = format_p_value(stat["p"])
        row["effect_r_rb"] = round(stat["r_rb"], 3)
        rq1_rows.append(row)

    df_rq1 = pd.DataFrame(rq1_rows)
    df_rq1.to_csv(os.path.join(out_dir, "table1_RQ1_clarity_testability.csv"), index=False)

    # =========================================================================
    # RQ2: Traceability and Grounded Evidence Verification
    # =========================================================================
    items["trace_cat"] = items["traceability"].round().astype(int).clip(0, 2)
    trace_dist = items.groupby("condition")["trace_cat"].value_counts(normalize=True).unstack(fill_value=0)
    trace_dist = trace_dist.reindex(columns=[0, 1, 2], fill_value=0) * 100.0

    df_rq2 = pd.DataFrame({
        "condition": CONDITIONS,
        "none_pct": [round(trace_dist.loc[c, 0], 1) if c in trace_dist.index else 0.0 for c in CONDITIONS],
        "partial_pct": [round(trace_dist.loc[c, 1], 1) if c in trace_dist.index else 0.0 for c in CONDITIONS],
        "full_pct": [round(trace_dist.loc[c, 2], 1) if c in trace_dist.index else 0.0 for c in CONDITIONS],
    })
    stat_tr = run_paired_wilcoxon(per_record, "traceability")
    df_rq2["wilcoxon_p(mean)"] = format_p_value(stat_tr["p"])
    df_rq2.to_csv(os.path.join(out_dir, "table2_RQ2_traceability.csv"), index=False)

    # Automated quote match stats for grounded requirements
    grounded_reqs = requirements_df[requirements_df["condition"] == "grounded"]
    quote_counts = grounded_reqs["auto_quote_match"].value_counts(normalize=True) * 100.0
    summary_lines.append("")
    summary_lines.append("## Automated Grounded Evidence Quote Verification")
    summary_lines.append(f"Grounded prompt evidence quotes evaluated against source record text ($n = {len(grounded_reqs)}$ requirements):")
    for q_match in ["exact", "near", "no", "none"]:
        pct = quote_counts.get(q_match, 0.0)
        summary_lines.append(f"- **{q_match.capitalize()} match**: {pct:.1f}%")

    # =========================================================================
    # RQ3: Completeness vs Quality
    # =========================================================================
    rq3_rows = []
    for cond in CONDITIONS:
        sub = per_record[per_record["condition"] == cond]
        high_group = sub[sub["group"] == "high"]["composite"].dropna()
        low_group = sub[sub["group"] == "low"]["composite"].dropna()

        # Mann-Whitney U test (High vs Low)
        if len(high_group) > 0 and len(low_group) > 0:
            u_stat, u_p = stats.mannwhitneyu(high_group, low_group, alternative="two-sided")
        else:
            u_p = np.nan

        # Spearman correlation (Completeness vs Composite)
        if len(sub) > 2:
            rho, rho_p = stats.spearmanr(sub["completeness"], sub["composite"])
        else:
            rho, rho_p = np.nan, np.nan

        rq3_rows.append({
            "condition": cond,
            "high_mean": round(float(high_group.mean()), 3) if len(high_group) else np.nan,
            "low_mean": round(float(low_group.mean()), 3) if len(low_group) else np.nan,
            "n_high": len(high_group),
            "n_low": len(low_group),
            "mannwhitney_p": format_p_value(u_p),
            "spearman_rho": round(float(rho), 3) if not pd.isna(rho) else np.nan,
            "spearman_p": format_p_value(rho_p),
        })

    df_rq3 = pd.DataFrame(rq3_rows)
    df_rq3.to_csv(os.path.join(out_dir, "table3_RQ3_completeness.csv"), index=False)

    # =========================================================================
    # RQ4: Unsupported Claims
    # =========================================================================
    rq4_rows = []
    for cond in CONDITIONS:
        sub_items = items[items["condition"] == cond]
        sub_pr = per_record[per_record["condition"] == cond]

        overall_pct = float(sub_items["unsupported"].mean()) * 100.0
        high_pct = float(sub_pr[sub_pr["group"] == "high"]["unsupported"].mean()) * 100.0
        low_pct = float(sub_pr[sub_pr["group"] == "low"]["unsupported"].mean()) * 100.0

        rq4_rows.append({
            "condition": cond,
            "overall_rate_pct": round(overall_pct, 1),
            "high_completeness_pct": round(high_pct, 1),
            "low_completeness_pct": round(low_pct, 1),
        })

    df_rq4 = pd.DataFrame(rq4_rows)
    stat_un = run_paired_wilcoxon(per_record, "unsupported")
    df_rq4["paired_wilcoxon_p"] = format_p_value(stat_un["p"])
    df_rq4.to_csv(os.path.join(out_dir, "table4_RQ4_unsupported.csv"), index=False)

    # =========================================================================
    # Figures (Publication Ready, 300 DPI)
    # =========================================================================
    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.size": 10,
        "axes.edgecolor": "#333333",
        "axes.linewidth": 0.8,
        "axes.grid": True,
        "grid.color": "#e0e0e0",
        "grid.linestyle": ":",
        "grid.alpha": 0.7,
    })

    # --- Fig 1: RQ1 Clarity & Testability ---
    fig, ax = plt.subplots(figsize=(6, 4.2), dpi=300)
    width = 0.35
    x = np.arange(2)

    for idx, cond in enumerate(CONDITIONS):
        means = [per_record[per_record["condition"] == cond][m].mean() for m in ["clarity", "verifiability"]]
        stds = [per_record[per_record["condition"] == cond][m].std() for m in ["clarity", "verifiability"]]
        ax.bar(
            x + (idx - 0.5) * width,
            means,
            width,
            yerr=stds,
            capsize=4,
            label=cond.capitalize(),
            color=PALETTE[cond],
            alpha=0.9,
            edgecolor="#222222",
            linewidth=0.6,
        )

    ax.set_xticks(x)
    ax.set_xticklabels(["Clarity (1-3)", "Verifiability (1-3)"], fontweight="bold")
    ax.set_ylabel("Mean Human Rating (Score 1-3)", fontweight="bold")
    ax.set_ylim(0, 3.4)
    ax.set_title("Fig 1 (RQ1): Clarity and Verifiability by Prompt Condition", fontweight="bold", pad=12)
    ax.legend(frameon=True, facecolor="white", edgecolor="#cccccc")
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "fig1_RQ1.png"), dpi=300)
    plt.close()

    # --- Fig 2: RQ2 Traceability to Source Evidence ---
    fig, ax = plt.subplots(figsize=(6, 4.2), dpi=300)
    bottom = np.zeros(len(CONDITIONS))

    for lvl, label, color in [(2, "Full Support", PALETTE["full"]),
                              (1, "Partial Support", PALETTE["partial"]),
                              (0, "No Support", PALETTE["none"])]:
        vals = np.array([df_rq2.loc[df_rq2["condition"] == c, f"{['none', 'partial', 'full'][lvl]}_pct"].values[0] for c in CONDITIONS])
        ax.bar(
            [c.capitalize() for c in CONDITIONS],
            vals,
            bottom=bottom,
            label=label,
            color=color,
            alpha=0.9,
            edgecolor="#222222",
            linewidth=0.6,
            width=0.45,
        )
        bottom += vals

    ax.set_ylabel("Percentage of Requirements (%)", fontweight="bold")
    ax.set_ylim(0, 105)
    ax.set_title("Fig 2 (RQ2): Traceability to Source Evidence", fontweight="bold", pad=12)
    ax.legend(frameon=True, facecolor="white", edgecolor="#cccccc", loc="lower right")
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "fig2_RQ2.png"), dpi=300)
    plt.close()

    # --- Fig 3: RQ3 Completeness vs Composite Quality ---
    fig, ax = plt.subplots(figsize=(6.2, 4.2), dpi=300)
    for cond in CONDITIONS:
        sub = per_record[per_record["condition"] == cond]
        ax.scatter(
            sub["completeness"],
            sub["composite"],
            color=PALETTE[cond],
            alpha=0.75,
            edgecolors="none",
            s=45,
            label=f"{cond.capitalize()} observations",
        )
        if len(sub) > 1:
            poly = np.polyfit(sub["completeness"], sub["composite"], 1)
            x_line = np.linspace(sub["completeness"].min(), sub["completeness"].max(), 30)
            ax.plot(x_line, np.polyval(poly, x_line), color=PALETTE[cond], linewidth=2.0, label=f"{cond.capitalize()} trend")

    ax.set_xlabel("Record Completeness Score (0.0 to 1.0)", fontweight="bold")
    ax.set_ylabel("Composite Requirement Quality (0.0 to 1.0)", fontweight="bold")
    ax.set_ylim(0.2, 1.05)
    ax.set_title("Fig 3 (RQ3): Record Completeness vs Requirement Quality", fontweight="bold", pad=12)
    ax.legend(frameon=True, facecolor="white", edgecolor="#cccccc", loc="lower right", fontsize=8)
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "fig3_RQ3.png"), dpi=300)
    plt.close()

    # --- Fig 4: RQ4 Unsupported Claims by Completeness Level ---
    fig, ax = plt.subplots(figsize=(6, 4.2), dpi=300)
    width = 0.35
    x = np.arange(2)

    rq4_indexed = df_rq4.set_index("condition")
    for idx, cond in enumerate(CONDITIONS):
        vals = [
            rq4_indexed.loc[cond, "low_completeness_pct"],
            rq4_indexed.loc[cond, "high_completeness_pct"],
        ]
        ax.bar(
            x + (idx - 0.5) * width,
            vals,
            width,
            label=cond.capitalize(),
            color=PALETTE[cond],
            alpha=0.9,
            edgecolor="#222222",
            linewidth=0.6,
        )

    ax.set_xticks(x)
    ax.set_xticklabels(["Low Completeness Records", "High Completeness Records"], fontweight="bold")
    ax.set_ylabel("Unsupported Claims Rate (%)", fontweight="bold")
    ax.set_ylim(0, max(50.0, df_rq4[["high_completeness_pct", "low_completeness_pct"]].max().max() + 10))
    ax.set_title("Fig 4 (RQ4): Hallucinated / Unsupported Claims by Record Completeness", fontweight="bold", pad=12)
    ax.legend(frameon=True, facecolor="white", edgecolor="#cccccc")
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "fig4_RQ4.png"), dpi=300)
    plt.close()

    # Append markdown tables to results_summary.md
    summary_lines.append("")
    summary_lines.append("## Table 1 (RQ1): Clarity and Testability Comparison")
    summary_lines.append(df_to_markdown(df_rq1))

    summary_lines.append("")
    summary_lines.append("## Table 2 (RQ2): Traceability to Source Evidence")
    summary_lines.append(df_to_markdown(df_rq2))

    summary_lines.append("")
    summary_lines.append("## Table 3 (RQ3): Requirement Quality Across Record Completeness")
    summary_lines.append(df_to_markdown(df_rq3))

    summary_lines.append("")
    summary_lines.append("## Table 4 (RQ4): Frequency of Unsupported Claims")
    summary_lines.append(df_to_markdown(df_rq4))

    summary_path = os.path.join(out_dir, "results_summary.md")
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("\n".join(summary_lines) + "\n")

    print("\n" + "=" * 60)
    print("ANALYSIS COMPLETE")
    print("=" * 60)
    print(f"Tables saved to CSV in: {out_dir}")
    print(f"Figures saved to PNG (300 DPI) in: {out_dir}")
    print(f"Results summary written to: {summary_path}")
    print("\n" + "\n".join(summary_lines))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Step 6: Statistical analysis, CSV tables, and PNG figures.")
    parser.add_argument(
        "--data",
        default=config.DATA_DIR,
        help=f"Data directory containing completed annotations (defaults to {config.DATA_DIR})",
    )
    parser.add_argument(
        "--out",
        default=config.OUT_DIR,
        help=f"Output directory for tables and figures (defaults to {config.OUT_DIR})",
    )
    args = parser.parse_args()

    try:
        analyze(data_dir=args.data, out_dir=args.out)
    except FileNotFoundError as err:
        print(f"\n[INFO] {err}\n")
        sys.exit(1)
