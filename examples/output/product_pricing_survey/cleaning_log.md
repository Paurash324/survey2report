# Cleaning log — product_pricing_survey.csv

- Rows: **177 → 170** (7 removed)
- Columns: **9 → 9**
- Missing cells: **12.1% → 12.2%**
- Recorded actions: **21**

## Detected column types

| Column | Type | Unique | Missing |
| --- | --- | --- | --- |
| `respondent_id` | text | 170 | 0 |
| `segment` | categorical | 4 | 0 |
| `willingness_to_pay` | numeric | 19 | 26 |
| `purchase_intent` | categorical | 5 | 0 |
| `price_shown` | numeric | 86 | 11 |
| `discount_pct` | numeric | 5 | 26 |
| `interview_date` | date | 93 | 0 |
| `decision_maker` | categorical | 4 | 0 |
| `verbatim` | text | 4 | 123 |

## Actions taken

| Column | Issue | Action | Cells |
| --- | --- | --- | --- |
| — | inconsistent header | renamed to snake_case (Segment → segment) | 1 |
| `segment` | whitespace padding | stripped surrounding whitespace | 35 |
| `willingness_to_pay` | whitespace padding | stripped surrounding whitespace | 4 |
| `willingness_to_pay` | sentinel missing value | treated as missing | 27 |
| `purchase_intent` | whitespace padding | stripped surrounding whitespace | 39 |
| `price_shown` | whitespace padding | stripped surrounding whitespace | 3 |
| `price_shown` | sentinel missing value | treated as missing | 11 |
| `discount_pct` | whitespace padding | stripped surrounding whitespace | 5 |
| `discount_pct` | sentinel missing value | treated as missing | 27 |
| `decision_maker` | whitespace padding | stripped surrounding whitespace | 29 |
| `verbatim` | sentinel missing value | treated as missing | 127 |
| — | duplicate row | removed exact duplicate | 7 |
| `segment` | inconsistent category spelling | standardised to most common spelling | 3 |
| `willingness_to_pay` | messy numeric text | extracted value from units, currency or separators | 121 |
| `purchase_intent` | inconsistent category spelling | standardised to most common spelling | 5 |
| `price_shown` | messy numeric text | extracted value from units, currency or separators | 114 |
| `discount_pct` | messy numeric text | extracted value from units, currency or separators | 61 |
| `interview_date` | ambiguous DD/MM vs MM/DD | read day-first unless month-first is forced | 74 |
| `interview_date` | mixed date formats | parsed to ISO date (YYYY-MM-DD) | 138 |
| `decision_maker` | inconsistent category spelling | standardised to most common spelling | 4 |
| `verbatim` | 72% missing after cleaning | flagged low-confidence column | 123 |
