<!-- last-reviewed: 2026-02-26 -->
# SSH Connection Guide

This guide will help you set up SSH connections to OSC for secure and convenient access to the clusters.

!!! note "Windows users: run SSH from WSL"
    All SSH commands in this guide should be run inside your WSL terminal, not PowerShell or Command Prompt. If you haven't set up WSL yet, see the [WSL Setup Guide](../getting-started/wsl-setup.md) first.

## Basic SSH Connection

### Quick Start

Connect to OSC with this command:

```bash
ssh username@pitzer.osc.edu
```

Replace `username` with your OSU name.# (e.g., `buckeye.1`).

### Available Clusters

```bash
ssh username@pitzer.osc.edu
```

## Configuring SSH for Convenience

### SSH Config File

Create or edit `~/.ssh/config` to simplify connections:

**On Linux/macOS:**
```bash
nano ~/.ssh/config
```

**On Windows:**
```powershell
notepad $HOME\.ssh\config
```

### Basic Configuration

Add this to your SSH config file:

```ssh-config
# OSC Pitzer
Host pitzer
    HostName pitzer.osc.edu
    User your.osuusername
    ServerAliveInterval 60
    ServerAliveCountMax 3
```

Replace `your.osuusername` with your actual OSU username (e.g., `buckeye.1`).

Now you can connect simply with:
```bash
ssh pitzer
```

### Advanced Configuration with SSH Keys

For password-less login (after [setting up SSH keys](#ssh-keys-setup)):

```ssh-config
Host pitzer
    HostName pitzer.osc.edu
    User your.osuusername
    IdentityFile ~/.ssh/id_ed25519
    ServerAliveInterval 60
    ServerAliveCountMax 3
    Compression yes
    ForwardAgent no
```

### Configuration Options Explained

- **ServerAliveInterval 60**: Sends keep-alive messages every 60 seconds
- **ServerAliveCountMax 3**: Disconnects after 3 failed keep-alives
- **Compression yes**: Enables data compression (useful for slow connections)
- **ForwardAgent no**: Disables SSH agent forwarding (security best practice)
- **IdentityFile**: Specifies which SSH key to use

## SSH Keys Setup

### Why Use SSH Keys?

- **No password typing**: Automatic authentication
- **More secure**: Harder to compromise than passwords
- **Required for VS Code Remote**: Makes remote development seamless

### Generate SSH Key Pair

If you haven't already:

```bash
# Generate ED25519 key (recommended)
ssh-keygen -t ed25519 -C "your.email@osu.edu"

# Or generate RSA key (alternative)
ssh-keygen -t rsa -b 4096 -C "your.email@osu.edu"
```

Press Enter to accept the default location, then optionally enter a passphrase.

### Add Key to OSC

1. Display your public key:
   ```bash
   cat ~/.ssh/id_ed25519.pub
   # Or for RSA: cat ~/.ssh/id_rsa.pub
   ```

2. Copy the entire output

3. Log into [my.osc.edu](https://my.osc.edu)

4. Go to "My Account" → "Manage SSH Public Keys"

5. Add your public key

6. Wait 5-10 minutes for propagation

### Test SSH Key Authentication

```bash
ssh pitzer
```

You should connect without entering your OSU password (though you may need your SSH key passphrase if you set one).

## Using SSH Agent (Optional)

If you set a passphrase on your SSH key, use SSH agent to avoid typing it repeatedly:

### Linux/macOS

```bash
# Start SSH agent
eval "$(ssh-agent -s)"

# Add your key
ssh-add ~/.ssh/id_ed25519

# Verify it was added
ssh-add -l
```

### Windows (PowerShell)

```powershell
# Start SSH agent service
Start-Service ssh-agent

# Add your key
ssh-add $HOME\.ssh\id_ed25519
```

## Connection from Off-Campus

### Option 1: OSU VPN (Recommended)

1. Install [Cisco AnyConnect](https://www.osu.edu/downloads/)
2. Connect to OSU VPN
3. SSH to OSC normally

### Option 2: Direct Connection via Duo 2FA

OSC systems are accessible from off-campus without VPN, but you must authenticate with Duo two-factor authentication at each login.

## Port Forwarding

Forward ports for accessing services running on OSC (e.g., Jupyter, TensorBoard):

### Local Port Forwarding

```bash
# Forward remote port 8888 to local port 8888
ssh -L 8888:localhost:8888 pitzer

# Forward with custom local port
ssh -L 9999:localhost:8888 pitzer
```

### In SSH Config

```ssh-config
Host pitzer-jupyter
    HostName pitzer.osc.edu
    User your.osuusername
    LocalForward 8888 localhost:8888
```

Then connect with:
```bash
ssh pitzer-jupyter
```

### Dynamic Port Forwarding (SOCKS Proxy)

```bash
ssh -D 8080 pitzer
```

## File Transfer

For SCP, SFTP, rsync, and other transfer methods, see the [File Transfer Guide](osc-file-transfer.md).

## Troubleshooting

### Connection Timeout

**Problem**: Connection times out or hangs
```
ssh: connect to host pitzer.osc.edu port 22: Operation timed out
```

**Solutions**:
- Check if you're on OSU network or VPN
- Verify OSC system status: [https://www.osc.edu/resources/system-status](https://www.osc.edu/resources/system-status)
- Try again in a few minutes (login nodes rotate)

### Permission Denied (publickey)

**Problem**: SSH key authentication fails
```
Permission denied (publickey,gssapi-keyex,gssapi-with-mic).
```

**Solutions**:
- Verify SSH key is added to OSC: [my.osc.edu](https://my.osc.edu) → SSH Keys
- Check key permissions:
  ```bash
  chmod 600 ~/.ssh/id_ed25519
  chmod 644 ~/.ssh/id_ed25519.pub
  chmod 700 ~/.ssh
  ```
- Wait 10 minutes after adding key for propagation
- Verify correct key with `ssh-add -l`

### Connection Closes Unexpectedly

**Problem**: Connection drops after period of inactivity

**Solution**: Add to SSH config:
```ssh-config
ServerAliveInterval 60
ServerAliveCountMax 3
```

### SSH Key Not Working

**Problem**: Still prompted for password despite SSH key

**Solutions**:
1. Verify public key is on OSC:
   ```bash
   ssh pitzer 'cat ~/.ssh/authorized_keys'
   ```

2. Check SSH config uses correct key:
   ```ssh-config
   IdentityFile ~/.ssh/id_ed25519
   ```

3. Test with verbose output:
   ```bash
   ssh -v pitzer
   ```

### Cannot Create SSH Config File

**Windows Issue**: `~/.ssh` directory doesn't exist

**Solution**:
```powershell
mkdir $HOME\.ssh
```

## Next Steps

- [Set Up Remote Development with VS Code](osc-remote-development.md)
- [Learn File Transfer Methods](osc-file-transfer.md)
- [Job Submission Guide](../working-on-osc/osc-job-submission.md)

## Additional Resources

- [OSC Getting Connected](https://www.osc.edu/resources/getting_started/getting_connected)
- [SSH Config File Documentation](https://www.ssh.com/academy/ssh/config)
- [Troubleshooting Guide](../resources/troubleshooting.md)
