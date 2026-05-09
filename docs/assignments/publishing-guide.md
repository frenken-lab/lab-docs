<!-- last-reviewed: 2026-04-16 -->
# Publishing Guide

Every lab assignment ends with a blog post on your personal Quarto site. This page is the single reference for how to publish one — YAML headers, categories, the preview/commit/push loop, and the portfolio habits that turn assignments into artifacts worth showing off.

!!! abstract "What you need before publishing"
    - A working Quarto site from [Assignment 1: Personal Website](personal-website.md)
    - A notebook or `.qmd` draft with your analysis
    - Any figures saved as images (PNG/SVG) or generated inline by the notebook

---

## Why publish at all?

Assignments aren't throwaway homework. Every blog post becomes a permanent artifact — future employers, grad school committees, lab collaborators, and even future-you searching for "that plot I made" will land on these pages.

!!! tip "Turn assignments into portfolio pieces"
    1. **Write a clear intro** — assume the reader has no context about the assignment. What problem are you exploring, and why?
    2. **Lead with your best visualization** — a compelling plot is worth more than a wall of text.
    3. **Add a "What I Learned" section** — reflection shows depth of understanding.
    4. **Use categories** — they make it easy to find related posts and signal topical focus to readers.

---

## YAML header template

Every post starts with a YAML header. Use this template and customize the fields:

=== "Notebook (.ipynb)"

    Add a **Raw** cell at the top of the notebook:

    ```yaml
    ---
    title: "Exploratory Data Analysis: Survival IDS Dataset"
    description: "EDA and baseline ML models on the HCRL Survival IDS dataset."
    date: "2026-04-16"
    author: "Your Name"
    categories: [eda, python, machine-learning]
    image: "figures/cover.png"   # optional — shows on the listing page
    ---
    ```

=== "Quarto doc (.qmd)"

    The YAML header is the very first thing in the file — no blank lines before it:

    ```yaml
    ---
    title: "Exploratory Data Analysis: Survival IDS Dataset"
    description: "EDA and baseline ML models on the HCRL Survival IDS dataset."
    date: "2026-04-16"
    author: "Your Name"
    categories: [eda, python, machine-learning]
    image: "figures/cover.png"
    execute:
      echo: true        # show code
      warning: false    # hide warnings
    ---
    ```

??? info "Optional fields worth knowing"
    - `image:` — path to a cover image shown on the blog listing page
    - `draft: true` — hide the post from the listing until you remove this
    - `execute:` — control notebook execution (`echo`, `warning`, `eval`)
    - `format: html: toc: true` — enable a table of contents for long posts
    - `bibliography: refs.bib` — enable citation rendering if you're using references

    Full reference: [Quarto YAML options](https://quarto.org/docs/reference/formats/html.html)

---

## Category taxonomy

Use categories consistently so related posts group together. Pick 2–4 per post from this taxonomy:

| Category | Use for |
|----------|---------|
| `python` | Any Python-centric post |
| `eda` | Exploratory data analysis, visualizations |
| `machine-learning` | Modeling, training, evaluation |
| `deep-learning` | Neural networks, PyTorch, from-scratch models |
| `infra` | OSC, SLURM, compute/environment setup |
| `tooling` | Package management, editor config, dotfiles |
| `ai-assistants` | Copilot, Claude, LLM workflow reflections |
| `reflection` | "What I learned" write-ups, concept walkthroughs |
| `visualization` | Charts-heavy posts (altair, matplotlib, etc.) |

!!! example "Good category choices"
    - EDA assignment → `[eda, python, visualization, machine-learning]`
    - NN from scratch → `[deep-learning, python, reflection]`
    - Package management essay → `[tooling, python, reflection]`
    - AI workflow writeup → `[ai-assistants, tooling, reflection]`

---

## Publishing workflow

The same loop works for every assignment:

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#e8f4fd', 'primaryTextColor': '#1a1a1a', 'lineColor': '#555'}}}%%
graph LR
    A@{ shape: doc, label: "fa:fa-file-code Notebook<br/>or .qmd" }:::data -->|"copy to posts/"| B{{"fa:fa-eye quarto preview"}}:::process
    B -->|"looks good"| C{{"fa:fa-code-branch git add + commit"}}:::process
    C -->|"push"| D(["fa:fa-rocket Live on<br/>GitHub Pages"]):::success

    classDef process fill:#e8f4fd,stroke:#3b82f6,color:#1a1a1a,stroke-width:2px
    classDef data fill:#d1fae5,stroke:#059669,color:#1a1a1a,stroke-width:2px
    classDef success fill:#d1fae5,stroke:#059669,color:#1a1a1a,stroke-width:2px
```

### Step-by-step

=== "If your post is a notebook"

    1. **Clean the notebook.** Restart kernel → run all cells top-to-bottom (++ctrl+shift+f5++ in VS Code). Remove debug cells. Make sure every code cell has a markdown cell above or below explaining what it does.

    2. **Add the YAML header** (see [YAML template](#yaml-header-template)) as a **Raw** cell at the top.

    3. **Copy into your Quarto site's `posts/` folder:**

        ```bash
        cp -r notebooks/eda.ipynb ~/my-site/posts/eda-post/index.ipynb
        cp -r figures/ ~/my-site/posts/eda-post/figures/
        ```

    4. **Preview locally:**

        ```bash
        cd ~/my-site
        quarto preview
        ```

        Open the URL it prints. Check formatting, figure rendering, and that code outputs look right.

    5. **Commit and push:**

        ```bash
        git add posts/eda-post/
        git commit -m "Add EDA blog post"
        git push
        ```

        GitHub Actions builds and deploys within a minute or two.

=== "If your post is a .qmd"

    1. **Create the file** in `posts/your-post/index.qmd`.

    2. **Add the YAML header** at the very top.

    3. **Write content** — inline code blocks execute when rendered:

        ````markdown
        ## Loading the data

        We use polars for its speed and clean API:

        ```{python}
        import polars as pl
        df = pl.read_csv("data/survival_ids.csv")
        df.head()
        ```
        ````

    4. **Preview locally:**

        ```bash
        quarto preview
        ```

    5. **Commit and push** (same as notebook workflow).

### Stopping the preview server

Press ++ctrl+c++ in the terminal running `quarto preview`.

---

## Writing style for lab blog posts

??? tip "Structure that works"
    A reliable template:

    1. **Intro (2–3 sentences)** — What's the problem? Why does it matter?
    2. **Dataset / Setup** — Brief description, not a data dictionary dump.
    3. **Analysis or Implementation** — Your actual work, broken into short sections with one idea each.
    4. **Results** — Lead with the best plot or number. Interpret it in one sentence.
    5. **What I Learned** — Two or three specific things. Not "I learned Python."
    6. **(Optional) Next Steps** — Questions this raised, things you'd try next.

??? tip "Things to avoid"
    - **Wall-of-code posts** — if a reader can't skim and understand the story, break up code with prose.
    - **Uncommented plots** — every figure needs a one-sentence takeaway under it.
    - **Vague reflections** — "I learned a lot" is filler. Say what *specifically* changed in your understanding.
    - **Broken figure paths** — always preview before pushing.
    - **Committing data files** — large CSVs/Parquet don't belong in Git. Link to the source instead.

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `quarto preview` fails on notebook | Restart kernel, run all cells top-to-bottom, fix any errors, retry |
| Figures don't render on the deployed site | Check relative paths — use `figures/plot.png` not `/Users/.../figures/plot.png` |
| Post doesn't appear on the listing page | Check `draft: true` isn't in the YAML; verify the file is in `posts/` |
| Mermaid diagram renders as raw text | Use fenced code block with ```` ```{mermaid} ```` (Quarto) or ```` ```mermaid ```` — check Quarto version supports it |
| `quarto render` complains about missing packages | Install the missing package in your active environment, then re-run |
| Changes live locally but not on github.io | Check the Actions tab — GitHub Pages builds can fail silently on YAML errors |

---

## Reference

- [Quarto blog guide](https://quarto.org/docs/websites/website-blog.html)
- [Quarto YAML reference](https://quarto.org/docs/reference/formats/html.html)
- [Student Site Showcase](site-showcase.md) — examples of lab blog posts
