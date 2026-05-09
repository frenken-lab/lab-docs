<!-- last-reviewed: 2026-02-26 -->
# GitHub Pages Setup

This guide walks through setting up a documentation website using GitHub Pages — whether for a lab group, a research project, or a personal site. We cover two popular static site generators: **MkDocs Material** (what this site uses) and **Quarto** (great for academic and research content).

---

## Why Have a Documentation Site?

- **Onboarding** — New lab members can get up to speed without asking the same questions repeatedly
- **Reproducibility** — Setup steps, workflows, and conventions are recorded in one place
- **Discoverability** — Public documentation makes your tools and methods findable by the broader research community

---

## Option 1: MkDocs Material

[MkDocs Material](https://squidfunk.github.io/mkdocs-material/) is a documentation framework built on MkDocs. It produces clean, searchable sites from plain Markdown files. This is what the CAR-MSL Lab Setup Guide uses.

### Quick Start

#### 1. Install

```bash
pip install mkdocs-material
```

#### 2. Create a New Project

```bash
mkdocs new my-docs-site
cd my-docs-site
```

This creates a minimal project:

```
my-docs-site/
├── mkdocs.yml       # Configuration
└── docs/
    └── index.md     # Homepage
```

#### 3. Configure `mkdocs.yml`

```yaml
site_name: My Project Docs
site_url: https://username.github.io/my-docs-site/

theme:
  name: material
  features:
    - navigation.tabs
    - navigation.sections
    - search.suggest
    - content.code.copy

nav:
  - Home: index.md
  - Setup: setup.md
  - Usage: usage.md
```

#### 4. Add Pages

Create Markdown files in `docs/` and add them to the `nav:` section in `mkdocs.yml`:

```bash
# Create a new page
echo "# Setup Guide" > docs/setup.md
echo "# Usage" > docs/usage.md
```

#### 5. Preview Locally

```bash
mkdocs serve
# Open http://127.0.0.1:8000
```

The server auto-reloads when you save a file.

#### 6. Deploy with GitHub Actions

Create `.github/workflows/deploy-docs.yml`:

```yaml
name: Deploy Docs

on:
  push:
    branches: [main]
    paths:
      - 'docs/**'
      - 'mkdocs.yml'
      - '.github/workflows/deploy-docs.yml'
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: "pages"
  cancel-in-progress: false

jobs:
  deploy:
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.x'
      - run: pip install mkdocs-material
      - run: mkdocs build --strict
      - uses: actions/upload-pages-artifact@v3
        with:
          path: site/
      - id: deployment
        uses: actions/deploy-pages@v4
```

#### 7. Enable GitHub Pages

Go to your repo's **Settings > Pages** and set the source to **GitHub Actions**.

### Customization Tips

- **Colors** — Set `palette.primary` and `palette.accent` in `mkdocs.yml`, or add a custom CSS file
- **Dark mode** — Add a palette toggle (see this site's `mkdocs.yml` for an example)
- **Plugins** — Add search, minification, or social cards via the `plugins:` section
- **Admonitions** — Enable `admonition` and `pymdownx.details` extensions for callout boxes

!!! tip "Use this site as a template"
    The [lab-setup-guide repo](https://github.com/OSU-CAR-MSL/lab-setup-guide) is a complete working example. Fork it, replace the content, and customize `mkdocs.yml` to get started quickly.

---

## Option 2: Quarto

[Quarto](https://quarto.org/) is a publishing system built for scientific and technical content. It supports Markdown, Jupyter notebooks, and R Markdown, making it ideal for research-oriented sites.

### Quick Start

#### 1. Install

Download Quarto from [quarto.org/docs/get-started](https://quarto.org/docs/get-started/).

#### 2. Create a Website Project

```bash
quarto create project website my-quarto-site
cd my-quarto-site
```

#### 3. Configure `_quarto.yml`

```yaml
project:
  type: website
  output-dir: _site

website:
  title: "My Research Docs"
  navbar:
    left:
      - href: index.qmd
        text: Home
      - href: methods.qmd
        text: Methods

format:
  html:
    theme: cosmo
```

#### 4. Preview Locally

```bash
quarto preview
```

#### 5. Deploy with GitHub Actions

Create `.github/workflows/deploy-quarto.yml`:

```yaml
name: Deploy Quarto Site

on:
  push:
    branches: [main]
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

jobs:
  deploy:
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: quarto-dev/quarto-actions/setup@v2
      - run: quarto render
      - uses: actions/upload-pages-artifact@v3
        with:
          path: _site/
      - id: deployment
        uses: actions/deploy-pages@v4
```

### MkDocs vs Quarto

| Feature | MkDocs Material | Quarto |
|---------|----------------|--------|
| **Content format** | Markdown | Markdown, Jupyter, R Markdown |
| **Best for** | Technical docs, guides | Research papers, notebooks, mixed content |
| **Search** | Built-in, fast | Built-in |
| **Themes** | Material Design, highly polished | Multiple (Bootstrap-based) |
| **Code execution** | No (static code blocks) | Yes (renders notebook output) |
| **Learning curve** | Low | Moderate |
| **Configuration** | `mkdocs.yml` | `_quarto.yml` |

!!! note "Which should you choose?"
    **MkDocs Material** if you're writing documentation, tutorials, or setup guides. **Quarto** if you want to publish Jupyter notebooks, include rendered figures, or mix code output with prose.

### Lab Academic Website Template

The lab maintains a ready-to-use [Quarto academic site template](https://github.com/OSU-CAR-MSL/quarto-academic-site-template) for personal websites. It includes auto-listing pages for research and blog posts, GitHub Actions deployment, and the `cosmo` Bootstrap theme. For a full walkthrough of the template structure, setup steps, and adding content, see the [Personal Website assignment](../assignments/personal-website.md).

---

## GitHub Pages Configuration

### Enabling GitHub Pages

1. Go to your repository on GitHub
2. Navigate to **Settings > Pages**
3. Under **Source**, select **GitHub Actions**
4. Push your workflow file to `main` — the first build will deploy automatically

### Custom Domains

To use a custom domain (e.g., `docs.mylab.org`):

1. Add a `CNAME` file to your site's root (for MkDocs, put it in `docs/CNAME`)
2. Configure DNS with your domain provider (CNAME record pointing to `username.github.io`)
3. In **Settings > Pages**, enter your custom domain and enable HTTPS

### Organization Sites

For a GitHub organization (like `OSU-CAR-MSL`):

- A repo named `orgname.github.io` deploys to `https://orgname.github.io/`
- Any other repo deploys to `https://orgname.github.io/repo-name/`

---

## CI/CD Best Practices

### Path Filtering

Only trigger builds when documentation files change:

```yaml
on:
  push:
    branches: [main]
    paths:
      - 'docs/**'
      - 'mkdocs.yml'
      - '.github/workflows/deploy-docs.yml'
```

### Strict Mode

Use strict mode to catch broken links during CI:

```bash
mkdocs build --strict    # MkDocs
quarto render --strict   # Quarto (not available by default, use link checkers)
```

### Caching

Speed up builds by caching Python packages:

```yaml
- uses: actions/setup-python@v5
  with:
    python-version: '3.x'
    cache: 'pip'
```

### Concurrency

Prevent conflicting deployments:

```yaml
concurrency:
  group: "pages"
  cancel-in-progress: false
```

---

## Next Steps

- [GitHub Actions & CI/CD](../github/github-actions-ci-cd.md) — Testing, linting, and automation beyond deployment
- [Contributing Guide](how-this-site-works.md) — Architecture and how to add pages to the CAR-MSL documentation site
- [MkDocs Material docs](https://squidfunk.github.io/mkdocs-material/) — Full reference for the MkDocs Material theme
- [Quarto docs](https://quarto.org/docs/websites/) — Quarto website documentation
