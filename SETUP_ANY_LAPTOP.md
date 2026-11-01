# Zero-Setup Portability Guide: Run on Any Laptop
**Project:** ATRS Requirements Engineering Research Pipeline  
**Authors:** Yashika Mehra & Shaina Mehra (Team On Top)  
**Target Journal:** *Requirements Engineering* (Springer Nature, 2025 Impact Factor: 3.3)

---

## 🚀 How to Run on Any Laptop (No Setup Required)

This repository is engineered to work out-of-the-box on **any Windows laptop, MacBook, Linux machine, Chromebook, or cloud environment**, even if the machine does not have Python pre-configured or previously failed with virtual environment path mismatches.

Choose your preferred method below:

---

### 1. Windows Laptops (1-Click Double-Click) 🪟

1. Open the project folder in Windows File Explorer:
   `c:\Users\<your_user>\Downloads\atrs_project`
2. **Double-click `run.bat`**.

#### What `run.bat` does automatically:
- **Deep Python Discovery:** Auto-detects `py -3`, `python`, `python3`, and standard system directories (`%LocalAppData%\Programs\Python\...`, `C:\Program Files\Python...`, `C:\Python...`).
- **Auto-Installer Fallback:** If Python is not installed anywhere on the laptop, `run.bat` offers a **1-click silent install** via Windows `winget`.
- **Self-Healing Virtual Environment:** If this folder was copied from another laptop, `run.bat` tests if the existing `venv` points to the other computer's paths. If invalid, it **automatically purges and rebuilds the virtual environment** cleanly for the current machine!
- **Automatic Dependency Check:** Verifies all 9 Python packages and auto-installs `requirements.txt` if any are missing.
- **Interactive Menu:** Lets you run the live pipeline, demo test, statistical analysis, diagnostic checker, or open the visual dashboard.

---

### 2. macOS & Linux Laptops (Terminal 1-Liner) 🍎 🐧

Open Terminal inside this folder and run:
```bash
chmod +x run.sh && ./run.sh
```

#### What `run.sh` does automatically:
- Detects `python3` or `python`.
- Detects cross-platform or stale virtual environments and auto-rebuilds them.
- Auto-installs missing dependencies from `requirements.txt`.
- Launches an interactive menu identical to the Windows launcher.

---

### 3. Zero-Install Web Browser Dashboard (No Python Needed!) 🌐

If you are presenting on a laptop where you cannot install software (e.g., locked school/university computers, supervisor's laptop, tablet):

1. **Double-click `dashboard.html`** (or right-click → Open with Chrome / Edge / Safari / Firefox).
2. Works **100% offline with zero dependencies**:
   - 📊 **Dataset Explorer:** Search and filter all 40 UK ATRS records by completeness stratum.
   - ⚖️ **Prompt Comparator:** Compare Baseline vs Evidence-Grounded prompts and generated requirements.
   - 📈 **Empirical Results:** Inspect Table 1 to Table 4, Cohen's Kappa, and high-resolution 300 DPI publication figures.
   - 📋 **Rubric & Protocol:** Inspect Clarity, Verifiability, Traceability, and Unsupported claims criteria.
   - 📄 **Manuscript Reader:** View the full Springer Nature research paper draft.
   - 🚀 **Quick Run Commands:** Copy-paste runners for all platforms.

---

### 4. Universal Docker Container 🐳

If the laptop has Docker Desktop or Docker engine installed:
```bash
docker compose up
```
- Completely isolated Debian container running Python 3.11.
- Zero local dependencies or Python required on the host system.
- Mounts local directory so all generated tables, figures, and CSVs save directly to your folder.

---

### 5. Google Colab / Cloud Jupyter Notebook ☁️

For running in the cloud with zero local disk space or software installation:
1. Open [Google Colab](https://colab.research.google.com/).
2. Upload `atrs_replication_notebook.ipynb`.
3. Click **Runtime → Run all**.
- Runs in Google's cloud on free compute.
- Renders publication figures and tables directly in your browser.

---

## 🛠️ Instant Laptop Diagnostic Tool

To verify that any laptop is 100% ready to run live generations or demo tests:
```bash
python verify_environment.py
```
This tool checks:
1. Python runtime version (>= 3.10)
2. All 9 Python libraries (`pandas`, `numpy`, `scipy`, `sklearn`, `matplotlib`, `requests`, `bs4`, `anthropic`, `tabulate`)
3. Primary dataset (`data/atrs_records.csv`, 136 records)
4. Scraped full-text corpus (`data/texts/`, 70 documents)
5. 40 stratified study records (`data/records.csv`)
6. Active Google Gemini / Anthropic API credentials
7. Output folders and scripts

---

## 📊 Summary of Pipeline Actions

| Choice | Script | Purpose |
|---|---|---|
| `[0]` | `dashboard.html` | Opens interactive visual research dashboard in default browser |
| `[1]` | `01` to `04` | Full live pipeline: selects records, scrapes texts, scores completeness, generates requirements with LLM |
| `[2]` | `05_make_annotation_sheets.py` | Generates blind evaluation sheets for Raters A & B |
| `[3]` | `06_analyze.py` | Computes statistical tests (Wilcoxon, Mann-Whitney, Spearman) and exports 4 publication figures |
| `[4]` | `make_demo_data.py` + `06` | Runs complete replication offline without an API key in ~5 seconds |
| `[5]` | `verify_environment.py` | Runs diagnostic environment check |
| `[6]` | Token Summary | Displays total token consumption and API calls logged |
