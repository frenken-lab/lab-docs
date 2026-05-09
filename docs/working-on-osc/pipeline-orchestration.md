---
last-reviewed: 2026-05-09
---
<!-- last-reviewed: 2026-05-09 -->
# Pipeline Orchestration

Use an orchestrator when a workflow has multiple dependent stages, mixed resource needs, or expensive reruns. For one-off jobs, arrays, and simple dependency chains, SLURM alone is usually enough.

## When to Use Ray

Ray is the easiest fit when the pipeline is mostly Python and you want:

- stage-level dependencies
- CPU and GPU tasks in one workflow
- parallel fan-out over many datasets or configs
- distributed HPO with early stopping

## Simple Pattern

Keep each stage as a separate subprocess so failures stay isolated and checkpoints live on disk instead of in memory.

```python
import subprocess, sys

def run_stage(script: str, *args: str) -> None:
    subprocess.run([sys.executable, script, *args], check=True)
```

Use files for handoff between stages:

- Parquet for tabular outputs
- checkpoints for model state
- JSON or CSV for small metadata

## Ray on SLURM

```bash
source .venv/bin/activate
uv add "ray[default]>=2.49" optuna
```

For one node, `ray.init()` is enough. For multiple nodes, `ray symmetric-run` can bootstrap the cluster from an allocation.

```bash
srun --nodes=$SLURM_JOB_NUM_NODES --ntasks=$SLURM_JOB_NUM_NODES \
    ray symmetric-run -- python pipeline.py
```

## Ray Tune

Use Ray Tune when you want distributed hyperparameter search.

- pair `OptunaSearch` with `ASHA` for a solid default
- keep `max_concurrent_trials` aligned with available GPUs
- report metrics each epoch with `ray.train.report(...)`

## Benchmarking

Toggle a `BENCHMARK=1` environment variable to print stage timing and peak GPU memory. Keep the instrumentation lightweight so it does not affect normal runs.

## Troubleshooting

| Problem | Typical fix |
|---|---|
| Worker OOM | Reduce task concurrency or increase memory |
| `ray.get()` timeout | Raise the timeout or make the stage faster |
| Temp directory fills up | Point Ray at scratch |
| No available node | Reduce requested GPUs |
| Port conflict | Let Ray auto-select the port |
| Stale cluster | `ray stop --force` |

## Next Steps

- [Job Submission](osc-job-submission.md) for SLURM basics
- [ML Project Workflow](../ml-workflows/ml-workflow.md) for project structure and tracking
- [HPC Training Nuances](../ml-workflows/hpc-training-nuances.md) for scheduler gotchas
