<!-- last-reviewed: 2026-03-03 -->

# Student Site Showcase

Example personal academic websites built by lab members using the [Assignment 1](personal-website.md) template. Use these as inspiration for your own site.

------------------------------------------------------------------------

## Example Sites

| Name | Site | Notable Features |
|----------------|----------------|---------------------------------------|
| Robert Frenken | [robertfrenken.github.io](https://robertfrenken.github.io) | Typst PDF CV, `_brand.yml` theming, custom SCSS, research page |
| Drew Ralston | [dralston168.github.io](https://dralston168.github.io) | Clean blog layout, EDA posts |
| Chunyu Gu | [gugu-12.github.io](https://gugu-12.github.io) | Blog posts with visualizations |

!!! tip "Add your site" Once your personal site is live, let the lab know and we'll add it to this showcase.

------------------------------------------------------------------------

## Beyond the Template

After completing Assignment 1 with the basic template, here are ways to level up your site:

### Typst PDF CV

Replace the default Markdown `cv.qmd` with a professionally typeset PDF generated from Typst. Typst compiles in milliseconds (vs LaTeX's seconds), has readable syntax, and full LSP support in VS Code via the Tinymist extension.

See the [Typst CV Guide](typst-cv-guide.md) for a step-by-step walkthrough.

### Brand Configuration (`_brand.yml`)

Quarto's `_brand.yml` centralizes your site's visual identity — colors, fonts, and logos — in one file:

``` yaml
# _brand.yml
color:
  primary: "#bb0000"
  link: "#333333"
typography:
  base:
    family: "Source Sans Pro"
  headings:
    family: "Source Serif Pro"
```

Reference it in `_quarto.yml`:

``` yaml
brand: _brand.yml
```

### Custom SCSS

For deeper styling control, add a custom SCSS file:

``` yaml
# _quarto.yml
format:
  html:
    theme:
      - litera          # Base Bootswatch theme
      - custom.scss     # Your overrides
```

``` scss
// custom.scss
$link-color: #bb0000;

.navbar {
  border-bottom: 2px solid $link-color;
}
```

### CI Pre-Render Hooks

Automate build steps (like compiling a Typst CV) so they run every time your site builds — locally and in GitHub Actions:

``` yaml
# _quarto.yml
project:
  pre-render:
    - typst compile cv.typ My_CV.pdf
```

------------------------------------------------------------------------

## Related

-   [Assignment 1: Personal Website](personal-website.md) — The base assignment
-   [Typst CV Guide](typst-cv-guide.md) — Detailed walkthrough for Typst CV integration
