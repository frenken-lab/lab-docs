<!-- last-reviewed: 2026-02-26 -->
# Contributing Guide

This site is built with [MkDocs](https://www.mkdocs.org/) using the [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/) theme. It turns plain markdown files into a professional documentation website, hosted for free on GitHub Pages.

## Architecture Overview

```
lab-setup-guide/
├── mkdocs.yml                  # Site configuration (theme, nav, plugins)
├── docs/                       # All markdown content lives here
│   ├── index.md                # Homepage
│   ├── getting-started/        # VS Code setup guides
│   ├── osc-basics/             # OSC account, SSH, remote dev, file transfer
│   ├── working-on-osc/         # Jobs, environments, orchestration
│   ├── ml-workflows/           # PyTorch, ML workflow, GPU computing
│   ├── contributing/           # This guide and GitHub Pages setup
│   ├── assignments/            # Hands-on tasks for new lab members
│   ├── resources/              # Troubleshooting and useful links
│   └── stylesheets/
│       └── extra.css           # Custom OSU scarlet branding
└── .github/
    └── workflows/
        ├── deploy-docs.yml     # Automatic build & deploy pipeline
        └── link-check.yml      # Weekly link checker & freshness audit
```

## How Deployment Works

Every time you push changes to the `main` branch, the following happens automatically:

```
git push origin main
       │
       ▼
GitHub detects the push
       │
       ▼
GitHub Actions workflow triggers
(only if docs/ or mkdocs.yml changed)
       │
       ▼
A cloud server spins up and:
  1. Checks out the repo
  2. Installs Python + mkdocs-material
  3. Runs "mkdocs build --strict"
  4. Uploads the built site
       │
       ▼
GitHub Pages serves the site at:
osu-car-msl.github.io/lab-setup-guide/
```

You never need to manually build or upload anything. Just push markdown and the site updates in about 45 seconds.

A separate CI workflow (`link-check.yml`) runs on each push and weekly to check external links, content freshness (pages not reviewed in 12+ months), and SSOT duplication.

## Adding a New Page

### 1. Create the file

Create a `.md` file in the appropriate `docs/` subfolder. Every page should start with a level-1 heading:

```markdown
# My New Guide

A brief introduction to what this page covers.

## First Section

Your content here.
```

!!! important "Content freshness tag required"
    Every page must have `<!-- last-reviewed: YYYY-MM-DD -->` as its **very first line** (before the heading). Use today's date. CI will flag pages that haven't been reviewed in 12 months.

    ```markdown
    <!-- last-reviewed: 2026-02-26 -->
    # My New Guide
    ```

### 2. Add it to the navigation

Open `mkdocs.yml` and add your page to the `nav:` section:

```yaml
nav:
  - Working on OSC:
    - My New Guide: working-on-osc/my-new-guide.md   # path relative to docs/
```

### 3. Validate

```bash
mkdocs build --strict
```

The `--strict` flag catches broken links, missing nav entries, and other issues that would fail CI.

### 4. Commit and push

```bash
git add docs/working-on-osc/my-new-guide.md mkdocs.yml
git commit -m "Add guide for my-new-guide"
git push origin main
# Site updates at osu-car-msl.github.io/lab-setup-guide/ in ~45 seconds
```

!!! warning "File paths in `nav:` are relative to `docs/`"
    `docs/working-on-osc/my-guide.md` is listed as `working-on-osc/my-guide.md` in `mkdocs.yml`.

## Local Preview

Run `mkdocs serve` from the repo root to start a local development server:

```bash
# Install dependencies (one time)
pip install -r requirements-docs.txt

# Start local server with live reload
mkdocs serve
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000). The server auto-reloads when you save — no commit needed.

| What you want to do | Command | Commit needed? |
|---|---|---|
| Preview changes locally | `mkdocs serve` | No |
| Check for broken links | `mkdocs build --strict` | No |
| Update the live site | `git push origin main` | Yes |

## Key Files

### `mkdocs.yml`

The main configuration file at the repo root. It controls:

- **`site_name`** — The title shown in the header
- **`theme`** — Material theme settings, color palette, features like dark mode
- **`nav`** — The sidebar navigation structure (which pages appear and in what order)
- **`markdown_extensions`** — Extra features like code highlighting, admonitions, tabs
- **`plugins`** — Search, HTML minification

### `docs/` folder

Every `.md` file in this folder becomes a page on the site. The file path determines the URL:

| File path | URL |
|-----------|-----|
| `docs/index.md` | `/lab-setup-guide/` |
| `docs/getting-started/vscode-setup.md` | `/lab-setup-guide/getting-started/vscode-setup/` |

## Markdown Quick Reference

### Admonitions

```markdown
!!! tip "Helpful hint"
    This is a tip callout box.

!!! warning
    This is a warning.
```

### Code blocks with syntax highlighting

````markdown
```python
import torch
print(torch.cuda.is_available())
```
````

### Tabbed content

```markdown
=== "Linux"
    ```bash
    ssh user@pitzer.osc.edu
    ```

=== "Windows"
    ```bash
    ssh user@pitzer.osc.edu
    ```
```

### Other features

- **Keyboard keys:** `++ctrl+c++`
- **Task lists:** `- [x] Done` / `- [ ] Todo`
- **Mermaid diagrams:** fenced with ` ```mermaid `

## Checklist

Before pushing a new page:

- [ ] File is in the correct `docs/` subfolder
- [ ] First line is `<!-- last-reviewed: YYYY-MM-DD -->` with today's date
- [ ] File starts with a `# Title` heading
- [ ] Page is added to `nav:` in `mkdocs.yml`
- [ ] Links to other pages use correct relative paths
- [ ] Code blocks specify the language for syntax highlighting
- [ ] `mkdocs build --strict` passes
- [ ] `python scripts/check-freshness.py --max-age-days 365` passes

## Related Guides

- [Git Fundamentals](../github/git-fundamentals.md) — Core Git commands and mental model
- [Issues, PRs & Code Review](github-issues-and-prs.md) — Filing issues, opening pull requests, and reviewing code
- [Project Management](github-projects.md) — GitHub Projects boards, workflows, and automation
- [GitHub Pages Setup](github-pages-setup.md) — Setting up MkDocs or Quarto documentation sites
