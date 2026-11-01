"""Environment verification and diagnostic tool for ATRS Requirements Engineering project.

Validates that Python, packages, datasets, prompts, scripts, and API credentials
are correctly configured and fully operational on this computer.
"""
import sys
import os
import importlib

# Ensure relative paths resolve relative to project root
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(PROJECT_ROOT)

def print_header(title):
    print("\n" + "=" * 65)
    print(f"  {title}")
    print("=" * 65)

def check_python():
    print(f">> Python Executable: {sys.executable}")
    print(f">> Python Version:    {sys.version.split()[0]}")
    v = sys.version_info
    if v.major == 3 and v.minor >= 10:
        print("   [PASS] Python version is 3.10+ (Supported)")
        return True
    else:
        print(f"   [WARN] Python version {v.major}.{v.minor} is below recommended 3.10+")
        return False

def check_dependencies():
    packages = [
        ("pandas", "Pandas DataFrames"),
        ("numpy", "NumPy Array Computing"),
        ("scipy", "SciPy Statistical Tests (Wilcoxon, Mann-Whitney)"),
        ("sklearn", "Scikit-Learn (Cohen's Kappa)"),
        ("matplotlib", "Matplotlib Publication Figures"),
        ("requests", "HTTP Requests for gov.uk Scraping & Gemini API"),
        ("bs4", "BeautifulSoup4 HTML Cleaning"),
        ("anthropic", "Anthropic Claude API Client"),
        ("tabulate", "Markdown Table Formatter")
    ]
    all_ok = True
    for mod_name, desc in packages:
        try:
            mod = importlib.import_module(mod_name)
            ver = getattr(mod, "__version__", "installed")
            print(f"   [PASS] {mod_name:<12} ({ver:<10}) - {desc}")
        except ImportError:
            print(f"   [FAIL] {mod_name:<12} (MISSING)    - {desc}")
            all_ok = False
    return all_ok

def check_project_files():
    required_paths = [
        ("config.py", "Configuration module"),
        ("requirements.txt", "Package dependencies list"),
        ("prompts/baseline.txt", "Baseline prompt template"),
        ("prompts/grounded.txt", "Evidence-grounded prompt template"),
        ("rubric.md", "Evaluation rubric & protocol"),
        ("paper_draft.md", "Research paper draft"),
        ("scripts/01_select_records.py", "Step 1 script"),
        ("scripts/02_fetch_texts.py", "Step 2 script"),
        ("scripts/03_completeness.py", "Step 3 script"),
        ("scripts/04_generate.py", "Step 4 script"),
        ("scripts/05_make_annotation_sheets.py", "Step 5 script"),
        ("scripts/06_analyze.py", "Step 6 script"),
        ("scripts/llm.py", "LLM abstraction layer"),
        ("scripts/make_demo_data.py", "Synthetic demo generator"),
        ("data/atrs_records.csv", "UK ATRS primary dataset"),
        ("data/records.csv", "40 sampled empirical records"),
    ]
    all_ok = True
    for rel_path, desc in required_paths:
        full_path = os.path.join(PROJECT_ROOT, rel_path)
        if os.path.exists(full_path):
            size = os.path.getsize(full_path)
            print(f"   [PASS] {rel_path:<35} ({size:>7,} bytes) - {desc}")
        else:
            print(f"   [FAIL] {rel_path:<35} (NOT FOUND)      - {desc}")
            all_ok = False
    
    # Check text corpus
    texts_dir = os.path.join(PROJECT_ROOT, "data", "texts")
    if os.path.exists(texts_dir):
        txt_files = [f for f in os.listdir(texts_dir) if f.endswith(".txt")]
        print(f"   [PASS] data/texts/                         ({len(txt_files)} files)        - Scraped gov.uk texts")
    else:
        print("   [WARN] data/texts/ directory not found yet.")
    return all_ok

def check_api_credentials():
    try:
        import config
        has_gemini = bool(getattr(config, "GEMINI_API_KEY", None))
        has_anthropic = bool(getattr(config, "ANTHROPIC_API_KEY", None)) or bool(os.environ.get("ANTHROPIC_API_KEY"))
        
        if has_gemini:
            key = config.GEMINI_API_KEY
            masked = key[:6] + "..." + key[-4:] if len(key) > 10 else "***"
            print(f"   [PASS] Google Gemini API Key configured: {masked}")
            print(f"   [INFO] Default Model: {config.MODEL}")
            return True
        elif has_anthropic:
            print("   [PASS] Anthropic API Key configured.")
            return True
        else:
            print("   [WARN] No API key configured. Live generations will require GEMINI_API_KEY or ANTHROPIC_API_KEY.")
            print("          (Offline Demo mode does not require any API key).")
            return False
    except Exception as e:
        print(f"   [FAIL] Error reading config: {e}")
        return False

def main():
    print_header("ATRS RESEARCH PIPELINE: LAPTOP ENVIRONMENT DIAGNOSTIC")
    
    print("\n[1] Checking Python Runtime:")
    py_ok = check_python()
    
    print("\n[2] Checking Required Python Packages:")
    dep_ok = check_dependencies()
    
    print("\n[3] Checking Project Files & Datasets:")
    files_ok = check_project_files()
    
    print("\n[4] Checking LLM API Configuration:")
    api_ok = check_api_credentials()
    
    print_header("DIAGNOSTIC SUMMARY")
    if py_ok and dep_ok and files_ok:
        print("  Status: 100% READY! All requirements and assets are verified.")
        print("  This project is fully operational on this computer.")
        if api_ok:
            print("  Ready for both LIVE empirical generation AND offline demo testing.")
        else:
            print("  Ready for offline demo testing. Set API key in config.py for live generation.")
    else:
        print("  Status: SOME CHECKS NEED ATTENTION.")
        if not dep_ok:
            print("  -> Run: pip install -r requirements.txt")
    print("=" * 65 + "\n")

if __name__ == "__main__":
    main()
