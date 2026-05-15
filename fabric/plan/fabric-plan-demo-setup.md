# Fabric Plan Demo — Setup & Reset Instructions

## Prerequisites

- A Fabric capacity (F SKU or trial). Pro-only workspaces won't work.
- Your account has Admin or Member role on the workspace.
- Plan (preview) is enabled in your tenant admin settings.
- Your capacity region [supports Plan](https://learn.microsoft.com/fabric/iq/plan/overview-regions).

---

## Part 1 — Data Engineering Setup

This is the data team's work. Do this once. The finance user never sees any of it.

### 1. Load the dataset into Fabric

Upload the five CSVs from `fabric/plan/dataset/` into a Fabric lakehouse or SQL database:

- `dim_department.csv`
- `dim_category.csv`
- `dim_month.csv`
- `fact_actuals.csv`
- `fact_headcount.csv`

**Lakehouse path:** Workspace → Lakehouse → Upload files → load into tables.

### 2. Build the semantic model

Create a semantic model on top of the loaded tables:

- **Relationships:**
  - `fact_actuals.DepartmentKey` → `dim_department.DepartmentKey`
  - `fact_actuals.CategoryKey` → `dim_category.CategoryKey`
  - `fact_actuals.MonthKey` → `dim_month.MonthKey`
  - `fact_headcount.DepartmentKey` → `dim_department.DepartmentKey`
  - `fact_headcount.MonthKey` → `dim_month.MonthKey`
- **Hierarchies:**
  - Department hierarchy: `Division` → `Department` (in dim_department)
  - Time hierarchy: `Year` → `Quarter` → `Month` (in dim_month)
- **Measures:**
  - `Total Actuals = SUM(fact_actuals[ActualAmount])`
  - `Total Headcount = SUM(fact_headcount[Headcount])`
- **Publish** the semantic model to the workspace.

---

## Part 2 — Plan Setup

This is what the finance user would do (or what you do to prep the demo environment). Depends on Part 1 being complete.

### 3. Create the cloud connection

1. Settings → Manage connections and gateways → New → Cloud
2. Connection type: **Power BI Semantic Model**
3. Authentication: **OAuth 2.0** → sign in
4. Create

If your semantic model uses **Direct Lake** mode (the default when created from a lakehouse), you also need to bind this connection to the semantic model:

1. Go to the semantic model in your workspace → **… > Settings > Gateway & Cloud Connections**
2. By default the connection is set to Single Sign On. Select the cloud connection you just created from the dropdown.
3. Select **Apply**

> **Note:** If you skip binding the connection to the Direct Lake semantic model, Plan will show "Connection failed. Please check your dataset access" when you try to connect the Planning sheet.

See: [Create a cloud connection](https://learn.microsoft.com/fabric/iq/plan/planning-how-to-create-semantic-model-connection)

### 4. Create the Plan item

1. Workspace → New item → **Plan (preview)**
2. Name it "Finance Plan Demo"
3. A SQL database is auto-created in the workspace for Plan metadata

### 5. Create the Budget Planning sheet

1. Inside the Plan item → Planning → name it "Budget" → Create
2. Add → Connect → select your cloud connection → select the semantic model
3. Configure the fields:
   - **Rows:** Department (use the Division → Department hierarchy)
   - **Columns:** Month (use the Year → Quarter → Month hierarchy)
   - **Values:** Total Actuals
4. Verify you see departments down the left, months across the top, actuals populating

### 6. Configure writeback

1. Writeback tab → Add Destination
2. Select the auto-created SQL database connection
3. Table name: `budget_writeback`
4. Writeback type: **Wide** (easier to read in demos)
5. Save

See: [Persist planning data using writeback](https://learn.microsoft.com/fabric/iq/plan/planning-how-to-write-back-data)

### 7. Create the Intelligence sheet (BvA report)

1. Inside the Plan item → Intelligence → name it "BvA Report" → Create
2. Add a Planning visual → import data from the Budget Planning sheet
3. Add charts:
   - Bar chart: Department × Actuals, with Division hierarchy for drill-down
   - Waterfall or variance chart: Year-over-year comparison
   - Time series: Monthly actuals with seasonality visible
4. Format with IBCS styling if available
5. This sheet is pre-built — you just open it during the demo

### 8. Create the Headcount Planning sheet (optional, for Scene 5)

1. Inside the Plan item → Planning → name it "Headcount" → Create
2. Connect to the same semantic model
3. Rows: Department, Columns: Month, Values: Total Headcount

---

## Before Each Demo

Do this 15–30 minutes before you present.

### Quick reset checklist

| Step | What to do | Why |
|---|---|---|
| 1 | Open the Budget Planning sheet. Delete any data input rows, formula rows, or template rows you added in previous demos. | Clears the "build a budget" scene so you can do it live. |
| 2 | Delete any snapshots from previous demos (or rename them so they don't confuse the narrative). | Clears the "what-if + snapshots" scene. |
| 3 | Delete any what-if simulations still applied. | Returns the sheet to actuals-only baseline. |
| 4 | Check the Intelligence sheet. Remove any annotations/comments you added previously. | Clears the "annotate a variance" scene. |
| 5 | If you wrote back in a previous demo, check the `budget_writeback` table in the SQL database. Either drop/truncate it or create a fresh table name in writeback settings. | Prevents stale data from a prior run showing up. |
| 6 | Open each sheet and verify data loads correctly. | Catches refresh issues before you're live. |
| 7 | Close all other browser tabs. Open the Plan item to the Budget sheet. | Clean starting point. |

### If you need a full rebuild

If the Plan item is too messy to clean up:

1. Delete the Plan item from the workspace.
2. Delete the auto-created SQL database (it was created when the Plan item was first made).
3. Redo Part 2 (steps 3–8). Part 1 stays intact.

The semantic model and dataset don't need to change — only the cloud connection, Plan item, and its sheets get recreated.

---

## Troubleshooting

| Problem | Fix |
|---|---|
| "Connection failed. Please check your dataset access" | If using a Direct Lake semantic model, create the cloud connection first (Manage connections and gateways), then bind it to the semantic model via its Settings → Gateway & Cloud Connections page (step 3 above). Also verify you have Build permission on the semantic model and that the semantic model owner has read access to the underlying lakehouse tables. |
| "No data" in Planning sheet after connecting | Check that the semantic model is published and you have Build permission on it. Refresh the connection. |
| Writeback fails | Verify the SQL database connection is still valid. Check that the table name doesn't conflict with an existing table. |
| Hierarchy not showing in Planning sheet | Confirm the hierarchy is defined in the semantic model (Division → Department, Year → Quarter → Month), not just as flat columns. Republish the model. |
| Plan item won't create | Confirm Plan is enabled in tenant admin settings, workspace is on a capacity (not Pro-only), and the capacity region supports Plan. |
| Intelligence sheet charts are empty | Make sure the Planning visual is pointing to the right Planning sheet and the measures are mapped in the Data pane under "From Sheets." |
| Actuals look wrong or flat | Rerun the ETL pipeline (`fabric/plan/etl/`) and re-upload the dataset CSVs. The pipeline is deterministic — same output every time. |
