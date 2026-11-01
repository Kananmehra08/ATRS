# ATRS Human Annotation Rubric and Evaluation Protocol

This rubric governs the blind human evaluation of software requirements generated from UK Algorithmic Transparency Recording Standard (ATRS) records.

> **Blinding Notice:** Human raters evaluate requirements in randomized order. The prompting condition (`baseline` vs. `grounded`) and any LLM-provided evidence quotes are strictly hidden from raters. Raters evaluate each requirement against the full source record text (`data/texts/{record_id}.txt`).

---

## 1. Evaluation Dimensions

### Dimension 1: Clarity (1 to 3)
Measures linguistic precision, grammatical structure, and absence of ambiguity.

| Score | Level | Operational Definition & Criteria | Concrete Examples |
| :---: | :--- | :--- | :--- |
| **3** | **Unambiguous** | Clear single interpretation. Well-formed requirement syntax ("The system shall [verb]..."). Explicit subject, actor, and unambiguous action. Free from colloquialisms. | *"The system shall log each user authentication attempt with timestamp, user ID, and IP address."* |
| **2** | **Mostly Clear** | Minor ambiguity, slightly informal phrasing, or compound statement (two actions joined by 'and'), but engineering intent is understandable without guessing. | *"The system shall alert the administrator and create a backup when disk space is low."* (Compound action, slightly vague threshold 'low'). |
| **1** | **Unclear / Vague** | Ambiguous, subjective, or open-ended. Uses undefined qualifiers like *"appropriate"*, *"adequate"*, *"robust"*, *"user-friendly"*, or *"as fast as possible"*. | *"The system shall ensure adequate protection against algorithmic bias."* |

---

### Dimension 2: Verifiability / Testability (1 to 3)
Measures whether a software quality assurance engineer can design an objective, repeatable test or inspection to verify compliance.

| Score | Level | Operational Definition & Criteria | Concrete Examples |
| :---: | :--- | :--- | :--- |
| **3** | **Directly Testable** | A concrete pass/fail verification procedure can be designed (e.g., unit/integration test, measurable metric threshold, automated audit log inspection, observable state transition). | *"The system shall record an audit log entry within 500 milliseconds of every inference request."* |
| **2** | **Testable with Refinement** | Intended test is apparent, but requires operational parameters to be specified (e.g., specific file format, exact error code, or exact interval). | *"The system shall periodically verify model accuracy against ground truth."* (Testable once 'periodically' and 'accuracy threshold' are operationalized). |
| **1** | **Non-Testable** | Purely aspirational statement, high-level ethical principle, or subjective quality attribute that cannot be objectively verified by software testing. | *"The system shall respect human dignity and foster social cohesion."* |

---

### Dimension 3: Traceability to Source Record (0 to 2)
Measures the extent to which the requirement is directly grounded in commitments or specifications articulated in the ATRS source record.

| Score | Level | Operational Definition & Criteria |
| :---: | :--- | :--- |
| **2** | **Full Traceability** | The requirement is directly supported by an explicit statement, operational commitment, or constraint in the source record. |
| **1** | **Partial Traceability** | The record mentions the topic or general intent, but the requirement extrapolates or makes specific claims that go beyond the text. |
| **0** | **No Traceability** | No passage or commitment in the source record supports this requirement; the LLM fabricated the commitment from generic domain knowledge. |

---

### Dimension 4: Unsupported Claim / Hallucination (0 or 1)
Measures whether the LLM introduced fabricated facts, metrics, thresholds, roles, or technological commitments not found in the source record.

| Score | Designation | Criteria |
| :---: | :--- | :--- |
| **0** | **Supported** | All components (features, roles, numbers, standards, frequencies) are backed by the source text. |
| **1** | **Unsupported Claim** | The requirement asserts a specific fact, quantitative threshold (e.g., "99.9% uptime", "within 2 seconds"), technical standard (e.g., "ISO 27001", "WCAG 2.1 AA"), or role not stated anywhere in the source record. |

> **Relationship between Traceability and Unsupported Claims:**
> - If `traceability == 0`, `unsupported` is almost always `1`.
> - If `traceability == 1` (partial), `unsupported` is often `1` if an invented detail was introduced.
> - If `traceability == 2` (full), `unsupported` must be `0`.

---

## 2. Human Annotation Protocol

1. **Calibration Phase:**
   - Both Rater A and Rater B independently score 10 calibration items selected from practice records.
   - The raters convene to discuss discrepancies, clarify edge cases, and align on scoring thresholds.
   - Calibration items are excluded from the empirical research sample.

2. **Primary Annotation (Rater A):**
   - Rater A scores 100% of items in `data/annotations_template_A.csv`.
   - Saves completed ratings to `data/annotations_A.csv`.

3. **Inter-Rater Reliability (Rater B):**
   - Rater B independently scores the 20% random subset in `data/annotations_template_B.csv`.
   - Saves completed ratings to `data/annotations_B.csv`.
   - Inter-rater agreement is evaluated using quadratic weighted Cohen's $\kappa$ for ordinal metrics and unweighted Cohen's $\kappa$ for the binary unsupported flag. Target: $\kappa \ge 0.60$.

4. **Aggregation for Analysis:**
   - For double-annotated items, the final score is the arithmetic mean of Rater A and Rater B.
   - Run `python scripts/06_analyze.py` to produce statistical tests, tables, and figures.
