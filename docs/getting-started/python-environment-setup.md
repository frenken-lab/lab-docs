<!-- last-reviewed: 2026-02-26 -->
# Python Environment Setup

This guide walks you through setting up Python development environments for lab work. The approach uses **two environments** tuned for different workloads:

| Environment | Where | Package Manager | Use Case |
|-------------|-------|----------------|----------|
| **Local (WSL)** | `~/projects/` on WSL native filesystem | **`uv`** | Docs, light dev, scripting, Claude Code |
| **OSC** | `~/venvs/` or project `.venv/` on OSC | **`uv`** or **`pip` + `venv`** (via `module load`) | ML training, torch-geometric, CUDA workloads |

!!! info "uv works on both, with a caveat on OSC"
    **`uv`** is 10-100x faster than pip and handles everything you need for local work. It **also works on OSC**, but you must use OSC's system Python (`uv venv --python /apps/python/3.12/bin/python3`) instead of uv's managed Python downloads, which can segfault on RHEL 9. PyTorch from PyPI bundles NVIDIA libraries, so `module load cuda` is not needed. See [Environment Management](../working-on-osc/osc-environment-management.md) for the full OSC setup.

---

## Step 1: Set Up WSL (Windows Only)

If you're on Windows, install WSL2 first — see the [WSL Setup Guide](wsl-setup.md). That page covers installation, filesystem migration, and VS Code integration.

---

## Step 2: Bootstrap WSL Python Tooling

Install the minimum system packages, then let `uv` manage everything else.

```bash
# Install system prerequisites
sudo apt update && sudo apt install -y python3-pip python3-venv

# Install uv (Astral's fast Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Restart shell or source the path (the installer adds ~/.local/bin to PATH)
source ~/.bashrc

# Verify
uv --version
```

### What `uv` replaces locally

| Traditional Tool | `uv` Equivalent | Purpose |
|-----------------|-----------------|---------|
| `pip install` | `uv pip install` | Install packages |
| `python -m venv` | `uv venv` | Create virtual environments |
| `pyenv` | `uv python install 3.12` | Manage Python versions |
| `pip-tools` | `uv lock` / `uv sync` | Lockfiles and reproducibility |

---

## Step 3: Set Up Local Project Environments

### For this docs site (lab-setup-guide)

```bash
cd ~/projects/lab-setup-guide

# Create a venv managed by uv
uv venv

# Activate it
source .venv/bin/activate

# Install docs dependencies
uv pip install mkdocs-material mkdocs-minify-plugin

# Verify the site builds
mkdocs serve   # visit http://127.0.0.1:8000
```

### For a general Python project

```bash
cd ~/projects/my-research

# Initialize uv project (creates pyproject.toml if missing)
uv init

# Add dependencies
uv add numpy pandas matplotlib

# Run inside the venv without manually activating
uv run python my_script.py
```

### The `.venv/` convention

`uv` creates a `.venv/` directory inside each project (not a central location). This is standard Python convention and works well with VS Code's auto-detection of virtual environments.

!!! warning "Don't commit `.venv/`"
    The `.venv/` directory should be in your `.gitignore`. Each machine builds its own venv from the lockfile.

### Pre-commit hooks

Many lab repos include a `.pre-commit-config.yaml` that runs linters (e.g. `ruff`) automatically before each commit. After cloning a repo, install the hooks once:

```bash
# Install pre-commit (if not already available)
uv pip install pre-commit

# Activate hooks for this repo
pre-commit install
```

After this, every `git commit` will run the configured checks. If a check fails, the commit is blocked and you'll see what to fix. This catches lint and formatting issues before they reach CI.

!!! tip "First run is slow"
    The first commit after `pre-commit install` downloads and caches the hook environments. Subsequent commits are fast.

---

## Step 4: Git Line-Ending Configuration

WSL uses LF line endings while Windows uses CRLF. Setting `core.autocrlf=input` (converts CRLF to LF on commit) is a good start. For extra safety, add a `.gitattributes` file to each repo:

```gitattributes
# Normalize line endings
* text=auto
*.sh text eol=lf
*.py text eol=lf
*.md text eol=lf
*.yml text eol=lf
*.yaml text eol=lf
```

This ensures consistent LF endings regardless of which machine or OS commits the files. A `.gitattributes` file has been added to this repository.

To set `autocrlf` globally if you haven't already:

```bash
git config --global core.autocrlf input
```

---

## Step 5: OSC Environments

On OSC, you can use either `pip` + `venv` (traditional) or `uv` (faster). Both work, but `uv` requires using OSC's system Python explicitly.

For full details on modules, venvs, and uv on OSC, see [OSC Environment Management](../working-on-osc/osc-environment-management.md).

---

## Step 6: Multi-Device Workflow

If you work on multiple machines (desktop and laptop), keep them in sync:

1. Both machines use WSL with code in `~/projects/`
2. Sync via `git push` / `git pull` (not file copying)
3. `.gitattributes` in each repo ensures consistent line endings
4. `uv sync` on each machine recreates the same venv from the lockfile
5. `.venv/` is gitignored — each machine builds its own

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#e8f4fd', 'primaryTextColor': '#1a1a1a', 'lineColor': '#555'}}}%%
graph LR
    A["fa:fa-desktop Desktop WSL"]:::process -->|git push| B(("fa:fa-cloud GitHub")):::external
    B -->|git pull| C["fa:fa-laptop Laptop WSL"]:::process
    C -->|git push| B
    B -->|git pull| A
    A -.->|uv sync| D@{ shape: cyl, label: "fa:fa-box .venv/" }:::data
    C -.->|uv sync| E@{ shape: cyl, label: "fa:fa-box .venv/" }:::data

    classDef process fill:#e8f4fd,stroke:#3b82f6,color:#1a1a1a,stroke-width:2px
    classDef external fill:#ede9fe,stroke:#7c3aed,color:#1a1a1a,stroke-width:2px
    classDef data fill:#d1fae5,stroke:#059669,color:#1a1a1a,stroke-width:2px
```

---

## Summary of What Gets Installed

| Tool | Install Method | Purpose |
|------|---------------|---------|
| `python3-pip` | `apt` | System pip (bootstrap only) |
| `python3-venv` | `apt` | System venv support |
| `uv` | `curl` installer | Primary local package manager |
| `mkdocs-material` | `uv pip install` in project `.venv/` | Docs site |

---

## Verification

After completing all steps, confirm everything works:

```bash
# Confirm you're in WSL native filesystem
pwd
# Should show ~/projects/..., NOT /mnt/c/...

# Confirm uv works
uv --version

# Confirm docs site builds
cd ~/projects/lab-setup-guide
source .venv/bin/activate
mkdocs build --strict
mkdocs serve   # visit http://127.0.0.1:8000

# Confirm git is clean (no phantom permission changes)
git status
# Should be fast, no spurious modifications
```

---

## What This Does NOT Cover

These topics are out of scope for local development setup:

- **Local CUDA/GPU setup** — ML training happens on OSC, not locally
- **Conda** — `uv` replaces this for local work; OSC uses modules instead
- **Docker** — Not needed for the current workflow

---

## Next Steps

- Set up [AI Coding Assistants](ai-coding-assistants.md) for VS Code
- Learn about [OSC Environment Management](../working-on-osc/osc-environment-management.md)
- Review [PyTorch Setup on OSC](../ml-workflows/pytorch-setup.md)
