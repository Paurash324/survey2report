# Cleaning log — event_feedback.csv

- Rows: **166 → 160** (6 removed)
- Columns: **9 → 9**
- Missing cells: **13.4% → 12.8%**
- Recorded actions: **23**

## Detected column types

| Column | Type | Unique | Missing |
| --- | --- | --- | --- |
| `reg_id` | text | 160 | 0 |
| `attendee_name` | text | 5 | 8 |
| `session_rating` | numeric | 5 | 20 |
| `speaker_rating` | numeric | 5 | 23 |
| `would_attend_again` | categorical | 4 | 0 |
| `session_length_mins` | numeric | 4 | 12 |
| `feedback_date` | date | 94 | 0 |
| `city` | categorical | 5 | 0 |
| `notes` | text | 5 | 122 |

## Actions taken

| Column | Issue | Action | Cells |
| --- | --- | --- | --- |
| — | inconsistent header | renamed to snake_case (Reg ID → reg_id, Session Rating → session_rating, Would attend again? → would_attend_again, Feedback Date → feedback_date) | 5 |
| `reg_id` | sentinel missing value | treated as missing | 1 |
| `attendee_name` | sentinel missing value | treated as missing | 10 |
| `session_rating` | whitespace padding | stripped surrounding whitespace | 4 |
| `session_rating` | sentinel missing value | treated as missing | 21 |
| `speaker_rating` | whitespace padding | stripped surrounding whitespace | 2 |
| `speaker_rating` | sentinel missing value | treated as missing | 25 |
| `would_attend_again` | whitespace padding | stripped surrounding whitespace | 32 |
| `would_attend_again` | sentinel missing value | treated as missing | 1 |
| `session_length_mins` | whitespace padding | stripped surrounding whitespace | 5 |
| `session_length_mins` | sentinel missing value | treated as missing | 13 |
| `feedback_date` | sentinel missing value | treated as missing | 1 |
| `city` | whitespace padding | stripped surrounding whitespace | 26 |
| `city` | sentinel missing value | treated as missing | 1 |
| `notes` | sentinel missing value | treated as missing | 127 |
| — | blank row | dropped row | 1 |
| — | duplicate row | removed exact duplicate | 5 |
| `would_attend_again` | inconsistent category spelling | standardised to most common spelling | 4 |
| `session_length_mins` | messy numeric text | extracted value from units, currency or separators | 113 |
| `feedback_date` | ambiguous DD/MM vs MM/DD | read day-first unless month-first is forced | 70 |
| `feedback_date` | mixed date formats | parsed to ISO date (YYYY-MM-DD) | 136 |
| `city` | inconsistent category spelling | standardised to most common spelling | 5 |
| `notes` | 76% missing after cleaning | flagged low-confidence column | 122 |
