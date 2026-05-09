---
tags:
  - OSC
  - SSH
---
<!-- last-reviewed: 2026-03-04 -->
# Remote Development on OSC

Use VS Code Remote-SSH to work on OSC as if the cluster were a local machine.

## Prerequisites

- [VS Code installed](../getting-started/vscode-setup.md)
- [Remote-SSH extension installed](../getting-started/vscode-extensions.md#1-remote-ssh)
- [OSC account and SSH configured](osc-ssh-connection.md)

## Connecting to OSC

### Method 1: Command Palette

1. Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on macOS)
2. Type "Remote-SSH: Connect to Host"
3. Select `pitzer` from your SSH config
4. A new VS Code window opens connected to OSC

### Method 2: Remote Explorer

1. Click the Remote Explorer icon in the sidebar (><)
2. Select "SSH Targets" from dropdown
3. Click the connect icon next to `pitzer`

### Method 3: Command Line

```bash
code --remote ssh-remote+pitzer /path/to/directory
```

### First Connection

VS Code installs the server on first connect. After that, reconnects are much faster.

## Installing Extensions Remotely

Install the extensions you actually use on the remote server. For recommended extensions, see [VS Code Extensions](../getting-started/vscode-extensions.md).

## File Transfer

Use drag-and-drop or right-click download for small files. For larger transfers, see the [File Transfer Guide](osc-file-transfer.md).

## Port Forwarding

VS Code usually detects ports automatically. If not, use the **PORTS** panel and forward the port manually.

```bash
# In VS Code terminal on OSC
module load python/3.12
jupyter notebook --no-browser --port=8888
```

## Best Practices

### Use Login Nodes for Light Work

Login nodes are fine for editing, git, job submission, and AI coding tools. Do not run long builds, large test suites, or GPU work there.

### Use Compute Nodes for Heavy Work

Use `sinteractive` to get your own compute node from the VS Code terminal:

```bash
# CPU-only (for builds, tests, preprocessing)
sinteractive -A PAS1234 -c 4 -t 02:00:00

# With GPU (for training, debugging GPU code)
sinteractive -A PAS1234 -c 4 -g 1 -t 01:00:00
```

Your home directory is the same on login and compute nodes. Type `exit` when you are done.

For longer unattended runs, use batch jobs:

```bash
sbatch job_script.sh
```

For full details, see the [Job Submission Guide](../working-on-osc/osc-job-submission.md).

### Save and Recover

- Enable auto-save
- Commit frequently
- Use `tmux` or `screen` if you want terminal persistence

## Advanced Tips

### Using tmux for Persistent Sessions

```bash
# Start tmux session
tmux new -s work

# Detach: Ctrl+b, then d
# Reattach: tmux attach -t work
```

This keeps your session alive even if VS Code disconnects.

### SSH Config for Multiple Login Nodes

```ssh-config
# Primary login
Host pitzer
    HostName pitzer.osc.edu
    User your.osuusername

# Specific login node (if needed)
Host pitzer01
    HostName pitzer-login01.osc.edu
    User your.osuusername
```

## Troubleshooting

- If connection setup hangs, confirm `ssh pitzer` works and try removing `~/.vscode-server`
- If Python is missing, load `python/3.12` and re-select the interpreter
- If ports do not forward, add them manually in the **PORTS** panel
- If the terminal feels unstable, simplify shell startup files
- If remote performance is slow, install only the extensions you need

## Next Steps

- Set up [PyTorch on OSC](../ml-workflows/pytorch-setup.md)
- Explore [Job Submission Guide](../working-on-osc/osc-job-submission.md)
- Read [ML Project Workflow](../ml-workflows/ml-workflow.md)

## Resources

- [VS Code Remote-SSH Documentation](https://code.visualstudio.com/docs/remote/ssh)
- [OSC Documentation](https://www.osc.edu/resources/technical_support/supercomputers)
- [Troubleshooting Guide](../resources/troubleshooting.md)
