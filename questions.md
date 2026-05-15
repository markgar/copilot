Seeking Guidance on Tenant-Level Capacity Observability in Power BI / Fabric
External
Ganguly, Payel (TR Technology)<Payel.Ganguly@thomsonreuters.com>

​
Mark Garner (WITH NO D);​
Corey Cox;​
Hamzah Pandith​
​Patel, Rita (TR Technology) <Rita.Patel@thomsonreuters.com>;​Munnangi, Pravallika (TR Technology) <Pravallika.Munnangi@thomsonreuters.com>​
Hi Mark , Crey and Hamzah,


Good Morning! Hope you all are doing well.

We’re reaching out to seek your expert guidance on a specific use case.
We are evaluating options for tenant‑level capacity observability and admin analytics in Power BI / Microsoft Fabric and would appreciate your inputs on current capabilities and forward‑looking plans.
 

1. Capacity Units (CU) Utilization – Historical Retention & Access

Currently, the Fabric Capacity Metrics App displays approximately 7 days of Capacity Unit (CU) utilization data, with no visibility beyond this window. Could you please confirm:

Whether CU usage/utilization can be retrieved historically for up to a month or longer?
If yes, is this controlled by:
A configurable retention setting, or
A backend telemetry retention limitation?
Additionally:

Is there a supported API to access the same underlying telemetry used by the Fabric Capacity Metrics App?
If such an API exists, could you please share relevant documentation or examples for programmatic access?

2. Capacity Telemetry, Event Streaming, and Granularity Gaps

We attempted to use Power BI Activity Log and the Capacity APIs Capacities - Get Workload - REST API (Power BI Power BI REST APIs) | Microsoft Learn  as a proxy for real‑time or near‑real‑time capacity monitoring. However, these sources do not expose critical capacity metrics such as:

Capacity Units (CU) consumption
CPU usage
Memory usage
Throttling indicators
As a result, the available event data is insufficient for accurate and detailed capacity utilization analysis.

We are aware of that the CU usage is available via Fabric Capacity Event Streaming in near‑real‑time. We implemented this in real time hub and checked that it currently provides high‑level, capacity‑level telemetry only, with fields such as:

CapacityName, capacitySkucapacitySku, capacityRegion
WindowStartTime & windowEndTime
BaseCapacityUnits & capacityUnitMs
InteractiveDelayThresholdPercentage etc.
While useful, this data does not provide visibility at the workspace, report, dataset, or user activity level, which is required for detailed analysis, chargeback/showback, and troubleshooting. 

3. Admin‑Level Analytics Requested by Business Stakeholders

We have received the following questions from business users and leadership regarding capacity usage, performance, and semantic model behavior. We are seeking guidance on which of these can be answered today and how an admin team should address them using Microsoft‑supported tooling.

Business stakeholders are also interested in understanding whether statistics and trends over time are available for Power BI semantic model (dataset) partitions.

Specifically, we are looking for your advice on the following areas:

“How is the CPU load behaving at various times of the month?”   Is this best addressed via: Capacity Metrics App only? Any additional admin analytics or exports?
“Which semantic model is busiest, and at what times?”   “Are we hitting any thresholds, and what are those thresholds?” 
--- We would like clarity on: Dataset‑level CPU / CU attribution. Any Microsoft‑defined or recommended thresholds. How admins should interpret “busy” from an official standpoint.

“Where are we exceeding recommended limits?”  Could you please advise:  Whether Microsoft publishes recommended limits or guardrails for:
CU usage

CPU saturation

Query wait times

   Or whether these are expected to be internally defined by customers

“Are users being dropped or waiting a long time for queries to respond?” We understand that:  User session‑level telemetry is not fully exposed in Power BI SaaS.
Could you please confirm:  What system‑level indicators admins should rely on (e.g., wait times, throttling) and What cannot be observed by design ?

We would also like to understand : What out‑of‑the‑box analytics Microsoft recommends (e.g., Capacity Metrics App, Admin insights) and whether these are considered the primary source of truth for capacity and performance monitoring?
 

 

Our objective is to set accurate expectations with stakeholders and build a supported, scalable admin monitoring approach aligned with Microsoft’s intended design. We intend to include multiple capacities (shared and dedicated) in our analysis. This exercise will also help us derive insights for further analysis on optimisation.


We appreciate your time and look forward to your expert guidance.

Thanks & Regards,
Payel

This e-mail is for the sole use of the intended recipient and contains information that may be privileged and/or confidential. If you are not an intended recipient, please notify the sender by return e-mail and delete this e-mail and any attachments. Certain required legal entity disclosures can be accessed on our website: https://www.thomsonreuters.com/en/resources/disclosures.html