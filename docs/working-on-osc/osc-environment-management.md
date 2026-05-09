---
tags:
  - OSC
  - uv
---
<!-- last-reviewed: 2026-05-09 -->
# Environment Management

Use OSC modules for system software and `uv` or `venv` for project-specific Python environments.

## The Two Main Choices

1. Modules for preinstalled tools
2. Virtual environments for project packages

If you need RAPIDS, keep it in a separate conda environment. Do not mix RAPIDS and PyTorch in the same env.

## Modules

Useful commands:

```bash
module avail
module spider python
module load python/3.12
module load cuda/12.4
module list
module purge
```

### Important Note

You usually do **not** need `module load cuda` for PyTorch wheels from PyPI. Only load CUDA when compiling custom CUDA extensions or when a specific workflow explicitly needs it.

## uv

`uv` is the preferred way to manage project environments on OSC.

```bash
uv venv --python /apps/python/3.12/bin/python3
source .venv/bin/activate
uv sync
uv add numpy pandas matplotlib
```

### uv Rules on OSC

- Use OSC's system Python path with `uv venv`
- Do not rely on uv-managed Python downloads
- Keep `pyproject.toml` and `uv.lock` in version control

## venv + pip

```bash
module load python/3.12
python -m venv ~/venvs/myproject
source ~/venvs/myproject/bin/activate
pip install numpy pandas matplotlib
```

## RAPIDS Exception

RAPIDS is conda-only. Use a separate conda environment for preprocessing jobs, then pass files to your PyTorch environment.

## Environments in Job Scripts

```bash
#!/bin/bash
#SBATCH --job-name=my_job
#SBATCH --time=02:00:00

module load python/3.12
source .venv/bin/activate
python train.py
```

## Troubleshooting

- `module: command not found` usually means the module system is not initialized
- If `uv venv` segfaults, you probably did not use OSC's system Python path
- If PyTorch does not see CUDA, confirm you are on a GPU node and installed the PyPI torch wheels
- If a package install fails, check disk quota and upgrade `pip`

## Secrets

Keep API keys out of source code:

```bash
export API_KEY="your_key_here"
```

```python
import os
api_key = os.environ["API_KEY"]
```

## Next Steps

- [PyTorch & GPU Setup](../ml-workflows/pytorch-setup.md)
- [Job Submission Guide](osc-job-submission.md)
