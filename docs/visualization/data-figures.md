---
status: new
tags:
  - Visualization
  - matplotlib
  - altair
  - Paper Writing
---
<!-- last-reviewed: 2026-04-24 -->
# Data-Driven Figures

!!! abstract "For training curves, attention heatmaps, ablations, and anything that's a function of experimental data"
    The expert-practice stack in 2026 is **matplotlib + [`tueplots`](https://github.com/pnkraemer/tueplots)** for paper PDFs (venue-calibrated defaults, Computer-Modern-matching fonts), with **altair/Vega-Lite** as an escape hatch when you want the same figure to render interactively in TMLR Beyond PDF.

    Everything ties together through a **shared palette file** (4–6 named colors) imported into the matplotlib style, the Svelte interactive components, and — if you use it — your Figma library. This is the single most copyable practice from Grootendorst's "Visual Guide" series.

---

## Three contexts, three pipelines

| Context | Pipeline | Output |
|---|---|---|
| **Paper static PDF** | matplotlib + `tueplots` + shared palette | `.pdf` via `savefig(..., format='pdf')`, vector, fonts match LaTeX |
| **Paper interactive (TMLR Beyond PDF)** | altair / Vega-Lite with shared palette | `.html` via `chart.save(...)`, interactive tooltips, also renders to static PNG if needed |
| **Talk slide (Slidev)** | Whichever of the above you already have; `.png` at 2× is fine for slides | PNG dropped into `decks/<slug>/public/images/` |

Rule of thumb: **write the figure script once, export to multiple formats**. The deep mistake is authoring the same figure three times in three tools.

---

## matplotlib + `tueplots` for paper PDFs

[`tueplots`](https://github.com/pnkraemer/tueplots) is a small library of `rcParams` presets calibrated for specific venues (ICML, NeurIPS, JMLR/TMLR, TMLR Beyond PDF, AISTATS, JASA). Drop-in at the top of every figure script:

```python
# figures/training_curve.py
import matplotlib.pyplot as plt
from tueplots import bundles, cycler
from tueplots.constants.color import palettes

# Calibrated for JMLR/TMLR column width, font, margin
plt.rcParams.update(bundles.jmlr2001())

# Use the lab's shared palette
plt.rcParams.update(cycler.cycler(color=palettes.tue_plot))  # or your own

import pandas as pd
df = pd.read_parquet('runs/kd_gat.parquet')

fig, ax = plt.subplots()
ax.plot(df.step, df.student_loss, label='Student')
ax.plot(df.step, df.teacher_loss, label='Teacher', linestyle='--')
ax.plot(df.step, df.kd_loss,      label='KD')
ax.set_xlabel('Training step')
ax.set_ylabel('Loss')
ax.legend()
fig.savefig('figures/training_curve.pdf', bbox_inches='tight')
fig.savefig('figures/training_curve.png', dpi=300, bbox_inches='tight')
```

What `bundles.jmlr2001()` sets for you:

- Serif font matching the paper's body text (Computer Modern / TeX Gyre)
- Figure width = TMLR column width (in inches)
- Appropriate `font.size`, `axes.titlesize`, `axes.labelsize`
- Thin spines, no top/right axis, consistent tick marks
- Palettes tuned for print (colorblind-safe by default)

!!! tip "Pin the venue before you start plotting"
    Every venue has different column widths and font sizes. Picking the wrong bundle means your fonts will be 10 pt in the paper instead of 8 pt and the figure will visually clash with the body. If the venue isn't in `tueplots.bundles`, check the venue template's `\textwidth` in inches and write your own one-liner.

### Shared `mplstyle` file (alternative / supplement)

If `tueplots` doesn't cover your venue, roll your own:

```ini
# paper/figures/paper.mplstyle
# Load with: plt.style.use('paper/figures/paper.mplstyle')

font.family:       serif
font.serif:        Computer Modern Roman
font.size:         9

axes.labelsize:    9
axes.titlesize:    10
axes.spines.top:   False
axes.spines.right: False

xtick.labelsize:   8
ytick.labelsize:   8

legend.fontsize:   8
legend.frameon:    False

figure.figsize:    5.5, 3.4      ; TMLR single-column width, golden ratio
figure.dpi:        150
savefig.dpi:       300
savefig.bbox:      tight

lines.linewidth:   1.5

axes.prop_cycle:   cycler('color', ['c8102e', '4f46e5', '0e7490', 'd97706', '059669'])
```

Commit the `.mplstyle` in the paper repo. Load once per figure script:

```python
plt.style.use('paper/figures/paper.mplstyle')
```

---

## `altair` / Vega-Lite for dual static + interactive {#altair-vega-lite}

This is **Sasha Rush's pattern in [*The Annotated Transformer*](https://nlp.seas.harvard.edu/annotated-transformer/)** — see [`the_annotated_transformer.py:473`](https://raw.githubusercontent.com/harvardnlp/annotated-transformer/master/the_annotated_transformer.py) for the subsequent-mask heatmap and `:1974` for the attention-head heatmaps.

Altair emits Vega-Lite JSON. The same JSON spec renders:

- **Statically** to PNG/PDF/SVG via `chart.save('fig.png')` (requires `vl-convert-python`)
- **Interactively** as HTML with hover tooltips via `chart.save('fig.html')` — embeds directly in TMLR Beyond PDF

### Example: attention heatmap

```python
# figures/attention_weights.py
import altair as alt
import pandas as pd
import torch

# Load attention weights from a forward pass
model = load_trained_model('checkpoints/kd_gat_best.pt')
attn = model.get_attention(sample_batch)  # (num_heads, seq_len, seq_len)

# Reshape to long form for Vega-Lite
records = []
for head in range(attn.shape[0]):
    for i in range(attn.shape[1]):
        for j in range(attn.shape[2]):
            records.append({
                'head': head, 'query': i, 'key': j,
                'weight': attn[head, i, j].item(),
            })
df = pd.DataFrame(records)

chart = (
    alt.Chart(df).mark_rect().encode(
        x=alt.X('key:O', title='Key position'),
        y=alt.Y('query:O', title='Query position'),
        color=alt.Color('weight:Q', scale=alt.Scale(scheme='viridis')),
        tooltip=['head', 'query', 'key', 'weight'],
    )
    .properties(width=200, height=200)
    .facet(column='head:O')
)

chart.save('figures/attention_weights.html')    # interactive (Beyond PDF)
chart.save('figures/attention_weights.png')     # static (PDF paper)
chart.save('figures/attention_weights.pdf')     # static vector
```

Both outputs come from one script, one spec. No duplicate authoring.

### When to reach for altair vs matplotlib

| Situation | matplotlib + tueplots | altair |
|---|---|---|
| Training curves, loss landscapes, ablation bars | :material-check: Default — pandas plays nicely, full control | |
| Attention heatmaps, correlation matrices, confusion matrices | Works, but hover tooltips absent | :material-check: Interactive value-on-hover is a genuine upgrade |
| TMLR Beyond PDF submission | PNG only | :material-check: Same spec → interactive HTML + static PDF |
| Heavy custom styling (multiple y-axes, inset zoom, broken axes) | :material-check: Full control | Awkward |
| Reviewer asks for log-scale replot | One-line `set_yscale('log')` | Rebuild spec |

**Default to matplotlib. Reach for altair when the interactive version genuinely adds something.**

---

## Shared palette file

This is the single most important practice in this page. Define colors once, import them everywhere.

```python
# paper/figures/palette.py
"""
Semantic colors for the KD-GAT paper and associated talks.

One hue per concept, held constant across every figure,
architecture diagram, slide deck, and interactive demo.
"""

STUDENT   = '#c8102e'   # OSU scarlet — primary method
TEACHER   = '#6b7280'   # neutral gray — reference / baseline
GAT_ATTN  = '#4f46e5'   # indigo — learned attention
CAN_BUS   = '#0e7490'   # teal — data modality
BASELINE  = '#d97706'   # amber — published baseline
BEST      = '#059669'   # green — our result highlights


PALETTE_HEX = {
    'STUDENT':  STUDENT,
    'TEACHER':  TEACHER,
    'GAT_ATTN': GAT_ATTN,
    'CAN_BUS':  CAN_BUS,
    'BASELINE': BASELINE,
    'BEST':     BEST,
}

# For matplotlib cycler
CYCLE = [STUDENT, GAT_ATTN, TEACHER, BASELINE, CAN_BUS, BEST]
```

```python
# In every matplotlib script
from figures.palette import STUDENT, TEACHER, GAT_ATTN

ax.plot(df.step, df.student_loss, color=STUDENT, label='Student')
ax.plot(df.step, df.teacher_loss, color=TEACHER, label='Teacher')
```

```python
# In every altair script
from figures.palette import PALETTE_HEX

color_scale = alt.Scale(
    domain=list(PALETTE_HEX.keys()),
    range=list(PALETTE_HEX.values()),
)
```

For the Svelte interactive components, mirror the palette in JSON:

```json
// kd-gat-paper/interactive/src/lib/palette.json
{
  "STUDENT":  "#c8102e",
  "TEACHER":  "#6b7280",
  "GAT_ATTN": "#4f46e5",
  "CAN_BUS":  "#0e7490",
  "BASELINE": "#d97706",
  "BEST":     "#059669"
}
```

```svelte
<script>
  import palette from '$lib/palette.json';
  // ...
  <rect fill={palette.STUDENT} ... />
</script>
```

**Result:** the training curve's "student loss" line is the same scarlet as the student box in Figure 1, which is the same scarlet as the student node in the Slidev talk's Svelte Flow demo. That visual coherence is what makes a paper read as one artifact — and it's what [Grootendorst's per-post color ontology](communicators.md#maarten-grootendorst) is actually doing under the hood.

---

## Project layout for figures

Recommended directory structure for a lab paper repo:

```
kd-gat-paper/
├── paper/
│   ├── submission.md                  # MyST / TMLR Beyond PDF source
│   └── figures/
│       ├── palette.py                 # ← shared across all figures
│       ├── paper.mplstyle             # matplotlib style (if not using tueplots)
│       ├── training_curve.py          # generates training_curve.{pdf,png}
│       ├── attention_weights.py       # generates attention_weights.{html,png,pdf}
│       ├── architecture.svg           # exported from interactive/ (static)
│       └── data/                      # canonical CSV/Parquet for figures
│           ├── runs_summary.parquet
│           └── attention_weights.pt
├── interactive/                       # Svelte 5 + Vite workspace
│   └── src/
│       ├── lib/palette.json           # ← mirror of paper/figures/palette.py
│       └── figures/
│           └── architecture/
│               └── App.svelte         # hand-SVG architecture figure
└── Makefile                           # `make figures` regenerates everything
```

Each figure script:

1. Reads data from `paper/figures/data/` (committed Parquet or CSV; deterministic).
2. Imports colors from `palette.py`.
3. Emits vector PDF + PNG fallback + (optional) interactive HTML.

A `Makefile` target keeps the regeneration reproducible:

```makefile
# Makefile
FIGURES := $(wildcard paper/figures/*.py)
PDFS := $(patsubst %.py,%.pdf,$(FIGURES))

figures: $(PDFS)

paper/figures/%.pdf: paper/figures/%.py paper/figures/palette.py
	python $<

clean-figures:
	rm -f paper/figures/*.pdf paper/figures/*.png paper/figures/*.html
```

Now `make figures` regenerates every figure from the committed data; reviewers can reproduce plots exactly.

---

## Anti-patterns to avoid

!!! danger "Do not do these"
    1. **Exporting a `pd.DataFrame.plot()` to PNG and treating it as the paper figure.** The defaults look like Jupyter notebooks, not paper figures. Always apply a style.
    2. **Hand-tuning each figure's colors separately.** Drift is guaranteed — figure 3 will be blue-ish while figure 5 is blue-er. Use `palette.py`.
    3. **Re-authoring the same figure in a different tool for the talk.** Reuse the paper figure or reuse the data + swap the style. Never re-author from scratch.
    4. **Putting figure-generation code inside notebooks that also train models.** Figure scripts should be pure: read data, plot, save. See [Notebook-to-Script Workflow](../ml-workflows/ml-workflow.md#notebook-to-script-workflow).
    5. **Using matplotlib's default palette in a TMLR paper.** The default cycle (`tab:blue`, `tab:orange`, etc.) is colorblind-unsafe for certain pairs and has strong "intro ML course" associations. Override with your palette.
    6. **Embedding raw data in the figure script.** Hardcoded numbers break reproducibility. Read from a committed Parquet/CSV in `data/`.

---

## `tueplots` bundles reference

At time of writing, [`tueplots.bundles`](https://github.com/pnkraemer/tueplots/blob/main/tueplots/bundles.py) ships:

- `aaai2022`, `aistats2022`, `aistats2023`
- `beamer_moml`, `beamer_moml_wide`
- `icml2022`, `icml2022_half`
- `iclr2023`, `iclr2024`
- `jmlr2001` (useful for TMLR — same publisher)
- `neurips2021`, `neurips2022`, `neurips2023`, `neurips2024`
- `tmlr2023`

Verify against your target venue's LaTeX template (column width in `\textwidth`, font size in `\documentclass[...]`) before submitting.

---

## Sources

- [tueplots on GitHub](https://github.com/pnkraemer/tueplots)
- [Altair documentation](https://altair-viz.github.io/)
- [Vega-Lite documentation](https://vega.github.io/vega-lite/)
- [The Annotated Transformer source — altair calls](https://raw.githubusercontent.com/harvardnlp/annotated-transformer/master/the_annotated_transformer.py)
- [vl-convert-python — altair's static-export backend](https://github.com/vega/vl-convert)
- [matplotlib rcParams reference](https://matplotlib.org/stable/users/explain/customizing.html)
- [matplotlib colorblind-safe palette guidance](https://matplotlib.org/stable/users/explain/colors/colormaps.html)
