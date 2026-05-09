# OSC Overview Presentation

Quarto RevealJS presentation for MSL lab onboarding. ~24 slides covering OSC clusters, SSH, SLURM, environments, and GPU workflows.

## Build

```bash
cd ~/lab-setup-guide/presentations/osc-overview
quarto render index.qmd
# Output: _output/index.html
```

## Content Sources

All slide content comes from the lab-setup-guide docs (../docs/). When updating slides, verify against the source docs — do not fabricate specs, quotas, or commands.

> Quarto RevealJS conventions: See `~/.claude/rules/quarto-presentations.md`
