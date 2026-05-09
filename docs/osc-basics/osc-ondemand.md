---
tags:
  - OSC
  - Jupyter
  - OnDemand
---
<!-- last-reviewed: 2026-02-26 -->
# OSC OnDemand Portal

OSC OnDemand is a web-based portal that provides browser access to Ohio Supercomputer Center resources without requiring SSH, terminal commands, or local software installation. Through OnDemand you can launch interactive applications (Jupyter, RStudio, VS Code), manage files, monitor jobs, and open a web-based terminal -- all from a standard web browser at [ondemand.osc.edu](https://ondemand.osc.edu).

## Accessing OnDemand

1. Open [https://ondemand.osc.edu](https://ondemand.osc.edu) in any modern browser.
2. Log in with your OSC credentials (your OSU `name.#` and OSC password).
3. After authentication you land on the OnDemand dashboard, which shows a top navigation bar with links to Interactive Apps, Jobs, Files, Clusters (shell access), and more.

!!! note "Active OSC account required"
    You must have an active OSC account and be a member of at least one project before you can log in. If you haven't set up your account yet, follow the [Account Setup](osc-account-setup.md) guide first.

## Interactive Apps

OnDemand's main strength is one-click access to interactive compute sessions that run on dedicated compute nodes (not login nodes). The following apps are available:

| App | Description | GPU Support |
|-----|-------------|-------------|
| Jupyter Notebook/Lab | Python notebooks on compute nodes | Yes |
| RStudio Server | R development environment | No |
| VS Code Server | Browser-based VS Code | Yes |
| Virtual Desktop | Full Linux desktop (VNC) | Yes |

Each app launches a SLURM job behind the scenes, so your work runs on real compute resources with the cores, memory, and GPUs you request.

## Launching a Jupyter Session

Jupyter is the most commonly used OnDemand app in the lab. Here is the step-by-step process:

### 1. Open the Jupyter app

From the top navigation bar, click **Interactive Apps** and select **Jupyter**.

### 2. Fill in the session form

| Field | What to enter | Example |
|-------|---------------|---------|
| **Project account** | Your lab's OSC project code | `PAS1234` |
| **Cluster** | Which cluster to run on | Pitzer (recommended for GPU work) |
| **Partition** | Node type / queue | `gpu`, `serial`, `debug` |
| **Number of cores** | CPU cores for your session | 4 |
| **Memory (GB)** | RAM per node | 16 |
| **Number of GPUs** | GPUs to request (partition must support GPUs) | 1 |
| **Walltime (hours)** | Maximum session duration | 4 |
| **Jupyter type** | Notebook Classic or JupyterLab | JupyterLab |

!!! tip "Use the `debug` partition for quick prototyping"
    The `debug` partition has a short maximum walltime (typically 1 hour) but jobs usually start within seconds instead of waiting in the queue. This is ideal for testing code changes, verifying that your environment works, or running small experiments.

### 3. Launch and connect

1. Click **Launch** at the bottom of the form.
2. Your request enters the SLURM queue. The card will show "Queued" and then "Running" once resources are allocated.
3. When the session is running, click **Connect to Jupyter** to open JupyterLab (or Jupyter Notebook) in a new browser tab.

### 4. Select a kernel

Inside JupyterLab, click the kernel picker in the top-right corner of a notebook. You will see every Python environment that has `ipykernel` installed.

!!! tip "Make your venv available as a Jupyter kernel"
    If your virtual environment doesn't appear in the kernel list, install `ipykernel` inside it:

    ```bash
    # Activate your venv first
    source ~/envs/myenv/bin/activate

    # Install ipykernel and register the kernel
    pip install ipykernel
    python -m ipykernel install --user --name myenv --display-name "My Project (myenv)"
    ```

    The new kernel will appear the next time you open or refresh a Jupyter session. For more on environment management, see [Environment Management](../working-on-osc/osc-environment-management.md).

## File Management

OnDemand includes a built-in file manager that lets you browse, upload, download, and edit files without leaving your browser.

### Navigating the file manager

1. In the top navigation bar, click **Files**.
2. Select a starting location: **Home Directory**, **Project**, or **Scratch**.
3. Click into folders to navigate, or use the breadcrumb trail at the top to jump back.

### Uploading and downloading

- **Upload:** Click the **Upload** button at the top of the file manager, then select files or drag-and-drop them into the dialog. Uploads work well for files under ~100 MB.
- **Download:** Select the checkbox next to one or more files, then click **Download**. The browser will download a single file directly or a zip archive for multiple files.

### Editing files in the browser

Click any text file to open it in OnDemand's built-in editor. The editor supports syntax highlighting and basic editing -- useful for quick config or script changes.

!!! info "For bulk or large transfers, use dedicated tools"
    The OnDemand file manager is convenient for small files, but for anything over 100 MB or for syncing entire directories, use SCP, rsync, or VS Code drag-and-drop. See the [File Transfer Guide](osc-file-transfer.md) for details.

## Job Monitoring

OnDemand provides a web interface for monitoring and managing your SLURM jobs.

### Viewing active jobs

1. Click **Jobs** in the top navigation bar, then select **Active Jobs**.
2. The table shows all your running and queued jobs, including:
    - Job ID
    - Job name
    - Account (project code)
    - Status (Running, Pending, Completing)
    - Cluster and partition
    - Time used / time remaining
    - Number of nodes and cores

### Managing jobs

- **View details:** Click a job ID to see the full job submission script, output file path, working directory, and resource usage.
- **View output:** Click the folder icon to open the job's working directory in the file manager, where you can inspect `slurm-<jobid>.out` and other output files.
- **Cancel a job:** Click the red **Delete** button next to a running or queued job to cancel it immediately. This is equivalent to running `scancel <jobid>` in the terminal.

!!! info "For detailed job management"
    The OnDemand job viewer covers the basics, but for advanced operations like job arrays, job dependencies, and resource optimization, see the [Job Submission Guide](../working-on-osc/osc-job-submission.md).

## OnDemand vs SSH Comparison

Both OnDemand and SSH-based workflows are fully supported at OSC. Choose the one that fits the task at hand -- many lab members use both depending on the situation.

| Feature | OnDemand | SSH + VS Code |
|---------|----------|---------------|
| Setup required | Browser only | SSH keys, VS Code, extensions |
| Jupyter notebooks | Native support | Port forwarding needed |
| File editing | Basic browser editor | Full VS Code with extensions |
| Terminal access | Yes (web terminal) | Yes (integrated terminal) |
| GPU jobs | Via interactive apps | Via SLURM commands |
| Best for | Quick tasks, Jupyter, file browsing | Daily development, debugging |

For setting up SSH-based access, see the [SSH Connection Guide](osc-ssh-connection.md) and [Remote Development](osc-remote-development.md).

## Tips

!!! tip "Don't leave idle sessions running"
    Interactive app sessions consume your project's core-hour allocation the entire time they are running, even if you are not actively using them. Close sessions you no longer need by going to **My Interactive Sessions** and clicking **Delete** on idle cards.

!!! warning "Browser sessions can time out -- save frequently"
    If your browser tab is inactive for too long, the connection to the Jupyter server may drop. Your compute job keeps running on the cluster, but you may lose unsaved notebook state. Save your work frequently with ++ctrl+s++ and consider enabling JupyterLab's autosave.

!!! tip "Use the shell app for quick terminal access"
    If you just need a terminal without setting up SSH, click **Clusters** in the top navigation bar and select a cluster (e.g., **Pitzer Shell Access**). This opens a web-based terminal connected to a login node -- handy for checking job status, editing configs, or running quick commands.

## Next Steps

- [File Transfer Guide](osc-file-transfer.md) -- upload and download files efficiently with SCP, rsync, or SFTP
- [Job Submission Guide](../working-on-osc/osc-job-submission.md) -- write SLURM scripts and manage batch jobs from the command line
- [Notebook-to-Script Workflow](../ml-workflows/notebook-to-script.md) -- convert Jupyter prototypes into production-ready Python scripts for large-scale experiments
