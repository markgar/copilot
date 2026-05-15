# Fabric Plan — Finance User Demo Script

This demo is for the **finance audience**. The goal is to get them saying "this is easy," "this is cool," or "I can't do this today" — and then asking their data team to set it up. You are not showing connectivity, pipelines, or semantic model configuration. You are showing what the finance user touches.

**Pre-work (done before the demo, not shown to the audience):**

- A Fabric workspace with a Plan item already created
- The demo dataset loaded into a semantic model (dim_department, dim_category, dim_month, fact_actuals, fact_headcount)
- A cloud connection to the semantic model already configured
- A Planning sheet already connected to the semantic model with Department, Category, and Month dimensions mapped
- An Intelligence sheet with a pre-built BvA report (see Scene 4 setup notes)

---

## Scene 1 — Build a Budget (~8 min)

**Reaction you want:** "This is easy. I already know how to do this."

### What to show

1. **Open the Planning sheet.** Departments down the left, months across the top. Say: "This is your budget. It looks like Excel because it works like Excel."

2. **Enter numbers.** Click into a few cells in the Sales row and type budget figures for Jan, Feb, Mar. No menus, no special UI — just click and type. Say: "You already know how to do this."

3. **Add a formula row.** Insert a Total row. Use an Excel-style SUM formula to total the months. Say: "Same formulas you use in Excel. Nothing new to learn."

4. **Show the hierarchy.** Expand the Revenue division — Sales and Marketing appear underneath. Collapse it — the numbers roll up automatically. Then expand Operations (IT + Operations) and Corporate (Finance + HR). Say: "No pivot table setup. The hierarchy is built into the model. Expand, collapse, and the math just works."

5. **Template rows.** Create a template row for a standard expense line (e.g., "Contractor Costs") and apply it across departments. Say: "Set the pattern once, reuse it everywhere. No copy-paste across 20 tabs."

### Talking points during this scene

- "Your data team set up the connection once. You never see that part."
- "The dimensions — departments, accounts, months — come from the same semantic model your reports use. Same definitions, same numbers."
- "This replaces the spreadsheet your team emails back and forth every October."

---

## Scene 2 — What-If and Snapshots (~5 min)

**Reaction you want:** "This is cool. I can't do this today."

### What to show

6. **What-if simulation.** Select the Marketing row. Apply a -15% scenario. The numbers ripple through the hierarchy — the Revenue division total drops, the company total drops. Say: "You don't rebuild the spreadsheet. You ask 'what if' and see the answer immediately."

7. **Take a snapshot.** Save the current state as "Base Case." Then apply a different scenario — +10% growth on Sales. Save as "Optimistic." Show both side by side. Say: "Every version is saved. No more Budget_v7_final_FINAL.xlsx."

8. **Rolling forecast.** Show how to copy actuals forward from the closed months and project the remaining months using an average of recent actuals. Say: "Your forecast updates in 30 seconds, not 3 days."

### Talking points during this scene

- "In Excel, scenario modeling means duplicating the whole workbook. Here it's a button."
- "Snapshots are permanent. You can always go back and compare. The CFO asks 'what did we assume in March?' — you pull it up in two clicks."

---

## Scene 3 — Writeback (~2 min)

**Reaction you want:** "So my data team can see this immediately?"

### What to show

9. **Trigger a writeback.** Click the writeback button. The budget numbers land in a Fabric SQL database. Say: "That's it. Your budget is now in a database your analytics team can query, report on, or pipeline — no export, no email."

10. **Show the confirmation.** Point to the writeback log showing success. Say: "Every writeback is logged. You know exactly when the numbers were published and by whom."

### Talking points during this scene

- "The data team doesn't have to ask you for the file. They don't have to import anything. It's already in Fabric."
- "This is how budget and actuals end up in the same model — the data team wires this table into the semantic model once, and from then on, every writeback flows through automatically."

---

## Scene 4 — Budget vs. Actual Reporting (~5 min)

**Reaction you want:** "The CFO would actually use this."

### What to show

11. **Open the Intelligence sheet.** Show a pre-built BvA (Budget vs. Actual) report. Use IBCS-formatted charts — waterfall or bar charts with red/green variance indicators. The data shows the three years of actuals with visible trends (YoY growth, seasonal patterns). Say: "This is your variance report. Built once, updates automatically."

12. **Drill into a variance.** Click into Marketing for Q2 2023. The breakdown shows Marketing and Travel categories spiked — that's the product launch story baked into the data. Say: "You don't email the department head asking 'what happened?' You drill in and see it."

    Other stories you can drill into:
    - **IT Q3 2023** — Infrastructure and Utilities spiked ~90% (infrastructure migration)
    - **Sales Q4 2023** — Travel up ~57% (conference season)

13. **Add an annotation.** Click the Marketing Q2 data point and add a comment: "Overspend due to Q2 product launch — approved by VP Marketing." Show that it's threaded — others can reply. Say: "The explanation lives with the number. Not in a separate email chain nobody can find in January."

14. **Export to PDF.** One click — pixel-perfect output with header and logo. Say: "This is your board deck. Done."

### Talking points during this scene

- "The variance stories are real. You drill in, you see the category-level detail, you annotate it, and the next person who looks at this report sees the explanation."
- "100+ chart types. IBCS formatting. Paginated reports. This isn't a dashboard — it's a finance reporting tool."

---

## Scene 5 (Optional) — Driver-Based Planning with Headcount (~3 min)

**Only show this if time allows or the customer mentions workforce planning.**

**Reaction you want:** "We've been trying to do this in Excel for years."

### What to show

15. **Open a second Planning sheet** connected to the headcount data. Show Department × Month with headcount numbers. Point out the growth pattern and the hire bumps (Sales Q1 ramps, Marketing Q2 product launch team, IT Q3 migration contractors).

16. **Add a formula row** that calculates payroll: `Headcount × Average Salary`. Change the headcount for a department — the payroll number updates instantly. Say: "This is driver-based planning. Change the input, the output recalculates. No circular references, no broken links across workbooks."

### Talking points during this scene

- "The headcount data comes from the same platform. HR updates it, and your payroll forecast updates automatically."
- "This is the pattern for any driver-based model — headcount × salary, units × price, square footage × cost per sqft."

---

## What NOT to Show

- **Cloud connection setup** — "Your data team does this once. You never see it."
- **Semantic model configuration** — same. Not your audience.
- **InfoBridge** — too technical. Save for the data engineering follow-up.
- **Model editor** — the data team's concern.
- **Limitations** — don't volunteer them. If asked, be honest, but this demo is about creating desire, not due diligence. Due diligence comes in the follow-up.

---

## Demo Dataset

The demo data is in `fabric/plan/`. It was built from a [Kaggle budget-vs-actual dataset](https://www.kaggle.com/datasets/kennathalexanderroy/budget-vs-actual-financial-dataset) and enhanced with a Python pipeline.

### Files to load into the semantic model

Located in `fabric/plan/dataset/`:

| File | What it is |
|---|---|
| `dim_department.csv` | 6 departments grouped into 3 divisions (Revenue, Operations, Corporate) |
| `dim_category.csv` | 6 expense categories (Salaries, Infrastructure, Marketing, Travel, Training, Utilities) |
| `dim_month.csv` | 36 months (Jan 2021–Dec 2023) with Quarter and Year attributes |
| `fact_actuals.csv` | 1,296 rows of monthly actuals by department and category |
| `fact_headcount.csv` | 216 rows of monthly headcount by department |

### Stories baked into the data

| What | Where | Detail |
|---|---|---|
| YoY growth | All departments | ~8% annual increase (2021 → 2022 → 2023) |
| Seasonality | All categories | Travel peaks in Q4, training spikes in Dec, marketing has spring + fall campaigns |
| Marketing overspend | Marketing, Q2 2023 | Marketing + Travel categories ~80% above prior year (product launch) |
| IT infrastructure spike | IT, Q3 2023 | Infrastructure + Utilities ~90% above prior year (migration project) |
| Sales travel spike | Sales, Q4 2023 | Travel ~57% above prior year (conference season) |
| Headcount ramps | Sales Q1, Marketing Q2, IT Q3 | Hire bumps aligned with the spending stories above |

### Rebuild pipeline

Run in order from the `fabric/plan/etl/` directory:

```
python 01_build_star_schema.py
python 02_enrich_departments.py
python 03_reshape_amounts.py
python 04_add_headcount.py
python verify_data.py          # optional — confirms everything looks right
```

Source data: `working/budget-vs-actual-data.csv` (original Kaggle export, kept as backup). Cleaned intermediate: `working/demo-actuals.csv`. Final output: `dataset/`.
