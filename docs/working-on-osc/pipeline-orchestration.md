<!-- last-reviewed: 2026-03-30 -->
# Pipeline Orchestration

Automate multi-step computational pipelines on OSC with proper dependency tracking, resource allocation, and failure recovery using Ray.

## When You Need an Orchestrator

| Approach | Best For | Limitations |
|----------|----------|-------------|
| **Single `sbatch` script** | One-off jobs, simple tasks | No dependency tracking, manual reruns |
| **Job arrays** | Many identical jobs with different parameters | All jobs must use same resources |
| **Dependency chains** (`--dependency`) | Sequential multi-stage pipelines | Manual setup, fragile, no partial reruns |
| **Ray** | Multi-step pipelines with complex dependencies | Initial setup time |

Use an orchestrator when your workflow has:

- Multiple steps with input/output dependencies
- Steps that need different resources (CPU vs GPU)
- Need to rerun only failed or changed steps
- Parameter sweeps combined with processing pipelines

For simpler job patterns (single jobs, job arrays, dependency chains), see [Job Submission](osc-job-submission.md).

## Ray on SLURM

[Ray](https://docs.ray.io/) is a Python-native distributed compute framework — ideal when your entire pipeline is Python and you need GPU resource management, distributed HPO, and fault tolerance.

**Why Ray for ML workloads:**

- Native SLURM integration — `ray symmetric-run` bootstraps a Ray cluster across SLURM-allocated nodes
- GPU resource management per task/actor — no manual `CUDA_VISIBLE_DEVICES` juggling
- Ray Tune for distributed hyperparameter optimization with early stopping
- Fault tolerance — tasks retry automatically on GPU failures
- Zero code change to scale from single-GPU to multi-node

### Setup

```bash
# In your project environment
source .venv/bin/activate
uv add "ray[default]>=2.49" optuna
```

No OSC module needed — Ray runs entirely from your Python environment.

## Subprocess-per-Stage Pattern

For ML pipelines, each stage (preprocessing, training, evaluation, export) benefits from running as a separate `subprocess.run()` call rather than in the same Python process. This pattern provides:

- **CUDA context isolation** — each stage gets a fresh GPU context, avoiding memory leaks between stages
- **Fault isolation** — a crash in one stage doesn't take down the orchestrator
- **Stage-level restartability** — failed stages can be retried independently
- **Clean dependency boundaries** — stages communicate through files (Parquet, checkpoints), not shared memory

```python
import subprocess
import sys

def run_stage(script: str, args: list[str] | None = None) -> None:
    """Run a pipeline stage as a subprocess."""
    cmd = [sys.executable, script] + (args or [])
    result = subprocess.run(cmd, check=True)
    if result.returncode != 0:
        raise RuntimeError(f"Stage {script} failed with code {result.returncode}")
```

### Why Not In-Process?

CUDA contexts allocate 300-500 MB of GPU memory per model that **cannot be reclaimed** without killing the process. In a 4-stage pipeline (preprocessing → training → evaluation → export), running in-process accumulates ~1.5 GB of dead GPU memory. The subprocess overhead (~3-5 seconds per stage) is negligible compared to typical stage runtimes (minutes to hours).

### Checkpoint Passing via Filesystem

Stages communicate through filesystem paths (Parquet files, model checkpoints), not shared memory or Ray object store:

```python
# Stage 1 writes a checkpoint
checkpoint_path = f"experimentruns/{dataset}/vgae_large_autoencoder/best_model.pt"
torch.save(model.state_dict(), checkpoint_path)

# Stage 2 reads it
model.load_state_dict(torch.load(checkpoint_path))
```

**Why filesystem over object store:**

- **Debuggable** — you can inspect checkpoints with standard tools
- **Restartable** — failed stages can be re-run without replaying earlier stages
- **Survives crashes** — Ray object store is ephemeral; filesystem persists
- **Subprocess-compatible** — subprocesses can't access Ray's object store directly

## Pipeline DAG Example

A training pipeline using `ray.remote` tasks with dependency chaining and fan-out per dataset:

```python
import ray

@ray.remote(num_cpus=4)
def preprocess(dataset_name: str, raw_dir: str, out_dir: str) -> str:
    """Preprocess a single dataset (CPU-only stage)."""
    import subprocess, sys
    subprocess.run(
        [sys.executable, "scripts/preprocess.py",
         "--dataset", dataset_name,
         "--raw-dir", raw_dir,
         "--out-dir", out_dir],
        check=True,
    )
    return f"{out_dir}/{dataset_name}.parquet"

@ray.remote(num_gpus=1, num_cpus=4)
def train(data_path: str, config: dict) -> str:
    """Train a model on one dataset (GPU stage)."""
    import subprocess, sys, json
    subprocess.run(
        [sys.executable, "scripts/train.py",
         "--data", data_path,
         "--config", json.dumps(config)],
        check=True,
    )
    return f"checkpoints/{config['run_name']}/best.pt"

@ray.remote(num_gpus=1)
def evaluate(model_path: str, data_path: str) -> dict:
    """Evaluate a trained model."""
    import subprocess, sys, json
    result = subprocess.run(
        [sys.executable, "scripts/evaluate.py",
         "--model", model_path,
         "--data", data_path,
         "--output", "metrics.json"],
        check=True, capture_output=True, text=True,
    )
    return json.loads(open("metrics.json").read())

if __name__ == "__main__":
    ray.init()

    datasets = ["dataset_a", "dataset_b", "dataset_c"]
    configs = [
        {"run_name": ds, "lr": 1e-3, "hidden_dim": 128}
        for ds in datasets
    ]

    # Fan-out: preprocess all datasets in parallel
    data_refs = [
        preprocess.remote(ds, "data/raw", "data/processed")
        for ds in datasets
    ]

    # Chain: train after each dataset is preprocessed
    model_refs = [
        train.remote(data_ref, cfg)
        for data_ref, cfg in zip(data_refs, configs)
    ]

    # Chain: evaluate after each model is trained
    metric_refs = [
        evaluate.remote(model_ref, data_ref)
        for model_ref, data_ref in zip(model_refs, data_refs)
    ]

    # Collect results
    metrics = ray.get(metric_refs)
    for ds, m in zip(datasets, metrics):
        print(f"{ds}: {m}")
```

## Multi-Node with `ray symmetric-run`

For multi-node jobs, Ray 2.49+ provides `ray symmetric-run` to bootstrap a Ray cluster across SLURM-allocated nodes automatically:

```bash
#!/bin/bash
#SBATCH --job-name=ray_pipeline
#SBATCH --account=PAS1234
#SBATCH --nodes=2
#SBATCH --gpus-per-node=4
#SBATCH --cpus-per-task=32
#SBATCH --time=08:00:00
#SBATCH --output=logs/ray_pipeline_%j.out

source .venv/bin/activate

# ray symmetric-run starts Ray on all SLURM nodes, then runs your script
srun --nodes=$SLURM_JOB_NUM_NODES --ntasks=$SLURM_JOB_NUM_NODES \
    ray symmetric-run -- python pipeline.py
```

For single-node jobs (1-4 GPUs), `ray.init()` works out of the box — no special setup:

```bash
#!/bin/bash
#SBATCH --nodes=1 --gpus-per-node=1 --cpus-per-task=8
#SBATCH --time=04:00:00 --account=PAS1234

source .venv/bin/activate
python pipeline.py
```

## Ray Tune for HPO

Ray Tune provides distributed hyperparameter optimization with Optuna search and ASHA early stopping:

```python
from ray import tune
from ray.tune.search.optuna import OptunaSearch

def train_fn(config):
    import ray.train
    # ... build model from config, train one epoch at a time ...
    for epoch in range(100):
        loss, f1 = train_one_epoch(config)
        ray.train.report({"val_f1": f1, "val_loss": loss})

tuner = tune.Tuner(
    tune.with_resources(train_fn, {"gpu": 1, "cpu": 4}),
    tune_config=tune.TuneConfig(
        search_alg=OptunaSearch(metric="val_f1", mode="max"),
        scheduler=tune.schedulers.ASHAScheduler(
            max_t=100, grace_period=10, reduction_factor=3,
        ),
        num_samples=50,
        max_concurrent_trials=4,  # match available GPUs
    ),
    param_space={
        "lr": tune.loguniform(1e-5, 1e-2),
        "hidden_dim": tune.choice([64, 128, 256]),
        "dropout": tune.uniform(0.1, 0.5),
    },
)
results = tuner.fit()
print(f"Best F1: {results.get_best_result('val_f1', 'max').metrics['val_f1']}")
```

!!! tip "W&B integration"
    Ray Tune integrates with Weights & Biases via `WandbLoggerCallback`:
    ```python
    from ray.air.integrations.wandb import WandbLoggerCallback

    tuner = tune.Tuner(
        train_fn,
        run_config=tune.RunConfig(
            callbacks=[WandbLoggerCallback(project="my-hpo")]
        ),
        # ... rest of config ...
    )
    ```

## Benchmark Mode

Add per-stage timing and GPU snapshots with an environment variable toggle:

```python
import os
import time
import torch

BENCHMARK = os.environ.get("BENCHMARK", "0") == "1"

def benchmark_stage(name: str):
    """Context manager for timing a pipeline stage."""
    class _Timer:
        def __enter__(self):
            if BENCHMARK:
                torch.cuda.synchronize() if torch.cuda.is_available() else None
                self.start = time.perf_counter()
            return self

        def __exit__(self, *args):
            if BENCHMARK:
                torch.cuda.synchronize() if torch.cuda.is_available() else None
                elapsed = time.perf_counter() - self.start
                gpu_mem = (torch.cuda.max_memory_allocated() / 1e9
                           if torch.cuda.is_available() else 0)
                print(f"[BENCH] {name}: {elapsed:.1f}s, GPU peak: {gpu_mem:.2f} GB")
    return _Timer()
```

Enable in your SLURM script:

```bash
export BENCHMARK=1
python pipeline.py
```

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| Worker OOM | Ray worker runs out of memory | Increase `--mem` in SLURM script, or reduce `num_cpus`/`num_gpus` per task so fewer tasks run concurrently |
| `ray.get()` timeout | Task takes longer than expected | Set `ray.get(ref, timeout=None)` for long tasks, or increase the timeout |
| Temp dir fills up | Ray writes to `/tmp` by default | Set `ray.init(configure_logging=True, _temp_dir="/fs/scratch/PAS1234/$USER/ray_tmp")` |
| "No available node" | Requested more GPUs than available | Check `ray.cluster_resources()` and reduce `num_gpus` per task |
| Port conflict | Multiple Ray clusters on same node | Let Ray auto-select ports: `ray.init(dashboard_port=0)` |
| Stale Ray cluster | Previous run left orphaned processes | Run `ray stop --force` before starting a new cluster |

## Next Steps

- [Job Submission](osc-job-submission.md) — SLURM fundamentals, job arrays, dependency chains
- [ML Project Template](../ml-workflows/ml-workflow.md) — project structure for ML experiments
- [Data & Experiment Tracking](../ml-workflows/data-experiment-tracking.md) — W&B, DVC, DuckDB analytics
- [DuckDB Analytics Layer](../ml-workflows/duckdb-analytics.md) — querying experiment results with SQL
