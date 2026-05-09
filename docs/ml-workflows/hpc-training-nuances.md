---
status: new
---
<!-- last-reviewed: 2026-04-21 -->
# HPC Training Nuances

Practical lessons learned about ML training on OSC clusters. This page
complements [OSC Clusters Overview](../osc-basics/osc-clusters-overview.md)
(what each cluster is) with the operational gotchas that only surface
once you've run real ablation campaigns.

Each section opens with a one-line rule, then a concrete case study from
an actual failure or surprise. Contribute your own when a debug session
teaches you something worth sharing.

---

## 1. Cluster choice dominates wall-clock

**Rule**: pick the cluster that matches your workload's memory and
throughput profile, not the one you happen to have logged into.

For graph attention models on the `set_01` CAN-bus dataset:

| Cluster | GPU | VRAM | VGAE 1200-ep wall-clock | Typical queue wait |
|---|---|---|---|---|
| Pitzer | V100 | 16 GB | ~2.5–3 h | 30 min–hours (backlog-prone) |
| Ascend | A100 | 40/80 GB | ~45 min | minutes–hours |
| Cardinal | H100 | 94 GB | ~45 min | minutes |

On set_01, a single batch needs ~48 GB of VRAM on H100 (~50% utilization),
so Cardinal can fit the entire working set in one forward pass. V100's
16 GB forces 3× more batches per epoch, plus V100 tensor cores are
slower per-FLOP than H100. Net effect: **~3.5× longer wall-clock per
epoch on V100** *and* you pay more queue wait because Pitzer sees
heavier contention.

**Operational rule**: for anything training-heavy, default to
`--cluster cardinal` unless you specifically need something Pitzer-only
(older CUDA, certain module versions).

---

## 2. `Reason=Priority` is a scheduler hint, not a promise

**Rule**: before assuming your queue will drain "soon", read
`scontrol show job <jid> | grep StartTime` — SLURM gives you its actual
projection.

**Case study (2026-04-21)**: submitted 33 jobs to Pitzer `gpu`. One
started immediately, 10 more Priority-queued. After 1 h, still only 1
was running. `squeue -u $USER` showed `Reason=Priority` — which in
normal parlance just means "the scheduler has you queued by priority".
Running `scontrol show job <queued_jid>` revealed:

```text
StartTime=2026-04-22T02:56:34
```

The scheduler had already estimated that job wouldn't start for **~16
more hours** because 60 other jobs were occupying the partition's ~64
GPU slots and backfill wasn't shaking a slot loose. Switching to
Cardinal immediately was the right call.

When a job is Priority-queued, always check its projected `StartTime`
before deciding how to pace yourself. If the projection is > a few
hours, change clusters or change resource ask.

---

## 3. Shared filesystems let you hop clusters mid-DAG (carefully)

**Rule**: ESS (`/fs/ess/`) is mounted on all OSC clusters. Checkpoints
and caches are portable. SLURM job dependencies (`afterok`) are **not**.

A fit running on Pitzer writes its checkpoint to
`/fs/ess/PAS1266/.../best_model.ckpt`. A downstream analysis or
fusion-states extraction submitted on Cardinal can read that path with
no copy step.

But `#SBATCH --dependency=afterok:<jid>` only works within one
cluster's scheduler. If you submit Stage 1 on Pitzer and Stage 2 on
Cardinal, the `afterok` clause silently won't chain — Cardinal doesn't
know what Pitzer's job IDs mean.

Options for cross-cluster chains:

- Do the whole DAG on one cluster. Simplest.
- Wait for Stage 1 to finish by polling the checkpoint file on ESS,
  then manually submit Stage 2. Works, adds operator steps.
- Use a launcher that polls SLURM across clusters and writes a
  sentinel file when all upstream jobs complete. Worth building if you
  hop clusters often.

---

## 4. Mixed precision (fp16) has dataset-specific failure modes

**Rule**: fp16 + autocast is fast on V100/A100/H100, but any
intermediate activation that overflows fp16's ~65 504 max becomes `inf`
or `NaN` and propagates silently through the rest of the forward pass.

**Case study (2026-04-20)**: VGAE on dataset `hcrl_sa` crashed in the
first validation epoch with `ValueError: NaN encountered in metric
'val_loss'`. Same code path on `set_01` ran cleanly for 11+ minutes
past the crash point. Root cause: `hcrl_sa`'s feature distribution
under the train-only scaler (cache v9) has outliers that push an
internal activation past fp16's dynamic range; `set_01`'s distribution
is tamer.

**Mitigations, in order of preference**:

1. Add explicit `.clamp(-10, 10)` on the specific activation that
   overflows (requires per-layer `isfinite` instrumentation to find).
2. Train that model in fp32: `--set trainer.precision="32-true"`.
   Slower but numerically safe. Worth it for small models where
   throughput isn't the bottleneck.
3. Use bf16 if the cluster supports it. Same dynamic range as fp32
   but half the memory. A100/H100 have bf16 tensor cores; V100 does
   not.

Never globally disable autocast as a blanket fix — you lose the
throughput benefit on the majority of workloads that are fine under
fp16.

---

## 5. Test / eval dataloaders should not run the training-time budget probe

**Rule**: dynamic batching probes need CUDA. Test jobs often run on
CPU-only partitions (eval demarcation). Build a separate code path for
eval dataloaders that uses a fixed batch size and skips the probe.

**Case study (2026-04-20)**: every CPU-partition test job failed with

```text
RuntimeError: budget probe prerequisites missing: CUDA
```

because `test_dataloader()` called `_ensure_budget()` → `node_budget()`
→ `_require_probe_prereqs()`, which (rightly) refuses to hand out a
conservative fallback budget silently. Fix was to split the dataloader
builder: one `_build_train_loader` that runs the probe, one
`_build_eval_loader` that uses a fixed batch size and doesn't.

General principle: **any code path that unconditionally reaches for
CUDA should be guarded by a training-only flag**, or you'll pay for it
the first time you try to run eval, inference, or analysis on a CPU
node.

---

## 6. Capture SLURM job IDs with `sbatch --parsable`, not by parsing stdout

**Rule**: `sbatch` with `--parsable` emits `<jid>[;<cluster>]` on
stdout — machine-readable and version-stable. Never `awk` over
`"Submitted batch job NNN on cluster X"`.

**Case study**: a launcher used `${line##* }` to extract the job ID
from sbatch's default output. That pattern grabs the **last**
whitespace-separated token. Without `--clusters`, it returns the jid
correctly. With `--clusters=pitzer` (which causes sbatch to append
" on cluster pitzer"), it returns `pitzer`. The downstream
`afterok:pitzer` dependency then failed with "Job dependency problem"
and silently cancelled chained jobs.

Always use `--parsable`. In a bash launcher:

```bash
JID=$(sbatch --parsable --partition=gpu ... --wrap="$WRAP" | cut -d';' -f1)
```

Same applies to any CLI-scraping pattern — prefer structured output
(`--json`, `--parsable`, `-o` format strings) over free-text fallbacks.

---

## 7. Walltime signals give you a graceful-shutdown window

**Rule**: `--signal=B:USR1@300` tells SLURM to send `SIGUSR1` to the
batch shell 5 minutes before walltime. Use that window to save a final
checkpoint cleanly instead of losing the last epoch of work when SLURM
sends the kill.

The shape that works:

```bash
#SBATCH --signal=B:USR1@300
# or on scripts/run: scripts/run defaults this in its GPU profile
```

Inside the training script, install a handler (PyTorch Lightning does
this automatically via its SLURM signal plugin; custom trainers need
their own). On `SIGUSR1`:

1. Flush the current epoch's metrics.
2. Write a "last" checkpoint with the current model state.
3. Exit with a non-zero status that marks the job for requeue if
   `--requeue` is set, or 0 if you're doing a one-shot.

---

## 8. Queue-level concurrency has no visible limit — backfill does

**Rule**: `sacctmgr show assoc user=$USER` may show no `MaxJobs` /
`MaxSubmitJobs` limit on your account, but that doesn't mean every job
runs immediately. Concurrent capacity is gated by cluster resource
availability (total GPUs minus what others are running) *and* by
SLURM's backfill window (how far ahead the scheduler looks to fit
smaller jobs into gaps).

Submission tactics to improve backfill luck:

- **Shorter walltimes** — easier to fit in gaps between longer jobs.
- **Smaller resource asks** — 16 GB memory jobs backfill sooner than
  48 GB.
- **Single-GPU instead of multi-GPU** — if your job can tolerate the
  gres=gpu:1 shape, prefer it.
- **Array jobs over separate submissions** — the scheduler treats
  array tasks as one accounting entry, often better fair-share
  behavior.

---

## 9. MLflow tracking URI must resolve on every node that touches it

**Rule**: set `MLFLOW_TRACKING_URI` to a path accessible from all
nodes (ESS, not scratch, not `/tmp`). The SQLite backend at
`sqlite:///{LAKE_ROOT}/mlflow.db` works because `/fs/ess/` is
network-mounted everywhere; a local-only path silently creates
per-node DBs you'll never find.

Verify on submission with:

```bash
python -c "from graphids.config.constants import LAKE_ROOT; print(LAKE_ROOT)"
```

If runs mysteriously don't appear in MLflow, first check you're
querying the same DB the job wrote to. SQLite files happily get
created wherever `sqlite:///` points, even if that path doesn't exist
cluster-wide.

---

## 10. Parent/child MLflow runs need the env-var handoff

**Rule**: MLflow's `nested=True` parent/child linkage only works
inside one Python process. For SLURM-chained children (separate
processes), open the parent on the login node, export the run ID as
`MLFLOW_PARENT_RUN_ID`, and have each child stamp it as the
`mlflow.parentRunId` tag at its own `start_run`.

Launcher shape:

```bash
rid=$(python -m graphids mlflow-start-parent --group X --variant Y --dataset D)
MLFLOW_PARENT_RUN_ID="$rid" sbatch ... --wrap "python -m graphids fit ..."
```

Inside the child:

```python
tags = {"mlflow.parentRunId": os.environ.get("MLFLOW_PARENT_RUN_ID")}
with mlflow.start_run(tags=tags, run_name=...):
    ...
```

Without this, each fit starts its own orphan run and you lose the
grouping that makes cross-seed / cross-variant analysis possible.

---

## 11. Prebatching fixes worker starvation, not compute-vs-pipeline ratio

**Rule**: high GPU utilization requires `T_gpu(batch) ≫ T_main_process(batch)`.
Prebatching (collate once at setup, `num_workers=0`, `PrefetchLoader`)
eliminates worker cost but cannot shrink main-process per-step
overhead below a floor. When the model is compute-tiny, the floor
dominates and GPU util looks low — even though the pipeline is
correct.

**Case study (graphids, set_01 VGAE-small on V100, 2026-04-22)**:
the prebatched training path was measured at ~100% GPU util on
hcrl_sa with `scale="medium"` (T_gpu ~155 ms, T_cpu ~15 ms). The same
pipeline on set_01 with `scale="small"` showed **27% mean GPU util
over 54 min of training** — MLflow `system/gpu_0_utilization_percentage`,
5-second nvml samples. VRAM was at 93% (the two-point budget probe
was sized correctly), but the GPU sat idle 86% of the time because
the smaller model's T_gpu had collapsed to ~5 ms while the main-process
step wall (`Batch.clone()` + async H2D + callback dispatch) stayed
near ~20 ms. Not a regression: different workload, different ratio.

**V100 / A100 / H100 are compute-heavy machines.** A 10k-parameter
model on a V100 can't saturate the device by any pipeline tuning —
that's a workload characteristic. The practical implication:

- **Smoke runs** (tiny model, tiny epochs, `gpudebug`) — expect low
  GPU util, measure correctness only (no NaN, loss shape).
- **Production fits** — scale the model up (or the batch, via the
  budget probe) until T_gpu dominates. For most graph-IDS-style
  workloads on V100 that means `scale="medium"` or larger; on H100
  you can often push further.
- **Moving to a bigger GPU doesn't help a small model** — H100 has
  more VRAM and faster tensor cores, but a tiny model still runs in
  5 ms, so you'll get the same low util with fewer jobs finishing
  sooner (wall-clock wins, util doesn't).

**Diagnostic hierarchy** — always in this order:

1. Device-level metrics first: `nvidia-smi dmon -s u`,
   MLflow `system/gpu_*_utilization_percentage`, DCGM. These read from
   nvml and are ground truth.
2. Per-step timing: OTel traces, `torch.profiler`, `time.perf_counter`
   around the training step.
3. Wall-clock per epoch last — it aggregates everything and hides the
   signal. **Never diagnose throughput from wall-clock alone**.

Cross-reference: the full graphids quantitative breakdown lives at
[`docs/reference/prebatch-timing.md`](https://frenken-lab.github.io/graphids/reference/prebatch-timing/)
(Generalization and limits section).

---

## TODO — room to grow

Sections worth adding as experience accumulates:

- **Budget probe two-point sizing** — why the probe needs both a small
  and large batch, and what "binding: measured_degenerate_fallback"
  means in the MLflow tag.
- **`module load` vs `uv` lockfiles** — when to pin CUDA versions via
  modules vs. let `torch` pick.
- **OnDemand GPU sessions vs batch jobs** — when each is appropriate.
- **Scratch purge policy** — 90-day inactivity timer on `/fs/scratch/`.
- **GPU profiling** (`nsys`, `torch.profiler`, `nvidia-smi dmon`) —
  how to diagnose "why is this slow".
- **Multi-node training** — when DDP is worth the added fragility vs.
  a single-node larger GPU.
