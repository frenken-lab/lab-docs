---
status: updated
tags:
  - PyTorch
  - GPU
  - CUDA
  - OSC
---
<!-- last-reviewed: 2026-03-30 -->
# PyTorch & GPU Setup

Everything you need to install PyTorch, request GPUs, and train efficiently on OSC.

## Prerequisites

- OSC account with GPU access
- SSH connection configured
- Basic familiarity with Python and PyTorch

## Quick Setup

=== "uv (Recommended)"

    ```bash
    # 1. Create venv with OSC's system Python (never use uv-managed Python on OSC)
    uv venv --python /apps/python/3.12/bin/python3

    # 2. Activate
    source .venv/bin/activate

    # 3. Install PyTorch (PyPI wheels bundle CUDA — no module load cuda needed)
    uv add "torch>=2.8.0,<2.9" torchvision torchaudio

    # 4. Install common ML packages
    uv add numpy pandas matplotlib scikit-learn jupyter tensorboard
    ```

=== "pip + venv"

    ```bash
    # 1. Load Python module
    module load python/3.12

    # 2. Create virtual environment
    python -m venv ~/venvs/pytorch

    # 3. Activate
    source ~/venvs/pytorch/bin/activate

    # 4. Install PyTorch (PyPI wheels bundle CUDA — no --index-url needed)
    pip install --upgrade pip
    pip install "torch>=2.8.0,<2.9" torchvision torchaudio

    # 5. Install common ML packages
    pip install numpy pandas matplotlib scikit-learn jupyter tensorboard
    ```

!!! tip "No `module load cuda` needed with PyPI torch"
    PyTorch wheels on PyPI bundle their own NVIDIA libraries. You do **not** need `module load cuda` or `--index-url` pytorch wheel URLs. Only load a CUDA module if you are compiling custom CUDA extensions or using venv/pip with the legacy pytorch wheel index.

!!! warning "Version Constraint Triangle (PyTorch + PyG + CUDA)"
    If you plan to use PyTorch Geometric (PyG), there is a **three-way version coupling** between PyTorch, PyG extension wheels, and CUDA. PyPI may ship torch 2.10+ but PyG only has compiled wheels up to torch 2.8.0. Installing mismatched versions compiles fine but **segfaults at runtime** (silent C++ ABI mismatch). Always check [data.pyg.org/whl/](https://data.pyg.org/whl/) for the latest torch version supported by PyG before upgrading. See [PyG Setup](pyg-setup.md) for full details.

## Detailed Setup

### Step 1: Create Virtual Environment

=== "uv (Recommended)"

    ```bash
    # Use OSC's system Python (never uv-managed Python on OSC)
    uv venv --python /apps/python/3.12/bin/python3
    source .venv/bin/activate
    ```

=== "venv + pip"

    ```bash
    module load python/3.12
    python -m venv ~/venvs/pytorch
    source ~/venvs/pytorch/bin/activate
    pip install --upgrade pip
    ```

### Step 2: Install PyTorch

PyTorch wheels on PyPI now bundle CUDA libraries. No `--index-url` or `module load cuda` is needed.

```bash
# uv
uv add "torch>=2.8.0,<2.9" torchvision torchaudio

# pip
pip install "torch>=2.8.0,<2.9" torchvision torchaudio
```

### Step 3: Install Additional Packages

For graph neural network libraries (PyTorch Geometric), see the [PyG Setup Guide](pyg-setup.md).

```bash
# Core scientific packages
pip install numpy pandas matplotlib seaborn

# Machine learning utilities
pip install scikit-learn scipy

# Deep learning tools
pip install tensorboard wandb

# Jupyter for notebooks
pip install jupyter ipykernel

# Computer vision
pip install opencv-python pillow

# NLP (if needed)
pip install transformers datasets tokenizers

# Optimization and monitoring
pip install tqdm pytorch-lightning
```

### Step 4: Verify Installation

Create `test_pytorch.py`:

```python
import torch
import torchvision

print("=" * 50)
print("PyTorch Installation Test")
print("=" * 50)

print(f"\nPyTorch version: {torch.__version__}")
print(f"Torchvision version: {torchvision.__version__}")
print(f"CUDA available: {torch.cuda.is_available()}")

if torch.cuda.is_available():
    print(f"CUDA version: {torch.version.cuda}")
    print(f"Number of GPUs: {torch.cuda.device_count()}")
    print(f"Current GPU: {torch.cuda.current_device()}")
    print(f"GPU name: {torch.cuda.get_device_name(0)}")

    # Test tensor operations
    print("\nTesting GPU operations...")
    x = torch.rand(5, 3)
    print(f"CPU tensor shape: {x.shape}")

    x_gpu = x.cuda()
    print(f"GPU tensor device: {x_gpu.device}")
    print("GPU operations working!")
else:
    print("\nCUDA not available. Running on CPU.")

print("\n" + "=" * 50)
```

Test on GPU node:

```bash
# Request GPU node
srun -p gpu --gpus-per-node=1 --time=00:10:00 --pty bash

# Activate environment
source .venv/bin/activate  # uv
# or: source ~/venvs/pytorch/bin/activate  # venv + pip

# Run test
python test_pytorch.py

# Exit
exit
```

## Requesting GPUs

### Available GPU Types

#### Pitzer (Current)

| GPU Model | Memory | Partition | Nodes | Best For |
|-----------|--------|-----------|-------|----------|
| NVIDIA V100 | 16 GB | `gpu` | 32 | General training |
| NVIDIA V100 | 32 GB | `gpu-exp` | 42 | Larger models, bigger batches |
| NVIDIA V100 (×4, NVLink) | 32 GB | `gpu-quad` | 4 | Multi-GPU training |

#### Ascend / Cardinal (Newer — may require separate allocation)

| GPU Model | Memory | Best For |
|-----------|--------|----------|
| NVIDIA A100 | 40 / 80 GB | Transformers, large-model training |
| NVIDIA H100 | 94 GB | Latest generation, highest throughput |

See the [Clusters Overview](../osc-basics/osc-clusters-overview.md) for full specs and access details.

### Interactive GPU Session

```bash
# Request any available GPU on Pitzer
srun -p gpu --gpus-per-node=1 --time=01:00:00 --pty bash

# Request V100 32 GB specifically
srun -p gpu-exp --gpus-per-node=1 --time=01:00:00 --pty bash

# Request multiple GPUs (quad nodes)
srun -p gpu-quad --gpus-per-node=2 --time=01:00:00 --pty bash

# With more CPUs and memory
srun -p gpu --gpus-per-node=1 --cpus-per-task=8 --mem=64G --time=02:00:00 --pty bash
```

### Batch Job

```bash
#!/bin/bash
#SBATCH --job-name=gpu_job
#SBATCH --partition=gpu
#SBATCH --gpus-per-node=1           # Any available GPU
# #SBATCH --gpus-per-node=v100:1   # OR: request specific GPU type
#SBATCH --cpus-per-task=4           # CPUs (for data loading)
#SBATCH --mem=32G                   # Memory
#SBATCH --time=08:00:00

# Your GPU job commands
```

## Monitoring GPUs

### Using nvidia-smi

```bash
# Basic GPU info
nvidia-smi

# Continuous monitoring
watch -n 1 nvidia-smi

# Specific GPU
nvidia-smi -i 0

# Show processes
nvidia-smi pmon

# Detailed query
nvidia-smi --query-gpu=index,name,memory.total,memory.used,memory.free,utilization.gpu --format=csv
```

### Using Python

```python
import torch

# Check CUDA availability
print(f"CUDA available: {torch.cuda.is_available()}")
print(f"CUDA version: {torch.version.cuda}")

# GPU information
print(f"Number of GPUs: {torch.cuda.device_count()}")
for i in range(torch.cuda.device_count()):
    print(f"GPU {i}: {torch.cuda.get_device_name(i)}")
    print(f"  Memory: {torch.cuda.get_device_properties(i).total_memory / 1e9:.2f} GB")

# Memory usage
print(f"Allocated: {torch.cuda.memory_allocated(0) / 1e9:.2f} GB")
print(f"Cached: {torch.cuda.memory_reserved(0) / 1e9:.2f} GB")
```

### GPU Selection

```bash
# Use specific GPU
export CUDA_VISIBLE_DEVICES=0

# Use multiple GPUs
export CUDA_VISIBLE_DEVICES=0,1
```

```python
# In Python
import os
os.environ['CUDA_VISIBLE_DEVICES'] = '0'

# Or use device parameter
device = torch.device('cuda:0')
```

## Performance

### Data Loading Optimization

```python
from torch.utils.data import DataLoader

# Use multiple workers (match CPUs requested)
train_loader = DataLoader(
    dataset,
    batch_size=64,
    shuffle=True,
    num_workers=4,        # Match --cpus-per-task
    pin_memory=True,      # Faster GPU transfer
    prefetch_factor=2,    # Prefetch batches
    persistent_workers=True  # Keep workers alive
)
```

### Mixed Precision Training

Mixed precision uses FP16 where possible, saving memory and speeding up training.

```python
from torch.cuda.amp import autocast, GradScaler

scaler = GradScaler()

for epoch in range(num_epochs):
    for data, target in train_loader:
        data, target = data.cuda(), target.cuda()

        optimizer.zero_grad()

        # Forward pass in mixed precision
        with autocast():
            output = model(data)
            loss = criterion(output, target)

        # Backward pass with scaling
        scaler.scale(loss).backward()
        scaler.step(optimizer)
        scaler.update()
```

!!! danger "Mixed Precision Gotchas"
    FP16 has a much smaller dynamic range than FP32 (max ±65504). Two common traps (see [PyTorch AMP docs](https://pytorch.org/docs/stable/amp.html)):

    1. **Intermediate overflow** — Operations that accumulate large values (reductions, layer norms, custom statistics) can overflow FP16, producing `inf` or `NaN`. PyTorch's autocast keeps some ops in FP32 automatically, but custom operations may need explicit `.float()` casts.

    2. **Loss scaling failures** — If `GradScaler` repeatedly skips optimizer steps (logged as "Found inf/nan in gradients"), your loss magnitude may exceed FP16 range. The default `init_scale` is `2**16` ([GradScaler docs](https://pytorch.org/docs/stable/amp.html#torch.cuda.amp.GradScaler)); lowering it (e.g., `2**10`) can help stabilize early training.

### CUDA Memory Allocator

For models with variable-size inputs (GNNs, NLP with dynamic padding), set the [CUDA memory allocator](https://pytorch.org/docs/stable/notes/cuda.html#memory-management) to reduce fragmentation:

```bash
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
```

See the [Job Submission Guide](../working-on-osc/osc-job-submission.md#cuda-memory-configuration) for a full explanation of allocator settings.

### Multiprocessing with CUDA

PyTorch with CUDA requires `spawn` (not `fork`) for multiprocessing when child processes use the GPU. Forking after CUDA initialization corrupts GPU state — see [PyTorch multiprocessing notes](https://pytorch.org/docs/stable/notes/multiprocessing.html#cuda-in-multiprocessing).

```python
# At the top of your main script
import torch.multiprocessing as mp
mp.set_start_method("spawn", force=True)
```

If you use PyTorch Lightning, set it in the Trainer:

```yaml
# In your config YAML
trainer:
  strategy:
    class_path: pytorch_lightning.strategies.DDPStrategy
    init_args:
      start_method: spawn
```

!!! warning "DataLoader workers are different"
    `DataLoader(num_workers=N)` uses `fork` by default. This is generally safe because worker processes typically don't initialize CUDA themselves — they load data on CPU. The `spawn` requirement applies when you explicitly create processes that use GPUs (e.g., distributed training, Ray actors with GPU resources).

### Gradient Accumulation

Simulate larger batch sizes without more GPU memory:

```python
accumulation_steps = 4  # Effective batch size = batch_size * 4

for i, (data, target) in enumerate(train_loader):
    data, target = data.cuda(), target.cuda()

    # Forward pass
    output = model(data)
    loss = criterion(output, target)

    # Scale loss and backward
    loss = loss / accumulation_steps
    loss.backward()

    # Update weights every accumulation_steps
    if (i + 1) % accumulation_steps == 0:
        optimizer.step()
        optimizer.zero_grad()
```

### torch.compile() (PyTorch 2.0+)

`torch.compile()` JIT-compiles your model for faster execution with minimal code changes.

```python
import torch

model = MyModel().cuda()

# Basic usage — tries the best available backend
model = torch.compile(model)

# Specify backend explicitly
model = torch.compile(model, backend="inductor")  # Default, good general choice

# Max performance (longer compile time, best runtime)
model = torch.compile(model, mode="max-autotune")
```

!!! warning "Requires PyTorch 2.0+"
    `torch.compile()` is only available in PyTorch 2.0 and later. Check your version with `torch.__version__`. If you're using an older version, upgrade with:
    ```bash
    pip install --upgrade "torch>=2.8.0,<2.9" torchvision torchaudio
    ```

!!! tip "V100 and newer GPUs benefit most"
    `torch.compile()` with `mode="max-autotune"` leverages GPU-specific optimizations. V100s on Pitzer support this; A100s on Ascend (if you have access) benefit even more from TF32 tensor cores.

??? tip "Gradient Checkpointing"

    Save memory by recomputing activations during backward pass:

    ```python
    import torch.utils.checkpoint as checkpoint

    class MyModel(nn.Module):
        def forward(self, x):
            # Use checkpointing for memory-intensive layers
            x = checkpoint.checkpoint(self.layer1, x)
            x = checkpoint.checkpoint(self.layer2, x)
            return x
    ```

??? tip "Profiling with PyTorch Profiler"

    ```python
    import torch.profiler

    with torch.profiler.profile(
        activities=[
            torch.profiler.ProfilerActivity.CPU,
            torch.profiler.ProfilerActivity.CUDA,
        ],
        record_shapes=True,
        profile_memory=True,
        with_stack=True
    ) as prof:
        for i in range(10):
            output = model(input)
            loss = criterion(output, target)
            loss.backward()
            optimizer.step()

    # Print results
    print(prof.key_averages().table(sort_by="cuda_time_total", row_limit=10))

    # Save trace for visualization
    prof.export_chrome_trace("trace.json")
    # View at chrome://tracing
    ```

## Multi-GPU Training

### DataParallel (Simple, Single Node)

```python
import torch.nn as nn

model = MyModel()

# Wrap model for multi-GPU
if torch.cuda.device_count() > 1:
    print(f"Using {torch.cuda.device_count()} GPUs")
    model = nn.DataParallel(model)

model = model.cuda()

# Train as usual
for data, target in train_loader:
    output = model(data.cuda())  # Automatically distributed
    loss = criterion(output, target.cuda())
    loss.backward()
    optimizer.step()
```

Job script:
```bash
#SBATCH --gpus-per-node=4
```

### DistributedDataParallel (Recommended)

More efficient than DataParallel:

```python
import torch.distributed as dist
from torch.nn.parallel import DistributedDataParallel as DDP
from torch.utils.data.distributed import DistributedSampler

def setup(rank, world_size):
    os.environ['MASTER_ADDR'] = 'localhost'
    os.environ['MASTER_PORT'] = '12355'
    dist.init_process_group("nccl", rank=rank, world_size=world_size)

def cleanup():
    dist.destroy_process_group()

def train(rank, world_size):
    setup(rank, world_size)

    # Create model and move to GPU
    model = MyModel().to(rank)
    ddp_model = DDP(model, device_ids=[rank])

    # Use DistributedSampler
    sampler = DistributedSampler(dataset, num_replicas=world_size, rank=rank)
    dataloader = DataLoader(dataset, sampler=sampler, batch_size=64)

    # Training loop
    for epoch in range(num_epochs):
        sampler.set_epoch(epoch)  # Shuffle differently each epoch
        for data, target in dataloader:
            data, target = data.to(rank), target.to(rank)
            output = ddp_model(data)
            loss = criterion(output, target)
            loss.backward()
            optimizer.step()
            optimizer.zero_grad()

    cleanup()

if __name__ == '__main__':
    world_size = torch.cuda.device_count()
    torch.multiprocessing.spawn(train, args=(world_size,), nprocs=world_size)
```

Job script:
```bash
#!/bin/bash
#SBATCH --gpus-per-node=4
#SBATCH --ntasks-per-node=4

# torchrun replaces the deprecated torch.distributed.launch
torchrun --nproc_per_node=4 train_ddp.py
```

## Memory Management

### Check Memory Usage

```python
import torch

# Current GPU memory usage
print(f"Allocated: {torch.cuda.memory_allocated(0) / 1e9:.2f} GB")
print(f"Cached: {torch.cuda.memory_reserved(0) / 1e9:.2f} GB")

# Peak memory usage
print(f"Max allocated: {torch.cuda.max_memory_allocated(0) / 1e9:.2f} GB")

# Detailed memory summary
print(torch.cuda.memory_summary(device=0, abbreviated=False))
```

### Clear GPU Memory

```python
# Clear cache
torch.cuda.empty_cache()

# Delete tensors explicitly
del large_tensor
torch.cuda.empty_cache()

# Move to CPU and delete
large_tensor = large_tensor.cpu()
del large_tensor
torch.cuda.empty_cache()
```

### Memory-Efficient Practices

```python
# 1. Use in-place operations
x.add_(y)  # Instead of x = x + y

# 2. Use torch.no_grad() for inference
with torch.no_grad():
    output = model(input)

# 3. Clear gradients efficiently
optimizer.zero_grad(set_to_none=True)  # More memory efficient

# 4. Set memory fraction
torch.cuda.set_per_process_memory_fraction(0.8, device=0)
```

## Using PyTorch in Jobs

### Batch Job Script

Create `pytorch_job.sh`:

```bash
#!/bin/bash
#SBATCH --job-name=pytorch_train
#SBATCH --account=PAS1234
#SBATCH --nodes=1
#SBATCH --gpus-per-node=1
#SBATCH --time=04:00:00
#SBATCH --output=logs/train_%j.out
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=your.email@osu.edu

# Print job info
echo "Job started at: $(date)"
echo "Running on node: $(hostname)"
echo "Job ID: $SLURM_JOB_ID"

# Activate environment (PyPI torch bundles CUDA — no module load cuda needed)
source .venv/bin/activate

# Verify GPU
nvidia-smi
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"

# Run training
python train.py \
    --data-path /fs/scratch/PAS1234/$USER/data \
    --epochs 100 \
    --batch-size 64 \
    --lr 0.001 \
    --device cuda

echo "Job completed at: $(date)"
```

Submit:
```bash
mkdir -p logs
sbatch pytorch_job.sh
```

## Checkpointing

### Save Checkpoints

```python
def save_checkpoint(model, optimizer, epoch, loss, path):
    torch.save({
        'epoch': epoch,
        'model_state_dict': model.state_dict(),
        'optimizer_state_dict': optimizer.state_dict(),
        'loss': loss,
    }, path)

# Save every N epochs
if epoch % 10 == 0:
    save_checkpoint(
        model, optimizer, epoch, loss,
        f'checkpoints/epoch_{epoch}.pth'
    )

# Save best model
if loss < best_loss:
    save_checkpoint(
        model, optimizer, epoch, loss,
        'checkpoints/best_model.pth'
    )
```

### Load Checkpoints

```python
def load_checkpoint(model, optimizer, path):
    checkpoint = torch.load(path)
    model.load_state_dict(checkpoint['model_state_dict'])
    optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
    epoch = checkpoint['epoch']
    loss = checkpoint['loss']
    return epoch, loss

# Resume training
if os.path.exists('checkpoints/best_model.pth'):
    epoch, loss = load_checkpoint(model, optimizer, 'checkpoints/best_model.pth')
    print(f"Resumed from epoch {epoch}")
```

## Troubleshooting

Common failure modes and their fixes. Click an entry to expand.

<details class="collapsible-issue" markdown id="cuda-out-of-memory">
<summary>CUDA Out of Memory</summary>

**Symptoms:**
```
RuntimeError: CUDA out of memory
```

**Solutions:**

1. **Reduce batch size**
   ```python
   batch_size = 32  # Instead of 64
   ```

2. **Use gradient accumulation**
   ```python
   accumulation_steps = 2  # Effective batch size = 64
   ```

3. **Use mixed precision**
   ```python
   from torch.cuda.amp import autocast
   with autocast():
       output = model(input)
   ```

4. **Clear cache**
   ```python
   torch.cuda.empty_cache()
   ```

5. **Use gradient checkpointing**
   ```python
   model.gradient_checkpointing_enable()
   ```

6. **Reduce model size**

</details>

<details class="collapsible-issue" markdown id="cuda-not-available">
<summary>CUDA Not Available</summary>

**Checks:**

```bash
# 1. Verify you're on a GPU node (not a login node)
squeue -u $USER

# 2. Check node has GPU
nvidia-smi

# 3. Check PyTorch sees CUDA
python -c "import torch; print(torch.cuda.is_available())"

# 4. If still failing, reinstall PyTorch
pip uninstall torch torchvision torchaudio
pip install "torch>=2.8.0,<2.9" torchvision torchaudio
```

!!! note "You do NOT need `module load cuda` for PyPI torch"
    If you installed PyTorch from PyPI (via `pip install` or `uv add`), the wheels bundle their own CUDA libraries. `module load cuda` is only needed if you are compiling custom CUDA extensions (e.g. custom C++/CUDA kernels). If `torch.cuda.is_available()` returns False, the most common cause is running on a login node instead of a GPU compute node.

</details>

<details class="collapsible-issue" markdown id="slow-training">
<summary>Slow Training</summary>

**Common issues:**
- Too few data loader workers
- Not using pin_memory
- Not using mixed precision
- CPU-GPU transfer bottleneck

**Diagnose:**

```python
# Profile to find bottlenecks
import torch.profiler
with torch.profiler.profile() as prof:
    train_one_epoch()
print(prof.key_averages().table())
```

</details>

<details class="collapsible-issue" markdown id="module-import-errors">
<summary>Module Import Errors</summary>

```bash
# Verify environment activated
which python  # Should point to venv

# Reinstall package
pip install --force-reinstall torch

# Check Python path
python -c "import sys; print('\n'.join(sys.path))"
```

</details>

## Best Practices

1. **Always use virtual environments**
2. **Test on GPU node before batch submission**
3. **Save checkpoints regularly**
4. **Use mixed precision for faster training**
5. **Monitor GPU usage** with `nvidia-smi`
6. **Don't over-request GPUs** you won't use
7. **Use appropriate batch size** for your GPU memory
8. **Pin memory and use multiple workers** for data loading
9. **Profile before optimizing** — find actual bottlenecks
10. **Document your environment** in requirements.txt

## Next Steps

- Read [ML Workflow Guide](ml-workflow.md)
- Review [Job Submission](../working-on-osc/osc-job-submission.md)

## Resources

- [PyTorch Performance Tuning Guide](https://pytorch.org/tutorials/recipes/recipes/tuning_guide.html) — hard-to-find, detailed optimization recipes
