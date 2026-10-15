# Analysis — event_feedback.csv

- Rows analysed: **160**
- Columns analysed: **6** (3 numeric, 2 categorical, 1 date)

## Key findings

- 160 responses across 6 analysed columns
- Most common city: Lisbon (31% of responses)
- Strongest relationship: session_rating ↔ speaker_rating (r = +0.83, strong positive)
- Highest session_length_mins by would_attend_again: No (60.5) vs Definitely (47.5)
- Highest session_rating by city: Austin (3.5) vs Toronto (2.7)
- 5 duplicate rows were removed during cleaning

## Numeric columns

| Column | N | Missing | Mean | Median | Std | Min | Max |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `session_rating` | 140 | 20 | 3.21 | 3.00 | 1.40 | 1.00 | 5.00 |
| `speaker_rating` | 137 | 23 | 3.08 | 3.00 | 1.42 | 1.00 | 5.00 |
| `session_length_mins` | 148 | 12 | 53.51 | 45.00 | 21.93 | 30.00 | 90.00 |

## Categorical columns

| Column | Levels | Most common | Share |
| --- | --- | --- | --- |
| `would_attend_again` | 4 | Probably not | 28% |
| `city` | 5 | Lisbon | 31% |

## Correlations

| Pair | r | Strength |
| --- | --- | --- |
| session_rating ↔ speaker_rating | +0.83 | strong positive |

## Segment comparisons

| Segment | Measure | Best | Worst | Gap |
| --- | --- | --- | --- | --- |
| `would_attend_again` | `session_length_mins` | No (60.5) | Definitely (47.5) | 24% |
| `city` | `session_rating` | Austin (3.5) | Toronto (2.7) | 23% |
| `city` | `speaker_rating` | Lisbon (3.3) | Toronto (2.6) | 20% |
