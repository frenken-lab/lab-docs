<!-- last-reviewed: 2026-02-26 -->
# AI Coding Assistants

Set up AI-powered coding tools to accelerate your development workflow in the lab.

## Overview

AI coding assistants can help you write code faster, understand unfamiliar codebases, debug errors, and learn new frameworks. This guide covers the two most useful tools for lab work: **GitHub Copilot** (integrated into VS Code) and **Claude Code** (a CLI tool).

### Pros and Cons

| | Benefit |
|---|---------|
| ✅ | Speeds up writing boilerplate and repetitive code |
| ✅ | Helps explore unfamiliar libraries and APIs |
| ✅ | Useful for debugging errors and understanding stack traces |
| ✅ | Can generate documentation and tests |
| ❌ | Generated code may contain bugs — always review |
| ❌ | May suggest outdated patterns or incorrect API usage |
| ❌ | Can be a crutch if relied on without understanding |

### Comparison

| Feature | GitHub Copilot | Claude Code |
|---------|---------------|-------------|
| **Interface** | VS Code extension (inline + chat) | Terminal CLI |
| **Best For** | Inline completions while coding | Multi-file edits, project-wide tasks |
| **Context** | Current file + open tabs | Entire project directory |
| **Cost** | Free with GitHub Education | API key or Claude.ai subscription |
| **Works on OSC** | Yes (VS Code Remote-SSH) | Yes (install via curl on login node) |

## GitHub Copilot

GitHub Copilot provides AI-powered code completions directly in VS Code.

### Installation

Install the Copilot extensions in VS Code:

1. Open VS Code
2. Go to the Extensions view (++ctrl+shift+x++)
3. Search for and install these two extensions:
    - `GitHub.copilot` — Inline code completions
    - `GitHub.copilot-chat` — Chat sidebar for questions and explanations

Or install from the command line:

```bash
code --install-extension GitHub.copilot
code --install-extension GitHub.copilot-chat
```

### Authentication

1. After installing, click the Copilot icon in the VS Code status bar
2. Sign in with your **GitHub account**
3. Authorize the extension when prompted

!!! tip "Free access with GitHub Education"
    Students and educators get GitHub Copilot for free through the [GitHub Education Pack](https://education.github.com/pack). Sign up with your `@osu.edu` email.

### Usage

#### Inline Completions

Copilot suggests code as you type. Ghost text appears in gray:

- Press ++tab++ to accept a suggestion
- Press ++escape++ to dismiss
- Press ++alt+bracket-right++ / ++alt+bracket-left++ to cycle through alternatives

```python
# Example: start typing a function and Copilot completes it
def load_dataset(path, batch_size=32):
    # Copilot suggests the body based on context
```

#### Copilot Chat

Open the chat sidebar with ++ctrl+shift+i++ (or click the Copilot icon) to ask questions:

- **Explain code**: Select code, then ask "Explain this"
- **Fix errors**: Paste an error message and ask for help
- **Generate code**: Describe what you want in natural language

Useful slash commands in Copilot Chat:

| Command | Description |
|---------|-------------|
| `/explain` | Explain the selected code |
| `/fix` | Suggest a fix for problems in selected code |
| `/tests` | Generate unit tests for selected code |
| `/doc` | Generate documentation for selected code |

### Configuration

Add these to your VS Code `settings.json` (++ctrl+comma++ → Open Settings JSON):

```json
{
    "github.copilot.enable": {
        "*": true,
        "markdown": true,
        "yaml": true
    }
}
```

!!! note "Copilot works over Remote-SSH"
    When connected to OSC via VS Code Remote-SSH, Copilot runs locally on your machine and sends completions to the remote editor. No additional setup is needed on OSC.

## Claude Code (CLI)

Claude Code is a command-line AI assistant that can read, edit, and create files across your entire project.

### What It Is

Claude Code is a terminal-based tool that:

- Understands your full project context (reads files, searches code)
- Can edit multiple files in a single session
- Runs commands and interprets their output
- Follows project-specific instructions via `CLAUDE.md` files

### Installation

Install Claude Code using the official installer:

```bash
# Install on your local machine or OSC
curl -fsSL https://claude.ai/install.sh | bash
```

This installs the `claude` binary to `~/.local/bin/`. No Node.js required.

### Authentication

Set your Anthropic API key:

```bash
# Add to your shell profile (~/.bashrc or ~/.zshrc)
export ANTHROPIC_API_KEY="sk-ant-..."
```

Or authenticate interactively on first launch:

```bash
claude
# Follow the prompts to sign in
```

### Basic Usage

#### Interactive Mode

Start an interactive session in your project directory:

```bash
cd ~/projects/my-research
claude
```

Then type natural language requests:

- "Explain what `train.py` does"
- "Add a learning rate scheduler to the training loop"
- "Find all places where we load data and add error handling"

#### One-Shot Mode

Run a single prompt and print the output without entering interactive mode:

```bash
claude -p "Explain the architecture of this project"
claude -p "Generate a .gitignore for a Python ML project"
```

## Project Configuration with CLAUDE.md

### What It Is

A `CLAUDE.md` file gives Claude Code project-specific context — coding conventions, build commands, architecture notes, and other instructions it should follow.

### Creating a CLAUDE.md

Place a `CLAUDE.md` file in your project root:

```markdown
# CLAUDE.md

## Project Overview
PyTorch-based object detection pipeline for autonomous vehicle research.
Uses YOLO architecture with custom modifications for lidar-camera fusion.

## Commands
- `python train.py --config configs/default.yaml` — Train model
- `python evaluate.py --checkpoint models/best.pt` — Evaluate
- `pytest tests/` — Run tests

## Architecture
- `models/` — Model definitions (YOLO variants)
- `data/` — Dataset loaders and augmentation
- `configs/` — YAML configuration files
- `scripts/` — SLURM job scripts for OSC

## Conventions
- Use PyTorch 2.0+ features
- Type hints on all public functions
- Config files in YAML format
- SLURM scripts use `PAS1234` account
```

### Nested CLAUDE.md Files

You can place additional `CLAUDE.md` files in subdirectories for component-specific instructions:

```
my-project/
├── CLAUDE.md                    # Project-wide context
├── models/
│   └── CLAUDE.md                # Model-specific conventions
├── data/
│   └── CLAUDE.md                # Data pipeline details
└── scripts/
    └── CLAUDE.md                # SLURM/OSC-specific notes
```

Claude Code merges instructions from all `CLAUDE.md` files in the path hierarchy.

### Example for an ML Project

````markdown
# CLAUDE.md

## Project Overview
Point cloud segmentation for autonomous driving using PointNet++.
Training runs on OSC Pitzer cluster with V100 GPUs.

## Commands
```bash
# Local testing
python train.py --config configs/debug.yaml --fast-dev-run

# OSC job submission
sbatch scripts/train_gpu.sh

# Evaluation
python evaluate.py --checkpoint outputs/best_model.pt --data data/test/
```

## Architecture
- `models/pointnet2.py` — PointNet++ implementation
- `data/nuscenes_loader.py` — nuScenes dataset loader
- `configs/` — Hydra YAML configs (base, debug, full)
- `scripts/` — SLURM scripts targeting Pitzer GPU partition

## Coding Conventions
- Python 3.9+, PyTorch 2.0+
- Use Hydra for configuration management
- Logging via Python `logging` module (not print)
- Save checkpoints every 10 epochs to `outputs/checkpoints/`
````

## Settings Configuration

Claude Code supports three levels of settings files:

### Per-Repository Settings (Not Committed)

`.claude/settings.local.json` — Personal preferences for this repo. Add to `.gitignore`.

```json
{
    "permissions": {
        "allow": [
            "Bash(python *)",
            "Bash(pip install *)",
            "Bash(sbatch *)"
        ]
    }
}
```

### Team-Shared Settings (Committed)

`.claude/settings.json` — Shared team conventions. Commit to version control.

```json
{
    "permissions": {
        "allow": [
            "Bash(python *)",
            "Bash(pytest *)",
            "Bash(mkdocs *)"
        ]
    }
}
```

### User-Level Global Settings

`~/.claude/settings.json` — Applies to all your projects.

```json
{
    "permissions": {
        "deny": [
            "Bash(rm -rf *)"
        ]
    }
}
```

!!! warning "Don't commit `settings.local.json`"
    The `.claude/settings.local.json` file may contain personal preferences and allowed commands specific to your machine. Add `.claude/settings.local.json` to your `.gitignore`.

## Best Practices

### 1. Always Review Generated Code

AI assistants can produce plausible-looking code that is subtly wrong. Before accepting suggestions:

- ✅ Read through the generated code line by line
- ✅ Check that API calls use correct arguments and return types
- ✅ Verify edge cases are handled
- ✅ Run tests after accepting changes

### 2. Don't Share Secrets

Never paste API keys, passwords, or credentials into AI chat interfaces:

- ❌ Don't include secrets in prompts
- ❌ Don't include secrets in `CLAUDE.md` files
- ✅ Use environment variables for sensitive values
- ✅ Add `.env` files to `.gitignore`

### 3. Use `.claudeignore`

Create a `.claudeignore` file (same syntax as `.gitignore`) to prevent Claude Code from reading sensitive or irrelevant files:

```
# .claudeignore
.env
*.pth
*.pt
data/raw/
wandb/
__pycache__/
```

### 4. Version Control Configuration

Files to commit:

- ✅ `CLAUDE.md` — Project context for the team
- ✅ `.claude/settings.json` — Shared permissions
- ✅ `.claudeignore` — Shared ignore patterns

Files to **not** commit:

- ❌ `.claude/settings.local.json` — Personal preferences

### 5. Use AI for Learning, Not Just Output

When an AI assistant suggests something unfamiliar:

- Ask it to explain *why* it chose that approach
- Look up the documentation for any new APIs or patterns
- Understand the code before committing it to your project

## Troubleshooting

### Copilot Not Showing Suggestions

1. Check that you're signed in (look for the Copilot icon in the status bar)
2. Verify the extension is enabled for the current language
3. Check your internet connection (Copilot needs network access)
4. Try reloading VS Code (++ctrl+shift+p++ → "Reload Window")

### Claude Code "Command Not Found"

```bash
# Check installation
which claude

# Reinstall if needed
curl -fsSL https://claude.ai/install.sh | sh

# Ensure ~/.claude/bin is in your PATH
export PATH="$HOME/.claude/bin:$PATH"
```

### Claude Code API Key Issues

```bash
# Verify your key is set
echo $ANTHROPIC_API_KEY

# If empty, add to your shell profile
echo 'export ANTHROPIC_API_KEY="sk-ant-..."' >> ~/.bashrc
source ~/.bashrc
```

### Copilot Not Working Over Remote-SSH

1. Ensure the Copilot extension is installed locally (not on the remote)
2. Check that VS Code is connected to the remote (look at the bottom-left status bar)
3. Reload the VS Code window after reconnecting

## Next Steps

- [Agent Workflows](agent-workflows.md) — Advanced usage: MCP servers, custom skills, hooks, knowledge management
- Set up [VS Code](vscode-setup.md) if you haven't already
- Install recommended [VS Code Extensions](vscode-extensions.md)
- Connect to OSC for [Remote Development](../osc-basics/osc-remote-development.md)

## Resources

- [GitHub Copilot Documentation](https://docs.github.com/en/copilot)
- [GitHub Education Pack](https://education.github.com/pack)
- [Claude Code Documentation](https://docs.anthropic.com/en/docs/claude-code)
- [Anthropic API Documentation](https://docs.anthropic.com/)
