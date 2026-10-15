# Analysis — customer_satisfaction_q1.csv

- Rows analysed: **200**
- Columns analysed: **7** (4 numeric, 2 categorical, 1 date)

## Key findings

- 200 responses across 7 analysed columns
- Most common churn_risk: high (35% of responses)
- Strongest relationship: nps_score ↔ satisfaction_1_5 (r = +0.91, strong positive)
- Highest annual_spend by churn_risk: low (3131.8) vs medium (1284.0)
- Highest support_tickets by plan: Pro (3.0) vs Enterprise (1.6)
- 25 extreme values in annual_spend worth verifying

## Numeric columns

| Column | N | Missing | Mean | Median | Std | Min | Max |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `nps_score` | 173 | 27 | 7.89 | 9.00 | 2.58 | 0.00 | 10.00 |
| `satisfaction_1_5` | 190 | 10 | 4.07 | 5.00 | 1.30 | 1.00 | 5.00 |
| `support_tickets` | 167 | 33 | 2.16 | 1.00 | 2.65 | 0.00 | 8.00 |
| `annual_spend` | 175 | 25 | 2079.90 | 149.00 | 4291.08 | 0.00 | 12500.00 |

## Categorical columns

| Column | Levels | Most common | Share |
| --- | --- | --- | --- |
| `plan` | 4 | Enterprise | 30% |
| `churn_risk` | 3 | high | 35% |

## Correlations

| Pair | r | Strength |
| --- | --- | --- |
| nps_score ↔ satisfaction_1_5 | +0.91 | strong positive |
| satisfaction_1_5 ↔ support_tickets | -0.91 | strong negative |
| nps_score ↔ support_tickets | -0.84 | strong negative |

## Segment comparisons

| Segment | Measure | Best | Worst | Gap |
| --- | --- | --- | --- | --- |
| `churn_risk` | `annual_spend` | low (3131.8) | medium (1284.0) | 89% |
| `plan` | `support_tickets` | Pro (3.0) | Enterprise (1.6) | 65% |
| `plan` | `nps_score` | Enterprise (8.3) | Pro (7.0) | 17% |
