---
hide:
  - toc
---
<!-- last-reviewed: 2026-03-30 -->
# CAR Mobility Systems Lab Setup Guide

Welcome to the OSU CAR Mobility Systems Lab documentation! This guide helps lab members set up their development environment and work effectively on the Ohio Supercomputer Center (OSC).

!!! info "Lab Compute Dashboard"
    Track our OSC spending, job health, and per-user breakdowns on the [live dashboard](https://huggingface.co/spaces/buckeyeguy/osc-usage-dashboard). Data refreshes automatically every morning. See [how it's built](ml-workflows/huggingface-spaces.md#streamlit-dashboard-with-hf-dataset-cron).

---

## :rocket: Quick Start

New to the lab? Follow these steps to get up and running:

| Step | Guide | Description |
|:----:|-------|-------------|
| **1** | **[Install WSL2](getting-started/wsl-setup.md)** | Windows users: set up WSL2 (your Linux development environment) |
| **2** | **[Set up VS Code](getting-started/vscode-setup.md)** | Install and configure Visual Studio Code with essential extensions |
| **3** | **[Get OSC Access](osc-basics/osc-account-setup.md)** | Request your account on the Ohio Supercomputer Center |
| **4** | **[Connect via SSH](osc-basics/osc-ssh-connection.md)** | Set up SSH keys and connect to OSC from your machine |
| **5** | **[Start Developing](osc-basics/osc-remote-development.md)** | Use VS Code's Remote-SSH for seamless development on the cluster |

---

## :wrench: Our Tool Stack

<div class="grid cards" markdown>

-   :material-microsoft-visual-studio-code:{ .lg .middle } **VS Code + Remote-SSH**

    ---

    Edit, debug, and develop directly on OSC nodes from your local machine.

-   :fontawesome-brands-git-alt:{ .lg .middle } **[Git & GitHub](github/git-fundamentals.md)**

    ---

    Version control, pull requests, and CI/CD for reproducible research.

-   :material-console:{ .lg .middle } **SLURM**

    ---

    Schedule CPU and GPU jobs on OSC's Pitzer cluster.

-   :material-language-python:{ .lg .middle } **uv + Modules**

    ---

    Fast, reproducible Python environments on HPC.

-   :material-fire:{ .lg .middle } **PyTorch & PyG**

    ---

    Neural network training with GPU acceleration and graph neural networks.

-   :material-robot:{ .lg .middle } **Claude & Copilot**

    ---

    AI-assisted coding, debugging, and pipeline automation.

</div>

---

## :books: Documentation Sections

<div class="grid cards" markdown>

-   :material-laptop:{ .lg .middle } **Getting Started**

    ---

    WSL2, VS Code, Python environments, and AI coding assistants for local development.

    [:octicons-arrow-right-24: Get started](getting-started/wsl-setup.md)

-   :material-server-network:{ .lg .middle } **OSC Basics**

    ---

    Cluster specs, account setup, SSH, remote development, file transfer, and OnDemand.

    [:octicons-arrow-right-24: Learn OSC basics](osc-basics/osc-clusters-overview.md)

-   :material-cog-play:{ .lg .middle } **Working on OSC**

    ---

    SLURM job submission, environment management, pipeline orchestration, and simulators.

    [:octicons-arrow-right-24: Start working](working-on-osc/osc-job-submission.md)

-   :material-brain:{ .lg .middle } **ML Workflows**

    ---

    PyTorch & GPU setup, PyG, project templates, notebook-to-script, and experiment tracking.

    [:octicons-arrow-right-24: ML guides](ml-workflows/pytorch-setup.md)

-   :material-file-document-edit:{ .lg .middle } **Contributing**

    ---

    How this site works, adding pages, and setting up your own documentation site.

    [:octicons-arrow-right-24: Contribute](contributing/how-this-site-works.md)

-   :material-school:{ .lg .middle } **Assignments**

    ---

    Hands-on tasks for new undergraduates: personal websites, EDA, and OSC onboarding.

    [:octicons-arrow-right-24: View assignments](assignments/index.md)

-   :material-lifebuoy:{ .lg .middle } **Resources**

    ---

    Troubleshooting guides, useful links, and OSC support contacts.

    [:octicons-arrow-right-24: Get help](resources/troubleshooting.md)

</div>

---

## :bulb: Tips

<div class="grid" markdown>

!!! tip "Use the search"
    Press ++s++ or ++slash++ to search. Indexes all pages and code blocks.

!!! tip "Dark mode"
    Click the :material-brightness-7: icon in the header to toggle.

!!! tip "Edit on GitHub"
    Found an error? Click :material-pencil: on any page to suggest a fix.

</div>

---

## :link: Quick Links

<div class="grid cards" markdown>

-   :material-chart-bar:{ .lg .middle } **[Lab Compute Dashboard](https://huggingface.co/spaces/buckeyeguy/osc-usage-dashboard)**

    OSC spending, job health, and per-user breakdowns.

-   :material-book-open-variant:{ .lg .middle } **[OSC Documentation](https://www.osc.edu/resources)**

    Official OSC guides, FAQs, and support.

-   :material-application:{ .lg .middle } **[OSC OnDemand](https://ondemand.osc.edu)**

    Web portal for file browsing, jobs, and desktops.

-   :material-traffic-light:{ .lg .middle } **[OSC Status](https://www.osc.edu/resources/system-status)**

    Cluster status, maintenance windows, and outages.

-   :fontawesome-brands-github:{ .lg .middle } **[Lab GitHub](https://github.com/OSU-CAR-MSL)**

    All lab repositories and project code.

</div>
