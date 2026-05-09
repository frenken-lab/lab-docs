<!-- last-reviewed: 2026-02-26 -->
# VS Code Extensions

Extensions enhance VS Code's functionality. This guide covers required extensions for lab work and recommended extensions for productivity.

## Installing Extensions

### Method 1: Extension Marketplace (GUI)
1. Click the Extensions icon in the sidebar (or press `Ctrl+Shift+X` / `Cmd+Shift+X`)
2. Search for the extension name
3. Click "Install"

### Method 2: Command Line
```bash
code --install-extension <extension-id>
```

## Required Extensions

These extensions are essential for lab work:

### 1. Remote - SSH
- **ID**: `ms-vscode-remote.remote-ssh`
- **Purpose**: Connect to OSC and other remote servers
- **Why Required**: Essential for working on OSC clusters
- **Documentation**: [Remote - SSH Guide](../osc-basics/osc-remote-development.md)

### 2. Remote - SSH: Editing Configuration Files
- **ID**: `ms-vscode-remote.remote-ssh-edit`
- **Purpose**: Edit SSH configuration files easily

### 3. Python
- **ID**: `ms-python.python`
- **Purpose**: Python language support, debugging, linting
- **Why Required**: Most lab projects use Python

### 4. Pylance
- **ID**: `ms-python.vscode-pylance`
- **Purpose**: Fast, feature-rich Python language server
- **Features**: Type checking, auto-imports, better IntelliSense

### 5. Remote - WSL
- **ID**: `ms-vscode-remote.remote-wsl`
- **Purpose**: Open any folder inside WSL as a VS Code workspace
- **Why Required**: Windows users run all lab tools inside WSL; this extension bridges VS Code to the WSL filesystem
- **Documentation**: [WSL Setup Guide](wsl-setup.md)

### 6. Jupyter
- **ID**: `ms-toolsai.jupyter`
- **Purpose**: Run and edit Jupyter notebooks in VS Code
- **Why Required**: Many ML workflows use Jupyter notebooks

## Highly Recommended Extensions

### General Development

#### 1. GitLens
- **ID**: `eamodio.gitlens`
- **Purpose**: Supercharge Git capabilities
- **Features**: Blame annotations, commit history, repository insights

#### 2. Git Graph
- **ID**: `mhutchie.git-graph`
- **Purpose**: View Git repository graph
- **Features**: Visual commit history, branch visualization

#### 3. Path Intellisense
- **ID**: `christian-kohler.path-intellisense`
- **Purpose**: Auto-complete file paths

#### 4. Todo Tree
- **ID**: `gruntfuggly.todo-tree`
- **Purpose**: Highlight and organize TODO comments

### Python Development

#### 5. autoDocstring
- **ID**: `njpwerner.autodocstring`
- **Purpose**: Generate Python docstrings automatically

#### 6. Python Indent
- **ID**: `kevinrose.vsc-python-indent`
- **Purpose**: Correct Python indentation

#### 7. Ruff
- **ID**: `astral-sh.ruff`
- **Purpose**: Fast Python linter and formatter (replaces Black, isort, Flake8, and more)
- **Note**: Ruff is a single tool that handles both linting and formatting. It replaces the now-deprecated `python.linting.*` and `python.formatting.*` settings.

### Machine Learning

#### 8. PyTorch Snippets
- **ID**: `SBSnippets.pytorch-snippets`
- **Purpose**: PyTorch code snippets

#### 9. TensorBoard
- **ID**: `ms-toolsai.vscode-tensorboard`
- **Purpose**: View TensorBoard logs in VS Code

### Productivity

#### 10. Markdown All in One
- **ID**: `yzhang.markdown-all-in-one`
- **Purpose**: Enhanced Markdown editing
- **Features**: Shortcuts, table of contents, preview

#### 11. Better Comments
- **ID**: `aaron-bond.better-comments`
- **Purpose**: Color-code comments (TODO, FIXME, etc.)

#### 12. Error Lens
- **ID**: `usernamehw.errorlens`
- **Purpose**: Highlight errors inline

#### 13. Bracket Pair Colorization (Built-in)
- VS Code has built-in bracket pair colorization — no extension needed
- **Enable**: Search for "Bracket Pair Colorization" in settings and enable it

## Extension Configuration

### Python Extension Settings

Add to your `settings.json`:

```json
{
  "python.languageServer": "Pylance",
  "python.analysis.typeCheckingMode": "basic",
  "[python]": {
    "editor.defaultFormatter": "astral-sh.ruff",
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
      "source.fixAll": "explicit",
      "source.organizeImports": "explicit"
    }
  },
  "ruff.lineLength": 100
}
```

!!! note "Deprecated settings"
    The `python.linting.*` and `python.formatting.*` settings were removed in recent versions of the Python extension. Use the Ruff extension instead — it handles linting, formatting, and import sorting in one tool.

### Remote SSH Settings

```json
{
  "remote.SSH.remotePlatform": {
    "pitzer.osc.edu": "linux"
  },
  "remote.SSH.showLoginTerminal": true,
  "remote.SSH.useLocalServer": false
}
```

## Batch Installation

Install all required extensions at once:

```bash
# Required extensions
code --install-extension ms-vscode-remote.remote-ssh
code --install-extension ms-vscode-remote.remote-ssh-edit
code --install-extension ms-python.python
code --install-extension ms-python.vscode-pylance
code --install-extension ms-toolsai.jupyter

# Recommended extensions
code --install-extension eamodio.gitlens
code --install-extension mhutchie.git-graph
code --install-extension christian-kohler.path-intellisense
code --install-extension njpwerner.autodocstring
code --install-extension astral-sh.ruff
code --install-extension yzhang.markdown-all-in-one
code --install-extension usernamehw.errorlens
```

## Managing Extensions

### Disable Extensions for Specific Workspaces
- Right-click an extension in the Extensions view
- Select "Disable (Workspace)" to disable it only for the current project

### Extension Recommendations for Projects
Create `.vscode/extensions.json` in your project:

```json
{
  "recommendations": [
    "ms-python.python",
    "ms-python.vscode-pylance",
    "ms-toolsai.jupyter"
  ]
}
```

## Extension Syncing

Enable Settings Sync (see [VS Code Setup](vscode-setup.md#settings-sync)) to sync extensions across machines.

## Next Steps

- Configure [Remote Development on OSC](../osc-basics/osc-remote-development.md)
- Set up [SSH Connection to OSC](../osc-basics/osc-ssh-connection.md)
- Learn about [PyTorch Setup](../ml-workflows/pytorch-setup.md)

## Troubleshooting

### Extension won't activate on remote
- Make sure the extension supports remote development
- Try reloading the VS Code window: `Ctrl+Shift+P` → "Developer: Reload Window"
- Check the extension's output log for errors

### Extensions causing performance issues
- Disable extensions you don't actively use
- Use "Disable (Workspace)" for extensions not needed in specific projects
- Check extension ratings and reviews for known issues

For more help, see the [Troubleshooting Guide](../resources/troubleshooting.md).
