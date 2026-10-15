# Analysis — public_health_checkup.csv

- Rows analysed: **190**
- Columns analysed: **7** (4 numeric, 2 categorical, 1 date)

## Key findings

- 190 responses across 7 analysed columns
- Most common smoker: No (46% of responses)
- Strongest relationship: bmi ↔ exercise_days_per_week (r = -0.70, moderate negative)
- Highest exercise_days_per_week by sex: Non-binary (3.2) vs Male (2.8)
- Highest systolic_bp by sex: Male (141.3) vs Female (127.8)
- 2 extreme values in systolic_bp worth verifying

## Numeric columns

| Column | N | Missing | Mean | Median | Std | Min | Max |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `age` | 183 | 7 | 50.54 | 52.00 | 18.52 | 19.00 | 84.00 |
| `bmi` | 177 | 13 | 26.41 | 26.50 | 4.17 | 16.40 | 36.80 |
| `systolic_bp` | 185 | 5 | 133.27 | 128.00 | 65.26 | 88.00 | 999.00 |
| `exercise_days_per_week` | 168 | 22 | 3.02 | 3.00 | 0.98 | 1.00 | 5.00 |

## Categorical columns

| Column | Levels | Most common | Share |
| --- | --- | --- | --- |
| `sex` | 3 | Male | 36% |
| `smoker` | 3 | No | 46% |

## Correlations

| Pair | r | Strength |
| --- | --- | --- |
| bmi ↔ exercise_days_per_week | -0.70 | moderate negative |

## Segment comparisons

| Segment | Measure | Best | Worst | Gap |
| --- | --- | --- | --- | --- |
| `sex` | `exercise_days_per_week` | Non-binary (3.2) | Male (2.8) | 15% |
| `sex` | `systolic_bp` | Male (141.3) | Female (127.8) | 10% |
