---
status: updated
tags:
  - PyTorch
  - GNN
  - CUDA
  - GPU
---
<!-- last-reviewed: 2026-03-30 -->
# PyG (PyTorch Geometric) Setup

[PyTorch Geometric (PyG)](https://pytorch-geometric.readthedocs.io/en/latest/#) is the leading library for deep learning on graphs and other irregular structures. It provides efficient implementations of graph neural network layers (GCN, GAT, GraphSAGE, GIN, and many more), standard benchmark datasets, mini-batch loaders for large graphs, and utilities for graph transforms and sampling. If your research involves graph neural networks — whether for citation networks, molecular property prediction, point clouds, or CAN bus intrusion detection — PyG is the go-to framework on top of PyTorch.

## Prerequisites

Before installing PyG, you need a working PyTorch installation with CUDA support on OSC. If you haven't done this yet, complete the [PyTorch & GPU Setup](pytorch-setup.md) guide first. Specifically, you need:

- An OSC account with GPU access
- SSH connection configured (see [SSH Connection](../osc-basics/osc-ssh-connection.md))
- Python 3.12 virtual environment with PyTorch + CUDA installed
- Familiarity with SLURM job submission (see [Job Submission](../working-on-osc/osc-job-submission.md))

## Installation on OSC

PyG depends on several compiled extension packages (`torch-scatter`, `torch-sparse`, `torch-cluster`, `torch-spline-conv`) that must match your exact PyTorch version and CUDA version. Installing from pre-built wheels avoids lengthy compilation on login nodes.

### Step 1: Activate Your Environment

```bash
# Activate your PyTorch virtual environment
source .venv/bin/activate        # uv
# or: source ~/venvs/pytorch/bin/activate  # venv + pip
```

### Step 2: Verify PyTorch Version and CUDA

Before installing, confirm the versions you need to match:

```bash
python -c "import torch; print(f'PyTorch: {torch.__version__}, CUDA: {torch.version.cuda}')"
```

Note the output — you'll use these versions in the wheel URL below.

### Step 3: Install PyG Extension Libraries

Install the compiled extension packages from PyG's wheel index. The URL must match your **PyTorch version** and **CUDA version** exactly:

=== "PyTorch 2.8.x + CUDA 12.6 (current)"

    ```bash
    pip install torch-scatter torch-sparse torch-cluster \
        -f https://data.pyg.org/whl/torch-2.8.0+cu126.html
    ```

!!! tip "Check the wheel index for your version"
    The URLs above are pinned to PyTorch 2.8.0 + CUDA 12.6. When PyTorch updates, browse [https://data.pyg.org/whl/](https://data.pyg.org/whl/) to find the correct URL for your version. The URL must match your installed versions exactly. Always verify with Step 2 first.

### Step 4: Install PyTorch Geometric

```bash
pip install torch-geometric
```

### Alternative: uv with `pyproject.toml`

If you manage your project with `uv`, configure PyG's flat wheel index in `pyproject.toml` instead of using `-f` flags:

```toml
[project]
requires-python = ">=3.12,<3.13"
dependencies = [
    "torch>=2.8.0,<2.9",
    "torch-geometric>=2.7.0",
    "torch-scatter",
    "torch-sparse",
    "torch-cluster",
]

[[tool.uv.index]]
name = "pyg"
url = "https://data.pyg.org/whl/torch-2.8.0+cu126.html"
format = "flat"
explicit = true

[tool.uv.sources]
torch-scatter = { index = "pyg" }
torch-sparse = { index = "pyg" }
torch-cluster = { index = "pyg" }
```

Then install with:

```bash
# Use OSC's system Python (never uv's managed Python on OSC)
uv venv --python /apps/python/3.12/bin/python3
uv sync
```

!!! warning "uv PyG traps"
    - **Use `[[tool.uv.index]]` with `format = "flat"` and `explicit = true`**, not `[tool.uv] find-links`. `find-links` doesn't support the `explicit` flag, so non-PyG packages may accidentally resolve from the flat index.
    - **Always pin `torch<next_minor`** (e.g., `<2.9`). Without an upper bound, uv resolves to the latest PyPI version (2.10+), which has no PyG wheels.
    - **Pin `requires-python` with an upper bound** (e.g., `<3.13`). Without it, uv resolves for all supported Pythons including 3.13, where PyG wheels may not exist.
    - **Never use uv-managed Python on OSC.** Standalone Python builds from uv can segfault on RHEL 9. Always point to OSC's system Python: `uv venv --python /apps/python/3.12/bin/python3`.

!!! warning "Version Mismatch Will Cause Silent Failures"
    The most common PyG installation problem is a mismatch between the PyTorch/CUDA version in the wheel URL and the PyTorch/CUDA version actually installed. If the versions don't match, the extension libraries may install but fail at import time with `undefined symbol` errors or segfaults. Always verify with the check in Step 2 before installing.

!!! tip "Check the full wheel index"
    Browse [https://data.pyg.org/whl/](https://data.pyg.org/whl/) to find the correct URL for your specific PyTorch + CUDA combination. The PyG [installation guide](https://pytorch-geometric.readthedocs.io/en/latest/install/installation.html) also has an interactive matrix.

## Verification Script

After installation, run this script on a GPU node to verify everything works:

```bash
# Request an interactive GPU session
srun -p gpu --gpus-per-node=1 --time=00:10:00 --pty bash

# Activate environment (PyPI torch bundles CUDA — no module load needed)
source .venv/bin/activate

# Run the verification script
python test_pyg.py
```

Create `test_pyg.py`:

```python
import torch
import torch_geometric
from torch_geometric.datasets import Planetoid

print("=" * 55)
print("PyG Installation Verification")
print("=" * 55)

print(f"\nPyTorch version:          {torch.__version__}")
print(f"PyG version:              {torch_geometric.__version__}")
print(f"CUDA available:           {torch.cuda.is_available()}")

if torch.cuda.is_available():
    print(f"CUDA version:             {torch.version.cuda}")
    print(f"GPU:                      {torch.cuda.get_device_name(0)}")

# Test extension packages
print("\nExtension packages:")
try:
    import torch_scatter
    print(f"  torch-scatter:          {torch_scatter.__version__}")
except ImportError:
    print("  torch-scatter:          NOT INSTALLED")

try:
    import torch_sparse
    print(f"  torch-sparse:           {torch_sparse.__version__}")
except ImportError:
    print("  torch-sparse:           NOT INSTALLED")

try:
    import torch_cluster
    print(f"  torch-cluster:          {torch_cluster.__version__}")
except ImportError:
    print("  torch-cluster:          NOT INSTALLED")

# Test dataset loading
print("\nLoading Cora dataset...")
dataset = Planetoid(root="/tmp/pyg_test_data", name="Cora")
data = dataset[0]
print(f"  Nodes:                  {data.num_nodes}")
print(f"  Edges:                  {data.num_edges}")
print(f"  Features per node:      {data.num_node_features}")
print(f"  Classes:                {dataset.num_classes}")

# Test GPU transfer
if torch.cuda.is_available():
    data = data.to("cuda")
    print(f"\n  Data moved to GPU:      {data.x.device}")

print("\n" + "=" * 55)
print("All checks passed!")
print("=" * 55)
```

You should see all versions printed, the Cora dataset loaded successfully, and data transferred to GPU without errors.

## Minimal GCN Example

This example trains a 2-layer Graph Convolutional Network (GCN) on the Cora citation dataset — a standard benchmark for node classification. Cora contains 2,708 scientific papers (nodes) with 5,429 citation links (edges), each paper represented by a 1,433-dimensional bag-of-words feature vector and classified into one of 7 topics.

Create `train_gcn.py`:

```python
import torch
import torch.nn.functional as F
from torch_geometric.datasets import Planetoid
from torch_geometric.nn import GCNConv

# --- Dataset ---
dataset = Planetoid(root="/tmp/pyg_data", name="Cora")
data = dataset[0]
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
data = data.to(device)


# --- Model ---
class GCN(torch.nn.Module):
    def __init__(self, in_channels: int, hidden_channels: int, out_channels: int):
        super().__init__()
        self.conv1 = GCNConv(in_channels, hidden_channels)
        self.conv2 = GCNConv(hidden_channels, out_channels)

    def forward(self, x, edge_index):
        x = self.conv1(x, edge_index)
        x = F.relu(x)
        x = F.dropout(x, p=0.5, training=self.training)
        x = self.conv2(x, edge_index)
        return x


model = GCN(dataset.num_node_features, 16, dataset.num_classes).to(device)
optimizer = torch.optim.Adam(model.parameters(), lr=0.01, weight_decay=5e-4)

# --- Training ---
model.train()
for epoch in range(1, 201):
    optimizer.zero_grad()
    out = model(data.x, data.edge_index)
    loss = F.cross_entropy(out[data.train_mask], data.y[data.train_mask])
    loss.backward()
    optimizer.step()

    if epoch % 50 == 0:
        model.eval()
        with torch.no_grad():
            pred = model(data.x, data.edge_index).argmax(dim=1)
            correct = (pred[data.test_mask] == data.y[data.test_mask]).sum()
            acc = correct / data.test_mask.sum()
        print(f"Epoch {epoch:>3d}  Loss: {loss:.4f}  Test Acc: {acc:.4f}")
        model.train()
```

Expected output (accuracy varies slightly per run):

```
Epoch  50  Loss: 0.6834  Test Acc: 0.7810
Epoch 100  Loss: 0.3521  Test Acc: 0.8050
Epoch 150  Loss: 0.2487  Test Acc: 0.8100
Epoch 200  Loss: 0.1923  Test Acc: 0.8130
```

!!! tip "Beyond GCN"
    PyG provides dozens of GNN layers out of the box. To swap in a different architecture, replace `GCNConv` with `GATConv` (Graph Attention), `SAGEConv` (GraphSAGE), `GINConv` (Graph Isomorphism Network), or any other layer from `torch_geometric.nn`. The API is consistent — most layers take `(x, edge_index)` as input.

## OSC-Specific Notes

### Storage: Use Scratch for Datasets

PyG datasets can be large (some exceed several GB). Always point the dataset `root` directory to your OSC scratch space, not your home directory which has a limited quota:

```bash
# Set in your ~/.bashrc or job script
export TORCH_HOME=/fs/scratch/PAS1234/$USER/torch_cache
export PYG_DATA_ROOT=/fs/scratch/PAS1234/$USER/pyg_datasets
```

Then in your Python code:

```python
import os

data_root = os.environ.get("PYG_DATA_ROOT", "/tmp/pyg_data")
dataset = Planetoid(root=data_root, name="Cora")
```

!!! warning "Scratch purge policy"
    OSC scratch files are purged after **60 days of inactivity** ([OSC scratch policy](https://www.osc.edu/supercomputing/storage-environment-at-osc/available-file-systems)). If your datasets take a long time to download or preprocess, keep a backup elsewhere or use a DVC remote. See [Data & Experiment Tracking](data-experiment-tracking.md) for details on DVC.

### DataLoader Configuration

PyG's `DataLoader` works like PyTorch's but handles batching of graph data (merging multiple graphs into a single disconnected graph). Match `num_workers` to your SLURM `--cpus-per-task` allocation:

```python
from torch_geometric.loader import DataLoader

# If your job requests --cpus-per-task=4, use num_workers=4
loader = DataLoader(
    dataset,
    batch_size=32,
    shuffle=True,
    num_workers=4,          # Match --cpus-per-task
    pin_memory=True,        # Faster CPU-to-GPU transfer
    persistent_workers=True,  # Avoid worker respawn overhead
)
```

!!! tip "Single large graph vs. many small graphs"
    If your task is **node classification on a single large graph** (like Cora), you don't need a `DataLoader` — the entire graph fits in GPU memory. `DataLoader` is for tasks with **many separate graphs** (e.g., molecular property prediction with thousands of molecules) or when using **neighbor sampling** on large graphs via `torch_geometric.loader.NeighborLoader`.

### Memory Considerations

GNN message passing can be memory-intensive, especially on dense graphs. A few strategies:

- **Neighbor sampling** — For large graphs that don't fit in GPU memory, use `NeighborLoader` to sample local subgraphs:
  ```python
  from torch_geometric.loader import NeighborLoader

  loader = NeighborLoader(
      data,
      num_neighbors=[25, 10],   # Sample 25 neighbors at hop 1, 10 at hop 2
      batch_size=128,
      input_nodes=data.train_mask,
  )
  ```
- **Sparse tensor backend** — Enable sparse matrix multiplication for lower memory usage:
  ```python
  from torch_geometric.nn import GCNConv
  conv = GCNConv(in_channels, out_channels)
  # PyG will use sparse tensors when data has SparseTensor edge representation
  ```
- **Request sufficient memory** — For large datasets, request more RAM in your SLURM job: `#SBATCH --mem=64G`

### PyG-Specific Gotchas

!!! danger "`Data.to()` is in-place — always clone first"
    Unlike standard PyTorch tensors, PyG's `Data.to(device)` modifies the object **in place** and returns the same reference. If you hold a reference to the original data (e.g., in a dataset or cache), it's now on GPU too — corrupting your data pipeline.

    ```python
    # ❌ WRONG — mutates the original dataset entry
    data = dataset[0]
    data = data.to(device)  # dataset[0] is now on GPU too!

    # ✅ CORRECT — clone before moving
    data = dataset[0].clone().to(device)
    ```

    This is a common source of silent bugs in PyG code. It can cause memory leaks (dataset entries gradually migrate to GPU), incorrect batching, and irreproducible results.

!!! warning "Save and restore `model.training` state"
    When switching between [`model.train()` and `model.eval()`](https://pytorch.org/docs/stable/generated/torch.nn.Module.html#torch.nn.Module.eval) for validation, always restore the original state. Forgetting to call `model.train()` after `model.eval()` disables dropout and switches batch normalization to use running statistics for the rest of training.

    ```python
    # ✅ Safe evaluation pattern
    was_training = model.training
    model.eval()
    with torch.no_grad():
        val_out = model(data.x, data.edge_index)
    if was_training:
        model.train()
    ```

**Dynamic batching for variable-size graphs** — If your graphs vary in size (e.g., molecular datasets, traffic networks), fixed `batch_size` can cause OOM on batches with unusually large graphs. Use PyG's dynamic batching:

```python
from torch_geometric.loader import DataLoader
from torch_geometric.data import DynamicBatchSampler

# Limit by total number of nodes per batch, not graph count
sampler = DynamicBatchSampler(dataset, max_num=2048)  # max 2048 nodes per batch
loader = DataLoader(dataset, batch_sampler=sampler)
```

This caps the total node count per batch instead of the graph count, preventing memory spikes from outlier-large graphs.

## Batch Job Script

Create `pyg_train.sh` for submitting a PyG training job:

```bash
#!/bin/bash
#SBATCH --job-name=pyg_train
#SBATCH --account=PAS1234
#SBATCH --partition=gpu
#SBATCH --gpus-per-node=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=32G
#SBATCH --time=04:00:00
#SBATCH --output=logs/pyg_train_%j.out
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=your.email@osu.edu

# Print job info
echo "Job started at: $(date)"
echo "Running on node: $(hostname)"
echo "Job ID: $SLURM_JOB_ID"

# Activate environment (PyPI torch bundles CUDA — no module load needed)
source .venv/bin/activate

# Point datasets and caches to scratch
export TORCH_HOME=/fs/scratch/PAS1234/$USER/torch_cache
export PYG_DATA_ROOT=/fs/scratch/PAS1234/$USER/pyg_datasets

# Verify GPU
nvidia-smi
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"
python -c "import torch_geometric; print(f'PyG version: {torch_geometric.__version__}')"

# Run training
python train_gcn.py \
    --data-root $PYG_DATA_ROOT \
    --epochs 200 \
    --hidden-dim 64 \
    --lr 0.01 \
    --device cuda

echo "Job completed at: $(date)"
```

Submit:

```bash
mkdir -p logs
sbatch pyg_train.sh
```

For details on SLURM directives, job arrays, and monitoring jobs, see the [Job Submission Guide](../working-on-osc/osc-job-submission.md).

## Troubleshooting

| Problem | Symptoms | Solution |
|---------|----------|----------|
| **Version mismatch** | `undefined symbol` or `ImportError` when importing `torch_scatter` / `torch_sparse` | Uninstall all PyG packages (`pip uninstall torch-scatter torch-sparse torch-cluster torch-spline-conv torch-geometric`), verify your PyTorch + CUDA versions, and reinstall with the correct wheel URL. |
| **`ModuleNotFoundError: No module named 'torch_geometric'`** | Import fails | Confirm your venv is activated (`which python` should point to your venv). Reinstall with `pip install torch-geometric`. |
| **CUDA out of memory** | `RuntimeError: CUDA out of memory` during training | Reduce batch size, use `NeighborLoader` for large graphs, enable mixed precision, or request a V100 32 GB on `gpu-exp` instead of a 16 GB on `gpu`. |
| **CUDA not available** | `torch.cuda.is_available()` returns `False` | Ensure you requested a GPU partition (`--partition=gpu --gpus-per-node=1`) and installed PyTorch with CUDA support (PyPI wheels bundle CUDA automatically). See [PyTorch & GPU Setup](pytorch-setup.md#cuda-not-available). |
| **Slow data loading** | GPU utilization low, training bottlenecked on CPU | Increase `num_workers` in `DataLoader` (match `--cpus-per-task`), enable `pin_memory=True`, cache preprocessed data to scratch as `.pt` files. |
| **Dataset download fails** | Timeout or connection error when downloading benchmark datasets | Compute nodes may lack internet access. Download datasets on the login node first (`python -c "from torch_geometric.datasets import Planetoid; Planetoid(root='...', name='Cora')"`), then point your training script to the cached path. |
| **`torch-sparse` build fails** | Compilation errors during `pip install` | You're building from source instead of using a pre-built wheel. Make sure the `-f` URL matches your exact PyTorch + CUDA versions. If no wheel exists, install build dependencies first: `pip install ninja cmake`. |
| **`Segmentation fault` on import** | Python crashes immediately when importing PyG | Almost always a version mismatch. Do a clean reinstall: uninstall everything, purge modules (`module purge`), reload, and reinstall from scratch. |

## Next Steps

- [PyTorch & GPU Setup](pytorch-setup.md) — Base PyTorch installation, GPU requesting, performance tuning, and multi-GPU training
- [Data & Experiment Tracking](data-experiment-tracking.md) — DVC, MLflow, W&B, and structured experiment logging for your GNN experiments
- [Job Submission Guide](../working-on-osc/osc-job-submission.md) — SLURM directives, job arrays, and monitoring for batch training runs
- [Environment Management](../working-on-osc/osc-environment-management.md) — Managing modules, venvs, and conda on OSC
