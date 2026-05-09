---
status: new
tags:
  - Visualization
  - Distill
  - TMLR
  - Svelte
  - Paper Writing
---
<!-- last-reviewed: 2026-04-24 -->
# Distill.pub Primitives & TMLR Beyond PDF

!!! abstract "The big finding"
    **TMLR's new Beyond PDF track uses Distill.pub's template as its rendering engine.** Every `d-*` custom element Distill ships — `d-article`, `d-figure`, `d-cite`, `d-bibliography`, `d-footnote`, `d-math`, `d-slider` — is native in a TMLR Beyond PDF submission. There is no port, no polyfill, no framework adapter. You author in Markdown, drop Distill tags inline, and publish.

    Interactive figures embed as `<iframe>` pointing at self-contained HTML in `assets/html/submission/` — structurally identical to how our lab's Slidev decks already embed Svelte bundles via `interactive/build.js`. A single Svelte 5 + Vite single-file bundle ships to **three destinations** (Slidev deck, TMLR submission, MyST draft) with zero modifications.

---

## TMLR Beyond PDF submission structure

From the [official submission instructions](https://tmlr-beyond-pdf.org/submission-instructions):

```
submission_folder/
├── submission.md
└── assets/
    ├── img/submission/          # static images (PNG, SVG, JPG)
    ├── gif/submission/          # videos as GIF
    ├── html/submission/         # interactive figures as self-contained HTML
    └── bibliography/submission.bib
```

The instructions say verbatim: *"Add dynamic HTML content (that can include Javascript for animations, etc.) to `assets/html/submission/`."* Build is local via Docker + `python compile_submission.py`; output is uploaded as a zip to OpenReview alongside a PDF-for-archive fallback.

### The canonical iframe embedding pattern

From inspecting the [live example submission](https://tmlr-beyond-pdf.org/under_review/submission/), every interactive figure uses raw HTML `<figure>` + `<iframe>` inside the Markdown:

```html
<figure style="text-align: center;">
  <iframe src="/assets/html/submission/physics.html"
          width="100%" height="600"
          style="border: none; border-radius: 12px;"
          title="Interactive Physics">
  </iframe>
  <figcaption>Interactive physics sandbox.</figcaption>
</figure>
```

The referenced [`physics.html`](https://tmlr-beyond-pdf.org/assets/html/submission/physics.html) (13.5 KB) is a standalone page with its own `<!DOCTYPE html>`, inlined `<style>`, and script tags — **structurally identical to what `vite-plugin-singlefile` emits from our lab's `interactive/` Svelte workspaces**.

### Gotchas

!!! warning "Things to plan around"
    1. **Absolute `/assets/...` paths.** The compiled site serves from `/tmlr-beyond-pdf/under_review/<id>/`, so leading slashes resolve correctly. Don't use `./` or `../`.
    2. **Fonts inside the iframe are isolated.** The Distill outer page uses Roboto; your Svelte bundle must self-inline any custom fonts. `vite-plugin-singlefile` does this automatically, but double-check for external `@font-face` calls.
    3. **Height is hard-coded per embed.** No auto-resize. Pick `height=` deliberately or add a `postMessage` resize handshake between the iframe and the host.
    4. **PDF archive is required.** OpenReview still wants a PDF copy. *"Print to PDF"* renders a blank iframe — plan to include a static screenshot fallback with a *"see HTML version at &lt;URL&gt;"* caption.
    5. **No MyST in Beyond PDF.** TMLR Beyond PDF is CommonMark + Distill tags (`<d-cite>`, `<d-bibliography>`). If your paper source is MyST, you port the prose once; figures reuse as-is.

---

## Distill primitives inventory

The [`distillpub/template`](https://github.com/distillpub/template) ships ~20 plain `HTMLElement` subclasses — **no framework runtime, no Svelte, no React inside the template itself**. Svelte only enters inside *article* repos (e.g. [`post--visual-exploration-gaussian-processes`](https://github.com/distillpub/post--visual-exploration-gaussian-processes)). The template is framework-free and bundled as a single UMD file `dist/template.v2.js`.

| Element | Role | Native in TMLR? | Worth porting to Slidev? |
|---|---|:---:|:---:|
| `d-article` | Wrapper; `MutationObserver` wraps loose text nodes in spans | :material-check: | |
| `d-title` / `d-byline` / `d-front-matter` | Title + authors + metadata JSON | :material-check: | |
| `d-abstract` / `d-interstitial` | Semantic section wrappers | :material-check: | |
| `d-figure` | Lazy-render via dual `IntersectionObserver` (2× viewport pre-warm + on-screen trigger, 500 ms scroll debounce) | :material-check: | :material-check: (iframe figures benefit) |
| `d-cite` | Emits `onCiteKeyCreated`/`onCiteKeyChanged` events; renders hover preview | :material-check: | |
| `d-bibliography` | Parses BibTeX from inline `<script>` or `src`; dispatches `onBibliographyChanged` | :material-check: | |
| `d-citation-list` / `d-references` | Render formatted reference list | :material-check: | |
| `d-footnote` | Numbered `<sup>` + hover preview + side-gutter aside | :material-check: | |
| `d-footnote-list` | Auto-aggregated footnote section | :material-check: | |
| `d-hover-box` | Absolute-positioned preview card shared by cite + footnote | :material-check: | |
| `d-math` | KaTeX auto-render; `[block]` attr toggles display mode | :material-check: | |
| `d-code` | Prism.js highlight; must specify `language=` | :material-check: | |
| `d-slider` | D3-drag pointer + Home/End/PgUp/PgDn keyboard + `input`/`change` events + `aria-valuenow` | :material-check: | :material-check: (reusable for demos) |
| `d-toc` | Auto-generates TOC from h2/h3 | :material-check: | |
| `d-appendix` / `distill-header` / `distill-footer` | distill.pub site chrome — **not** for TMLR | :material-close: | :material-close: |

Implementation details:

- All primitives are plain `class FooBar extends HTMLElement` — registered with `customElements.define()` in [`src/components.js`](https://raw.githubusercontent.com/distillpub/template/master/src/components.js).
- Three mixins in `src/mixins/`: `template.js` (shadow-DOM template injection), `mutating.js` (re-render on textContent mutation), `properties.js` (attribute↔property reflection).
- [`d-math`](https://raw.githubusercontent.com/distillpub/template/master/src/components/d-math.js) lazy-loads KaTeX from CDN; the `[block]` attribute toggles `displayMode: true` + `display: block`.
- [`d-figure`](https://raw.githubusercontent.com/distillpub/template/master/src/components/d-figure.js) uses dual `IntersectionObserver` — one at 2× viewport margin for pre-warm, one at `[0, 1.0]` threshold for on-screen commit.
- [`d-slider`](https://raw.githubusercontent.com/distillpub/template/master/src/components/d-slider.js) depends only on `d3-drag`; keyboard semantics (Home/End/PgUp/PgDn/arrows) are the non-obvious spec to preserve when porting.

---

## The crown jewel: the named-column CSS grid

Distill's most reusable asset is not any `d-*` element. It's the **named-column CSS Grid** in [`styles-layout.css`](https://raw.githubusercontent.com/distillpub/template/master/src/styles/styles-layout.css) — four breakpoints (mobile / 768 / 1000 / 1180) with classes `.l-body` (~684 px text column), `.l-page`, `.l-body-outset`, `.l-middle`, `.l-screen`, `.l-gutter`.

Side-gutter footnotes are **pure CSS** — no JS positioning:

```css
d-article aside {
  grid-column: gutter;
  font-size: 12px;
  /* ... */
}
```

This layout vocabulary is what makes Distill look Distill. The fonts are a generic system stack (`-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, ...`) — **not** IBM Plex or any custom webfont. The distinctive feel comes from the grid + typography rules on headings + the hairline link underline (`border-bottom: 1px solid rgba(0,0,0,0.4)`).

---

## Typography

```css
/* From distill-template/src/styles/styles-base.css */
body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI",
               Roboto, Oxygen, Ubuntu, Cantarell,
               "Fira Sans", "Droid Sans", "Helvetica Neue", Arial,
               sans-serif;
}

d-article a {
  color: inherit;
  border-bottom: 1px solid rgba(0, 0, 0, 0.4);
  text-decoration: none;
}
```

No `@font-face`. No Google Fonts. No Plex. The "academic but web-first" feel is CSS Grid + typography rules + link styling — nothing more.

---

## Svelte + D3 composition: 2019 vs 2026

Inside Distill article repos (not the template), Svelte 2/3 components were used to organize interactive figures. The canonical example is [`post--visual-exploration-gaussian-processes`](https://github.com/distillpub/post--visual-exploration-gaussian-processes).

### 2019 pattern: Svelte shell, D3-dominant

```html
<!-- Posterior.html (Svelte 2, paraphrased from the GP article) -->
<svg ref:covMat viewBox="0 0 {w} {h}"></svg>

<script>
  export default {
    oncreate() {
      // D3 owns all DOM mutation — enter/update/exit joins
      d3.select(this.refs.covMat)
        .selectAll('path')
        .data(this.get('data'))
        .enter()
        .append('path')
        .attr('d', d3.line()(...));
    },
    onupdate({ changed }) {
      if (changed.data) {
        d3.select(this.refs.covMat)
          .select('.zero')
          .transition().duration(750)
          // ...
      }
    }
  };
</script>
```

Svelte owned only the empty SVG shell. D3 handled every DOM mutation, enter/update/exit join, and transition. Cross-component state traveled via **DOM events on refs**, not Svelte stores. This was correct for Svelte 2's coarse-grained reactivity — D3's enter/update/exit was the fine-grained update engine.

### 2026 pattern: flip it — Svelte 5 runes own everything

Svelte 5 gives you runes (`$state`, `$derived`, `$effect`) that rival D3's update model. D3 shrinks to math-only (`d3-scale`, `d3-shape`, `d3-hierarchy`, `d3-force`). No more `d3.select`, no more enter/update/exit.

```svelte
<!-- Posterior.svelte — Svelte 5 -->
<script>
  import { scaleLinear } from 'd3-scale';
  import { line, curveBasis } from 'd3-shape';

  let { data, width = 600, height = 300 } = $props();

  let x = $derived(
    scaleLinear().domain([0, data.length - 1]).range([0, width])
  );
  let y = $derived(
    scaleLinear().domain([0, 1]).range([height, 0])
  );
  let pathD = $derived(
    line().x((d, i) => x(i)).y(d => y(d)).curve(curveBasis)(data)
  );
</script>

<svg {width} {height}>
  <path d={pathD} stroke="black" fill="none" />
  {#each data as v, i}
    <circle cx={x(i)} cy={y(v)} r="3" />
  {/each}
</svg>
```

**What changed:**

| Concern | Svelte 2 + D3 (2019) | Svelte 5 + `d3-scale`/`d3-shape` (2026) |
|---|---|---|
| DOM mutation | `d3.select(...).selectAll(...).data(...).enter().append(...)` | `{#each}` block in template |
| Attribute updates | `.transition().duration(750).attr(...)` | `$derived` + template binding |
| Event flow | `refs.foo.on('update', ...)` DOM events | `$props()` down, callbacks up (`onchange={...}`) |
| Testability | Needs jsdom to exercise D3 mutation | `$derived` values testable without a DOM |
| LOC for a typical figure | ~150–200 lines | ~50–80 lines |

For any **new** interactive figure in a lab paper or deck, use the 2026 pattern. The old pattern still works if you're porting existing Distill components (e.g. forking a `distillpub/post--*` repo wholesale) but there's no reason to write new code that way.

---

## Distill's successors (2026 ecosystem)

Distill paused accepting new submissions [July 2, 2021](https://distill.pub/). No "Distill 2.0" exists. Viable modern stacks with overlapping goals:

| Stack | Strengths | Weaknesses | Our lab uses it for... |
|---|---|---|---|
| **MyST + Curvenote** | Scientific markdown → web, native `{figure}`/`{cite}` directives, TMLR Beyond PDF–adjacent | Interactive figure story is less polished than Distill's; no `d-slider` equivalent | `kd-gat-paper` (Curvenote sync) |
| **TMLR Beyond PDF** | Distill template natively, low-overhead | TMLR-specific, not portable | The paper's public HTML version |
| **[Quarto](https://quarto.org/)** | Pandoc-based, multi-output (HTML/PDF/Word), excellent cite/math | Weaker custom-interactivity story than Distill | Occasional one-off reports |
| **[Observable Framework](https://observablehq.com/framework/)** | Vite-based static site generator for data apps | Awkward for prose-heavy articles | Data dashboards, not papers |
| **[HF distill-blog-template](https://github.com/huggingface/distill-blog-template)** | Community fork of Distill template on HF Spaces | Still Svelte 3 + Webpack 4 | Not currently used |
| **Slidev** | Vue 3 + Markdown, iframe-embed for Svelte Flow | Presentation-only, not papers | All lab talks |

---

## Port plan: what to reuse for lab projects

For `presentations/shared/` (Slidev addon):

1. **Copy Distill's `styles-layout.css`** verbatim into `shared/style.css`, namespaced under `.distill-grid`. Decks opt in per-slide with `<div class="distill-grid">`.
2. **Port `d-figure`** as a Svelte 5 component using `$effect` + `IntersectionObserver`. ~30 lines. Worth it because iframe figures benefit from lazy mount.
3. **Port `d-slider`** as a Svelte 5 component — pointer events + runes + keyboard semantics (Home/End/PgUp/PgDn/arrows). ~60 lines. Reusable for interactive demos.
4. **Skip** `d-math` (Slidev has KaTeX), `d-code` (Slidev has Shiki), `d-cite`/`d-bibliography` (decks don't need academic cites).

For `kd-gat-paper/`:

5. In `submission.md` use Distill primitives natively: `<d-cite key="vaswani2017">`, `<d-bibliography src="assets/bibliography/submission.bib">`, `<d-figure>`, `<d-math>`. No port — they're in the template.
6. Build Figure 1 as a hand-authored SVG Svelte component under `kd-gat-paper/interactive/src/figures/architecture/`. See [Architecture Diagrams](architecture-diagrams.md).
7. Drop the same single-file HTML bundle into three places: `assets/html/submission/` (TMLR), `decks/<deck>/public/figures/` (Slidev), `figures/` via `{raw} html` iframe fallback (MyST draft).

Net: **one Svelte component library, three iframe destinations, shared Distill layout CSS**.

---

## Sources

- [TMLR main page](https://jmlr.org/tmlr/)
- [TMLR Beyond PDF submission instructions](https://tmlr-beyond-pdf.org/submission-instructions)
- [TMLR Beyond PDF submission process](https://tmlr-beyond-pdf.org/submission-process)
- [Live example submission](https://tmlr-beyond-pdf.org/under_review/submission/)
- [Example interactive bundle — physics.html](https://tmlr-beyond-pdf.org/assets/html/submission/physics.html)
- [Real under-review Beyond PDF paper](https://tmlr-beyond-pdf.org/under_review/z4PfNDNAcN/)
- [distillpub/template](https://github.com/distillpub/template)
- [distillpub/template — components registration](https://raw.githubusercontent.com/distillpub/template/master/src/components.js)
- [distillpub/template — Rollup config](https://raw.githubusercontent.com/distillpub/template/master/rollup.config.common.js)
- [d-math.js source](https://raw.githubusercontent.com/distillpub/template/master/src/components/d-math.js)
- [d-figure.js source](https://raw.githubusercontent.com/distillpub/template/master/src/components/d-figure.js)
- [d-slider.js source](https://raw.githubusercontent.com/distillpub/template/master/src/components/d-slider.js)
- [styles-layout.css — named-column grid](https://raw.githubusercontent.com/distillpub/template/master/src/styles/styles-layout.css)
- [styles-base.css — system font stack](https://raw.githubusercontent.com/distillpub/template/master/src/styles/styles-base.css)
- [distillpub/post--example](https://github.com/distillpub/post--example)
- [distillpub/post--visual-exploration-gaussian-processes](https://github.com/distillpub/post--visual-exploration-gaussian-processes)
- [Distill homepage — 2021 hiatus notice](https://distill.pub/)
- [Svelte 5 docs — runes](https://svelte.dev/docs/svelte/what-are-runes)
- [MyST Markdown docs](https://mystmd.org/)
- [Curvenote docs](https://curvenote.com/docs)
