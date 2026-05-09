---
hide:
  - toc
---
<!-- last-reviewed: 2026-04-23 -->
# ML Workflows

!!! abstract "What this section covers"
    The **ML research stack on OSC**: framework setup (PyTorch, PyG, RAPIDS), project structure, experiment tracking, analytics, deployment, and hard-won lessons from running ablation campaigns at scale.

    Prerequisites: you've done [Working on OSC](../working-on-osc/index.md) — you can submit SLURM jobs and manage environments. These pages assume you know `sbatch` and `module load`.

---

## Framework setup

<div class="grid cards" markdown>

-   :material-fire:{ .lg .middle } **PyTorch & GPU Setup**

    ---

    Install PyTorch against OSC's CUDA, request GPUs correctly, verify the install. Multi-GPU and `torch.compile` notes for the ablation-campaign crowd.

    [:octicons-arrow-right-24: Set up PyTorch](pytorch-setup.md)

-   :material-graph:{ .lg .middle } **PyG (PyTorch Geometric)**

    ---

    Graph neural networks on OSC. Clean install against the pinned PyTorch version, dataset caching, mini-batch loaders for large graphs.

    [:octicons-arrow-right-24: Install PyG](pyg-setup.md)

-   :material-rocket-launch:{ .lg .middle } **GPU Preprocessing (RAPIDS)**

    ---

    10–100× faster tabular preprocessing with cuDF/cuML. Drop-in replacement for pandas on datasets that otherwise take hours to filter.

    [:octicons-arrow-right-24: Accelerate preprocessing](rapids-gpu-preprocessing.md)

</div>

## Project structure & iteration

<div class="grid cards" markdown>

-   :material-folder-multiple:{ .lg .middle } **ML Project Template**

    ---

    Starting-point directory layout and run checklist. What to standardize across ML repos so the lab can onboard onto each other's projects fast.

    [:octicons-arrow-right-24: Use the template](ml-workflow.md)

-   :material-notebook-edit:{ .lg .middle } **Notebook-to-Script Workflow**

    ---

    Iterate in Jupyter, graduate to `python -m` scripts for sbatch. Shared patterns for keeping the two in sync without copy-paste.

    [:octicons-arrow-right-24: Graduate notebooks](notebook-to-script.md)

-   :material-chart-line:{ .lg .middle } **Data & Experiment Tracking**

    ---

    DVC for datasets, W&B/MLflow for runs, TensorBoard for training curves, Parquet for loaders. The full tracking stack the lab actually uses.

    [:octicons-arrow-right-24: Track experiments](data-experiment-tracking.md)

</div>

## Analytics & deployment

<div class="grid cards" markdown>

-   :material-database-search:{ .lg .middle } **DuckDB Analytics Layer**

    ---

    SQL over Parquet — no server, single binary, faster than pandas. How the lab slices experiment results across hundreds of runs.

    [:octicons-arrow-right-24: Query with DuckDB](duckdb-analytics.md)

-   :material-hand-heart:{ .lg .middle } **Hugging Face Spaces**

    ---

    Free hosting for Streamlit/Gradio dashboards and Quarto reports. CI-driven deploys from GitHub — how the [OSC usage dashboard](https://huggingface.co/spaces/buckeyeguy/osc-usage-dashboard) ships.

    [:octicons-arrow-right-24: Deploy a Space](huggingface-spaces.md)

</div>

## Lessons from the trenches

<div class="grid cards" markdown>

-   :material-alert-circle:{ .lg .middle } **HPC Training Nuances**

    ---

    Worker starvation, prebatching, gradient-accumulation gotchas, the stuff that only shows up at scale. Read before your first ablation campaign — save a week of wasted compute.

    [:octicons-arrow-right-24: Avoid the traps](hpc-training-nuances.md)

</div>
