# SQL Server Enabled by Azure Arc — Feature Deep Dive

## Overview

Connecting [[sql-server]] to [[azure-arc]] gives you a set of Azure-based management, security, monitoring, and compliance features for on-premises and multi-cloud SQL Server instances. The features you get depend on your **license type**, **SQL Server version/edition**, and **operating system**.

This document covers what each feature does, what it requires, and what it doesn't do.

---

## Feature Availability by License Type

Not everything is available on every license type. This is the most important table to internalize:

| Feature | License Only (`LicenseOnly`) | SA / Subscription (`Paid`) | PAYG (`PAYG`) |
|---|:---:|:---:|:---:|
| Connect to Arc + inventory | Yes | Yes | Yes |
| Detailed database inventory | Yes | Yes | Yes |
| Migration readiness assessment | Yes | Yes | Yes |
| Database migration (to Azure SQL MI) | Yes | Yes | Yes |
| Microsoft Entra authentication | Yes | Yes | Yes |
| Microsoft Defender for Cloud | Yes | Yes | Yes |
| Microsoft Purview governance | Yes | Yes | Yes |
| FCI / AG management | Yes | Yes | Yes |
| Client connection summary | Yes | Yes | Yes |
| Least privilege mode | Yes | Yes | Yes |
| ESU subscription | **No** | Yes | Yes |
| Best practices assessment | **No** | Yes | Yes |
| Automated backups (preview) | **No** | Yes | Yes |
| Point-in-time restore (preview) | **No** | Yes | Yes |
| Automatic updates | **No** | Yes | Yes |
| Performance monitoring (preview) | **No** | Yes | Yes |
| Free Power BI Report Server license | Yes¹ | Yes | Yes |
| 180-day dual-use benefit | **No** | Yes | Yes |

¹ Power BI Report Server license availability varies by edition and SQL version.

**Key takeaway**: `LicenseOnly` gets you inventory, security (Defender, Entra, Purview), and migration tools. The operational features — backups, patching, monitoring, best practices — require SA, subscription, or PAYG.

Source: [Feature availability depending on license type](https://learn.microsoft.com/sql/sql-server/azure-arc/overview?view=sql-server-ver17#feature-availability-depending-on-license-type)

---

## Inventory and Centralized Management

**What it does**: Every SQL Server instance connected to Arc appears as a first-class Azure resource (`SQL Server - Azure Arc`). You get:

- Instance-level details: version, edition, core count, host OS, patch level
- Database-level inventory: every database listed as a child resource with properties (size, compatibility level, encryption status, backup status, etc.)
- Cross-estate querying via [[azure-resource-graph]] ([docs](https://learn.microsoft.com/azure/governance/resource-graph/overview)) — run KQL queries across all your SQL Servers ("which instances are still on 2014?", "which databases haven't been backed up in 7 days?")
- Custom dashboards in the Azure portal pinned from Resource Graph queries

**Available on**: All license types, all editions (including Express), all supported versions (2012+), Windows and Linux.

**What it doesn't do**: It's read-only inventory — it doesn't let you remotely execute queries or manage databases. It reflects what the extension discovers; it doesn't modify SQL Server configuration.

Source: [Manage your SQL Server instances at scale](https://learn.microsoft.com/sql/sql-server/azure-arc/overview?view=sql-server-ver17#manage-your-sql-server-instances-at-scale-from-a-single-point-of-control)

---

## Best Practices Assessment

**What it does**: Runs a set of rules against your SQL Server configuration — based on years of Microsoft Support experience — and produces a report in the Azure portal with specific, actionable recommendations. Covers areas like:

- Security settings
- Performance configuration
- High availability configuration
- Storage and I/O layout
- SQL Server and OS settings

**Requirements**:
- License type: `Paid` or `PAYG` (not `LicenseOnly`)
- Windows only
- SQL Server 2012+
- Can be enabled at scale via [[azure-policy]]

**How it works**: The extension runs the assessment using `NT AUTHORITY\SYSTEM` (or the least-privilege service account if configured). Results are uploaded to Azure and visible in the portal under the SQL Server resource > **Best practices assessment**.

Source: [Configure SQL best practices assessment](https://learn.microsoft.com/sql/sql-server/azure-arc/assess?view=sql-server-ver17)

---

## Performance Monitoring (Preview)

**What it does**: Collects performance metrics from DMVs and displays them on a built-in performance dashboard in the Azure portal. Metrics include:

- CPU utilization (SQL process vs. other vs. idle)
- Active sessions and blocking
- Memory counters (buffer pool, PLE, target vs. total server memory)
- Storage I/O (IOPS, throughput, latency per file)
- Wait statistics
- Performance counters (compilations, transactions/sec, batch requests, lock waits, etc.)
- Database properties (encryption, CDC, change feed, compatibility level)

Collection runs at intervals from 10 seconds to 5 minutes depending on the metric type.

**Where the data goes**: The extension collects DMV data on the SQL Server host, then sends it outbound over HTTPS to the **Azure Arc Data Processing Service** (`telemetry.<region>.arcdataservices.com`). From there it enters the Azure telemetry pipeline for near real-time processing. The data is stored in the Azure telemetry backend — not in a Log Analytics workspace or Azure Monitor Metrics store you own. You view it exclusively through the built-in **Performance Dashboard** in the Azure portal (SQL Server resource > **Monitoring** > **Performance Dashboard**). There's no way to query the raw data, export it, or route it to your own storage. No personal data or customer content is collected — only DMV-level metadata and counters.

**Requirements**:
- License type: `Paid` or `PAYG`
- Windows only
- SQL Server 2016 SP1+ or later
- Enterprise or Standard edition (not Express or Developer)
- Connectivity to `telemetry.<region>.arcdataservices.com`

**What it doesn't do**: It's not a replacement for a full monitoring solution (no alerting built in, no historical deep-dive beyond what the dashboard shows). It's useful for portal-based spot-checks and triage, not 24/7 ops monitoring.

Source: [Monitor SQL Server enabled by Azure Arc (preview)](https://learn.microsoft.com/sql/sql-server/azure-arc/sql-monitoring?view=sql-server-ver17)

---

## Client Connection Summary

**What it does**: Shows a summary of all client connections to the SQL Server instance over the last 30 days. The Azure Connected Machine agent polls `sys.dm_exec_sessions` hourly and uploads summarized data. In the portal you see:

- Program name, client interface, database name
- Total reads/writes, elapsed time
- Session count, last request time

Useful for understanding who/what is connecting to a SQL Server — especially during migration planning or decommission analysis.

**Requirements**:
- Windows only
- SQL Server 2016 SP1+ or later
- All license types
- All editions (including Express)

Source: [Client connection summary](https://learn.microsoft.com/sql/sql-server/azure-arc/sql-connection-summary?view=sql-server-ver17)

---

## Automated Backups (Preview)

**What it does**: The Azure Extension for SQL Server performs native SQL Server backups to a local or network share path on a schedule you configure. Default schedule:

- Full backup: every 7 days
- Differential backup: every 12 hours
- Log backup: every 5 minutes

Schedules are customizable at the instance or individual database level. Backups are standard native SQL Server backups — history is recorded in `msdb` backup tables.

**Requirements**:
- License type: `Paid` or `PAYG`
- Windows only
- Disabled by default — must be explicitly enabled
- The backup agent uses `NT AUTHORITY\SYSTEM` (or least-privilege account). It needs `dbcreator` at the server level and `db_backupoperator` in each relevant database.

**What it doesn't do**: It doesn't send backups to Azure Blob Storage. Backups go to the default backup location or a path you specify (local disk, UNC share). If you need cloud-based backup, you'd use SQL Server's native backup-to-URL or a third-party tool.

Source: [Manage automated backups](https://learn.microsoft.com/sql/sql-server/azure-arc/backup-local?view=sql-server-ver17)

---

## Point-in-Time Restore (Preview)

**What it does**: Restores a database to a new database on the same SQL Server instance from a specific point in time, using the automated backups described above.

- Available via Azure portal or Azure CLI (`az sql db-arc restore`)
- Requires automated backups to be enabled first
- Creates a new database (doesn't overwrite the source)

**Requirements**:
- Automated backups must be configured and running
- License type: `Paid` or `PAYG`

Source: [Restore to a point-in-time](https://learn.microsoft.com/sql/sql-server/azure-arc/point-in-time-restore?view=sql-server-ver17)

---

## Automatic Updates

**What it does**: Configures Windows Update / Microsoft Update on the host to automatically install SQL Server and Windows updates marked as **Important** or **Critical**. This is essentially the same mechanism as Windows Update, but managed through Arc.

**Key details**:
- Only Important/Critical updates are installed — cumulative updates, service packs, and non-critical patches must still be installed manually
- Operates at the host OS level — applies to all SQL instances on the machine
- Overrides any pre-existing Windows Update / Microsoft Update policies on the server
- Windows only

**Requirements**:
- License type: `Paid` or `PAYG`

**What it doesn't replace**: This is not a full patching solution. It won't install CUs or SPs that aren't rated Critical/Important. For comprehensive patch management, pair it with WSUS, SCCM, [[azure-update-manager]], or equivalent.

Source: [Configure automatic updates](https://learn.microsoft.com/sql/sql-server/azure-arc/update?view=sql-server-ver17)

---

## Microsoft Entra Authentication

**What it does**: Enables [[microsoft-entra-id]] (formerly Azure AD) authentication for SQL Server, using the managed identity provisioned through Arc. This gives you:

- Centralized identity management — no more SQL logins with passwords
- MFA, SSO, conditional access policies
- Managed identity for outbound connections to Azure services (Key Vault, Blob Storage, Fabric, etc.)
- Inbound authentication via Entra ID users/groups

**Requirements**:
- SQL Server 2022+ for inbound authentication via app registration
- SQL Server 2025+ for managed identity-based authentication (recommended)
- Azure Arc connection with managed identity enabled
- Certificate stored in [[azure-key-vault]] (2022 only; not needed for 2025)
- All license types

**How it works**: The Connected Machine agent creates a system-assigned managed identity (SAMI) for the server — this is the server's representation in Entra. Two distinct directions:

- **Outbound** (SQL Server → Azure services like Key Vault, Blob Storage, Fabric): SQL Server presents the SAMI to authenticate itself to Azure services.
- **Inbound** (users/apps authenticating to SQL Server via Entra): Users connect with their own Entra identities (user accounts, service principals, managed identities from other resources). On SQL Server 2025, the SAMI is sufficient — it represents SQL Server in Entra so tokens can be issued for it; no app registration needed. On SQL Server 2022, there's no SAMI support, so you must create an app registration manually to serve that role. App registrations can only enable inbound — they cannot enable outbound connections.

### How Entra inbound auth works (SQL Server 2022)

On 2022, you must manually create an **app registration** in Entra to represent SQL Server. This involves:

1. Create the app registration (gives you an Application ID)
2. Create a certificate in Azure Key Vault
3. Upload the certificate's public key to the app registration
4. Grant Graph API permissions (`Directory.Read.All`, or `Application.Read.All` + `Group.Read.All` + `User.Read.All`) with admin consent
5. The Arc agent downloads the certificate's private key to the SQL Server host

The certificate binds SQL Server to its app registration — SQL Server uses the private key to authenticate to Graph for resolving users/groups. The app registration's Application ID is the **audience** — Entra needs it to know what the token is for.

Each SQL Server should have its own app registration. Sharing one registration across servers means tokens are interchangeable (a token for Server A would be accepted by Server B), you lose audit separation in Entra sign-in logs, and a compromised certificate affects all servers.

On **SQL Server 2025**, the SAMI replaces all of this — no app registration, no certificate, no Graph permissions to configure. Each Arc-connected server automatically gets its own unique identity.

### User vs. service principal authentication

Two common inbound scenarios; both target SQL Server's app registration (2022) or SAMI (2025) as the audience:

- **User authentication**: A human authenticates to Entra interactively (username/password, MFA, SSO, etc.). Entra issues a token targeting SQL Server's application ID. The user's client connects on port 1433 and presents the token. SQL Server validates it and maps it to an Entra login.
- **Service principal authentication**: An application (not a human) authenticates to Entra using *its own* app registration's credentials (its own app ID + certificate or client secret). Entra issues a token targeting SQL Server's application ID as the audience. Two registrations are involved — the caller's and SQL Server's. On SQL Server you create a login for the caller's app ID:
  ```sql
  CREATE LOGIN [<caller-app-id>] FROM EXTERNAL PROVIDER;
  ```

Note: "Service principal" in Entra (an application identity) is unrelated to "SPN" in Kerberos (`MSSQLSvc/server:1433`), which is a traditional AD/Windows auth concept.

Source: [Managed identity for SQL Server enabled by Azure Arc](https://learn.microsoft.com/sql/sql-server/azure-arc/managed-identity?view=sql-server-ver17), [Microsoft Entra authentication for SQL Server](https://learn.microsoft.com/sql/relational-databases/security/authentication-access/azure-ad-authentication-sql-server-overview?view=sql-server-ver17), [Set up Entra auth for SQL Server 2022](https://learn.microsoft.com/sql/sql-server/azure-arc/entra-authentication-setup-tutorial?view=sql-server-ver16)

---

## Microsoft Defender for Cloud

**What it does**: [[microsoft-defender-for-cloud]] provides vulnerability assessment and advanced threat protection for Arc-enabled SQL Server:

1. **Vulnerability assessment**: Scans databases for security misconfigurations, excessive permissions, unencrypted data, and other risks. Provides remediation guidance.
2. **Advanced Threat Protection**: Detects anomalous activities — SQL injection attempts, unusual access patterns, brute force login attacks — and generates security alerts with recommended actions.

**Requirements**:
- [[azure-monitor]] Agent (AMA) installed on the Arc-enabled server
- All license types
- Defender for SQL plan enabled in your subscription
- Cost savings available when enabled through Arc vs. standalone

Source: [Microsoft Defender for Cloud](https://learn.microsoft.com/azure/defender-for-cloud/defender-for-sql-usage)

---

## Microsoft Purview Integration

**What it does**: Connects your on-premises SQL Server into [[microsoft-purview]] for unified data governance:

- Automated data discovery and cataloging
- Sensitive data classification
- End-to-end data lineage
- Data owner access policies (manage who can access what from Purview, enforced at the SQL Server level)

Arc makes it easier to register and scan on-premises SQL Servers in Purview, and powers the access policy enforcement feature.

**Requirements**:
- Self-hosted integration runtime for scanning
- Microsoft Entra ID and Key Vault enabled (for RBAC)
- All license types

Source: [Microsoft Purview](https://learn.microsoft.com/sql/sql-server/azure-arc/overview?view=sql-server-ver17#microsoft-purview)

---

## Migration Readiness Assessment

**What it does**: Automatically assesses your SQL Server instances for migration to Azure SQL (Azure SQL DB, SQL MI, SQL Server on Azure VM). Produces:

- Cloud readiness analysis per target
- Blocker / warning / informational findings
- Risk identification and mitigation strategies
- **Performance-based SKU recommendation** — collects 30-second performance samples, aggregates over 10-minute windows, stores a month of data, and uses 95th-percentile sizing to recommend the right Azure SQL tier and configuration

Runs on a default weekly schedule. Results are available in the portal under **Migration > Assessments**.

A centralized [Migration Dashboard](https://learn.microsoft.com/sql/sql-server/azure-arc/migration-inventory?view=sql-server-ver17) aggregates readiness across your entire SQL estate.

**Requirements**:
- Windows only
- SQL Server 2012+
- Extension version 1.1.2594.118+
- All license types (including `LicenseOnly`)

Source: [Assess migration readiness](https://learn.microsoft.com/sql/sql-server/azure-arc/migration-assessment?view=sql-server-ver17)

---

## Database Migration (to Azure SQL MI)

**What it does**: Migrate databases from Arc-enabled SQL Server to [[azure-sql-managed-instance]] directly from the Azure portal using the Managed Instance Link. Supports:

- Online migration (minimal downtime using AG-based replication)
- Reverse migration back to SQL Server 2022/2025
- Migration wizard in the portal handles link creation, data sync, and cutover

**Requirements**:
- SQL Server 2016+ (for link-based migration)
- Windows only
- All license types

Source: [Migrate to Azure SQL Managed Instance](https://learn.microsoft.com/sql/sql-server/azure-arc/migrate-to-azure-sql-managed-instance?view=sql-server-ver17)

---

## Extended Security Updates (ESU)

**What it does**: For SQL Server versions past end of support (2012, 2014), Arc enables a pay-as-you-go ESU subscription — monthly billing through Azure instead of annual VLSC purchases. You get:

- Critical and Important security updates for up to 3 years past end of support
- Auto-cancellation when you upgrade to a supported version or migrate to Azure SQL
- Per-instance subscription management in the portal

**Requirements**:
- License type: `Paid` or `PAYG`
- SQL Server must be past its end-of-support date
- 30-day connectivity rule applies (same as PAYG)

Source: [Extended Security Updates enabled by Azure Arc](https://learn.microsoft.com/sql/sql-server/azure-arc/extended-security-updates?view=sql-server-ver17)

---

## Failover Cluster Instance (FCI) and Availability Group (AG) Support

**What it does**: Arc-enabled SQL Server recognizes and manages FCI and AG configurations:

- FCI passive nodes and AG secondary replicas are detected for proper billing ($0 DR meter for qualifying passive instances)
- AG health and configuration visible in the portal
- AG failover operations can be managed through Arc
- All FCI/AG nodes must be individually connected to Arc

**Requirements**:
- Windows only (FCI and AG management via Arc)
- All license types, all editions that support FCI/AG

Source: [Failover cluster instances](https://learn.microsoft.com/sql/sql-server/azure-arc/support-for-fci?view=sql-server-ver17), [Availability groups](https://learn.microsoft.com/sql/sql-server/azure-arc/manage-availability-group?view=sql-server-ver17)

---

## Least Privilege Mode

**What it does**: By default, the Azure Extension for SQL Server runs as `NT AUTHORITY\SYSTEM`, which has full admin access. Least privilege mode lets you run the extension under a dedicated low-privilege local Windows account (`NT Service\SQLServerExtension`) with only the specific SQL Server and OS permissions it actually needs.

Permissions are dynamically elevated only when a specific feature requires it (e.g., `sysadmin` is temporarily granted during database migration, then removed).

**Requirements**:
- Windows only
- All license types, all versions, all editions

Source: [Operate with least privilege](https://learn.microsoft.com/sql/sql-server/azure-arc/configure-least-privilege?view=sql-server-ver17)

---

## Fabric Mirroring (SQL Server 2025)

**What it does**: Continuously replicates SQL Server databases to [[microsoft-fabric]]'s OneLake in Delta Parquet format, enabling analytics, [[power-bi]], Spark, and data engineering scenarios without building ETL pipelines.

**How Arc is involved**: For SQL Server 2025, Arc provides the managed identity that authenticates SQL Server to Fabric. The data replication itself is a native engine feature (the "Fabric mirroring change feed"), not something the Arc extension moves. For SQL Server 2016–2022, mirroring uses CDC instead and does not require Arc.

**Requirements (SQL Server 2025)**:
- Azure Arc connection with managed identity enabled
- On-premises data gateway or VNet data gateway
- On-premises SQL Server only (Azure VMs not currently supported for 2025 mirroring)
- Windows only
- For AGs, every node must be Arc-connected and each secondary's SAMI must have Contributor access to the Fabric workspace

Source: [Mirroring SQL Server](https://learn.microsoft.com/fabric/mirroring/sql-server), [Tutorial: Configure Fabric mirroring from SQL Server](https://learn.microsoft.com/fabric/mirroring/sql-server-tutorial)

---

## Feature Availability by OS

Most Arc SQL features are Windows-only. Linux support is limited:

| Feature | Windows | Linux |
|---|:---:|:---:|
| Inventory | Yes | Yes |
| PAYG / license management | Yes | Yes |
| ESU subscription | Yes | Yes |
| Entra authentication | Yes | **No** |
| Defender for Cloud | Yes | Yes |
| Purview | Yes | Yes |
| Best practices assessment | Yes | **No** |
| Automated backups | Yes | **No** |
| Point-in-time restore | Yes | **No** |
| Automatic updates | Yes | **No** |
| Performance monitoring | Yes | **No** |
| Client connection summary | Yes | **No** |
| FCI / AG management | Yes | **No** |
| Least privilege mode | Yes | **No** |
| Passive replica detection | Yes | **No** |
| Fabric mirroring (2025) | Yes | **No** |

Source: [Feature availability by operating system](https://learn.microsoft.com/sql/sql-server/azure-arc/overview?view=sql-server-ver17#feature-availability-by-operating-system)

---

## Feature Availability by SQL Server Version

| Feature | 2012–2014 | 2016–2019 | 2022 | 2025 |
|---|:---:|:---:|:---:|:---:|
| Inventory | Yes | Yes | Yes | Yes |
| FCI / AG management | Yes | Yes | Yes | Yes |
| Least privilege | Yes | Yes | Yes | Yes |
| Performance monitoring | **No** | Yes¹ | Yes | Yes |
| Client connection summary | **No** | Yes¹ | Yes | Yes |
| Best practices assessment | Yes² | Yes | Yes | Yes |
| Entra authentication | **No** | **No** | Yes³ | Yes |
| Managed identity (native) | **No** | **No** | **No** | Yes |
| Fabric mirroring (native) | **No** | CDC-based | CDC-based | Change feed |

¹ Requires SQL Server 2016 SP1+.
² Requires ESU subscription for SQL Server 2012.
³ SQL Server 2022 uses app registration; SQL Server 2025 uses managed identity directly.

Source: [Feature availability by version](https://learn.microsoft.com/sql/sql-server/azure-arc/overview?view=sql-server-ver17#feature-availability-by-version)

---

**Sources**:
- [SQL Server enabled by Azure Arc — Overview](https://learn.microsoft.com/sql/sql-server/azure-arc/overview?view=sql-server-ver17)
- [Security — SQL Server enabled by Azure Arc](https://learn.microsoft.com/sql/sql-server/azure-arc/security-overview?view=sql-server-ver17)
- [Release notes — SQL Server enabled by Azure Arc](https://learn.microsoft.com/sql/sql-server/azure-arc/release-notes?view=sql-server-ver17)
- [Monitor SQL Server enabled by Azure Arc](https://learn.microsoft.com/sql/sql-server/azure-arc/sql-monitoring?view=sql-server-ver17)
- [Managed identity for SQL Server enabled by Azure Arc](https://learn.microsoft.com/sql/sql-server/azure-arc/managed-identity?view=sql-server-ver17)
- [Mirroring SQL Server](https://learn.microsoft.com/fabric/mirroring/sql-server)
