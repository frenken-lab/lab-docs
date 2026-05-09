---
hide:
  - toc
---
<!-- last-reviewed: 2026-04-23 -->
# Getting Started

!!! abstract "What this section covers"
    Your **local development environment** — the laptop side of the lab. Install WSL2 (Windows only), set up VS Code, configure Python, and plug in AI coding assistants. Once this is done, you're ready to move to the [OSC Basics](../osc-basics/index.md) section to get on the cluster.

    **Plan on ~4–6 hours total** if you're starting from a fresh Windows machine. macOS/Linux users can skip WSL2 and cut that roughly in half.

---

## Suggested order

<div class="grid cards" markdown>

-   :material-microsoft-windows:{ .lg .middle } **1. WSL2 Setup**

    ---

    Windows users only: install the Windows Subsystem for Linux so you can run a real Ubuntu environment alongside Windows. Skip if you're on macOS or native Linux.

    **~45 min · Windows only**

    [:octicons-arrow-right-24: Install WSL2](wsl-setup.md)

-   :material-microsoft-visual-studio-code:{ .lg .middle } **2. VS Code Setup**

    ---

    Install VS Code, connect it to WSL, set sensible defaults. The editor we use for everything — local scripts, remote SSH into OSC, Jupyter, Markdown.

    **~30 min · All platforms**

    [:octicons-arrow-right-24: Set up VS Code](vscode-setup.md)

-   :material-puzzle:{ .lg .middle } **3. VS Code Extensions**

    ---

    The required extensions (Python, Remote-SSH, GitLens) plus the productivity picks we actually use. Install as a batch — takes five minutes.

    **~15 min · All platforms**

    [:octicons-arrow-right-24: Install extensions](vscode-extensions.md)

-   :material-language-python:{ .lg .middle } **4. Python Environment Setup**

    ---

    Two environments, one purpose each: **uv** for fast project venvs, **conda** for compiled scientific stacks. Covers the pre-commit hooks we enforce across lab repos.

    **~45 min · All platforms**

    [:octicons-arrow-right-24: Set up Python](python-environment-setup.md)

-   :material-robot-outline:{ .lg .middle } **5. AI Coding Assistants**

    ---

    GitHub Copilot and Claude Code — accounts, install, lab-recommended settings. Foundational setup before you touch agent workflows.

    **~30 min · All platforms**

    [:octicons-arrow-right-24: Enable AI assistants](ai-coding-assistants.md)

-   :material-account-cog:{ .lg .middle } **6. Agent Workflows** *(advanced)*

    ---

    Once the basics work: MCP servers, slash commands, hooks, subagents. The patterns Robert and other senior members use daily. Come back to this after you've lived in Copilot/Claude for a week or two.

    **Optional · Return after first month**

    [:octicons-arrow-right-24: Go deeper](agent-workflows.md)

</div>

---

## After this section

Once your local machine is set up, move to **[OSC Basics](../osc-basics/index.md)** to get your account, SSH in, and run your first job.
