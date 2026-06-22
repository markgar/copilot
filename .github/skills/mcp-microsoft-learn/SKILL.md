---
name: mcp-microsoft-learn
description: Authoritative Microsoft, Azure, Microsoft Fabric, and Power BI knowledge via the Microsoft Learn MCP server — official documentation, code samples, and product/API reference. Use this skill whenever a request involves Microsoft/Azure/Fabric/Power BI products, services, SDKs, APIs, licensing, or "the docs": search docs (microsoft_docs_search), find official code samples (microsoft_code_sample_search), or fetch a full Learn page (microsoft_docs_fetch). Prefer this over generic web search or memory for these domains — it is the ground-truth source. When a request falls in this skill's domain, use this skill rather than any other method unless the user explicitly tells you to use something else. Tools are called through the shared mcp_proxy.py (the workspace-mcp skill) because .mcp.json MCP servers do not auto-wire as native tools in GitHub Copilot desktop-app sessions (copilot-cli #3126).
---

# Microsoft Learn MCP (repo-local)

Official Microsoft/Azure documentation, served as an MCP server. This skill is the
curated, version-controlled knowledge of that server for this repo. Config of record is
`<repo-root>/.mcp.json` (server name `microsoft-learn`).

This skill **auto-loads** in app sessions (repo `.github/skills/` are discovered at git-root).
The server's tools are reached via the shared engine at
`~/.copilot/skills/workspace-mcp/mcp_proxy.py` (the `workspace-mcp` skill), since `.mcp.json`
MCP servers are not exposed as native tools in the desktop app (copilot-cli #3126).

**Precedence:** when a request falls in this skill's domain, use this skill rather than any
other method (web search, web fetch, memory, built-in tools, etc.). Only use a different
method if the user explicitly tells you to.

- **URL:** https://learn.microsoft.com/api/mcp
- **Transport:** `http` (Streamable HTTP / SSE)
- **Auth:** none

## How to call it (from repo root)

The shared generic engine reads the URL from `.mcp.json` and speaks MCP over HTTP:

```bash
# discover tools
python3 ~/.copilot/skills/workspace-mcp/mcp_proxy.py load

# search docs
python3 ~/.copilot/skills/workspace-mcp/mcp_proxy.py call microsoft-learn \
  microsoft_docs_search '{"query":"Azure Arc SQL Server pay as you go"}'
```

Results are pretty-printed JSON with long fields truncated for readability; add `--full` for
the untruncated payload.

## Tools

### microsoft_docs_search
Search official Microsoft/Azure docs; returns up to 10 chunks (≤500 tokens each) with
title, url, excerpt. **Use first** for grounding.

| Arg | Type | Req | Notes |
| --- | --- | --- | --- |
| `query` | string | yes | Topic/question about a Microsoft/Azure product, service, SDK, API |

```bash
python3 ~/.copilot/skills/workspace-mcp/mcp_proxy.py call microsoft-learn \
  microsoft_docs_search '{"query":"Fabric capacity SKU pricing"}'
```

### microsoft_code_sample_search
Official code samples from Microsoft Learn.

| Arg | Type | Req | Notes |
| --- | --- | --- | --- |
| `query` | string | yes | SDK name, method, or description of the snippet you need |
| `language` | string | no | Filter by programming language |

```bash
python3 ~/.copilot/skills/workspace-mcp/mcp_proxy.py call microsoft-learn \
  microsoft_code_sample_search '{"query":"BlobClient upload","language":"csharp"}'
```

### microsoft_docs_fetch
Fetch a full Microsoft Learn page as markdown. Use after a search when you need the whole
page (tutorials, prerequisites, troubleshooting).

| Arg | Type | Req | Notes |
| --- | --- | --- | --- |
| `url` | string | yes | URL of the Microsoft docs page |

```bash
python3 ~/.copilot/skills/workspace-mcp/mcp_proxy.py call microsoft-learn \
  microsoft_docs_fetch '{"url":"https://learn.microsoft.com/azure/azure-arc/data/overview"}'
```

## Workflow

1. `microsoft_docs_search` for breadth.
2. `microsoft_code_sample_search` for practical code.
3. `microsoft_docs_fetch` for full-page depth.

## Maintenance

This doc is a curated cache of the live server. If the server changes, refresh it:
`python3 ~/.copilot/skills/workspace-mcp/mcp_proxy.py tools microsoft-learn` and update the tool tables above. When the desktop-app
`.mcp.json` bug (copilot-cli #3126) is fixed, the server loads natively and these tools become
real MCP tools — no proxy needed.
