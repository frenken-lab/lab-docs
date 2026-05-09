# Lab-Docs MCP Server

`scripts/mcp_lab_docs.py` is a FastMCP server exposing documentation as queryable tools for any Claude Code session.

## Architecture

At startup, the server:
1. Parses all `docs/**/*.md` into section chunks at H2 boundaries (sub-splits at H3 if >1500 words)
2. Builds a BM25 keyword index over chunk text for ranked search
3. Parses cross-links between pages into an adjacency map
4. Exposes 7 tools via FastMCP stdio transport

## Tools

| Tool | Purpose |
|------|---------|
| `search_docs(query, section?, limit=5)` | BM25-ranked search over H2 chunks. `section` filters by folder (e.g. "ml-workflows") |
| `get_section(page_path, heading)` | Fetch one H2/H3 section by heading text (case-insensitive) |
| `read_page(page_path)` | Full page read (use get_section when possible) |
| `list_pages(category?)` | Nav tree, optionally filtered by section name |
| `find_related(page_path)` | Pages that link to/from this page + same-section siblings |
| `get_summary(page_path)` | Title + heading outline + first sentence per section |
| `troubleshoot(error_text)` | Targeted search biased toward troubleshooting sections + warning/danger admonitions |

## Configuration

Registered in `~/.claude.json` under the `lab-docs` key. Uses `uv run --with` for `mcp[cli]`, `pyyaml`, and `rank-bm25` at runtime.

```bash
# Test
uv run --with "mcp[cli]" --with pyyaml --with rank-bm25 scripts/mcp_lab_docs.py
# Verify in Claude Code: /mcp → "lab-docs" with 7 tools
```
