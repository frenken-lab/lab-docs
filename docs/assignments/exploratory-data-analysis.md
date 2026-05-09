<!-- last-reviewed: 2026-04-16 -->
# Assignment 2a: Exploratory Data Analysis

|                    |                                                        |
| ------------------ | ------------------------------------------------------ |
| **Author**         | Robert Frenken                                         |
| **Estimated time** | 6--8 hours                                             |
| **Prerequisites**  | Assignment 1 completed, Python basics, GitHub account  |

!!! abstract "What you'll build"
    An exploratory data analysis of a real automotive intrusion detection dataset, published as a blog post on your Quarto website. You'll load and explore the data with **polars**, create visualizations with **altair**, train two simple ML models with **scikit-learn**, and recreate two plots from the interactive charting ecosystem.

??? info "Why polars + altair instead of pandas + matplotlib?"
    Both stacks get the job done, but the lab standardizes on polars + altair for new projects:

    - **Polars** is 10–100× faster than pandas on most operations, has a cleaner API (no `inplace=`, no `SettingWithCopyWarning`), and expression-based syntax that composes well. It's what you'll see in current lab code.
    - **Altair** produces interactive, grammar-of-graphics plots out of the box. Hover tooltips, zoom, and linked-brushing come for free. It also renders cleanly in Quarto, Jupyter, and on the web.
    - You'll still encounter pandas + matplotlib/seaborn in older code and tutorials. Knowing both is useful, but start here.

---

## Part 0: Project Setup

### 0.1 Create a GitHub repository

1. Go to [github.com/new](https://github.com/new)
2. Repository name: `eda-assignment`
3. Set to **Public**, check **"Add a README"**, add a **Python `.gitignore`**
4. Clone it:

```bash
git clone git@github.com:YOURUSERNAME/eda-assignment.git
cd eda-assignment
```

### 0.2 Set up a Python environment

=== "uv (recommended)"

    ```bash
    # Install uv if you haven't already
    curl -LsSf https://astral.sh/uv/install.sh | sh

    uv venv
    source .venv/bin/activate   # Windows Git Bash: source .venv/Scripts/activate
    uv pip install polars altair scikit-learn jupyter vl-convert-python
    ```

=== "pip"

    ```bash
    python -m venv .venv
    source .venv/bin/activate
    pip install polars altair scikit-learn jupyter vl-convert-python
    ```

=== "conda"

    ```bash
    conda create -n eda python=3.12 polars altair scikit-learn jupyter vl-convert-python -c conda-forge -y
    conda activate eda
    ```

!!! info "Why `vl-convert-python`?"
    Altair renders to HTML by default. `vl-convert-python` adds the ability to save charts as PNG/SVG/PDF — useful for the figures you'll commit to the repo.

For more on Python environments, see [Python Environment Setup](../getting-started/python-environment-setup.md).

### 0.3 Project layout

```text
eda-assignment/
├── data/               # Raw and processed data (gitignored if large)
├── figures/            # Saved plot images
├── notebooks/
│   └── eda.ipynb       # Your main analysis notebook
├── .gitignore
├── README.md
└── requirements.txt
```

Create the directories and save dependencies:

```bash
mkdir -p data figures notebooks
uv pip freeze > requirements.txt
```

!!! warning "Don't commit large data files"
    Add `data/` to your `.gitignore` if the dataset exceeds a few MB. Git is not designed for large binary files — use a link in the README to the dataset source instead.

- [ ] Repo created and cloned
- [ ] Virtual environment activated
- [ ] Dependencies installed and pinned to `requirements.txt`
- [ ] Directory structure in place

---

## Part 1: Get & Explore the Data

### 1.1 Download the dataset

Download the **HCRL Survival IDS** dataset from [ocslab.hksecurity.net/Datasets/survival-ids](https://ocslab.hksecurity.net/Datasets/survival-ids).

1. Visit the link and download the dataset files
2. Place the CSV file(s) in your `data/` directory
3. Open `notebooks/eda.ipynb` (create it in VS Code or with `jupyter notebook`)

### 1.2 Load and inspect

```python
import polars as pl

df = pl.read_csv("../data/survival_ids.csv")  # adjust filename as needed

print(f"Shape: {df.shape}")
print(f"Columns: {df.columns}")
df.head()
```

??? tip "Polars vs pandas cheatsheet"
    | Task | pandas | polars |
    |------|--------|--------|
    | Load CSV | `pd.read_csv(f)` | `pl.read_csv(f)` |
    | Shape | `df.shape` | `df.shape` |
    | First rows | `df.head()` | `df.head()` |
    | Column types | `df.dtypes` | `df.schema` |
    | Summary stats | `df.describe()` | `df.describe()` |
    | Select columns | `df[["a", "b"]]` | `df.select("a", "b")` |
    | Filter | `df[df.x > 0]` | `df.filter(pl.col("x") > 0)` |
    | New column | `df["y"] = df.x * 2` | `df.with_columns((pl.col("x") * 2).alias("y"))` |
    | Group + aggregate | `df.groupby("g").sum()` | `df.group_by("g").sum()` |
    | Null count per column | `df.isnull().sum()` | `df.null_count()` |

### 1.3 Summary statistics

Run these in separate notebook cells and **read the output** — don't just run them blindly:

```python
# Schema: column names + dtypes
df.schema

# Descriptive statistics (mean, std, min, max, quartiles)
df.describe()

# Missing values per column
df.null_count()

# Value counts for a categorical column (if any)
# df.group_by("column_name").len().sort("len", descending=True)
```

- [ ] Data loaded successfully with `pl.read_csv`
- [ ] Schema reviewed — you understand the column types
- [ ] `df.describe()` output reviewed — you can identify reasonable ranges
- [ ] Missing values checked

---

## Part 2: Visualizations

Create **at least 3** EDA plots with **altair**. Save each figure to `figures/`.

!!! info "Altair in 30 seconds"
    Altair charts are built by chaining three things:

    1. `alt.Chart(data)` — the data source (polars DataFrame works directly)
    2. `.mark_*(...)` — the visual element (`mark_bar`, `mark_line`, `mark_rect`, `mark_point`, etc.)
    3. `.encode(...)` — which columns map to which visual channels (x, y, color, size, tooltip)

    Then `.properties(title=..., width=..., height=...)` to style.

### 2.1 Distribution plot

Pick a numeric column and visualize its distribution:

```python
import altair as alt

hist = (
    alt.Chart(df)
    .mark_bar()
    .encode(
        alt.X("your_column:Q", bin=alt.Bin(maxbins=50), title="Value"),
        alt.Y("count():Q", title="Count"),
        tooltip=["count():Q"],
    )
    .properties(title="Distribution of Your Column", width=600, height=350)
)
hist.save("../figures/distribution.png", scale_factor=2)
hist
```

??? example "Adding a density overlay"
    Layer a `transform_density` chart over the histogram for a smoother view:

    ```python
    density = (
        alt.Chart(df)
        .transform_density("your_column", as_=["your_column", "density"])
        .mark_line(color="crimson")
        .encode(x="your_column:Q", y="density:Q")
    )

    (hist + density).resolve_scale(y="independent").save("../figures/distribution_kde.png", scale_factor=2)
    ```

### 2.2 Correlation heatmap

Altair heatmaps need data in **long form** (one row per cell). Polars makes that a two-step transform:

```python
# 1) Compute correlation matrix on numeric columns only
numeric = df.select(pl.col(pl.NUMERIC_DTYPES))
corr = numeric.corr()

# 2) Reshape to long form: one row per (row_feature, col_feature, correlation)
corr_long = (
    corr.with_columns(pl.Series("row", numeric.columns))
    .unpivot(index="row", variable_name="col", value_name="corr")
)

heatmap = (
    alt.Chart(corr_long)
    .mark_rect()
    .encode(
        alt.X("col:N", title=None, sort=numeric.columns),
        alt.Y("row:N", title=None, sort=numeric.columns),
        alt.Color("corr:Q", scale=alt.Scale(scheme="redblue", domain=[-1, 1]), title="r"),
        tooltip=["row:N", "col:N", alt.Tooltip("corr:Q", format=".2f")],
    )
    .properties(title="Feature Correlation Heatmap", width=500, height=500)
)

# Overlay the numeric values on top of each cell
text = (
    alt.Chart(corr_long)
    .mark_text(baseline="middle", fontSize=10)
    .encode(
        x="col:N",
        y="row:N",
        text=alt.Text("corr:Q", format=".2f"),
        color=alt.condition("abs(datum.corr) > 0.5", alt.value("white"), alt.value("black")),
    )
)

(heatmap + text).save("../figures/correlation_heatmap.png", scale_factor=2)
heatmap + text
```

!!! tip "Why the long-form reshape?"
    Altair follows the grammar-of-graphics convention where each row is one observation. A correlation matrix is a 2D grid, so we flatten it: every cell becomes a row with `(row_feature, col_feature, correlation)`. The `unpivot` (also called `melt` in pandas) does this in one call.

### 2.3 Class distribution

If your dataset has a label column, visualize its balance:

```python
class_counts = df.group_by("label_column").len().rename({"len": "count"})

bar = (
    alt.Chart(class_counts)
    .mark_bar()
    .encode(
        alt.X("label_column:N", title="Class"),
        alt.Y("count:Q", title="Count"),
        alt.Color("label_column:N", legend=None),
        tooltip=["label_column:N", "count:Q"],
    )
    .properties(title="Class Distribution", width=500, height=300)
)
bar.save("../figures/class_distribution.png", scale_factor=2)
bar
```

!!! tip "Make your plots readable"
    Always include a title and axis labels. Altair auto-generates titles from column names — override them for a cleaner read. Hover tooltips give readers a zoom-in without cluttering the chart.

- [ ] Distribution plot created and saved
- [ ] Correlation heatmap created and saved (with annotations)
- [ ] Class distribution (or third plot of your choice) created and saved

---

## Part 3: Toy ML Models

Train two simple classifiers and evaluate them. This is a first exposure to the sklearn API — the goal is to learn the workflow, not to achieve state-of-the-art accuracy.

### 3.1 Prepare the data

Polars converts to numpy arrays for sklearn:

```python
from sklearn.model_selection import train_test_split

# Drop the label and any non-numeric columns
X = df.drop("label_column").select(pl.col(pl.NUMERIC_DTYPES)).to_numpy()
y = df["label_column"].to_numpy()

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
print(f"Train: {X_train.shape}, Test: {X_test.shape}")
```

### 3.2 Train two models

```python
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier

lr = LogisticRegression(max_iter=1000, random_state=42)
lr.fit(X_train, y_train)

rf = RandomForestClassifier(n_estimators=100, random_state=42)
rf.fit(X_train, y_train)
```

### 3.3 Evaluate with confusion matrices

Build one altair confusion matrix function you can reuse for both models:

```python
from sklearn.metrics import classification_report, confusion_matrix

def confusion_chart(y_true, y_pred, title: str) -> alt.Chart:
    cm = confusion_matrix(y_true, y_pred)
    labels = sorted(set(y_true))
    cm_long = pl.DataFrame(
        {
            "actual": [labels[i] for i in range(len(labels)) for _ in labels],
            "predicted": [labels[j] for _ in labels for j in range(len(labels))],
            "count": cm.flatten().tolist(),
        }
    )

    base = alt.Chart(cm_long).encode(
        alt.X("predicted:N", title="Predicted"),
        alt.Y("actual:N", title="Actual"),
    )
    rects = base.mark_rect().encode(
        alt.Color("count:Q", scale=alt.Scale(scheme="blues"), title="Count"),
        tooltip=["actual:N", "predicted:N", "count:Q"],
    )
    text = base.mark_text(fontSize=14, fontWeight="bold").encode(
        text="count:Q",
        color=alt.condition("datum.count > 50", alt.value("white"), alt.value("black")),
    )
    return (rects + text).properties(title=title, width=300, height=300)

for name, model in [("Logistic Regression", lr), ("Random Forest", rf)]:
    y_pred = model.predict(X_test)
    print(f"\n{'='*40}\n{name}\n{'='*40}")
    print(classification_report(y_test, y_pred))

    chart = confusion_chart(y_test, y_pred, f"Confusion Matrix — {name}")
    chart.save(
        f"../figures/confusion_matrix_{name.lower().replace(' ', '_')}.png",
        scale_factor=2,
    )
    chart.display()
```

??? question "What's the white/black text trick doing?"
    Dark cells need white text to stay readable; light cells need black. The `alt.condition` expression checks the cell's count value and picks the right text color. This is a common altair pattern for annotated heatmaps.

- [ ] Train/test split created
- [ ] Two models trained (Logistic Regression + Random Forest)
- [ ] `classification_report` printed for both models
- [ ] Confusion matrices created and saved

---

## Part 4: Gallery Picks

Visit the [Vega-Altair Example Gallery](https://altair-viz.github.io/gallery/index.html) and pick **2 chart types** that look interesting. Recreate them using the Survival IDS dataset (or a subset of it).

### Requirements

1. Choose 2 **different** chart types (e.g., violin plot, strip plot, radial chart, parallel coordinates, linked brushing, faceted chart)
2. Adapt the gallery code to use columns from your dataset
3. Customize each plot: tweak the color scheme, add a meaningful title/labels, add tooltips or interaction where it makes sense
4. Save both figures to `figures/`

!!! tip "Picking good chart types"
    Don't just pick the simplest plots. Try something you haven't used before — the point is to expand your visualization toolkit. Good picks:

    - **Violin / strip plots** for distributions across categories
    - **Linked brushing** across two panels (altair's superpower)
    - **Faceted charts** (`.facet(...)`) for comparing groups
    - **Parallel coordinates** for multi-feature comparison

??? example "Linked brushing starter"
    ```python
    brush = alt.selection_interval()

    top = (
        alt.Chart(df).mark_point()
        .encode(x="feature_a:Q", y="feature_b:Q",
                color=alt.condition(brush, "label_column:N", alt.value("lightgray")))
        .add_params(brush)
    )
    bottom = (
        alt.Chart(df).mark_bar()
        .encode(x="label_column:N", y="count()")
        .transform_filter(brush)
    )
    (top & bottom).save("../figures/linked_brushing.png", scale_factor=2)
    ```

    Drag a box on the scatter — the bar chart below updates in real time.

- [ ] Gallery plot 1 created, customized, and saved
- [ ] Gallery plot 2 created, customized, and saved

---

## Part 5: Publish

Turn your analysis into a blog post on your Quarto website. The full workflow (YAML header, categories, preview/commit/push) lives in the **[Publishing Guide](publishing-guide.md)** — follow it end-to-end.

**Quick reference for this assignment:**

- **Suggested categories:** `[eda, python, visualization, machine-learning]`
- **Cover image:** lead with your correlation heatmap or the best gallery pick
- **What to write in the "What I Learned" section:** the single most surprising finding from the data, and one thing that changed in your mental model (polars vs pandas, altair vs matplotlib, etc.)

- [ ] Notebook runs cleanly top-to-bottom after a kernel restart
- [ ] Markdown explanations added between code cells
- [ ] Blog post live on your Quarto site

---

## Final Deliverables

- [ ] **GitHub repo URL** for your EDA project (e.g., `github.com/YOURUSERNAME/eda-assignment`)
- [ ] **5+ visualizations** in `figures/` (3 EDA + 2 gallery picks)
- [ ] **Confusion matrix** charts for both models
- [ ] **Blog post live** on your Quarto site
- [ ] **`requirements.txt`** in the repo root

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `ModuleNotFoundError: No module named 'polars'` | Make sure your virtual environment is activated and you've installed the packages |
| Jupyter kernel doesn't see installed packages | Click the kernel name in the top-right of VS Code and pick your `.venv` |
| Altair chart displays as raw JSON in Jupyter | Run `alt.renderers.enable("default")` at the top of the notebook, or update to altair ≥ 5 |
| `chart.save("file.png")` fails | Install `vl-convert-python` (`uv pip install vl-convert-python`) |
| `quarto render` fails on notebook | Restart kernel, run all cells, fix any errors, then try again |
| Data file too large for Git | Add `data/` to `.gitignore` — don't commit large files to Git |
| Correlation heatmap has too many features | Filter to the top-N most variable columns first: `df.select([c for c in numeric.columns if df[c].std() > threshold])` |
| Polars error on `.corr()` with non-numeric columns | Select numeric columns first: `df.select(pl.col(pl.NUMERIC_DTYPES))` |

---

## Sources

- [Polars user guide](https://docs.pola.rs/) — Polars team
- [Altair example gallery](https://altair-viz.github.io/gallery/index.html) — Vega-Altair project
- [HCRL Survival IDS dataset](https://ocslab.hksecurity.net/Datasets/survival-ids) — Hacking and Countermeasure Research Lab
