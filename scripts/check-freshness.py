#!/usr/bin/env python3
"""Check docs pages for stale last-reviewed dates.

Scans all docs/**/*.md files for a <!-- last-reviewed: YYYY-MM-DD --> comment
in the first 10 lines (to support YAML front matter before the comment)
and flags pages older than the threshold.
"""

import argparse
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path

REVIEW_RE = re.compile(r"<!--\s*last-reviewed:\s*(\d{4}-\d{2}-\d{2})\s*-->")

# Files that are included via snippets, not standalone pages
EXCLUDE_PATTERNS = {"includes/"}


def main() -> None:
    parser = argparse.ArgumentParser(description="Check content freshness")
    parser.add_argument(
        "--max-age-days", type=int, default=365, help="Flag pages older than N days"
    )
    parser.add_argument("--docs-dir", type=str, default="docs", help="Docs directory")
    args = parser.parse_args()

    threshold = datetime.now() - timedelta(days=args.max_age_days)
    docs = Path(args.docs_dir)
    stale: list[tuple[str, str]] = []
    missing: list[str] = []

    for md in sorted(docs.rglob("*.md")):
        rel = str(md.relative_to(docs))
        if any(rel.startswith(pat) for pat in EXCLUDE_PATTERNS):
            continue

        text = md.read_text(encoding="utf-8")
        # Search first 10 lines for the review comment
        head = "\n".join(text.split("\n", 10)[:10])
        match = REVIEW_RE.search(head)
        if not match:
            missing.append(str(md))
            continue
        reviewed = datetime.strptime(match.group(1), "%Y-%m-%d")
        if reviewed < threshold:
            stale.append((str(md), match.group(1)))

    if missing:
        print(f"\n⚠ {len(missing)} page(s) missing last-reviewed comment:")
        for p in missing:
            print(f"  {p}")

    if stale:
        print(f"\n⚠ {len(stale)} page(s) older than {args.max_age_days} days:")
        for p, d in stale:
            print(f"  {p}  (last reviewed {d})")

    if not missing and not stale:
        print(f"✓ All pages reviewed within {args.max_age_days} days.")

    if stale:
        sys.exit(1)


if __name__ == "__main__":
    main()
