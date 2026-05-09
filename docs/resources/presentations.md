<!-- last-reviewed: 2026-03-09 -->

# Presentations

Slide decks for lab onboarding and training sessions, built with [Quarto RevealJS](https://quarto.org/docs/presentations/revealjs/).

## Available Presentations

### OSC & HPC Overview

An introduction to the Ohio Supercomputer Center for new lab members. Covers OSC clusters, three levels of access (OnDemand, terminal, batch jobs), storage tiers, SLURM job submission, and Python environment setup.

- **Audience:** New MSL lab members
- **Slides:** ~30
- **Source:** `presentations/osc-overview/`

!!! tip "Building the slides"

    ```bash
    cd presentations/osc-overview
    quarto render index.qmd
    # Open _output/index.html in a browser
    ```

    On OSC, render on a login node then transfer to your local machine:

    ```bash
    scp -r pitzer:~/lab-setup-guide/presentations/osc-overview/_output/ ./osc-slides/
    ```

## Adding a New Presentation

1. Copy the [presentation starter template](https://github.com/OSU-CAR-MSL/quarto-lab-templates/tree/main/presentation) as your starting point
2. Create a directory under `presentations/` (e.g., `presentations/my-topic/`)
3. Add `_quarto.yml`, `index.qmd`, `custom.scss`, and an `images/` folder
4. Add `presentations/my-topic/_output/` to `.gitignore`
5. Add an entry to this page

Presentations live outside `docs/` so MkDocs ignores them. Only this index page is part of the docs site.

!!! note "Quarto conventions"

    See the [Quarto RevealJS guide](https://quarto.org/docs/presentations/revealjs/) for syntax reference. Lab-specific conventions (Mermaid handling, defensive settings) are documented in the presentation project's `CLAUDE.md`.
