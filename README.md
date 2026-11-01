# ATRS Research Pipeline: Can Language Models Turn AI Governance Commitments into Verifiable Requirements?

An end-to-end, reproducible empirical software engineering research pipeline designed to convert UK Algorithmic Transparency Recording Standard (ATRS) public records into verifiable, traceable software requirements using Large Language Models (LLMs), and evaluate their quality through blind human annotation and statistical rigor.

---

## 1. Study Overview

- **Title:** *Can language models turn AI governance commitments into verifiable requirements?*
- **Target Journal:** *Requirements Engineering* (Springer)
- **Goal:** Sample 30–50 UK ATRS records, generate software requirements under Baseline and Evidence-Grounded conditions, and statistically evaluate requirement quality, traceability, and hallucination rates.

### Research Questions
- **RQ1 (Clarity & Testability):** Does evidence-grounded prompting yield significantly higher clarity and verifiability scores than ungrounded baseline generation?
- **RQ2 (Traceability):** To what extent are generated requirements grounded in identifiable evidence from the source record?
- **RQ3 (Source Completeness vs. Quality):** How does the informational completeness of the source ATRS disclosure affect requirement quality?
- **RQ4 (Unsupported / Hallucinated Claims):** At what rate do language models fabricate unsupported metrics, standards, or procedures, and does grounding prevent this?

---

## Quick Start (Zero Setup on Any Laptop)

This project is engineered to work out-of-the-box on **any laptop without manual setup**:

- **Windows Laptops (1-Click):** Double-click [run.bat](file:///c:/Users/HP/Downloads/atrs_project/run.bat). Auto-detects Python, auto-repairs virtual environments if copied from another PC, auto-installs packages, and opens the interactive menu.
- **macOS / Linux Laptops (1-Liner):** Run `./run.sh` in Terminal.
- **Web Browser (Zero Install, No Python needed):** Double-click [dashboard.html](file:///c:/Users/HP/Downloads/atrs_project/dashboard.html). Opens our rich interactive research dashboard offline in Chrome, Edge, Safari, or Firefox.
- **Universal Container (Docker):** Run `docker compose up` for an identical isolated environment.
- **Cloud Execution (Google Colab):** Open [atrs_replication_notebook.ipynb](file:///c:/Users/HP/Downloads/atrs_project/atrs_replication_notebook.ipynb) in Google Colab for instant cloud execution.
- **Diagnostic Audit:** Run `python verify_environment.py` to audit your laptop's environment in 1 second.
- See detailed instructions in [SETUP_ANY_LAPTOP.md](file:///c:/Users/HP/Downloads/atrs_project/SETUP_ANY_LAPTOP.md).

---

## 2. Directory and File Layout

```
atrs_project/
├── config.py                           # Central configuration (seeds, sample sizes, thresholds, model settings)
├── requirements.txt                    # Project dependencies (pandas, scipy, scikit-learn, matplotlib, etc.)
├── README.md                           # Comprehensive pipeline documentation and run order
├── rubric.md                           # 4-dimensional annotation rubric and calibration protocol
├── paper_draft.md                      # Complete manuscript skeleton formatted for Requirements Engineering
│
├── prompts/                            # Experimental prompting conditions (Independent Variable)
│   ├── baseline.txt                    # Standard requirements engineer prompt (8-12 requirements)
│   └── grounded.txt                    # Evidence-grounded prompt (shall-statements + verbatim quotes)
│
├── scripts/                            # Self-contained executable pipeline scripts
│   ├── llm.py                          # Unified Anthropic SDK interface with token usage logging
│   ├── 01_select_records.py            # Step 1: Detect columns, sample candidates, assign IDs R001...
│   ├── 02_fetch_texts.py               # Step 2: Download gov.uk pages, clean HTML, polite 1s delay
│   ├── 03_completeness.py              # Step 3: Compute completeness scores, median split, sample 40
│   ├── 04_generate.py                  # Step 4: Run LLM generations, JSON cache, quote verification
│   ├── 05_make_annotation_sheets.py    # Step 5: Generate blind evaluation sheets and secret key
│   ├── 06_analyze.py                   # Step 6: Cohen's kappa, Wilcoxon paired tests, 4 CSVs, 4 PNGs
│   └── make_demo_data.py               # Synthetic test generator to validate Steps 5-6 without API/internet
│
├── data/                               # Data artifacts (created by pipeline scripts)
│   ├── candidates.csv                  # Sampled candidate records with download statuses
│   ├── texts/                          # Raw cleaned text files of ATRS disclosures ({record_id}.txt)
│   ├── records.csv                     # Scored records with completeness metrics and high/low split
│   ├── generations.jsonl               # Resumable raw LLM cache
│   ├── requirements.csv                # Extracted requirements with automated quote verification
│   ├── annotation_key.csv              # Secret blinding key (hidden from raters)
│   ├── annotations_template_A.csv      # Blank scoring sheet for Rater A (100% sample)
│   ├── annotations_template_B.csv      # Blank scoring sheet for Rater B (20% sample)
│   ├── annotations_A.csv               # Completed human ratings from Rater A
│   ├── annotations_B.csv               # Completed human ratings from Rater B
│   └── usage_log.csv                   # Audit log tracking LLM tokens and API calls
│
└── outputs/                            # Research findings and publication assets (generated by Step 6)
    ├── table1_RQ1_clarity_testability.csv
    ├── table2_RQ2_traceability.csv
    ├── table3_RQ3_completeness.csv
    ├── table4_RQ4_unsupported.csv
    ├── item_scores.csv
    ├── fig1_RQ1.png                    # 300 DPI bar chart with SD error bars
    ├── fig2_RQ2.png                    # 300 DPI 100% stacked bar chart (Traceability tiers)
    ├── fig3_RQ3.png                    # 300 DPI scatter plot with regression trendlines
    ├── fig4_RQ4.png                    # 300 DPI grouped bar chart (Hallucinations by completeness)
    └── results_summary.md              # Markdown empirical report
```

---

## 3. Environment Setup

### 3.1 Prerequisites
- Python 3.10+ (tested on Python 3.11 on Windows and macOS).
- Anthropic API key (required only for live LLM generation in Step 4).

### 3.2 Installation
Clone or navigate to the project directory and install dependencies:

```bash
# Windows
py -3.11 -m pip install -r requirements.txt

# macOS / Linux
python3 -m pip install -r requirements.txt
```

### 3.3 API Key Configuration
For live generation (Step 4), set your Anthropic API key in your terminal session:

```bash
# Windows (PowerShell)
$env:ANTHROPIC_API_KEY="your-anthropic-api-key"

# Windows (Command Prompt)
set ANTHROPIC_API_KEY=your-anthropic-api-key

# macOS / Linux
export ANTHROPIC_API_KEY="your-anthropic-api-key"
```

---

## 4. End-to-End Execution Run Order

Every script is designed to be executed directly from the project root using relative paths.

### Step 1: Select Candidate Records
Download `atrs_records.csv` from the public UK algorithmic transparency repository into `data/atrs_records.csv`, then run:

```bash
python scripts/01_select_records.py data/atrs_records.csv
```
- Automatically detects publisher, tool name, date, and URL columns.
- Filters duplicates and invalid links.
- Samples $N = 70$ candidates (`config.N_CANDIDATES`) with seed 42.
- Assigns IDs: `R001`, `R002`, ..., and saves to `data/candidates.csv`.

### Step 2: Download Full Record Texts
Download the full disclosures from gov.uk:

```bash
python scripts/02_fetch_texts.py
```
- Polite 1.0-second delay between requests to gov.uk.
- Cleans HTML via BeautifulSoup (strips scripts, styles, navigation, headers, footers).
- Fully resumable: skips records that already exist in `data/texts/`.
- Logs failures and download status to `data/candidates.csv`.

### Step 3: Compute Completeness and Split Cohorts
Score each record's informational richness and select the final study cohort:

```bash
python scripts/03_completeness.py
```
- Computes completeness: $0.4 \times \text{section coverage} + 0.4 \times \text{length ratio (cap 2500 words)} + 0.2 \times \text{placeholder penalty}$.
- Excludes records with $< 300$ words.
- Samples $N = 40$ records evenly spaced across completeness.
- Performs median split into `high` and `low` completeness cohorts.
- Saves to `data/records.csv`.

### Step 4: Generate Requirements (LLM)
Generate requirements under Baseline and Grounded conditions:

```bash
python scripts/04_generate.py
```
- Executes both prompts (`baseline.txt` and `grounded.txt`) for each record.
- Cached in `data/generations.jsonl` (fully resumable if interrupted).
- Logs token usage and request latency to `data/usage_log.csv`.
- Robust JSON parsing with markdown code-fence handling.
- Performs automated quote verification against the source record (`exact`, `near`, `no`, or `none`).
- Exports final requirements to `data/requirements.csv`.

### Step 5: Generate Blind Annotation Sheets
Build randomized, blind evaluation sheets for human raters:

```bash
python scripts/05_make_annotation_sheets.py
```
- Shuffles requirements deterministically with seed 42 so baseline and grounded items are interleaved.
- Hides condition and evidence quotes from the sheets.
- Creates `data/annotation_key.csv` (secret key kept separate from raters).
- Creates `data/annotations_template_A.csv` (all items for Rater A).
- Creates `data/annotations_template_B.csv` (20% random subset for Rater B).

### Human Annotation Phase
1. Rater A opens `annotations_template_A.csv`, evaluates each requirement against `data/texts/{record_id}.txt` following `rubric.md`, and saves as `data/annotations_A.csv`.
2. Rater B independently scores `annotations_template_B.csv` and saves as `data/annotations_B.csv`.
3. Raters must not view `annotation_key.csv` during scoring.

### Step 6: Statistical Analysis and Visualization
Compute inter-rater reliability, statistical hypothesis tests, tables, and figures:

```bash
python scripts/06_analyze.py
```
- Inter-rater agreement: Quadratic weighted Cohen's $\kappa$ (Clarity, Verifiability, Traceability) and unweighted $\kappa$ (Unsupported).
- Paired Wilcoxon signed-rank tests per record with matched-pairs rank-biserial effect sizes ($r_{rb}$).
- Mann-Whitney $U$ test and Spearman correlation ($\rho$) for completeness effects.
- Exports 4 publication-ready CSV tables: `table1_RQ1` through `table4_RQ4`.
- Exports 4 publication-ready 300 DPI figures: `fig1_RQ1.png` through `fig4_RQ4.png`.
- Produces comprehensive report in `outputs/results_summary.md`.

---

## 5. Offline Synthetic Testing (Steps 5 and 6)

To test and validate the evaluation and statistical pipeline without internet access or an Anthropic API key, use the built-in synthetic test data generator:

```bash
# 1. Generate synthetic dataset with realistic distributions and mock texts
python scripts/make_demo_data.py --data demo_data

# 2. Test Step 5 (Blind sheet generation)
python scripts/05_make_annotation_sheets.py --data demo_data

# 3. Test Step 6 (Statistical analysis, tables, and figures)
python scripts/06_analyze.py --data demo_data --out demo_outputs
```

All 4 tables, 4 figures, and `results_summary.md` will be generated in `demo_outputs/`.

> **Notice:** Demo numbers are synthetically generated for verification only and should never be reported as empirical results.

---

## 6. Verification and Testing Status

### What Was Tested
- **All Python Dependencies:** Successfully installed and verified on Python 3.11 (`pandas`, `numpy`, `scipy`, `scikit-learn`, `matplotlib`, `requests`, `beautifulsoup4`, `anthropic`, `tabulate`).
- **Scripts 01, 02, 03, 04, 05, 06, llm, make_demo_data:** All verified for syntax and argument parsing (`--help`).
- **Offline Pipeline Testing (Steps 5 & 6):** Executed end-to-end on synthetic data:
  - `make_demo_data.py` generated 40 records, mock texts in `demo_data/texts/`, 820 requirements, secret keys, and realistic ratings for Raters A and B.
  - `05_make_annotation_sheets.py` verified blinding, shuffling, and template creation.
  - `06_analyze.py` successfully computed Cohen's quadratic kappa, paired Wilcoxon tests, Mann-Whitney $U$, Spearman correlations, 4 CSV tables, 4 publication figures at 300 DPI, and `results_summary.md`.
- **Zero-Dependency Formatting:** Formats clean markdown tables without external package failures.

### What Could Not Be Tested
- **Live gov.uk Network Scraping (Step 2):** Downloading live pages from `gov.uk` requires an active ATRS metadata index and internet connection.
- **Live Anthropic API Calls (Step 4 & llm.py):** Live generation of real LLM requirements requires an active `ANTHROPIC_API_KEY` with account balance.
