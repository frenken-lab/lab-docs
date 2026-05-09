<!-- last-reviewed: 2026-03-05 -->
# Hugging Face Spaces Deployment

Deploy interactive ML dashboards, Quarto reports, and demo apps to [Hugging Face Spaces](https://huggingface.co/spaces) — free hosting with GitHub Actions CI/CD.

---

## What HF Spaces Are

Hugging Face Spaces provides free hosting for:

- **Static sites** — Quarto reports, HTML dashboards, paper supplements
- **Gradio apps** — Interactive ML demos with auto-generated UIs
- **Streamlit apps** — Data apps with Python
- **Docker containers** — Anything else

For research, the most common use case is deploying a Quarto report site with interactive figures (Mosaic/vgplot, Observable Plot) backed by DuckDB-WASM for in-browser SQL queries over your experiment data.

### Why HF Spaces for Research

| Alternative | Limitation |
|-------------|-----------|
| GitHub Pages | No custom headers (breaks DuckDB-WASM CORS), public repos only for free |
| Netlify/Vercel | Requires separate account, more complex setup |
| **HF Spaces** | Free, ML-native, custom CORS headers, private spaces, API integration |

HF Spaces supports custom HTTP headers — critical for DuckDB-WASM, which requires Cross-Origin Isolation headers (`cross-origin-embedder-policy: require-corp`).

---

## Account & Token Setup

### 1. Create a Hugging Face Account

Sign up at [huggingface.co](https://huggingface.co/) — free accounts work fine.

### 2. Create a Write Token

1. Go to [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)
2. Click **New token**
3. Name it (e.g., `github-actions-deploy`)
4. Select **Write** permission
5. Copy the token (`hf_...`)

### 3. Add as GitHub Secret

In your GitHub repository:

1. Go to **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret**
3. Name: `HF_TOKEN`
4. Value: paste your `hf_...` token

---

## Deploying a Static Quarto Site

### Step 1: Create the HF Space

You can create the Space manually on huggingface.co, or let the first deploy create it automatically. If creating manually:

1. Go to [huggingface.co/new-space](https://huggingface.co/new-space)
2. Choose **Static** as the SDK
3. Set visibility (public or private)

### Step 2: Prepare Your Quarto Project

Ensure your Quarto project builds to a `_site/` directory:

```yaml
# _quarto.yml
project:
  type: website
  output-dir: _site
```

### Step 3: Add the GitHub Actions Workflow

Add a deploy job to your CI workflow (`.github/workflows/ci.yml`):

```yaml
deploy-hf:
  if: github.ref == 'refs/heads/main'
  needs: [build]  # Run after your build/test jobs
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4

    - uses: quarto-dev/quarto-actions/setup@v2

    - uses: quarto-dev/quarto-actions/render@v2
      with:
        path: reports/    # Path to your Quarto project

    - name: Create Space README
      run: |
        cat > reports/_site/README.md << 'EOF'
        ---
        title: "My Research Dashboard"
        sdk: static
        app_file: index.html
        pinned: true
        custom_headers:
          cross-origin-embedder-policy: require-corp
          cross-origin-opener-policy: same-origin
          cross-origin-resource-policy: cross-origin
        ---
        EOF

    - name: Deploy to HF Space
      env:
        HF_TOKEN: ${{ secrets.HF_TOKEN }}
      run: |
        pip install huggingface-hub
        python -c "
        from huggingface_hub import HfApi
        api = HfApi()
        api.upload_folder(
            repo_id='YOUR-USERNAME/YOUR-SPACE-NAME',
            folder_path='reports/_site',
            repo_type='space',
            commit_message='Deploy from ${{ github.sha }}',
        )
        print('HF Space deploy complete')
        "
```

!!! warning "Replace placeholders"
    Change `YOUR-USERNAME/YOUR-SPACE-NAME` to your actual HF username and Space name (e.g., `buckeyeguy/my-dashboard`). Change `reports/` to the path of your Quarto project.

---

## Space Configuration

The Space README (`README.md` in the Space root) controls Space behavior via YAML front matter:

```yaml
---
title: "My Research Dashboard"
sdk: static                    # static | gradio | streamlit | docker
app_file: index.html           # Entry point for static sites
pinned: true                   # Pin to your profile
private: true                  # Private visibility (optional)
colorFrom: green               # Gradient color (cosmetic)
colorTo: blue
custom_headers:                # Custom HTTP headers
  cross-origin-embedder-policy: require-corp
  cross-origin-opener-policy: same-origin
  cross-origin-resource-policy: cross-origin
---
```

### CORS Headers for DuckDB-WASM

DuckDB-WASM requires Cross-Origin Isolation to use `SharedArrayBuffer`. Without these headers, DuckDB-WASM falls back to a slower single-threaded mode or fails entirely:

| Header | Value | Why |
|--------|-------|-----|
| `cross-origin-embedder-policy` | `require-corp` | Enables `SharedArrayBuffer` |
| `cross-origin-opener-policy` | `same-origin` | Required companion to COEP |
| `cross-origin-resource-policy` | `cross-origin` | Allows loading resources cross-origin |

!!! note
    GitHub Pages does not support custom headers, which is one reason HF Spaces is better suited for DuckDB-WASM dashboards.

---

## Use Cases in Research

### Interactive Paper Supplements

Deploy a Quarto website alongside your paper with interactive figures that let reviewers explore your data:

```
reports/
├── _quarto.yml
├── index.qmd              # Landing page
├── dashboard.qmd          # Interactive dashboard
├── paper/                 # Paper chapters with embedded figures
│   ├── 01-introduction.qmd
│   ├── 02-methods.qmd
│   └── ...
└── data/                  # Parquet files for DuckDB-WASM
    ├── metrics.parquet
    └── training_curves.parquet
```

### Sharing Experiment Results

The Parquet datalake pattern from [Data & Experiment Tracking](data-experiment-tracking.md) pairs naturally with HF Spaces:

1. **Train** — Run experiments, log to Parquet datalake
2. **Export** — Export datalake Parquet to `reports/data/`
3. **Build** — Quarto renders interactive dashboards with DuckDB-WASM
4. **Deploy** — GitHub Actions pushes to HF Spaces on every push to main

This gives you a live dashboard that updates automatically with every new experiment.

### Gradio Apps for Model Demos

For interactive model inference demos, use Gradio instead of static:

```python
# app.py
import gradio as gr
import torch

model = torch.load("model.pt")

def predict(input_data):
    with torch.no_grad():
        return model(input_data)

demo = gr.Interface(fn=predict, inputs="text", outputs="text")
demo.launch()
```

Set `sdk: gradio` in the Space README and push `app.py` + `requirements.txt`.

### Streamlit Dashboard with HF Dataset + Cron

For dashboards that need **regularly updated data** from OSC, the pattern is:

1. **Collector script** on OSC gathers data → stores in local DuckDB → exports Parquet to a private HF Dataset
2. **Streamlit app** on HF Spaces reads from the HF Dataset (cached, refreshes every 5 min)
3. **Cron job** on an OSC login node runs the collector daily

This decouples data collection (OSC-only) from visualization (public web).

#### Architecture

```
OSC login node                    Hugging Face
┌──────────────────┐              ┌─────────────────────┐
│ collect.py        │   Parquet    │ HF Dataset (private) │
│  OSCusage → DuckDB ├────────────►│  jobs.parquet        │
│  (cron: daily 6AM)│  HfApi push  │  metadata.json       │
└──────────────────┘              └─────────┬───────────┘
                                            │ hf_hub_download
                                  ┌─────────▼───────────┐
                                  │ HF Space (public)    │
                                  │  Streamlit + Plotly  │
                                  │  Docker SDK          │
                                  └─────────────────────┘
```

**Live example:** [OSC Usage Dashboard](https://huggingface.co/spaces/buckeyeguy/osc-usage-dashboard) — tracks lab compute spending, job health, and per-user breakdowns.

#### HF Dataset as the data layer

Create a private HF Dataset to hold your Parquet files. The collector pushes with `HfApi.upload_file()`:

```python
from huggingface_hub import HfApi

api = HfApi(token=os.environ["HF_TOKEN"])
api.upload_file(
    path_or_fileobj="jobs.parquet",
    path_in_repo="jobs.parquet",
    repo_id="your-username/your-dataset",
    repo_type="dataset",
)
```

The Streamlit app reads it with caching:

```python
import streamlit as st
from huggingface_hub import hf_hub_download

@st.cache_data(ttl=300)  # 5-minute cache
def load_data():
    path = hf_hub_download(
        repo_id="your-username/your-dataset",
        filename="jobs.parquet",
        repo_type="dataset",
    )
    return pd.read_parquet(path)
```

The HF Dataset stays **private** (only your token can read it), while the Space is **public**.

#### Streamlit Docker SDK Space

For Streamlit on HF Spaces, use the Docker SDK. Your Space needs:

```
├── Dockerfile
├── README.md          # Space config (YAML front matter)
├── requirements.txt
├── app.py             # Streamlit entry point
├── config.py
├── data_loader.py
└── charts.py
```

**Dockerfile:**

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 7860
CMD ["streamlit", "run", "app.py", "--server.port=7860", "--server.address=0.0.0.0", "--server.headless=true"]
```

**README.md front matter:**

```yaml
---
title: My Dashboard
sdk: docker
app_port: 7860
pinned: true
---
```

!!! warning "Port must match"
    `app_port` in README, `EXPOSE` in Dockerfile, and `--server.port` in CMD must all be the same value.

The Space needs your HF token to read the private Dataset. Add it as a Space secret:

1. Go to your Space → **Settings** → **Variables and secrets**
2. Add secret: `HF_TOKEN` = your write token

#### Upload files with `HfApi`

On OSC, `git clone` to HF Spaces can fail due to old git versions. Use `HfApi.upload_file()` instead:

```python
from huggingface_hub import HfApi

api = HfApi(token=os.environ["HF_TOKEN"])
for fname in ["app.py", "config.py", "data_loader.py", "charts.py"]:
    api.upload_file(
        path_or_fileobj=fname,
        path_in_repo=fname,
        repo_id="your-username/your-space",
        repo_type="space",
    )
```

Each upload triggers a Space rebuild (Docker build + deploy). Batch uploads with `upload_folder()` triggers only one rebuild.

#### Automating collection with cron

Cron on OSC login nodes runs your collector on a schedule. The key challenge is that cron doesn't source `.bashrc`, so you need a wrapper script:

```bash
#!/usr/bin/env bash
# cron-collect.sh — wrapper for cron (no .bashrc available)
set -euo pipefail

source ~/.env.local                    # HF_TOKEN and other secrets
export PATH="/opt/osc/bin:$PATH"       # OSCusage lives here

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
LOG="$SCRIPT_DIR/cron-collect.log"

echo "=== $(date -Iseconds) ===" >> "$LOG"
"$SCRIPT_DIR/.venv/bin/python" "$SCRIPT_DIR/collect.py" --push-hf >> "$LOG" 2>&1
echo "" >> "$LOG"

# Keep log from growing forever
tail -500 "$LOG" > "$LOG.tmp" && mv "$LOG.tmp" "$LOG"
```

Install the cron job:

```bash
chmod +x cron-collect.sh

# Test in a stripped environment first
env -i HOME=$HOME ./cron-collect.sh

# Install — daily at 6 AM
crontab -e
# Add: 0 6 * * * /path/to/cron-collect.sh
```

!!! tip "Test before installing"
    Always test with `env -i HOME=$HOME` to simulate cron's empty environment. Missing `PATH` entries or unsourced env vars are the most common failures.

Check `cron-collect.log` to verify it's running. If a cron run fails, the dashboard keeps serving the last successful data — it won't break.

---

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| Deploy fails with 401 | Invalid or expired HF token | Regenerate token, update GitHub secret |
| DuckDB-WASM errors in browser | Missing CORS headers | Verify `custom_headers` in Space README |
| Space shows "Building" forever | Large files or build errors | Check Space logs on HF; reduce `_site/` size |
| Charts don't render | OJS/JS runtime errors | Open browser console; `quarto render` success doesn't guarantee JS works |
| Space is blank | Wrong `app_file` | Verify `app_file: index.html` matches your build output |
| Streamlit Space fails to start | Port mismatch | Ensure `app_port`, `EXPOSE`, and `--server.port` all match |
| Space can't read private Dataset | Missing secret | Add `HF_TOKEN` as a Space secret in Settings |
| Cron job not running | Empty environment | Test with `env -i HOME=$HOME`; ensure wrapper sources `~/.env.local` and sets `PATH` |
| `git clone` to HF fails on OSC | Old git version | Use `HfApi.upload_file()` or `upload_folder()` instead |

---

## Next Steps

- [Data & Experiment Tracking](data-experiment-tracking.md) — Parquet datalake that feeds HF Spaces dashboards
- [DuckDB Analytics Layer](duckdb-analytics.md) — SQL queries over experiment results
- [Pipeline Orchestration](../working-on-osc/pipeline-orchestration.md) — Automating the train → export → deploy pipeline
