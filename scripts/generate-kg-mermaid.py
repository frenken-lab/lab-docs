#!/usr/bin/env python3
"""Generate a Mermaid diagram from the Claude Code MCP knowledge graph.

Reads ~/.claude/knowledge-graph.json (NDJSON format) and outputs a valid
Mermaid `graph LR` block with entities as styled nodes and relations as
labeled edges.

Usage:
    python scripts/generate-kg-mermaid.py                     # default path
    python scripts/generate-kg-mermaid.py /path/to/kg.json    # custom path
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

# Color scheme by entity type (Mermaid classDef fill colors)
TYPE_COLORS: dict[str, tuple[str, str]] = {
    # entityType -> (fill, stroke)
    "architecture_decision": ("#4A90D9", "#2A5F9E"),  # blue
    "convention": ("#9B59B6", "#6C3483"),  # purple
    "infrastructure": ("#E67E22", "#BA4A00"),  # orange
    "technology": ("#1ABC9C", "#0E8C73"),  # teal
    "library": ("#1ABC9C", "#0E8C73"),  # teal (same as technology)
    "learning": ("#E91E90", "#B3166E"),  # pink
    "milestone": ("#F1C40F", "#B7950B"),  # yellow
    "changelog": ("#95A5A6", "#717D7E"),  # grey
    "canonical_answer": ("#27AE60", "#1E8449"),  # green
}


def normalize_type(entity_type: str) -> str:
    """Normalize entity type to snake_case key for color lookup."""
    return re.sub(r"[\s\-]+", "_", entity_type.strip().lower())


def sanitize_id(name: str) -> str:
    """Convert entity name to a valid Mermaid node ID."""
    return re.sub(r"[^a-zA-Z0-9]", "_", name).strip("_")


def truncate_label(name: str, max_len: int = 30) -> str:
    """Truncate long names for readable node labels."""
    if len(name) <= max_len:
        return name
    return name[: max_len - 1] + "..."


def generate_mermaid(kg_path: Path) -> str:
    """Read NDJSON knowledge graph and return a Mermaid diagram string."""
    entities: list[dict] = []
    relations: list[dict] = []

    with open(kg_path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            record = json.loads(line)
            if record.get("type") == "entity":
                entities.append(record)
            elif record.get("type") == "relation":
                relations.append(record)

    lines: list[str] = []
    lines.append("graph LR")

    # Collect which types are actually used
    used_types: set[str] = set()
    defined_ids: set[str] = set()

    # Emit nodes
    for entity in entities:
        node_id = sanitize_id(entity["name"])
        label = truncate_label(entity["name"])
        norm_type = normalize_type(entity.get("entityType", "unknown"))
        used_types.add(norm_type)
        defined_ids.add(node_id)
        lines.append(f'    {node_id}["{label}"]:::{norm_type}')

    lines.append("")

    # Collect edges, track referenced but undefined nodes
    edge_lines: list[str] = []
    for rel in relations:
        src = sanitize_id(rel["from"])
        dst = sanitize_id(rel["to"])
        label = rel.get("relationType", "")
        # Only emit edges where both endpoints are defined entities
        if src in defined_ids and dst in defined_ids:
            edge_lines.append(f"    {src} -->|{label}| {dst}")

    lines.extend(edge_lines)

    lines.append("")

    # Emit classDef for each used type
    for norm_type in sorted(used_types):
        fill, stroke = TYPE_COLORS.get(norm_type, ("#BDC3C7", "#7F8C8D"))
        lines.append(
            f"    classDef {norm_type} fill:{fill},stroke:{stroke},color:#fff,stroke-width:2px"
        )

    return "\n".join(lines)


def main() -> None:
    if len(sys.argv) > 1:
        kg_path = Path(sys.argv[1])
    else:
        kg_path = Path.home() / ".claude" / "knowledge-graph.json"

    if not kg_path.exists():
        print(f"Error: {kg_path} not found", file=sys.stderr)
        sys.exit(1)

    print(generate_mermaid(kg_path))


if __name__ == "__main__":
    main()
