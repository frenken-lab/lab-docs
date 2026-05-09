---
status: updated
---
<!-- last-reviewed: 2026-03-30 -->
# Data & Experiment Tracking

Managing datasets, tracking experiments, and reproducing results are core challenges in ML research. This guide covers practical tools for structured data and experiment tracking on OSC — DVC for data versioning, SQLite for metadata, MLflow and Weights & Biases for experiment tracking, TensorBoard for training visualization, and Parquet for fast data loading.

---

## Why You Need Structured Tracking

Without tracking infrastructure, ML projects quickly accumulate problems:

- **Dataset confusion** — Which version of the data was used for a given result?
- **Lost experiments** — Hyperparameters buried in terminal history or forgotten notebooks
- **Broken reproduction** — "It worked on my machine" but no one can replicate the setup
- **Slow iteration** — Re-processing raw data from scratch every time

A tracking stack solves these by versioning data, logging every run, and making results queryable.

---

!!! tip "Choosing Your Approach"
    - **Small datasets / sharing with collaborators** → DVC
    - **Many runs / analytics-heavy** → Parquet datalake + DuckDB ([DuckDB Analytics Layer](duckdb-analytics.md))
    - **Real-time monitoring** → W&B

## Tool Overview

| Tool | Purpose | Best For |
|------|---------|----------|
| **DVC** | Dataset versioning + remote storage | Large datasets, data pipelines |
| **DuckDB** | SQL analytics over Parquet files | Leaderboards, experiment comparison, export pipelines |
| **SQLite** | Lightweight relational database | Structured metadata, queryable results |
| **MLflow** | Experiment tracking UI + API | Comparing runs, logging metrics/artifacts |
| **W&B** | Cloud experiment tracking + visualization | Team dashboards, no port forwarding needed |
| **TensorBoard** | Training visualization | Loss curves, model graphs, quick local checks |
| **Parquet** | Columnar data format | Fast reads of large tabular datasets |

These tools complement each other — a typical project might use DVC for data versioning, W&B for live monitoring, and Parquet + DuckDB for post-hoc analytics and export.

---

## DVC (Data Version Control)

[DVC](https://dvc.org/) tracks large files and datasets alongside your Git history without storing them in the repo.

### Setup on OSC

```bash
# Install in your project environment
pip install dvc

# Initialize DVC in your repo
cd ~/projects/my-ml-project
dvc init

# Use your OSC scratch space as a local remote
dvc remote add -d osc_scratch /fs/scratch/$OSC_PROJECT/dvc-store
```

### Basic Workflow

```bash
# Track a dataset
dvc add data/raw/sensor_readings.csv

# This creates data/raw/sensor_readings.csv.dvc (a small pointer file)
# Commit the pointer file to Git
git add data/raw/sensor_readings.csv.dvc data/raw/.gitignore
git commit -m "Track sensor readings dataset v1"

# Push data to remote storage
dvc push
```

### Switching Data Versions

```bash
# Check out a previous version of the dataset
git checkout v1.0 -- data/raw/sensor_readings.csv.dvc
dvc checkout

# Return to latest
git checkout main -- data/raw/sensor_readings.csv.dvc
dvc checkout
```

!!! tip "DVC on OSC scratch"
    OSC scratch directories (`/fs/scratch/`) are ideal for DVC remote storage — they're high-performance, shared across nodes, and have large quotas. Just remember that scratch files are purged after [60 days of inactivity](https://www.osc.edu/supercomputing/storage-environment-at-osc/available-file-systems), so keep important data backed up.

---

## SQLite Project Database

SQLite is a file-based relational database — no server needed. It's perfect for storing structured project metadata directly in your repo.

### Schema Design

A practical schema for ML projects tracks three things: datasets, training runs, and metrics.

```sql
-- datasets: what data versions exist
CREATE TABLE datasets (
    id          INTEGER PRIMARY KEY,
    name        TEXT NOT NULL,
    version     TEXT NOT NULL,
    path        TEXT NOT NULL,
    num_samples INTEGER,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    description TEXT
);

-- runs: each training experiment
CREATE TABLE runs (
    id          INTEGER PRIMARY KEY,
    dataset_id  INTEGER REFERENCES datasets(id),
    model_name  TEXT NOT NULL,
    config      TEXT,          -- JSON string of hyperparameters
    started_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    finished_at TIMESTAMP,
    status      TEXT DEFAULT 'running'
);

-- metrics: results from each run
CREATE TABLE metrics (
    id       INTEGER PRIMARY KEY,
    run_id   INTEGER REFERENCES runs(id),
    epoch    INTEGER,
    metric   TEXT NOT NULL,    -- e.g. 'val_loss', 'accuracy'
    value    REAL NOT NULL
);
```

### Python Helper Module

Create a small helper to interact with the database from your training scripts:

```python
# src/db.py
import sqlite3
import json
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "project.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def log_run(dataset_id, model_name, config):
    conn = get_connection()
    cursor = conn.execute(
        "INSERT INTO runs (dataset_id, model_name, config) VALUES (?, ?, ?)",
        (dataset_id, model_name, json.dumps(config))
    )
    conn.commit()
    run_id = cursor.lastrowid
    conn.close()
    return run_id

def log_metric(run_id, epoch, metric, value):
    conn = get_connection()
    conn.execute(
        "INSERT INTO metrics (run_id, epoch, metric, value) VALUES (?, ?, ?, ?)",
        (run_id, epoch, metric, value)
    )
    conn.commit()
    conn.close()
```

### YAML Dataset Catalog

Keep a human-readable catalog of datasets alongside the database:

```yaml
# data/catalog.yaml
datasets:
  sensor_v1:
    path: data/raw/sensor_readings_v1.csv
    description: Raw sensor readings, Jan-Mar 2025
    num_samples: 50000

  sensor_v2:
    path: data/raw/sensor_readings_v2.csv
    description: Extended sensor readings with new features
    num_samples: 120000
```

---

## MLflow

[MLflow](https://mlflow.org/) provides a tracking API and web UI for logging parameters, metrics, and artifacts from training runs.

### Setup with SQLite Backend on OSC

```bash
# Install
pip install mlflow

# Set tracking URI to a local SQLite database
# Note: use ${HOME} instead of ~ (tilde is not expanded in SQLite URIs)
export MLFLOW_TRACKING_URI=sqlite:///${HOME}/projects/my-ml-project/mlflow.db
```

Add this to your `~/.bashrc` or project activation script so it's always set.

### Training Code Integration

```python
import mlflow

mlflow.set_experiment("my-experiment")

with mlflow.start_run(run_name="lr-sweep-001"):
    # Log hyperparameters
    mlflow.log_params({
        "learning_rate": 1e-3,
        "batch_size": 64,
        "hidden_dim": 256,
        "optimizer": "adam",
    })

    for epoch in range(num_epochs):
        train_loss = train_one_epoch(model, train_loader, optimizer)
        val_loss, val_acc = evaluate(model, val_loader)

        # Log metrics at each epoch
        mlflow.log_metrics({
            "train_loss": train_loss,
            "val_loss": val_loss,
            "val_accuracy": val_acc,
        }, step=epoch)

    # Log the trained model
    mlflow.pytorch.log_model(model, "model")
```

### Viewing Results via Port Forwarding

Since OSC compute nodes don't have public web access, use SSH port forwarding to view the MLflow UI locally:

```bash
# On the OSC login node, start the MLflow server
mlflow ui --port 5000 --backend-store-uri sqlite:///~/projects/my-ml-project/mlflow.db

# From your local machine, forward the port
ssh -L 5000:localhost:5000 username@pitzer.osc.edu

# Open http://localhost:5000 in your browser
```

### Comparing Runs

The MLflow UI lets you:

- **Compare metrics** across runs with interactive charts
- **Filter runs** by parameters, metrics, or tags
- **Download artifacts** (saved models, plots, configs)
- **Search runs** with SQL-like queries: `metrics.val_accuracy > 0.9`

!!! tip "MLflow with SLURM"
    In batch jobs, set the experiment name and run name in your SLURM script so results are automatically organized:
    ```bash
    export MLFLOW_EXPERIMENT_NAME="my-experiment"
    export MLFLOW_RUN_NAME="job-${SLURM_JOB_ID}"
    python train.py
    ```

---

## Weights & Biases (W&B)

[Weights & Biases](https://wandb.ai/) is a cloud-hosted experiment tracker. Unlike MLflow, results sync to wandb.ai automatically — no port forwarding needed to view dashboards from OSC jobs.

### Account Setup

1. Sign up at [wandb.ai/site](https://wandb.ai/site) with your university email
2. Apply for a free academic team at [wandb.ai/academic](https://wandb.ai/site/academic) (unlimited private projects)
3. Copy your API key from [wandb.ai/authorize](https://wandb.ai/authorize)

```bash
pip install wandb
wandb login
# Paste your API key when prompted
```

!!! tip "Store your API key on OSC"
    Add `export WANDB_API_KEY=<your-key>` to your `~/.bashrc` so SLURM batch jobs can authenticate automatically.

### Training Code Integration

```python
import wandb

wandb.init(
    project="my-experiment",
    name="lr-sweep-001",
    config={
        "learning_rate": 1e-3,
        "batch_size": 64,
        "hidden_dim": 256,
        "optimizer": "adam",
    },
)

for epoch in range(num_epochs):
    train_loss = train_one_epoch(model, train_loader, optimizer)
    val_loss, val_acc = evaluate(model, val_loader)

    wandb.log({
        "train_loss": train_loss,
        "val_loss": val_loss,
        "val_accuracy": val_acc,
        "epoch": epoch,
    })

# Save the trained model as an artifact
artifact = wandb.Artifact("model", type="model")
artifact.add_file("checkpoints/best_model.pt")
wandb.log_artifact(artifact)

wandb.finish()
```

### SLURM Usage

Compute nodes on OSC may have limited internet access. Use W&B's offline mode to log locally, then sync after the job finishes:

```bash
#!/bin/bash
#SBATCH --job-name=train
#SBATCH --gpus-per-node=1

export WANDB_MODE=offline   # Log to local directory
python train.py

# Sync results after training completes
wandb sync --sync-all
```

Alternatively, if your cluster allows outbound HTTPS from compute nodes (Pitzer compute nodes currently have internet access), W&B syncs in real time with no extra steps — remove the `WANDB_MODE=offline` line.

### OSC Performance: Redirect W&B to Scratch

W&B writes many small files (logs, media, metadata) to its [local run directory](https://docs.wandb.ai/guides/track/environment-variables/#wandb_dir). On NFS home directories, this adds metadata I/O overhead. Redirect W&B's working directory to scratch:

```bash
# Add to your job script, before python
export WANDB_DIR=/fs/scratch/PAS1234/$USER/wandb
mkdir -p "$WANDB_DIR"
```

This avoids NFS contention during training. W&B still syncs to the cloud — only the local staging directory changes.

### Forwarding Full Config to W&B

If you use a config file (YAML, JSON, or argparse), forward the full config so every parameter is searchable in the W&B dashboard:

```python
import yaml
import wandb

# Load your config however you prefer
with open("configs/experiment.yaml") as f:
    config = yaml.safe_load(f)

wandb.init(project="my-experiment", config=config)

# All keys from the YAML are now searchable in the W&B UI
# You can filter runs by any config value
```

!!! tip "PyTorch Lightning + W&B"
    If you use LightningCLI with [`WandbLogger`](https://lightning.ai/docs/pytorch/stable/extensions/generated/lightning.pytorch.loggers.WandbLogger.html), the logger logs hyperparameters from the LightningModule's `self.save_hyperparameters()` when a logger is attached to the Trainer. No manual config forwarding needed in that case.

### Viewing Results

Open [wandb.ai](https://wandb.ai/) in your browser — your runs appear in the project dashboard with interactive charts, system metrics, and logged artifacts. No SSH tunneling required.

---

## TensorBoard

[TensorBoard](https://www.tensorflow.org/tensorboard) provides lightweight training visualization. It's bundled with PyTorch via `torch.utils.tensorboard`.

### Basic Usage

```python
from torch.utils.tensorboard import SummaryWriter

writer = SummaryWriter("runs/experiment-001")

for epoch in range(num_epochs):
    train_loss = train_one_epoch(model, train_loader, optimizer)
    val_loss, val_acc = evaluate(model, val_loader)

    writer.add_scalar("Loss/train", train_loss, epoch)
    writer.add_scalar("Loss/val", val_loss, epoch)
    writer.add_scalar("Accuracy/val", val_acc, epoch)

writer.close()
```

### Viewing on OSC via Port Forwarding

```bash
# On the OSC login node
tensorboard --logdir=runs/ --port 6006

# From your local machine
ssh -L 6006:localhost:6006 username@pitzer.osc.edu

# Open http://localhost:6006 in your browser
```

!!! tip "TensorBoard vs W&B vs MLflow"
    **TensorBoard** is great for quick, local visualization during development. **MLflow** adds structured experiment comparison with a SQLite backend. **W&B** provides the richest cloud-hosted dashboards with zero port-forwarding setup — ideal for long-running SLURM jobs where you want to check progress from anywhere.

---

## Data Format Pipeline

Raw CSV data is convenient but slow to load for large datasets. A common pipeline converts data through progressively faster formats:

```
CSV (raw) → Parquet (compressed + fast reads) → PyTorch tensors (GPU-ready cache)
```

### Parquet Conversion

```python
import pandas as pd

# Read raw CSV
df = pd.read_csv("data/raw/sensor_readings.csv")

# Save as Parquet (typically 2-5x smaller, 10-100x faster to read)
df.to_parquet("data/processed/sensor_readings.parquet")
```

### PyTorch Dataset with Caching

```python
import torch
from torch.utils.data import Dataset
import pandas as pd
from pathlib import Path

class SensorDataset(Dataset):
    def __init__(self, parquet_path, cache_dir="data/cache"):
        cache_path = Path(cache_dir) / f"{Path(parquet_path).stem}.pt"

        if cache_path.exists():
            cached = torch.load(cache_path)
            self.features = cached["features"]
            self.labels = cached["labels"]
        else:
            df = pd.read_parquet(parquet_path)
            self.features = torch.tensor(df.drop("label", axis=1).values, dtype=torch.float32)
            self.labels = torch.tensor(df["label"].values, dtype=torch.long)
            cache_path.parent.mkdir(parents=True, exist_ok=True)
            torch.save({"features": self.features, "labels": self.labels}, cache_path)

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, idx):
        return self.features[idx], self.labels[idx]
```

### Performance Comparison

| Format | File Size (100K rows) | Read Time |
|--------|----------------------|-----------|
| CSV | ~50 MB | ~2 s |
| Parquet | ~12 MB | ~0.1 s |
| PyTorch cache (.pt) | ~40 MB | ~0.02 s |

!!! note
    Exact numbers depend on your data. The relative speedups are what matter — Parquet is significantly faster than CSV, and pre-cached tensors are fastest of all.

---

## Parquet Datalake for Experiment Results

For projects with many training runs, storing results as Parquet files creates a queryable datalake that DuckDB can analyze instantly with SQL — leaderboards, metric trends, config comparisons, and JSON exports for dashboards. This pattern scales better than SQLite for analytics-heavy workflows.

For full details — Parquet layout, DuckDB views, export scripts, and interactive queries — see the [DuckDB Analytics Layer](duckdb-analytics.md) page.

---

## Putting It All Together

Here's what a well-structured ML project looks like with these tools:

```
my-ml-project/
├── data/
│   ├── catalog.yaml              # Dataset catalog
│   ├── raw/                      # Original data (DVC-tracked)
│   │   ├── sensor_readings.csv
│   │   └── sensor_readings.csv.dvc
│   ├── processed/                # Parquet files (DVC-tracked)
│   │   └── sensor_readings.parquet
│   └── cache/                    # PyTorch tensor cache (gitignored)
│       └── sensor_readings.pt
├── src/
│   ├── db.py                     # SQLite helper
│   ├── data.py                   # Dataset classes
│   └── train.py                  # Training script with MLflow
├── project.db                    # SQLite metadata database
├── mlflow.db                     # MLflow tracking database
├── dvc.yaml                      # DVC pipeline definitions
├── dvc.lock                      # DVC pipeline state
├── .dvc/                         # DVC configuration
├── .gitignore
└── README.md
```

### Recommended Workflow

1. **Add raw data** — Place files in `data/raw/`, track with `dvc add`
2. **Register in catalog** — Add an entry to `data/catalog.yaml`
3. **Process data** — Convert to Parquet, run feature engineering
4. **Train with tracking** — Use MLflow to log params and metrics, use SQLite for structured metadata
5. **Compare results** — Use `mlflow ui` to compare runs, query SQLite for custom analysis
6. **Version everything** — `git commit` for code + DVC pointers, `dvc push` for data

---

## Next Steps

- [Hugging Face Spaces](huggingface-spaces.md) — Deploy Parquet datalake dashboards to HF Spaces with GitHub Actions
- [DuckDB Analytics Layer](duckdb-analytics.md) — SQL queries over your Parquet datalake
- [ML Workflow Guide](ml-workflow.md) — Best practices for ML projects on OSC
- [PyTorch Setup](pytorch-setup.md) — Installing and configuring PyTorch
- [Job Submission](../working-on-osc/osc-job-submission.md) — Running training jobs on SLURM
- [Environment Management](../working-on-osc/osc-environment-management.md) — Managing Python environments on OSC
