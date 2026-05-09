<!-- last-reviewed: 2026-02-26 -->
# DuckDB Analytics Layer

Query and analyze ML experiment results using DuckDB over a Parquet datalake — fast SQL analytics without a database server.

---

## When to Use DuckDB

| Need | Tool | Why |
|------|------|-----|
| **Small datasets, sharing with collaborators** | DVC | Git-like versioning for files, S3/GCS remotes |
| **Many runs, analytics-heavy queries** | Parquet + DuckDB | Columnar storage, instant SQL, no server |
| **Real-time monitoring during training** | W&B | Cloud dashboards, live loss curves |
| **Structured metadata alongside code** | SQLite | Embedded in repo, lightweight |

DuckDB fills the gap between "dump everything to CSV" and "run a full database server." It reads Parquet files directly, runs analytical SQL instantly, and needs zero infrastructure.

---

## Parquet Datalake Layout

Store experiment results as Parquet files on scratch or in your project directory. Each pipeline run appends rows; the files are the source of truth.

```
data/lakehouse/
├── runs.parquet          # One row per training run (run_id, config, status, timestamps)
├── metrics.parquet       # One row per metric per epoch (run_id, epoch, metric_name, value)
├── configs.parquet       # Flattened hyperparameters (run_id, lr, hidden_dim, dropout, ...)
└── datasets.parquet      # Dataset metadata (dataset_id, name, num_samples, path)
```

Write Parquet files from your training scripts using pandas or PyArrow:

```python
import pandas as pd
from pathlib import Path

LAKEHOUSE = Path("data/lakehouse")
LAKEHOUSE.mkdir(parents=True, exist_ok=True)

def log_run(run_id: str, config: dict, status: str = "running"):
    """Append a run record to the lakehouse."""
    row = {"run_id": run_id, "status": status, **config}
    df = pd.DataFrame([row])
    path = LAKEHOUSE / "runs.parquet"
    if path.exists():
        existing = pd.read_parquet(path)
        df = pd.concat([existing, df], ignore_index=True)
    df.to_parquet(path, index=False)

def log_metrics(run_id: str, epoch: int, metrics: dict):
    """Append metric rows to the lakehouse."""
    rows = [
        {"run_id": run_id, "epoch": epoch, "metric": k, "value": v}
        for k, v in metrics.items()
    ]
    df = pd.DataFrame(rows)
    path = LAKEHOUSE / "metrics.parquet"
    if path.exists():
        existing = pd.read_parquet(path)
        df = pd.concat([existing, df], ignore_index=True)
    df.to_parquet(path, index=False)
```

---

## Building a DuckDB Analytics File

The DuckDB file is a **views-only** layer over your Parquet files — always rebuildable, never the source of truth. This is the `build_analytics.py` pattern:

```python
"""Build DuckDB analytics views over the Parquet datalake."""
import duckdb

DB_PATH = "analytics.duckdb"
LAKEHOUSE = "data/lakehouse"

def build():
    con = duckdb.connect(DB_PATH)

    # Create views (not tables) — always reads live Parquet data
    con.execute(f"""
        CREATE OR REPLACE VIEW runs AS
        SELECT * FROM read_parquet('{LAKEHOUSE}/runs.parquet')
    """)
    con.execute(f"""
        CREATE OR REPLACE VIEW metrics AS
        SELECT * FROM read_parquet('{LAKEHOUSE}/metrics.parquet')
    """)
    con.execute(f"""
        CREATE OR REPLACE VIEW configs AS
        SELECT * FROM read_parquet('{LAKEHOUSE}/configs.parquet')
    """)

    # Materialized convenience views
    con.execute("""
        CREATE OR REPLACE VIEW leaderboard AS
        SELECT
            r.run_id,
            r.status,
            c.lr,
            c.hidden_dim,
            MAX(CASE WHEN m.metric = 'val_f1' THEN m.value END) AS best_f1,
            MAX(CASE WHEN m.metric = 'val_accuracy' THEN m.value END) AS best_acc,
            MAX(m.epoch) AS epochs_completed
        FROM runs r
        JOIN configs c ON r.run_id = c.run_id
        JOIN metrics m ON r.run_id = m.run_id
        GROUP BY r.run_id, r.status, c.lr, c.hidden_dim
        ORDER BY best_f1 DESC NULLS LAST
    """)

    print(f"Built {DB_PATH} with views over {LAKEHOUSE}/")
    con.close()

if __name__ == "__main__":
    build()
```

Rebuild anytime your Parquet files change:

```bash
python build_analytics.py
```

---

## Exporting Static JSON for Dashboards

Generate JSON files that a static dashboard can consume — the `export.py` pattern:

```python
"""Export leaderboard and metric trends as static JSON."""
import duckdb
import json

def export():
    con = duckdb.connect("analytics.duckdb", read_only=True)

    # Leaderboard
    leaderboard = con.execute("SELECT * FROM leaderboard").fetchdf()
    leaderboard.to_json("exports/leaderboard.json", orient="records", indent=2)

    # Metric trends for top 5 runs
    top_runs = con.execute("""
        SELECT run_id FROM leaderboard LIMIT 5
    """).fetchdf()["run_id"].tolist()

    trends = con.execute("""
        SELECT run_id, epoch, metric, value
        FROM metrics
        WHERE run_id = ANY($1) AND metric IN ('val_f1', 'val_loss')
        ORDER BY run_id, epoch
    """, [top_runs]).fetchdf()
    trends.to_json("exports/metric_trends.json", orient="records", indent=2)

    print("Exported to exports/")
    con.close()

if __name__ == "__main__":
    export()
```

---

## Interactive Querying

DuckDB's CLI or Python API makes ad-hoc analysis fast:

```bash
# Install DuckDB Python package (one-time)
pip install duckdb
# Quick test
python -c "import duckdb; print(duckdb.sql('SELECT 42').fetchone())"
```

### Leaderboard Query

```sql
-- Top 10 runs by F1 score
SELECT run_id, lr, hidden_dim, best_f1, epochs_completed
FROM leaderboard
LIMIT 10;
```

### Hyperparameter Impact Analysis

```sql
-- Compare runs grouped by a config flag
SELECT
    c.use_augmentation,
    COUNT(*) AS num_runs,
    AVG(m.value) AS avg_f1,
    MAX(m.value) AS best_f1
FROM configs c
JOIN metrics m ON c.run_id = m.run_id
WHERE m.metric = 'val_f1'
  AND m.epoch = (SELECT MAX(epoch) FROM metrics WHERE run_id = m.run_id)
GROUP BY c.use_augmentation;
```

### Metric Trend for a Specific Run

```sql
-- Loss and F1 over epochs for a specific run
SELECT epoch, metric, value
FROM metrics
WHERE run_id = 'run_20260101_001'
  AND metric IN ('val_loss', 'val_f1')
ORDER BY epoch;
```

---

## OSC Considerations

- **Runs on login node** — DuckDB is read-only analytics, not compute. Run `build_analytics.py` and queries on the login node. No GPU or SLURM job needed.
- **Scratch for active datalake** — Store Parquet files on `/fs/scratch/PAS1234/$USER/lakehouse/` for fast I/O during training. Copy final results to project space.
- **Parquet is the source of truth** — The `.duckdb` file is always rebuildable. Don't back it up; back up the Parquet files.
- **Not DuckDB-WASM** — This page covers the Python/CLI analytics layer. DuckDB-WASM (for in-browser dashboards) is a separate topic specific to web applications.

---

## Next Steps

- [Data & Experiment Tracking](data-experiment-tracking.md) — DVC, W&B, and the broader tracking stack
- [Pipeline Orchestration](../working-on-osc/pipeline-orchestration.md) — Ray pipelines that produce the Parquet files
- [ML Project Template](ml-workflow.md) — Project structure for ML experiments
