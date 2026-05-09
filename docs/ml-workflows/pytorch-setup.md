---
status: updated
tags:
  - PyTorch
  - GPU
  - CUDA
  - OSC
---
<!-- last-reviewed: 2026-05-09 -->
# PyTorch & PyG Setup

Install PyTorch, add PyG when needed, and verify the GPU path on OSC.

## Prerequisites

- OSC account with GPU access
- SSH connection configured
- Basic familiarity with Python

## Quick Setup

=== "uv (Recommended)"

    ```bash
    uv venv --python /apps/python/3.12/bin/python3
    source .venv/bin/activate
    uv add "torch>=2.8.0,<2.9" torchvision torchaudio
    uv add numpy pandas matplotlib scikit-learn jupyter tensorboard
    ```

=== "pip + venv"

    ```bash
    module load python/3.12
    python -m venv ~/venvs/pytorch
    source ~/venvs/pytorch/bin/activate
    pip install --upgrade pip
    pip install "torch>=2.8.0,<2.9" torchvision torchaudio
    pip install numpy pandas matplotlib scikit-learn jupyter tensorboard
    ```

!!! tip "PyPI torch bundles CUDA"
    You do not need `module load cuda` for standard PyTorch wheels.

## PyG (PyTorch Geometric)

PyG wheels must match your exact `torch` and CUDA build.

!!! warning "Version matching matters"
    Check [data.pyg.org/whl](https://data.pyg.org/whl/) before installing PyG wheels. Mismatched wheels can import but fail at runtime.

```bash
uv add pyg-lib torch-scatter torch-sparse torch-cluster torch-spline-conv \
  -f https://data.pyg.org/whl/torch-2.8.0+cu124.html
```

```bash
pip install pyg-lib torch-scatter torch-sparse torch-cluster torch-spline-conv \
  -f https://data.pyg.org/whl/torch-2.8.0+cu124.html
```

Verify:

```bash
python - <<'PY'
import torch
import torch_geometric
print(torch.__version__)
print(torch_geometric.__version__)
PY
```

## Verify Installation

Create a tiny check script:

```python
import torch

print(torch.__version__)
print(torch.cuda.is_available())
```

Run it on a GPU node:

```bash
srun -p gpu --gpus-per-node=1 --time=00:10:00 --pty bash
source .venv/bin/activate
python test_pytorch.py
```

## GPU Basics

- Use `srun` for interactive checks
- Use `sbatch` for real training
- Start with one GPU and scale up only when the model benefits from it

### Common cluster shapes

| Cluster | Best For |
|---|---|
| Pitzer | General training, older CUDA/module combos |
| Ascend / Cardinal | Larger models, higher throughput, more memory |

## Monitoring

Use `nvidia-smi` to confirm the job is actually using the GPU:

```bash
nvidia-smi
watch -n 1 nvidia-smi
```

## Troubleshooting

### CUDA Out of Memory

- Reduce batch size
- Use gradient accumulation
- Move to a larger GPU tier if the model genuinely needs more memory

### Slow Training

- Check that the job is actually on a GPU node
- Increase data-loader workers
- Try mixed precision if the model is numerically stable

## Next Steps

- [GPU Preprocessing (RAPIDS)](rapids-gpu-preprocessing.md) if preprocessing is the bottleneck
- [ML Project Workflow](ml-workflow.md) for project structure and tracking
- [HPC Training Nuances](hpc-training-nuances.md) for scheduler and runtime gotchas
