# Cleaning log — customer_satisfaction_q1.csv

- Rows: **208 → 200** (8 removed)
- Columns: **10 → 10**
- Missing cells: **11.8% → 12.0%**
- Recorded actions: **22**

## Detected column types

| Column | Type | Unique | Missing |
| --- | --- | --- | --- |
| `response_id` | text | 200 | 0 |
| `customer_name` | text | 5 | 13 |
| `plan` | categorical | 4 | 0 |
| `nps_score` | numeric | 11 | 27 |
| `satisfaction_1_5` | numeric | 5 | 10 |
| `support_tickets` | numeric | 5 | 33 |
| `annual_spend` | numeric | 5 | 25 |
| `churn_risk` | categorical | 3 | 0 |
| `response_date` | date | 103 | 0 |
| `feedback` | text | 5 | 132 |

## Actions taken

| Column | Issue | Action | Cells |
| --- | --- | --- | --- |
| — | inconsistent header | renamed to snake_case (Customer Name → customer_name, Plan → plan, satisfaction_(1-5) → satisfaction_1_5, Annual Spend → annual_spend) | 4 |
| `customer_name` | whitespace padding | stripped surrounding whitespace | 2 |
| `customer_name` | sentinel missing value | treated as missing | 14 |
| `plan` | whitespace padding | stripped surrounding whitespace | 44 |
| `nps_score` | whitespace padding | stripped surrounding whitespace | 3 |
| `nps_score` | sentinel missing value | treated as missing | 27 |
| `satisfaction_1_5` | whitespace padding | stripped surrounding whitespace | 1 |
| `satisfaction_1_5` | sentinel missing value | treated as missing | 10 |
| `support_tickets` | whitespace padding | stripped surrounding whitespace | 3 |
| `support_tickets` | sentinel missing value | treated as missing | 34 |
| `annual_spend` | whitespace padding | stripped surrounding whitespace | 5 |
| `annual_spend` | sentinel missing value | treated as missing | 26 |
| `churn_risk` | whitespace padding | stripped surrounding whitespace | 33 |
| `feedback` | sentinel missing value | treated as missing | 135 |
| — | duplicate row | removed exact duplicate | 8 |
| `plan` | inconsistent category spelling | standardised to most common spelling | 4 |
| `nps_score` | messy numeric text | extracted value from units, currency or separators | 32 |
| `annual_spend` | messy numeric text | extracted value from units, currency or separators | 121 |
| `churn_risk` | inconsistent category spelling | standardised to most common spelling | 3 |
| `response_date` | ambiguous DD/MM vs MM/DD | read day-first unless month-first is forced | 82 |
| `response_date` | mixed date formats | parsed to ISO date (YYYY-MM-DD) | 160 |
| `feedback` | 66% missing after cleaning | flagged low-confidence column | 132 |
