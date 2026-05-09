<!-- last-reviewed: 2026-03-03 -->
# Typst CV Guide

Upgrade your personal website's CV from a Markdown page to a professionally typeset PDF using [Typst](https://typst.app/) — a modern alternative to LaTeX with fast compilation, readable syntax, and full editor support.

---

## Why Typst?

| | Markdown Tables | LaTeX | Typst |
|---|---|---|---|
| **Output quality** | Basic HTML tables | Publication-grade PDF | Publication-grade PDF |
| **Compile speed** | Instant (HTML) | 2-10 seconds | < 0.5 seconds |
| **Syntax readability** | Very readable | Verbose, bracket-heavy | Clean, readable |
| **Editor support** | Standard | Varies | Full LSP via Tinymist |
| **Learning curve** | None | Steep | Gentle |

Typst gives you LaTeX-quality PDFs with a syntax that's nearly as readable as Markdown. For a CV — which benefits from precise layout control — it's the best of both worlds.

---

## Installing Typst

=== "Local (macOS/Linux/WSL)"

    ```bash
    # Via cargo (if you have Rust installed)
    cargo install typst-cli

    # Or download the binary directly
    # See https://github.com/typst/typst/releases for the latest release
    curl -fsSL https://github.com/typst/typst/releases/latest/download/typst-x86_64-unknown-linux-musl.tar.xz \
      | tar -xJ --strip-components=1 -C ~/.local/bin/
    ```

=== "OSC"

    ```bash
    # Download to ~/.local/bin/ (already in PATH)
    curl -fsSL https://github.com/typst/typst/releases/latest/download/typst-x86_64-unknown-linux-musl.tar.xz \
      | tar -xJ --strip-components=1 -C ~/.local/bin/

    # Verify
    typst --version
    ```

=== "VS Code Extension"

    Install the **Tinymist** extension for Typst support:

    1. Open VS Code
    2. Extensions (++ctrl+shift+x++) → Search "Tinymist"
    3. Install `myriad-dreamin.tinymist`

    Tinymist provides syntax highlighting, autocomplete, live preview, and error diagnostics.

---

## CV Template Walkthrough

Here's a starter `cv.typ` template. The key building blocks are page setup, a color theme, and two helper functions.

### Page Setup

```typ
// Page setup
#set page(margin: (x: 0.5in, y: 0.5in), paper: "us-letter")
#set text(size: 10.5pt)
#set par(justify: true)

// Color theme — change this to match your site's branding
#let accent = rgb("#bb0000")
#let link-color = rgb("#333333")

// Make all links use link-color
#show link: set text(fill: link-color)
```

### Header

```typ
#align(center)[
  #text(size: 20pt, weight: "bold")[Your Name] \
  #v(2pt)
  #text(size: 10pt)[
    ✉ #link("mailto:you@university.edu")[you\@university.edu]
    · 📍 City, State
    · 🌐 #link("https://yourusername.github.io")[yourusername.github.io]
  ]
  #text(size: 10pt)[
    💻 #link("https://github.com/yourusername")[GitHub]
    · 💼 #link("https://linkedin.com/in/yourname")[LinkedIn]
  ]
]
```

!!! note "Escape `@` in Typst"
    The `@` symbol is used for label references in Typst. In text, escape it as `\@` (e.g., `you\@university.edu`).

### Helper Functions

Two reusable functions handle the repetitive layout patterns in a CV:

```typ
// Section heading with colored rule
#let section(title) = {
  v(4pt)
  text(size: 12pt, weight: "bold", fill: accent)[#upper(title)]
  v(-3pt)
  line(length: 100%, stroke: 0.5pt + accent)
  v(2pt)
}

// Entry with title on left, date on right
#let entry(title, org, date) = {
  grid(
    columns: (1fr, auto),
    column-gutter: 8pt,
    text(weight: "bold", size: 10.5pt)[#title],
    text(style: "italic", size: 10pt)[#date],
  )
  if org != none {
    text(style: "italic", size: 10pt)[#org]
  }
  v(1pt)
}
```

### Content Sections

Use the helpers to build your CV content:

```typ
#section("Education")

#entry("Ph.D. in Computer Science", "Your University", "2022 – Present")
#entry("B.S. in Computer Science", "Your University", "2018 – 2022")

#section("Experience")

#entry("Graduate Research Assistant", "Your Lab", "2022 – Present")
#list(
  indent: 8pt,
  body-indent: 3pt,
  [Developed a graph neural network for anomaly detection.],
  [Published results at a top-tier venue.],
)

#entry("Software Engineering Intern", "Company | City, ST", "Summer 2021")
#list(
  indent: 8pt,
  body-indent: 3pt,
  [Built data pipeline processing 1M+ records daily.],
)

#section("Skills")

#grid(
  columns: (auto, 1fr),
  column-gutter: 10pt,
  row-gutter: 3pt,
  text(weight: "bold", size: 10pt)[ML/DL:],
  [PyTorch, scikit-learn, Weights & Biases],
  text(weight: "bold", size: 10pt)[Languages:],
  [Python, Java, SQL],
)
```

---

## Full Starter Template

Here's the complete `cv.typ` file — copy this into your project and customize:

```typ
// Page setup
#set page(margin: (x: 0.5in, y: 0.5in), paper: "us-letter")
#set text(size: 10.5pt)
#set par(justify: true)

// Color theme
#let accent = rgb("#bb0000")
#let link-color = rgb("#333333")
#show link: set text(fill: link-color)

// --- Header ---
#align(center)[
  #text(size: 20pt, weight: "bold")[Your Name] \
  #v(2pt)
  #text(size: 10pt)[
    ✉ #link("mailto:you@university.edu")[you\@university.edu]
    · 📍 City, State
    · 🌐 #link("https://yourusername.github.io")[yourusername.github.io]
  ]
]
#v(4pt)

// --- Helpers ---
#let section(title) = {
  v(4pt)
  text(size: 12pt, weight: "bold", fill: accent)[#upper(title)]
  v(-3pt)
  line(length: 100%, stroke: 0.5pt + accent)
  v(2pt)
}

#let entry(title, org, date) = {
  grid(
    columns: (1fr, auto),
    column-gutter: 8pt,
    text(weight: "bold", size: 10.5pt)[#title],
    text(style: "italic", size: 10pt)[#date],
  )
  if org != none {
    text(style: "italic", size: 10pt)[#org]
  }
  v(1pt)
}

// --- Content ---
#section("Education")
#entry("Ph.D. in Your Field", "Your University", "2022 – Present")
#entry("B.S. in Your Field", "Your University", "2018 – 2022")

#section("Experience")
#entry("Graduate Research Assistant", "Your Lab · Your University", "2022 – Present")
#list(
  indent: 8pt,
  body-indent: 3pt,
  [Description of your research work.],
  [Another accomplishment or responsibility.],
)

#section("Publications")
#list(
  indent: 8pt,
  body-indent: 3pt,
  [*Your Name*, Co-Author (2025) "Paper Title" _Conference/Journal_.],
)

#section("Skills")
#grid(
  columns: (auto, 1fr),
  column-gutter: 10pt,
  row-gutter: 3pt,
  text(weight: "bold", size: 10pt)[ML/DL:],
  [PyTorch, scikit-learn, Weights & Biases],
  text(weight: "bold", size: 10pt)[Languages:],
  [Python, Java, SQL, MATLAB],
  text(weight: "bold", size: 10pt)[Tools:],
  [Git, Linux, SLURM, Docker],
)
```

---

## Integrating with Quarto

### Pre-Render Hook

Add a `pre-render` step to `_quarto.yml` so the CV compiles automatically whenever you build your site:

```yaml
# _quarto.yml
project:
  type: website
  output-dir: _site
  resources:
    - "*.pdf"
  pre-render:
    - typst compile cv.typ Your_Name_CV.pdf
```

The `resources: ["*.pdf"]` line tells Quarto to copy the PDF to `_site/`.

### Navbar Link

Update the navbar to link to the PDF instead of the Markdown CV page:

```yaml
# _quarto.yml
website:
  navbar:
    left:
      - text: CV
        href: Your_Name_CV.pdf
```

### GitHub Actions

If your site deploys via GitHub Actions, install Typst in the workflow:

```yaml
- name: Install Typst
  run: |
    curl -fsSL https://github.com/typst/typst/releases/latest/download/typst-x86_64-unknown-linux-musl.tar.xz \
      | sudo tar -xJ --strip-components=1 -C /usr/local/bin/
```

Place this step before `quarto render`. The pre-render hook handles compilation automatically.

!!! tip "Keep cv.qmd as a fallback"
    You don't need to delete `cv.qmd` — keep it as a web-viewable version of your CV. The Typst PDF is for downloading and printing. Remove `cv.qmd` from the navbar if you link to the PDF instead.

---

## Editing Workflow

1. **Edit** `cv.typ` in VS Code with the Tinymist extension
2. **Preview** using Tinymist's live preview (++ctrl+shift+p++ → "Tinymist: Show PDF")
3. **Compile** manually: `typst compile cv.typ Your_Name_CV.pdf`
4. **Build site** with `quarto render` — pre-render hook compiles automatically
5. **Push** — GitHub Actions deploys the updated site with the new PDF

---

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| `typst: command not found` | Typst not installed or not in PATH | Install to `~/.local/bin/` (see above) |
| `@` renders as label reference | `@` is special in Typst | Escape as `\@` |
| PDF not in `_site/` after build | Missing `resources` config | Add `resources: ["*.pdf"]` to `_quarto.yml` |
| Tinymist not showing preview | Extension not installed | Install `myriad-dreamin.tinymist` in VS Code |
| Pre-render fails in CI | Typst not installed in Actions | Add the Typst install step to your workflow |

---

## Related

- [Assignment 1: Personal Website](personal-website.md) — The base Quarto site assignment
- [Student Site Showcase](site-showcase.md) — Examples of completed sites with Typst CVs
- [Standalone resume template](https://github.com/OSU-CAR-MSL/quarto-lab-templates/tree/main/resume) — If you just want a Typst CV without a Quarto website, use the `resume/` template
