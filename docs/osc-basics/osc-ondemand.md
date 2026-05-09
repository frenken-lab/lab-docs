---
tags:
  - OSC
  - Jupyter
  - OnDemand
---
<!-- last-reviewed: 2026-02-26 -->
# OSC OnDemand Portal

OSC OnDemand gives you browser access to OSC resources for interactive apps, files, job monitoring, and a web terminal.

## Accessing OnDemand

1. Open [https://ondemand.osc.edu](https://ondemand.osc.edu) in any modern browser.
2. Log in with your OSC credentials (your OSU `name.#` and OSC password).
3. You land on the OnDemand dashboard with links to apps, jobs, files, and clusters.

!!! note "Active OSC account required"
    You must have an active OSC account and be a member of at least one project before you can log in. If you haven't set up your account yet, follow the [Account Setup](osc-account-setup.md) guide first.

## Interactive Apps

OnDemand launches SLURM-backed interactive sessions on compute nodes:

| App | Use |
|---|---|
| Jupyter Notebook/Lab | Python notebooks on compute nodes |
| RStudio Server | R development environment |
| VS Code Server | Browser-based VS Code |
| Virtual Desktop | Full Linux desktop |

Each app launches a SLURM job behind the scenes, so your session uses real compute resources.

## Launching a Jupyter Session

Jupyter is the most commonly used OnDemand app in the lab. Here is the step-by-step process:

### 1. Open and configure Jupyter

| Field | What to enter | Example |
|-------|---------------|---------|
| **Project account** | Your OSC project code | `PAS1234` |
| **Cluster** | Cluster to run on | Pitzer |
| **Partition** | Node type / queue | `gpu`, `serial`, `debug` |
| **Number of cores** | CPU cores | 4 |
| **Memory (GB)** | RAM | 16 |
| **Number of GPUs** | GPUs to request | 1 |
| **Walltime (hours)** | Session duration | 4 |
| **Jupyter type** | Notebook Classic or JupyterLab | JupyterLab |

!!! tip "Use the `debug` partition for quick prototyping"
    The `debug` partition has a short maximum walltime (typically 1 hour) but jobs usually start within seconds instead of waiting in the queue. This is ideal for testing code changes, verifying that your environment works, or running small experiments.

### 2. Launch and connect

Click **Launch**, wait for the queue to move to running, then open **Connect to Jupyter**.

### 3. Select a kernel

If your environment does not appear in the kernel picker, install `ipykernel` inside it and register the kernel:

```bash
source ~/envs/myenv/bin/activate
pip install ipykernel
python -m ipykernel install --user --name myenv --display-name "My Project (myenv)"
```

For more on environment management, see [Environment Management](../working-on-osc/osc-environment-management.md).

## File Management

Use the built-in file manager for small transfers and quick edits.

### Basics

- Open **Files** and choose Home, Project, or Scratch
- Upload small files by clicking **Upload** or dragging them in
- Download files from the file list
- Click a text file to make quick edits in the browser

!!! info "For bulk or large transfers, use dedicated tools"
    Use SCP, rsync, or VS Code for anything over about 100 MB or for whole directories. See the [File Transfer Guide](osc-file-transfer.md).

## Job Monitoring

OnDemand lets you inspect and cancel SLURM jobs from the browser.

### Basics

- Open **Jobs** and then **Active Jobs**
- View job details, output files, and working directories
- Use **Delete** to cancel a running or queued job

!!! info "For detailed job management"
    The OnDemand job viewer covers the basics, but for advanced operations like job arrays, job dependencies, and resource optimization, see the [Job Submission Guide](../working-on-osc/osc-job-submission.md).

## OnDemand vs SSH

Use OnDemand for browser-based tasks and SSH + VS Code for day-to-day development.

| Feature | OnDemand | SSH + VS Code |
|---|---|---|
| Setup | Browser only | SSH keys + VS Code |
| Jupyter | Native | Port forwarding needed |
| Editing | Basic browser editor | Full IDE |
| Terminal | Web terminal | Integrated terminal |
| Best for | Quick tasks, file browsing | Daily development |

For setting up SSH-based access, see the [SSH Connection Guide](osc-ssh-connection.md) and [Remote Development](osc-remote-development.md).

## Tips

!!! tip "Close idle sessions"
    Interactive apps keep charging core-hours until you delete them.

!!! warning "Save frequently"
    Browser sessions can time out and drop unsaved notebook state.

!!! tip "Use shell access for quick terminal work"
    The **Clusters** menu gives you a browser terminal on a login node.

## Next Steps

- [File Transfer Guide](osc-file-transfer.md) -- upload and download files efficiently with SCP, rsync, or SFTP
- [Job Submission Guide](../working-on-osc/osc-job-submission.md) -- write SLURM scripts and manage batch jobs from the command line
- [Notebook-to-Script Workflow](../ml-workflows/ml-workflow.md#notebook-to-script-workflow) -- convert Jupyter prototypes into production-ready Python scripts for large-scale experiments
