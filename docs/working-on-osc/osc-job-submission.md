---
status: updated
tags:
  - SLURM
  - OSC
  - GPU
---
<!-- last-reviewed: 2026-05-09 -->
# Job Submission Guide

Use SLURM to run interactive tests, batch jobs, and GPU training on OSC.

## Quick Start

### Interactive

Use `sinteractive` when you want a shell on a compute node:

```bash
sinteractive -A PAS1234 -c 4 -t 01:00:00
sinteractive -A PAS1234 -c 4 -g 1 -t 01:00:00
```

### Batch

Use `sbatch` for real work:

```bash
#!/bin/bash
#SBATCH --job-name=my_job
#SBATCH --account=PAS1234
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=4
#SBATCH --time=02:00:00
#SBATCH --output=logs/job_%j.out

module load python/3.12
source .venv/bin/activate
python train.py
```

## SLURM Basics

### Core Commands

```bash
sbatch job.sh
srun -p partition --pty bash
squeue -u $USER
scancel <job_id>
scontrol show job <job_id>
seff <job_id>
```

### Job States

- `PD` pending
- `R` running
- `CG` completing
- `CD` completed
- `F` failed
- `CA` cancelled

## Job Scripts

### Must-Knows

- `#SBATCH` lines must come before the first executable line
- `--account` and `--time` are required in most submissions
- SLURM stops reading directives after the first non-comment line

### Useful Directives

| Directive | Use |
|---|---|
| `--nodes` | Usually `1` |
| `--ntasks-per-node` | Usually `1` for Python jobs |
| `--cpus-per-task` | DataLoader workers, preprocessing threads |
| `--gpus-per-node` | GPU count or GPU type |
| `--mem` | RAM per node |
| `--partition` | Queue selection |
| `--output` / `--error` | Log files |
| `--array` | Repeated tasks |
| `--dependency` | Chained jobs |
| `--signal=B:USR1@300` | Graceful checkpointing |

## Common Patterns

### GPU Job

```bash
#!/bin/bash
#SBATCH --job-name=gpu_training
#SBATCH --account=PAS1234
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --gpus-per-node=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=32G
#SBATCH --time=04:00:00

module load python/3.12
source ~/venvs/pytorch/bin/activate
python train.py --device cuda
```

### Checkpoint Resume

Save checkpoints during training and resume from the newest one when the job restarts. Use `--signal=B:USR1@300` if you need a final save before walltime.

### Data Processing

For CPU-heavy preprocessing, request more CPUs and memory, then stage data to faster storage if I/O becomes the bottleneck.

## Good Habits

- Use `sbatch --parsable` in scripts that launch other jobs
- Keep interactive sessions short and `exit` when done
- Verify your job is actually on a compute node before running heavy code
- Prefer shorter walltimes when you want faster backfill scheduling

## Next Steps

- [Environment Management](osc-environment-management.md)
- [PyTorch & PyG Setup](../ml-workflows/pytorch-setup.md)
- [HPC Training Nuances](../ml-workflows/hpc-training-nuances.md)
