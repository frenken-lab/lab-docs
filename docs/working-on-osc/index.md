---
hide:
  - toc
---
<!-- last-reviewed: 2026-04-23 -->
# Working on OSC

!!! abstract "What this section covers"
    How to **actually run work** on OSC: submitting SLURM jobs, managing software environments (modules + venvs), orchestrating multi-step pipelines, and the two lab-specific tooling pages for CARLA and MATLAB/Simulink users.

    Prerequisites: you've finished [OSC Basics](../osc-basics/index.md) — account is live, SSH works, you can move files. ML-specific stack (PyTorch, PyG, RAPIDS) lives in [ML Workflows](../ml-workflows/index.md).

---

## Core topics

<div class="grid cards" markdown>

-   :material-calendar-clock:{ .lg .middle } **Job Submission**

    ---

    SLURM deep-dive: `sbatch` scripts, partitions, GPU requests, job arrays, debugging failed jobs. The reference page you'll come back to constantly.

    [:octicons-arrow-right-24: Submit jobs](osc-job-submission.md)

-   :material-package-variant-closed:{ .lg .middle } **Environment Management**

    ---

    OSC's `module` system plus project-level venvs with `uv`. Cached wheels, `$TMPDIR` tricks, avoiding home-directory bloat.

    [:octicons-arrow-right-24: Manage environments](osc-environment-management.md)

-   :material-sitemap:{ .lg .middle } **Pipeline Orchestration**

    ---

    Multi-stage experiments with Ray on SLURM — dependency tracking, resource allocation, failure recovery. For when a single `sbatch` isn't enough.

    [:octicons-arrow-right-24: Orchestrate pipelines](pipeline-orchestration.md)

</div>

## Specialized tooling

<div class="grid cards" markdown>

-   :material-car:{ .lg .middle } **CARLA Simulator**

    ---

    Install, run, and develop against the CARLA autonomous driving simulator on OSC. Headless GPU rendering, scenario scripting, data collection.

    [:octicons-arrow-right-24: Use CARLA](carla-simulator.md)

-   :material-math-integral:{ .lg .middle } **MATLAB & Simulink**

    ---

    Interactive MATLAB sessions, batch jobs, Simulink models. License pool notes, parallel toolbox on multi-node jobs.

    [:octicons-arrow-right-24: Run MATLAB](matlab-simulink.md)

</div>

---

## After this section

If your work is ML-heavy, head to **[ML Workflows](../ml-workflows/index.md)** for PyTorch, PyG, experiment tracking, and HPC-specific training gotchas.
