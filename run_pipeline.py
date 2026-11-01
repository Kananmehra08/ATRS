"""Cross-platform master pipeline launcher for ATRS Requirements Engineering study.
Team On Top: Yashika Mehra & Shaina Mehra

Usage:
    python run_pipeline.py            (Interactive menu)
    python run_pipeline.py --demo     (Run 100% offline demo test)
    python run_pipeline.py --live     (Run full live data pipeline: Steps 1 to 4)
    python run_pipeline.py --sheets   (Run Step 5: Blind annotation sheets)
    python run_pipeline.py --analyze  (Run Step 6: Statistics, tables, figures)
    python run_pipeline.py --diag     (Run laptop environment diagnostics)
    python run_pipeline.py --dashboard (Open interactive visual dashboard)
    python run_pipeline.py --usage    (Print API token summary)
"""
import os
import sys
import subprocess
import argparse
import webbrowser

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(PROJECT_ROOT)


def get_python_exe():
    """Locate the Python executable within the local virtual environment or active interpreter."""
    if sys.platform == "win32":
        venv_py = os.path.join(PROJECT_ROOT, "venv", "Scripts", "python.exe")
    else:
        venv_py = os.path.join(PROJECT_ROOT, "venv", "bin", "python")

    # Verify if venv python actually works (avoids broken paths from copied folders)
    if os.path.exists(venv_py):
        try:
            res = subprocess.run([venv_py, "-c", "import sys"], capture_output=True)
            if res.returncode == 0:
                return venv_py
        except Exception:
            pass

    return sys.executable


def run_cmd(args_list):
    """Execute a command list using the verified Python executable and check exit status."""
    py_exe = get_python_exe()
    full_cmd = [py_exe] + args_list
    print(f"\n>> Executing: {' '.join(full_cmd)}")
    res = subprocess.run(full_cmd)
    if res.returncode != 0:
        print(f"\n[ERROR] Command failed with exit code {res.returncode}")
        return False
    return True


def run_demo():
    """Run full offline test suite on synthetic data."""
    print("\n" + "=" * 60)
    print("RUNNING DEMO TEST (100% OFFLINE, NO API KEY NEEDED)")
    print("=" * 60)
    if not run_cmd(["scripts/make_demo_data.py", "--data", "demo_data"]):
        return
    if not run_cmd(["scripts/05_make_annotation_sheets.py", "--data", "demo_data"]):
        return
    if not run_cmd(["scripts/06_analyze.py", "--data", "demo_data", "--out", "demo_outputs"]):
        return
    print("\n[SUCCESS] Demo test completed! 4 figures and results_summary.md are in demo_outputs/")


def run_live_pipeline():
    """Run live data pipeline Steps 1 through 4."""
    print("\n" + "=" * 60)
    print("RUNNING LIVE DATA PIPELINE (STEPS 1 TO 4)")
    print("=" * 60)
    csv_file = os.path.join("data", "atrs_records.csv")
    if not os.path.exists(csv_file):
        print(f"[ERROR] {csv_file} not found. Please ensure the dataset is present.")
        return

    if not run_cmd(["scripts/01_select_records.py", csv_file]):
        return
    if not run_cmd(["scripts/02_fetch_texts.py"]):
        return
    if not run_cmd(["scripts/03_completeness.py"]):
        return
    if not run_cmd(["scripts/04_generate.py"]):
        return
    print("\n[SUCCESS] Steps 1 to 4 complete! Requirements saved to data/requirements.csv")


def run_sheets():
    """Run Step 5: Blind annotation sheets."""
    print("\n" + "=" * 60)
    print("BUILDING BLIND ANNOTATION SHEETS (STEP 5)")
    print("=" * 60)
    run_cmd(["scripts/05_make_annotation_sheets.py"])


def run_analyze():
    """Run Step 6: Analysis, tables, figures."""
    print("\n" + "=" * 60)
    print("RUNNING STATISTICAL ANALYSIS & VISUALIZATION (STEP 6)")
    print("=" * 60)
    run_cmd(["scripts/06_analyze.py"])


def run_diagnostics():
    """Run laptop environment diagnostics."""
    run_cmd(["verify_environment.py"])


def open_dashboard():
    """Open interactive HTML dashboard in default browser."""
    dash_path = os.path.join(PROJECT_ROOT, "dashboard.html")
    if os.path.exists(dash_path):
        print(f"\nOpening {dash_path} in your browser...")
        webbrowser.open(f"file://{os.path.abspath(dash_path)}")
    else:
        print("\ndashboard.html not found.")


def print_usage_summary():
    """Read usage_log.csv and print token summary."""
    p = os.path.join("data", "usage_log.csv")
    if not os.path.exists(p):
        print("\nNo usage log found at data/usage_log.csv")
        return
    try:
        import pandas as pd
        df = pd.read_csv(p)
        print("\n" + "=" * 60)
        print("LLM API USAGE & TOKEN CONSUMPTION SUMMARY")
        print("=" * 60)
        print(f"Total API Calls:     {len(df)}")
        print(f"Total Input Tokens:  {df['input_tokens'].sum():,}")
        print(f"Total Output Tokens: {df['output_tokens'].sum():,}")
        print(f"Grand Total Tokens:  {df['total_tokens'].sum():,}")
    except Exception as e:
        print(f"Could not read usage log: {e}")


def interactive_menu():
    """Display interactive CLI menu."""
    while True:
        print("\n" + "=" * 60)
        print("  ATRS REQUIREMENTS ENGINEERING PIPELINE")
        print("  Team On Top (Yashika & Shaina Mehra)")
        print("=" * 60)
        print("  [0] Open Interactive Visual Dashboard (in Web Browser)")
        print("  [1] Run Full Live Pipeline (Steps 1 to 4: Fetch + Generate)")
        print("  [2] Build Blind Annotation Sheets (Step 5)")
        print("  [3] Run Statistical Analysis, Tables & Figures (Step 6)")
        print("  [4] Run Demo Test (100% Offline, No API key needed)")
        print("  [5] Run Laptop Environment Diagnostics (verify_environment.py)")
        print("  [6] View Token Usage Summary")
        print("  [7] Exit")
        choice = input("\nEnter choice [0-7]: ").strip()

        if choice == "0":
            open_dashboard()
        elif choice == "1":
            run_live_pipeline()
        elif choice == "2":
            run_sheets()
        elif choice == "3":
            run_analyze()
        elif choice == "4":
            run_demo()
        elif choice == "5":
            run_diagnostics()
        elif choice == "6":
            print_usage_summary()
        elif choice == "7":
            print("Exiting.")
            sys.exit(0)
        else:
            print("Invalid selection, please try again.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ATRS Pipeline Runner")
    parser.add_argument("--demo", action="store_true", help="Run 100% offline synthetic demo test")
    parser.add_argument("--live", action="store_true", help="Run live pipeline (Steps 1 to 4)")
    parser.add_argument("--sheets", action="store_true", help="Run Step 5 (Blind sheets)")
    parser.add_argument("--analyze", action="store_true", help="Run Step 6 (Analysis)")
    parser.add_argument("--diag", action="store_true", help="Run laptop environment diagnostics")
    parser.add_argument("--dashboard", action="store_true", help="Open interactive web dashboard")
    parser.add_argument("--usage", action="store_true", help="Print token usage summary")
    args = parser.parse_args()

    if args.demo:
        run_demo()
    elif args.live:
        run_live_pipeline()
    elif args.sheets:
        run_sheets()
    elif args.analyze:
        run_analyze()
    elif args.diag:
        run_diagnostics()
    elif args.dashboard:
        open_dashboard()
    elif args.usage:
        print_usage_summary()
    else:
        interactive_menu()
