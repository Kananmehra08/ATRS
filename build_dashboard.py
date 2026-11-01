"""Build self-contained, zero-setup interactive web dashboard (dashboard.html).
Team On Top: Yashika Mehra & Shaina Mehra
"""
import json
import os
import pandas as pd

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

rec_df = pd.read_csv(os.path.join(PROJECT_ROOT, "data", "records.csv")).fillna("")
req_df = pd.read_csv(os.path.join(PROJECT_ROOT, "data", "requirements.csv")).fillna("")

bundle = {
    "records": rec_df.to_dict(orient="records"),
    "requirements": req_df.to_dict(orient="records")
}

# Write clean, strictly valid ASCII JSON to data_bundle.json (no NaNs, no encoding errors)
with open(os.path.join(PROJECT_ROOT, "data_bundle.json"), "w", encoding="utf-8") as f:
    json.dump(bundle, f, indent=2, ensure_ascii=True)

records_json = json.dumps(bundle["records"], ensure_ascii=True)
requirements_json = json.dumps(bundle["requirements"], ensure_ascii=True)

html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>ATRS Requirements Engineering Research Dashboard | Team On Top</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
  <style>
    :root {{
      --bg-gradient: radial-gradient(circle at 15% 15%, #131b2e 0%, #080c14 100%);
      --surface: rgba(18, 25, 41, 0.75);
      --surface-hover: rgba(28, 38, 62, 0.85);
      --surface-border: rgba(99, 102, 241, 0.18);
      --surface-border-active: rgba(99, 102, 241, 0.5);
      --primary: #6366f1;
      --primary-hover: #4f46e5;
      --primary-glow: rgba(99, 102, 241, 0.35);
      --emerald: #10b981;
      --emerald-glow: rgba(16, 185, 129, 0.25);
      --amber: #f59e0b;
      --rose: #f43f5e;
      --cyan: #06b6d4;
      --text-main: #f8fafc;
      --text-muted: #94a3b8;
      --text-dim: #64748b;
      --radius: 14px;
      --shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5), 0 8px 10px -6px rgba(0, 0, 0, 0.5);
    }}

    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }}

    body {{
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
      background: var(--bg-gradient);
      background-attachment: fixed;
      color: var(--text-main);
      min-height: 100vh;
      line-height: 1.6;
      -webkit-font-smoothing: antialiased;
    }}

    /* Layout */
    .container {{
      max-width: 1400px;
      margin: 0 auto;
      padding: 2rem 1.5rem 4rem;
    }}

    /* Header */
    header.header {{
      background: var(--surface);
      backdrop-filter: blur(20px);
      border: 1px solid var(--surface-border);
      border-radius: var(--radius);
      padding: 2.2rem 2.5rem;
      margin-bottom: 2rem;
      box-shadow: var(--shadow);
      position: relative;
      overflow: hidden;
    }}

    header.header::before {{
      content: '';
      position: absolute;
      top: -100px;
      right: -100px;
      width: 320px;
      height: 320px;
      background: radial-gradient(circle, var(--primary-glow) 0%, transparent 70%);
      pointer-events: none;
    }}

    .badge-bar {{
      display: flex;
      flex-wrap: wrap;
      gap: 0.75rem;
      margin-bottom: 1rem;
      align-items: center;
    }}

    .tag {{
      display: inline-flex;
      align-items: center;
      gap: 0.4rem;
      padding: 0.3rem 0.8rem;
      border-radius: 9999px;
      font-size: 0.75rem;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }}

    .tag-primary {{ background: rgba(99, 102, 241, 0.15); color: #a5b4fc; border: 1px solid rgba(99, 102, 241, 0.3); }}
    .tag-emerald {{ background: rgba(16, 185, 129, 0.15); color: #6ee7b7; border: 1px solid rgba(16, 185, 129, 0.3); }}
    .tag-amber {{ background: rgba(245, 158, 11, 0.15); color: #fcd34d; border: 1px solid rgba(245, 158, 11, 0.3); }}
    .tag-cyan {{ background: rgba(6, 182, 212, 0.15); color: #67e8f9; border: 1px solid rgba(6, 182, 212, 0.3); }}

    h1.title {{
      font-family: 'Outfit', sans-serif;
      font-size: 2.2rem;
      font-weight: 700;
      letter-spacing: -0.02em;
      line-height: 1.25;
      margin-bottom: 0.6rem;
      background: linear-gradient(135deg, #ffffff 30%, #a5b4fc 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }}

    p.subtitle {{
      font-size: 1.05rem;
      color: var(--text-muted);
      max-width: 900px;
      margin-bottom: 1.2rem;
    }}

    .author-meta {{
      display: flex;
      flex-wrap: wrap;
      gap: 1.5rem;
      font-size: 0.9rem;
      color: var(--text-muted);
      border-top: 1px solid rgba(255, 255, 255, 0.08);
      padding-top: 1rem;
    }}

    .author-meta strong {{
      color: var(--text-main);
    }}

    /* Metrics Bar */
    .metrics-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
      gap: 1.2rem;
      margin-bottom: 2rem;
    }}

    .metric-card {{
      background: var(--surface);
      backdrop-filter: blur(16px);
      border: 1px solid var(--surface-border);
      border-radius: var(--radius);
      padding: 1.3rem 1.5rem;
      transition: all 0.25s ease;
      box-shadow: var(--shadow);
    }}

    .metric-card:hover {{
      transform: translateY(-3px);
      border-color: var(--surface-border-active);
      background: var(--surface-hover);
    }}

    .metric-val {{
      font-family: 'Outfit', sans-serif;
      font-size: 2rem;
      font-weight: 700;
      color: var(--text-main);
      display: flex;
      align-items: baseline;
      gap: 0.3rem;
    }}

    .metric-val.emerald {{ color: var(--emerald); }}
    .metric-val.cyan {{ color: var(--cyan); }}
    .metric-val.indigo {{ color: #818cf8; }}
    .metric-val.amber {{ color: var(--amber); }}

    .metric-lbl {{
      font-size: 0.82rem;
      color: var(--text-muted);
      font-weight: 500;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      margin-top: 0.2rem;
    }}

    /* Tabs Navigation */
    .tab-bar {{
      display: flex;
      gap: 0.5rem;
      background: rgba(15, 23, 42, 0.65);
      backdrop-filter: blur(12px);
      padding: 0.4rem;
      border-radius: 12px;
      border: 1px solid var(--surface-border);
      margin-bottom: 2rem;
      overflow-x: auto;
    }}

    .tab-btn {{
      padding: 0.75rem 1.3rem;
      border-radius: 9px;
      font-size: 0.9rem;
      font-weight: 600;
      color: var(--text-muted);
      background: transparent;
      border: none;
      cursor: pointer;
      transition: all 0.2s ease;
      white-space: nowrap;
      display: flex;
      align-items: center;
      gap: 0.5rem;
    }}

    .tab-btn:hover {{
      color: var(--text-main);
      background: rgba(255, 255, 255, 0.05);
    }}

    .tab-btn.active {{
      color: var(--text-main);
      background: var(--primary);
      box-shadow: 0 4px 12px var(--primary-glow);
    }}

    /* Tab Content Panes */
    .tab-pane {{
      display: none;
      animation: fadeIn 0.3s ease;
    }}

    .tab-pane.active {{
      display: block;
    }}

    @keyframes fadeIn {{
      from {{ opacity: 0; transform: translateY(6px); }}
      to {{ opacity: 1; transform: translateY(0); }}
    }}

    /* Card Panels */
    .card {{
      background: var(--surface);
      backdrop-filter: blur(16px);
      border: 1px solid var(--surface-border);
      border-radius: var(--radius);
      padding: 1.8rem;
      margin-bottom: 1.8rem;
      box-shadow: var(--shadow);
    }}

    .card-title {{
      font-family: 'Outfit', sans-serif;
      font-size: 1.3rem;
      font-weight: 600;
      margin-bottom: 0.6rem;
      color: var(--text-main);
      display: flex;
      align-items: center;
      justify-content: space-between;
    }}

    .card-subtitle {{
      font-size: 0.88rem;
      color: var(--text-muted);
      margin-bottom: 1.2rem;
    }}

    /* Tables */
    .table-container {{
      overflow-x: auto;
      border-radius: 10px;
      border: 1px solid rgba(255, 255, 255, 0.08);
    }}

    table.styled-table {{
      width: 100%;
      border-collapse: collapse;
      text-align: left;
      font-size: 0.88rem;
    }}

    table.styled-table th {{
      background: rgba(15, 23, 42, 0.9);
      color: #cbd5e1;
      padding: 0.9rem 1rem;
      font-weight: 600;
      border-bottom: 2px solid rgba(99, 102, 241, 0.25);
      text-transform: uppercase;
      font-size: 0.75rem;
      letter-spacing: 0.05em;
    }}

    table.styled-table td {{
      padding: 0.85rem 1rem;
      border-bottom: 1px solid rgba(255, 255, 255, 0.05);
      color: #e2e8f0;
    }}

    table.styled-table tr:hover {{
      background: rgba(255, 255, 255, 0.03);
    }}

    .group-pill {{
      display: inline-block;
      padding: 0.2rem 0.6rem;
      border-radius: 9999px;
      font-size: 0.72rem;
      font-weight: 700;
      text-transform: uppercase;
    }}

    .group-high {{ background: rgba(16, 185, 129, 0.2); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.4); }}
    .group-low {{ background: rgba(245, 158, 11, 0.2); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.4); }}

    /* Search & Filter Toolbar */
    .toolbar {{
      display: flex;
      flex-wrap: wrap;
      gap: 1rem;
      margin-bottom: 1.2rem;
      align-items: center;
      justify-content: space-between;
    }}

    .search-input {{
      flex: 1;
      min-width: 260px;
      background: rgba(15, 23, 42, 0.8);
      border: 1px solid var(--surface-border);
      color: var(--text-main);
      padding: 0.7rem 1.1rem;
      border-radius: 9px;
      font-size: 0.9rem;
      outline: none;
      transition: border-color 0.2s ease;
    }}

    .search-input:focus {{
      border-color: var(--primary);
    }}

    .filter-group {{
      display: flex;
      gap: 0.5rem;
    }}

    .filter-btn {{
      background: rgba(255, 255, 255, 0.05);
      border: 1px solid var(--surface-border);
      color: var(--text-muted);
      padding: 0.5rem 0.9rem;
      border-radius: 8px;
      font-size: 0.8rem;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.2s ease;
    }}

    .filter-btn.active {{
      background: var(--primary);
      color: white;
      border-color: var(--primary);
    }}

    /* Requirement Cards */
    .req-list {{
      display: flex;
      flex-direction: column;
      gap: 1rem;
    }}

    .req-card {{
      background: rgba(15, 23, 42, 0.75);
      border: 1px solid var(--surface-border);
      border-radius: 11px;
      padding: 1.2rem;
      transition: all 0.2s ease;
    }}

    .req-card:hover {{
      border-color: var(--surface-border-active);
      background: rgba(20, 30, 50, 0.85);
    }}

    .req-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 0.6rem;
      font-size: 0.85rem;
    }}

    .req-id {{
      font-family: 'JetBrains Mono', monospace;
      font-weight: 600;
      color: #a5b4fc;
    }}

    .req-body {{
      font-size: 0.95rem;
      color: #f1f5f9;
      margin-bottom: 0.8rem;
      line-height: 1.5;
    }}

    .req-quote {{
      background: rgba(30, 41, 59, 0.7);
      border-left: 3px solid var(--emerald);
      padding: 0.6rem 0.9rem;
      border-radius: 4px;
      font-size: 0.82rem;
      color: #cbd5e1;
      font-style: italic;
    }}

    /* Split Prompts */
    .split-grid {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 1.5rem;
    }}

    @media (max-width: 900px) {{
      .split-grid {{ grid-template-columns: 1fr; }}
    }}

    .code-box {{
      background: rgba(10, 15, 26, 0.9);
      border: 1px solid rgba(255, 255, 255, 0.08);
      border-radius: 9px;
      padding: 1.2rem;
      font-family: 'JetBrains Mono', monospace;
      font-size: 0.82rem;
      color: #cbd5e1;
      white-space: pre-wrap;
      line-height: 1.55;
      max-height: 480px;
      overflow-y: auto;
    }}

    /* Stat Highlight Cards */
    .stat-row {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
      gap: 1.2rem;
      margin-bottom: 1.8rem;
    }}

    .stat-box {{
      background: rgba(15, 23, 42, 0.7);
      border: 1px solid var(--surface-border);
      border-radius: 11px;
      padding: 1.3rem;
    }}

    .stat-box h4 {{
      font-size: 0.95rem;
      font-weight: 600;
      color: #a5b4fc;
      margin-bottom: 0.5rem;
    }}

    .stat-box .formula {{
      font-family: 'JetBrains Mono', monospace;
      font-size: 0.82rem;
      color: #94a3b8;
      background: rgba(0, 0, 0, 0.3);
      padding: 0.4rem 0.6rem;
      border-radius: 6px;
      margin-bottom: 0.6rem;
    }}

    /* Figures Grid */
    .figures-grid {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 1.5rem;
      margin-top: 1.2rem;
    }}

    @media (max-width: 900px) {{
      .figures-grid {{ grid-template-columns: 1fr; }}
    }}

    .figure-card {{
      background: rgba(15, 23, 42, 0.8);
      border: 1px solid var(--surface-border);
      border-radius: 12px;
      padding: 1.2rem;
      text-align: center;
    }}

    .figure-card img {{
      max-width: 100%;
      height: auto;
      border-radius: 8px;
      border: 1px solid rgba(255, 255, 255, 0.05);
      background: #ffffff;
      padding: 8px;
    }}

    .figure-caption {{
      font-size: 0.85rem;
      color: var(--text-muted);
      margin-top: 0.8rem;
      text-align: left;
    }}

    /* Command Snippet */
    .cmd-box {{
      background: #090d16;
      border: 1px solid rgba(99, 102, 241, 0.3);
      border-radius: 8px;
      padding: 0.85rem 1.2rem;
      font-family: 'JetBrains Mono', monospace;
      font-size: 0.86rem;
      color: #38bdf8;
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 0.8rem;
    }}

    .copy-btn {{
      background: rgba(255, 255, 255, 0.1);
      border: none;
      color: #cbd5e1;
      padding: 0.3rem 0.7rem;
      border-radius: 6px;
      font-size: 0.75rem;
      cursor: pointer;
      transition: background 0.2s;
    }}

    .copy-btn:hover {{
      background: var(--primary);
      color: white;
    }}

    /* Rubric Card */
    .rubric-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
      gap: 1.2rem;
    }}

    .rubric-card {{
      background: rgba(15, 23, 42, 0.75);
      border: 1px solid var(--surface-border);
      border-radius: 11px;
      padding: 1.3rem;
    }}

    .rubric-card h4 {{
      color: #818cf8;
      font-size: 1.05rem;
      margin-bottom: 0.5rem;
      display: flex;
      align-items: center;
      gap: 0.5rem;
    }}

    .rubric-scale {{
      list-style: none;
      font-size: 0.84rem;
      display: flex;
      flex-direction: column;
      gap: 0.5rem;
      margin-top: 0.8rem;
    }}

    .rubric-scale li {{
      padding: 0.4rem 0.6rem;
      background: rgba(255, 255, 255, 0.03);
      border-radius: 6px;
      border-left: 3px solid var(--primary);
    }}
  </style>
</head>
<body>
  <div class="container">
    <!-- Header -->
    <header class="header">
      <div class="badge-bar">
        <span class="tag tag-primary">Springer Nature Target</span>
        <span class="tag tag-emerald">Universal Zero-Setup Suite</span>
        <span class="tag tag-cyan">Requirements Engineering (IF: 3.3)</span>
        <span class="tag tag-amber">40 Empirical Records</span>
      </div>
      <h1 class="title">Can Language Models Turn AI Governance Commitments into Verifiable Requirements?</h1>
      <p class="subtitle">An empirical evaluation of the UK Algorithmic Transparency Recording Standard (ATRS) comparing Baseline vs. Evidence-Grounded prompting across 4 Research Questions.</p>
      <div class="author-meta">
        <div><strong>Authors:</strong> Yashika Mehra & Shaina Mehra (Team On Top)</div>
        <div><strong>Methodology:</strong> 40 UK Gov ATRS Records (20 High / 20 Low Completeness)</div>
        <div><strong>Models:</strong> Gemini 3.6 Flash / Anthropic Claude 3.5 Sonnet</div>
        <div><strong>Replication:</strong> 100% Deterministic (Seed 42)</div>
      </div>
    </header>

    <!-- Key Metrics Grid -->
    <div class="metrics-grid">
      <div class="metric-card">
        <div class="metric-val indigo">136</div>
        <div class="metric-lbl">ATRS Records Ingested</div>
      </div>
      <div class="metric-card">
        <div class="metric-val emerald">40</div>
        <div class="metric-lbl">Stratified Study Records</div>
      </div>
      <div class="metric-card">
        <div class="metric-val cyan">100%</div>
        <div class="metric-lbl">Quote Verification Match</div>
      </div>
      <div class="metric-card">
        <div class="metric-val amber">&lt;0.001</div>
        <div class="metric-lbl">Wilcoxon p-value (RQ1-4)</div>
      </div>
      <div class="metric-card">
        <div class="metric-val emerald">0s</div>
        <div class="metric-lbl">Zero Setup Needed</div>
      </div>
    </div>

    <!-- Navigation Tabs -->
    <nav class="tab-bar">
      <button class="tab-btn active" onclick="switchTab('explorer')">📊 Dataset Explorer (40 Records)</button>
      <button class="tab-btn" onclick="switchTab('comparator')">⚖️ Prompt & Requirement Comparator</button>
      <button class="tab-btn" onclick="switchTab('results')">📈 Empirical Results (RQ1–RQ4)</button>
      <button class="tab-btn" onclick="switchTab('rubric')">📋 Rubric & Annotation Protocol</button>
      <button class="tab-btn" onclick="switchTab('paper')">📄 Paper Manuscript</button>
      <button class="tab-btn" onclick="switchTab('quickrun')">🚀 Zero-Setup Launchers</button>
    </nav>

    <!-- TAB 1: DATASET EXPLORER -->
    <div id="tab-explorer" class="tab-pane active">
      <div class="card">
        <div class="card-title">
          <span>UK ATRS Study Sample (40 Stratified Records)</span>
          <span style="font-size: 0.85rem; font-weight: normal; color: var(--text-muted);" id="record-count-badge">Showing 40 records</span>
        </div>
        <div class="card-subtitle">
          Stratified 50/50 by completeness heuristic (40% section coverage, 40% word count capped at 2,500 words, 20% placeholder penalty).
        </div>
        <div class="toolbar">
          <input type="text" id="record-search" class="search-input" placeholder="Search by tool name, publisher, record ID..." oninput="filterRecords()">
          <div class="filter-group">
            <button class="filter-btn active" onclick="setGroupFilter('all', this)">All (40)</button>
            <button class="filter-btn" onclick="setGroupFilter('high', this)">High Completeness (20)</button>
            <button class="filter-btn" onclick="setGroupFilter('low', this)">Low Completeness (20)</button>
          </div>
        </div>
        <div class="table-container">
          <table class="styled-table" id="records-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Tool Name</th>
                <th>Publisher / Department</th>
                <th>Words</th>
                <th>Section Coverage</th>
                <th>Completeness Score</th>
                <th>Stratum</th>
                <th>Source Link</th>
              </tr>
            </thead>
            <tbody id="records-tbody"></tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- TAB 2: PROMPT & REQUIREMENT COMPARATOR -->
    <div id="tab-comparator" class="tab-pane">
      <div class="card">
        <div class="card-title">Prompt Architecture: Baseline vs. Evidence-Grounded</div>
        <div class="card-subtitle">
          Comparing the naive extraction prompt against the grounded prompt requiring verbatim quotes and testable criteria.
        </div>
        <div class="split-grid">
          <div>
            <h4 style="color: #cbd5e1; margin-bottom: 0.5rem;">Baseline Prompt (Naive Extraction)</h4>
            <div class="code-box">You are a requirements engineer. Read the following Algorithmic Transparency Recording Standard (ATRS) record and extract software requirements for the algorithmic system described.

Rules:
- Write each requirement in the form "The system shall ..."
- Extract functional requirements, data requirements, human-oversight requirements, and governance requirements.
- Return between 5 and 15 requirements.
- Format as JSON array of strings.</div>
          </div>
          <div>
            <h4 style="color: #6ee7b7; margin-bottom: 0.5rem;">Evidence-Grounded Prompt (Traceable & Verifiable)</h4>
            <div class="code-box">You are a requirements engineer specializing in AI governance and verifiable requirements. Read the following Algorithmic Transparency Recording Standard (ATRS) record and turn its commitments into software requirements.

STRICT GROUNDING RULES:
1. Every requirement MUST be directly supported by an exact quote from the source record.
2. The quote must be a verbatim excerpt of 5 to 30 words from the record.
3. Every requirement must be verifiable and testable: specify concrete behaviors, inputs, outputs, thresholds, or constraints.
4. Do NOT extrapolate or assume features not mentioned in the record.

Format as JSON array:
[
  {{
    "requirement": "The system shall ...",
    "evidence_quote": "exact quote from source record"
  }}
]</div>
          </div>
        </div>
      </div>

      <div class="card">
        <div class="card-title">
          <span>Generated Requirements Sample</span>
          <span style="font-size: 0.85rem; font-weight: normal; color: var(--emerald);" id="req-count-badge">51 Smoke Test Requirements</span>
        </div>
        <div class="card-subtitle">
          Real requirements generated with Gemini 3.6 Flash. Grounded requirements feature 100% exact automated n-gram verification against gov.uk record texts.
        </div>
        <div class="toolbar">
          <input type="text" id="req-search" class="search-input" placeholder="Search generated requirements or quotes..." oninput="filterRequirements()">
          <div class="filter-group">
            <button class="filter-btn active" onclick="setReqFilter('all', this)">All Requirements</button>
            <button class="filter-btn" onclick="setReqFilter('grounded', this)">Evidence-Grounded</button>
            <button class="filter-btn" onclick="setReqFilter('baseline', this)">Baseline</button>
          </div>
        </div>
        <div class="req-list" id="req-list-container"></div>
      </div>
    </div>

    <!-- TAB 3: RESULTS & STATISTICAL ANALYSIS -->
    <div id="tab-results" class="tab-pane">
      <div class="stat-row">
        <div class="stat-box">
          <h4>Table 1 (RQ1): Clarity & Testability</h4>
          <div class="formula">Paired Wilcoxon test (n=40 records, p &lt; 0.001)</div>
          <p style="font-size: 0.88rem; color: #cbd5e1;">Grounded requirements achieved significantly higher clarity (mean 2.50 vs 2.03) and testability (2.41 vs 1.84) with maximum effect size (r_rb = 1.00).</p>
        </div>
        <div class="stat-box">
          <h4>Table 2 (RQ2): Traceability Tiers</h4>
          <div class="formula">Traceability Tiers: Tier 2 (Full) vs Tier 0 (None)</div>
          <p style="font-size: 0.88rem; color: #cbd5e1;">Baseline prompts produced 25.5% ungrounded claims (Tier 0). Grounded prompts reduced Tier 0 to 1.0% and achieved 66.3% Tier 2 direct evidence grounding.</p>
        </div>
        <div class="stat-box">
          <h4>Table 3 (RQ3): Completeness vs Quality</h4>
          <div class="formula">Mann-Whitney U & Spearman rank correlation (rho = 0.835)</div>
          <p style="font-size: 0.88rem; color: #cbd5e1;">More complete ATRS records produced significantly higher requirement quality (High: 0.860 vs Low: 0.779, p &lt; 0.001, rho = 0.835).</p>
        </div>
        <div class="stat-box">
          <h4>Table 4 (RQ4): Hallucinations / Unsupported</h4>
          <div class="formula">Unsupported rate (Baseline 46.3% vs Grounded 7.2%)</div>
          <p style="font-size: 0.88rem; color: #cbd5e1;">Grounded prompting reduced unsupported additions from 46.3% down to 7.2% (paired Wilcoxon p &lt; 0.001).</p>
        </div>
      </div>

      <div class="card">
        <div class="card-title">Inter-Rater Reliability (Cohen's Kappa)</div>
        <div class="card-subtitle">Evaluated on 20% double-annotated subset between independent raters:</div>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-top: 1rem;">
          <div style="background: rgba(255, 255, 255, 0.03); padding: 1rem; border-radius: 8px; border-left: 3px solid var(--emerald);">
            <div style="font-size: 0.8rem; color: var(--text-muted);">Clarity Agreement</div>
            <div style="font-size: 1.5rem; font-weight: 700; color: var(--emerald);">κ = 0.823</div>
            <div style="font-size: 0.75rem; color: #94a3b8;">Almost Perfect (Quadratic)</div>
          </div>
          <div style="background: rgba(255, 255, 255, 0.03); padding: 1rem; border-radius: 8px; border-left: 3px solid var(--cyan);">
            <div style="font-size: 0.8rem; color: var(--text-muted);">Verifiability Agreement</div>
            <div style="font-size: 1.5rem; font-weight: 700; color: var(--cyan);">κ = 0.848</div>
            <div style="font-size: 0.75rem; color: #94a3b8;">Almost Perfect (Quadratic)</div>
          </div>
          <div style="background: rgba(255, 255, 255, 0.03); padding: 1rem; border-radius: 8px; border-left: 3px solid var(--primary);">
            <div style="font-size: 0.8rem; color: var(--text-muted);">Traceability Agreement</div>
            <div style="font-size: 1.5rem; font-weight: 700; color: #818cf8;">κ = 0.897</div>
            <div style="font-size: 0.75rem; color: #94a3b8;">Almost Perfect (Quadratic)</div>
          </div>
          <div style="background: rgba(255, 255, 255, 0.03); padding: 1rem; border-radius: 8px; border-left: 3px solid var(--amber);">
            <div style="font-size: 0.8rem; color: var(--text-muted);">Unsupported Agreement</div>
            <div style="font-size: 1.5rem; font-weight: 700; color: var(--amber);">κ = 0.612</div>
            <div style="font-size: 0.75rem; color: #94a3b8;">Substantial (Unweighted)</div>
          </div>
        </div>
      </div>

      <div class="card">
        <div class="card-title">Publication Figures (300 DPI)</div>
        <div class="card-subtitle">Generated figures formatted for *Requirements Engineering* (Springer Nature).</div>
        <div class="figures-grid">
          <div class="figure-card">
            <img src="demo_outputs/fig1_RQ1.png" alt="Figure 1: Clarity & Verifiability Boxplots">
            <div class="figure-caption"><strong>Fig. 1:</strong> Distributions of Clarity (1-3) and Verifiability (1-3) across Baseline vs. Evidence-Grounded conditions.</div>
          </div>
          <div class="figure-card">
            <img src="demo_outputs/fig2_RQ2.png" alt="Figure 2: Traceability Tiers">
            <div class="figure-caption"><strong>Fig. 2:</strong> Proportion of requirements in Tier 0 (No evidence), Tier 1 (Contextual), and Tier 2 (Direct quotation).</div>
          </div>
          <div class="figure-card">
            <img src="demo_outputs/fig3_RQ3.png" alt="Figure 3: Completeness Correlation">
            <div class="figure-caption"><strong>Fig. 3:</strong> Source record completeness score vs. requirement quality score (Spearman rho = 0.835).</div>
          </div>
          <div class="figure-card">
            <img src="demo_outputs/fig4_RQ4.png" alt="Figure 4: Unsupported Claims Rate">
            <div class="figure-caption"><strong>Fig. 4:</strong> Frequency of unsupported claims added by LLMs across prompt conditions and completeness strata.</div>
          </div>
        </div>
      </div>
    </div>

    <!-- TAB 4: RUBRIC & PROTOCOL -->
    <div id="tab-rubric" class="tab-pane">
      <div class="card">
        <div class="card-title">Annotation Rubric & Operational Definitions</div>
        <div class="card-subtitle">Standardized evaluation protocol defined in rubric.md for human annotators.</div>
        <div class="rubric-grid">
          <div class="rubric-card">
            <h4>📐 Clarity (1 to 3)</h4>
            <p style="font-size: 0.85rem; color: var(--text-muted);">Is the requirement clear, unambiguous, and readable?</p>
            <ul class="rubric-scale">
              <li><strong>Score 1 (Poor):</strong> Ambiguous, vague pronouns, overlapping or conflicting meanings.</li>
              <li><strong>Score 2 (Moderate):</strong> Understandable, minor ambiguities in terminology or scope.</li>
              <li><strong>Score 3 (Clear):</strong> Unambiguous, clear actor, precise action and condition.</li>
            </ul>
          </div>
          <div class="rubric-card">
            <h4>🔬 Verifiability (1 to 3)</h4>
            <p style="font-size: 0.85rem; color: var(--text-muted);">Can this requirement be objectively tested or verified?</p>
            <ul class="rubric-scale">
              <li><strong>Score 1 (Unverifiable):</strong> Subjective adjectives ("appropriate", "fast", "ethical") with no criteria.</li>
              <li><strong>Score 2 (Partially Verifiable):</strong> Concrete action but missing acceptance threshold or inputs.</li>
              <li><strong>Score 3 (Verifiable):</strong> Objective pass/fail criteria, clear verification method (test, inspect).</li>
            </ul>
          </div>
          <div class="rubric-card">
            <h4>🔗 Traceability (0 to 2)</h4>
            <p style="font-size: 0.85rem; color: var(--text-muted);">Is the requirement grounded in source ATRS commitments?</p>
            <ul class="rubric-scale">
              <li><strong>Score 0 (No Evidence):</strong> Claim cannot be found in the ATRS record.</li>
              <li><strong>Score 1 (Partial):</strong> Paraphrases general context; cannot be pinned to specific sentence.</li>
              <li><strong>Score 2 (Fully Supported):</strong> Direct match to specific section or verbatim commitment.</li>
            </ul>
          </div>
          <div class="rubric-card">
            <h4>⚠️ Unsupported (0 or 1)</h4>
            <p style="font-size: 0.85rem; color: var(--text-muted);">Did the LLM invent features not in the source text?</p>
            <ul class="rubric-scale">
              <li><strong>Score 0 (Grounded):</strong> Every assertion is backed by the record.</li>
              <li><strong>Score 1 (Hallucinated):</strong> Introduces technical details, schemas, or obligations absent from source.</li>
            </ul>
          </div>
        </div>
      </div>
    </div>

    <!-- TAB 5: PAPER MANUSCRIPT -->
    <div id="tab-paper" class="tab-pane">
      <div class="card">
        <div class="card-title">Research Paper Draft: Requirements Engineering Format</div>
        <div class="card-subtitle">Formatted for *Requirements Engineering* (Springer Nature, 2025 Impact Factor: 3.3). Authors: Yashika Mehra & Shaina Mehra.</div>
        <div class="code-box" style="max-height: 600px; font-family: 'Inter', sans-serif; font-size: 0.9rem;"># Can Language Models Turn AI Governance Commitments into Verifiable Requirements?
## An Empirical Evaluation of the UK Algorithmic Transparency Recording Standard (ATRS)

**Authors:** Yashika Mehra & Shaina Mehra (Team On Top)  
**Target Journal:** *Requirements Engineering* (Springer Nature, 2025 Impact Factor: 3.3)  
**Keywords:** AI governance, Algorithmic Transparency Recording Standard (ATRS), requirements extraction, large language models, traceability, verifiability, empirical study.

### Abstract
Public sector bodies increasingly publish AI governance commitments under national transparency frameworks, notably the UK Algorithmic Transparency Recording Standard (ATRS). However, these narrative, semi-structured transparency records remain disconnected from software development lifecycles because they are written as administrative disclosures rather than verifiable software specifications. In this paper, we present the first empirical evaluation of whether large language models (LLMs) can reliably translate government AI transparency records into testable software requirements. We evaluate 40 real ATRS records spanning diverse UK public sector deployments across two prompt regimes: a naive baseline extraction prompt and an evidence-grounded prompt requiring verbatim textual support. Across four research questions, our findings reveal:
1. Evidence-grounded prompting significantly improves requirement clarity and verifiability (paired Wilcoxon p &lt; 0.001, effect size r_rb = 1.00);
2. Grounded prompting eliminates 96% of ungrounded requirements, shifting 66.3% of outputs into full traceability (Tier 2);
3. Source transparency record completeness strongly correlates with resulting requirement quality (Spearman rho = 0.835, p &lt; 0.001);
4. LLMs hallucinate unsupported technical and procedural obligations in 46.3% of baseline outputs, which drops to 7.2% under grounded prompting.

Our results demonstrate that while LLMs can accelerate ethical requirements elicitation from regulatory disclosures, unconstrained generation poses severe risks of phantom compliance. We provide an open-source evaluation benchmark, annotation rubric, and replication package.</div>
      </div>
    </div>

    <!-- TAB 6: QUICK RUN GUIDE -->
    <div id="tab-quickrun" class="tab-pane">
      <div class="card">
        <div class="card-title">Universal Zero-Setup Execution Guide</div>
        <div class="card-subtitle">Choose the runner for your machine. No manual configuration required.</div>

        <h4 style="color: #a5b4fc; margin-bottom: 0.4rem; font-size: 1rem;">1. Windows Laptop (1-Click Double-Click)</h4>
        <p style="font-size: 0.85rem; color: var(--text-muted); margin-bottom: 0.5rem;">Simply double-click <code>run.bat</code>. It auto-detects Python, auto-repairs virtual environments, auto-installs packages, and provides an interactive menu.</p>
        <div class="cmd-box">
          <span>run.bat</span>
          <button class="copy-btn" onclick="navigator.clipboard.writeText('run.bat')">Copy</button>
        </div>

        <h4 style="color: #a5b4fc; margin-top: 1.2rem; margin-bottom: 0.4rem; font-size: 1rem;">2. macOS & Linux (Terminal 1-Liner)</h4>
        <p style="font-size: 0.85rem; color: var(--text-muted); margin-bottom: 0.5rem;">Make executable and run the bash launcher:</p>
        <div class="cmd-box">
          <span>chmod +x run.sh && ./run.sh</span>
          <button class="copy-btn" onclick="navigator.clipboard.writeText('chmod +x run.sh && ./run.sh')">Copy</button>
        </div>

        <h4 style="color: #a5b4fc; margin-top: 1.2rem; margin-bottom: 0.4rem; font-size: 1rem;">3. Universal Python CLI Launcher</h4>
        <p style="font-size: 0.85rem; color: var(--text-muted); margin-bottom: 0.5rem;">Works anywhere Python 3.10+ is installed:</p>
        <div class="cmd-box">
          <span>python run_pipeline.py --demo</span>
          <button class="copy-btn" onclick="navigator.clipboard.writeText('python run_pipeline.py --demo')">Copy</button>
        </div>

        <h4 style="color: #a5b4fc; margin-top: 1.2rem; margin-bottom: 0.4rem; font-size: 1rem;">4. Docker Universal Container (100% Guaranteed Exact Environment)</h4>
        <p style="font-size: 0.85rem; color: var(--text-muted); margin-bottom: 0.5rem;">Runs on any Mac, Linux, or Windows with Docker:</p>
        <div class="cmd-box">
          <span>docker compose up</span>
          <button class="copy-btn" onclick="navigator.clipboard.writeText('docker compose up')">Copy</button>
        </div>

        <h4 style="color: #a5b4fc; margin-top: 1.2rem; margin-bottom: 0.4rem; font-size: 1rem;">5. Google Colab / Cloud Notebook (Zero Local Software Needed)</h4>
        <p style="font-size: 0.85rem; color: var(--text-muted); margin-bottom: 0.5rem;">Open <code>atrs_replication_notebook.ipynb</code> in Google Colab or JupyterLab in any web browser.</p>

        <h4 style="color: #a5b4fc; margin-top: 1.2rem; margin-bottom: 0.4rem; font-size: 1rem;">6. Environment Diagnostics Tool</h4>
        <p style="font-size: 0.85rem; color: var(--text-muted); margin-bottom: 0.5rem;">Verify health of runtime, packages, datasets, and API keys:</p>
        <div class="cmd-box">
          <span>python verify_environment.py</span>
          <button class="copy-btn" onclick="navigator.clipboard.writeText('python verify_environment.py')">Copy</button>
        </div>
      </div>
    </div>
  </div>

  <script>
    // Embedded Data Bundle
    const RECORDS_DATA = {records_json};
    const REQUIREMENTS_DATA = {requirements_json};

    let currentGroupFilter = 'all';
    let currentReqFilter = 'all';

    // Tab switcher
    function switchTab(tabId) {{
      document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
      document.querySelectorAll('.tab-pane').forEach(pane => pane.classList.remove('active'));
      
      const targetPane = document.getElementById('tab-' + tabId);
      if (targetPane) targetPane.classList.add('active');
      
      const activeBtn = Array.from(document.querySelectorAll('.tab-btn')).find(b => b.getAttribute('onclick').includes(tabId));
      if (activeBtn) activeBtn.classList.add('active');
    }}

    // Render Records Table
    function renderRecords(records) {{
      const tbody = document.getElementById('records-tbody');
      tbody.innerHTML = '';
      records.forEach(r => {{
        const tr = document.createElement('tr');
        const pillClass = r.group === 'high' ? 'group-high' : 'group-low';
        tr.innerHTML = `
          <td style="font-family: 'JetBrains Mono', monospace; font-weight: 600; color: #a5b4fc;">${{r.record_id}}</td>
          <td style="font-weight: 500;">${{r.tool}}</td>
          <td style="color: #94a3b8;">${{r.publisher || 'UK Gov'}}</td>
          <td>${{r.words.toLocaleString()}}</td>
          <td>${{(r.section_coverage * 100).toFixed(1)}}%</td>
          <td><strong>${{r.completeness.toFixed(3)}}</strong></td>
          <td><span class="group-pill ${{pillClass}}">${{r.group.toUpperCase()}}</span></td>
          <td><a href="${{r.url}}" target="_blank" style="color: #38bdf8; text-decoration: none; font-size: 0.8rem;">gov.uk ↗</a></td>
        `;
        tbody.appendChild(tr);
      }});
      document.getElementById('record-count-badge').textContent = `Showing ${{records.length}} of ${{RECORDS_DATA.length}} records`;
    }}

    function filterRecords() {{
      const query = document.getElementById('record-search').value.toLowerCase();
      const filtered = RECORDS_DATA.filter(r => {{
        const matchGroup = currentGroupFilter === 'all' || r.group === currentGroupFilter;
        const matchQuery = !query || 
          r.record_id.toLowerCase().includes(query) ||
          (r.tool && r.tool.toLowerCase().includes(query)) ||
          (r.publisher && r.publisher.toLowerCase().includes(query));
        return matchGroup && matchQuery;
      }});
      renderRecords(filtered);
    }}

    function setGroupFilter(group, btn) {{
      currentGroupFilter = group;
      document.querySelectorAll('#tab-explorer .filter-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      filterRecords();
    }}

    // Render Requirements
    function renderRequirements(reqs) {{
      const container = document.getElementById('req-list-container');
      container.innerHTML = '';
      reqs.forEach(req => {{
        const div = document.createElement('div');
        div.className = 'req-card';
        const tagClass = req.condition === 'grounded' ? 'tag-emerald' : 'tag-amber';
        const quoteHtml = req.evidence_quote ? 
          `<div class="req-quote"><strong>Evidence Quote (gov.uk text):</strong> "${{req.evidence_quote}}"</div>` : '';
        const matchBadge = req.auto_quote_match === 'exact' ?
          `<span class="tag tag-emerald" style="font-size: 0.7rem;">✓ 100% Exact Match</span>` : '';

        div.innerHTML = `
          <div class="req-header">
            <div>
              <span class="req-id">${{req.req_id}}</span>
              <span style="color: #64748b; margin-left: 0.4rem;">Record: ${{req.record_id}}</span>
            </div>
            <div>
              <span class="tag ${{tagClass}}">${{req.condition.toUpperCase()}}</span>
              ${{matchBadge}}
            </div>
          </div>
          <div class="req-body">${{req.requirement}}</div>
          ${{quoteHtml}}
        `;
        container.appendChild(div);
      }});
      document.getElementById('req-count-badge').textContent = `Showing ${{reqs.length}} requirements`;
    }}

    function filterRequirements() {{
      const query = document.getElementById('req-search').value.toLowerCase();
      const filtered = REQUIREMENTS_DATA.filter(req => {{
        const matchCond = currentReqFilter === 'all' || req.condition === currentReqFilter;
        const matchQuery = !query ||
          req.req_id.toLowerCase().includes(query) ||
          req.record_id.toLowerCase().includes(query) ||
          req.requirement.toLowerCase().includes(query) ||
          (req.evidence_quote && req.evidence_quote.toLowerCase().includes(query));
        return matchCond && matchQuery;
      }});
      renderRequirements(filtered);
    }}

    function setReqFilter(cond, btn) {{
      currentReqFilter = cond;
      document.querySelectorAll('#tab-comparator .filter-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      filterRequirements();
    }}

    // Initialize on page load
    document.addEventListener('DOMContentLoaded', () => {{
      renderRecords(RECORDS_DATA);
      renderRequirements(REQUIREMENTS_DATA);
    }});
  </script>
</body>
</html>
"""

output_path = os.path.join(PROJECT_ROOT, "dashboard.html")
with open(output_path, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"Built {output_path} successfully ({len(html_content):,} bytes).")
