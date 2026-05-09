---
tags:
  - WSL2
---
<!-- last-reviewed: 2026-02-26 -->
# WSL2 Setup

This guide walks you through installing and configuring the Windows Subsystem for Linux 2 (WSL2), the foundation for local development in the lab.

## Why WSL2

Most development tools in the lab ecosystem -- SSH, Python toolchains, Git, `uv`, and terminal-based utilities -- are designed for Linux. WSL2 lets you run a full Linux environment directly on your Windows machine without dual-booting or a virtual machine.

Key points:

- **Real Linux kernel.** WSL2 ships a lightweight Linux kernel managed by Windows, so you get native syscall compatibility. Tools like `ssh-keygen`, `rsync`, and shell scripts work exactly as they would on a Linux server.
- **VS Code integration.** VS Code's WSL extension connects seamlessly to your Linux filesystem, giving you a native editor experience with Linux tooling underneath.
- **Required for lab workflows.** The [Python Environment Setup](python-environment-setup.md) guide assumes a Linux shell, and SSH connections to OSC are simplest from a Linux terminal.

!!! note "macOS users"
    macOS is Unix-based and does not need WSL. If you are on macOS, skip this page and go directly to [VS Code Setup](vscode-setup.md).

---

## Installation

=== "Windows 11"

    Windows 11 includes WSL2 support out of the box. A single command handles everything:

    ```powershell
    wsl --install
    ```

    This command:

    1. Enables the "Virtual Machine Platform" and "Windows Subsystem for Linux" features
    2. Downloads and installs the latest Linux kernel
    3. Sets WSL2 as the default version
    4. Installs **Ubuntu** as the default distribution

    After the command completes, **restart your computer** when prompted.

    !!! tip "Run as Administrator"
        Open **Windows Terminal** or **PowerShell** as Administrator (right-click, "Run as administrator") before running `wsl --install`.

=== "Windows 10"

    Windows 10 (version 1903+ with Build 18362+) supports WSL2, but requires manual feature enablement.

    **Step 1 -- Enable WSL and Virtual Machine Platform:**

    Open PowerShell as Administrator and run:

    ```powershell
    # Enable Windows Subsystem for Linux
    dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart

    # Enable Virtual Machine Platform (required for WSL2)
    dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart
    ```

    **Restart your computer** after both commands complete.

    **Step 2 -- Install the WSL2 Linux kernel update:**

    Download and run the kernel update package from Microsoft:

    [WSL2 Linux kernel update package for x64 machines](https://wslstorestorage.blob.core.windows.net/wslblob/wsl_update_x64.msi)

    **Step 3 -- Set WSL2 as default:**

    ```powershell
    wsl --set-default-version 2
    ```

    **Step 4 -- Install Ubuntu:**

    Open the **Microsoft Store**, search for **Ubuntu**, and click **Install**. The latest LTS release (e.g., Ubuntu 24.04) is recommended.

    After installation, launch Ubuntu from the Start menu to complete first-time setup.

    !!! warning "Check your Windows version"
        Run `winver` to verify your build number. If you are on an older build that does not support WSL2, update Windows first via Settings > Update & Security > Windows Update.

---

## Initial Configuration

When Ubuntu launches for the first time, it prompts you to create a Linux user account. This is separate from your Windows account.

1. **Set a username** -- use something short and lowercase (e.g., your OSU name.N):

    ```
    Enter new UNIX username: buckeye42
    ```

2. **Set a password** -- you will need this for `sudo` commands. It does not display as you type.

3. **Update system packages:**

    ```bash
    sudo apt update && sudo apt upgrade -y
    ```

    Run this periodically (every few weeks) to keep your system packages current.

4. **Verify WSL2 is active:**

    Open a new PowerShell or Windows Terminal window (not inside WSL) and run:

    ```powershell
    wsl -l -v
    ```

    You should see output like:

    ```
      NAME      STATE           VERSION
    * Ubuntu    Running         2
    ```

    The `VERSION` column must show `2`. If it shows `1`, convert it:

    ```powershell
    wsl --set-version Ubuntu 2
    ```

---

## Filesystem Guidance

This is one of the most important performance decisions for your WSL setup.

!!! danger "Do NOT keep code on `/mnt/c/`"
    The `/mnt/c/` mount gives WSL access to your Windows `C:\` drive, but it goes through a **9P protocol translation layer** that is dramatically slower than native Linux I/O. File operations (Git, Python imports, `pip install`, build tools) can be **5-10x slower** on `/mnt/c/` compared to the WSL native filesystem.

**Store all code on the WSL native filesystem:**

```bash
# Create a projects directory in your WSL home
mkdir -p ~/projects

# Clone repos here
cd ~/projects
git clone https://github.com/your-org/your-repo.git
```

Your WSL home directory (`~/`) lives on an ext4 virtual disk managed by WSL. It is fast, supports Linux permissions correctly, and avoids the line-ending and permission issues that plague `/mnt/c/`.

| Location | Path example | Speed | Use for |
|----------|-------------|-------|---------|
| WSL native | `~/projects/my-repo` | Fast | All code, venvs, builds |
| Windows mount | `/mnt/c/Users/You/Documents/` | Slow (9P) | Accessing Windows-only files when needed |

!!! tip "Accessing WSL files from Windows"
    You can browse your WSL filesystem from Windows Explorer at `\\wsl$\Ubuntu\home\your-username\`. This is useful for dragging files into Windows applications, but do your actual development work from within WSL.

For detailed instructions on setting up Python, `uv`, and project virtual environments on the WSL native filesystem, see the [Python Environment Setup](python-environment-setup.md) guide.

---

## Windows Terminal / WezTerm

You need a good terminal emulator to work comfortably in WSL. Two solid options:

### Windows Terminal

Windows Terminal is Microsoft's modern terminal with tabs, split panes, and GPU-accelerated rendering.

=== "Windows 11"

    Windows Terminal is **pre-installed** on Windows 11. Open it from the Start menu or press ++win+x++ and select "Terminal."

=== "Windows 10"

    Install from the [Microsoft Store](https://aka.ms/terminal). Search for **Windows Terminal** and click Install.

After installation, Windows Terminal automatically detects your WSL distributions and adds them as profile options. Click the dropdown arrow next to the tab bar to open a new Ubuntu tab.

**Recommended settings** (open with ++ctrl+comma++):

- Set **Ubuntu** as the default profile so new tabs open in WSL
- Set the starting directory to your WSL home: `//wsl$/Ubuntu/home/your-username`
- Enable "Automatically copy selection to clipboard"

### WezTerm

[WezTerm](https://wezfurlong.org/wezterm/) is a cross-platform terminal written in Rust with built-in multiplexing (similar to tmux), ligature support, and Lua-based configuration.

Download the installer from [wezterm.org/installation](https://wezterm.org/installation.html).

WezTerm can launch WSL directly. Add this to your `~/.wezterm.lua` config:

```lua
local wezterm = require("wezterm")
local config = wezterm.config_builder()

config.default_domain = "WSL:Ubuntu"
config.font_size = 11.0
config.color_scheme = "Catppuccin Mocha"

return config
```

!!! tip "Why WezTerm?"
    WezTerm's built-in multiplexer means you can split panes and create tabs without needing tmux. This is especially handy if you want `mkdocs serve` running in one pane and your shell in another. It also works identically on Windows, macOS, and Linux if you use multiple machines.

---

## VS Code Integration

VS Code integrates seamlessly with WSL via the Remote - WSL extension. Install the extension, then open a WSL terminal and run `code .` to launch VS Code connected to your WSL environment. For full VS Code setup instructions, see the [VS Code Setup Guide](vscode-setup.md).

---

## Next Steps

With WSL2 configured, continue setting up your development environment:

- [VS Code Setup](vscode-setup.md) -- Install and configure VS Code with recommended settings
- [Python Environment Setup](python-environment-setup.md) -- Set up `uv`, virtual environments, and project workflows on WSL
- [AI Coding Assistants](ai-coding-assistants.md) -- Configure GitHub Copilot and Claude Code for VS Code
