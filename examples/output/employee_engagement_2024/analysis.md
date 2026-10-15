# Analysis — employee_engagement_2024.csv

- Rows analysed: **180**
- Columns analysed: **7** (3 numeric, 3 categorical, 1 date)

## Key findings

- 180 responses across 7 analysed columns
- Most common would_recommend: Yes (35% of responses)
- Strongest relationship: engagement_score ↔ manager_support (r = +0.88, strong positive)
- Highest tenure_yrs by department: Support (6.4) vs Marketing (4.3)
- Highest engagement_score by role: Individual Contributor (3.5) vs Team Lead (3.0)
- 7 duplicate rows were removed during cleaning

## Numeric columns

| Column | N | Missing | Mean | Median | Std | Min | Max |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `tenure_yrs` | 173 | 7 | 5.76 | 6.00 | 3.89 | 0.00 | 12.00 |
| `engagement_score` | 165 | 15 | 3.30 | 4.00 | 1.38 | 1.00 | 5.00 |
| `manager_support` | 156 | 24 | 3.30 | 3.00 | 1.40 | 1.00 | 5.00 |

## Categorical columns

| Column | Levels | Most common | Share |
| --- | --- | --- | --- |
| `department` | 5 | Support | 24% |
| `role` | 4 | Manager | 28% |
| `would_recommend` | 3 | Yes | 35% |

## Correlations

| Pair | r | Strength |
| --- | --- | --- |
| engagement_score ↔ manager_support | +0.88 | strong positive |

## Segment comparisons

| Segment | Measure | Best | Worst | Gap |
| --- | --- | --- | --- | --- |
| `department` | `tenure_yrs` | Support (6.4) | Marketing (4.3) | 37% |
| `role` | `engagement_score` | Individual Contributor (3.5) | Team Lead (3.0) | 18% |
| `role` | `manager_support` | Individual Contributor (3.5) | Team Lead (3.1) | 15% |
