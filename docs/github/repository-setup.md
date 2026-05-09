---
status: new
tags:
  - Git
  - GitHub
  - repository
---
<!-- last-reviewed: 2026-03-30 -->
# Repository Setup

| | |
|---|---|
| **Audience** | All lab members |
| **Prerequisites** | GitHub account, `gh` CLI authenticated ([setup guide](ssh-and-authentication.md)) |

---

## Creating a Repository

### From Scratch (CLI)

The `gh repo create` command creates a repository on GitHub and optionally clones it locally in one step:

```bash
gh repo create my-project --public --clone --gitignore Python --license MIT
```

Key flags:

- `--public` / `--private` — visibility (use `--private` for unpublished research)
- `--clone` — clones the new repo into the current directory after creation
- `--gitignore Python` — adds GitHub's Python `.gitignore` template
- `--license MIT` — adds the MIT license file

If you prefer guided prompts instead of memorizing flags, run it with no arguments:

```bash
gh repo create
```

This walks you through each option interactively.

### From a Template

If you are starting from an existing template repository:

```bash
gh repo create my-new-project --template owner/template-repo --clone --public
```

This copies the template's file structure into a fresh repository with no shared commit history.

!!! tip "Lab templates"
    Lab starter templates are listed on the [Templates](../resources/templates.md) page. Check there before creating a repo from scratch — a template may save significant setup time.

### Cloning an Existing Repository

=== "SSH (Recommended)"

    ```bash
    git clone git@github.com:owner/repo.git
    ```

=== "HTTPS"

    ```bash
    git clone https://github.com/owner/repo.git
    ```

!!! info "Why SSH?"
    SSH is preferred because it never prompts for a password after your key is set up. See [SSH & Authentication](ssh-and-authentication.md) for key setup instructions.

## Essential Repository Files

### README.md

Every repository needs a README. At minimum, include:

- Project name and a one-line description
- Setup instructions (how to clone and install dependencies)
- A usage example
- License

Minimal template:

````markdown
# Project Name

One-line description of what this project does.

## Setup

```bash
git clone git@github.com:owner/project.git
cd project
uv sync
```

## Usage

```bash
python main.py --config config.yaml
```

## License

MIT
````

### .gitignore

GitHub's Python template covers most ML research needs. Add project-specific entries for files that should never be committed:

```gitignore
# Large datasets
data/

# Training outputs
outputs/

# Experiment tracking
wandb/

# Model checkpoints
*.pt
*.pth
```

!!! tip "Start with the template"
    Use `gh repo create --gitignore Python` to get GitHub's Python template automatically. Then add your project-specific patterns on top.

For `.gitignore` syntax and common patterns, see [Git Fundamentals](git-fundamentals.md#gitignore).

### LICENSE

Without a license file, your code is technically "all rights reserved" — others cannot legally use or modify it, even if the repo is public.

Lab recommendations:

- **MIT** — use this for open research code. It is permissive, simple, and widely understood.
- **Apache 2.0** — use this if patent protection matters (includes an explicit patent grant).

Don't overthink license choice for research repos. MIT is the safe default.

### .gitattributes

This file ensures consistent line endings and diff behavior across platforms (Windows, macOS, Linux). This matters most when lab members use both WSL and native Linux.

For line-ending configuration details on Windows/WSL, see [Python Environment Setup](../getting-started/python-environment-setup.md).

## Repository Settings

### Branch Protection Rules

Branch protection prevents accidental pushes to `main` and enforces code review before merging.

Step-by-step setup:

1. Go to your repository on GitHub
2. Navigate to **Settings** → **Branches** → **Add branch protection rule**
3. Set branch name pattern to `main`
4. Enable these settings:
    - [x] Require a pull request before merging
    - [x] Require approvals: **1**
    - [x] Require status checks to pass before merging (if you have CI)
    - [x] Do not allow bypassing the above settings
5. Click **Create**

!!! warning "Solo projects"
    For solo projects (e.g., thesis work), branch protection is optional. It is most valuable when 2+ people contribute to the same repository. If you are the only contributor, enforcing pull requests adds overhead without benefit.

### Default Branch

GitHub defaults to `main` — keep this convention for all lab repositories.

If you encounter a repo that still uses `master`:

1. Go to **Settings** → **Branches**
2. Click the rename icon next to the default branch
3. Rename `master` to `main`

GitHub automatically updates existing pull requests and redirects branch references.

### GitHub Features Toggle

Under **Settings** → **General** → **Features**, configure which GitHub features are enabled:

- **Issues** — keep enabled. Use for tracking bugs, tasks, and feature requests.
- **Wiki** — disable. Use the repo's `docs/` folder or a MkDocs site instead.
- **Projects** — enable if you are using [GitHub Projects](../contributing/github-projects.md) for task tracking on this repo.
- **Discussions** — optional. Useful for open-ended questions in larger projects with multiple contributors.

## Repository Maintenance

### Keeping Forks in Sync

If you forked a lab repository, you need to periodically pull in changes from the original (upstream) repo.

```bash
git remote add upstream git@github.com:original-owner/repo.git
git fetch upstream
git merge upstream/main
git push origin main
```

For the full step-by-step fork sync workflow, see the [Contributing guide](../contributing/github-issues-and-prs.md).

### Archiving a Repository

When a project is complete, no longer maintained, or superseded by another repo:

1. Go to **Settings** → scroll to **Danger Zone**
2. Click **Archive this repository**

The repo becomes read-only but remains visible and cloneable. This signals to others that no further development is planned.

## Related Guides

- [Git Fundamentals](git-fundamentals.md) — core Git commands and mental model
- [SSH & Authentication](ssh-and-authentication.md) — set up keys and the `gh` CLI
- [Issues, PRs & Code Review](../contributing/github-issues-and-prs.md) — the collaboration workflow
- [GitHub Projects](../contributing/github-projects.md) — project management with boards and tracking
- [Templates](../resources/templates.md) — lab starter templates
