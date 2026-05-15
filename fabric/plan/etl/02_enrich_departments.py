"""
02 — Add division hierarchy to dim_department.csv.

Groups departments into divisions so Planning sheets can demo roll-ups:
  Revenue:    Sales, Marketing
  Operations: IT, Operations
  Corporate:  Finance, HR
"""

import csv
from pathlib import Path

DATASET_DIR = Path(__file__).parent.parent / "dataset"
FILE = DATASET_DIR / "dim_department.csv"

DIVISION_MAP = {
    "Sales": "Revenue",
    "Marketing": "Revenue",
    "IT": "Operations",
    "Operations": "Operations",
    "Finance": "Corporate",
    "HR": "Corporate",
}

# Read existing dim
with open(FILE, newline="", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))

# Add Division column
for row in rows:
    row["Division"] = DIVISION_MAP[row["Department"]]

# Write back
fieldnames = ["DepartmentKey", "Department", "Division"]
with open(FILE, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print("dim_department.csv updated with Division hierarchy:")
for r in rows:
    print(f"  {r['Department']} → {r['Division']}")
