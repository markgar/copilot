# Fabric Plan — Seller Knowledge Guide

This guide is for Microsoft Fabric sellers. It gives you enough finance planning vocabulary and Fabric Plan product knowledge to have credible conversations with two audiences at a customer organization:

- **Finance people** — FP&A analysts, budget owners, controllers, CFO office. They do the planning. They care about budgets, forecasts, variance analysis, and approval workflows.
- **Finance analytics / data people** — BI developers, data engineers, analytics leads. They build and maintain the data platform. They care about pipelines, semantic models, and data governance.

You don't need to do either job. You need to speak to both sides and explain how Fabric Plan connects their worlds.

---

## The Goal of Finance Planning

Every organization needs to answer three questions about money:

1. **Where did the money go?** (Actuals — what already happened)
2. **Where do we expect it to go?** (Forecast — our best current prediction)
3. **Where should it go?** (Budget — the approved plan)

The entire finance planning process is a continuous loop of setting targets (budgets), updating predictions (forecasts), comparing both against reality (actuals), understanding why the numbers differ (variance analysis), and adjusting. The output of this process drives decisions like hiring, investment, cost cuts, and pricing — basically every major business decision that involves money.

The people who own this process sit in **FP&A (Financial Planning & Analysis)** and report to the CFO. The people who supply the data and build the analytical platform typically sit in IT, a BI/analytics team, or a Center of Excellence.

---

## Core Finance Concepts

### Budget, Forecast, and Actuals

- **Budget** — the approved spending and revenue plan for a period (typically annual). Set once, rarely changed. It's the commitment to leadership/the board.
- **Forecast** — an updated prediction of where things will actually land. Revised monthly or quarterly. More realistic than the budget.
- **Actuals** — what actually happened. Comes from the ERP / GL (General Ledger) system.

These three are constantly compared. The most common report in finance is **Budget vs. Actual (BvA)**.

### Variance Analysis

A **variance** is the gap between any two numbers (budget vs. actual, forecast vs. actual, this year vs. last year). Finance teams don't just want to see the delta — they want to understand **why** it happened. That's variance analysis.

- **Favorable** — spent less or earned more than planned
- **Unfavorable** — the opposite

### Dimensions

Finance slices everything by **dimensions** — if the customer's analytics team already uses semantic models, this is the same concept:

- **Account** (the chart of accounts: revenue, salary, travel, etc.)
- **Cost Center / Department**
- **Entity** (subsidiary, business unit)
- **Time** (month, quarter, year — often fiscal, not calendar)
- **Product / Project / Region**

When talking to finance people, use the word "dimensions." When talking to analytics people, you can say "these map directly to dimension tables in their semantic model or warehouse."

### Planning Approaches

- **Top-down** — leadership sets a target ("grow 10%"), departments figure out how
- **Bottom-up** — departments build their own plans, they roll up into a total
- **Driver-based** — model key inputs (e.g., headcount × avg salary = payroll), formulas do the rest
- **Rolling forecast** — always look 12–18 months ahead instead of a fixed annual window
- **Scenario / What-if** — model multiple versions of the future ("what if revenue drops 15%?")

---

## Fabric Plan — Feature Map

Fabric Plan (preview) is an EPM/CPM solution built directly into [[microsoft-fabric]], under the **[[fabric-iq]]** umbrella — Microsoft's decision intelligence layer that also includes ontology (semantic definitions across the platform) and AI-readiness capabilities. Plan lets organizations do budgeting, forecasting, and scenario modeling inside the same governed platform used for data, analytics, and AI.

> **Preview status.** Plan is in public preview. That means: no SLA, best-effort support, not intended for production workloads, and not available in all regions. Meters exist but are **not currently billed**. Position it as ready for POC, pilot, or parallel-run — not as a replacement for a production EPM tool today. See [region availability](https://learn.microsoft.com/fabric/iq/plan/overview-regions).
>
> **Cost.** Plan is included in the Fabric SKU — no separate license. The customer needs a Fabric capacity (F SKU or trial). Pro-only workspaces do not support Plan. During preview there is no charge for Plan usage, but meters are being tracked so the billing model is visible.

### Components

| Component | What it does |
|---|---|
| **Planning sheets** | Excel-like grid for budgeting, forecasting, scenario modeling. Supports formulas, input rows, hierarchy roll-ups, what-if simulations, rolling forecasts, snapshots. |
| **PowerTable sheets** | No-code **reference data management and productivity app platform**. Build collaborative table apps directly on database tables or semantic models with live sync back to the source. Use cases: master data management, project planning (Gantt charts, resource allocation, timesheets), task management, structured data entry, operational workflows. Includes approval workflows, automated triggers/webhooks, row- and column-level security, full audit logs, and Type II SCD support. Think of it as Plan's extension **beyond finance into operational planning**. |
| **Intelligence sheets** | Reporting and analysis layer — goes well beyond basic charts. IBCS-standard formatting, 100+ chart types (including specialized charts Power BI doesn't have natively: marimekko, sankey, network graphs, radar/polar, lollipop, multi-axis). Paginated reporting with first/previous/next/last navigation, pixel-perfect export to PDF/Excel/PNG, cell-level and data-point annotations, threaded comments, and custom header/footer with logo upload. Actuals vs. plan comparison, variance analysis, reusable measures, and presentation-ready layouts. |
| **InfoBridge** | No-code data integration engine. Connects multiple sources, consolidates into a single writeback table. Merge, append, pivot, group transforms. |

### Feature-to-Need Mapping

| They say... | They mean... | Fabric Plan feature |
|---|---|---|
| "Build next year's budget" | Enter targets by dept/account/month, roll up | **Planning sheets** — grid, formulas, hierarchy roll-ups |
| "Update our forecast" | Revise projections with recent actuals | **Planning sheets** — rolling forecast, copy actuals forward, averages |
| "What if revenue drops 15%?" | Scenario modeling | **Planning sheets** — what-if simulations, version management, snapshots |
| "We model off drivers like headcount" | Formulas calculate from key inputs | **Planning sheets** — formula rows (Excel-style), calculated columns, template rows |
| "Budget vs. actual reports" | Compare plan to reality with variance | **Intelligence sheets** — actuals vs. plan, variance analysis, charts |
| "Data comes from 5 different places" | Combine sources into one view | **InfoBridge** — no-code integration, merge/append/pivot, single writeback table |
| "Write this back to the database" | Persist planning results somewhere queryable | **Writeback** — Plan writes to a SQL database in Fabric automatically |
| "Need approval before numbers are final" | Governance over changes | **Approval workflows** — define flows, assign approvers, lock data |
| "CEO needs a summary dashboard" | Executive-ready output | **Intelligence sheets** — IBCS-formatted charts, 100+ chart types, paginated reports, pixel-perfect PDF/Excel/PNG export |
| "Tired of emailing spreadsheets" | Collaboration and version control | **Comments, @mentions, notifications** + central Fabric governance |
| "We need to manage our chart of accounts" | Master data governance | **PowerTable sheets** — table apps on database tables with live sync, audit logs, approval workflows |
| "Track project timelines and resources" | Operational planning | **PowerTable sheets** — Gantt charts, resource allocation, timesheets, task management, webhooks |

---

## Connecting to Actuals — What to Tell the Customer

This is the section that bridges the two audiences. The finance people want to know "how do my actuals show up?" The analytics people want to know "what do I need to build?"

The key message: **Plan doesn't prescribe a specific data schema.** There's no "Plan-compatible model" the customer has to conform to. Plan connects to a data source, and the finance user configures the planning model inside Plan using the **Model editor** — selecting which dimensions to include, defining hierarchies, mapping measures, and setting up the Cube (the multidimensional structure that stores planning data).

### Data Source Options (What to Present to the Customer)

| Source | What it is | Best for | Tradeoff |
|---|---|---|---|
| **[[power-bi]] semantic model** | Connect via a cloud connection to an existing semantic model | Customers already using Power BI for financial reporting — they likely have a model already | Richest starting point (hierarchies, measures, relationships pre-built). Recommended path for production. |
| **Fabric SQL database** | Connect directly to a SQL database in Fabric | Customers with a Fabric warehouse who don't want an extra layer | Finance has to define more structure themselves in the Model editor |
| **Excel / CSV upload** | Import data from files | Quick demos, POCs, or small teams just getting started | No live connection, manual refresh, doesn't scale |
| **Manual entry** | Type data directly into Planning sheets or PowerTable sheets | Standalone planning exercises or when no source data exists yet | Only practical for small models |
| **InfoBridge** | Pull and consolidate from multiple sources, including other Planning sheets | Customers whose data is spread across multiple reports or systems | Adds configuration, but avoids needing a single consolidated model upfront |

### How to Explain the End-to-End Flow

When talking to the **analytics / data team**:

1. **They get actuals into Fabric** — via [[data-factory]] pipelines, connectors, or whatever ingestion method fits the source system (SAP, Oracle, [[microsoft-dynamics]], etc.). The data lands in a lakehouse, warehouse, or SQL database.
2. **A semantic model exists (or they build one)** — with dimensions (accounts, cost centers, time, etc.) and measures (revenue, expenses, balances). If the org already does Power BI reporting on financials, this likely exists already.
3. **They create a cloud connection** — pointing to the semantic model or SQL database. One-time setup (Settings → Manage connections and gateways → New → Cloud).

When talking to the **finance team**:

4. **They connect Plan to the data** — inside a Planning sheet, select "Add → Connect," pick the connection, choose the semantic model or database, and drag fields into rows/columns/values.
5. **They configure the planning model** — using the Model editor, they select which dimensions participate, define hierarchies for roll-ups, and map measures. This is their metadata layer — they own it.

### What the Customer Needs to Get Right

These are the points to raise during a solution conversation:

- **The data pipeline must be reliable** — actuals need to arrive on time (usually a few days after month-end close) and be accurate. If SAP says $1.2M in revenue, Fabric better say the same. This is the analytics team's responsibility.
- **Dimensions need to match what finance expects** — if finance needs a 4-level cost center hierarchy, it has to be in the model. If they need to plan by product and region, those dimensions need to exist. This is the main collaboration point between the customer's two teams.
- **No special schema required** — Plan reads whatever dimensions and measures are in the semantic model or database. It doesn't auto-detect "actuals" — the finance user decides which measure represents actuals when they configure their Planning sheet.- **A SQL database is auto-created per workspace** — when someone creates a Plan item in a workspace, Fabric automatically provisions a SQL database for that workspace to store Plan metadata. This reduces setup friction — the analytics team doesn’t need to pre-create a database just to get started.
### Typical Architecture (e.g., SAP Customer)

```
SAP (GL, CO, FI)                           ← Customer's source system
    ↓  Data Factory pipeline / connector    ← Analytics team builds this
Fabric Lakehouse or Warehouse               ← Analytics team manages this
    ↓
Semantic Model (dimensions + measures)      ← Analytics team builds/maintains
    ↓
Fabric Plan                                 ← Finance team owns this
    ├── Planning sheets (budget/forecast)
    ├── Intelligence sheets (variance reports)
    └── InfoBridge (consolidation)
    ↓  writeback
Fabric SQL Database (planning outputs)      ← Available to both teams
```

### Typical Architecture (e.g., Snowflake Customer)

If the customer's data platform is [[snowflake]] rather than Fabric-native, use [[fabric-mirroring]] to bring the data in without rebuilding their pipelines:

```
ERP (SAP, Oracle, etc.)                     ← Customer's source system
    ↓  existing ETL (Informatica, dbt, etc.)
Snowflake                                   ← Customer's existing data platform
    ↓  Fabric Mirroring (Snowflake)         ← Near real-time replication to OneLake
Mirrored Database in Fabric                 ← Read-only Delta tables, auto-synced
    ↓
Semantic Model (dimensions + measures)      ← Analytics team builds on mirrored data
    ↓
Fabric Plan                                 ← Finance team owns this
    ├── Planning sheets (budget/forecast)
    ├── Intelligence sheets (variance reports)
    └── InfoBridge (consolidation)
    ↓  writeback
Fabric SQL Database (planning outputs)      ← Available to both teams
```

**Key differences from the Fabric-native path**:

- **No new ingestion pipeline needed** — the customer keeps their existing ERP → Snowflake flow. Mirroring handles the Snowflake → Fabric leg automatically.
- **Mirrored data is read-only** — Fabric gets a continuously synced copy in Delta Parquet format. The source of truth stays in Snowflake.
- **The semantic model sits on top of mirrored tables** — the analytics team builds it in Fabric the same way they would on a lakehouse or warehouse. Plan doesn't know or care that the data originated in Snowflake.
- **Writeback still goes to Fabric SQL Database** — planning outputs stay in Fabric. If the customer needs those results back in Snowflake, that's a separate reverse-sync (Data Factory, dbt, etc.).

This pattern works for any mirroring-supported source (Snowflake, Azure SQL, Cosmos DB, etc.) — the architecture is the same, just swap the source system.

### Closing the Loop: Getting Plan Data Back into the Cube

In both architectures above, there's a gap that isn't obvious: Plan *reads* from the semantic model (to get actuals and dimensions), but *writes* to a Fabric SQL Database. The writeback table is a separate SQL table — it doesn't automatically appear in the existing semantic model.

To get budget/forecast data into the same cube as actuals, the analytics team has to close the loop:

1. **Plan writes back** — finance completes their budget/forecast in Planning sheets and triggers a writeback. The data lands in a Fabric SQL Database table with the dimensions and measures they configured.

   **Writeback format options** — Plan supports four writeback table structures. The analytics team will care about this when they wire the data into the semantic model:

   | Format | Description |
   |---|---|
   | **Long** | Measures stored as key-value pairs (row-based). One row per dimension-member × measure. |
   | **Wide** | Measures stored as columns. One row per dimension-member combination. |
   | **Long with Changes** | Same as Long, but only changed values are written — tracks deltas. |
   | **Wide with Changes** | Same as Wide, but only changed values are written. |

   The "with Changes" variants are useful when the downstream process needs to know what finance modified rather than getting a full snapshot each time.

2. **Analytics team adds the writeback table to the semantic model** — they add the Fabric SQL Database as a source in the existing semantic model and create relationships between the writeback table's dimension keys and the existing dimension tables.
3. **Now the model has both** — actuals come from the original source (lakehouse, warehouse, mirrored database), and plans come from the writeback table. Measures like `Budget vs. Actual` can be built in a single model.

```
Semantic Model
    ├── Actuals (from lakehouse / warehouse / mirrored DB)
    ├── Budget & Forecast (from Plan writeback SQL table)
    └── Shared dimensions (Account, Cost Center, Time, etc.)
```

This is a one-time setup by the analytics team — once the writeback table is wired into the model, subsequent writebacks from finance flow through automatically.

**Alternative: Composite model** — if the analytics team doesn't want to modify the original semantic model, they can create a [[composite-model]] that layers the writeback table on top of the existing model via DirectQuery. This keeps the base model untouched.

---

## Security and Governance

Plan inherits Fabric's governance model. When the customer asks about security:

- **Workspace roles** — Plan items live in Fabric workspaces. Access is controlled by standard workspace roles (Admin, Member, Contributor, Viewer).
- **Semantic model permissions** — Admin or Build permission required on the source semantic model. The connection creator can share the connection with other workspace users.
- **Row-level security** — PowerTable sheets support row-level and column-level security natively. For Planning sheets, RLS on the underlying semantic model flows through.
- **Approval workflows** — built into Planning sheets and PowerTable sheets. Define flows, assign approvers, lock data after approval.
- **Audit and change tracking** — PowerTable sheets include full change history and audit logs with Type II SCD support. Planning sheet writeback can use the "with Changes" format to track deltas.
- **Fabric admin controls** — Plan is enabled/disabled at the tenant level by the Fabric admin, same as other preview features.

---

## Known Limitations (Preview)

Surface these early in a solution conversation. Getting surprised by a limitation after a customer commits is worse than flagging it upfront.

| Limitation | Impact |
|---|---|
| **Preview — no production SLA** | Customer can pilot and parallel-run, but shouldn’t rip-and-replace their current EPM tool yet. |
| **Region restrictions** | Plan is not available in all Fabric regions. Check the [region list](https://learn.microsoft.com/fabric/iq/plan/overview-regions) against the customer’s capacity region before demoing. |
| **Private link not supported** | Plan items won’t work in workspaces or tenants that use private links. If the customer has strict network isolation requirements, this is a blocker. |
| **Semantic model permissions** | User must have **Admin** or **Build** permission on the semantic model. Read-only access is not enough. |
| **Direct Lake semantic models** | Require [additional configuration](https://learn.microsoft.com/fabric/iq/plan/planning-how-to-create-semantic-model-connection#connect-to-a-direct-lake-semantic-model) to work with Plan. |
| **"My workspace" not supported** | Semantic models in the user’s personal workspace can’t be used as a Plan source. Must be in a shared workspace. |
| **Pro-only workspaces** | Capacity workspaces with only Pro licenses are not supported. Requires premium capacity (F SKU or trial). |
| **Browser compatibility** | Older browsers supporting only HTTP/1.1 may cause errors. Modern browser with HTTP/2 required. |

Source: [Known issues and limitations in plan (preview)](https://learn.microsoft.com/fabric/iq/plan/overview-known-issues)

---

## Product Gaps — What Customers Will Ask About

The limitations table above covers documented bugs and constraints. This section covers the bigger gaps — capabilities customers expect from a mature EPM tool that Fabric Plan **does not have yet** (as of April 2026 preview). Know these before you walk into a meeting. Every competitor will bring them up.

### No Copilot / AI Integration

Plan's marketing says "AI-ready foundation." Customers will ask "so where's the AI?" The answer today: **nowhere inside Plan itself.** There is no Copilot integration for generating forecasts, explaining variances, suggesting allocations, or natural-language querying of planning data. The "AI-ready" story is about data unification (actuals + plans in one governed platform), which *enables* future AI — but delivers none today. Competitors like Anaplan and Workday Adaptive already have AI-assisted forecasting features in production.

**What to say:** "Plan puts your planning data on the same platform as your analytics and AI workloads — that's the prerequisite. Copilot integration for Plan is on Microsoft's roadmap, but it's not in the preview today."

### No Multi-Currency Support

Multinational customers will ask this in the first five minutes. Plan has **no built-in currency conversion**. There is no exchange rate table, no translation logic, no multi-currency consolidation. If a customer plans in USD in the US and EUR in Europe, they need to handle currency translation themselves — either in the semantic model (DAX), in the data pipeline, or with manual formula rows in Planning sheets.

Every major EPM competitor (Anaplan, Adaptive, Oracle EPM, SAP BPC) has native multi-currency built in.

**What to say:** "Currency conversion is handled in the data layer — either in the semantic model or the pipeline. Plan gives you the formulas and dimensions to model it, but there's no built-in currency engine like you'd find in dedicated EPM tools. For a pilot, we'd build a simple FX rate dimension and conversion formula."

### No Intercompany Eliminations

Large enterprises with multiple legal entities need to eliminate intercompany transactions when they consolidate. Plan has **no elimination engine**. There are no matching rules, no auto-generated elimination entries, no intercompany reconciliation views. A customer doing statutory consolidation will need this handled outside Plan — either in the ERP, in a separate consolidation tool, or with manual adjustments.

**What to say:** "Intercompany eliminations are typically handled in the ERP or close process today. Plan can *report* on the consolidated result, but it doesn't automate the elimination entries themselves."

### No Allocation Engine

Top-down allocation — distributing a corporate cost pool across business units using drivers (headcount, revenue, square footage) — is a core EPM function. Plan has formulas and calculated columns, so you can *build* simple allocations manually using formula rows. But there is **no dedicated allocation engine** with rule definitions, multi-step cascading allocations, or step-allocation tracing. Competitors like Anaplan and Oracle Hyperion have purpose-built allocation modules.

**What to say:** "Plan supports driver-based formulas, so simple allocations work. For complex multi-step allocations, like a shared services cascade, most customers keep those in their ERP or build them in the data pipeline. This is a gap versus dedicated EPM tools."

### No Workforce / Headcount Planning Module

Workforce planning (headcount, compensation modeling, new hire timelines, attrition modeling) is a top-3 use case for EPM tools. Plan has no dedicated workforce module — no employee-level planning, no position management, no salary/benefit modeling templates. You *could* build a basic headcount model using Planning sheets with a headcount dimension and salary formulas, but it would be entirely manual.

Adaptive Planning and Anaplan both have purpose-built workforce planning modules.

**What to say:** "You can model headcount and compensation with planning sheets and driver-based formulas. It's flexible. But there's no pre-built workforce module with position management like you'd find in Adaptive. For the pilot, we'd build a lightweight headcount model to show the pattern."

### No REST API or Programmatic Access

There is **no public API for Plan** — no REST endpoints to create planning models, trigger writebacks, read/write planning data, or automate any part of the planning workflow. Everything is manual/interactive through the browser UI. This means:

- No CI/CD or deployment pipelines for planning models
- No scheduled or event-triggered writebacks (writeback is manual, user-initiated)
- No integration with Power Automate, Logic Apps, or Azure Functions
- No Git integration for version control of planning model definitions

For enterprise customers who automate their close-to-plan cycle, this is a blocker. Competitors have APIs (Anaplan has a full REST API; Adaptive has an API and Office Connect).

**What to say:** "Plan is preview — API and automation support is expected as part of the GA roadmap, but it's not available today. For the pilot, all writeback and model configuration is done through the UI."

### No Offline / Excel Add-in

Many finance teams enter budgets in Excel and upload them. Plan has **no Excel add-in** and no offline editing capability. Planning sheets are Excel-*like* in the browser, but there's no way to work offline and sync later, and no way to use actual Excel as a front-end connected to Plan's data model.

This matters because budget season often means finance managers filling in templates on planes, at home, or in locations with poor connectivity. Anaplan has an Excel add-in; Adaptive has Office Connect; Oracle has Smart View.

**What to say:** "Plan's interface is browser-based and feels like Excel, but there's no offline mode or Excel add-in today. Budget entry requires a browser and connectivity."

### No Mobile Experience

No dedicated mobile app or mobile-optimized view for Plan. Finance leaders who want to review or approve budgets on their phone can't do it through Plan. Approval workflows exist but are browser-only.

**What to say:** "Approval workflows and reviews are browser-based today. Mobile access would come through the Fabric mobile experience, but Plan doesn't have a dedicated mobile view yet."

### No Pre-Built Planning Templates or Accelerators

Competitors ship with industry templates — P&L templates, balance sheet planning, cash flow planning, SaaS metrics, retail demand planning. Plan ships with **a blank canvas.** Every planning model is built from scratch. This increases time-to-value and consulting effort for implementation.

**What to say:** "Plan is flexible — you model what you need. But unlike some competitors, there aren't pre-built P&L or cash flow templates out of the box. Expect to build the model as part of the pilot."

### No Scheduled Writeback or Event-Driven Triggers

Writeback is **manual and user-initiated only.** There's no way to schedule a writeback (e.g., "every Monday at 6am, write the latest forecast to the SQL table") or trigger one from an event (e.g., "when the approval workflow completes, auto-writeback"). Combined with the lack of APIs, this means the close-to-plan automation story is weak.

**What to say:** "Writeback is on-demand today — a user clicks the button. There's no scheduling or automation. For the pilot that's fine, but for production at scale, the customer should know this is a gap."

### No Git Integration or Deployment Pipelines

Fabric supports Git integration and deployment pipelines for many item types (notebooks, semantic models, reports). **Plan items are not currently supported** in Git integration or Fabric deployment pipelines. This means no version control for planning model definitions, no dev/test/prod promotion, and no change tracking beyond what's in the UI.

**What to say:** "Plan models live in the workspace and are managed through the UI. Dev/test/prod promotion and Git-based version control aren't available for Plan items yet — that's expected to come as the product matures."

### Summary: Gap Heat Map

Use this to quickly assess deal risk based on what the customer needs:

| Gap | Risk level | Who asks | Workaround available? |
|---|---|---|---|
| No Copilot / AI | Medium | Everyone (exec sponsors especially) | Position as future; data unification story is real |
| No multi-currency | **High** | Any multinational | Build FX rate logic in semantic model or pipeline |
| No intercompany eliminations | **High** | Large enterprises, audit/compliance | Handle in ERP or consolidation tool |
| No allocation engine | Medium | Shared services orgs, corporate finance | Manual formula rows for simple cases |
| No workforce planning module | Medium | HR-adjacent FP&A teams | Build lightweight model manually |
| No API / automation | **High** | IT teams, enterprise architects | None — everything is manual |
| No Excel add-in / offline | Medium | Traditional finance teams | Browser-only; CSV upload for bulk entry |
| No mobile experience | Low | Execs, approvers on the go | Use browser on mobile (not optimized) |
| No pre-built templates | Medium | Customers expecting fast time-to-value | Build from scratch; increases pilot effort |
| No scheduled writeback | Medium | Analytics/data teams automating pipelines | Manual writeback only |
| No Git / deployment pipelines | Medium | DevOps-oriented analytics teams | Manual workspace management |

---

## Key Talking Points

Use these when positioning Fabric Plan in a customer conversation:

1. **Plan lives inside Fabric** — no separate tool to buy, license, or integrate. Planning data sits alongside the warehouse, lakehouse, and reports. Same governance, same security, same semantic models. For the analytics team, this means no new platform to manage. For finance, it means no data exports or reconciliation.

2. **Actuals and plans can share one semantic model** — the #1 pain in finance is reconciling numbers across systems. Because Plan writes back to a Fabric SQL Database, the analytics team can wire that table into the same semantic model that holds actuals. Budget, forecast, and actuals then use the same dimensions and definitions — no export, no reconciliation. (See *Closing the Loop* above for how this is set up.) This resonates strongly with finance people who have been burned by "the numbers don't match" conversations.

3. **Finance users do it themselves** — it's no-code, Excel-like. Finance teams don't need to file tickets with IT to build their budgets. The analytics team sets up the data connections and semantic model; finance owns the planning from there. This resonates with both sides — finance gets independence, analytics gets fewer ad hoc requests.

4. **It writes back to SQL in Fabric** — planning outputs land in a SQL database that the analytics team can query, pipeline, or report on like any other Fabric data. This is a key point for the analytics audience — they don't lose visibility into what finance produces.

5. **InfoBridge replaces their ETL for planning data** — when finance needs to pull data from multiple reports or sources into one consolidated view, InfoBridge does it without code. Think of it as lightweight Power Query scoped to planning. For the analytics team, this means fewer "can you build me a pipeline" requests.

6. **Replaces expensive standalone EPM tools** — customers today may be paying for [[anaplan]], [[workday-adaptive-planning]], Oracle EPM, SAP BPC/SAC, Planful, or Vena. Fabric Plan is included in the Fabric SKU. That’s a consolidation and cost story. During preview, position this as a future-state migration path — customers can pilot Plan alongside their existing tool and plan a cutover when GA lands.

7. **AI-ready foundation** — Microsoft positions Plan as creating an “AI-ready foundation for smarter decisions.” By putting planning data in the same governed platform as analytics, historical data, and real-time signals, Plan makes it easier to layer on Copilot and AI capabilities as they mature. Plan doesn’t have its own Copilot integration yet, but the data unification story is the prerequisite. When talking to forward-looking customers, this is the “why now” even during preview.

8. **It’s preview — be upfront** — don’t hide this. Customers respect honesty more than discovering preview status after they’ve committed. Position it as: “ready for pilot, not for rip-and-replace today, and you get to shape the product through preview feedback.”

---

## Competitive Context

You will hit one of these in almost every deal. Plan’s preview status is a disadvantage against established tools, but the Fabric integration story is a genuine differentiator.

| Competitor | What they do well | Fabric Plan differentiator |
|---|---|---|
| **Anaplan** | Powerful modeling engine, large enterprise adoption | Plan is native to the Fabric data platform — no ETL between planning and analytics. No separate license cost. |
| **Workday Adaptive Planning** | Strong mid-market, easy onboarding | Same Fabric-native advantage. Customers on Power BI already have half the integration done. |
| **Oracle EPM (Hyperion/Cloud)** | Deep Oracle ERP integration | For non-Oracle shops (or Oracle shops moving to Azure), Plan avoids vendor lock-in. |
| **SAP BPC / SAC Planning** | Tight SAP ERP integration | For SAP customers already on Fabric (or evaluating it), Plan keeps everything in one platform instead of two. |
| **Planful / Vena** | Finance-team-friendly UX | Plan’s Excel-like interface competes here, plus the shared semantic model story is stronger. |
| **Excel** | Free, everyone knows it | Plan is Excel-like but adds governance, collaboration, writeback, approval workflows, and version control. |

---

## Who Does What at the Customer

| Analytics / data team | Finance / planning team |
|---|---|
| Set up and manage the Fabric workspace and capacity | Define the budget structure, accounts, and planning model |
| Build and maintain the semantic model | Enter and manage budget/forecast numbers |
| Build pipelines to bring actuals from ERP/GL into Fabric | Configure the Model editor (dimensions, hierarchies, cube) |
| Manage security, governance, refresh schedules | Run approval workflows and finalize plans |
| Create cloud connections to semantic models / databases | Build Intelligence sheet reports and dashboards for leadership |

The handoff point: the analytics team delivers reliable, well-structured data in Fabric. The finance team takes it from there inside Plan. Your job as the seller is to make sure both sides see how their piece fits.

---

## Discovery Questions

For the **finance audience**:

- "How are you handling your rolling forecast cadence today?"
- "Are you doing driver-based planning or mostly line-item entry?"
- "How long is your budget cycle, and where are the bottlenecks?"
- "How do you handle allocations and intercompany eliminations?"
- "What tool are you using for planning today — Anaplan, Adaptive, Excel?"
- "How much time does your team spend reconciling actuals vs. plan data?"

For the **analytics / data audience**:

- "Where do your actuals come from — what's the GL/ERP?"
- "Do you already have a semantic model over your financial data?"
- "How are you getting data from [SAP/Oracle/Dynamics] into Fabric today?"
- "Is the finance team filing requests with you to build reports or move data?"
- "What does your month-end close process look like from a data availability standpoint?"

---

## Reference

- [What is plan (preview)?](https://learn.microsoft.com/fabric/iq/plan/overview)
- [What is Fabric IQ (preview)?](https://learn.microsoft.com/fabric/iq/overview)
- [Planning sheets overview](https://learn.microsoft.com/fabric/iq/plan/planning-overview)
- [PowerTable sheets overview](https://learn.microsoft.com/fabric/iq/plan/powertable-overview)
- [Intelligence sheets overview](https://learn.microsoft.com/fabric/iq/plan/intelligence-overview)
- [InfoBridge overview](https://learn.microsoft.com/fabric/iq/plan/infobridge-overview)
- [Create a Planning sheet](https://learn.microsoft.com/fabric/iq/plan/planning-how-to-get-started)
- [Persist planning data using writeback](https://learn.microsoft.com/fabric/iq/plan/planning-how-to-write-back-data)
- [Write back transformed data from InfoBridge](https://learn.microsoft.com/fabric/iq/plan/infobridge-how-to-write-back-data)
- [Known issues and limitations](https://learn.microsoft.com/fabric/iq/plan/overview-known-issues)
- [Region availability for plan (preview)](https://learn.microsoft.com/fabric/iq/plan/overview-regions)
- [Forecast data to predict future trends](https://learn.microsoft.com/fabric/iq/plan/planning-how-to-build-forecasts)
- [Visualize simulations, budgets, and forecasts](https://learn.microsoft.com/fabric/iq/plan/intelligence-how-to-visualize-planning-data)
- [Connect PowerTable sheet to a semantic model](https://learn.microsoft.com/fabric/iq/plan/powertable-how-to-connect-semantic-model)
