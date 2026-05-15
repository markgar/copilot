# SQL Server Arc Pay-As-You-Go — How It Actually Works

## What It Is

Pay-as-you-go (PAYG) is a third way to license [[sql-server]] — alongside perpetual L+SA and subscription — where you pay hourly through your Azure bill instead of through a volume licensing agreement. It requires your SQL Server to be connected to [[azure-arc]].

It's available for SQL Server 2012 through 2025, Standard and Enterprise editions. (Web edition is available for `LicenseOnly` but is discontinued in SQL Server 2025 and later.)

## The Core Concept

You install the Azure Connected Machine agent and the Azure Extension for SQL Server on your host. The extension collects SQL Server usage locally and uploads it to Azure roughly every 12 hours. Azure meters it hourly and puts the charges on your Azure invoice. No EA, no true-up, no anniversary — just an Azure bill like any other Azure resource.

You get the same SA-equivalent benefits as a license with [[software-assurance]] or a SQL Server subscription:

- Version upgrade rights
- HA/DR failover rights (free passive replicas)
- Unlimited virtualization (Enterprise, p-core)
- ESU eligibility
- Best practices assessment
- Automated backups, point-in-time restore, automatic updates
- Monitoring, connection summaries
- [[microsoft-entra-id]] authentication
- [[microsoft-defender-for-cloud]] integration
- [[microsoft-purview]] governance
- Migration readiness assessment
- [[power-bi-report-server]] license (Enterprise w/ SA or subscription; Standard + Enterprise for all license types in SQL 2025+)
- 180-day dual-use benefit (run SQL on-prem and in Azure simultaneously during migration)

You do NOT get [[azure-hybrid-benefit]] — that's for bringing your own license to Azure. PAYG *is* the Azure billing model, so AHB doesn't apply.

## Installing Arc (High-Level)

Arc onboarding installs two components: the **Azure Connected Machine agent** (registers the server with Azure) and the **Azure Extension for SQL Server** (discovers SQL instances and reports usage). On new machines, a single onboarding script installs both. If the server is already Arc-connected, you just add the SQL extension.

### Prerequisites

- An Azure account with an active subscription
- Resource providers registered: `Microsoft.HybridCompute`, `Microsoft.AzureArcData`, `Microsoft.HybridConnectivity`, `Microsoft.GuestConfiguration`
- RBAC: `Azure Connected Machine Onboarding` role (or Contributor/Owner) on the target resource group
- Local admin on the machine (Windows Local Administrators group, or root on Linux)
- Outbound HTTPS (443) connectivity to Azure — either directly, through a proxy, or via Private Link. See [network requirements](https://learn.microsoft.com/azure/azure-arc/servers/network-requirements)

### Single-Machine Onboarding (Portal Script)

1. In the Azure portal, go to **Azure Arc > SQL Server > + Add**
2. Select **Connect SQL Server instances**
3. Fill in subscription, resource group, region, OS, edition, and license type (`PAYG`, `Paid`, or `LicenseOnly`)
4. Optionally exclude specific SQL instances by name
5. Click **Run script** → **Download**
6. On the target machine, execute the script:
   - **Windows**: Run in an elevated PowerShell: `& '.\RegisterSqlServerArc.ps1'`
   - **Linux**: `sudo chmod +x ./RegisterSqlServerArc.sh && ./RegisterSqlServerArc.sh`

The script installs the Connected Machine agent (if not already present), registers the server as a `Server - Azure Arc` resource, then installs the SQL extension, which creates `SQL Server - Azure Arc` resources for each discovered instance.

### Server Already Arc-Connected

If the Connected Machine agent is already installed but the SQL extension isn't:

- **Portal**: Go to the Arc server resource > **Extensions** > **+ Add** > select `Azure extension for SQL Server` > set edition and license type > **Create**
- **Azure CLI**:
  ```
  az connectedmachine extension create \
    --machine-name "<machine>" --resource-group "<rg>" --location "<region>" \
    --name "WindowsAgent.SqlServer" --type "WindowsAgent.SqlServer" \
    --publisher "Microsoft.AzureData" \
    --settings '{"SqlManagement":{"IsEnabled":true}, "LicenseType":"PAYG"}'
  ```

### At Scale

- **Automatic deployment**: Arc auto-installs the SQL extension on any newly connected server where SQL Server is detected. Set the license type via the `ArcSQLServerExtensionDeployment` tag on the server. To opt out, set that tag to `Disabled`.
- **Configuration Manager**: Push the onboarding script via SCCM task sequences or PowerShell deployments.
- **[[azure-policy]] / service principal**: Use a service principal with `Azure Connected Machine Onboarding` role for unattended bulk onboarding. See [Connect machines at scale](https://learn.microsoft.com/azure/azure-arc/servers/onboard-service-principal).

### SQL Server 2022+ Installer Integration

Starting with SQL Server 2022, the installer has a built-in option to connect to Azure Arc during setup. Select the Azure Arc option during installation and provide your Azure credentials — it handles the agent and extension install as part of SQL Server setup.

### Validation

After onboarding, verify in the portal:

- **Azure Arc > Servers**: The machine should appear as `Connected`
- **Azure Arc > SQL Server**: Each SQL instance should appear with the correct edition, version, and license type
- On the machine: `azcmagent show` displays agent status and connectivity

**Sources**: [Prerequisites](https://learn.microsoft.com/sql/sql-server/azure-arc/prerequisites), [Connect your SQL Server to Azure Arc](https://learn.microsoft.com/sql/sql-server/azure-arc/connect), [Deployment options](https://learn.microsoft.com/sql/sql-server/azure-arc/deployment-options), [Manage automatic connection](https://learn.microsoft.com/sql/sql-server/azure-arc/manage-autodeploy)

## What Gets Metered

The extension looks at the SQL Server edition installed and the number of cores visible to the OS. It picks the right meter automatically:

- **V-core licensing**: Billed per v-core of the VM. Minimum 4 cores per OSE. Standard edition capped at 24 v-cores even if the OSE has more.
- **P-core without VMs**: Billed per physical core of the host. Minimum 4 cores. Standard edition capped at 24 p-cores.
- **P-core with unlimited virtualization**: A single license resource covers all VMs on the host. Billed per physical core. Minimum 16 p-cores. Enterprise edition only.

If multiple SQL Server instances are on the same OSE, you're billed once for the OSE based on the highest edition installed — not per instance.

The affinity mask doesn't help. Even if you restrict SQL to 4 of 16 cores, you pay for all 16. The licensing rule is: you license the cores *available* to the OSE, not the cores SQL Server actually uses.

## Billing Granularity

- **One hour** is the smallest billing unit. If SQL ran for 5 minutes during an hour, you pay for the full hour.
- **VM stopped** = not billed (no usage data collected).
- **SQL Server service stopped** = not billed (extension requires an active instance to report).
- **VM running but SQL Server idle** = still billed (the instance is running, even if nobody's connected).

## The 30-Day Connectivity Rule

This is the most important operational detail for PAYG.

The extension collects usage data locally and uploads it roughly every 12 hours. If the machine loses connectivity to Azure:

<table>
<tr>
  <th>Scenario</th>
  <th></th>
  <th>What Happens</th>
</tr>
<tr>
  <td colspan="2"><strong>Reconnects within 30 days</strong></td>
  <td>Usage logs stored locally get uploaded. Billing is based on actual usage during the disconnected period. If the VM was off, those hours aren't billed.</td>
</tr>
<tr>
  <td rowspan="2"><strong>Disconnected beyond 30 days</strong></td>
  <td><strong>CSP</strong> (<a href="https://learn.microsoft.com/partner-center/overview">Cloud Solution Provider</a> — an Azure subscription managed by a Microsoft partner on your behalf; with recurring billing consent)</td>
  <td>The Connected Machine agent certificate expires. Azure switches to <strong>recurring billing</strong> based on the last known configuration (edition, core count, HA setup). Charges are backfilled for the 30 days of silence, then continue hourly until the machine reconnects. The PAYG subscription also expires — you are no longer authorized to use the software.</td>
</tr>
<tr>
  <td><strong>Non-CSP</strong></td>
  <td>The Connected Machine agent certificate expires. <strong>No charges while disconnected</strong> — billing resumes when/if the machine reconnects. However, the PAYG subscription still expires at day 30, so you are <strong>out of compliance</strong> for the entire disconnected period. This is a licensing violation, not just a billing gap.</td>
</tr>
<tr>
  <td rowspan="2"><strong>Never reconnects</strong></td>
  <td><strong>CSP</strong> (with recurring billing consent)</td>
  <td>Billing continues indefinitely at the last known configuration. You're paying for a server you might not even be running.</td>
</tr>
<tr>
  <td><strong>Non-CSP</strong></td>
  <td>No billing while disconnected — billing resumes upon reconnection. You remain <strong>out of compliance</strong> for the entire disconnected period.</td>
</tr>
</table>

**This means**: if you intentionally take a PAYG server offline for more than 30 days, you should **disconnect it from Azure Arc first**. For CSP subscriptions, this avoids being billed as if it's still running. For all subscriptions, it avoids losing authorization to use the software. When you bring it back, re-onboard it to Arc.

For intermittent-use servers that regularly go dark for 30+ days, PAYG is probably the wrong model. Consider volume licensing instead, or accept the overhead of disconnecting/reconnecting from Arc each time.

> **June 2026 enforcement**: Starting June 2026, Azure Arc will begin **enforcing** the 30-day check-in requirement. This means machines that fail to check in within 30 days will be actively flagged/blocked, not just silently shifted to recurring billing. Plan ahead — this is imminent.

## Recurring Billing (CSP-Specific)

If your Azure subscription is managed by a Cloud Solution Provider (CSP), there's an extra requirement: you or the CSP must explicitly consent to recurring billing before PAYG can be enabled. This consent is recorded on the extension and can't be changed without reinstalling. New PAYG subscriptions aren't allowed without this consent.

For non-CSP subscriptions (direct EA Azure subscriptions, etc.), this consent isn't required.

### SPLA Transition

For SQL Server instances currently licensed through a Services Provider License Agreement (SPLA), use `LicenseOnly` for the license type until you transition. Transitioning to PAYG requires onboarding to Arc in a CSP-managed subscription with recurring billing consent. SPLA vendors should ensure the Azure Connected Machine agent and extension are healthy before transition — a broken or misconfigured extension leads to underreported usage and noncompliance.

## How PAYG Compares to Volume Licensing

| | PAYG (Arc) | Perpetual L+SA (EA) | Subscription (EA) |
|---|---|---|---|
| **Billing** | Hourly, on Azure invoice | Annual true-up at EA anniversary | Annual true-up at EA anniversary |
| **Granularity** | Pay only for hours SQL is running | Pay for every core in your baseline, all year | Pay for every core in your baseline, all year |
| **Scale down** | Stop the VM = stop paying | Can't reduce until enrollment renewal | Can true-down to high-water mark at anniversary |
| **Scale up** | Just deploy — metered automatically | Deploy now, pay at true-up | Deploy now, pay at true-up |
| **Commitment** | None — can switch to BYOL anytime | 3-year enrollment term | Annual, within EA term |
| **Own the license?** | No | Yes (perpetual) | No |
| **SA-equivalent benefits?** | Yes | Yes (with active SA) | Yes |
| **Who tracks compliance?** | Azure (automatic metering) | You (self-reported true-up + audit risk) | You (self-reported true-up + audit risk) |

## When PAYG Makes Sense

- **Variable workloads**: Dev/test servers that spin up and down. Seasonal capacity. Short-lived projects.
- **No EA / no VL agreement**: Small shops or teams that don't have (or want) a volume licensing relationship for SQL Server.
- **Avoiding true-up risk**: You don't want to worry about tracking deployments and reporting at anniversary. Arc does it for you.
- **Migration staging**: You're moving to Azure SQL and want to avoid committing to a new 3-year license term for servers that will be decommissioned.
- **Compliance simplification**: The extension tracks and reports everything automatically. No more spreadsheet audits.

## When PAYG Doesn't Make Sense

- **Stable, always-on production workloads**: If you're running 100 Enterprise cores 24/7/365, the hourly rate will almost certainly cost more than a volume license. PAYG pricing tends to be a premium for the flexibility.
- **Unreliable connectivity**: If your servers can't maintain a connection to Azure (air-gapped, strict firewall policies), the 30-day rule becomes a liability.
- **Linux limitations**: On Linux, passive instance detection isn't available — all instances bill as active, even DR secondaries. Core detection is OS-level only. Connected user detection on readable secondaries isn't available either. If you have a lot of passive AG replicas on Linux, PAYG will overbill compared to volume licensing where you'd simply declare them passive.
- **Listed providers / multi-cloud**: The unlimited virtualization benefit is **not available** for VMs running on infrastructure from [listed providers](https://aka.ms/listedproviders) (AWS, GCP, and others). Those VMs can only be licensed by v-core. If you create a p-core license intending to cover listed-provider VMs, you'll still be charged per v-core based on each VM's SQL config.
- **Outsourcing restrictions**: Deploying PAYG through Azure Arc is subject to [Product Terms outsourcing restrictions](https://www.microsoft.com/licensing/terms/productoffering/MicrosoftAzure/allprograms). If you host SQL Server on third-party infrastructure, verify you comply with these terms.

## Switching Between Models

You can switch between PAYG and BYOL (bring your own license) at any time by changing the `licenseType` property on the extension or re-running SQL Server setup:

- `PAYG` → billed hourly through Azure
- `Paid` → you attest you have a license with SA or subscription (free $0 meter for tracking)
- `LicenseOnly` → perpetual license without SA (limited Arc features)

The switch is effective immediately. There's no penalty or waiting period.

A common transition pattern: an org runs PAYG while their EA is being negotiated, then switches to `Paid` once the license agreement is signed. Or the reverse — an EA expires and they flip to PAYG to maintain compliance without a gap.

> **Important**: If you're switching from `Paid` to `PAYG` while using **unlimited virtualization**, switch the p-core license resource's billing plan to `PAYG` **first**, then switch individual VMs to `PAYG`. If you switch VMs first, they'll be individually billed by v-core until the p-core license catches up.

## Passive / DR Replicas

On Windows, the extension automatically detects passive AG secondaries and FCI passive nodes and emits a $0 DR meter instead of a paid meter. The rules for qualifying as passive:

- All replicas in the OSE must be secondary (or a DAG forwarder not in use)
- No standalone databases outside an AG (regardless of database state)
- No active user connections to user databases
- No associated services (SSIS, SSRS, SSAS) running on the same machine

> **Note on standalone associated services**: SSIS, SSRS, SSAS, and Power BI Report Server installed as standalone instances (without the SQL Server database engine) are metered separately under PAYG. If a p-core license is active in scope and the machine is configured to use it, standalone associated services are covered and not individually billed.

If a readable secondary has active connections, it doesn't qualify — it gets billed.

> **Note**: Connecting to `master`, `msdb`, `tempdb`, or `model` to run DMV queries or `BACKUP DATABASE` commands does **not** disqualify a passive replica. Only user-database connections matter.

During failover, the extension detects the role change and switches billing automatically. No double-billing (within the hourly granularity — a failover within the same hour might bill both briefly).

On Linux, none of this works. All instances are billed as active.

## Dev/Test

Two options to avoid paying for non-production:

1. **Developer Edition**: Free. The extension detects it and emits a $0 meter regardless of the host license type setting.
2. **Azure Dev/Test subscription**: Put your non-prod Arc machines in a dev/test subscription. All SQL meters in that subscription type are nullified. This lets you run Standard/Enterprise in non-prod without charges.

## Physical Core License (Unlimited Virtualization)

For PAYG with unlimited virtualization, you create a `SQLServerLicense` Azure resource:

- Set `licenseCategory` = `Core`
- Set `billingPlan` = `PAYG`
- Set the `scopeType` (tenant, subscription, or resource group)
- Set `Size` = total physical cores across your hosts (minimum 16)
- Activate it

All VMs in scope that are configured to use the p-core license (`UsePhysicalCoreLicense` = true) are covered. The p-core license resource itself gets billed at the Enterprise hourly rate per p-core. Individual VMs within scope show a $0 "Virtual license" meter.

This is the most cost-effective PAYG option for dense virtualization scenarios (many VMs per host).

> **Restriction**: Unlimited virtualization is **not available** for VMs on [listed provider](https://aka.ms/listedproviders) infrastructure (AWS, GCP, etc.). Those VMs are billed individually by v-core regardless of any p-core license in scope. Physical machines without VMs that happen to be in a p-core license scope are also licensed/billed separately — the unlimited virtualization benefit doesn't apply to bare-metal hosts.

## Cost Management

PAYG charges show up in Azure Cost Management like any other Azure resource. You can:

- Filter by **Service name** = "Azure Arc-enabled SQL Server"
- Group by resource, resource group, or meter to see what's driving costs
- Set budget alerts (50%, 75%, 90%)
- View forecasts

The meter names tell you the edition and billing type (e.g., "Ent edition - PAYG", "Std edition - PAYG", "Ent edition - DR replica").

## Extension Health and Compliance

With PAYG, the health of the Azure Extension for SQL Server is a **compliance requirement**, not just an operational nice-to-have. If the extension is broken, blocked by firewalls, or misconfigured (proxy issues, etc.), it stops reporting usage — which means underreported billing, potential noncompliance, and reduced Arc functionality (monitoring, Entra auth, inventory).

Azure provides a [Health Dashboard](https://ms.portal.azure.com/#view/Microsoft_Azure_ArcCenterUX/ArcCenterMenuBlade/%7E/sqlServerHealthDashboard) in the portal for a high-level view of extension state. You should also:

- Subscribe to Activity Log events for missed usage uploads or recurring billing triggers
- Check the billing mode of each machine via the Arc-enabled SQL Server Billing dashboard
- Use Azure Resource Graph queries to surface machines with stale `lastBilled` timestamps

---

**Sources**:
- [Manage licensing and billing — SQL Server enabled by Azure Arc](https://learn.microsoft.com/sql/sql-server/azure-arc/manage-license-billing?view=sql-server-ver17)
- [Move SQL Server license to pay-as-you-go](https://learn.microsoft.com/sql/sql-server/azure-arc/manage-pay-as-you-go-transition?view=sql-server-ver17)
- [FAQ — SQL Server enabled by Azure Arc](https://learn.microsoft.com/sql/sql-server/azure-arc/faq?view=sql-server-ver17)
- [SQL Server pricing](https://www.microsoft.com/sql-server/sql-server-2022-pricing)
- [Listed providers (unlimited virtualization exclusion)](https://aka.ms/listedproviders)
- [Product Terms outsourcing restrictions](https://www.microsoft.com/licensing/terms/productoffering/MicrosoftAzure/allprograms)
