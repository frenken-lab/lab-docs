---
hide:
  - toc
---
<!-- last-reviewed: 2026-04-16 -->
# Assignments

!!! abstract "Why these assignments exist"
    Joining a research lab in 2026 is not just "read some papers and start coding." You need to plug into shared infrastructure (OSC compute, W&B tracking, GitHub), adopt the lab's tool stack (polars, altair, uv, PyTorch), and build habits for working with AI coding assistants. **These assignments get you there in ~4 weeks.**

    By the end of onboarding you will have:

    - A published personal academic website that doubles as a portfolio
    - An EDA blog post demonstrating real polars + altair fluency
    - OSC, W&B, and GitHub Education accounts fully set up
    - A neural network you built from scratch — no frameworks
    - A working mental model of package management, dependency resolution, and AI-augmented development

---

## How assignments work

1. **Read the full assignment** before starting — each one lists prerequisites, estimated time, and deliverables.
2. **Work through the tasks in order** — later tasks build on earlier ones.
3. **Ask for help early** — if you're stuck for more than 15 minutes on a setup issue, post in the lab Slack/Teams channel. Setup problems are normal and everyone encounters them.
4. **Publish your deliverables** — every assignment ends with a blog post. See the **[Publishing Guide](publishing-guide.md)** for the workflow.

---

## Current assignments

<div class="grid cards" markdown>

-   :material-web:{ .lg .middle } **Assignment 1: Personal Website**

    ---

    Git, GitHub, VS Code, Quarto, GitHub Pages. Ship a site that's the foundation for every future blog post.

    **3–4 hrs · Beginner**

    [:octicons-arrow-right-24: Start Assignment 1](personal-website.md)

-   :material-chart-scatter-plot:{ .lg .middle } **Assignment 2a: Exploratory Data Analysis**

    ---

    polars, altair, scikit-learn. Explore a real automotive intrusion detection dataset and publish the analysis.

    **6–8 hrs · Beginner**

    [:octicons-arrow-right-24: Start Assignment 2a](exploratory-data-analysis.md)

-   :material-server-network:{ .lg .middle } **Assignment 2b: Research Infrastructure**

    ---

    OSC, W&B, GitHub Education. ML pipeline mental model. SQL as the foundation of experiment tracking.

    **3–4 hrs · Beginner**

    [:octicons-arrow-right-24: Start Assignment 2b](concepts-admin-setup.md)

-   :material-robot:{ .lg .middle } **Assignment 2c: AI-Augmented Development**

    ---

    Copilot, LLM interaction framework, `CLAUDE.md`. Build habits for working with AI assistants effectively.

    **3–4 hrs · Beginner**

    [:octicons-arrow-right-24: Start Assignment 2c](ai-augmented-development.md)

-   :material-package-variant:{ .lg .middle } **Assignment 3a: Package Management Concepts**

    ---

    pip vs conda vs uv. Virtual environments, dependency resolution, lock files. Why this matters on OSC.

    **3–4 hrs · Beginner**

    [:octicons-arrow-right-24: Start Assignment 3a](package-management-concepts.md)

-   :material-brain:{ .lg .middle } **Assignment 3b: Neural Network from Scratch**

    ---

    numpy only. Implement forward pass, backprop, and a training loop. Understand what PyTorch does under the hood.

    **5–7 hrs · Beginner–Intermediate**

    [:octicons-arrow-right-24: Start Assignment 3b](neural-network-from-scratch.md)

</div>

!!! info "Scheduling"
    - **2a + 2b + 2c** are assigned together — **2 weeks total**. 2a is hands-on coding; 2b is lab infrastructure + pipeline concepts; 2c is AI tooling. Part 4 of 2c configures the repo you built in 2a.
    - **3a + 3b** are assigned together — **2 weeks total**. 3a is conceptual; 3b is hands-on. Both end in a blog post.

---

## Cross-cutting references

<div class="grid cards" markdown>

-   :material-rocket-launch:{ .lg .middle } **Publishing Guide**

    ---

    The single reference for turning an assignment into a blog post: YAML headers, categories, preview/commit/push workflow, portfolio habits.

    [:octicons-arrow-right-24: Open the guide](publishing-guide.md)

-   :material-view-gallery:{ .lg .middle } **Student Site Showcase**

    ---

    Example personal sites built by lab members. Use them for inspiration when designing your own.

    [:octicons-arrow-right-24: Browse showcase](site-showcase.md)

-   :material-file-document-edit:{ .lg .middle } **Typst CV Guide (optional)**

    ---

    Upgrade your CV to a professionally typeset PDF with Typst. Not required — but recommended before job applications.

    [:octicons-arrow-right-24: Read the guide](typst-cv-guide.md)

</div>
