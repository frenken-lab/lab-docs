---
tags:
  - OSC
  - SSH
  - GPU
---
<!-- last-reviewed: 2026-05-09 -->
# Troubleshooting Guide

Common issues and solutions for working on OSC.

## Connection Issues

### SSH Connection Failed

**Problem:** Cannot connect to OSC
```
ssh: connect to host pitzer.osc.edu port 22: Connection refused
```

**Solutions:**

1. **Check if on OSU network or VPN**
   ```bash
   # Install and connect to OSU VPN
   # Download from: https://osuitsm.service-now.com/
   ```

2. **Verify hostname**
   ```bash
   # Correct hostname:
   pitzer.osc.edu

   # Not: pitzer.org or pitzer.com
   ```

3. **Check system status**
   - Visit: https://www.osc.edu/resources/system-status

### SSH Key Authentication Failed

**Problem:** Permission denied with SSH key
```
Permission denied (publickey,gssapi-keyex,gssapi-with-mic)
```

**Solutions:**

1. **Verify key is added to OSC**
   - Log into my.osc.edu
   - Check "SSH Public Keys"
   - Wait 10 minutes after adding

2. **Check key permissions**
   ```bash
   chmod 700 ~/.ssh
   chmod 600 ~/.ssh/id_ed25519
   chmod 644 ~/.ssh/id_ed25519.pub
   ```

3. **Verify SSH config**
   ```bash
   cat ~/.ssh/config
   # Should have:
   # IdentityFile ~/.ssh/id_ed25519
   ```

4. **Test with verbose output**
   ```bash
   ssh -v pitzer
   # Look for which key is being tried
   ```

### VS Code Remote Connection Hangs

**Problem:** "Setting up SSH Host..." hangs

See [Remote Development](../osc-basics/osc-remote-development.md) for the full VS Code setup. If the remote server is stale, remove `~/.vscode-server` and reconnect.

## Module and Environment Issues

### Module Not Found

**Problem:** `module: command not found`

**Solution:**
```bash
# Module system not initialized
# Add to ~/.bashrc:
source /etc/profile.d/modules.sh

# Or reinitialize shell
bash --login
```

### Virtual Environment Won't Activate

**Problem:** Environment doesn't activate

**Solutions:**

1. **Verify path exists**
   ```bash
   # uv (recommended) — .venv/ in project root
   ls .venv/bin/activate

   # pip+venv — ~/venvs/ convention
   ls ~/venvs/myproject/bin/activate
   ```

2. **Recreate if corrupted**
   ```bash
   # uv (recommended)
   rm -rf .venv
   uv venv --python /apps/python/3.12/bin/python3

   # pip+venv
   rm -rf ~/venvs/myproject
   module load python/3.12
   python -m venv ~/venvs/myproject
   ```

3. **Check Python module loaded** (pip+venv only)
   ```bash
   module list | grep python
   module load python/3.12
   ```

## GPU Issues

### CUDA Not Available

**Problem:** `torch.cuda.is_available()` returns False

Quick checks: verify you're on a GPU node (`nvidia-smi`) and check `torch.cuda.is_available()`. If you installed PyTorch from PyPI, you do **not** need `module load cuda` -- PyPI wheels bundle CUDA. Only load a CUDA module if you're compiling custom CUDA extensions. For full diagnostic steps and reinstall commands, see [PyTorch & GPU Setup -- Troubleshooting](../ml-workflows/pytorch-setup.md#troubleshooting).

### CUDA Out of Memory

**Problem:** `RuntimeError: CUDA out of memory`

Start by reducing batch size or clearing the cache with `torch.cuda.empty_cache()`. For a complete list of solutions (gradient accumulation, mixed precision, gradient checkpointing), see [PyTorch & GPU Setup — CUDA Out of Memory](../ml-workflows/pytorch-setup.md#cuda-out-of-memory).

### GPU Utilization Low

**Problem:** GPU usage < 50% during training

Increase `num_workers` in your DataLoader to match `--cpus-per-task`, enable `pin_memory=True`, and use a larger batch size if memory allows. If that still doesn’t help, profile the pipeline and compare it with [PyTorch & GPU Setup — Slow Training](../ml-workflows/pytorch-setup.md#slow-training).

## Job Submission Issues

### Job Pending Forever

**Problem:** Job stuck in PD (pending) state

**Check reason:**
```bash
squeue -u $USER
# Look at REASON column
```

**Common reasons and solutions:**

1. **QOSMaxGRESPerUser**
   - Too many GPU jobs running
   - Wait or cancel old jobs: `scancel <job_id>`

2. **Resources**
   - Requesting too many resources
   - Reduce resources requested

3. **ReqNodeNotAvail**
   - Maintenance window approaching
   - Reduce time limit or wait

4. **Priority**
   - Other jobs have higher priority
   - Wait in queue

### Job Fails Immediately

**Problem:** Job exits with error immediately

**Solutions:**

1. **Check error logs**
   ```bash
   cat logs/job_<jobid>.err
   tail -50 logs/job_<jobid>.out
   ```

2. **Common causes:**

   **Module not loaded:**
   ```bash
   # Add to job script
   module load python/3.12
   ```

   **Environment not activated:**
   ```bash
   source .venv/bin/activate  # uv (recommended)
   # or: source ~/venvs/myproject/bin/activate  # pip+venv
   ```

   **File not found:**
   ```bash
   # Use absolute paths
   python ~/projects/myproject/train.py
   ```

   **Permission denied:**
   ```bash
   chmod +x script.sh
   ```

3. **Test interactively first**
   ```bash
   srun -p debug --pty bash
   # Run commands manually
   ```

## File System Issues

### Disk Quota Exceeded

**Problem:** Cannot write files
```
Disk quota exceeded
```

**Solutions:**

1. **Check quota**
   ```bash
   quota -s
   ```

2. **Find large directories**
   ```bash
   du -sh ~/*/  | sort -hr | head -10
   ```

3. **Clean up**
   ```bash
   # Remove old virtual environments
   rm -rf ~/venvs/old_project
   
   # Clean pip cache
   pip cache purge
   
   # Clean conda cache
   conda clean --all
   
   # Remove old checkpoints
   rm checkpoints/epoch_*.pth
   
   # Clear Python cache
   find . -type d -name __pycache__ -exec rm -rf {} +
   ```

4. **Use scratch space**
   ```bash
   # Move large data to scratch
   mv large_dataset/ /fs/scratch/PAS1234/$USER/
   ```

## Data Transfer Issues

### rsync/scp Fails

**Problem:** Transfer interrupted or failed

**Solutions:**

1. **Use rsync with resume**
   ```bash
   rsync -avz --progress --partial source/ pitzer:~/dest/
   ```

2. **Check disk space on destination**
   ```bash
   ssh pitzer
   quota -s
   ```

3. **Check network connection**
   ```bash
   ping pitzer.osc.edu
   ```

4. **Use tmux for long transfers**
   ```bash
   tmux new -s transfer
   rsync -avz source/ pitzer:~/dest/
   # Ctrl+b, then d to detach
   ```

### Slow File Transfer

Use `rsync -z` for compression, or archive first if you’re moving many small files. For long transfers, keep them in `tmux` so a disconnect does not kill the copy.

## Python/PyTorch Issues

### Import Error

**Problem:** `ModuleNotFoundError: No module named 'torch'`

**Solutions:**

1. **Verify environment activated**
   ```bash
   which python
   # Should point to venv, not system Python
   ```

2. **Reinstall package**
   ```bash
   pip install torch
   ```

3. **Check Python version**
   ```bash
   python --version
   # Should match venv Python version
   ```

## Performance Issues

For GPU performance troubleshooting (slow training, profiling, DataLoader optimization), see [PyTorch & GPU Setup](../ml-workflows/pytorch-setup.md#troubleshooting).

### Out of Memory (RAM)

**Problem:** Job killed due to RAM

**Solutions:**

1. **Request more memory**
   ```bash
   #SBATCH --mem=64G  # Instead of 32G
   ```

2. **Reduce data in memory**
   ```python
   # Don't load entire dataset at once
   # Use generators or data loaders
   ```

3. **Monitor memory usage**
   ```bash
   top -u $USER
   ```
