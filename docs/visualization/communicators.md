---
status: new
tags:
  - Visualization
  - Research Communication
  - Diagrams
---
<!-- last-reviewed: 2026-04-24 -->
# How ML Communicators Make Their Diagrams

Evidence-based survey of five widely-read ML explainers. The goal is to tell you **what tools they actually use** (with primary-source citations, not guesses) so you can make an informed choice about what to adopt for your own papers and talks.

The short answer: the most visually polished ML explainers on the internet are divided into two camps. **GUI-first** (Alammar, Grootendorst, Raschka) draw in Figma/Keynote/OmniGraffle and ship rendered PNGs — maximum polish, zero reproducibility. **Code-first** (Rush, Fleuret) produce figures from scripts — maximum reproducibility, figures look less "magazine-polished." Neither is wrong; they solve different problems.

---

## Summary comparison

| Communicator | Tool | Confirmed? | License posture | Signature visual |
|---|---|---|---|---|
| **Jay Alammar** | Apple Keynote (+ `datamapplot` for scatter, `ecco` for interpretability) | Yes — [YouTube walkthrough](https://www.youtube.com/watch?v=gSPRxJLxIHA) | Only rendered PNGs in blog repo; no `.key` files | Saturated token-yellow pill rows, N×N attention grids, Magic-Move progressive reveals |
| **Maarten Grootendorst** | Figma (+ manim for one BERTopic animation) | Yes — [newsletter comment](https://newsletter.maartengrootendorst.com/p/a-visual-guide-to-reasoning-llms/comments) | PNG-only in book repo; no Figma Community file | Muted pastels with **per-post color ontology** (e.g. Mamba post: pink=B, purple=A held across ~30 figures) |
| **Sebastian Raschka** | Unknown — the one post that would settle it is [paywalled](https://magazine.sebastianraschka.com/p/workflow-for-understanding-llms); OmniGraffle-on-macOS is a reasonable inference but unverified | No | **Images explicitly license-excluded** from Apache 2.0; Architecture Gallery sold commercially | Flat vector on white, muted pastels, `(B, T, C)` tensor-shape labels inside rectangles |
| **Sasha Rush** | `altair`/Vega-Lite (Annotated series); `chalk` (Tensor Puzzles, separate project); `matplotlib` (Annotated S4) | Yes — read the source | Everything public, liberally licensed | Viridis heatmaps on white, interactive Vega-Lite tooltips, compositional `chalk` SVG for tensor diagrams |
| **François Fleuret** | TikZ + PGFPlots, fed by PyTorch-generated ASCII data tables | Yes — [Overleaf template](https://fleuret.org/francois/lbdl.html) describes the pipeline | PDF free; Python pipeline not in one public repo | Sans-serif math labels, thin strokes, uniform typography with body LaTeX |

---

## Jay Alammar

**Newsletter:** [newsletter.languagemodels.co](https://newsletter.languagemodels.co/) — Director & Engineering Fellow at Cohere, author of *The Illustrated Transformer* (2018, ~4M pageviews), co-author of O'Reilly's *Hands-On Large Language Models*.

**Tool — confirmed.** His YouTube video is explicitly titled *"My Visualization Tools (my Apple Keynote setup for visualizations and animations)"* — [watch it here](https://www.youtube.com/watch?v=gSPRxJLxIHA). Corroborated by Hillel Taub-Tabib's reaction tweet: *"I really love @JayAlammar's visualizations... Surprisingly, it's all plain Keynote!"* ([source](https://x.com/hilleltt/status/1335912281503379460)).

The only non-Keynote tools in the archive are:

- [`datamapplot`](https://newsletter.languagemodels.co/p/the-illustrated-neurips-2025-a-visual) (Python) — used for the NeurIPS 2025 paper-landscape plot: Cohere embeddings → UMAP → K-Means.
- [`ecco`](https://github.com/jalammar/ecco) (his own library) — interpretability visualizations (attention heads, hidden-state probes).

No Figma, Illustrator, Sketch, Excalidraw, TikZ, Mermaid, or D3 in his explainer figures.

**Style signature.** Saturated primaries on white. A signature **golden-yellow token** ("token-yellow"), muted blue for query/key/value, green for outputs, red/orange for problems/rejected paths, teal accent. Rounded rectangles for tokens/vectors, square cells for matrix entries, 1–2 px black/dark-gray strokes. Math lives *beside* figures as KaTeX, not inside.

**Layout patterns.** Horizontal token streams running left-to-right. Transformer blocks as nested rounded rectangles (outer = block, inner = sublayers) with residual arrows bypassing. Multi-panel builds with ~5–10 progressive reveals — which is precisely what Keynote's Magic Move / Build Order optimizes for.

**Open-source posture.** [`github.com/jalammar/jalammar.github.io`](https://github.com/jalammar/jalammar.github.io) is the Jekyll blog — **rendered PNGs only**, no `.key` sources. There's no Figma Community file, no Notion template, no open figure repo. His open-source output is code ([`ecco`](https://github.com/jalammar/ecco)), not figure sources.

**Relevance to us.** If you want the Alammar look for a talk, Keynote or its open-source equivalents (Google Slides, Slidev) will get you 80% of the way. His YouTube walkthrough is the closest thing to a published curriculum for this aesthetic.

---

## Maarten Grootendorst

**Newsletter:** [newsletter.maartengrootendorst.com](https://newsletter.maartengrootendorst.com/) — Senior Data Scientist, author of BERTopic, co-author with Jay Alammar of *Hands-On Large Language Models*. Famous for "A Visual Guide to..." series on Mamba, Mixture of Experts, Quantization, LLM Agents, Reasoning LLMs.

**Tool — confirmed.** In a reply to commenter `datnt114` on *A Visual Guide to Reasoning LLMs*, he wrote verbatim:

> *"Thank you for the kind words! I'm using Figma to create the visualizations but all visuals (same with my other visual guides) could have been done with something like Powerpoint, KeyNote, etc."*

([source — newsletter comments](https://newsletter.maartengrootendorst.com/p/a-visual-guide-to-reasoning-llms/comments))

For animations (e.g. the BERTopic rotating 3D embedding), he uses [`manim`](https://github.com/3b1b/manim) — the 3Blue1Brown library — per [this interview](https://medium.com/data-science/learning-from-machine-learning-maarten-grootendorst-bertopic-data-science-psychology-9ed9b9b2921): *"I did that with the software of 3Blue1Brown."* In the same interview he cites Jay Alammar as his direct influence: *"I started out learning transformer based models with the visualizations of Jay Alammar."*

**Style signature.** Muted/pastel palette. In the [Mamba guide](https://newsletter.maartengrootendorst.com/p/a-visual-guide-to-mamba-and-state), he maintains a **per-post color ontology** — soft pink/salmon for matrix B, teal/cyan for hidden states, purple/lavender for matrix A, mustard yellow, soft blue — and **each hue stays mapped to one mathematical role across ~30 figures**. This is the single most copyable practice in his work.

Rounded rectangles for tokens/weights (generous ~8–12 px corner radius), pills for states, matrices as subdivided large rectangles. Sans-serif throughout (likely Figma's default Inter or Helvetica-family). Pure white backgrounds, no grids, heavy whitespace. Flat fills — no gradients. Arrows are thin solid black/dark-gray with standard triangular heads.

**Volume.** *"Almost 300 custom-made figures"* in the *Hands-On LLM* book ([llm-book.com](https://www.llm-book.com/)); *"more than 50 custom visuals"* in the [Quantization post](https://newsletter.maartengrootendorst.com/p/a-visual-guide-to-quantization); *"over 60 custom visuals"* in [LLM Agents](https://newsletter.maartengrootendorst.com/p/a-visual-guide-to-llm-agents).

**Open-source posture.** [`HandsOnLLM/Hands-On-Large-Language-Models`](https://github.com/HandsOnLLM/Hands-On-Large-Language-Models) ships `/images/*.png` only — **no SVGs, no `.fig` files, no Figma Community link** (verified via GitHub code search: 0 SVG hits). Neither his [personal site](https://www.maartengrootendorst.com/) nor the newsletter About page links a Figma file.

**Relevance to us.** The per-post color ontology is the single best-practice idea in this survey. For your paper, define 4–6 semantic colors (`STUDENT`, `TEACHER`, `GAT_ATTN`, `CAN_BUS`, ...) and hold them constant across every figure in the paper, the talk, and any interactive demo. This alone makes a paper read as one artifact.

---

## Sebastian Raschka

**Newsletter:** [magazine.sebastianraschka.com](https://magazine.sebastianraschka.com/) (*Ahead of AI*) — author of *Build a Large Language Model (From Scratch)*, *Machine Learning Q and AI*, creator of the [LLM Architecture Gallery](https://sebastianraschka.com/llm-architecture-gallery/).

**Tool — unverified.** Across the paywalled *"My Workflow for Understanding LLM Architectures"* article, three long-form podcast appearances, the `LLMs-from-scratch` README, and two blog posts about the Architecture Gallery, **no public statement names a specific drawing app**. OmniGraffle-on-macOS is a reasonable inference from visual fingerprints (crisp vector rectangles, no hand-drawn jitter, consistent 1–1.5 px strokes, no matplotlib serifs) but we could not substantiate it with a direct quote.

The [paywalled article](https://magazine.sebastianraschka.com/p/workflow-for-understanding-llms) (\$5/mo) is the most likely single source of truth. If you subscribe and find out, please update this page.

**Style signature.** Observed from [*Understanding Multimodal LLMs*](https://magazine.sebastianraschka.com/p/understanding-multimodal-llms) and the [MoE chapter README](https://github.com/rasbt/LLMs-from-scratch/blob/main/ch04/07_moe/README.md):

- Palette: muted, desaturated — pale blues, mint/sage greens, lavender, soft grays on pure white; red/orange reserved for highlight.
- Tensors: stacked/offset rectangles with rounded corners; solid-fill rectangles for single slices.
- Typography: geometric sans-serif; not matplotlib's DejaVu Sans. Consistent with SF Pro / Inter / Helvetica Neue — cannot confirm without source files.
- Strokes: uniform thin black outlines (~1 px), orthogonal arrows with small filled heads, no gradients, no shadows.
- Annotations: dimension labels like `(B, T, C)` placed *inside* or *below* the tensor rectangle in a monospaced face.

**Volume.** 275 custom figures in *Build an LLM from Scratch*, per Manning's [product page](https://www.manning.com/books/build-a-large-language-model-from-scratch).

!!! warning "License carve-out — do not copy his figures"
    [`rasbt/LLMs-from-scratch/LICENSE.txt`](https://github.com/rasbt/LLMs-from-scratch) ships a **modified Apache 2.0**: the `"Source"` definition is altered to read *"explicitly excluding any books specific to this software and any related images"*. Code is Apache 2.0; figures are **not**.

    The repo contains **zero image files** — figures are hot-linked from [`sebastianraschka.com/images/LLMs-from-scratch-images/...webp`](https://sebastianraschka.com/images/LLMs-from-scratch-images/).

    The [Architecture Gallery poster](https://sebastianraschka.com/llm-architecture-gallery/) is sold on [Gumroad](https://sebastianraschka.com/llm-architecture-gallery/) and [Redbubble](https://www.redbubble.com/i/poster/LLM-Architecture-Gallery-by-Ahead-of-AI/179274487/flk2). A 24836×21288 px PNG export (~133 MB) is referenced — the canonical archive is raster.

    **Redraw in the same style, or ask permission. Do not include his figures in a paper or talk.**

**Relevance to us.** The `(B, T, C)` tensor-shape-label convention is worth stealing — a clean way to show activation shapes in any architecture figure.

---

## Sasha Rush

**Home:** [rush-nlp.com](https://rush-nlp.com/) — Cornell Tech / Hugging Face. Author of [*The Annotated Transformer*](https://nlp.seas.harvard.edu/annotated-transformer/), [*The Annotated S4*](https://srush.github.io/annotated-s4/), [*Annotated Mamba*](https://srush.github.io/annotated-mamba/), [MiniTorch](https://minitorch.github.io/), [Tensor Puzzles](https://github.com/srush/Tensor-Puzzles), [GPU Puzzles](https://github.com/srush/GPU-Puzzles).

**Tool — confirmed by reading source code.** This is where the misconception lives. Rush has **two separate diagramming projects**:

### 1. `altair` (Vega-Lite) for the Annotated series

The Annotated Transformer's figures — subsequent-mask heatmap, position-encoding line plot, learning-rate schedule, label-smoothing heatmap, attention-head heatmaps — are all **altair/Vega-Lite**.

Read [`the_annotated_transformer.py`](https://raw.githubusercontent.com/harvardnlp/annotated-transformer/master/the_annotated_transformer.py):

```python
# line 120
import altair as alt

# line 473 — subsequent mask heatmap
alt.Chart(...).mark_rect().encode(
    alt.Color("Subsequent Mask:Q", scale=alt.Scale(scheme="viridis"))
)

# line 1974 — attention-head heatmaps
alt.Chart(...).mark_rect().encode(...)
```

Not matplotlib. Not `chalk`.

[*Annotated S4*](https://raw.githubusercontent.com/srush/annotated-s4/main/s4/s4.py) uses **matplotlib + seaborn** for its spectral/kernel plots — a different stack again.

### 2. `chalk` (declarative diagramming DSL) for Tensor Puzzles

[`chalk-diagrams/chalk`](https://github.com/chalk-diagrams/chalk) is a separate library co-authored with Dan Oneață, *"heavy inspiration from Haskell's diagrams, Scala's doodle, and Jeremy Gibbons's lecture notes"*. It powers [Tensor Puzzles](https://github.com/srush/Tensor-Puzzles) (the README installs `git+https://github.com/danoneata/chalk@srush-patch-1` and calls `draw_examples()` for every tensor figure) and the [pydiagrams gallery](https://srush.github.io/pydiagrams/) (LeNet, Hanoi, Hilbert curves).

Chalk is compositional: `hcat` and `vcat` combinators for horizontal/vertical concatenation, `beside` for overlay, SVG output in monochrome.

**Style signature.** Vega-Lite: viridis-on-white heatmaps with interactive tooltips. Chalk: black-line monochrome SVG, compositional layouts, code-driven arrow routing.

**Open-source posture.** Everything public: [`harvardnlp/annotated-transformer`](https://github.com/harvardnlp/annotated-transformer), [`srush/annotated-s4`](https://github.com/srush/annotated-s4), [`srush/Tensor-Puzzles`](https://github.com/srush/Tensor-Puzzles), [`chalk-diagrams/chalk`](https://github.com/chalk-diagrams/chalk). Every figure is an executable function of model state.

**Relevance to us.** Rush's model is the closest code-first analogue to what Alammar/Grootendorst/Raschka offer in GUI form. For data-driven figures that want to be both static and interactive (which matters in TMLR Beyond PDF), **altair is the right primitive** — see [Data-Driven Figures](data-figures.md#altair-vega-lite).

---

## François Fleuret

**Home:** [fleuret.org](https://fleuret.org/francois/) — University of Geneva. Author of [*The Little Book of Deep Learning*](https://fleuret.org/public/lbdl.pdf) (free, ~120 pages, distinctive typography).

**Tool — confirmed.** From the [Overleaf template page](https://www.overleaf.com/latex/templates/little-book/wzbbdmdtvtkn):

> *"The book is highly illustrated using LaTeX's packages TikZ and PGFPlots, with figures numerically generated through computations done in Python using the PyTorch library, and the output stored as ASCII files that are read by LaTeX for visualization."*

A single `maths-preamble.tex` stylesheet controls fonts, sizes, colors — hence the uniform look across all ~120 pages.

**Pipeline (three stages):**

1. PyTorch script computes the data (e.g. a learning-rate trajectory, a loss landscape slice).
2. Script dumps to an ASCII file (CSV-like).
3. `\input{}`-ed TikZ/PGFPlots reads the ASCII at LaTeX compile time and renders.

**Style signature.** Sans-serif math labels, thin black strokes, uniform teal/orange accent palette, PGFPlots axes on compute-derived curves. The typography is perfectly aligned with the body LaTeX — same fonts, same kerning, because they're the same typesetting engine.

**Open-source posture.** PDF is [free](https://fleuret.org/public/lbdl.pdf); an Overleaf template exists but the full figure-generating Python is not in one mirrored public repo. The pipeline is described publicly but the source is not.

**Relevance to us.** The *PyTorch → ASCII → TikZ* pattern is the gold standard if you're writing a pure-LaTeX paper. For MyST/Curvenote (what our lab uses), the analogous pattern would be **PyTorch → JSON → altair/Svelte component** — same idea, web-native. See [Data-Driven Figures](data-figures.md).

---

## Key misconceptions

!!! warning "What people get wrong about these five"
    1. **Distill uses IBM Plex.** Wrong. System font stack — see [Distill & TMLR](distill-and-tmlr.md#typography).
    2. **The Annotated Transformer uses `chalk`.** Wrong. It uses altair/Vega-Lite. `chalk` is Rush's separate library, used in Tensor Puzzles.
    3. **Raschka's `LLMs-from-scratch` figures are Apache 2.0.** Wrong. The license carves images out explicitly.
    4. **Grootendorst draws in PowerPoint.** He has publicly said he uses Figma (and that PowerPoint/Keynote *could* produce similar visuals).
    5. **Alammar uses D3/Observable for his Illustrated series.** Wrong. It's Keynote — he has a YouTube walkthrough of his setup.
    6. **All five use the same lineage.** Partially true — Grootendorst cites Alammar explicitly as his starting point; Raschka and Rush evolved independently.

---

## What to steal, what to leave

| Practice | Steal it | Leave it |
|---|---|---|
| **Per-post color ontology** (Grootendorst) | :material-check: Yes — define 4–6 semantic colors once, hold them constant across every figure in the paper and talk | |
| **Progressive reveals** (Alammar) | :material-check: Yes for talks — Slidev's `<v-clicks>` does exactly this | Not applicable to static paper figures |
| **`(B, T, C)` tensor-shape labels** (Raschka) | :material-check: Yes — cleanest way to show activation shapes in an architecture figure | |
| **altair heatmaps** (Rush) | :material-check: Yes for data-driven figures — one spec renders to both PNG and interactive HTML | |
| **PyTorch → ASCII → TikZ pipeline** (Fleuret) | Yes if you're writing pure LaTeX | :material-close: Skip for MyST/Curvenote — use PyTorch → JSON → Svelte instead |
| **Copying their actual figures** | | :material-close: No — attribution is required for Alammar/Grootendorst/Rush (permissive but credit them); **forbidden for Raschka** |

---

## Sources

Primary sources cited above; cross-checked by reading repo source files and watching the Alammar YouTube video directly.

**Alammar**

- [The Illustrated Transformer (2018)](https://jalammar.github.io/illustrated-transformer/)
- [jalammar.github.io](https://jalammar.github.io/)
- [YouTube — "My Visualization Tools"](https://www.youtube.com/watch?v=gSPRxJLxIHA)
- [About page — Language Models & Co.](https://newsletter.languagemodels.co/about)
- [Tweet — Hillel Taub-Tabib confirming Keynote](https://x.com/hilleltt/status/1335912281503379460)
- [What's AI Podcast interview](https://www.louisbouchard.ai/jay-alammar/)
- [The Illustrated NeurIPS 2025 — datamapplot post](https://newsletter.languagemodels.co/p/the-illustrated-neurips-2025-a-visual)
- [ecco library](https://github.com/jalammar/ecco)
- [newsletter.languagemodels.co archive](https://newsletter.languagemodels.co/archive)

**Grootendorst**

- [Reasoning LLMs post — Figma confirmation](https://newsletter.maartengrootendorst.com/p/a-visual-guide-to-reasoning-llms/comments)
- [Medium interview — manim + Alammar influence](https://medium.com/data-science/learning-from-machine-learning-maarten-grootendorst-bertopic-data-science-psychology-9ed9b9b2921)
- [Hands-On LLM book site](https://www.llm-book.com/)
- [HandsOnLLM/Hands-On-Large-Language-Models repo](https://github.com/HandsOnLLM/Hands-On-Large-Language-Models)
- [Visual Guide to Mamba](https://newsletter.maartengrootendorst.com/p/a-visual-guide-to-mamba-and-state)
- [Visual Guide to MoE](https://newsletter.maartengrootendorst.com/p/a-visual-guide-to-mixture-of-experts)
- [Visual Guide to LLM Agents](https://newsletter.maartengrootendorst.com/p/a-visual-guide-to-llm-agents)
- [Visual Guide to Quantization](https://newsletter.maartengrootendorst.com/p/a-visual-guide-to-quantization)
- [Personal site](https://www.maartengrootendorst.com/)

**Raschka**

- [*My Workflow for Understanding LLMs* — paywalled](https://magazine.sebastianraschka.com/p/workflow-for-understanding-llms)
- [LLMs-from-scratch repo and license](https://github.com/rasbt/LLMs-from-scratch)
- [*Understanding Multimodal LLMs*](https://magazine.sebastianraschka.com/p/understanding-multimodal-llms)
- [Manning — *Build a Large Language Model*](https://www.manning.com/books/build-a-large-language-model-from-scratch)
- [llm-architecture-gallery repo](https://github.com/rasbt/llm-architecture-gallery)
- [MoE chapter — hot-linked webp images](https://github.com/rasbt/LLMs-from-scratch/blob/main/ch04/07_moe/README.md)
- [LLM Architecture Gallery — sold on Gumroad](https://sebastianraschka.com/llm-architecture-gallery/)
- [Redbubble poster listing](https://www.redbubble.com/i/poster/LLM-Architecture-Gallery-by-Ahead-of-AI/179274487/flk2)
- [SDS-767 podcast](https://www.superdatascience.com/podcast/sds-767-open-source-llm-libraries-and-techniques-with-dr-sebastian-raschka)
- [Writing *Python Machine Learning* 2nd ed — matplotlib 2.0 transition](https://sebastianraschka.com/blog/2015/writing-pymle.html)

**Rush**

- [The Annotated Transformer source — altair calls](https://raw.githubusercontent.com/harvardnlp/annotated-transformer/master/the_annotated_transformer.py)
- [chalk-diagrams/chalk](https://github.com/chalk-diagrams/chalk)
- [chalk-diagrams on PyPI](https://pypi.org/project/chalk-diagrams/)
- [Tensor Puzzles](https://github.com/srush/Tensor-Puzzles)
- [pydiagrams gallery](https://srush.github.io/pydiagrams/)
- [Annotated S4 source — matplotlib calls](https://raw.githubusercontent.com/srush/annotated-s4/main/s4/s4.py)

**Fleuret**

- [*The Little Book of Deep Learning* PDF](https://fleuret.org/public/lbdl.pdf)
- [LBDL home page](https://fleuret.org/francois/lbdl.html)
- [Overleaf template describing pipeline](https://www.overleaf.com/latex/templates/little-book/wzbbdmdtvtkn)
