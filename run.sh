#!/usr/bin/env bash
# ATRS Requirements Engineering Research Pipeline Runner (macOS / Linux)
# Team On Top: Yashika Mehra & Shaina Mehra
# Universal Zero-Setup Launcher

set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"

echo "============================================================"
echo "  ATRS Requirements Engineering Research Pipeline"
echo "  Team On Top: Yashika Mehra & Shaina Mehra"
echo "  Universal Zero-Setup Launcher (macOS / Linux)"
echo "============================================================"
echo ""

# 1. Detect Python 3
if command -v python3 &>/dev/null; then
    PY_CMD="python3"
elif command -v python &>/dev/null; then
    PY_CMD="python"
else
    echo "[ERROR] Python 3 was not found."
    echo "Please install Python 3.10+ using: brew install python (macOS) or apt install python3 python3-venv (Ubuntu/Debian)"
    exit 1
fi

echo "[1/3] Python Runtime: $($PY_CMD --version)"

# 2. Virtual Environment Verification & Auto-Repair
NEED_INSTALL=0

if [ -d "venv" ]; then
    # Test if existing venv actually executes on THIS computer
    if ! ./venv/bin/python -c "import sys" &>/dev/null; then
        echo "[2/3] Existing 'venv' was created on another machine or OS."
        echo "      Auto-repairing virtual environment for this computer..."
        rm -rf venv
        $PY_CMD -m venv venv
        NEED_INSTALL=1
    else
        echo "[2/3] Virtual environment 'venv' verified on this machine."
    fi
else
    echo "[2/3] Creating virtual environment 'venv'..."
    $PY_CMD -m venv venv
    NEED_INSTALL=1
fi

# 3. Dependency Verification
if [ $NEED_INSTALL -eq 0 ]; then
    if ! ./venv/bin/python -c "import pandas, scipy, sklearn, matplotlib, requests, bs4, anthropic, tabulate" &>/dev/null; then
        echo "[3/3] Missing dependencies detected. Auto-installing..."
        NEED_INSTALL=1
    fi
fi

if [ $NEED_INSTALL -eq 1 ]; then
    echo "[3/3] Installing dependencies from requirements.txt..."
    ./venv/bin/pip install --upgrade pip
    ./venv/bin/pip install -r requirements.txt
    echo "      All dependencies installed successfully!"
else
    echo "[3/3] All dependencies verified and ready!"
fi

show_menu() {
    echo ""
    echo "============================================================"
    echo "  Environment Ready! Select an action:"
    echo "============================================================"
    echo "  [0] Open Interactive Visual Dashboard (in Web Browser)"
    echo "  [1] Run Full Live Pipeline (Steps 1 to 4: Fetch + Generate)"
    echo "  [2] Build Blind Annotation Sheets (Step 5)"
    echo "  [3] Run Statistical Analysis, Tables & Figures (Step 6)"
    echo "  [4] Run Demo Test (100% Offline, No API key needed)"
    echo "  [5] Run Laptop Environment Diagnostics (verify_environment.py)"
    echo "  [6] View Token Usage & API Statistics"
    echo "  [7] Open Shell inside (venv)"
    echo "  [8] Exit"
    echo ""
    read -p "Enter choice [0-8]: " opt

    case "$opt" in
        0)
            if command -v xdg-open &>/dev/null; then
                xdg-open dashboard.html
            elif command -v open &>/dev/null; then
                open dashboard.html
            else
                echo "Open file in browser: file://$DIR/dashboard.html"
            fi
            show_menu
            ;;
        1)
            ./venv/bin/python scripts/01_select_records.py data/atrs_records.csv
            ./venv/bin/python scripts/02_fetch_texts.py
            ./venv/bin/python scripts/03_completeness.py
            ./venv/bin/python scripts/04_generate.py
            show_menu
            ;;
        2)
            ./venv/bin/python scripts/05_make_annotation_sheets.py
            show_menu
            ;;
        3)
            ./venv/bin/python scripts/06_analyze.py
            show_menu
            ;;
        4)
            ./venv/bin/python scripts/make_demo_data.py --data demo_data
            ./venv/bin/python scripts/05_make_annotation_sheets.py --data demo_data
            ./venv/bin/python scripts/06_analyze.py --data demo_data --out demo_outputs
            echo "Demo Test Complete! Figures and summary saved in demo_outputs/"
            show_menu
            ;;
        5)
            ./venv/bin/python verify_environment.py
            show_menu
            ;;
        6)
            ./venv/bin/python -c "import os, pandas as pd; p='data/usage_log.csv'; df=pd.read_csv(p) if os.path.exists(p) else None; print(f'Total Calls: {len(df)} | Input: {df.input_tokens.sum():,} | Output: {df.output_tokens.sum():,} | Total Tokens: {df.total_tokens.sum():,}') if df is not None and len(df) else print('No usage logged yet.')"
            show_menu
            ;;
        7)
            source venv/bin/activate
            bash --login
            show_menu
            ;;
        8)
            exit 0
            ;;
        *)
            echo "Invalid choice."
            show_menu
            ;;
    esac
}

show_menu
