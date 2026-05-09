<!-- last-reviewed: 2026-05-09 -->
# ML Project Workflow

One compact guide for the pieces that used to live across the ML workflow subpages.

## Project Layout

Keep one repo with a predictable shape:

```text
~/projects/my_ml_project/
├── README.md
├── pyproject.toml or requirements.txt
├── configs/
├── data/
├── notebooks/
├── scripts/
├── src/
├── checkpoints/
├── logs/
└── results/
```

Put large datasets and job outputs on `/fs/scratch/` and keep the repo for code, configs, and small metadata.

!!! warning "Scratch is temporary"
    OSC scratch is fast, but files are purged after inactivity. Copy final artifacts to project storage when a run matters.

## Notebook-to-Script Workflow

Prototype in a notebook, then move the stable pieces into a script with `argparse` or a config file.

- notebooks for quick inspection and debugging
- scripts for repeatable SLURM jobs
- saved figures and logs instead of notebook-only state

```bash
jupyter nbconvert --to script notebooks/prototype.ipynb
```

## Experiment Tracking

Pick a light stack and keep it consistent:

- DVC for dataset versioning
- SQLite or Parquet for run metadata
- MLflow or W&B for experiment tracking
- TensorBoard for quick loss and curve checks

For most lab workflows, a simple pattern works well:

1. Version data with DVC or a Parquet lake
2. Log run metadata with MLflow, SQLite, or W&B
3. Save checkpoints, configs, and plots with each run

### SQLite Project Database

SQLite is a good fit when the project is small enough that you want a single file with no server to manage. Use it for run metadata, annotation tables, and simple joins between datasets and experiments.

## Analytics and Deployment

### DuckDB Analytics Layer

Use DuckDB when you want SQL over Parquet without a server. It is a good fit for local analysis, batch reporting, and quick joins across many experiment outputs.

- DuckDB is best for local or batch analytics over Parquet files
- GitHub Pages is fine for static sites, but it cannot set the headers DuckDB-WASM needs

### Hugging Face Spaces

Use Hugging Face Spaces when you want to publish dashboards or demos with custom headers, especially if DuckDB-WASM is involved.

- HF Spaces is best for lightweight public dashboards, demos, or report sites
- Pair it with the Parquet + DuckDB pattern when you want a simple public analytics layer

## Checklist

- [ ] Repo layout is stable
- [ ] Training script runs from the command line
- [ ] Data lives on scratch or a proper remote
- [ ] Runs are logged somewhere queryable
- [ ] Final artifacts are saved outside ephemeral scratch
