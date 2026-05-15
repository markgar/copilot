"""
Verify the demo dataset has the intended characteristics:
  1. Department hierarchy (Division column)
  2. YoY growth (~8% annual)
  3. Seasonality patterns per category
  4. Variance stories in specific dept/quarter combos
  5. Headcount driver table with growth and hire bumps
"""

import csv
from collections import defaultdict
from pathlib import Path

DATASET_DIR = Path(__file__).parent.parent / "dataset"

def load_csv(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

depts = load_csv(DATASET_DIR / "dim_department.csv")
cats = {int(c["CategoryKey"]): c["Category"] for c in load_csv(DATASET_DIR / "dim_category.csv")}
months = {int(m["MonthKey"]): m for m in load_csv(DATASET_DIR / "dim_month.csv")}
dept_map = {int(d["DepartmentKey"]): d for d in depts}
facts = load_csv(DATASET_DIR / "fact_actuals.csv")
headcount = load_csv(DATASET_DIR / "fact_headcount.csv")

print("=" * 60)
print("1. DEPARTMENT HIERARCHY")
print("=" * 60)
for d in depts:
    print(f"  {d['Division']:12s} → {d['Department']}")

print()
print("=" * 60)
print("2. YOY GROWTH (total spend by year)")
print("=" * 60)
yearly = defaultdict(float)
for r in facts:
    year = months[int(r["MonthKey"])]["Year"]
    yearly[year] += float(r["ActualAmount"])
base = None
for year in sorted(yearly):
    total = yearly[year]
    if base is None:
        base = total
        print(f"  {year}: ${total:>14,.0f}  (base)")
    else:
        growth = (total / base - 1) * 100
        print(f"  {year}: ${total:>14,.0f}  ({growth:+.1f}% vs 2021)")

print()
print("=" * 60)
print("3. SEASONALITY — Travel spend by month (all depts, 2023)")
print("=" * 60)
travel_key = [k for k, v in cats.items() if v == "Travel"][0]
travel_by_month = defaultdict(float)
for r in facts:
    mi = months[int(r["MonthKey"])]
    if mi["Year"] == "2023" and int(r["CategoryKey"]) == travel_key:
        travel_by_month[int(mi["MonthNum"])] += float(r["ActualAmount"])
for m in range(1, 13):
    bar = "█" * int(travel_by_month[m] / 40_000)
    print(f"  {m:2d}: ${travel_by_month[m]:>10,.0f}  {bar}")

print()
print("=" * 60)
print("4. VARIANCE STORIES")
print("=" * 60)

# Helper: sum by dept/year/quarter/category
def sum_by(dept_name, year_str, quarter, cat_name=None):
    total = 0
    for r in facts:
        mi = months[int(r["MonthKey"])]
        dn = dept_map[int(r["DepartmentKey"])]["Department"]
        cn = cats[int(r["CategoryKey"])]
        if dn == dept_name and mi["Year"] == year_str and mi["Quarter"] == quarter:
            if cat_name is None or cn == cat_name:
                total += float(r["ActualAmount"])
    return total

# Marketing Q2 2023 vs Q2 2022 (Marketing + Travel categories)
mkt_q2_22 = sum_by("Marketing", "2022", "Q2", "Marketing") + sum_by("Marketing", "2022", "Q2", "Travel")
mkt_q2_23 = sum_by("Marketing", "2023", "Q2", "Marketing") + sum_by("Marketing", "2023", "Q2", "Travel")
print(f"  Marketing (Marketing+Travel) Q2:")
print(f"    2022: ${mkt_q2_22:>10,.0f}")
print(f"    2023: ${mkt_q2_23:>10,.0f}  ({(mkt_q2_23/mkt_q2_22 - 1)*100:+.0f}% — product launch spike)")

# IT Q3 2023 vs Q3 2022 (Infrastructure + Utilities)
it_q3_22 = sum_by("IT", "2022", "Q3", "Infrastructure") + sum_by("IT", "2022", "Q3", "Utilities")
it_q3_23 = sum_by("IT", "2023", "Q3", "Infrastructure") + sum_by("IT", "2023", "Q3", "Utilities")
print(f"  IT (Infra+Utilities) Q3:")
print(f"    2022: ${it_q3_22:>10,.0f}")
print(f"    2023: ${it_q3_23:>10,.0f}  ({(it_q3_23/it_q3_22 - 1)*100:+.0f}% — infra migration spike)")

# Sales Q4 2023 vs Q4 2022 (Travel)
sales_q4_22 = sum_by("Sales", "2022", "Q4", "Travel")
sales_q4_23 = sum_by("Sales", "2023", "Q4", "Travel")
print(f"  Sales (Travel) Q4:")
print(f"    2022: ${sales_q4_22:>10,.0f}")
print(f"    2023: ${sales_q4_23:>10,.0f}  ({(sales_q4_23/sales_q4_22 - 1)*100:+.0f}% — conference spike)")

print()
print("=" * 60)
print("5. HEADCOUNT — by department, start vs end")
print("=" * 60)
hc_by_dept = defaultdict(list)
for r in headcount:
    dn = dept_map[int(r["DepartmentKey"])]["Department"]
    hc_by_dept[dn].append((int(r["MonthKey"]), int(r["Headcount"])))

for dept in sorted(hc_by_dept):
    sorted_hc = sorted(hc_by_dept[dept], key=lambda x: x[0])
    first = sorted_hc[0][1]
    last = sorted_hc[-1][1]
    print(f"  {dept:12s}: {first:3d} → {last:3d}  ({last - first:+d})")

# Check the specific hire bumps
print()
print("  Hire bump verification:")
for r in headcount:
    mi = months[int(r["MonthKey"])]
    dn = dept_map[int(r["DepartmentKey"])]["Department"]
    if dn == "Marketing" and mi["Year"] == "2023" and mi["MonthNum"] == "4":
        print(f"    Marketing 2023-04: {r['Headcount']} (should show Q2 bump)")
    if dn == "IT" and mi["Year"] == "2023" and mi["MonthNum"] == "7":
        print(f"    IT 2023-07: {r['Headcount']} (should show Q3 bump)")

print()
print("All checks complete.")
