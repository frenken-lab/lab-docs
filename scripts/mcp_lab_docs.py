#!/usr/bin/env python3
"""MCP server exposing lab-setup-guide documentation as queryable tools.

v2: Section-level chunking, BM25 ranked search, 7 tools, cross-link awareness.

Run with:
    uv run --with "mcp[cli]" --with pyyaml --with rank-bm25 scripts/mcp_lab_docs.py
"""

from __future__ import annotations

import posixpath
import re
import sys
from pathlib import Path

import yaml
from mcp.server.fastmcp import FastMCP
from rank_bm25 import BM25Okapi

REPO_ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = REPO_ROOT / "docs"
MKDOCS_YML = REPO_ROOT / "mkdocs.yml"

# Approximate token limit for a single chunk before sub-splitting at H3
MAX_CHUNK_WORDS = 1500

mcp = FastMCP(name="lab-setup-docs")


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------


class Chunk:
    """A section of documentation content."""

    __slots__ = (
        "page_path",
        "heading",
        "parent_heading",
        "content",
        "word_count",
        "category",
        "level",
    )

    def __init__(
        self,
        page_path: str,
        heading: str,
        content: str,
        *,
        parent_heading: str = "",
        category: str = "",
        level: int = 2,
    ) -> None:
        self.page_path = page_path
        self.heading = heading
        self.parent_heading = parent_heading
        self.content = content
        self.word_count = len(content.split())
        self.category = category
        self.level = level


# ---------------------------------------------------------------------------
# Chunking engine
# ---------------------------------------------------------------------------

_H2_RE = re.compile(r"^## (.+)$", re.MULTILINE)
_H3_RE = re.compile(r"^### (.+)$", re.MULTILINE)
_FENCE_RE = re.compile(r"^```", re.MULTILINE)


def _split_respecting_fences(text: str, pattern: re.Pattern) -> list[tuple[str, str]]:
    """Split text at heading boundaries, never inside fenced code blocks.

    Returns list of (heading, body) tuples. First item may have empty heading
    if text starts before first heading match.
    """
    # Find all heading positions and fence positions
    headings = [(m.start(), m.end(), m.group(1)) for m in pattern.finditer(text)]
    if not headings:
        return [("", text)]

    # Find fenced code block ranges
    fences = [m.start() for m in _FENCE_RE.finditer(text)]
    fence_ranges: list[tuple[int, int]] = []
    i = 0
    while i < len(fences) - 1:
        fence_ranges.append((fences[i], fences[i + 1]))
        i += 2

    def in_fence(pos: int) -> bool:
        return any(start <= pos <= end for start, end in fence_ranges)

    # Filter out headings inside fences
    valid = [(s, e, h) for s, e, h in headings if not in_fence(s)]
    if not valid:
        return [("", text)]

    parts: list[tuple[str, str]] = []
    # Content before first heading
    if valid[0][0] > 0:
        parts.append(("", text[: valid[0][0]]))

    for idx, (start, end, heading) in enumerate(valid):
        next_start = valid[idx + 1][0] if idx + 1 < len(valid) else len(text)
        body = text[end:next_start].strip()
        parts.append((heading, body))

    return parts


def _chunk_page(page_path: str, text: str) -> list[Chunk]:
    """Split a markdown page into chunks at H2 boundaries, sub-splitting at H3."""
    category = page_path.split("/")[0] if "/" in page_path else ""
    h2_sections = _split_respecting_fences(text, _H2_RE)

    chunks: list[Chunk] = []
    for h2_heading, h2_body in h2_sections:
        if not h2_heading:
            # Page preamble (before first H2) — include as-is
            if h2_body.strip():
                # Extract title from H1 if present
                h1_match = re.match(r"^# (.+)$", h2_body, re.MULTILINE)
                title = h1_match.group(1) if h1_match else "(preamble)"
                chunks.append(
                    Chunk(
                        page_path,
                        title,
                        h2_body.strip(),
                        category=category,
                        level=1,
                    )
                )
            continue

        word_count = len(h2_body.split())
        if word_count <= MAX_CHUNK_WORDS:
            chunks.append(
                Chunk(
                    page_path,
                    h2_heading,
                    h2_body,
                    category=category,
                    level=2,
                )
            )
        else:
            # Sub-split at H3
            h3_sections = _split_respecting_fences(h2_body, _H3_RE)
            for h3_heading, h3_body in h3_sections:
                if not h3_heading:
                    # Content between H2 and first H3
                    if h3_body.strip():
                        chunks.append(
                            Chunk(
                                page_path,
                                h2_heading,
                                h3_body.strip(),
                                category=category,
                                level=2,
                            )
                        )
                else:
                    chunks.append(
                        Chunk(
                            page_path,
                            h3_heading,
                            h3_body,
                            parent_heading=h2_heading,
                            category=category,
                            level=3,
                        )
                    )

    return chunks


# ---------------------------------------------------------------------------
# Cross-link parser
# ---------------------------------------------------------------------------

_LINK_RE = re.compile(r"\[([^\]]+)\]\((\.\./[^\)]+\.md[^\)]*|[^\)]+\.md[^\)]*)\)")


def _parse_cross_links(pages: dict[str, str]) -> dict[str, set[str]]:
    """Build adjacency map: page_path → set of linked page_paths."""
    links: dict[str, set[str]] = {}
    for page_path, text in pages.items():
        targets: set[str] = set()
        page_dir = str(Path(page_path).parent)
        for _, href in _LINK_RE.findall(text):
            # Strip anchors and query strings
            href = href.split("#")[0].split("?")[0]
            if not href.endswith(".md"):
                continue
            # Resolve relative paths and normalize (e.g. ml-workflows/../osc/ → osc/)
            resolved = posixpath.normpath(posixpath.join(page_dir, href))
            targets.add(resolved)
        links[page_path] = targets
    return links


# ---------------------------------------------------------------------------
# YAML loader that ignores !!python/* tags (mkdocs.yml uses them for emoji)
# ---------------------------------------------------------------------------


class _MkDocsLoader(yaml.SafeLoader):
    pass


def _ignore_python_tags(loader: yaml.Loader, tag_suffix: str, node: yaml.Node) -> None:
    return None


_MkDocsLoader.add_multi_constructor("tag:yaml.org,2002:python/", _ignore_python_tags)


# ---------------------------------------------------------------------------
# Index singleton
# ---------------------------------------------------------------------------


class DocsIndex:
    """Lazily built index over all documentation chunks."""

    _instance: DocsIndex | None = None

    def __init__(self) -> None:
        self.chunks: list[Chunk] = []
        self.pages: dict[str, str] = {}  # page_path → full text
        self.cross_links: dict[str, set[str]] = {}
        self._bm25: BM25Okapi | None = None
        self._tokenized: list[list[str]] = []
        self._nav: list | None = None

    @classmethod
    def get(cls) -> DocsIndex:
        if cls._instance is None:
            cls._instance = cls()
            cls._instance._build()
        return cls._instance

    def _build(self) -> None:
        # Load all pages
        for md_file in sorted(DOCS_DIR.rglob("*.md")):
            if "includes" in md_file.parts:
                continue
            rel = str(md_file.relative_to(DOCS_DIR))
            text = md_file.read_text(encoding="utf-8")
            self.pages[rel] = text
            self.chunks.extend(_chunk_page(rel, text))

        # Build BM25 index
        self._tokenized = [_tokenize(c.content) for c in self.chunks]
        if self._tokenized:
            self._bm25 = BM25Okapi(self._tokenized)

        # Cross-links
        self.cross_links = _parse_cross_links(self.pages)

        # Nav tree — mkdocs.yml has !!python/name tags that SafeLoader rejects
        config = yaml.load(MKDOCS_YML.read_text(encoding="utf-8"), Loader=_MkDocsLoader)
        self._nav = config.get("nav", [])

        print(
            f"Indexed {len(self.pages)} pages, {len(self.chunks)} chunks",
            file=sys.stderr,
        )

    def search(
        self,
        query: str,
        section: str | None = None,
        limit: int = 5,
    ) -> list[tuple[Chunk, float]]:
        """BM25 ranked search over chunks."""
        if not self._bm25:
            return []
        tokens = _tokenize(query)
        if not tokens:
            return []
        scores = self._bm25.get_scores(tokens)

        results: list[tuple[Chunk, float]] = []
        for idx, score in enumerate(scores):
            if score <= 0:
                continue
            chunk = self.chunks[idx]
            if section and chunk.category != section:
                continue
            results.append((chunk, float(score)))

        results.sort(key=lambda x: x[1], reverse=True)
        return results[:limit]

    def get_section(self, page_path: str, heading: str) -> Chunk | None:
        """Find a specific section by page path and heading."""
        heading_lower = heading.lower().strip()
        for chunk in self.chunks:
            if chunk.page_path != page_path:
                continue
            if chunk.heading.lower().strip() == heading_lower:
                return chunk
        return None

    def get_page_chunks(self, page_path: str) -> list[Chunk]:
        """All chunks for a given page."""
        return [c for c in self.chunks if c.page_path == page_path]

    def get_related(self, page_path: str) -> dict[str, list[str]]:
        """Pages linked from/to this page + same-section siblings."""
        outgoing = self.cross_links.get(page_path, set())

        incoming: set[str] = set()
        for src, targets in self.cross_links.items():
            if page_path in targets and src != page_path:
                incoming.add(src)

        category = page_path.split("/")[0] if "/" in page_path else ""
        siblings = (
            [p for p in self.pages if p != page_path and p.startswith(category + "/")]
            if category
            else []
        )

        return {
            "links_to": sorted(outgoing),
            "linked_from": sorted(incoming),
            "same_section": sorted(siblings),
        }

    def find_troubleshooting(self, error_text: str, limit: int = 5) -> list[tuple[Chunk, float]]:
        """Search specifically in troubleshooting/warning/danger sections."""
        if not self._bm25:
            return []
        tokens = _tokenize(error_text)
        if not tokens:
            return []
        scores = self._bm25.get_scores(tokens)

        results: list[tuple[Chunk, float]] = []
        for idx, score in enumerate(scores):
            if score <= 0:
                continue
            chunk = self.chunks[idx]
            # Boost chunks from troubleshooting sections or with admonition markers
            heading_lower = chunk.heading.lower()
            is_troubleshooting = (
                "troubleshoot" in heading_lower
                or "common issues" in heading_lower
                or "common errors" in heading_lower
                or "!!! warning" in chunk.content.lower()
                or "!!! danger" in chunk.content.lower()
                or chunk.page_path == "resources/troubleshooting.md"
            )
            effective_score = score * (2.0 if is_troubleshooting else 1.0)
            results.append((chunk, effective_score))

        results.sort(key=lambda x: x[1], reverse=True)
        return results[:limit]


def _tokenize(text: str) -> list[str]:
    """Simple whitespace + punctuation tokenizer for BM25."""
    return re.findall(r"[a-z0-9_]+", text.lower())


# ---------------------------------------------------------------------------
# Format helpers
# ---------------------------------------------------------------------------


def _format_chunk(chunk: Chunk, score: float | None = None) -> str:
    """Format a chunk for tool output."""
    parts = [f"### {chunk.page_path} → {chunk.heading}"]
    if chunk.parent_heading:
        parts[0] += f" (under {chunk.parent_heading})"
    if score is not None:
        parts[0] += f"  [score: {score:.2f}]"
    parts.append(f"*{chunk.word_count} words | {chunk.category or 'root'}*\n")
    # Truncate very long chunks for search results
    content = chunk.content
    if score is not None and len(content) > 2000:
        content = content[:2000] + "\n\n… (truncated — use get_section for full content)"
    parts.append(content)
    return "\n".join(parts)


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------


@mcp.tool()
async def search_docs(query: str, section: str | None = None, limit: int = 5) -> str:
    """Search lab documentation using ranked keyword search.

    Returns the most relevant documentation sections matching your query,
    ranked by relevance. Much more effective than simple text matching.

    Args:
        query: Natural language search query (e.g. "PyTorch GPU setup", "SLURM job array").
        section: Optional folder filter (e.g. "ml-workflows", "working-on-osc", "getting-started").
        limit: Maximum number of results to return (default 5).
    """
    idx = DocsIndex.get()
    results = idx.search(query, section=section, limit=limit)

    if not results:
        return f"No results found for '{query}'." + (
            f" (filtered to section '{section}')" if section else ""
        )

    parts = [f"Found {len(results)} result(s) for '{query}':\n"]
    for chunk, score in results:
        parts.append(_format_chunk(chunk, score))
        parts.append("---")
    return "\n".join(parts)


@mcp.tool()
async def get_section(page_path: str, heading: str) -> str:
    """Fetch a specific section from a documentation page by its heading.

    Use this instead of read_page when you only need one section. Much faster
    for agents than reading 400-line pages to find one answer.

    Args:
        page_path: Path relative to docs/ (e.g. 'ml-workflows/pytorch-setup.md').
        heading: The H2 or H3 heading text to retrieve (case-insensitive, e.g. 'Installation').
    """
    idx = DocsIndex.get()
    chunk = idx.get_section(page_path, heading)

    if chunk is None:
        # List available headings for this page
        page_chunks = idx.get_page_chunks(page_path)
        if not page_chunks:
            return f"Error: page '{page_path}' not found. Use list_pages() to see available pages."
        headings = [c.heading for c in page_chunks]
        return (
            f"Section '{heading}' not found in '{page_path}'.\n"
            f"Available sections: {', '.join(headings)}"
        )

    return _format_chunk(chunk)


@mcp.tool()
async def read_page(page_path: str) -> str:
    """Read the full markdown content of a documentation page.

    Use get_section if you only need a specific section. This tool returns
    the entire page, which may be long.

    Args:
        page_path: Path relative to docs/ (e.g. 'ml-workflows/pytorch-setup.md').
    """
    idx = DocsIndex.get()
    text = idx.pages.get(page_path)

    if text is None:
        return f"Error: page '{page_path}' not found. Use list_pages() to see available pages."

    title_match = re.search(r"^# (.+)$", text, re.MULTILINE)
    title = title_match.group(1) if title_match else page_path

    return f"# {title}\n**Source:** `{page_path}`\n\n{text}"


@mcp.tool()
async def list_pages(category: str | None = None) -> str:
    """List all documentation pages organized by section.

    Returns the navigation tree from mkdocs.yml. Use this to discover
    available pages and find the right page_path for other tools.

    Args:
        category: Optional section filter (e.g. "ML Workflows", "OSC Basics").
                  Matches against nav section names, case-insensitive.
    """
    idx = DocsIndex.get()
    nav = idx._nav or []

    lines: list[str] = ["# Lab Setup Guide — Page Index\n"]

    if category:
        cat_lower = category.lower()
        filtered = [
            item
            for item in nav
            if isinstance(item, dict) and any(cat_lower in k.lower() for k in item)
        ]
        if not filtered:
            # Show available sections
            sections = []
            for item in nav:
                if isinstance(item, dict):
                    sections.extend(item.keys())
            return f"No section matching '{category}'.\nAvailable sections: {', '.join(sections)}"
        _format_nav(filtered, lines, depth=0)
    else:
        _format_nav(nav, lines, depth=0)

    return "\n".join(lines)


@mcp.tool()
async def find_related(page_path: str) -> str:
    """Find pages related to a given page via cross-links and section siblings.

    Useful for discovering related documentation and navigating the knowledge graph.

    Args:
        page_path: Path relative to docs/ (e.g. 'ml-workflows/pytorch-setup.md').
    """
    idx = DocsIndex.get()

    if page_path not in idx.pages:
        return f"Error: page '{page_path}' not found. Use list_pages() to see available pages."

    related = idx.get_related(page_path)

    parts = [f"# Related pages for `{page_path}`\n"]

    if related["links_to"]:
        parts.append("## Links to (outgoing)")
        for p in related["links_to"]:
            parts.append(f"- `{p}`")
    else:
        parts.append("## Links to (outgoing)\nNone found.")

    if related["linked_from"]:
        parts.append("\n## Linked from (incoming)")
        for p in related["linked_from"]:
            parts.append(f"- `{p}`")
    else:
        parts.append("\n## Linked from (incoming)\nNone found.")

    if related["same_section"]:
        parts.append("\n## Same section")
        for p in related["same_section"]:
            parts.append(f"- `{p}`")

    return "\n".join(parts)


@mcp.tool()
async def get_summary(page_path: str) -> str:
    """Get a structural summary of a documentation page.

    Returns the title, heading outline, and first sentence of each section.
    Useful for understanding page structure before deciding which section to read.

    Args:
        page_path: Path relative to docs/ (e.g. 'working-on-osc/osc-job-submission.md').
    """
    idx = DocsIndex.get()

    if page_path not in idx.pages:
        return f"Error: page '{page_path}' not found. Use list_pages() to see available pages."

    chunks = idx.get_page_chunks(page_path)
    if not chunks:
        return f"No sections found in '{page_path}'."

    # Extract page title
    text = idx.pages[page_path]
    title_match = re.search(r"^# (.+)$", text, re.MULTILINE)
    title = title_match.group(1) if title_match else page_path

    total_words = sum(c.word_count for c in chunks)
    parts = [
        f"# {title}",
        f"**Source:** `{page_path}` | **{total_words} words** | **{len(chunks)} sections**\n",
        "## Sections\n",
    ]

    for chunk in chunks:
        # First meaningful sentence (skip blank lines and headings)
        first_sentence = ""
        for line in chunk.content.split("\n"):
            line = line.strip()
            if line and not line.startswith("#") and not line.startswith("!!! "):
                # Take first sentence
                sentence_end = re.search(r"[.!?](\s|$)", line)
                if sentence_end:
                    first_sentence = line[: sentence_end.end()].strip()
                else:
                    first_sentence = line[:120]
                break

        prefix = "  " if chunk.parent_heading else ""
        parts.append(f"{prefix}- **{chunk.heading}** ({chunk.word_count}w): {first_sentence}")

    return "\n".join(parts)


@mcp.tool()
async def troubleshoot(error_text: str) -> str:
    """Search for troubleshooting help by error message or symptom.

    Searches documentation with a bias toward troubleshooting sections,
    warning/danger admonitions, and the dedicated troubleshooting page.

    Args:
        error_text: The error message, symptom, or problem description
                    (e.g. "OUT_OF_MEMORY", "module load fails", "ssh connection refused").
    """
    idx = DocsIndex.get()
    results = idx.find_troubleshooting(error_text)

    if not results:
        return (
            f"No troubleshooting results for '{error_text}'. "
            "Try broader terms or use search_docs for general search."
        )

    parts = [f"Troubleshooting results for '{error_text}':\n"]
    for chunk, score in results:
        parts.append(_format_chunk(chunk, score))
        parts.append("---")
    return "\n".join(parts)


# ---------------------------------------------------------------------------
# Nav formatter (shared with list_pages)
# ---------------------------------------------------------------------------


def _format_nav(items: list, lines: list[str], depth: int) -> None:
    indent = "  " * depth
    for item in items:
        if isinstance(item, str):
            lines.append(f"{indent}- `{item}`")
        elif isinstance(item, dict):
            for label, value in item.items():
                if isinstance(value, str):
                    lines.append(f"{indent}- **{label}**: `{value}`")
                elif isinstance(value, list):
                    lines.append(f"{indent}- **{label}**")
                    _format_nav(value, lines, depth + 1)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("lab-setup-docs MCP server v2 starting…", file=sys.stderr)
    mcp.run(transport="stdio")
