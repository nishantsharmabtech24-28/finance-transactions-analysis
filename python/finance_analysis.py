"""
Finance Transactions Analysis (2023-2024)

Question: revenue fell about 13% in 2024 while expenses rose about 13%.
Where did the change come from, and is it real or normal month-to-month noise?

Setup:   pip install pandas numpy matplotlib scipy
Run:     python finance_analysis.py
Data:    set DATA_FILE below if your CSV is somewhere else.
Output:  printed tables in the terminal, charts saved in a "figures" folder
         next to this script, and chart windows at the end.
"""
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.ticker as mt
import numpy as np
import pandas as pd
from scipy import stats

# ---------------------------------------------------------------------------
# 0. Settings
# ---------------------------------------------------------------------------
HERE = Path(__file__).resolve().parent if "__file__" in globals() else Path.cwd()

# Change this line if your CSV is in a different place, for example:
# DATA_FILE = Path(r"C:\Users\you\Downloads\company_finance_transactions.csv")
DATA_FILE = HERE.parent / "data" / "raw" / "company_finance_transactions.csv"

FIG_DIR = HERE / "figures"
FIG_DIR.mkdir(exist_ok=True)

REV, EXP, NEG = "#2a5db0", "#d9822b", "#c0392b"
K = mt.FuncFormatter(lambda v, _: f"{v / 1000:.0f}K")
plt.rcParams.update({
    "figure.dpi": 110,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.color": "#e5e5e5",
    "axes.axisbelow": True,
})
pd.set_option("display.width", 140)
pd.set_option("display.max_columns", 20)


def section(title):
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)


# ---------------------------------------------------------------------------
# 1. Load and inspect the raw data
# ---------------------------------------------------------------------------
section("1. Raw data")
raw = pd.read_csv(DATA_FILE, parse_dates=["date"])
print("rows:", len(raw))
print("exact duplicate rows:", raw.duplicated().sum())
print("missing values:", int(raw.isna().sum().sum()),
      "| negative amounts:", int((raw.amount < 0).sum()))
print("department spellings:", sorted(raw.department.unique()))
print("region spellings:", sorted(raw.region.unique()))

# ---------------------------------------------------------------------------
# 2. Clean (same rules as the SQL clean_transactions view)
# ---------------------------------------------------------------------------
section("2. Cleaning")


def clean_department(name):
    name = name.strip()
    return name.upper() if name.lower() in ("hr", "it", "r&d") else name.title()


df = raw.copy()
df["department"] = df["department"].map(clean_department)
for col in ["region", "type", "category"]:
    df[col] = df[col].str.strip()
df["region"] = df["region"].str.title()
df = df.drop_duplicates().sort_values("date").reset_index(drop=True)

df["year"] = df.date.dt.year
df["month"] = df.date.dt.to_period("M").dt.to_timestamp()
df["signed"] = np.where(df.type == "Revenue", df.amount, -df.amount)  # revenue +, expense -

print("rows after cleaning:", len(df))
print("departments:", sorted(df.department.unique()))
print("regions:", sorted(df.region.unique()))

# ---------------------------------------------------------------------------
# 3. Headline numbers
# ---------------------------------------------------------------------------
section("3. Headline numbers")
rev = df.loc[df.type == "Revenue", "amount"].sum()
exp = df.loc[df.type == "Expense", "amount"].sum()
print(pd.Series({
    "Revenue": rev,
    "Expense": exp,
    "Net profit": rev - exp,
    "Margin %": (rev - exp) / rev * 100,
}).round(1))

# ---------------------------------------------------------------------------
# 4. Monthly trend
# ---------------------------------------------------------------------------
section("4. Monthly trend")
m = df.pivot_table(index="month", columns="type", values="amount", aggfunc="sum")
m["net"] = m.Revenue - m.Expense
print("loss-making months:")
print(m[m.net < 0].round(0))

fig1, ax = plt.subplots(figsize=(11, 4.2))
ax.plot(m.index, m.Revenue, color=REV, lw=2, label="Revenue")
ax.plot(m.index, m.Revenue.rolling(3).mean(), color=REV, lw=1.5, ls="--",
        alpha=0.7, label="Revenue, 3-month average")
ax.plot(m.index, m.Expense, color=EXP, lw=2, label="Expense")
loss = m[m.net < 0]
ax.scatter(loss.index, loss.Revenue, color=NEG, zorder=5)
for when, row in loss.iterrows():
    ax.annotate(f"{when:%b %Y}: net loss", (when, row.Revenue), xytext=(-110, -42),
                textcoords="offset points", color=NEG, fontsize=9,
                arrowprops=dict(arrowstyle="->", color=NEG))
ax.set_ylim(0, 155000)
ax.yaxis.set_major_formatter(K)
ax.set_title("Monthly revenue and expense", loc="left", fontweight="bold")
ax.legend(frameon=False, ncol=3, loc="upper right")
fig1.tight_layout()
fig1.savefig(FIG_DIR / "01_monthly_trend.png")

# ---------------------------------------------------------------------------
# 5. Year over year: volume or value?
# ---------------------------------------------------------------------------
section("5. Year over year: fewer deals or smaller deals?")


def yearly(kind):
    grouped = df[df.type == kind].groupby("year").amount
    return pd.DataFrame({"total": grouped.sum(),
                         "transactions": grouped.count(),
                         "avg_size": grouped.mean()})


rev_y, exp_y = yearly("Revenue"), yearly("Expense")
print("Revenue by year");  print(rev_y.round(0))
print("\nExpense by year"); print(exp_y.round(0))
print("\nChange 2023 to 2024 (%)")
print(pd.DataFrame({
    "Revenue": (rev_y.loc[2024] / rev_y.loc[2023] - 1) * 100,
    "Expense": (exp_y.loc[2024] / exp_y.loc[2023] - 1) * 100,
}).round(1))

# ---------------------------------------------------------------------------
# 6. Where did revenue fall?
# ---------------------------------------------------------------------------
section("6. Revenue change 2023 to 2024")
rev_df = df[df.type == "Revenue"]


def change_by(col, data):
    p = data.pivot_table(index=col, columns="year", values="amount", aggfunc="sum")
    p["change"] = p[2024] - p[2023]
    p["change_pct"] = p.change / p[2023] * 100
    return p.sort_values("change")


fig2, axes = plt.subplots(1, 3, figsize=(14, 4), sharex=True)
for ax, col in zip(axes, ["category", "region", "department"]):
    c = change_by(col, rev_df)
    print(f"\nBy {col}")
    print(c.round(0))
    ax.barh(c.index, c.change, color=[NEG if v < 0 else REV for v in c.change])
    ax.axvline(0, color="#555", lw=0.8)
    ax.set_title(f"Revenue change by {col}", loc="left", fontweight="bold", fontsize=10)
    ax.xaxis.set_major_formatter(K)
    ax.set_xlim(-105000, 45000)
    for i, (v, pct) in enumerate(zip(c.change, c.change_pct)):
        ax.text(v + (2000 if v >= 0 else -2000), i, f"{int(round(pct)):+d}%",
                va="center", ha="left" if v >= 0 else "right", fontsize=8)
fig2.tight_layout()
fig2.savefig(FIG_DIR / "02_revenue_change_drivers.png")

# ---------------------------------------------------------------------------
# 7. Where did expenses rise?
# ---------------------------------------------------------------------------
section("7. Expense change 2023 to 2024 by category")
exp_c = change_by("category", df[df.type == "Expense"])
print(exp_c.round(0))

fig3, ax = plt.subplots(figsize=(8, 4))
ax.barh(exp_c.index, exp_c.change, color=[REV if v < 0 else EXP for v in exp_c.change])
ax.axvline(0, color="#555", lw=0.8)
ax.xaxis.set_major_formatter(K)
ax.set_title("Expense change by category, 2023 to 2024", loc="left", fontweight="bold")
fig3.tight_layout()
fig3.savefig(FIG_DIR / "03_expense_change_drivers.png")

# ---------------------------------------------------------------------------
# 8. Is the 2024 revenue drop statistically significant?
# ---------------------------------------------------------------------------
section("8. Significance test on monthly revenue")
y23 = m.Revenue[m.index.year == 2023]
y24 = m.Revenue[m.index.year == 2024]
welch = stats.ttest_ind(y23, y24, equal_var=False)
mwu = stats.mannwhitneyu(y23, y24)
print(f"mean monthly revenue 2023: {y23.mean():,.0f} | 2024: {y24.mean():,.0f} "
      f"| difference: {y23.mean() - y24.mean():,.0f}")
print(f"std of monthly revenue 2023: {y23.std():,.0f} | 2024: {y24.std():,.0f}")
print(f"Welch t-test p-value: {welch.pvalue:.3f}")
print(f"Mann-Whitney p-value: {mwu.pvalue:.3f}")
verdict = "IS" if min(welch.pvalue, mwu.pvalue) < 0.05 else "is NOT"
print(f"-> the 2024 revenue decline {verdict} statistically significant at the 5% level.")

# ---------------------------------------------------------------------------
# 9. Outliers
# ---------------------------------------------------------------------------
section("9. Outliers (above Q3 + 1.5 x IQR within each type)")
grp = df.groupby("type").amount
q1 = grp.transform(lambda s: s.quantile(0.25))
q3 = grp.transform(lambda s: s.quantile(0.75))
df["outlier"] = df.amount > q3 + 1.5 * (q3 - q1)
print(df.groupby("type").outlier.agg(["sum", "mean"])
        .rename(columns={"sum": "outliers", "mean": "share"}).round(3))
print("\nLargest transactions:")
print(df.nlargest(5, "amount")[["date", "department", "region", "type", "category", "amount"]])

# ---------------------------------------------------------------------------
# 10. Profit margin by department and region
# ---------------------------------------------------------------------------
section("10. Profit margin % by department and region")
net = df.pivot_table(index="department", columns="region", values="signed", aggfunc="sum")
revenue = rev_df.pivot_table(index="department", columns="region", values="amount", aggfunc="sum")
margin = net / revenue * 100
margin = margin.loc[(net.sum(axis=1) / revenue.sum(axis=1)).sort_values(ascending=False).index]
print(margin.round(0))

fig4, ax = plt.subplots(figsize=(7, 4.6))
im = ax.imshow(margin.values, cmap="RdYlGn", vmin=-20, vmax=90, aspect="auto")
ax.set_xticks(range(margin.shape[1]))
ax.set_xticklabels(margin.columns)
ax.set_yticks(range(margin.shape[0]))
ax.set_yticklabels(margin.index)
ax.grid(False)
for i in range(margin.shape[0]):
    for j in range(margin.shape[1]):
        ax.text(j, i, f"{margin.values[i, j]:.0f}%", ha="center", va="center", fontsize=9)
ax.set_title("Profit margin % by department and region", loc="left", fontweight="bold")
fig4.colorbar(im, ax=ax, shrink=0.8)
fig4.tight_layout()
fig4.savefig(FIG_DIR / "04_margin_heatmap.png")

# ---------------------------------------------------------------------------
# 11. Conclusions
# ---------------------------------------------------------------------------
section("11. Conclusions")
print("""\
1. The company is profitable (56% margin), but 2024 revenue fell 13% and expenses rose 13%.
2. The revenue fall is a volume problem (about 15% fewer revenue transactions),
   concentrated in Product Sales, Licensing, East and West, and Sales and R&D.
3. The expense rise is also volume-driven: Marketing Spend, Utilities and Software.
4. With 24 months of data the revenue decline is not statistically significant,
   so treat it as a warning sign to monitor, not a proven trend.
5. Finance-East is the weakest combination (a loss) and East has the lowest margin.""")

print(f"\nCharts saved in: {FIG_DIR}")
plt.show()
