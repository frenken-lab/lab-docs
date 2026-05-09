---
last-reviewed: 2026-05-09
---
<!-- last-reviewed: 2026-05-09 -->
# GPU Preprocessing (RAPIDS)

Use RAPIDS when preprocessing is the bottleneck and the data is large enough that GPU acceleration is worth the setup overhead.

## What RAPIDS Is

RAPIDS gives you GPU-backed equivalents of the familiar pandas / scikit-learn stack:

- `cuDF` for DataFrames
- `cuML` for preprocessing and clustering
- `cuGraph` for graph analytics

If your data fits comfortably in memory and runs quickly on CPU, pandas is usually simpler.

## Environment

RAPIDS is easiest to keep in a separate conda environment from PyTorch.

```bash
module load python/3.12
conda create -n rapids -c rapidsai -c conda-forge -c nvidia rapids=24.12 cuda-version=12.6 python=3.12 -y
conda activate rapids
python -c "import cudf; print(cudf.__version__)"
```

Keep PyTorch in your normal `uv` or `venv` environment. Mixing the two stacks usually creates avoidable dependency pain.

## Pattern

Use RAPIDS for preprocessing, then hand off Parquet or CSV outputs to your training environment.

```python
try:
    import cudf
except ImportError:
    cudf = None

def read_table(path: str):
    if cudf is not None:
        return cudf.read_parquet(path)
    import pandas as pd
    return pd.read_parquet(path)
```

## Batch Job

```bash
#!/bin/bash
#SBATCH --job-name=rapids_preprocess
#SBATCH --partition=gpu
#SBATCH --gpus-per-node=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=64G
#SBATCH --time=01:00:00

module load python/3.12
conda activate rapids
python scripts/preprocess.py --input data/raw --output data/processed
```

## When Not to Use It

- Small datasets
- Interactive exploration
- Any workflow that also needs PyTorch in the same environment

## Next Steps

- [PyTorch & PyG Setup](pytorch-setup.md) for model training
- [ML Project Workflow](ml-workflow.md) for tracking and deployment
- [Environment Management](../working-on-osc/osc-environment-management.md) for module and venv handling
