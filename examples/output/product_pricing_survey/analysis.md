# Analysis — product_pricing_survey.csv

- Rows analysed: **170**
- Columns analysed: **7** (3 numeric, 3 categorical, 1 date)

## Key findings

- 170 responses across 7 analysed columns
- Most common segment: Enterprise (26% of responses)
- Strongest relationship: willingness_to_pay ↔ price_shown (r = +0.96, strong positive)
- Highest willingness_to_pay by segment: Enterprise (254.0) vs Startup (34.8)
- Highest price_shown by segment: Enterprise (242.0) vs Startup (45.7)
- 7 duplicate rows were removed during cleaning

## Numeric columns

| Column | N | Missing | Mean | Median | Std | Min | Max |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `willingness_to_pay` | 144 | 26 | 132.72 | 129.00 | 84.43 | 19.00 | 288.00 |
| `price_shown` | 159 | 11 | 132.66 | 119.00 | 81.01 | 19.00 | 318.00 |
| `discount_pct` | 144 | 26 | 13.40 | 15.00 | 9.12 | 0.00 | 25.00 |

## Categorical columns

| Column | Levels | Most common | Share |
| --- | --- | --- | --- |
| `segment` | 4 | Enterprise | 26% |
| `purchase_intent` | 5 | Likely | 22% |
| `decision_maker` | 4 | unknown | 29% |

## Correlations

| Pair | r | Strength |
| --- | --- | --- |
| willingness_to_pay ↔ price_shown | +0.96 | strong positive |

## Segment comparisons

| Segment | Measure | Best | Worst | Gap |
| --- | --- | --- | --- | --- |
| `segment` | `willingness_to_pay` | Enterprise (254.0) | Startup (34.8) | 165% |
| `segment` | `price_shown` | Enterprise (242.0) | Startup (45.7) | 148% |
| `purchase_intent` | `discount_pct` | Very likely (17.0) | Very unlikely (10.6) | 48% |
