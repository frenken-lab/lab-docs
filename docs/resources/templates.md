<!-- last-reviewed: 2026-03-04 -->
# Templates

Starter templates for common lab projects, maintained in the [quarto-lab-templates](https://github.com/OSU-CAR-MSL/quarto-lab-templates) repository.

## Available Templates

| Template | What It Is | Directory | Full Guide |
|----------|-----------|-----------|------------|
| **Website** | Quarto academic site + Typst CV, deployed to GitHub Pages | `website/` | [Personal Website assignment](../assignments/personal-website.md) |
| **Resume** | Standalone Typst CV (no Quarto site needed) | `resume/` | [Typst CV Guide](../assignments/typst-cv-guide.md) |
| **Presentation** | Quarto RevealJS slide deck with defensive Mermaid settings | `presentation/` | [Presentations](presentations.md) |

## Quick Start

=== "Website"

    ```bash
    # Use as a GitHub template
    # Go to github.com/OSU-CAR-MSL/quarto-lab-templates
    # Click "Use this template" → create YOURUSERNAME.github.io
    # Then clone and work from the website/ directory

    cd website
    quarto preview
    ```

=== "Resume"

    ```bash
    # Copy resume/cv.typ into your project
    # Edit with VS Code + Tinymist extension
    typst compile cv.typ
    ```

=== "Presentation"

    ```bash
    # Copy the presentation/ directory into your project
    cd presentation
    quarto render slides.qmd
    # Open _output/slides.html in a browser
    ```

## Customization Tips

- **Colors:** Each template uses a color theme variable (`accent` in Typst, SCSS variables in presentations). Change these to match your branding.
- **Website deployment:** The included GitHub Actions workflow deploys automatically on push. Set your repo's Pages source to "GitHub Actions" in Settings.
- **Typst + Quarto integration:** The website template can auto-compile the Typst CV during site builds — see the [Typst CV Guide](../assignments/typst-cv-guide.md#integrating-with-quarto) for setup.
