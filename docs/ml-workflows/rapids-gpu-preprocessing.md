<!-- last-reviewed: 2026-02-25 -->
# GPU Preprocessing (RAPIDS)

Accelerate large-scale tabular data preprocessing on OSC GPUs using NVIDIA RAPIDS — 10-100x faster than CPU-based pandas/NumPy for filtering, grouping, and feature engineering.

---

## What Is RAPIDS?

[RAPIDS](https://rapids.ai/) is a suite of GPU-accelerated libraries that mirror the pandas/scikit-learn API:

| Library | CPU Equivalent | Purpose |
|---------|---------------|---------|
| **cuDF** | pandas | GPU DataFrames — filtering, grouping, joins |
| **cuML** | scikit-learn | GPU machine learning — preprocessing, clustering, regression |
| **cuGraph** | NetworkX | GPU graph analytics |

RAPIDS is useful when your preprocessing pipeline is the bottleneck — large CSVs, millions of rows, complex feature engineering. If your data fits in memory and processes in seconds, stick with pandas.

---

## Why a Separate Conda Environment?

RAPIDS is **conda-only** — it cannot be installed via pip or uv. Its packages depend on conda-forge builds of CUDA libraries that conflict with pip-installed PyTorch. For this reason:

- **RAPIDS preprocessing** runs in a dedicated conda environment
- **Model training** runs in your normal uv/venv environment with PyTorch
- The two environments communicate through **files** (Parquet), not shared memory

This two-environment pattern is intentional — it keeps your training environment clean while giving you GPU-accelerated preprocessing when you need it.

---

## Setup

Create a dedicated conda environment for RAPIDS:

```bash
# Load conda
module load python/3.12

# Create RAPIDS environment (this takes a few minutes)
conda create -n gnn-rapids \
    -c rapidsai -c conda-forge -c nvidia \
    rapids=24.12 cuda-version=12.6 python=3.12 \
    -y

# Verify installation
conda activate gnn-rapids
python -c "import cudf; print(f'cuDF version: {cudf.__version__}')"
conda deactivate
```

!!! warning "Do not install PyTorch in this environment"
    The RAPIDS conda environment is for preprocessing only. Keep PyTorch in your separate uv/venv environment to avoid dependency conflicts.

---

## Soft-Import Pattern

To write code that works with or without RAPIDS, use a `RAPIDS_AVAILABLE` flag:

```python
try:
    import cudf
    import cuml
    RAPIDS_AVAILABLE = True
except ImportError:
    RAPIDS_AVAILABLE = False

def load_data(path: str):
    """Load data using cuDF if available, otherwise pandas."""
    if RAPIDS_AVAILABLE:
        return cudf.read_parquet(path)
    else:
        import pandas as pd
        return pd.read_parquet(path)
```

This lets the same script run on both GPU nodes (with RAPIDS) and login nodes (without RAPIDS, falling back to pandas).

---

## SLURM Script for GPU Preprocessing

`scripts/preprocess_gpu.sh`:

```bash
#!/bin/bash
#SBATCH --job-name=rapids_preprocess
#SBATCH --account=PAS1234
#SBATCH --partition=gpu
#SBATCH --gpus-per-node=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=64G
#SBATCH --time=01:00:00
#SBATCH --output=logs/preprocess_%j.out

echo "Job started at: $(date)"
echo "Node: $(hostname)"

# Load CUDA module (RAPIDS needs system CUDA)
module load cuda/12.x

# Activate RAPIDS conda environment
module load python/3.12
conda activate gnn-rapids

# Run preprocessing only
python scripts/preprocess.py \
    --input data/raw/ \
    --output data/processed/ \
    --preprocess-only

conda deactivate
echo "Job finished at: $(date)"
```

After preprocessing completes, run training in your normal environment:

```bash
#!/bin/bash
#SBATCH --job-name=train
#SBATCH --partition=gpu
#SBATCH --gpus-per-node=1

# Normal uv/venv environment — reads the Parquet files RAPIDS produced
source .venv/bin/activate
python scripts/train.py --data data/processed/
```

---

## When NOT to Use RAPIDS

- **Small datasets** (< 1M rows) — pandas is fast enough, and the conda setup overhead isn't worth it
- **Graph neural network training** — use PyTorch Geometric in your uv/venv environment instead
- **Anything that needs PyTorch** — RAPIDS and PyTorch should live in separate environments
- **Interactive exploration** — use pandas in a Jupyter notebook; RAPIDS is for batch preprocessing

---

## Next Steps

- [Environment Management](../working-on-osc/osc-environment-management.md) — uv, venv, and module management on OSC
- [PyTorch & GPU Setup](pytorch-setup.md) — Setting up your training environment
- [Pipeline Orchestration](../working-on-osc/pipeline-orchestration.md) — Ray pipelines that chain preprocessing → training
- [DuckDB Analytics Layer](duckdb-analytics.md) — Querying preprocessed results with SQL
