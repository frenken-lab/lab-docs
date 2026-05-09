---
hide:
  - toc
---
<!-- last-reviewed: 2026-04-23 -->
# OSC Basics

!!! abstract "What this section covers"
    Everything you need to **get on the Ohio Supercomputer Center** and start working. What clusters exist, how to request an account, how to SSH in, how to edit code remotely in VS Code, how to move files, and the web portal option if the terminal isn't your thing.

    By the end you'll have a working account, a stable SSH connection, and a way to open any OSC file from your laptop. The [Working on OSC](../working-on-osc/index.md) section then covers actually running jobs.

---

## Suggested order

<div class="grid cards" markdown>

-   :material-server:{ .lg .middle } **1. Clusters Overview**

    ---

    Pitzer, Cardinal, Ascend — specs, GPU availability, partitions, memory limits. Read this first so you understand what you're picking when you submit a job.

    [:octicons-arrow-right-24: Tour the clusters](osc-clusters-overview.md)

-   :material-account-plus:{ .lg .middle } **2. Account Setup**

    ---

    How to request an OSC account under the lab's allocation. PI approval workflow, what to expect, first-login steps.

    [:octicons-arrow-right-24: Request access](osc-account-setup.md)

-   :material-key-chain-variant:{ .lg .middle } **3. SSH Connection**

    ---

    Generate keys, upload to OSC, configure `~/.ssh/config` so `ssh osc` just works. The foundation for everything else in this section.

    [:octicons-arrow-right-24: Set up SSH](osc-ssh-connection.md)

-   :material-monitor-dashboard:{ .lg .middle } **4. Remote Development**

    ---

    VS Code Remote-SSH — edit OSC files from your laptop as if they were local. The daily-driver workflow for most lab work.

    [:octicons-arrow-right-24: Go remote](osc-remote-development.md)

-   :material-file-swap:{ .lg .middle } **5. File Transfer**

    ---

    `scp`, `rsync`, Globus, OnDemand upload. When to use each, and how to sync large datasets without wasting an allocation.

    [:octicons-arrow-right-24: Move files](osc-file-transfer.md)

-   :material-web:{ .lg .middle } **6. OnDemand Portal**

    ---

    Browser access to OSC — no SSH required. Launch Jupyter, RStudio, or a full desktop. Useful as a fallback and for quick visual tasks.

    [:octicons-arrow-right-24: Use the portal](osc-ondemand.md)

</div>

---

## After this section

You're connected and can move files — next up is **[Working on OSC](../working-on-osc/index.md)** for SLURM jobs, environments, and orchestration.
