#!/usr/bin/env python3
"""Advisory check for SSOT duplication.

Scans docs for known canonical patterns that should only appear in prose
on their canonical page. Findings are advisory, not blocking.
"""

import re
import sys
from pathlib import Path

# (pattern, canonical page relative to docs/)
CANONICAL_PATTERNS: list[tuple[str, str]] = [
    (r"python -m venv", "working-on-osc/osc-environment-management.md"),
    (r"pip install torch", "ml-workflows/pytorch-setup.md"),
    (r"conda create", "working-on-osc/osc-environment-management.md"),
    (r"conda activate", "working-on-osc/osc-environment-management.md"),
    (r"module load cuda", "ml-workflows/pytorch-setup.md"),
    (r"ssh-keygen", "osc-basics/osc-ssh-connection.md"),
    (r"scp .+ osc\.edu", "osc-basics/osc-file-transfer.md"),
    (r"rsync .+ osc\.edu", "osc-basics/osc-file-transfer.md"),
    (r"mlflow\.", "ml-workflows/data-experiment-tracking.md"),
    (r"wandb\.", "ml-workflows/data-experiment-tracking.md"),
]

DOCS = Path("docs")


def in_code_block(lines: list[str], line_idx: int) -> bool:
    """Return True if the line is inside a fenced code block."""
    fence_count = 0
    for i in range(line_idx):
        stripped = lines[i].lstrip()
        if stripped.startswith("```"):
            fence_count += 1
    return fence_count % 2 == 1


def main() -> None:
    findings: list[tuple[str, int, str, str]] = []

    for md in sorted(DOCS.rglob("*.md")):
        rel = str(md.relative_to(DOCS))
        text = md.read_text(encoding="utf-8")
        lines = text.split("\n")

        for pattern, canonical in CANONICAL_PATTERNS:
            if rel == canonical:
                continue
            for i, line in enumerate(lines):
                if re.search(pattern, line) and not in_code_block(lines, i):
                    findings.append((rel, i + 1, pattern, canonical))

    if findings:
        print(f"⚠ {len(findings)} potential SSOT duplication(s) found:\n")
        for page, lineno, pattern, canonical in findings:
            print(f"  {page}:{lineno}")
            print(f"    pattern: {pattern}")
            print(f"    canonical page: {canonical}\n")
    else:
        print("✓ No SSOT duplication detected.")

    # Advisory only — always exit 0
    sys.exit(0)


if __name__ == "__main__":
    main()
