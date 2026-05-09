---
hide:
  - toc
---
<!-- last-reviewed: 2026-05-09 -->
# OSC

!!! abstract "What this section covers"
    This is the one stop for working on the Ohio Supercomputer Center. Start here to get an account, connect by SSH, move files, and choose the right way to run jobs.

    The pages below split into two parts:

    - **Get connected**: cluster specs, account setup, SSH, remote development, file transfer, and OnDemand
    - **Run work**: SLURM jobs, environments, and pipeline orchestration

---

## Get connected

<div class="grid cards" markdown>

-   :material-server:{ .lg .middle } **1. Clusters Overview**

    ---

    What OSC provides: Pitzer, Cardinal, and Ascend; resource limits; partitions; and when to use each cluster.

    [:octicons-arrow-right-24: Compare the clusters](../osc-basics/osc-clusters-overview.md)

-   :material-account-plus:{ .lg .middle } **2. Account Setup**

    ---

    Request an OSC account under the lab allocation and get through first login.

    [:octicons-arrow-right-24: Get access](../osc-basics/osc-account-setup.md)

-   :material-key-chain-variant:{ .lg .middle } **3. SSH Connection**

    ---

    Set up keys and `~/.ssh/config` so OSC is a one-command login.

    [:octicons-arrow-right-24: Configure SSH](../osc-basics/osc-ssh-connection.md)

-   :material-monitor-dashboard:{ .lg .middle } **4. Remote Development**

    ---

    Use VS Code Remote-SSH to edit OSC files without leaving your laptop.

    [:octicons-arrow-right-24: Work remotely](../osc-basics/osc-remote-development.md)

-   :material-file-swap:{ .lg .middle } **5. File Transfer**

    ---

    Move data with `scp`, `rsync`, Globus, or OnDemand upload when the dataset is too large for Git.

    [:octicons-arrow-right-24: Sync files](../osc-basics/osc-file-transfer.md)

-   :material-web:{ .lg .middle } **6. OnDemand Portal**

    ---

    Browser access for files, jobs, desktops, and interactive apps.

    [:octicons-arrow-right-24: Open OnDemand](../osc-basics/osc-ondemand.md)

</div>

## Run work

<div class="grid cards" markdown>

-   :material-calendar-clock:{ .lg .middle } **7. Job Submission**

    ---

    Submit SLURM jobs, request GPUs, debug runs, and use job arrays.

    [:octicons-arrow-right-24: Submit jobs](../working-on-osc/osc-job-submission.md)

-   :material-package-variant-closed:{ .lg .middle } **8. Environment Management**

    ---

    Manage modules, `uv`, and virtual environments without cluttering home directories.

    [:octicons-arrow-right-24: Manage environments](../working-on-osc/osc-environment-management.md)

-   :material-sitemap:{ .lg .middle } **9. Pipeline Orchestration**

    ---

    Coordinate multi-step work with dependencies and resource-aware runs.

    [:octicons-arrow-right-24: Orchestrate pipelines](../working-on-osc/pipeline-orchestration.md)

</div>

---

## Where Next

If your work is ML-heavy, move to **[ML Workflows](../ml-workflows/index.md)**. If you need Git or contribution guidance, head to **[GitHub](../github/git-fundamentals.md)** or **[Contributing](../contributing/how-this-site-works.md)**.
