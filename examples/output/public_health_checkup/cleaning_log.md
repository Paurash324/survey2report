# Cleaning log — public_health_checkup.csv

- Rows: **194 → 190** (4 removed)
- Columns: **9 → 9**
- Missing cells: **10.5% → 10.6%**
- Recorded actions: **19**

## Detected column types

| Column | Type | Unique | Missing |
| --- | --- | --- | --- |
| `patient_id` | text | 190 | 0 |
| `visit_date` | date | 108 | 0 |
| `age` | numeric | 64 | 7 |
| `sex` | categorical | 3 | 0 |
| `bmi` | numeric | 110 | 13 |
| `systolic_bp` | numeric | 42 | 5 |
| `smoker` | categorical | 3 | 0 |
| `exercise_days_per_week` | numeric | 5 | 22 |
| `notes` | text | 5 | 135 |

## Actions taken

| Column | Issue | Action | Cells |
| --- | --- | --- | --- |
| `age` | whitespace padding | stripped surrounding whitespace | 2 |
| `age` | sentinel missing value | treated as missing | 7 |
| `sex` | whitespace padding | stripped surrounding whitespace | 38 |
| `bmi` | whitespace padding | stripped surrounding whitespace | 1 |
| `bmi` | sentinel missing value | treated as missing | 13 |
| `systolic_bp` | whitespace padding | stripped surrounding whitespace | 1 |
| `systolic_bp` | sentinel missing value | treated as missing | 5 |
| `smoker` | whitespace padding | stripped surrounding whitespace | 30 |
| `exercise_days_per_week` | whitespace padding | stripped surrounding whitespace | 1 |
| `exercise_days_per_week` | sentinel missing value | treated as missing | 22 |
| `notes` | sentinel missing value | treated as missing | 137 |
| — | duplicate row | removed exact duplicate | 4 |
| `visit_date` | ambiguous DD/MM vs MM/DD | read day-first unless month-first is forced | 71 |
| `visit_date` | mixed date formats | parsed to ISO date (YYYY-MM-DD) | 144 |
| `age` | messy numeric text | extracted value from units, currency or separators | 15 |
| `sex` | inconsistent category spelling | standardised to most common spelling | 3 |
| `bmi` | messy numeric text | extracted value from units, currency or separators | 19 |
| `smoker` | inconsistent category spelling | standardised to most common spelling | 5 |
| `notes` | 71% missing after cleaning | flagged low-confidence column | 135 |
