# Content Conventions

**Single source of truth.** Every topic lives on one page. Other pages link to the canonical page — never copy-paste content.

**Lean pages.** Each page covers its own topic only. If a section grows beyond scope, move it to its canonical page with a cross-link.

**Cross-links over duplication.** One- or two-line mention plus a Markdown link:
```markdown
For partition details, see the [Clusters Overview](../osc-basics/osc-clusters-overview.md).
```

**Content freshness.** Every `.md` page must have `<!-- last-reviewed: YYYY-MM-DD -->` within its first 10 lines (after any YAML frontmatter). Update when you meaningfully review or edit. CI flags pages older than 12 months.

**No link dumps.** Only OSC-specific portals, lab resources, and hard-to-find references. Skip generic links (Python docs, ML courses, framework homepages).

**Practical, not encyclopedic.** Include concrete commands, code snippets, and job script templates. Skip generic explanations covered by official docs.

## Canonical Locations

| Topic | Canonical Page |
|-------|---------------|
| WSL2 installation | `getting-started/wsl-setup.md` |
| Cluster specs, partitions | `osc-basics/osc-clusters-overview.md` |
| SSH keys and config | `osc-basics/osc-ssh-connection.md` |
| File transfer | `osc-basics/osc-file-transfer.md` |
| OSC OnDemand | `osc-basics/osc-ondemand.md` |
| VS Code extensions | `getting-started/vscode-extensions.md` |
| Modules, venvs, uv | `working-on-osc/osc-environment-management.md` |
| SLURM jobs | `working-on-osc/osc-job-submission.md` |
| Pipeline orchestration | `working-on-osc/pipeline-orchestration.md` |
| PyTorch setup | `ml-workflows/pytorch-setup.md` |
| PyG setup | `ml-workflows/pyg-setup.md` |
| RAPIDS AI, GPU preprocessing | `ml-workflows/rapids-gpu-preprocessing.md` |
| Experiment tracking | `ml-workflows/data-experiment-tracking.md` |
| DuckDB analytics, Parquet datalake | `ml-workflows/duckdb-analytics.md` |
| Hugging Face Spaces deployment | `ml-workflows/huggingface-spaces.md` |
| Agent workflows, MCP, skills, hooks | `getting-started/agent-workflows.md` |
| Student site showcase | `assignments/site-showcase.md` |
| Typst CV guide | `assignments/typst-cv-guide.md` |
| Publishing blog posts, Quarto YAML, categories taxonomy | `assignments/publishing-guide.md` |
| Git fundamentals, core commands | `github/git-fundamentals.md` |
| Repository setup, branch protection | `github/repository-setup.md` |
| SSH keys for GitHub, gh CLI auth, PATs | `github/ssh-and-authentication.md` |
| GitHub Actions, CI/CD workflows | `github/github-actions-ci-cd.md` |
| Git troubleshooting, merge conflicts, recovery | `github/git-troubleshooting.md` |
| Issues, PRs, code review, forks | `contributing/github-issues-and-prs.md` |
| GitHub Projects, project management | `contributing/github-projects.md` |
| Docs concept map, knowledge graph | `resources/concept-map.md` |
| Presentation slides index | `resources/presentations.md` |
| Lab templates index | `resources/templates.md` |

## Markdown Features Available

Admonitions (`!!! note/tip/warning/danger`), tabbed content (`=== "Tab"`), fenced code with copy buttons, Mermaid diagrams, keyboard keys (`++ctrl+c++`), task lists, abbreviation tooltips, tags, image lightbox, social cards, breadcrumbs, git revision dates.

## Adding a New Page

1. Create `.md` in appropriate `docs/` subfolder
2. Add `<!-- last-reviewed: YYYY-MM-DD -->` within the first 10 lines (after any YAML frontmatter)
3. Add to `nav:` in `mkdocs.yml`
4. Check canonical locations — cross-link, don't duplicate
5. Verify: `mkdocs build --strict && python scripts/check-freshness.py && python scripts/check-duplication.py`
