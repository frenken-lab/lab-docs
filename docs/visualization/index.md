---
hide:
  - toc
tags:
  - Visualization
  - Research Communication
  - Diagrams
---
<!-- last-reviewed: 2026-04-24 -->
# Visualization & Diagramming Practices

!!! abstract "What this section covers"
    **How lab members should produce figures and diagrams** for papers (TMLR, NeurIPS, ICML), talks (Slidev decks, conference presentations), and public-facing write-ups. Evidence-based survey of what leading ML communicators actually use, with tool recommendations calibrated for our stack (OSU scarlet palette, MyST/Curvenote papers, Svelte 5 interactive figures, Slidev talks).

    Prerequisites: you're comfortable with git, Python, and at least one of LaTeX / MyST Markdown. No prior diagramming-tool experience assumed.

!!! danger "Calibration warning — these pages were written 2026-04-24 with a known sycophancy/under-research error pattern"
    The factual sections (communicator profiles, Distill primitives inventory, TMLR Beyond PDF submission mechanics, license facts) are evidence-based and reliable.

    The **prescriptive sections** in `architecture-diagrams.md`, `data-figures.md`, and the "One-line recommendations" below are based on uncalibrated synthesis — they were written before reading any specific lab project's existing pipeline. Do not treat them as authoritative. If you're making tooling decisions for a specific paper or deck, read the project's own `CLAUDE.md` and build files first; see `~/paper-tooling-evidence.md` 2026-04-24 session-failure log for the full account of what went wrong and what to verify before acting.

---

## The two pipelines

Most figures in an ML paper fall into exactly one of these categories, and the pipelines should stay separate:

| | **Data-driven** | **Diagram-driven** |
|---|---|---|
| Artifact | training curves, attention heatmaps, confusion matrices, ablations, FLOPs/latency | Figure 1 (system overview), architecture blocks, conceptual diagrams |
| Regeneration need | **High** — reviewer asks for log-scale, the run gets re-trained, a new baseline is added | **Low** — redraw only when the architecture itself changes |
| Expert tool | matplotlib + a shared style file; altair/Vega-Lite if you want interactive + static from one spec | Hand-authored SVG in a Svelte 5 component; TikZ via `pytorch2tikz` as fallback |
| Anti-pattern | "Exported a pandas DataFrame to PNG" — not reproducible, not diffable | Drawing Figure 1 from scratch in PowerPoint for every revision |

The **one thing both pipelines should share** is a small palette file (4–6 named colors, e.g. `STUDENT`, `TEACHER`, `ATTN_HEAD`). Importing it into both a matplotlib style and a Figma/Svelte color library is what makes a paper visually coherent.

---

## :material-compass: Sections

<div class="grid cards" markdown>

-   :material-account-group:{ .lg .middle } **How ML Communicators Work**

    ---

    Evidence-based profiles of five widely-read ML explainers (Jay Alammar, Maarten Grootendorst, Sebastian Raschka, Sasha Rush, François Fleuret) — what tools they actually use, what their figure sources are open, what you can steal.

    [:octicons-arrow-right-24: Read the survey](communicators.md)

-   :material-file-document-multiple:{ .lg .middle } **Distill.pub & TMLR Beyond PDF**

    ---

    Distill's Custom-Element primitives (`d-article`, `d-figure`, `d-cite`, `d-math`, `d-slider`) and the named-column CSS grid. **Key finding:** the new TMLR Beyond PDF track uses Distill's template — every primitive is native in your submission.

    [:octicons-arrow-right-24: See the primitives](distill-and-tmlr.md)

-   :material-sitemap:{ .lg .middle } **Architecture Diagrams**

    ---

    When to use Svelte Flow vs. TikZ vs. hand-authored SVG vs. D2 vs. Penrose. Verdict: for TMLR Figure 1, programmatic *can* compete with Figma — but only two tools actually win on that axis, and they're not Svelte Flow.

    [:octicons-arrow-right-24: Pick a tool](architecture-diagrams.md)

-   :material-chart-scatter-plot:{ .lg .middle } **Data-Driven Figures**

    ---

    matplotlib + `tueplots` for paper PDFs, altair/Vega-Lite when you want the same spec to render interactively in TMLR Beyond PDF, shared palette files so the paper reads as one artifact.

    [:octicons-arrow-right-24: Data figures](data-figures.md)

</div>

---

## :material-lightbulb: One-line recommendations

!!! tip "If you're building a paper Figure 1"
    Hand-authored SVG as a Svelte 5 component in your project's `interactive/` workspace. Own every pixel. Export once, commit the SVG, embed via `image::` in MyST. See [Architecture Diagrams](architecture-diagrams.md).

!!! tip "If you're plotting training curves or attention heatmaps"
    matplotlib with `tueplots` for venue-calibrated defaults, or altair if the paper has a TMLR Beyond PDF interactive version. See [Data-Driven Figures](data-figures.md).

!!! tip "If you're submitting to TMLR Beyond PDF"
    The template **is** Distill.pub. You have `<d-cite>`, `<d-figure>`, `<d-math>`, `<d-slider>` natively — no porting. Interactive figures drop into `assets/html/submission/` as single-file HTML and embed via `<iframe>`. See [Distill & TMLR](distill-and-tmlr.md).

!!! tip "If you're building a Slidev deck"
    Reuse the same Svelte single-file bundles you'd ship to TMLR — they embed identically via `<iframe>` into Slidev slides. One figure, three destinations (paper HTML, paper PDF fallback, deck).

---

## :material-alert-circle-outline: Corrections and caveats

!!! note "Distill uses a system font stack, not IBM Plex"
    A common assumption — including in some earlier notes on this site — is that Distill's distinctive look comes from IBM Plex. It doesn't. [`distillpub/template/src/styles/styles-base.css`](https://raw.githubusercontent.com/distillpub/template/master/src/styles/styles-base.css) ships `-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, ...` — no `@font-face`, no Google Fonts. The Distill look comes from the **named-column CSS grid**, typography rules on `h1`/`h2`/`h3`, and hairline link underlines (`border-bottom: 1px solid rgba(0,0,0,0.4)`).

!!! note "The Annotated Transformer uses altair, not `chalk`"
    People often conflate Sasha Rush's two diagramming projects. The attention-matrix heatmaps in *The Annotated Transformer* are produced by [`altair`](https://altair-viz.github.io/) (Vega-Lite). [`chalk`](https://github.com/chalk-diagrams/chalk) is his *separate* diagramming library, used in Tensor Puzzles and pydiagrams — not in the Annotated series. See [the communicators page](communicators.md#sasha-rush).

!!! warning "Raschka's `LLMs-from-scratch` images are license-excluded"
    The repo is Apache 2.0 with a **modified `Source` definition** that carves out *"any books specific to this software and any related images"*. Verified by reading [`LICENSE.txt`](https://github.com/rasbt/LLMs-from-scratch/blob/main/LICENSE.txt) directly. **Do not copy his figures** for your paper or talk. Redraw in the same style, or ask permission. The architecture-gallery poster is sold commercially on [Gumroad](https://sebastianraschka.com/llm-architecture-gallery/) and Redbubble.

---

## :material-book-search: How this research was compiled

These pages are the output of a structured web investigation conducted April 2026 covering:

1. Three GUI-first communicators (Alammar, Grootendorst, Raschka) — primary sources: newsletter comments, YouTube walkthroughs, interview transcripts, repo license files.
2. Two code-first ML communicators (Rush, Fleuret) — primary sources: reading the actual figure-generating source code on GitHub.
3. The Distill.pub template internals — primary sources: `distillpub/template` source files (Custom Element classes, Rollup config, CSS).
4. TMLR Beyond PDF — primary sources: [tmlr-beyond-pdf.org](https://tmlr-beyond-pdf.org/) submission instructions + inspecting the live example's HTML.
5. Programmatic architecture-diagram tool landscape — primary sources: tool docs, tool repos, ML-paper figure-attribution spot checks.

Every claim that identifies a tool, quotes a person, or describes a license is linked to a primary source in the relevant page's *Sources* section. If a source becomes stale, please [open an issue](https://github.com/OSU-CAR-MSL/lab-setup-guide/issues) or edit the page directly.
