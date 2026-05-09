<!-- last-reviewed: 2026-04-16 -->
# Assignment 3a: Package Management Concepts

|                    |                                                              |
| ------------------ | ------------------------------------------------------------ |
| **Author**         | Robert Frenken                                               |
| **Estimated time** | 3--4 hours                                                   |
| **Prerequisites**  | Assignment 1 completed, Python basics                        |

!!! abstract "What you'll learn"
    Why package management exists, how dependency resolution works, and when to use **pip** vs **conda** vs **uv**. By the end you'll be able to create reproducible Python environments for any project — and you'll understand why that's a solved problem you no longer have to re-solve.

!!! info "3a and 3b are assigned together"
    You have **2 weeks** to complete both. 3a is conceptual (package management). [3b is hands-on coding (a neural network from scratch)](neural-network-from-scratch.md). Both include a blog post deliverable.

---

## Part 0: What is a Package?

Python's **standard library** ships with the language — modules like `os`, `json`, `math`, and `pathlib` are always available. But most real projects need **third-party packages** from [PyPI](https://pypi.org/) (the Python Package Index), a public repository of over 500,000 packages.

When you run `pip install requests`, pip:

1. Queries PyPI for the `requests` package
2. Downloads a **wheel** (`.whl`) — a pre-built archive of Python code
3. Installs it into your environment's `site-packages/` directory
4. Resolves and installs any **dependencies** that `requests` itself needs

### Task

Create and activate a fresh virtual environment, then count what's already installed:

=== "macOS / Linux / WSL"

    ```bash
    python -m venv scratch-env
    source scratch-env/bin/activate
    pip list
    ```

=== "Windows (Git Bash)"

    ```bash
    python -m venv scratch-env
    source scratch-env/Scripts/activate
    pip list
    ```

You should see only `pip` and `setuptools` — a clean slate. Now install one package and count again:

```bash
pip install requests
pip list
```

!!! question "How many packages are installed now?"
    You asked for 1 package but got several. Where did the extras come from? Keep this question in mind as you continue.

When you're done exploring, deactivate and delete the scratch environment:

```bash
deactivate
rm -rf scratch-env
```

- [ ] Created a fresh venv and confirmed the minimal package list
- [ ] Installed `requests` and counted the extras



---

## Part 1: Why Package Management Matters

### The dependency chain problem

When you install a package, it brings its own dependencies — and those dependencies have dependencies too. This is called a **dependency tree**.

Here's what happens when you install `requests`:

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#e8f4fd', 'primaryTextColor': '#1a1a1a', 'lineColor': '#555'}}}%%
graph TD
    A["fa:fa-box requests"]:::process --> B["charset-normalizer"]:::data
    A --> C["idna"]:::data
    A --> D["urllib3"]:::data
    A --> E["certifi"]:::data

    classDef process fill:#e8f4fd,stroke:#3b82f6,color:#1a1a1a,stroke-width:2px
    classDef data fill:#d1fae5,stroke:#059669,color:#1a1a1a,stroke-width:2px
```

Four dependencies — manageable. Now look at what happens with a large ML framework like PyTorch:

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#e8f4fd', 'primaryTextColor': '#1a1a1a', 'lineColor': '#555'}}}%%
graph TD
    A["fa:fa-fire torch"]:::process --> B["filelock"]:::data
    A --> C["typing-extensions"]:::data
    A --> D["sympy"]:::data
    A --> E["networkx"]:::data
    A --> F["jinja2"]:::data
    A --> G["fsspec"]:::data
    A --> H["fa:fa-microchip nvidia-cuda-runtime-cu12"]:::external
    A --> I["fa:fa-microchip nvidia-cudnn-cu12"]:::external
    A --> J["fa:fa-microchip nvidia-cublas-cu12"]:::external
    A --> K["fa:fa-microchip nvidia-nccl-cu12"]:::external
    A --> L["triton"]:::data
    D --> M["mpmath"]:::subdata
    F --> N["MarkupSafe"]:::subdata
    I --> J

    classDef process fill:#e8f4fd,stroke:#3b82f6,color:#1a1a1a,stroke-width:2px
    classDef data fill:#d1fae5,stroke:#059669,color:#1a1a1a,stroke-width:2px
    classDef external fill:#ede9fe,stroke:#7c3aed,color:#1a1a1a,stroke-width:2px
    classDef subdata fill:#ecfdf5,stroke:#059669,color:#1a1a1a,stroke-width:2px
```

One `pip install torch` pulls in **14+ packages** including GPU libraries, a symbolic math engine, and a template language. Every one of those packages has its own version requirements, and they all have to be compatible with each other.

??? abstract "How dependency resolution actually works"
    When you `pip install torch`, pip does a depth-first traversal of the dependency graph, collecting every package `torch` needs, then every package *those* need, and so on. At each step it has to pick a version that satisfies **all** constraints — if `torch` needs `numpy >= 1.24` and another already-installed package needs `numpy < 2`, the resolver has to find a version in the intersection.

    Modern resolvers (pip ≥ 20.3, uv, conda) use **backtracking** or **SAT solvers**: if they hit a dead end, they undo recent choices and try different versions. When no valid combination exists, you get a `ResolutionImpossible` error — and the only fix is relaxing a constraint somewhere.

### Why this matters

Imagine Project A needs `numpy==1.26.4` and Project B needs `numpy==2.0.0`. If both are installed into the same Python environment, one project breaks. This is the **version conflict problem**, and it's the core reason package management tools exist.

!!! question "Reflection"
    What could go wrong if two projects share a single Python installation and one of them upgrades a shared dependency?

- [ ] Dependency-tree reasoning makes sense to you
- [ ] Part 1 reflection answered

---

## Part 2: Virtual Environments

A **virtual environment** (venv) is an isolated Python installation. Each venv has its own `site-packages/` directory, so packages installed in one venv don't affect another.

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#e8f4fd', 'primaryTextColor': '#1a1a1a', 'lineColor': '#555'}}}%%
graph LR
    subgraph "System Python"
        SYS["fa:fa-computer python3.12"]:::system
    end
    subgraph "Project A venv"
        A_PY["python3.12"]:::processA
        A_NP["numpy 1.26.4"]:::processA
        A_PD["pandas 2.1.5"]:::processA
    end
    subgraph "Project B venv"
        B_PY["python3.12"]:::processB
        B_NP["numpy 2.0.0"]:::processB
        B_SK["scikit-learn 1.5.0"]:::processB
    end
    SYS -.->|"venv created from"| A_PY
    SYS -.->|"venv created from"| B_PY

    classDef system fill:#f3f4f6,stroke:#6b7280,color:#1a1a1a,stroke-width:2px
    classDef processA fill:#e8f4fd,stroke:#3b82f6,color:#1a1a1a,stroke-width:2px
    classDef processB fill:#d1fae5,stroke:#059669,color:#1a1a1a,stroke-width:2px
```

Each project gets exactly the versions it needs. No conflicts.

### Hands-on: prove isolation works

Create two virtual environments with different numpy versions:

```bash
# Environment 1: numpy 1.x
python -m venv env-numpy1
source env-numpy1/bin/activate
pip install "numpy>=1.26,<2"
python -c "import numpy; print(f'env-numpy1: numpy {numpy.__version__}')"
deactivate

# Environment 2: numpy 2.x
python -m venv env-numpy2
source env-numpy2/bin/activate
pip install "numpy>=2.0,<3"
python -c "import numpy; print(f'env-numpy2: numpy {numpy.__version__}')"
deactivate
```

Verify that each environment has its own version. Then clean up:

```bash
rm -rf env-numpy1 env-numpy2
```

!!! success "What just happened"
    You created two fully independent Python installations that share nothing but the interpreter. Installing a new package in one has zero effect on the other. This is what lets a lab machine host 20 projects without any of them breaking each other.

!!! question "Reflection"
    Why not install everything into the system Python? What problems would that cause on a shared system like OSC where multiple users and projects coexist?

- [ ] Two isolated venvs created with different numpy versions
- [ ] Part 2 reflection answered

---

## Part 3: Package Managers Compared

The lab uses three package managers. Each has different strengths:

| Feature | pip | conda | uv |
|---------|-----|-------|----|
| **Source** | PyPI (Python packages) | conda-forge / Anaconda (any language) | PyPI (Python packages) |
| **Speed** | Moderate | Slow | Very fast (10--100x pip) |
| **Resolver** | Backtracking (since pip 20.3) | SAT solver | SAT solver |
| **Lock files** | No built-in (`pip freeze` is approximate) | `environment.yml` (not locked) | `uv.lock` (deterministic) |
| **Non-Python packages** | No | Yes (CUDA, MKL, compilers) | No |
| **Lab usage** | Legacy projects, quick installs | CUDA toolkit, complex C dependencies | New projects, daily development |

### When to use each

- **uv** — Default choice for new projects. Fast, deterministic, excellent error messages.
- **conda** — When you need non-Python dependencies (CUDA, MKL, system libraries) that aren't available as pip wheels.
- **pip** — When a package is only on PyPI and not on conda-forge, or you're working in a codebase that hasn't migrated yet.

For details on how we use these on OSC, see the [Environment Management](../working-on-osc/osc-environment-management.md) guide and the [Python Environment Setup](../getting-started/python-environment-setup.md) guide.

### Hands-on: compare pip and uv speed

Install the same set of packages with pip and uv, then compare the time:

=== "pip"

    ```bash
    python -m venv pip-test
    source pip-test/bin/activate
    time pip install requests flask pandas numpy
    deactivate
    rm -rf pip-test
    ```

=== "uv"

    ```bash
    # Install uv first if needed:
    # curl -LsSf https://astral.sh/uv/install.sh | sh
    uv venv uv-test
    source uv-test/bin/activate
    time uv pip install requests flask pandas numpy
    deactivate
    rm -rf uv-test
    ```

Record the `real` time from each `time` command.

??? example "What you'll probably see"
    On a recent laptop with warm caches, rough numbers:

    | Tool | Time |
    |------|------|
    | `pip install` | 15–40s |
    | `uv pip install` | 1–3s |

    The gap is bigger the first time (cold cache) and for larger package sets (e.g., pytorch + its dependencies). uv also produces cleaner error messages when there's a conflict.

!!! question "Reflection"
    Conda can install non-Python packages like CUDA libraries. Why is this useful? When would pip or uv alone not be enough?

- [ ] Speed comparison run with times recorded
- [ ] Part 3 reflection answered

---

## Part 4: Requirements Files

A **requirements file** records exactly which packages (and versions) a project needs, so anyone can recreate the environment.

### Two approaches

**`pip freeze`** — captures everything currently installed, including transitive dependencies:

```bash
pip freeze > requirements.txt
# Output includes every package with exact versions:
# certifi==2024.8.30
# charset-normalizer==3.4.0
# idna==3.10
# requests==2.32.3
# urllib3==2.2.3
```

**Hand-curated** — list only your direct dependencies with version ranges:

```text
# requirements.txt (hand-curated)
requests>=2.31,<3
flask>=3.0,<4
pandas>=2.1,<3
```

The hand-curated approach is easier to maintain — you only list what you directly use. But it's less reproducible because transitive dependency versions can drift.

### Lock files: the best of both worlds

A **lock file** pins every dependency (direct and transitive) to exact versions, generated from your hand-curated requirements:

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#e8f4fd', 'primaryTextColor': '#1a1a1a', 'lineColor': '#555'}}}%%
graph LR
    A@{ shape: doc, label: "fa:fa-file-lines requirements.txt<br/>(what you want)" }:::decision -->|"uv pip compile"| B@{ shape: doc, label: "fa:fa-lock requirements.lock<br/>(exact versions)" }:::data
    B -->|"uv pip install -r"| C(["fa:fa-check Reproducible<br/>environment"]):::success

    classDef decision fill:#fef3c7,stroke:#d97706,color:#1a1a1a,stroke-width:2px
    classDef data fill:#d1fae5,stroke:#059669,color:#1a1a1a,stroke-width:2px
    classDef success fill:#d1fae5,stroke:#059669,color:#1a1a1a,stroke-width:2px
```

```bash
# Create a hand-curated requirements.txt first, then:
uv pip compile requirements.txt -o requirements.lock
uv pip install -r requirements.lock
```

### Hands-on: create and use a requirements file

1. Create a virtual environment and install some packages:

    ```bash
    uv venv req-test
    source req-test/bin/activate
    uv pip install requests pandas matplotlib
    ```

2. Generate a requirements file:

    ```bash
    pip freeze > requirements.txt
    cat requirements.txt
    ```

3. Test that it works — create a fresh environment and install from the file:

    ```bash
    deactivate
    uv venv req-verify
    source req-verify/bin/activate
    uv pip install -r requirements.txt
    python -c "import requests, pandas, matplotlib; print('All packages installed successfully')"
    ```

4. Clean up:

    ```bash
    deactivate
    rm -rf req-test req-verify requirements.txt
    ```

- [ ] Captured both a `pip freeze` and a hand-curated requirements file
- [ ] Reproduced an environment from a requirements file in a fresh venv

---

## Part 5: Publish

Write a short blog post on your Quarto website explaining **one concept** from this assignment. Pick the topic that surprised you most or that you think would be most useful to a classmate. Follow the **[Publishing Guide](publishing-guide.md)** for the full workflow.

**Quick reference for this assignment:**

- **Suggested categories:** `[tooling, python, reflection]`
- **Post angles** (pick one):
    - **Why virtual environments exist** — and what specifically goes wrong without them
    - **How dependency trees work** — with a diagram you draw for a package of your choice
    - **pip vs conda vs uv** — when to reach for each, with the time comparison you measured

Your post should include at least one code example or diagram.

---

## Final Deliverables

- [ ] Screenshot of `pip list` from Part 0 showing installed packages after `pip install requests`
- [ ] Screenshots showing different numpy versions in two separate venvs (Part 2)
- [ ] Terminal output comparing pip vs uv install times (Part 3)
- [ ] Contents of your `requirements.txt` from Part 4
- [ ] Three reflection question answers (Parts 1, 2, and 3)
- [ ] Blog post URL from Part 5

---

## Troubleshooting

| Problem | Cause | Fix |
|---------|-------|-----|
| `error: externally-managed-environment` | System Python is locked down (common on Ubuntu 23.04+, OSC) | Use a virtual environment — `python -m venv .venv && source .venv/bin/activate` |
| `pip: command not found` after activating venv | venv was created without pip, or activation failed | Recreate with `python -m venv --clear .venv` or use `uv venv` |
| `ResolutionImpossible` or version conflict | Two packages need incompatible versions of a shared dependency | Read the error to find the conflicting package. Try relaxing version pins or check if a newer version resolves the conflict |
| `uv: command not found` | uv is not installed | Install with `curl -LsSf https://astral.sh/uv/install.sh \| sh` then restart your terminal |

---

## Sources

- [Python Packaging User Guide](https://packaging.python.org/) — PyPA (Python Packaging Authority)
- [uv documentation](https://docs.astral.sh/uv/) — Astral
- [Conda documentation](https://docs.conda.io/) — Anaconda, Inc.
