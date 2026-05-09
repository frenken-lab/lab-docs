"""MkDocs hook: export the page cross-link graph as JSON for the interactive
concept-map widget on resources/concept-map.md.

Runs at build time (on_pre_build). Scans all docs/*.md, extracts Markdown links
to other .md files, and writes nodes + edges to docs/assets/concept-graph.json.
The assets file is then picked up by the copy-assets step of the build.

Only lab docs are included. Cross-section links are preserved. External URLs
and anchor-only links are ignored.
"""

from __future__ import annotations

import json
import posixpath
import re
from pathlib import Path

DOCS_DIR = Path(__file__).parent.parent / "docs"
OUTPUT_PATH = DOCS_DIR / "assets" / "concept-graph.json"

LINK_RE = re.compile(r"\[([^\]]+)\]\((\.\./[^\)]+\.md[^\)]*|[^\)]+\.md[^\)]*)\)")
TITLE_RE = re.compile(r"^#\s+(.+?)\s*$", re.MULTILINE)

# Section → color (matches the classDef palette in the old Mermaid diagram).
SECTION_COLORS = {
    "getting-started": "#3b82f6",
    "osc-basics": "#d97706",
    "working-on-osc": "#d97706",
    "ml-workflows": "#7c3aed",
    "github": "#059669",
    "contributing": "#059669",
    "assignments": "#bb0000",
    "resources": "#64748b",
}
DEFAULT_COLOR = "#64748b"


def _page_title(text: str, fallback: str) -> str:
    m = TITLE_RE.search(text)
    return m.group(1).strip() if m else fallback


def _section_of(page_path: str) -> str:
    parts = page_path.split("/")
    return parts[0] if len(parts) > 1 else "root"


def _build_graph() -> dict:
    pages: dict[str, str] = {}
    for md_file in sorted(DOCS_DIR.rglob("*.md")):
        if "includes" in md_file.parts:
            continue
        rel = md_file.relative_to(DOCS_DIR).as_posix()
        pages[rel] = md_file.read_text(encoding="utf-8")

    nodes = []
    for rel, text in pages.items():
        section = _section_of(rel)
        nodes.append(
            {
                "data": {
                    "id": rel,
                    "label": _page_title(text, rel),
                    "section": section,
                    "color": SECTION_COLORS.get(section, DEFAULT_COLOR),
                    "url": "/" + rel.replace(".md", "/"),
                }
            }
        )

    edges = []
    seen: set[tuple[str, str]] = set()
    for src, text in pages.items():
        src_dir = str(Path(src).parent)
        for _, href in LINK_RE.findall(text):
            href = href.split("#")[0].split("?")[0]
            if not href.endswith(".md"):
                continue
            target = posixpath.normpath(posixpath.join(src_dir, href))
            if target not in pages or target == src:
                continue
            key = (src, target)
            if key in seen:
                continue
            seen.add(key)
            edges.append({"data": {"source": src, "target": target}})

    return {"nodes": nodes, "edges": edges}


def on_pre_build(config, **kwargs):
    """MkDocs lifecycle hook."""
    graph = _build_graph()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(graph, indent=2), encoding="utf-8")


if __name__ == "__main__":
    graph = _build_graph()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(graph, indent=2), encoding="utf-8")
    print(f"Wrote {len(graph['nodes'])} nodes, {len(graph['edges'])} edges to {OUTPUT_PATH}")
