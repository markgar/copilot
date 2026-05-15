"""
04 — Generate a headcount driver table.

Creates fact_headcount.csv with monthly headcount per department.
Use in the demo to show driver-based planning: headcount × avg salary = payroll.

Pattern:
  - Base headcount per department (realistic relative sizes)
  - Gradual growth year over year
  - Occasional hire bumps (Sales Q1 ramp, Marketing Q2 for launch)
"""

import csv
import random
from pathlib import Path

DATASET_DIR = Path(__file__).parent.parent / "dataset"
MONTH_FILE = DATASET_DIR / "dim_month.csv"
DEPT_FILE = DATASET_DIR / "dim_department.csv"

random.seed(99)

def load_csv(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

months = load_csv(MONTH_FILE)
depts = load_csv(DEPT_FILE)

# Base headcount per department (2021-01 starting point)
BASE_HC = {
    "Sales": 45,
    "Marketing": 25,
    "IT": 30,
    "Operations": 50,
    "Finance": 15,
    "HR": 10,
}

# Monthly growth rate per department (compounding)
MONTHLY_GROWTH = {
    "Sales": 0.005,       # ~6% annual
    "Marketing": 0.004,   # ~5% annual
    "IT": 0.006,          # ~7% annual
    "Operations": 0.002,  # ~2.5% annual
    "Finance": 0.001,     # ~1.2% annual
    "HR": 0.001,          # ~1.2% annual
}

# One-time hire bumps: (Department, Year, Quarter) → extra heads
HIRE_BUMPS = {
    ("Sales", 2022, "Q1"): 5,       # new territory ramp
    ("Sales", 2023, "Q1"): 4,       # another Q1 ramp
    ("Marketing", 2023, "Q2"): 6,   # product launch team
    ("IT", 2023, "Q3"): 8,          # infra migration contractors
}

rows = []
row_id = 0

for dept in depts:
    dept_name = dept["Department"]
    dk = int(dept["DepartmentKey"])
    hc = float(BASE_HC[dept_name])
    growth = MONTHLY_GROWTH[dept_name]

    for m in months:
        mk = int(m["MonthKey"])
        year = int(m["Year"])
        quarter = m["Quarter"]
        month_num = int(m["MonthNum"])

        # Apply growth
        hc *= (1 + growth)

        # Apply hire bumps (spread across the quarter's first month)
        bump_key = (dept_name, year, quarter)
        if bump_key in HIRE_BUMPS and month_num in (1, 4, 7, 10):
            hc += HIRE_BUMPS[bump_key]

        # Small random fluctuation (±1 person for attrition/backfill)
        noise = random.choice([-1, 0, 0, 0, 1])

        row_id += 1
        rows.append({
            "HeadcountKey": row_id,
            "MonthKey": mk,
            "DepartmentKey": dk,
            "Headcount": max(1, round(hc + noise)),
        })

# Write
out = DATASET_DIR / "fact_headcount.csv"
fieldnames = ["HeadcountKey", "MonthKey", "DepartmentKey", "Headcount"]
with open(out, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print(f"fact_headcount.csv created: {len(rows)} rows")
print("Departments and starting headcount:")
for d, h in BASE_HC.items():
    print(f"  {d}: {h}")
print("Hire bumps planted:")
for (d, y, q), n in HIRE_BUMPS.items():
    print(f"  {d} {y}-{q}: +{n} heads")
