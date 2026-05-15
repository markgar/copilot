"""
03 — Reshape fact_actuals amounts to add realism.

Applies three transformations to the raw aggregated amounts:
  1. YoY growth  — ~8% annual increase (2021 base, 2022 ~1.08x, 2023 ~1.17x)
  2. Seasonality — monthly multipliers per category so trends are visible
  3. Variance stories — specific department/quarter spikes for demo narrative:
       - Marketing overspend in 2023-Q2 (product launch)
       - IT spike in 2023-Q3 (infrastructure migration)
       - Sales travel spike in 2023-Q4 (conferences)

Reads/writes fact_actuals.csv and dim_month.csv (for month metadata).
"""

import csv
import random
from pathlib import Path

DATASET_DIR = Path(__file__).parent.parent / "dataset"
FACT_FILE = DATASET_DIR / "fact_actuals.csv"
MONTH_FILE = DATASET_DIR / "dim_month.csv"
DEPT_FILE = DATASET_DIR / "dim_department.csv"
CAT_FILE = DATASET_DIR / "dim_category.csv"

random.seed(42)  # reproducible

# --- Load lookups ---

def load_csv(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

months = {int(m["MonthKey"]): m for m in load_csv(MONTH_FILE)}
depts = {int(d["DepartmentKey"]): d["Department"] for d in load_csv(DEPT_FILE)}
cats = {int(c["CategoryKey"]): c["Category"] for c in load_csv(CAT_FILE)}
facts = load_csv(FACT_FILE)

# --- 1. Normalize base amounts ---
# The raw data has random amounts. Replace with a base amount per category
# that we then modify with growth, seasonality, and stories.

BASE_AMOUNTS = {
    "Salaries":       800_000,
    "Infrastructure": 400_000,
    "Marketing":      300_000,
    "Travel":         150_000,
    "Training":       100_000,
    "Utilities":      200_000,
}

# --- 2. YoY growth multipliers ---
YEAR_GROWTH = {
    2021: 1.00,
    2022: 1.08,
    2023: 1.17,
}

# --- 3. Seasonality by category (monthly multipliers, indexed 1-12) ---
# These create visible patterns in charts
SEASONALITY = {
    "Salaries":       [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.05],  # small year-end bonus bump
    "Infrastructure": [0.8, 0.8, 0.9, 1.0, 1.0, 1.1, 1.1, 1.1, 1.0, 1.0, 0.9, 0.9],    # summer projects
    "Marketing":      [0.7, 0.8, 1.0, 1.1, 1.2, 1.1, 0.9, 0.8, 1.0, 1.1, 1.2, 0.8],    # spring + fall campaigns
    "Travel":         [0.6, 0.7, 0.9, 1.0, 1.0, 0.8, 0.7, 0.7, 1.1, 1.3, 1.4, 0.5],    # Q4 conferences
    "Training":       [1.2, 1.0, 0.9, 0.8, 0.7, 0.6, 0.6, 0.7, 1.0, 1.1, 1.2, 1.5],    # year-end use-it-or-lose-it
    "Utilities":      [1.2, 1.2, 1.0, 0.9, 0.8, 0.8, 0.9, 0.9, 0.9, 1.0, 1.1, 1.2],    # winter heating
}

# --- 4. Variance stories (multipliers applied on top) ---
# Key: (Department, Year, Quarter) → multiplier
VARIANCE_STORIES = {
    ("Marketing", 2023, "Q2"): 1.65,   # product launch overspend
    ("IT", 2023, "Q3"):        1.80,   # infrastructure migration
    ("Sales", 2023, "Q4"):     1.45,   # conference season travel blowout
}

# --- Generate new amounts ---

for row in facts:
    mk = int(row["MonthKey"])
    dk = int(row["DepartmentKey"])
    ck = int(row["CategoryKey"])

    month_info = months[mk]
    dept_name = depts[dk]
    cat_name = cats[ck]
    year = int(month_info["Year"])
    month_num = int(month_info["MonthNum"])
    quarter = month_info["Quarter"]

    # Base amount for this category
    base = BASE_AMOUNTS[cat_name]

    # Apply YoY growth
    amount = base * YEAR_GROWTH.get(year, 1.0)

    # Apply seasonality
    season_mult = SEASONALITY[cat_name][month_num - 1]
    amount *= season_mult

    # Apply variance story if applicable
    story_key = (dept_name, year, quarter)
    if story_key in VARIANCE_STORIES:
        # Only apply to relevant categories
        if story_key == ("Marketing", 2023, "Q2"):
            if cat_name in ("Marketing", "Travel"):
                amount *= VARIANCE_STORIES[story_key]
        elif story_key == ("IT", 2023, "Q3"):
            if cat_name in ("Infrastructure", "Utilities"):
                amount *= VARIANCE_STORIES[story_key]
        elif story_key == ("Sales", 2023, "Q4"):
            if cat_name == "Travel":
                amount *= VARIANCE_STORIES[story_key]

    # Add some noise (±5%) so it doesn't look perfectly synthetic
    noise = random.uniform(0.95, 1.05)
    amount *= noise

    row["ActualAmount"] = round(amount)

# --- Write back ---

fieldnames = ["ActualKey", "MonthKey", "DepartmentKey", "CategoryKey", "ActualAmount"]
with open(FACT_FILE, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(facts)

print(f"fact_actuals.csv reshaped: {len(facts)} rows")
print("Applied: YoY growth, seasonality, variance stories, ±5% noise")
print("Variance stories planted:")
print("  - Marketing overspend 2023-Q2 (product launch) → Marketing+Travel 1.65x")
print("  - IT spike 2023-Q3 (infra migration) → Infrastructure+Utilities 1.80x")
print("  - Sales travel spike 2023-Q4 (conferences) → Travel 1.45x")
