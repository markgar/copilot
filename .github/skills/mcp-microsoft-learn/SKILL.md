---
name: mcp-microsoft-learn
description: Repo-local asset describing the Microsoft Learn MCP server (https://learn.microsoft.com/api/mcp) and how to call its tools via the bundled mcp_proxy.py. NOTE: repo-local skills do NOT auto-load in GitHub Copilot desktop-app sessions (cwd bug, copilot-cli #3688) — the global `workspace-mcp` skill reads this file on demand. Use to search/fetch official Microsoft & Azure documentation from within this repo.
---

# Microsoft Learn MCP (repo-local)

Official Microsoft/Azure documentation, served as an MCP server. This file is the
curated, version-controlled knowledge of that server for this repo. Config of record
is `<repo-root>/.mcp.json` (server name `microsoft-learn`).

- **URL:** https://learn.microsoft.com/api/mcp
- **Transport:** `http` (Streamable HTTP / SSE)
- **Auth:** none

## How to call it (from repo root)

The bundled generic engine reads the URL from `.mcp.json` and speaks MCP over HTTP:

```bash
# discover tools
python3 .github/skills/mcp-microsoft-learn/mcp_proxy.py load

# search docs
python3 .github/skills/mcp-microsoft-learn/mcp_proxy.py call microsoft-learn \
  microsoft_docs_search '{"query":"Azure Arc SQL Server pay as you go"}'
```

Tool results are printed as text (usually a JSON string of `results[]` with title/url/content).

## Tools

### microsoft_docs_search
Search official Microsoft/Azure docs; returns up to 10 chunks (≤500 tokens each) with
title, url, excerpt. **Use first** for grounding.

| Arg | Type | Req | Notes |
| --- | --- | --- | --- |
| `query` | string | yes | Topic/question about a Microsoft/Azure product, service, SDK, API |

```bash
python3 .github/skills/mcp-microsoft-learn/mcp_proxy.py call microsoft-learn \
  microsoft_docs_search '{"query":"Fabric capacity SKU pricing"}'
```

### microsoft_code_sample_search
Official code samples from Microsoft Learn.

| Arg | Type | Req | Notes |
| --- | --- | --- | --- |
| `query` | string | yes | SDK name, method, or description of the snippet you need |
| `language` | string | no | Filter by programming language |

```bash
python3 .github/skills/mcp-microsoft-learn/mcp_proxy.py call microsoft-learn \
  microsoft_code_sample_search '{"query":"BlobClient upload","language":"csharp"}'
```

### microsoft_docs_fetch
Fetch a full Microsoft Learn page as markdown. Use after a search when you need the whole
page (tutorials, prerequisites, troubleshooting).

| Arg | Type | Req | Notes |
| --- | --- | --- | --- |
| `url` | string | yes | URL of the Microsoft docs page |

```bash
python3 .github/skills/mcp-microsoft-learn/mcp_proxy.py call microsoft-learn \
  microsoft_docs_fetch '{"url":"https://learn.microsoft.com/azure/azure-arc/data/overview"}'
```

## Workflow

1. `microsoft_docs_search` for breadth.
2. `microsoft_code_sample_search` for practical code.
3. `microsoft_docs_fetch` for full-page depth.

## Maintenance

This doc is a curated cache of the live server. If the server changes, refresh it:
`mcp_proxy.py tools microsoft-learn` and update the tool tables above. When the desktop-app
cwd bug (copilot-cli #3126/#3688) is fixed, `.mcp.json` loads natively and these tools become
real MCP tools — no proxy needed.
