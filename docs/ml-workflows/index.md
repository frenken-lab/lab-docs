---
hide:
  - toc
---
<!-- last-reviewed: 2026-05-09 -->
# ML Workflows

!!! abstract "What this section covers"
    The **ML research stack on OSC**: framework setup, project workflow, RAPIDS preprocessing, and a few hard-won lessons from running experiments at scale.

    Prerequisites: you've done [OSC](../osc/index.md) — you can submit SLURM jobs and manage environments. These pages assume you know `sbatch` and `module load`.

---

## Start Here

<div class="grid cards" markdown>

-   :material-fire:{ .lg .middle } **PyTorch & PyG Setup**

    ---

    Install PyTorch against OSC's CUDA, add PyG, request GPUs correctly, and verify the install.

    [:octicons-arrow-right-24: Set up PyTorch](pytorch-setup.md)

-   :material-rocket-launch:{ .lg .middle } **GPU Preprocessing (RAPIDS)**

    ---

    10–100× faster tabular preprocessing with cuDF/cuML. Drop-in replacement for pandas on datasets that otherwise take hours to filter.

    [:octicons-arrow-right-24: Accelerate preprocessing](rapids-gpu-preprocessing.md)

</div>

## ML Workflow

<div class="grid cards" markdown>

-   :material-folder-multiple:{ .lg .middle } **ML Project Workflow**

    ---

    Project layout, notebook-to-script, experiment tracking, analytics, and deployment in one compact guide.

    [:octicons-arrow-right-24: Open the workflow guide](ml-workflow.md)

</div>

## Lessons from the Trenches

<div class="grid cards" markdown>

-   :material-alert-circle:{ .lg .middle } **HPC Training Nuances**

    ---

    Worker starvation, prebatching, gradient-accumulation gotchas, the stuff that only shows up at scale. Read before your first ablation campaign — save a week of wasted compute.

    [:octicons-arrow-right-24: Avoid the traps](hpc-training-nuances.md)

</div>
