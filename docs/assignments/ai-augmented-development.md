<!-- last-reviewed: 2026-04-16 -->
# Assignment 2c: AI-Augmented Development

|                    |                                                           |
| ------------------ | --------------------------------------------------------- |
| **Author**         | Robert Frenken                                            |
| **Estimated time** | 3--4 hours                                                |
| **Prerequisites**  | Assignment 2a (EDA project) and 2b (GitHub Education submitted) |

!!! abstract "The throughline"
    Writing code in 2026 means collaborating with AI assistants. This assignment sets up Copilot in VS Code, builds the habits that make LLM collaboration actually productive, and configures your 2a EDA project so those assistants have the context they need.

!!! info "2b first"
    Start [2b (Research Infrastructure)](concepts-admin-setup.md) first — you need GitHub Education approved (or at least applied) before Copilot works.

---

## Part 1: The Dotfiles Concept

Modern projects ship their dev environment as code. Your editor settings, AI assistant instructions, linter config, and CI pipelines all live in files that are committed to the repo — so a teammate (or future you) can clone the repo and be productive in minutes.

| File/folder | Purpose |
|-------------|---------|
| `.vscode/settings.json` | Project-specific VS Code settings |
| `.github/workflows/` | GitHub Actions CI/CD pipelines |
| `.github/copilot-instructions.md` | Project context for GitHub Copilot |
| `.gitignore` | Files Git should ignore |
| `.claude/` | Claude Code project settings |
| `CLAUDE.md` | Instructions for Claude Code (and other LLMs) |

!!! info "Why commit these?"
    So the entire team shares the same configuration. No "works on my machine" — the repo *is* the dev environment.

---

## Part 2: VS Code + Copilot Setup

### 2.1 Confirm your VS Code baseline

Open VS Code settings (++ctrl+comma++) and verify the recommendations from [VS Code Extensions](../getting-started/vscode-extensions.md):

- [ ] Default formatter set to **Ruff** (`charliermarsh.ruff`)
- [ ] Format on save enabled
- [ ] Pylance language server active

### 2.2 Install GitHub Copilot

1. Install the **GitHub Copilot** extension (`github.copilot`)
2. Install **GitHub Copilot Chat** (`github.copilot-chat`)
3. Sign in when prompted (uses your GitHub Education account)
4. Test inline completions: open a Python file, type a comment, and wait for Copilot's suggestion:

    ```python
    # Function that calculates the mean of a list of numbers
    ```

5. Press ++tab++ to accept the suggestion.

For setup details, see [AI Coding Assistants](../getting-started/ai-coding-assistants.md).

??? warning "Copilot silent? Checklist"
    - Are you signed into the correct GitHub account? (Status bar, bottom right)
    - Is the Copilot icon **active** (not grayed out) in the status bar?
    - Is your GitHub Education status approved? Check [education.github.com](https://education.github.com/)
    - Is the file type supported (`.py`, `.md`, `.qmd`, `.js`, etc.)?
    - Try a ++ctrl+shift+p++ → "Developer: Reload Window"

- [ ] Copilot extension installed
- [ ] Copilot generated at least one useful suggestion
- [ ] Copilot Chat (++ctrl+alt+i++) responds to a test prompt

---

## Part 3: Working with LLMs

The tools only get you so far. The difference between a frustrating LLM session and a productive one is almost entirely about *how you ask*.

### 3.1 The four interaction modes

=== "Planning"

    **When to use:** before writing code — design the approach first.

    **Example prompt:**
    > "I need to build an EDA pipeline for the Survival IDS dataset using polars and altair. Walk me through the steps I should follow, in order, with one sentence per step."

    **Why it works:** gets you a roadmap you can critique before you're deep in code.

=== "Writing"

    **When to use:** generate code from a clear, scoped spec.

    **Example prompt:**
    > "Write a Python function that takes a polars DataFrame and returns a dict with `{shape, null_count, dtype_summary}`. Use only polars and the stdlib."

    **Why it works:** narrow scope + clear I/O = code you can review and accept in one pass.

=== "Explanation"

    **When to use:** understand existing code or a puzzling error.

    **Example prompt:**
    > "Explain what `df.group_by('model').agg(pl.col('acc').max())` does line by line, and what a pandas equivalent would look like."

    **Why it works:** gives you a mental model, not just a fix.

=== "Debugging"

    **When to use:** when you have context (code + traceback) and need a second pair of eyes.

    **Example prompt:**
    > "I get a `KeyError: 'label_column'` on line 15. Here's the full traceback and the dataframe columns: `['rpm', 'speed', 'attack_type']`. What's going wrong?"

    **Why it works:** concrete context beats "fix my code" every time.

### 3.2 The four habits

!!! tip "Habits that separate good LLM users from great ones"

    1. **Plan first.** Describe what you want to build before asking for code. Give context about the project.
    2. **Start slow.** Ask for small pieces, test them, then build up. Don't ask for 200 lines at once — you can't review them all, and neither can the LLM.
    3. **Ask for explanations.** When the LLM generates code you don't understand, ask it to explain line by line. Never commit code you can't explain.
    4. **Teach the next session.** When you discover a good pattern or correction, add it to `CLAUDE.md` or `copilot-instructions.md` so the next session starts smarter.

### 3.3 Practice: use an LLM on your EDA project

Pick **one** of these and do it in Copilot Chat (or Claude / ChatGPT):

=== "Option A: Write"

    Ask the LLM to write a polars function that loads your Survival IDS dataset and prints a summary report (shape, nulls per column, dtype counts, first/last row).

    Test the generated code in your notebook. If it doesn't work, iterate with the LLM until it does.

=== "Option B: Debug"

    Paste an error you actually hit during Assignment 2a (the real traceback, not a paraphrase). Ask the LLM to explain what went wrong and propose a fix.

    Evaluate the fix: is the *diagnosis* right, or did it just make the error disappear?

=== "Option C: Explain"

    Find a piece of code from Assignment 2a that you wrote but don't fully understand (e.g., the correlation heatmap `unpivot` step, or the confusion matrix `alt.condition` trick). Ask the LLM to explain it line by line.

    Summarize the explanation in your own words. That summary becomes part of your blog post.

**Save the conversation** — screenshot, copy-paste, or export. You'll reference it in Part 5.

- [ ] Used an LLM for at least one practice task
- [ ] Saved the conversation for your blog post

---

## Part 4: Create a CLAUDE.md for Your EDA Project

`CLAUDE.md` is a plain-markdown file at the root of a repo that gives [Claude Code](https://code.claude.com/docs/en/overview) (and, by the same convention, other LLM tools) persistent context about the project. It's the "project brief" that the assistant reads every time.

Create `CLAUDE.md` in the root of your EDA repository from Assignment 2a:

```markdown
# CLAUDE.md

## Project Overview
Exploratory data analysis of the HCRL Survival IDS dataset for
automotive CAN bus intrusion detection.

## Tech Stack
- Python 3.12+
- polars for data manipulation
- altair for visualization
- scikit-learn for baseline ML models
- Jupyter notebooks for analysis

## Commands
- Install dependencies: `uv pip install -r requirements.txt`
- Run notebook: `jupyter notebook notebooks/eda.ipynb`
- Preview blog post: `quarto preview` (from the site repo)

## Conventions
- Save figures to `figures/` as PNG with `scale_factor=2`
- Use polars expressions, not pandas APIs
- Pin dependencies in `requirements.txt`
- Keep notebook cells short — one idea per cell
```

Customize it based on your actual project setup — make the "Conventions" section reflect the patterns you want the LLM to repeat.

??? tip "What makes a good CLAUDE.md"
    - **Concrete > abstract.** "Use polars, not pandas" beats "follow modern Python conventions."
    - **Short.** One screen. The LLM reads it every turn.
    - **Living document.** When you catch the LLM making the same mistake twice, that's a signal to add a line.
    - **Project-specific.** Global preferences belong in `~/.claude/CLAUDE.md`; project specifics belong here.

For a deeper guide, see [Project Configuration with CLAUDE.md](../getting-started/ai-coding-assistants.md#project-configuration-with-claudemd).

### Parallel: `copilot-instructions.md`

GitHub Copilot reads `.github/copilot-instructions.md` for the same purpose. Create one in your EDA repo with the same conventions:

```markdown
# Copilot Instructions

This project analyzes the HCRL Survival IDS dataset for automotive intrusion detection.

- Use polars for data manipulation (not pandas)
- Use altair for visualization (not matplotlib/seaborn)
- Use scikit-learn for ML models
- Follow PEP 8; formatter is ruff
- Prefer explicit column names over positional indexing
```

- [ ] `CLAUDE.md` created in EDA project root
- [ ] `.github/copilot-instructions.md` created in EDA project root
- [ ] Both files customized to match your actual project

---

## Part 5: Publish

Write a blog post on your Quarto site reflecting on AI-assisted development. Follow the **[Publishing Guide](publishing-guide.md)** for the full workflow.

**Quick reference for this assignment:**

- **Suggested categories:** `[ai-assistants, tooling, reflection]`
- **Suggested framing:** pick one —
    - **"My LLM habit stack"** — walk through the four habits and give a concrete example of each (screenshot the LLM conversation from Part 3)
    - **"Teaching the assistant: the `CLAUDE.md` I wrote"** — share the file, explain each section, show a before/after of what the LLM produced with and without it
    - **"What Copilot got right and wrong"** — a few honest examples from your actual 2a project
- **Include the saved conversation** from Part 3

- [ ] Blog post written with a clear angle
- [ ] LLM conversation included (screenshot or quoted)
- [ ] Blog post live on your Quarto site

---

## Final Deliverables

- [ ] **Copilot** installed and working in VS Code
- [ ] **LLM practice task** completed (Option A, B, or C from Part 3) with conversation saved
- [ ] **`CLAUDE.md`** created in your EDA project repository
- [ ] **`.github/copilot-instructions.md`** created in your EDA project repository
- [ ] **Blog post** live on your Quarto site

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Copilot not showing suggestions | Check that you're signed in (Copilot icon in status bar). Make sure the file type is supported (`.py`, `.qmd`, etc.) |
| Copilot Chat says "not available" | Ensure `github.copilot-chat` extension is installed and your GitHub Education status is active |
| Copilot suggests pandas instead of polars | Add an explicit instruction in `.github/copilot-instructions.md` — Copilot reads it on every completion |
| LLM generates code that uses a package you don't have | Either install the package or tell the LLM your exact stack in the prompt |
| Claude Code can't find `CLAUDE.md` | Verify the file is named exactly `CLAUDE.md` (all caps, no extension beyond `.md`) and is at the repo root |
