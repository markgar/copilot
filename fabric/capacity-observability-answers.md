# Fabric Capacity Observability — Research Answers

These answers respond to the capacity observability questions raised by the Thomson Reuters team. Each section restates the question, then provides what Microsoft documentation says today.

---

## Question 1: CU Utilization — Historical Retention & API Access

**The question:** The Fabric Capacity Metrics App shows ~7 days of CU utilization data. Can CU usage be retrieved historically for a month or longer? Is this configurable or a backend limitation? Is there an API to access the same underlying telemetry?

### Answer

The Capacity Metrics App actually retains **14 days** of compute data (not 7). The Compute page provides "a 14-day view of your capacity's compute performance" including ribbon charts, utilization trends, and a matrix of operations. The Storage page retains 30 days. These are **fixed backend retention windows** — there is no configurable retention setting to extend them.

**There is no supported public API that exposes the same underlying CU telemetry** used by the Capacity Metrics App. Microsoft explicitly states: "The semantic model used by the Microsoft Fabric Capacity Metrics application is only supported for use by the reports provided in the application. Any consumption from, usage of, or modification of the semantic model isn't supported." You cannot programmatically query or export the Metrics App's semantic model.

**To get CU data beyond 14 days**, the supported approach is:

1. **Fabric Capacity Overview Events via Real-Time Hub.** These events emit a `Microsoft.Fabric.Capacity.Summary` event every 30 seconds with smoothed CU data at the capacity level. You can route these events into an **Eventhouse** (KQL database) for long-term storage and historical analysis. Microsoft's own documentation says these events "can be stored in an Eventhouse for granular or historical analysis." **This is a real-time, forward-looking system — it does not backfill historical data.** You must start collecting before you need the history.

2. **Power BI Activity Log** provides user activity events (up to **28 days** via the REST API / PowerShell cmdlet) but does **not** include CU consumption, CPU, memory, or throttling metrics. It covers actions like report views, dataset refreshes initiated, and so on — not capacity utilization.

3. **Unified Audit Log** (via Microsoft Purview or the Office 365 Management Activity API) provides up to **90 days** of user activity history, but again this is activity-level (who did what), not capacity telemetry.

**Bottom line:** To build a historical CU utilization store beyond 14 days, start streaming Capacity Overview Events to an Eventhouse now. There is no retroactive way to recover data older than what the Metrics App currently shows.

**References:**
- [What is the Microsoft Fabric Capacity Metrics app?](https://learn.microsoft.com/fabric/enterprise/metrics-app)
- [Understand the metrics app compute page](https://learn.microsoft.com/fabric/enterprise/metrics-app-compute-page)
- [Explore Fabric capacity overview events in Fabric Real-Time hub](https://learn.microsoft.com/fabric/real-time-hub/explore-fabric-capacity-overview-events)
- [Get Fabric capacity overview events in Real-Time hub](https://learn.microsoft.com/fabric/real-time-hub/create-streams-fabric-capacity-overview-events)
- [Access the Power BI activity log](https://learn.microsoft.com/power-bi/guidance/admin-activity-log)

---

## Question 2: Capacity Telemetry Granularity — Workspace/Item/User Level Gaps

**The question:** The Power BI Activity Log and Capacity REST APIs don't expose CU consumption, CPU, memory, or throttling indicators. The Capacity Overview Event Streaming in Real-Time Hub provides capacity-level telemetry only (CapacityName, CU usage, throttling percentages). It does not provide workspace-, report-, dataset-, or user-level detail needed for chargeback/showback and troubleshooting. What are the options?

### Answer

This is a correct assessment of the current state. Here is the granularity picture across each data source:

| Data Source | Granularity | CU / CPU Data? | User Attribution? | Retention |
|---|---|---|---|---|
| **Capacity Metrics App** | Item + operation level (within a capacity) | Yes — CU seconds per item, per operation | Yes — user counts, user names (if tenant setting enabled) | 14 days compute, 30 days storage |
| **Capacity Overview Events (Real-Time Hub)** | Capacity level only | Yes — smoothed CU milliseconds, throttling %, overage, utilization by workload category | No | As long as you store them (forward-looking only) |
| **Workspace Monitoring (Preview)** | Item + operation level (within a workspace) | Partial — DurationMs, CpuTimeMs for semantic model operations | Yes — ExecutingPrincipalId | 30 days in the monitoring Eventhouse |
| **Power BI Activity Log** | User action level | No — no CU/CPU/memory | Yes — user, workspace, item | 28 days via API |
| **Admin Monitoring Workspace** | Tenant-wide activity and adoption | No — activity counts, not CU | Yes | 30 days in reports |

**Key findings:**

1. **The Capacity Metrics App is the primary source of item-level CU attribution today.** The Compute page's matrix table shows CU seconds consumed per item, per operation, with user counts, over 14 days. The Timepoint pages let you drill into a specific 30-second window and see exactly which items and operations consumed CUs. This is the closest thing to chargeback data that exists.

2. **Capacity Overview Events provide a `capacityUnitUtilisationBreakdown` field** that breaks down CU consumption by workload type (e.g., Semantic Model, Warehouse, Spark, Eventstream, etc.) and by billable vs. non-billable, background vs. interactive. However, this is still at the **capacity level, not workspace or item level**. The possible workload values include: Semantic Model (AS), Warehouse (DMS), Spark (SparkCore), Eventstream (ES), Data Integration (DI), and many others.

3. **Workspace Monitoring (Preview)** is the newer mechanism for item-level detail. When enabled, it creates a read-only Eventhouse with KQL databases in the workspace. For **semantic models specifically**, it collects operation logs with columns like `CpuTimeMs`, `DurationMs`, `OperationName`, `ItemName`, `CapacityId`, user identifiers, and query text. This can partially fill the gap for semantic model chargeback. However, workspace monitoring is per-workspace, not cross-capacity.

4. **There is no single source today that provides workspace-level or item-level CU attribution in a programmatically accessible, long-retention format across all workloads.** The Metrics App is the closest, but it's capped at 14 days and its semantic model cannot be queried or exported programmatically (beyond Power BI's visual-level "Export Data" which is subject to sampling).

**Practical approach for chargeback/showback:**
- Use Capacity Overview Events streamed to an Eventhouse for capacity-level trending and budgeting (workload-level CU breakdown available).
- Use the Capacity Metrics App for the 14-day item-level CU attribution window.
- Enable Workspace Monitoring in critical workspaces for semantic model operation detail (30-day retention in the Eventhouse).
- Use the Power BI Activity Log for user-level activity attribution (who used what, when).

**References:**
- [Explore Fabric capacity overview events — Schema](https://learn.microsoft.com/fabric/real-time-hub/explore-fabric-capacity-overview-events#event-types)
- [What is workspace monitoring?](https://learn.microsoft.com/fabric/fundamentals/workspace-monitoring-overview)
- [Semantic model operations (workspace monitoring)](https://learn.microsoft.com/fabric/enterprise/powerbi/semantic-model-operations)
- [Understand the metrics app compute page](https://learn.microsoft.com/fabric/enterprise/metrics-app-compute-page)
- [Track user activities in Power BI](https://learn.microsoft.com/fabric/enterprise/powerbi/service-admin-auditing)

---

## Question 3: Admin-Level Analytics for Business Stakeholders

The business stakeholders asked several specific questions. Here are the answers for each:

### 3a. "How is the CPU load behaving at various times of the month?"

**Answer:** The Capacity Metrics App shows a **14-day** compute view with hourly granularity in the multi-metric ribbon chart. This lets you see CU utilization patterns (peaks during business hours, nightly processing, etc.) but **only within the 14-day window**. To see month-over-month trends, you must stream Capacity Overview Events to an Eventhouse and build your own time-series analysis. The `capacityUnitMs` field in the Summary events, emitted every 30 seconds, gives you the raw data to chart utilization over any historical period you've collected.

There is no additional admin analytics export beyond these two mechanisms.

**References:**
- [Understand the metrics app compute page](https://learn.microsoft.com/fabric/enterprise/metrics-app-compute-page)
- [Explore Fabric capacity overview events](https://learn.microsoft.com/fabric/real-time-hub/explore-fabric-capacity-overview-events)

---

### 3b. "Which semantic model is busiest, and at what times?" / "Are we hitting thresholds?"

**Answer:**

**Identifying the busiest semantic model:** The Capacity Metrics App's Compute page matrix table shows CU seconds, duration, operation count, and user count **per item** over 14 days. You can filter by item kind (select "Dataset" / semantic model) and sort by CU(s) descending to identify the busiest models. The Timepoint drill-through lets you see which items consumed the most CUs at specific 30-second intervals.

For deeper analysis, **Workspace Monitoring** (when enabled) collects semantic model operation logs with `CpuTimeMs`, `DurationMs`, and query text, which lets you identify the busiest models and their peak activity times using KQL queries.

**Thresholds and what "busy" means:** Microsoft defines throttling thresholds, not "busy" thresholds. The throttling policy is based on how much future capacity has been consumed:

| Condition | Threshold | Impact |
|---|---|---|
| Overage protection | Usage ≤ 10 minutes of future capacity | No throttling — operations proceed normally |
| Interactive Delay | 10 min < Usage ≤ 60 min of future capacity | Interactive operations delayed 20 seconds |
| Interactive Rejection | 60 min < Usage ≤ 24 hours of future capacity | Interactive operations rejected |
| Background Rejection | Usage > 24 hours of future capacity | All operations rejected |

The Capacity Metrics App's Compute page includes **Throttling** and **Overages** tabs that show when these thresholds were crossed. The `interactiveDelayThresholdPercentage`, `interactiveRejectionThresholdPercentage`, and `backgroundRejectionThresholdPercentage` fields in the Capacity Overview Events also track these in real time.

Microsoft does **not** publish "recommended CU usage limits" or guardrails in the sense of "stay below X%." The system is designed around bursting and smoothing — sustained overload triggers throttling, which is the enforcement mechanism. Admins should watch for **any** throttling events as the signal that capacity is insufficient.

Additionally, **Surge Protection** is a configurable feature that lets admins set per-capacity or per-workspace CU thresholds and automatically block workspaces that exceed them. These thresholds are customer-defined, not Microsoft-defined.

**References:**
- [The Fabric throttling policy](https://learn.microsoft.com/fabric/enterprise/throttling)
- [Troubleshooting guide: Monitor and identify capacity usage](https://learn.microsoft.com/fabric/enterprise/capacity-planning-troubleshoot-consumption)
- [Surge Protection](https://learn.microsoft.com/fabric/enterprise/surge-protection)
- [Semantic model operations](https://learn.microsoft.com/fabric/enterprise/powerbi/semantic-model-operations)

---

### 3c. "Where are we exceeding recommended limits?"

**Answer:** Microsoft does **not** publish specific recommended limits or guardrails for CU usage percentages, CPU saturation, or query wait times as explicit numbers customers should target. The Fabric capacity model relies on:

1. **Throttling as the enforcement mechanism.** The system tells you when you've exceeded limits by throttling operations (delays, then rejections). The Metrics App's System Events table and Throttling charts show this history.
2. **Surge Protection** (customer-configurable) to set your own per-workspace or per-capacity CU percentage limits.
3. **Performance delta** in the Metrics App, which shows whether item performance improved or worsened over the past week.

The implication: **customers are expected to define their own acceptable utilization thresholds** based on their tolerance for throttling and their business requirements. Microsoft's guidance is to monitor via the Metrics App and act when throttling occurs or trends upward.

**References:**
- [Evaluate and optimize your Microsoft Fabric capacity](https://learn.microsoft.com/fabric/enterprise/optimize-capacity)
- [The Fabric throttling policy](https://learn.microsoft.com/fabric/enterprise/throttling)
- [Metrics app calculations — Performance delta](https://learn.microsoft.com/fabric/enterprise/metrics-app-calculations#performance-delta)

---

### 3d. "Are users being dropped or waiting a long time for queries?"

**Answer:**

**What admins can observe:**
- **Throttling events** — The Metrics App's System Events table shows when the capacity entered states like `InteractiveDelay` (users waiting 20 seconds), `InteractiveRejected` (operations rejected), or `AllRejected`. These are the primary indicators that users were impacted.
- **Rejected operations** — The Metrics App drilldown shows operations that were rejected during throttling events, including the product, user, operation ID, and submission time.
- **CU % utilization** — The utilization chart shows when capacity was overloaded (columns exceeding the CU % Limit line).
- **Capacity Overview Events** — The `interactiveDelayThresholdPercentage` and `interactiveRejectionThresholdPercentage` fields give real-time signal on how close the capacity is to throttling.

**What cannot be observed by design:**
- **Individual user session-level query wait times** are not exposed. There is no telemetry that says "User X waited Y seconds for their report to load." The system reports throttling state at the capacity level, not per-user latency.
- **Memory usage per item or user** is not exposed in the Metrics App or the Capacity Overview Events. The CU model abstracts compute into a single unit; memory is not broken out separately.
- **In-flight operation performance degradation** — Operations that started before throttling are allowed to complete and are not tracked as "affected by throttling."

**References:**
- [Troubleshooting guide: Diagnose and resolve capacity limit exceeded errors](https://learn.microsoft.com/fabric/enterprise/capacity-planning-troubleshoot-errors)
- [Understand the metrics app compute page — System Events](https://learn.microsoft.com/fabric/enterprise/metrics-app-compute-page#system-events)
- [The Fabric throttling policy](https://learn.microsoft.com/fabric/enterprise/throttling)

---

### 3e. What out-of-the-box analytics does Microsoft recommend?

**Answer:** Microsoft positions the following as the recommended, supported monitoring stack:

| Tool | Purpose | Audience |
|---|---|---|
| **Fabric Capacity Metrics App** | Primary source of truth for capacity utilization, throttling, and item-level CU attribution | Capacity admins |
| **Capacity Overview Events (Real-Time Hub)** | Real-time capacity-level CU alerting and long-term historical storage (when streamed to Eventhouse) | Capacity admins |
| **Workspace Monitoring (Preview)** | Item-level operation logs for semantic models, pipelines, Eventhouses, etc. within a workspace | Workspace admins / contributors |
| **Admin Monitoring Workspace (Preview)** | Tenant-wide feature usage and adoption reporting (activity counts, sharing, users — not CU) | Fabric admins |
| **Fabric Monitoring Hub** | Real-time view of current and recent job execution status (success/fail/running) | All Fabric users (scoped by permissions) |
| **Power BI Activity Log** | User activity auditing (up to 28 days, programmatic access) | Fabric admins / governance teams |
| **Azure Log Analytics** | Premium workspace-level semantic model engine logs (alternative to Workspace Monitoring — cannot enable both simultaneously) | Premium workspace owners |

The **Capacity Metrics App is considered the primary source of truth** for capacity and performance monitoring. Microsoft's troubleshooting guides consistently direct admins to it first.

For the multi-capacity, chargeback-oriented analysis Thomson Reuters is describing, the practical architecture is:
1. Capacity Metrics App for the 14-day operational view across all capacities.
2. Capacity Overview Events → Eventhouse for long-term capacity-level trending.
3. Workspace Monitoring enabled in key workspaces for item-level operation detail.
4. Power BI Activity Log extracted daily for user activity and governance.

**References:**
- [What is the Microsoft Fabric Capacity Metrics app?](https://learn.microsoft.com/fabric/enterprise/metrics-app)
- [Monitor Fabric Capacity Health Using Capacity Overview Events](https://learn.microsoft.com/fabric/real-time-hub/tutorial-monitor-capacity-threshold)
- [What is workspace monitoring?](https://learn.microsoft.com/fabric/fundamentals/workspace-monitoring-overview)
- [What is the admin monitoring workspace?](https://learn.microsoft.com/fabric/admin/monitoring-workspace)
- [Use the monitoring hub to track Fabric activity](https://learn.microsoft.com/fabric/admin/monitoring-hub)
- [Evaluate and optimize your Microsoft Fabric capacity](https://learn.microsoft.com/fabric/enterprise/optimize-capacity)

---

---

### 3f. "Are statistics and trends over time available for semantic model partitions?"

**Answer:** Power BI does **not** provide built-in, out-of-the-box partition-level statistics or trend-over-time dashboards in the Fabric portal or the Capacity Metrics App. However, partition metadata **can** be accessed through the **XMLA endpoint** on Premium/Fabric capacities using the following approaches:

**Point-in-time partition metadata (available today):**

1. **SSMS (SQL Server Management Studio)** — Connect to the semantic model via the XMLA endpoint. In Object Explorer, you can view partitions for any table, including partition names, row counts, data sizes, and last-processed timestamps. This works for both tables with incremental refresh policies (which auto-create partitions) and manually managed partitions.

2. **DMV queries** — Run Dynamic Management View queries against the XMLA endpoint to get partition-level detail:
   - `TMSCHEMA_PARTITIONS` — Lists all partitions with state, modified time, refreshed time, and row counts.
   - `$System.DISCOVER_STORAGE_TABLE_COLUMNS` — Dictionary sizes by column.
   - `$System.DISCOVER_STORAGE_TABLE_COLUMN_SEGMENTS` — Segment-level used size, row count, and temperature (for on-demand load).

3. **DAX Studio / Tabular Editor** — Third-party tools (recommended in Microsoft docs) that connect via XMLA and provide richer visualization of partition metadata. DAX Studio's "View Metrics" (VertipaqAnalyzer) shows table, column, and partition sizes. You can export to `.vpax` files for sharing.

4. **TOM (Tabular Object Model) / PowerShell** — Programmatic access via the `Microsoft.AnalysisServices.Tabular` namespace to enumerate partitions, their row counts, sizes, and refresh times.

**Trends over time — not available out of the box.** None of these mechanisms provide historical trending. They are all point-in-time snapshots. To build partition-level trends (e.g., how row counts, sizes, or refresh durations change over time), you would need to:

- Schedule a script (PowerShell, Python, or Azure Automation) to periodically query the DMVs via the XMLA endpoint and store the results in a database or lakehouse.
- Build a Power BI report on top of that historical data store.

**Workspace Monitoring (Preview)** captures semantic model operation logs including refresh processing steps, which can show refresh duration per operation over time, but it does not currently expose partition-level row counts or sizes as time-series data.

**Bottom line:** Partition statistics are available as point-in-time data via the XMLA endpoint and DMVs. Trend-over-time analysis requires a custom-built solution that periodically captures and stores this data.

**References:**
- [Semantic model connectivity with the XMLA endpoint](https://learn.microsoft.com/fabric/enterprise/powerbi/service-premium-connect-tools)
- [Advanced incremental refresh — Partitions](https://learn.microsoft.com/power-bi/connect-data/incremental-refresh-xmla#partitions)
- [Refresh management with SSMS](https://learn.microsoft.com/power-bi/connect-data/incremental-refresh-xmla#refresh-management-with-sql-server-management-studio)
- [Large semantic models — Checking semantic model size (DMV examples)](https://learn.microsoft.com/fabric/enterprise/powerbi/service-premium-large-models#checking-semantic-model-size)
- [Data-level auditing — Data model metadata](https://learn.microsoft.com/power-bi/guidance/powerbi-implementation-planning-auditing-monitoring-data-level-auditing#data-model-metadata)

---

## Summary of Gaps

For transparency, here are the things that **cannot** be done today based on the documentation:

1. **No CU retention beyond 14 days** in the Metrics App (and no configurable retention).
2. **No API to programmatically access the Metrics App's semantic model.**
3. **No workspace-level or item-level CU attribution in the Capacity Overview Events** — only capacity-level with workload-type breakdown.
4. **No per-user query latency telemetry** — throttling state is capacity-level only.
5. **No memory usage telemetry** per item or user.
6. **No Microsoft-published recommended CU % thresholds** — customers must define their own guardrails.
7. **Workspace Monitoring is in Preview** and does not currently support all item types equally (e.g., pipeline activity-level monitoring is not yet available).
8. **No built-in partition-level trend data** — Partition statistics (row counts, sizes, refresh times) are available as point-in-time snapshots via the XMLA endpoint/DMVs but require a custom solution to track over time.
