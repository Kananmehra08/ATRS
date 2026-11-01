# ATRS Requirements Generation Study: Empirical Results Summary
Evaluated on 40 ATRS records (789 total requirements).

## Inter-Rater Reliability (Cohen's Kappa)
Double-annotated subset evaluated between Rater **A** and Rater **B**:
- **Clarity** (quadratic weighted): $\kappa = 0.917$ ($n = 158$ items)
- **Verifiability** (quadratic weighted): $\kappa = 0.916$ ($n = 158$ items)
- **Traceability** (quadratic weighted): $\kappa = 0.938$ ($n = 158$ items)
- **Unsupported** (unweighted): $\kappa = 0.707$ ($n = 158$ items)

## Automated Grounded Evidence Quote Verification
Grounded prompt evidence quotes evaluated against source record text ($n = 389$ requirements):
- **Exact match**: 100.0%
- **Near match**: 0.0%
- **No match**: 0.0%
- **None match**: 0.0%

## Table 1 (RQ1): Clarity and Testability Comparison
| metric        | baseline_mean | baseline_sd | grounded_mean | grounded_sd | median_diff | wilcoxon_p | effect_r_rb |
| ------------- | ------------- | ----------- | ------------- | ----------- | ----------- | ---------- | ----------- |
| clarity       | 1.945         | 0.242       | 2.513         | 0.193       | 0.6         | <0.001     | 1.0         |
| verifiability | 1.849         | 0.211       | 2.496         | 0.143       | 0.65        | <0.001     | 1.0         |

## Table 2 (RQ2): Traceability to Source Evidence
| condition | none_pct | partial_pct | full_pct | wilcoxon_p(mean) |
| --------- | -------- | ----------- | -------- | ---------------- |
| baseline  | 26.0     | 63.7        | 10.2     | <0.001           |
| grounded  | 0.0      | 30.3        | 69.7     | <0.001           |

## Table 3 (RQ3): Requirement Quality Across Record Completeness
| condition | high_mean | low_mean | n_high | n_low | mannwhitney_p | spearman_rho | spearman_p |
| --------- | --------- | -------- | ------ | ----- | ------------- | ------------ | ---------- |
| baseline  | 0.571     | 0.554    | 20     | 20    | 0.250         | 0.143        | 0.379      |
| grounded  | 0.837     | 0.84     | 20     | 19    | 0.757         | 0.003        | 0.986      |

## Table 4 (RQ4): Frequency of Unsupported Claims
| condition | overall_rate_pct | high_completeness_pct | low_completeness_pct | paired_wilcoxon_p |
| --------- | ---------------- | --------------------- | -------------------- | ----------------- |
| baseline  | 48.1             | 40.0                  | 56.2                 | <0.001            |
| grounded  | 11.1             | 10.0                  | 12.2                 | <0.001            |
