# Cleaning log — employee_engagement_2024.csv

- Rows: **187 → 180** (7 removed)
- Columns: **9 → 9**
- Missing cells: **9.8% → 9.6%**
- Recorded actions: **19**

## Detected column types

| Column | Type | Unique | Missing |
| --- | --- | --- | --- |
| `employee_id` | text | 180 | 0 |
| `department` | categorical | 5 | 0 |
| `tenure_yrs` | numeric | 13 | 7 |
| `role` | categorical | 4 | 0 |
| `engagement_score` | numeric | 5 | 15 |
| `manager_support` | numeric | 5 | 24 |
| `would_recommend` | categorical | 3 | 0 |
| `survey_date` | date | 105 | 0 |
| `comments` | text | 5 | 110 |

## Actions taken

| Column | Issue | Action | Cells |
| --- | --- | --- | --- |
| — | inconsistent header | renamed to snake_case (Employee ID → employee_id, Department  → department, Role → role, Engagement Score → engagement_score) | 6 |
| `department` | whitespace padding | stripped surrounding whitespace | 24 |
| `tenure_yrs` | whitespace padding | stripped surrounding whitespace | 2 |
| `tenure_yrs` | sentinel missing value | treated as missing | 8 |
| `role` | whitespace padding | stripped surrounding whitespace | 32 |
| `engagement_score` | whitespace padding | stripped surrounding whitespace | 5 |
| `engagement_score` | sentinel missing value | treated as missing | 17 |
| `manager_support` | whitespace padding | stripped surrounding whitespace | 3 |
| `manager_support` | sentinel missing value | treated as missing | 25 |
| `would_recommend` | whitespace padding | stripped surrounding whitespace | 33 |
| `comments` | sentinel missing value | treated as missing | 115 |
| — | duplicate row | removed exact duplicate | 7 |
| `department` | inconsistent category spelling | standardised to most common spelling | 5 |
| `role` | inconsistent category spelling | standardised to most common spelling | 4 |
| `engagement_score` | messy numeric text | extracted value from units, currency or separators | 38 |
| `would_recommend` | inconsistent category spelling | standardised to most common spelling | 3 |
| `survey_date` | ambiguous DD/MM vs MM/DD | read day-first unless month-first is forced | 70 |
| `survey_date` | mixed date formats | parsed to ISO date (YYYY-MM-DD) | 151 |
| `comments` | 61% missing after cleaning | flagged low-confidence column | 110 |
