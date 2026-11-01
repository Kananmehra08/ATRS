# ATRS Requirements Generation Study: Empirical Results Summary
Evaluated on 40 ATRS records (820 total requirements).

## Inter-Rater Reliability (Cohen's Kappa)
Double-annotated subset evaluated between Rater **A** and Rater **B**:
- **Clarity** (quadratic weighted): $\kappa = 0.823$ ($n = 164$ items)
- **Verifiability** (quadratic weighted): $\kappa = 0.848$ ($n = 164$ items)
- **Traceability** (quadratic weighted): $\kappa = 0.897$ ($n = 164$ items)
- **Unsupported** (unweighted): $\kappa = 0.612$ ($n = 164$ items)

## Automated Grounded Evidence Quote Verification
Grounded prompt evidence quotes evaluated against source record text ($n = 412$ requirements):
- **Exact match**: 78.6%
- **Near match**: 17.2%
- **No match**: 4.1%
- **None match**: 0.0%

## Table 1 (RQ1): Clarity and Testability Comparison
| metric        | baseline_mean | baseline_sd | grounded_mean | grounded_sd | median_diff | wilcoxon_p | effect_r_rb |
| ------------- | ------------- | ----------- | ------------- | ----------- | ----------- | ---------- | ----------- |
| clarity       | 2.028         | 0.2         | 2.495         | 0.181       | 0.5         | <0.001     | 1.0         |
| verifiability | 1.841         | 0.187       | 2.414         | 0.227       | 0.583       | <0.001     | 1.0         |

## Table 2 (RQ2): Traceability to Source Evidence
| condition | none_pct | partial_pct | full_pct | wilcoxon_p(mean) |
| --------- | -------- | ----------- | -------- | ---------------- |
| baseline  | 25.5     | 64.2        | 10.3     | <0.001           |
| grounded  | 1.0      | 32.8        | 66.3     | <0.001           |

## Table 3 (RQ3): Requirement Quality Across Record Completeness
| condition | high_mean | low_mean | n_high | n_low | mannwhitney_p | spearman_rho | spearman_p |
| --------- | --------- | -------- | ------ | ----- | ------------- | ------------ | ---------- |
| baseline  | 0.609     | 0.534    | 20     | 20    | <0.001        | 0.78         | <0.001     |
| grounded  | 0.86      | 0.779    | 20     | 20    | <0.001        | 0.835        | <0.001     |

## Table 4 (RQ4): Frequency of Unsupported Claims
| condition | overall_rate_pct | high_completeness_pct | low_completeness_pct | paired_wilcoxon_p |
| --------- | ---------------- | --------------------- | -------------------- | ----------------- |
| baseline  | 46.3             | 39.8                  | 51.7                 | <0.001            |
| grounded  | 7.2              | 3.1                   | 11.3                 | <0.001            |
