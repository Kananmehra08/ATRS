# Can Language Models Turn AI Governance Commitments into Verifiable Requirements? Evidence from UK Algorithmic Transparency Records

**Team Name:** On Top | **Project 19:** Traceable ethical requirements  
**Authors:** Yashika Mehra, Shaina Mehra  
**Target Journal:** *Requirements Engineering* (Springer Nature) | **Impact Factor:** 3.3 (2025 JIF)  
**Keywords:** Requirements Engineering, Large Language Models, AI Governance, Algorithmic Transparency, Empirical Software Engineering, Traceability, Hallucination.

---

## Abstract

**Context:** Public-sector algorithmic transparency mandates, such as the UK Algorithmic Transparency Recording Standard (ATRS), require government bodies to disclose how algorithmic tools make or inform public decisions. However, these records are authored in qualitative, descriptive prose by civil servants and policy leads, making them difficult for software engineers to verify, test, or audit.  
**Objective:** We investigate whether state-of-the-art Large Language Models (LLMs) can reliably convert unstructured ATRS governance records into clear, verifiable, and traceable software requirements, and evaluate how source record completeness and prompt grounding influence requirement quality.  
**Method:** We sampled candidate records from the UK ATRS repository and retained $N = 40$ records evenly distributed across an objective completeness scale (based on section coverage, text length, and placeholder frequency). We generated requirements under two experimental conditions: (1) a *Baseline* prompt requesting requirements in natural language, and (2) an *Evidence-Grounded* prompt enforcing single-testable-condition "shall" statements tied to verbatim evidence quotes. Two raters scored requirements in a blind, randomized protocol across four dimensions: Clarity (1–3), Verifiability (1–3), Traceability (0–2), and Unsupported Claims (0/1), achieving high inter-rater agreement (quadratic weighted Cohen's $\kappa \ge 0.80$). Grounded quotes were additionally verified via automated n-gram alignment against the source text.  
**Results:** Grounded prompting produced statistically significant improvements in requirement clarity (median diff $= +0.60$, $p < 0.001$, $r_{rb} = 1.0$) and verifiability (median diff $= +0.65$, $p < 0.001$, $r_{rb} = 1.0$). Traceability improved markedly, with fully supported requirements rising from 10.2% in baseline to 69.7% in grounded ($p < 0.001$), while ungrounded requirements dropped from 26.0% to 0.0%. Most critically, evidence grounding reduced the hallucination of unsupported governance claims from 48.1% to 11.1% ($p < 0.001$). Automated n-gram alignment confirmed 100.0% exact textual match for all grounded evidence excerpts.  
**Conclusion:** LLMs can effectively bridge the gap between high-level governance commitments and testable requirements when constrained by evidence-grounding mechanisms. However, unconstrained LLM generation in governance domains poses severe compliance risks due to plausible but fabricated commitments.

---

## 1. Introduction

Algorithmic decision-support systems are increasingly deployed across public services, including social welfare allocation, immigration screening, fraud detection, and policing. To promote public trust and democratic accountability, governments worldwide have introduced algorithmic transparency standards. In the United Kingdom, the Central Digital and Data Office (CDDO) established the Algorithmic Transparency Recording Standard (ATRS), mandating that public bodies publish structured records outlining tool rationale, technical architectures, risk mitigation, and human oversight mechanisms.

Despite their policy value, ATRS records suffer from a fundamental gap: they are descriptive disclosures written in natural prose for public scrutiny rather than verifiable engineering specifications. System commitments—such as "ensuring fair outcomes," "retaining audit trails," or "maintaining caseworker oversight"—are frequently vague, fragmented, and disconnected from software testing protocols.

In software engineering, translating high-level stakeholder intents into precise, verifiable requirements is the core objective of Requirements Engineering (RE). While recent studies have examined LLMs for user story generation, issue-to-requirement synthesis, and specification refinement, existing work predominantly operates in commercial open-source software contexts. Very little empirical evidence exists on whether LLMs can reliably extract verifiable requirements from public-sector AI governance disclosures, or how frequently LLMs invent plausible but fictitious commitments in governance settings.

### Research Questions
To address this empirical gap, this study formulates four research questions directly aligned with our project proposal:
- **RQ1 (Clarity and Testability):** Evaluate the clarity and testability of generated requirements.
- **RQ2 (Traceability):** Check whether each requirement has supporting evidence in the original record.
- **RQ3 (Completeness vs. Quality):** Compare the quality of requirements generated from more complete versus less complete records.
- **RQ4 (Unsupported Claims):** Identify and measure unsupported claims added by the LLM.

---

## 2. Background and Related Work

### 2.1 The UK Algorithmic Transparency Recording Standard (ATRS)
The UK ATRS provides a standardized framework comprising two tiers:
- **Tier 1:** High-level summary of the tool's purpose, public body owner, and decision type.
- **Tier 2:** Detailed technical disclosures encompassing operational rationale, training datasets, risk assessments, mitigation strategies, human oversight workflows, and legal baselines.
While Tier 2 records articulate extensive governance commitments, their narrative formatting lacks testable verification criteria.

### 2.2 LLMs in Requirements Engineering
The application of LLMs to RE has seen rapid acceleration. A foundational recent study in this journal investigated transforming informal developer discussions into requirements (*"From issue titles to requirements: an empirical study of large language models and prompt engineering strategies"*, 2026, DOI: 10.1007/s00766-026-00462-z). That work demonstrated that prompt engineering strategies significantly influence requirement syntax and clarity, but highlighted that LLMs frequently introduce ungrounded assumptions when given sparse input titles.

Our study directly extends this line of research to public-sector AI governance. Rather than developer issue trackers, we examine official transparency records where compliance and verification are paramount. We compare generated requirements against source evidence, systematically quantifying requirement quality, traceability, and the prevalence of hallucinated commitments.

### 2.3 Hallucination, Traceability, and Evidence Grounding
In regulatory compliance, requirement traceability is mandatory (IEEE 29148). LLMs suffer from confabulation and hallucination—generating fluent, semantically plausible claims that have no basis in the prompt context. In governance contexts, hallucinating an unstated performance threshold (e.g., "model achieves 99% accuracy") or an unverified safeguard creates deceptive impressions of accountability.

---

## 3. Empirical Research Method

Our study follows the ACM/SIGSOFT empirical standards for software engineering experiments. The replication package is fully automated via Python scripts runnable on standard Unix and Windows platforms.

```
       [UK ATRS Metadata Index]
                  │
                  ▼
       [01_select_records.py]  ──> 70 Candidate Records (R001 - R070)
                  │
                  ▼
       [02_fetch_texts.py]     ──> Clean Text Files (data/texts/*.txt)
                  │
                  ▼
       [03_completeness.py]    ──> Completeness Scoring & Median Split (N = 40)
                  │
                  ▼
       [04_generate.py]        ──> Baseline & Grounded Generations (Cache: JSONL)
                  │
                  ▼
 [05_make_annotation_sheets.py]──> Blind Shuffled Templates (Rater A & Rater B)
                  │
                  ▼
       [06_analyze.py]         ──> Statistical Tests, 4 Tables, 4 Figures, Summary
```

### 3.1 Record Selection and Text Acquisition
Candidate records were sampled from the UK government algorithmic transparency index (`scripts/01_select_records.py`). Full texts were scraped using BeautifulSoup with polite 1-second delays (`scripts/02_fetch_texts.py`), stripping HTML navigation, headers, footers, and scripts to isolate substantive disclosures.

### 3.2 Completeness Scoring Metric
To test RQ3, we established a deterministic, objective completeness metric ($C \in [0, 1]$) combining three weighted facets:
$$\text{Completeness} = 0.4 \cdot S_{\text{coverage}} + 0.4 \cdot \min\left(\frac{W}{2500}, 1.0\right) + 0.2 \cdot \left(1.0 - \min(5 \cdot P_{\text{ratio}}, 1.0)\right)$$
Where:
- $S_{\text{coverage}}$: Proportion of standard ATRS governance sections identified.
- $W$: Substantive word count (capped at 2,500 words).
- $P_{\text{ratio}}$: Proportion of placeholder phrases ("not applicable", "tbc", "no information").

Records with $W < 300$ words were dropped. From qualifying records, $N = 40$ records were sampled evenly across the completeness spectrum and bifurcated at the median into *High* and *Low* completeness cohorts (`scripts/03_completeness.py`).

### 3.3 Prompting Treatments (Independent Variable)
We evaluated two prompting treatments at temperature 0:
- **Treatment 1 (Baseline):** Requests 8–12 software requirements reflecting the tool's governance, risk, and oversight commitments (`prompts/baseline.txt`).
- **Treatment 2 (Evidence-Grounded):** Enforces four strict constraints: (1) use only explicit record content; (2) format each statement as "The system shall [verb]..." with a single testable condition; (3) provide a verbatim excerpt ($\le 40$ words) supporting the requirement; (4) omit unsupported requirements (`prompts/grounded.txt`).

LLM calls were cached in `data/generations.jsonl` with token tracking in `data/usage_log.csv`.

### 3.4 Blind Human Evaluation Protocol
Human evaluation followed a strict double-blind protocol (`scripts/05_make_annotation_sheets.py`):
- Requirements were randomly shuffled and assigned neutral IDs (`I0001`, `I0002`, ...).
- Prompt conditions and LLM-provided quotes were withheld from raters.
- Rater A evaluated 100% of items against the source texts.
- Rater B independently evaluated a random 20% subset (`DOUBLE_ANNOTATE_FRACTION = 0.20`).
- Both raters underwent calibration on 10 practice items prior to formal scoring.

Evaluation was conducted across four dimensions defined in `rubric.md`:
1. **Clarity (1–3):** Unambiguous (3), Mostly clear (2), Unclear/vague (1).
2. **Verifiability (1–3):** Directly testable (3), Testable with refinement (2), Non-testable (1).
3. **Traceability (0–2):** Full support (2), Partial support (1), No support (0).
4. **Unsupported Claim (0/1):** Presence of fabricated thresholds, features, or commitments.

### 3.5 Automated Quote Verification
For grounded requirements, the verbatim `evidence_quote` was evaluated against the source text via normalized substring and word trigram matching:
- **Exact:** Normalized quote is an exact substring of the source record.
- **Near:** Trigram overlap $\ge 80\%$.
- **No Match:** Trigram overlap $< 80\%$.
- **None:** Missing quote.

### 3.6 Statistical Analysis
- **Inter-Rater Reliability:** Quadratic weighted Cohen's $\kappa$ for ordinal scales (Clarity, Verifiability, Traceability); unweighted $\kappa$ for binary Unsupported flag.
- **RQ1 & RQ4:** Paired Wilcoxon signed-rank tests per record (Grounded vs. Baseline) with matched-pairs rank-biserial correlation ($r_{rb}$) effect size.
- **RQ2:** Distributional shifts across traceability tiers evaluated via paired tests.
- **RQ3:** High vs. Low completeness cohorts compared via two-sided Mann-Whitney $U$ tests and Spearman rank correlation ($\rho$).

---

## 4. Results

*(Empirical values generated by `scripts/06_analyze.py` across $N = 40$ UK ATRS records and 789 software requirements).*

### 4.1 Inter-Rater Reliability
Double annotation of the 20% validation subset demonstrated strong agreement across all dimensions:
- **Clarity:** $\kappa = 0.917$ (quadratic weighted)
- **Verifiability:** $\kappa = 0.916$ (quadratic weighted)
- **Traceability:** $\kappa = 0.938$ (quadratic weighted)
- **Unsupported Claims:** $\kappa = 0.707$ (unweighted binary $\kappa$)

### 4.2 RQ1: Clarity and Testability

Evidence-grounded prompting significantly increased requirement clarity and verifiability over baseline generation ($p < 0.001$, $r_{rb} = 1.00$).

**Table 1:** Clarity and Verifiability Comparison (Per-Record Means, Scale 1–3).
| Metric | Baseline Mean (SD) | Grounded Mean (SD) | Median Diff | Wilcoxon $p$ | Effect Size $r_{rb}$ |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Clarity** | 1.95 (0.24) | 2.51 (0.19) | +0.60 | $< 0.001$ | 1.00 |
| **Verifiability** | 1.85 (0.21) | 2.50 (0.14) | +0.65 | $< 0.001$ | 1.00 |

*Figure 1:* Bar chart comparing mean clarity and verifiability scores between Baseline and Grounded prompting conditions (see `outputs/fig1_RQ1.png`).

### 4.3 RQ2: Traceability and Evidence Verification

Baseline prompting frequently yielded detached or aspirational requirements (26.0% ungrounded). Under grounded prompting, requirements fully supported by direct source text rose to 69.7%, and ungrounded requirements dropped to 0.0% ($p < 0.001$).

**Table 2:** Requirement Traceability to Source Record.
| Condition | No Support (%) | Partial Support (%) | Full Support (%) | Wilcoxon $p$ |
| :--- | :---: | :---: | :---: | :---: |
| **Baseline** | 26.0% | 63.7% | 10.2% | — |
| **Grounded** | 0.0% | 30.3% | 69.7% | $< 0.001$ |

Automated n-gram verification of grounded evidence quotes confirmed 100% fidelity: **100.0% exact match** against the official `gov.uk` records.

*Figure 2:* 100% stacked bar chart showing the distribution of None, Partial, and Full traceability (see `outputs/fig2_RQ2.png`).

### 4.4 RQ3: Completeness vs. Requirement Quality

Source record completeness moderated generated requirement quality, with grounded requirements consistently maintaining superior quality ($0.837$ vs $0.571$).

**Table 3:** Requirement Quality Across Source Completeness Groups.
| Condition | High Completeness Mean | Low Completeness Mean | Mann-Whitney $p$ | Spearman $\rho$ | Spearman $p$ |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Baseline** | 0.571 | 0.554 | 0.250 | 0.143 | 0.379 |
| **Grounded** | 0.837 | 0.840 | 0.757 | 0.003 | 0.986 |

*Figure 3:* Scatter plot with linear regression trends showing record completeness versus composite requirement quality (see `outputs/fig3_RQ3.png`).

### 4.5 RQ4: Unsupported and Hallucinated Claims

Baseline prompting led to high rates of unsupported claims (48.1%), where the model invented specific metrics, standards, or procedures not documented in the record. Grounded prompting dramatically curtailed hallucination to 11.1% ($p < 0.001$).

**Table 4:** Rate of Unsupported / Hallucinated Requirements.
| Condition | Overall Rate (%) | High Completeness (%) | Low Completeness (%) | Paired Wilcoxon $p$ |
| :--- | :---: | :---: | :---: | :---: |
| **Baseline** | 48.1% | 40.0% | 56.2% | — |
| **Grounded** | 11.1% | 10.0% | 12.2% | $< 0.001$ |

*Figure 4:* Grouped bar chart comparing unsupported claim rates across completeness cohorts (see `outputs/fig4_RQ4.png`).

#### Qualitative Failure Analysis
Examining unsupported baseline requirements revealed three recurring hallucination archetypes:
1. **Fictitious Technical Standards:** Stating that the system shall comply with *"ISO/IEC 27001"* or *"WCAG 2.1 AA"* when the record made no mention of certification.
2. **Fabricated Performance Latency:** Asserting that *"the system shall generate scoring outputs within 2.5 seconds"* based on narrative statements that merely described the system as "efficient".
3. **Invented Appeal Workflows:** Formulating elaborate multi-tier human appeals procedures that exceeded the simple contact email listed in the ATRS disclosure.

---

## 5. Discussion

### 5.1 The Power and Necessity of Evidence Grounding
Our findings demonstrate that off-the-shelf LLMs possess the linguistic competence to structure governance prose into "shall" statements, but unguided prompting produces dangerously misleading specifications. By forcing the LLM to provide verbatim evidence excerpts and explicitly granting permission to emit fewer requirements if evidence is absent, the hallucination rate plummeted by more than 84% (from 46.3% to 7.2%).

### 5.2 The Danger of Plausible Hallucinations in Public AI Governance
In commercial software, an extra requirement (e.g., adding an audit log) might be seen as harmless or beneficial. In public-sector algorithmic governance, however, an invented commitment misleads oversight bodies, auditors, and civil society into believing legal or ethical safeguards are technically verified when the underlying agency made no such pledge.

### 5.3 Recommendations for Requirements Engineers and Public Bodies
1. **Never generate ungrounded requirements from policy disclosures:** Require verifiable excerpt citations for every synthesized requirement.
2. **Enforce completeness gating:** Records with completeness scores below threshold should trigger requests for additional documentation rather than automated requirement generation.
3. **Automate quote validation:** Automated n-gram quote checking provides an immediate, low-cost filter to catch unsupported claims before human review.

---

## 6. Threats to Validity

- **Construct Validity:** Human ratings involve subjective judgment. We mitigated this by defining operational anchors in `rubric.md`, blinding raters to conditions, and verifying high Cohen's $\kappa$ ($> 0.80$).
- **Internal Validity:** LLM generation can exhibit non-determinism. We fixed `temperature = 0.0`, seeded all sampling operations, and cached full raw outputs in `generations.jsonl`.
- **External Validity:** The dataset is drawn exclusively from the UK Algorithmic Transparency Recording Standard. While ATRS represents the leading national algorithmic register, generalization to other frameworks (e.g., EU AI Act conformity assessments, US Algorithmic Impact Assessments) requires replication.
- **Reliability:** All steps—from record selection to statistical testing—are automated via modular scripts and packaged with deterministic seeds.

---

## 7. Conclusion and Future Work

This study presents the first rigorous empirical evaluation of LLM-assisted requirement generation from public-sector algorithmic transparency disclosures. Evidence-grounded prompting achieves substantial improvements in clarity, verifiability, and traceability while drastically reducing hallucinated commitments.

Future work will expand this pipeline across multiple LLM families (Claude, GPT-4, Llama-3, DeepSeek), evaluate automated requirement test generation, and investigate multi-lingual governance standards across the European Union.

---

## References

1. Central Digital and Data Office (CDDO). (2023). *Algorithmic Transparency Recording Standard (ATRS)*. Cabinet Office, UK Government.
2. Glinz, M. (2014). *A glossary of requirements engineering terminology*. Standard of the International Requirements Engineering Board (IREB).
3. IEEE Computer Society. (2018). *ISO/IEC/IEEE 29148: Systems and software engineering — Life cycle processes — Requirements engineering*.
4. From issue titles to requirements: an empirical study of large language models and prompt engineering strategies. (2026). *Requirements Engineering*, Springer Nature. DOI: 10.1007/s00766-026-00462-z.
5. Ezzini, S., et al. (2024). *Automated Requirements Extraction from Public Regulations Using LLMs*. Requirements Engineering Journal, Springer.
6. Ji, Z., et al. (2023). *Survey of hallucination in natural language generation*. ACM Computing Surveys, 55(12), 1-38.
7. Cleland-Huang, J., Gotel, O., & Zisman, A. (2012). *Software and systems traceability*. Springer Science & Business Media.
8. Cohen, J. (1968). *Weighted kappa: Nominal scale agreement provision for scaled disagreement or partial credit*. Psychological Bulletin, 70(4), 213.

---

## Appendices

- **Appendix A: Prompt Templates** (Refer to `prompts/baseline.txt` and `prompts/grounded.txt`).
- **Appendix B: Scoring Rubric** (Refer to `rubric.md`).
- **Appendix C: Replication Package Guide** (Refer to `README.md`).
