---
status: new
tags:
  - Visualization
  - Diagrams
  - Svelte
  - TikZ
  - Paper Writing
---
<!-- last-reviewed: 2026-04-24 -->
# Architecture Diagrams

!!! abstract "When programmatic can compete with Figma — and when it can't"
    For an ML paper's Figure 1 (system overview, architecture blocks, distillation diagrams), the honest answer is that **Figma/OmniGraffle still has a large head start** on visual polish. But two programmatic paths *can* meet the polish bar for a TMLR / NeurIPS / ICML Figure 1: **hand-authored SVG as a Svelte 5 component** (Distill's own pattern) and **TikZ via `pytorch2tikz`** (seeds from a live `nn.Module`). Everything else is either too dashboardy (Svelte Flow), too niche (Penrose), too UML (Mermaid v11, D2), or requires a license carve-out you won't notice until the end (D2 TALA).

---

## The verdict

| Use case | Recommended | Why |
|---|---|---|
| **TMLR Figure 1** (system diagram, architecture blocks) | Hand-authored SVG in a Svelte 5 component | Owns every pixel; exports directly to SVG; reuses across paper + talk + slides |
| **TMLR Figure 1 fallback** (if hand-SVG is too expensive) | TikZ via `pytorch2tikz` seeded from your `nn.Module` | Highest ML-paper precedent (Vaswani transformer, ResNet, FCN); matches LaTeX typography |
| **Interactive figure for a talk or Beyond PDF** | Svelte Flow via `@xyflow/svelte` | Animated states, draggable nodes, hover tooltips; the right tool for your Mamba selective-scan demo |
| **Computation graph** (forward/backward pass, autograd) | Graphviz via `pydot` | Tiny, universal, exactly what Karpathy uses in [`micrograd/trace_graph.ipynb`](https://raw.githubusercontent.com/karpathy/micrograd/master/trace_graph.ipynb) |
| **Talk slide (low-stakes)** | Slidev Mermaid fence or any GUI tool | Polish ceiling matters less; iteration speed matters more |
| **Anything claiming "I'll use Mermaid for Figure 1"** | :material-close: Don't | Mermaid v11 architecture-beta is cloud-icon-biased and ugly in print |

---

## Tool comparison

| Tool | Authoring cost | Polish ceiling | ML-paper precedent | Portability (SVG/PDF/MyST) |
|---|---|---|---|---|
| Hand-authored SVG + Svelte 5 | High upfront, low ongoing (you own the primitives) | **Unbounded** — this is how every Distill article looks like a Distill article | Every Distill article ([*Illustrated Transformer*](https://jalammar.github.io/illustrated-transformer/), [*Building Blocks of Interpretability*](https://distill.pub/2018/building-blocks/), all of [Feature Visualization](https://distill.pub/2017/feature-visualization/)) | Pure SVG — trivial in MyST, Slidev iframe, LaTeX `\includegraphics` |
| [TikZ / PlotNeuralNet / pytorch2tikz](https://github.com/fraunhoferhhi/pytorch2tikz) | Learning curve + moderate per-figure once template exists | **Highest** of programmatic tools | 24.7k+ stars; widely used; the original Vaswani transformer block, every ResNet figure, FCN-8/32 figures are TikZ | LaTeX-native PDF/SVG; works in MyST via `tikzjax` or pre-compiled SVG |
| [Svelte Flow / xyflow](https://xyflow.com/) | Low for nodes, high for custom shapes | Medium — "dashboardy" by default | Zero ML-paper figures located; used for blog interactives and UI dashboards | **No native SVG export** ([xyflow discussion #1139](https://github.com/xyflow/xyflow/discussions/1139)); `html-to-image` workaround rasters go through the browser |
| [D2 + TALA](https://d2lang.com/) | Low-to-medium | Medium-high with TALA orthogonal routing; ELK/Dagre give "Graphviz-ish" output | Cloud-infra and MLOps diagrams on D2 homepage; no peer-reviewed ML Figure 1 | SVG, PNG, PDF via CLI. **TALA requires an API token outside evaluation mode** |
| [Mermaid v11 architecture-beta](https://mermaid.ai/open-source/syntax/architecture.html) | Lowest | Low — cloud-icon-biased (cloud, database, disk, server) | Blog posts and READMEs only | SVG export; Mermaid's standard rendering ceiling |
| [Graphviz / dot](https://graphviz.org/) | Low | Low-medium — unmistakable "dot aesthetic" | Karpathy's *micrograd* computation graphs; many ML papers use it silently for small diagrams | Native SVG and PDF; trivially embeddable anywhere |
| [Penrose 3.0 + Bloom](https://penrose.cs.cmu.edu/) | High (Substance + Style + Domain DSL trio) | Very high for mathematical diagrams | Math/geometry papers; zero ML-architecture examples in the gallery | SVG export optimized for LaTeX |
| [tldraw SDK 4.0](https://tldraw.dev/) / [Excalidraw API](https://docs.excalidraw.com/) | Medium | Low for papers — sketchy hand-drawn aesthetic | Neither appears in TMLR/ICML figure credits | SVG export; stylistic fit wrong for journal figures |
| [Observable Plot](https://observablehq.com/plot/) / [Vega-Lite](https://vega.github.io/vega-lite/) | N/A for architecture | — | Data-viz, not architecture | — |

---

## Hand-authored SVG in a Svelte 5 component (recommended)

This is the approach Distill itself recommends in its own [authoring guide](https://distill.pub/guide/). The trade is: highest upfront cost, lowest ongoing cost, absolute control.

### Why it wins for a paper figure

1. **You own every pixel.** Alignment, font, stroke weight, color — all yours. No "Figma autolayout moved my arrow 2 px."
2. **Export is trivial.** `document.querySelector('svg').outerHTML` in dev → commit the static file → embed in MyST with `image::` or in the paper's LaTeX via `\includegraphics`. Same file goes in Slidev.
3. **Version-diffable.** The figure is code. A reviewer asks for a color change, you `sed` the hex and re-export.
4. **Reuses Distill primitives.** You're already inheriting Distill's CSS grid, typography, and (if TMLR Beyond PDF) its `d-figure` / `d-cite`. The architecture figure slots in the same grammar.

### Minimal example

```svelte
<!-- kd-gat-paper/interactive/src/figures/architecture/App.svelte -->
<script>
  import { scaleBand } from 'd3-scale';
  import { linkHorizontal } from 'd3-shape';
  import palette from '$lib/palette.json';

  const w = 800, h = 400;

  const blocks = [
    { id: 'input',    x: 40,  y: 180, w: 100, h: 40, label: 'CAN frames', fill: palette.CAN_BUS },
    { id: 'student',  x: 200, y: 80,  w: 180, h: 240, label: 'Student GAT', fill: palette.STUDENT },
    { id: 'teacher',  x: 420, y: 80,  w: 180, h: 240, label: 'Teacher GAT', fill: palette.TEACHER },
    { id: 'output',   x: 660, y: 180, w: 100, h: 40, label: 'Anomaly score', fill: palette.GAT_ATTN },
  ];

  const edges = [
    { from: 'input',   to: 'student', type: 'solid' },
    { from: 'student', to: 'output',  type: 'solid' },
    { from: 'teacher', to: 'student', type: 'kd',    label: 'KL divergence' },
  ];

  // Bezier edge routing — d3-shape.linkHorizontal() computes the path
  const link = linkHorizontal().x(d => d.x).y(d => d.y);

  function edgePath(e) {
    const a = blocks.find(b => b.id === e.from);
    const b = blocks.find(b => b.id === e.to);
    return link({
      source: { x: a.x + a.w, y: a.y + a.h / 2 },
      target: { x: b.x,       y: b.y + b.h / 2 },
    });
  }
</script>

<svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg">
  {#each edges as e}
    <path
      d={edgePath(e)}
      fill="none"
      stroke="#222"
      stroke-width="1.5"
      stroke-dasharray={e.type === 'kd' ? '4 4' : ''}
    />
  {/each}

  {#each blocks as b}
    <g>
      <rect x={b.x} y={b.y} width={b.w} height={b.h} rx="8"
            fill={b.fill} stroke="#222" stroke-width="1" />
      <text x={b.x + b.w / 2} y={b.y + b.h / 2}
            text-anchor="middle" dominant-baseline="middle"
            font-family="-apple-system, sans-serif" font-size="14">
        {b.label}
      </text>
    </g>
  {/each}
</svg>
```

### Extraction workflow

```bash
# Dev — iterate live
cd kd-gat-paper/interactive
npm run dev

# When the figure is frozen, export once:
# in browser DevTools console on the dev page:
copy(document.querySelector('svg').outerHTML)

# Paste into figures/architecture.svg and commit
```

For parametric regeneration (figure changes when model changes), keep the Svelte component as the source of truth and regenerate the SVG via a headless-browser script (`playwright` + `page.evaluate`) in CI. Most papers don't need this — the architecture is fixed by camera-ready.

### What you lose vs Figma

- **Smart-guides-style auto-layout.** You're computing positions yourself. A small grid helper module (snap-to-40-px) solves most of it.
- **Export-to-PDF for print.** Modern LaTeX `\includegraphics{arch.svg}` works with `svg` package; or convert once with `rsvg-convert arch.svg -f pdf`.
- **Drag-and-drop iteration.** You iterate by editing code. For a paper figure that ships once and rarely changes, this is a non-issue.

---

## TikZ via `pytorch2tikz` (fallback)

[`fraunhoferhhi/pytorch2tikz`](https://github.com/fraunhoferhhi/pytorch2tikz) generates TikZ figures from a live `nn.Module`:

```python
from pytorch2tikz import Architecture
import torch

model = build_kd_gat_model()  # your nn.Module

arch = Architecture(model)
arch.save('figures/architecture.tex')
```

Then in your LaTeX paper:

```latex
\begin{figure}
  \input{figures/architecture.tex}
  \caption{KD-GAT architecture.}
  \label{fig:arch}
\end{figure}
```

**Strengths:**

- Highest polish ceiling in this survey. Vaswani's transformer figure, ResNet's residual block figure, FCN-8/32 figures are all TikZ.
- Seeds from the actual model. Change the number of heads, re-run, re-render.
- Matches body-text typography perfectly — same LaTeX engine.
- 24.7k+ stars on the related [PlotNeuralNet](https://github.com/HarisIqbal88/PlotNeuralNet); active community of ML-paper figures.

**Weaknesses for our lab:**

- Our papers are MyST/Curvenote, not pure LaTeX. TikZ works in MyST via `tikzjax` or via pre-compiled SVG, but you lose the tight font coupling that makes TikZ worthwhile in raw LaTeX.
- TikZ's authoring loop is slower than Svelte's hot-reload.
- Hand-tuning TikZ after auto-generation is necessary; you don't escape manual polish.

**When to choose TikZ over hand-SVG:**

- You're writing pure LaTeX (not MyST).
- You have many architecture variants and want seed-from-model regeneration.
- You're collaborating with someone who already writes TikZ.

---

## Svelte Flow: its actual niche

Svelte Flow ([`@xyflow/svelte`](https://xyflow.com/)) is the Svelte port of React Flow. Excellent for *interactive* node-graph figures. Wrong for *static* paper Figure 1.

**Why wrong for paper:**

- **No native SVG export.** Confirmed in [xyflow discussion #1139](https://github.com/xyflow/xyflow/discussions/1139). Workarounds (`html-to-image`, `dom-to-svg`) rasterize through the browser — text kerning, stroke anti-aliasing, and arrowhead shapes all go through DOM→bitmap.
- **Dashboardy default.** Rounded nodes with subtle shadows, zoom controls, minimap — all optimized for interactive apps, not print.
- **Mixed DOM+SVG rendering** makes PDF fidelity always go through a rasterizer.

**Why right for interactive:**

- Dragging nodes, animated state transitions, hover tooltips, collapsible subflows — all first-class.
- The lab's [Mamba selective-scan demo](https://github.com/OSU-CAR-MSL/presentations/tree/main/interactive/src/figures/mamba/selective-copy-demo) is exactly its niche.
- Single-file HTML export via `vite-plugin-singlefile` → iframe-embeds identically into Slidev, TMLR Beyond PDF, and MyST.

**Rule of thumb:** if the figure has state (time-stepping, user input, animation), use Svelte Flow. If the figure is static ink on a page, use hand-authored SVG.

---

## When each other tool wins

!!! note "D2 + TALA"
    Genuinely competitive for block-diagram architectures. TALA's orthogonal routing is designed for software architecture — which is what GAT + KD looks like (boxes + arrows + containers). SVG/PDF first-class. **But:** [TALA requires an API token](https://terrastruct.com/tala/) outside evaluation mode, and no TMLR-published ML paper using D2 was located in our searches. Skip unless you're doing cloud-infra diagrams.

!!! note "Penrose 3.0 / Bloom"
    Actively maintained ([Bloom Sep 2024](https://penrose.cs.cmu.edu/blog/bloom), [Penrose 3.0 Jul 2023](https://penrose.cs.cmu.edu/blog/v3)). The Substance + Style + Domain three-file DSL is powerful but every gallery example is mathematical (spectral graphs, commutative diagrams, geometry). Zero ML-architecture examples. Overkill for one Figure 1.

!!! note "Mermaid v11 architecture-beta"
    Added in v11 — cloud-icon-centric (cloud, database, disk, server icons). Works for blog posts and READMEs. Wrong aesthetic for paper Figure 1.

!!! note "Graphviz / dot"
    The right tool — and the *only* tool — for computation graphs (forward/backward passes, autograd traces). Karpathy's [`micrograd/trace_graph.ipynb`](https://raw.githubusercontent.com/karpathy/micrograd/master/trace_graph.ipynb) is the canonical pattern. Do not try to draw architecture diagrams with it; the "dot aesthetic" shows through immediately.

!!! note "tldraw SDK 4.0, Excalidraw API"
    Both have programmatic APIs now. Sketchy hand-drawn aesthetic. Good for blog posts; wrong for paper figures.

---

## A note on "invisible layout craft"

A common worry is that Figma provides "invisible layout craft" that a programmatic tool can't match. This is overstated. The craft reduces to:

1. **Aligned rectangles with consistent spacing.** `d3-scale.scaleBand()` or a hand-written 40 px grid snap.
2. **Consistent stroke weight.** One CSS variable: `stroke-width: 1.5`.
3. **Good typography.** One `<style>` block with `font-family` and `font-size` rules.
4. **Considered color.** A shared palette file — see [Data-Driven Figures](data-figures.md#shared-palette-file).

You don't need Figma. You need ~400 lines of SVG and a palette file.

---

## Decision tree

```mermaid
flowchart TD
    A[Figure to produce] --> B{Static or interactive?}
    B -->|Static| C{Pure LaTeX paper or MyST?}
    B -->|Interactive| D{Computation graph?}
    C -->|Pure LaTeX| E[TikZ via pytorch2tikz]
    C -->|MyST/Curvenote| F[Hand-SVG Svelte 5 component]
    D -->|Yes, comp graph| G[Graphviz via pydot]
    D -->|No, architecture or data| H[Svelte Flow or hand-SVG]
    F --> I[Commit SVG, embed via image::]
    E --> J[\input TikZ in LaTeX]
    G --> K[Render DOT → SVG → embed]
    H --> L[Single-file HTML → iframe]
```

---

## Sources

- [xyflow — Svelte Flow / React Flow](https://xyflow.com/)
- [xyflow discussion #1139 — SVG export](https://github.com/xyflow/xyflow/discussions/1139)
- [D2 language](https://d2lang.com/)
- [TALA — Terrastruct's AutoLayout](https://terrastruct.com/tala/)
- [Penrose 3.0](https://penrose.cs.cmu.edu/blog/v3)
- [Bloom (Penrose interactive)](https://penrose.cs.cmu.edu/blog/bloom)
- [Mermaid architecture-beta](https://mermaid.ai/open-source/syntax/architecture.html)
- [Mermaid v11.13 release notes](https://mermaid.ai/blog/posts/mermaid-v11-13-0-two-new-diagram-types-and-our-most-polished-release-yet)
- [Graphviz neural-network gallery](https://graphviz.org/Gallery/directed/neural-network.html)
- [martisak/dotnets](https://github.com/martisak/dotnets)
- [Kroki (unified API for text-based diagrams)](https://kroki.io/)
- [PlotNeuralNet](https://github.com/HarisIqbal88/PlotNeuralNet)
- [fraunhoferhhi/pytorch2tikz](https://github.com/fraunhoferhhi/pytorch2tikz)
- [tldraw SDK 4.0 announcement](https://tldraw.dev/blog/tldraw-sdk-4-0)
- [Excalidraw API docs](https://docs.excalidraw.com/docs/@excalidraw/excalidraw/api)
- [Distill guide — diagrams and interactivity](https://distill.pub/guide/)
- [Distill for R Markdown — diagrams page](https://rstudio.github.io/distill/diagrams.html)
- [Karpathy micrograd — trace_graph.ipynb](https://raw.githubusercontent.com/karpathy/micrograd/master/trace_graph.ipynb)
