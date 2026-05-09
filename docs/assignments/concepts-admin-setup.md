<!-- last-reviewed: 2026-04-16 -->
# Assignment 2b: Research Infrastructure

|                    |                                                           |
| ------------------ | --------------------------------------------------------- |
| **Author**         | Robert Frenken                                            |
| **Estimated time** | 3--4 hours                                                |
| **Prerequisites**  | Assignment 1 completed, GitHub account, computer access   |

!!! abstract "The throughline"
    Lab research runs on shared systems. Compute lives on OSC. Experiments live on Weights & Biases. Under the hood, both are databases. This assignment gets you accounts on those systems and gives you the mental model of how an ML project flows through them — from raw data to a tracked result.

!!! info "2b and 2c are assigned together"
    You have **2 weeks** to complete both 2b and [2c (AI-Augmented Development)](ai-augmented-development.md). Start 2b first — some of the account approvals take 1–2 business days.

---

## Part 1: Lab Accounts

You need three accounts to be a fully-plugged-in lab member. Two take minutes; one needs your `.edu` email and 1–2 business days to approve.

### 1.1 OSC — where your compute runs

If you don't already have an OSC account, follow the [Account Setup](../osc-basics/osc-account-setup.md) guide. Once you have credentials, verify SSH access:

```bash
ssh username@pitzer.osc.edu
```

You should land on a login node. Type `exit` to disconnect.

For SSH key setup and config tips, see [SSH Connection](../osc-basics/osc-ssh-connection.md).

- [ ] OSC account active
- [ ] SSH connection successful

### 1.2 Weights & Biases — where your experiments live

Weights & Biases (W&B) is the lab's experiment tracker. Every training run logs its config, metrics, and artifacts to a W&B project — you can compare runs, share dashboards, and reproduce results months later.

1. Sign up at [wandb.ai/site](https://wandb.ai/site) using your **university email**
2. Apply for a free academic account at [wandb.ai/academic](https://wandb.ai/site/academic)
3. Install and log in locally:

    ```bash
    pip install wandb
    wandb login
    # Paste your API key from https://wandb.ai/authorize
    ```

4. Verify it works:

    ```python
    import wandb
    wandb.init(project="test", mode="online")
    wandb.log({"test_metric": 42})
    wandb.finish()
    ```

5. Check [wandb.ai](https://wandb.ai/) — you should see a "test" project with one run.

For more on experiment tracking tools, see [Data & Experiment Tracking](../ml-workflows/data-experiment-tracking.md).

- [ ] W&B account created with university email
- [ ] `wandb login` successful
- [ ] Test run visible on wandb.ai

### 1.3 GitHub Education — the gateway to Copilot

You'll set up Copilot in [Assignment 2c](ai-augmented-development.md), but Education approval can take 1–2 days, so apply now.

1. Apply for [GitHub Education](https://education.github.com/) with your `.edu` email
2. Once approved, Copilot becomes free for you — set it up in 2c

- [ ] GitHub Education application submitted

---

## Part 2: The ML Pipeline Mental Model

Every ML project moves through the same stages. Understanding them tells you which tool to reach for at each step, and where things can go wrong.

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#e8f4fd', 'primaryTextColor': '#1a1a1a', 'lineColor': '#555'}}}%%
graph LR
    A@{ shape: cyl, label: "fa:fa-database Raw Data" }:::data --> B{{"fa:fa-filter Preprocessing"}}:::process
    B --> C{{"fa:fa-wrench Feature Engineering"}}:::process
    C --> D["fa:fa-brain Model Training"]:::process
    D --> E["fa:fa-chart-line Evaluation"]:::process
    E --> F["fa:fa-clipboard-list Experiment Tracking"]:::external
    F -->|iterate| C
    E --> G(["fa:fa-rocket Deployment"]):::success

    classDef process fill:#e8f4fd,stroke:#3b82f6,color:#1a1a1a,stroke-width:2px
    classDef data fill:#d1fae5,stroke:#059669,color:#1a1a1a,stroke-width:2px
    classDef external fill:#ede9fe,stroke:#7c3aed,color:#1a1a1a,stroke-width:2px
    classDef success fill:#d1fae5,stroke:#059669,color:#1a1a1a,stroke-width:2px
```

??? abstract "Stage-by-stage breakdown"
    - **Raw Data** — Collect or download the dataset (CSV, database, API). Version it with DVC or Git LFS.
    - **Preprocessing** — Clean missing values, normalize features, encode categoricals, split train/test.
    - **Feature Engineering** — Create new features, select relevant ones, transform representations (e.g., graph construction for GNNs).
    - **Model Training** — Fit the model to training data. Configure hyperparameters, choose optimizer, set up GPU training.
    - **Evaluation** — Measure performance on held-out test data. Use metrics appropriate for the task (accuracy, F1, AUC).
    - **Experiment Tracking** — Log parameters, metrics, and artifacts with W&B. Compare runs and iterate.
    - **Deployment** — Serve the model for inference (API, batch, embedded) — not always required for research.

    For a walkthrough of this pipeline on OSC, see the [ML Workflow Guide](../ml-workflows/ml-workflow.md).

### Map your 2a project onto the pipeline

You already did most of these stages in Assignment 2a. Write 1–2 sentences for each:

1. What was your **raw data** source? What format?
2. What **preprocessing** did you do (if any)?
3. What **features** did your models actually see?
4. Which models (Logistic Regression, Random Forest) count as **training** and **evaluation**?
5. What would **experiment tracking** add if you ran 20 different model configs?

### Reflection questions

Write 2–3 sentences for each in your blog post:

1. Why is it important to split data into train and test sets *before* any preprocessing?
2. How does experiment tracking help you iterate faster?
3. Which stage(s) of the pipeline would benefit most from GPU acceleration, and why?

- [ ] Pipeline diagram reviewed and understood
- [ ] 2a project mapped onto the pipeline
- [ ] Reflection questions answered

---

## Part 3: Why Structured Tracking

W&B stores your experiments in a database. So does MLflow. So do most production ML systems. Understanding *why* — and getting a feel for the query language that powers them — makes the whole stack less mysterious.

!!! info "SQL in 60 seconds"
    A **relational database** stores data in tables (rows = records, columns = fields). SQL (Structured Query Language) is how you ask it questions: "show me all experiments with accuracy above 0.9."

    **SQLite** is the simplest database — a single file, no server. Python ships with it.

### 3.1 Build a mini experiment tracker

Open a Python interpreter or notebook:

```python
import sqlite3

conn = sqlite3.connect(":memory:")  # in-memory, no file created
cursor = conn.cursor()

cursor.execute("""
    CREATE TABLE experiments (
        id INTEGER PRIMARY KEY,
        model_name TEXT NOT NULL,
        learning_rate REAL,
        batch_size INTEGER,
        accuracy REAL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")

experiments = [
    ("LogisticRegression", 0.01, 32, 0.85),
    ("RandomForest", None, None, 0.91),
    ("MLP", 0.001, 64, 0.88),
    ("CNN", 0.0005, 128, 0.93),
    ("MLP", 0.01, 32, 0.86),
    ("CNN", 0.001, 64, 0.95),
]
cursor.executemany(
    "INSERT INTO experiments (model_name, learning_rate, batch_size, accuracy) VALUES (?, ?, ?, ?)",
    experiments,
)
conn.commit()
```

### 3.2 Query it like W&B would

Now answer these four questions with SQL — the same questions W&B's UI lets you click through:

=== "1. Best runs"

    **Show all experiments with accuracy above 0.90:**

    ```sql
    SELECT * FROM experiments WHERE accuracy > 0.90;
    ```

=== "2. Model comparison"

    **Find the average accuracy per model:**

    ```sql
    SELECT model_name, AVG(accuracy) AS avg_accuracy
    FROM experiments
    GROUP BY model_name
    ORDER BY avg_accuracy DESC;
    ```

=== "3. Hyperparameter sweep"

    **Count experiments per batch size:**

    ```sql
    SELECT batch_size, COUNT(*) AS num_experiments
    FROM experiments
    GROUP BY batch_size;
    ```

=== "4. Insert + verify"

    **Add a new run and confirm it's there:**

    ```sql
    INSERT INTO experiments (model_name, learning_rate, batch_size, accuracy)
    VALUES ('GNN', 0.001, 64, 0.94);

    SELECT * FROM experiments WHERE model_name = 'GNN';
    ```

Run each query with `cursor.execute(...)` and print the results with `cursor.fetchall()`.

For a more complete example of SQLite in a lab project, see [SQLite Project Database](../ml-workflows/data-experiment-tracking.md#sqlite-project-database).

### Reflection questions

Write 2–3 sentences for each:

1. Why is a database better than a collection of CSV files for tracking experiments?
2. What would a **JOIN** be useful for in an ML project? (Hint: linking runs to datasets, or runs to a separate table of hyperparameter sweeps.)
3. When might you choose SQLite over a full database server like PostgreSQL — and vice versa?

- [ ] All 4 SQL queries run and results verified
- [ ] Reflection questions answered

---

## Part 4: Publish

Write a short post on your Quarto site that ties the three parts of this assignment into one narrative. Follow the **[Publishing Guide](publishing-guide.md)** for the full workflow.

**Quick reference for this assignment:**

- **Suggested categories:** `[infra, reflection, tooling]`
- **Suggested framing:** One of these angles —
    - **"Where my code actually lives"** — walk through OSC + W&B + GitHub and what each one does for a lab researcher
    - **"Mapping my 2a project onto the pipeline"** — annotate your own EDA work against the pipeline diagram
    - **"What W&B is doing under the hood"** — use the SQL exercises to demystify experiment trackers

Your post can be a single page. Pick one angle and make it specific.

- [ ] Blog post written with a clear angle
- [ ] Blog post live on your Quarto site

---

## Final Deliverables

- [ ] **OSC SSH access** working (terminal screenshot or output)
- [ ] **W&B test run** visible on wandb.ai
- [ ] **GitHub Education** applied for (approved or pending)
- [ ] **Pipeline reflection** answered (3 questions from Part 2)
- [ ] **SQL queries** run with output captured (4 queries + 3 reflection questions from Part 3)
- [ ] **Blog post live** on your Quarto site

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `ssh: connect to host pitzer.osc.edu port 22: Connection refused` | Check [OSC System Status](https://www.osc.edu/resources/system-status). Verify your SSH key is uploaded at [my.osc.edu](https://my.osc.edu) |
| `wandb: ERROR api_key not configured` | Run `wandb login` again and paste your key from [wandb.ai/authorize](https://wandb.ai/authorize) |
| GitHub Education approval takes forever | It's manual review — 1–2 business days. Submit early. A clear `.edu` email + a link to your academic profile speeds it up |
| `sqlite3.OperationalError: no such table` | Re-run the `CREATE TABLE` statement — in-memory databases disappear when the kernel restarts |
| `sqlite3.IntegrityError: NOT NULL constraint failed` | One of your `INSERT` rows is missing a required column. Check the schema vs. the values you're inserting |
