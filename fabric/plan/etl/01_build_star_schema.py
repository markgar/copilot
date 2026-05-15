"""
Build a star schema from demo-actuals.csv.
Outputs: dim_department.csv, dim_category.csv, dim_month.csv, fact_actuals.csv
"""

import csv
from pathlib import Path
import calendar

ETL_DIR = Path(__file__).parent
WORKING_DIR = ETL_DIR.parent / "working"
DATASET_DIR = ETL_DIR.parent / "dataset"
INPUT = WORKING_DIR / "demo-actuals.csv"

# Read source data
with open(INPUT, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    rows = list(reader)

# --- Build dimensions ---

# DimDepartment
departments = sorted(set(r["Department"] for r in rows))
dept_lookup = {}
dim_department = []
for i, dept in enumerate(departments, start=1):
    dept_lookup[dept] = i
    dim_department.append({"DepartmentKey": i, "Department": dept})

# DimCategory
categories = sorted(set(r["Category"] for r in rows))
cat_lookup = {}
dim_category = []
for i, cat in enumerate(categories, start=1):
    cat_lookup[cat] = i
    dim_category.append({"CategoryKey": i, "Category": cat})

# DimMonth
months = sorted(set(r["Month"] for r in rows))
month_lookup = {}
dim_month = []
for i, m in enumerate(months, start=1):
    year, mo = m.split("-")
    quarter = f"Q{(int(mo) - 1) // 3 + 1}"
    month_lookup[m] = i
    month_name = f"{calendar.month_name[int(mo)]} {year}"
    dim_month.append({
        "MonthKey": i,
        "Month": month_name,
        "MonthNum": int(mo),
        "Quarter": quarter,
        "Year": int(year),
    })

# --- Build fact table ---
fact_actuals = []
for i, r in enumerate(rows, start=1):
    fact_actuals.append({
        "ActualKey": i,
        "MonthKey": month_lookup[r["Month"]],
        "DepartmentKey": dept_lookup[r["Department"]],
        "CategoryKey": cat_lookup[r["Category"]],
        "ActualAmount": r["ActualAmount"],
    })

# --- Write CSVs ---

def write_csv(filename, data):
    DATASET_DIR.mkdir(exist_ok=True)
    path = DATASET_DIR / filename
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
    print(f"  {filename}: {len(data)} rows")

print("Writing star schema CSVs:")
write_csv("dim_department.csv", dim_department)
write_csv("dim_category.csv", dim_category)
write_csv("dim_month.csv", dim_month)
write_csv("fact_actuals.csv", fact_actuals)
print("Done.")
