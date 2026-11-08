# Findings and Recommendations

## Data cleaning

The raw file had 1,190 transactions; 1,175 unique transactions remain (Jan 2023 to Dec 2024).

- 15 exact duplicate rows removed.
- Department names standardized (HR, Finance, IT, Operations, R&D, Marketing).
- Region values trimmed of extra spaces.
- No missing values, negative amounts or invalid dates.

## Key findings

The company earned 2.33M in revenue against 1.02M in expenses, a net profit of 1.31M (56% margin), but revenue fell 13% in 2024 while expenses rose 13%.

### 1. Year over year

| Year | Revenue | Expense | Net |
| --- | --- | --- | --- |
| 2023 | 1,242,654 | 479,354 | 763,300 |
| 2024 | 1,082,756 | 540,184 | 542,572 |

Net profit dropped 29% from 2023 to 2024.

### 2. Monthly trend

- Revenue ranges from 48K (Nov 2024) to 142K (Dec 2023).
- Peaks fall in May and December; the weakest months cluster in Q4 2024 and Mar 2024.
- Nov 2024 is the only loss-making month (revenue 48K, expense 54K, net -5.4K).

### 3. Region

| Region | Revenue | Expense | Net | Margin |
| --- | --- | --- | --- | --- |
| West | 632,604 | 247,113 | 385,491 | 60.9% |
| South | 601,028 | 226,603 | 374,425 | 62.3% |
| North | 565,791 | 261,731 | 304,060 | 53.7% |
| East | 525,987 | 284,092 | 241,895 | 46.0% |

### 4. Department

| Department | Revenue | Expense | Net | Margin |
| --- | --- | --- | --- | --- |
| Sales | 371,132 | 126,440 | 244,693 | 65.9% |
| Operations | 349,118 | 124,324 | 224,794 | 64.4% |
| Marketing | 380,851 | 181,282 | 199,569 | 52.4% |
| IT | 295,015 | 126,853 | 168,162 | 57.0% |
| R&D | 321,802 | 156,383 | 165,419 | 51.4% |
| Finance | 321,600 | 160,154 | 161,446 | 50.2% |
| HR | 285,892 | 144,102 | 141,789 | 49.6% |

### 5. Category

- Consulting is the largest revenue source (704K, 30%). Product Sales (555K), Service Contracts (541K) and Licensing (525K) are close together.
- Expense categories are evenly spread; average transaction size ranges only from 1,306 (Salaries) to 1,669 (Office Supplies).

### 6. Department-region combinations

- Best net: IT-South (85.7K), Finance-West (80.4K), Sales-South (69.8K).
- Only loss-making combination: Finance-East (-5.6K).

## Why did 2024 change? (Python analysis)

- **Volume, not value:** revenue transactions fell 15% (272 to 232) while the average deal size rose 2% (4,569 to 4,667). Expense transactions rose 14% (314 to 357) at an unchanged average size.
- **Revenue fell most in:** Product Sales (-25%) and Licensing (-18%); the East (-26%) and West (-19%) regions; the Sales and R&D departments (-26% each). IT (+8%) and Finance (+20%) grew.
- **Expenses rose most in:** Marketing Spend (+31K), Utilities (+25K) and Software (+25K). Salaries fell 26K.
- **Significance:** mean monthly revenue was 103.6K in 2023 and 90.2K in 2024, but the difference is not statistically significant (Welch t-test p = 0.21, Mann-Whitney p = 0.31). It should be monitored, not treated as a proven trend.

## Recommendations

1. **Investigate the 2024 revenue drop.** Break 2024 revenue down by category and region and set a target to restore the 2023 level.
2. **Prepare for weak months.** Plan budgets around the May and December peaks and cut discretionary spend in low-revenue months.
3. **Review Marketing spend.** Highest expense (181K) with only a 52% margin, against 66% for Sales.
4. **Fix East and Finance-East.** Lowest regional margin (46%) and the only loss-making pair.
5. **Grow what works.** Consulting, Sales, Operations and IT have the best revenue and margins.

## Limitations

- Two years and 1,175 transactions: seasonality is indicative, not proven, and the 2024 revenue decline is not statistically significant.
- Shared or allocated costs are not visible.
- The findings show what happened, not why.
