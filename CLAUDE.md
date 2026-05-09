# Lab Setup Guide

MkDocs Material documentation site for the OSU CAR Mobility Systems Lab. All content is Markdown in `docs/`. Deployed automatically to GitHub Pages on push to `main`.

**Live site:** https://osu-car-msl.github.io/lab-setup-guide/

## Commands

```bash
pip install -r requirements-docs.txt           # Install deps
mkdocs serve                                    # Local dev server (auto-reload)
mkdocs build --strict                           # Production build (CI)
python scripts/check-freshness.py --max-age-days 365  # Content freshness
python scripts/check-duplication.py             # SSOT duplication check
```

No tests or linters. `--strict` in CI catches broken links and config errors.

## Architecture

```
lab-setup-guide/
├── mkdocs.yml                  # Nav, theme, extensions, plugins
├── requirements-docs.txt       # Python deps (CI cache key)
├── overrides/main.html         # Announcement bar override
├── overrides/404.html          # Custom 404 page
├── docs/                       # 33 Markdown pages
│   ├── index.md, tags.md
│   ├── includes/abbreviations.md
│   ├── getting-started/        # 5 pages
│   ├── osc-basics/             # 6 pages
│   ├── working-on-osc/         # 5 pages
│   ├── ml-workflows/           # 7 pages
│   ├── contributing/           # 4 pages
│   ├── assignments/            # 6 pages
│   └── resources/              # 5 pages (incl. templates, presentations index)
├── presentations/              # Quarto RevealJS slide decks (outside docs/)
│   └── osc-overview/           # OSC & HPC onboarding slides
├── scripts/                    # check-freshness.py, check-duplication.py, mcp_lab_docs.py
└── .github/workflows/          # deploy-docs.yml, link-check.yml
```

## Rules (auto-loaded from `.claude/rules/`)

- `content-conventions.md` — SSOT rules, canonical page locations, freshness, adding pages
- `mcp-server.md` — Lab-docs MCP server config and tools

## CI / Deployment

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `deploy-docs.yml` | Push to `main` | `mkdocs build --strict` → GitHub Pages |
| `link-check.yml` | Push + weekly cron | Lychee links, freshness audit, SSOT check |

## Assignments

Assignment pages in `docs/assignments/`. Pattern: metadata table, multi-part structure, admonitions, task-list checklists, troubleshooting table.

> Cross-repo propagation: See `~/.claude/rules/cross-repo-propagation.md`
