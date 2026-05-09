<!-- last-reviewed: 2026-03-03 -->
# Agent Workflows

Advanced patterns for working effectively with AI coding agents on research projects. This page covers the "power user" techniques — if you're new to Claude Code, start with [AI Coding Assistants](ai-coding-assistants.md) for setup basics.

---

## Effective Prompting for Research Code

The difference between a mediocre and excellent AI response often comes down to how you frame your request.

### Be Specific About Context

```
❌  "Fix the training loop"
✅  "The training loop in train.py loses GPU memory each epoch.
     After 50 epochs, OOM kills the job. I suspect the loss history
     list is holding graph references."
```

### Frame the Research Context

AI agents work better when they understand your domain:

```
❌  "Add a new model"
✅  "Add a GAT model variant that uses edge features for CAN bus
     message classification. It should follow the same PyG
     MessagePassing pattern as the existing VGAE in models/vgae.py.
     The edge features are 8-dimensional (DLC + padding bytes)."
```

### One-Shot vs Interactive Mode

| Mode | Command | Best For |
|------|---------|----------|
| **Interactive** | `claude` | Multi-file refactors, exploratory tasks, debugging sessions |
| **One-shot** | `claude -p "..."` | Quick questions, single-file generation, CI integration |

One-shot mode is useful for scripting — pipe output to files or other commands:

```bash
# Generate a .gitignore
claude -p "Generate a .gitignore for a Python ML project on OSC" > .gitignore

# Explain a file
claude -p "Explain the architecture of src/models/gat.py"
```

### Iterative Refinement

Complex tasks work best when broken into steps:

1. Ask Claude to **read and summarize** the relevant code first
2. Discuss the **approach** before writing code
3. Implement in **focused chunks** — one function or module at a time
4. **Review and test** before moving to the next piece

---

## CLAUDE.md Deep Dive

The [AI Coding Assistants](ai-coding-assistants.md) page covers basic `CLAUDE.md` usage. Here we cover advanced patterns for research projects.

### Modular Context Architecture

For large projects, a single `CLAUDE.md` becomes unwieldy. The modular pattern splits context into topic files:

```
my-project/
├── CLAUDE.md                    # Lean registry — overview + pointers
└── .claude/
    └── rules/                   # Topic files (auto-loaded by Claude Code)
        ├── project-structure.md # Directory tree, file roles
        ├── architecture.md      # Design decisions, patterns
        ├── code-style.md        # Import rules, conventions
        ├── config-system.md     # Configuration details
        └── slurm-hpc.md         # SLURM conventions
```

Claude Code auto-loads all `.md` files in `.claude/rules/` — no manual imports needed.

**The key rule: each topic has exactly one owner file.** Other files use one-line pointers:

```markdown
> Experiment tracking details: See `experiment-tracking.md`
```

This avoids contradictions when instructions span multiple files.

### What Goes in CLAUDE.md vs Rules Files

| Content | Location |
|---------|----------|
| Project overview, key commands, skills | `CLAUDE.md` (always loaded, lean) |
| Architecture decisions, design rationale | `.claude/rules/architecture.md` |
| Code style, import hierarchy, git conventions | `.claude/rules/code-style.md` |
| Crash-prevention rules, hard constraints | `.claude/rules/critical-constraints.md` |
| SLURM conventions, login node safety | `.claude/rules/slurm-hpc.md` |

### Nested Configs for Monorepos

Claude Code merges `CLAUDE.md` files from the path hierarchy. For a project with subcomponents:

```
project/
├── CLAUDE.md                # Project-wide: commands, overview
├── models/
│   └── CLAUDE.md            # Model-specific: architecture conventions
├── data/
│   └── CLAUDE.md            # Data pipeline: formats, validation rules
└── scripts/
    └── CLAUDE.md            # SLURM scripts: account, partition, resource defaults
```

When you `cd` into `models/`, Claude sees both the root and `models/CLAUDE.md`.

---

## MCP Servers

Model Context Protocol (MCP) servers extend Claude Code with external data sources and tools. They run as local processes that Claude Code communicates with over stdio.

### What They Are

MCP servers are lightweight processes that expose **tools** (callable functions) and **resources** (readable data) to Claude Code. Think of them as plugins — each server adds domain-specific capabilities.

### Configuration

MCP servers are configured in `~/.claude.json` (user-scope) or `.claude.json` (project-scope):

```json
{
  "mcpServers": {
    "lab-docs": {
      "command": "uv",
      "args": ["run", "--with", "mcp[cli]", "--with", "pyyaml",
               "/path/to/lab-setup-guide/scripts/mcp_lab_docs.py"],
      "env": {}
    },
    "memory": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-memory",
               "--memory-path", "/path/to/knowledge-graph.json"]
    }
  }
}
```

### Practical Examples

**Documentation search** — A lab-docs MCP server that indexes your MkDocs site, letting Claude search documentation without leaving the terminal:

```
You: "How do I set up PyG on OSC?"
Claude: [searches lab-docs MCP] → returns the relevant section from pyg-setup.md
```

**Library documentation** — [Context7](https://github.com/upstash/context7) aggregates docs for hundreds of libraries (PyTorch, Ray, pandas, etc.):

```
You: "Show me the Ray Tune API for ASHAScheduler"
Claude: [queries Context7] → returns up-to-date API docs with examples
```

**Persistent knowledge graph** — The [memory MCP server](https://github.com/modelcontextprotocol/servers/tree/main/src/memory) stores entities and relations across sessions:

```
You: "Remember that dataset hcrl_sa has 44K graphs and takes ~2 hours to preprocess"
Claude: [creates entity in knowledge graph] → persists across sessions
```

### Building Your Own MCP Server

MCP servers are simple Python scripts using the `mcp` library:

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("my-server")

@mcp.tool()
def search_experiments(query: str, limit: int = 5) -> str:
    """Search experiment results by description."""
    # Query your DuckDB datalake, W&B, or local files
    ...
    return results

if __name__ == "__main__":
    mcp.run(transport="stdio")
```

For the full MCP specification, see [modelcontextprotocol.io](https://modelcontextprotocol.io/).

---

## Custom Skills & Slash Commands

Skills are reusable prompt templates that you invoke with slash commands like `/save` or `/slurm-status`.

### Skill File Anatomy

Skills live in `.claude/skills/` (project-scope) or `~/.claude/skills/` (global). Each is a Markdown file:

```markdown
---
name: slurm-status
description: Check SLURM queue, recent jobs, and allocation usage
user_invocable: true
---

# SLURM Status Check

Run the following commands and summarize the results:

1. `squeue -u $USER` — current queue
2. `sacct -u $USER --starttime=today -o JobID,JobName,State,Elapsed,MaxRSS` — today's jobs
3. `accounts` or check allocation balance

Present as a concise table. Flag any failed jobs.
```

The `---` front matter defines metadata. The body is the prompt Claude receives when you type `/slurm-status`.

### When to Use Skills vs Manual Prompts

| Use Skills For | Use Manual Prompts For |
|----------------|----------------------|
| Repeated tasks (check status, run tests) | One-off questions |
| Workflows with specific steps | Exploratory debugging |
| Team-shared conventions | Context-dependent requests |

### Example Skills for Research

**`/save`** — Log a learning to your knowledge bank:

```markdown
---
name: save
description: Log a learning or decision to the knowledge bank
user_invocable: true
---

The user wants to save a learning. Append it to `~/.claude/rules/knowledge-bank.md`
under the Learnings section with today's date prefix. Also create/update an entity
in the memory MCP server.

Format: `- **YYYY-MM-DD:** <entry>`
```

**`/run-tests`** — Submit tests to SLURM (not the login node):

```markdown
---
name: run-tests
description: Run the pytest suite via SLURM
user_invocable: true
---

Submit tests to SLURM. NEVER run pytest on the login node.
Run: `bash scripts/slurm/run_tests_slurm.sh`
Monitor with `squeue -u $USER` until completion, then show results.
```

---

## Context Management

As your `CLAUDE.md` and rules files grow, managing context becomes important — you need to avoid drift (files contradicting each other) and bloat (too much context loaded per session).

### Ownership Registry Pattern

An ownership registry maps every topic to exactly one file:

```markdown
| Topic | Owner File |
|-------|-----------|
| Directory tree, layer hierarchy | `project-structure.md` |
| Config resolution | `config-system.md` |
| Import rules, git conventions | `code-style.md` |
| SLURM conventions | `slurm-hpc.md` |
```

**Rule:** To update a topic, find its owner in the registry. Edit only that file. If another file mentions the topic, it should be a one-line pointer, not duplicated content.

### `.claudeignore`

Like `.gitignore`, `.claudeignore` prevents Claude from reading irrelevant or sensitive files:

```
# .claudeignore
.env
*.pth
*.pt
data/raw/
wandb/
__pycache__/
node_modules/
```

This keeps context focused and avoids accidentally sharing secrets.

### Avoiding Context Drift

Context drift happens when multiple files contain overlapping or contradictory instructions. Prevent it by:

1. **Single source of truth** — each topic owned by one file
2. **Pointers, not copies** — other files link to the owner
3. **Regular audits** — periodically review rules files for staleness
4. **Date stamps** — mark mutable sections with `<!-- last-reviewed: YYYY-MM-DD -->`

---

## Hooks

Hooks are shell scripts that run automatically in response to Claude Code events. They provide safety guardrails and automation without manual intervention.

### Hook Types

| Type | When It Runs | Use Case |
|------|-------------|----------|
| `PreToolUse` | Before a tool executes | Block dangerous commands |
| `PostToolUse` | After a tool executes | Auto-format code, trigger checks |
| `SessionStart` | When a session begins | Inject environment context |

### Configuration

Hooks are defined in `.claude/settings.json` (project) or `~/.claude/settings.json` (global):

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "bash .claude/hooks/warn-login-node.sh \"$TOOL_INPUT\""
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "bash .claude/hooks/auto-format-python.sh \"$TOOL_INPUT\""
          }
        ]
      }
    ]
  }
}
```

### Practical Hook Examples

**Login node guard** — Blocks heavy computation on OSC login nodes:

```bash
#!/bin/bash
# warn-login-node.sh — PreToolUse hook for Bash
# Blocks commands that shouldn't run on login nodes

HOSTNAME=$(hostname)
if [[ "$HOSTNAME" == *login* ]]; then
    INPUT="$1"
    # Block pytest, training scripts, heavy Python
    if echo "$INPUT" | grep -qE '(pytest|python -m graphids|train\.py)'; then
        echo "BLOCKED: This command should be submitted to SLURM, not run on a login node."
        echo "Use: sbatch scripts/train.sh  or  bash scripts/slurm/run_tests_slurm.sh"
        exit 2  # Exit code 2 = block the tool call
    fi
fi
```

**Auto-format Python** — Runs `ruff` after every file edit:

```bash
#!/bin/bash
# auto-format-python.sh — PostToolUse hook for Edit/Write
# Auto-formats Python files with ruff after editing

FILE=$(echo "$1" | python3 -c "import sys,json; print(json.load(sys.stdin).get('file_path',''))")
if [[ "$FILE" == *.py ]]; then
    ruff format "$FILE" 2>/dev/null
    ruff check --fix "$FILE" 2>/dev/null
fi
```

**SLURM context injection** — Shows queue status at session start:

```bash
#!/bin/bash
# inject-slurm-context.sh — SessionStart hook
# Injects SLURM queue status into Claude's context

if command -v squeue &>/dev/null; then
    echo "--- SLURM Context ---"
    HOSTNAME=$(hostname)
    if [[ "$HOSTNAME" == *login* ]]; then
        echo "Running on login node ($HOSTNAME)"
    fi
    echo ""
    echo "Current SLURM queue:"
    QUEUE=$(squeue -u "$USER" -o "  %j %T %M %P" --noheader 2>/dev/null)
    if [ -z "$QUEUE" ]; then
        echo "  (no jobs in queue)"
    else
        echo "$QUEUE"
    fi
    echo "--- End SLURM Context ---"
fi
```

---

## Knowledge Bank & Memory

AI agents are stateless by default — they forget everything between sessions. Two mechanisms provide persistence.

### Auto-Memory (MEMORY.md)

Claude Code maintains a `MEMORY.md` file per project in `.claude/projects/`. It automatically records:

- Active project state and key decisions
- Environment details (Python version, tools)
- Patterns confirmed across multiple sessions

This file is loaded into context at the start of every session, giving Claude baseline awareness of your project.

### Memory MCP Server (Knowledge Graph)

For structured, cross-project memory, the [memory MCP server](https://github.com/modelcontextprotocol/servers/tree/main/src/memory) maintains a knowledge graph of entities and relations:

```
Entity: "hcrl_sa dataset"
  Type: dataset
  Observations:
    - "44K graphs, ~2 hours preprocessing"
    - "6 attack types: DoS, fuzzing, gear, RPM, standstill, max_speedometer"

Entity: "KD-GAT project"
  Type: project
  Relations:
    - uses → "hcrl_sa dataset"
    - deployed_to → "HF Spaces"
```

The `/save` skill writes to both the knowledge bank (flat Markdown) and the knowledge graph (structured entities).

### What to Save vs Not Save

| Save | Don't Save |
|------|-----------|
| Stable patterns confirmed across sessions | Session-specific debugging context |
| Key architecture decisions | In-progress task details |
| Solutions to recurring problems | Speculative conclusions from one file |
| User workflow preferences | Anything in existing CLAUDE.md |

---

## Next Steps

- [AI Coding Assistants](ai-coding-assistants.md) — Setup basics for Copilot and Claude Code
- [Job Submission](../working-on-osc/osc-job-submission.md) — SLURM context for the hooks examples above
- [Pipeline Orchestration](../working-on-osc/pipeline-orchestration.md) — Complex workflows that benefit from agent assistance

## Resources

- [Claude Code Documentation](https://docs.anthropic.com/en/docs/claude-code) — Official reference
- [MCP Specification](https://modelcontextprotocol.io/) — Model Context Protocol details
- [Claude Code Best Practices](https://docs.anthropic.com/en/docs/claude-code/best-practices) — Anthropic's recommendations
