# Power BI build guide

This folder gives you everything needed to build the dashboard in Power BI Desktop in about an hour: a ready data model (`data/`), 18 DAX measures (`measures.dax`) and a colour theme (`theme.json`). The `.pbix` file itself has to be built in Power BI Desktop, which runs on Windows only. If you don't have a Windows PC, use a college lab computer or a Windows virtual machine.

## 1. Load the data

1. Open Power BI Desktop, choose **Get data > Text/CSV** and load all five files from `data/`:
   `fact_transactions.csv`, `dim_date.csv`, `dim_department.csv`, `dim_region.csv`, `dim_category.csv`.
2. In **Transform data** (Power Query), check the types:
   - `fact_transactions[date]` and `dim_date[Date]`: **Date**
   - `fact_transactions[amount]`: **Fixed decimal number**
   - `dim_date[Year]` and `dim_date[MonthNumber]`: **Whole number**, and set `Year` to **Don't summarize** in the Column tools.
3. **Close & Apply**.

## 2. Build the model

In **Model view**, create these relationships (many-to-one, single direction, from the fact table to each dimension):

| From (fact_transactions) | To |
| --- | --- |
| date | dim_date[Date] |
| department | dim_department[Department] |
| region | dim_region[Region] |
| category | dim_category[Category] |

Then select `dim_date` and choose **Table tools > Mark as date table** using the `Date` column. This is required for the year-over-year measures.

Sort `dim_date[MonthName]` by `MonthNumber` (Column tools > Sort by column).

## 3. Add the measures

Create each measure from `measures.dax` (**Modeling > New measure**), one at a time. Format the measures:

- Total Revenue, Total Expense, Net Profit, the change measures: currency or whole number, thousands separator
- Profit Margin %, Revenue YoY %, Expense YoY %: percentage with one decimal

## 4. Check the numbers before building any visual

Put the measures in a table or cards and confirm they match the SQL results. If they don't, fix the model first.

| Measure | Expected |
| --- | --- |
| Total Revenue | 2,325,410 |
| Total Expense | 1,019,538 |
| Net Profit | 1,305,871 |
| Profit Margin % | 56.2% |
| Total Revenue, Year = 2024 | 1,082,756 |
| Revenue YoY %, Year = 2024 | -12.9% |
| Revenue Transactions, 2023 / 2024 | 272 / 232 |
| Number of rows in fact_transactions | 1,175 |

I could not run Power BI here, so the DAX is written carefully but untested. These checks are how you confirm it.

## 5. Apply the theme

**View > Themes > Browse for themes** and pick `theme.json`.

## 6. Build three report pages

### Page 1: Overview

- **Slicers:** `dim_date[Year]` (tile style) and `dim_region[Region]` (dropdown).
- **Cards (4):** Total Revenue, Total Expense, Net Profit, Profit Margin %.
- **Line chart:** X = `dim_date[YearMonth]`, Y = Total Revenue, Total Expense, Revenue 3M Avg. Turn the 3M Avg line dashed.
- **Clustered column chart:** X = `dim_department[Department]`, Y = Total Revenue and Total Expense, sorted by Net Profit.
- **Text box:** use the `Headline` measure in a card as the page subtitle.

### Page 2: Why did 2024 fall?

This page answers the main question of the project. Set the Year slicer to 2024 so the "vs PY" measures compare against 2023.

- **Slicer:** `dim_date[Year]`, single select, set to 2024.
- **Cards:** Total Revenue, Revenue PY, Revenue YoY %.
- **Three bar charts:** Y axis = `dim_category[Category]`, `dim_region[Region]` and `dim_department[Department]` (one chart each), X axis = Revenue Change vs PY. Sort ascending and colour negative bars red (Format > Bars > Colors > Conditional formatting on the measure).
- **Matrix:** rows = `dim_date[Year]`, values = Revenue Transactions, Avg Revenue per Transaction, Total Revenue. It shows that the drop comes from fewer deals (272 to 232), not smaller deals.
- **Expense bar chart:** Y = `dim_category[Category]` filtered to Type = Expense, X = Expense Change vs PY.

### Page 3: Department and region performance

- **Matrix:** rows = Department, columns = Region, values = Profit Margin %. Add conditional formatting (Cell elements > Background color > Gradient) with red for the minimum, yellow for the middle and green for the maximum.
- **Bar chart:** Net Profit by Department, with Net Profit Color as the bar colour.
- **Column chart:** Total Revenue by `dim_category[Category]` filtered to Type = Revenue.
- **Table:** Department, Region, Net Profit, sorted descending, top 10 (add a Top N filter).

## 7. Polish

- Sync the Year slicer across pages (**View > Sync slicers**), except on page 2 where it is set to 2024.
- Give every page a title and every chart a clear title. Remove gridlines and borders you do not need.
- Add alt text to the main visuals.
- Check **View > Mobile layout** only if you plan to show it on a phone.
- Rename the pages: `Overview`, `Why did 2024 fall`, `Department and Region`.

## 8. Save and publish

1. Save as `finance_dashboard.pbix` into this folder (`powerbi/`).
2. Export PDF: **File > Export > Export to PDF**.
3. Take a screenshot of each page and save them as `powerbi/screenshots/page1_overview.png`, and so on. Put page 1 in the main README.
4. Optional: publish to the Power BI Service (free work or school account needed). **Do not use "Publish to web" unless the data is public.** This dataset is a practice set, so it is fine only if you say that clearly.

## Interview tips

- Know why `dim_date` must be a marked date table (time-intelligence functions like `SAMEPERIODLASTYEAR` depend on it).
- Know the difference between a calculated column and a measure, and why every number here is a measure.
- Be ready to explain the star schema: one fact table, four dimension tables.
- Be ready to say the 2024 drop is not statistically significant (Python notebook, section 8).
