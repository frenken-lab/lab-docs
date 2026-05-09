---
status: new
---
<!-- last-reviewed: 2026-05-09 -->
# HPC Training Nuances

Short version: pick the right cluster, trust scheduler timestamps, and leave yourself a clean shutdown path.

These are the recurring gotchas that matter most once you start real training runs on OSC.

---

## Cluster Choice

Choose the cluster that matches the job, not the one you happen to be logged into.

- Use the largest GPU/memory tier that fits the model and batch size
- Prefer the cluster with shorter queue time for repeated experiments
- Move heavy training to the newer hardware when you do not need Pitzer-specific modules

## Scheduler Reality

`Reason=Priority` means “queued by priority,” not “starting soon.”

Before waiting on a queue, check the projected start time:

```bash
scontrol show job <jid> | grep StartTime
```

If the start time is hours away, lower the request or switch clusters.

## Shared Storage, Not Shared Job IDs

Files on ESS can be read from any OSC cluster, so checkpoints and datasets are portable.

- Stage outputs on shared storage
- Do not rely on `afterok` across clusters
- If you hop clusters in one pipeline, use a sentinel file or submit stages manually

## Numerical Stability

Mixed precision is useful, but it can surface dataset-specific overflows.

- Use fp16/autocast when it works
- Switch to fp32 if a model starts emitting `NaN`
- Try bf16 on hardware that supports it

## Job Hygiene

Keep training jobs easy to resume and easy to debug.

- Use `sbatch --parsable` for machine-readable job IDs
- Add a walltime signal so the job can save a final checkpoint
- Keep evaluation and inference paths separate from training-only CUDA probes

## MLflow and Parent Runs

If a child job runs in a separate process, pass the parent run ID through the environment instead of relying on nested runs.

```bash
rid=$(python -m graphids mlflow-start-parent --group X --variant Y --dataset D)
MLFLOW_PARENT_RUN_ID="$rid" sbatch ... --wrap "python -m graphids fit ..."
```

