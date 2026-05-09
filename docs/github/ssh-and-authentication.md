---
status: new
tags:
  - Git
  - GitHub
  - SSH
---
<!-- last-reviewed: 2026-03-30 -->
# SSH & Authentication

| | |
|---|---|
| **Audience** | All lab members |
| **Prerequisites** | GitHub account, terminal access (WSL, Mac Terminal, or Linux) |

---

## SSH Keys for GitHub

SSH keys let you authenticate to GitHub without typing your password every time you push or pull. You generate a key pair (private + public), keep the private key on your machine, and upload the public key to GitHub.

### Generate a Key Pair

=== "Windows (WSL)"

    Run these commands inside your **WSL terminal**, not PowerShell or Command Prompt.

    ```bash
    ssh-keygen -t ed25519 -C "your.email@example.com"
    ```

    When prompted:

    - **File location:** press ++enter++ to accept the default (`~/.ssh/id_ed25519`)
    - **Passphrase:** type a passphrase (recommended) or press ++enter++ for none

=== "macOS"

    Open **Terminal** and run:

    ```bash
    ssh-keygen -t ed25519 -C "your.email@example.com"
    ```

    When prompted:

    - **File location:** press ++return++ to accept the default (`~/.ssh/id_ed25519`)
    - **Passphrase:** type a passphrase (recommended) or press ++return++ for none

=== "Linux"

    ```bash
    ssh-keygen -t ed25519 -C "your.email@example.com"
    ```

    When prompted:

    - **File location:** press ++enter++ to accept the default (`~/.ssh/id_ed25519`)
    - **Passphrase:** type a passphrase (recommended) or press ++enter++ for none

This creates two files:

- `~/.ssh/id_ed25519` — your **private** key (never share this)
- `~/.ssh/id_ed25519.pub` — your **public** key (this goes to GitHub)

### Start the SSH Agent

The SSH agent holds your private key in memory so you don't re-enter the passphrase every command.

```bash
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519
```

!!! tip "Auto-start the agent on WSL"
    On WSL, the SSH agent resets each time you open a new terminal. Add these lines to your `~/.bashrc` to start it automatically:

    ```bash
    if [ -z "$SSH_AUTH_SOCK" ]; then
        eval "$(ssh-agent -s)" > /dev/null
        ssh-add ~/.ssh/id_ed25519 2> /dev/null
    fi
    ```

    Alternatively, install `keychain` (`sudo apt install keychain`) for a more robust solution that shares one agent across all terminal sessions.

### Add the Public Key to GitHub

1. Copy your public key to the clipboard:

    ```bash
    cat ~/.ssh/id_ed25519.pub
    ```

2. Go to **GitHub** → **Settings** → **SSH and GPG keys** → **New SSH key**
3. **Title:** something descriptive like `WSL - Dell Laptop` or `MacBook Pro`
4. **Key type:** Authentication Key
5. Paste the key contents and click **Add SSH key**

### Test the Connection

```bash
ssh -T git@github.com
```

Expected output:

```
Hi username! You've authenticated, but GitHub does not provide shell access.
```

If you see that message, your SSH key is working.

### Multiple SSH Keys

You may need multiple keys when you have a personal GitHub account alongside the university org account, or when you use both GitHub and OSC with separate credentials.

Create a `~/.ssh/config` file (or edit the existing one) to tell SSH which key to use for each host:

```
Host github.com
    HostName github.com
    User git
    IdentityFile ~/.ssh/id_ed25519

Host github-personal
    HostName github.com
    User git
    IdentityFile ~/.ssh/id_ed25519_personal
```

Then clone repos from your personal account using the alias:

```bash
git clone git@github-personal:user/repo.git
```

Repos cloned with `git@github.com:...` will use the default (university) key automatically.

## GitHub CLI (`gh`) Authentication

The GitHub CLI lets you create repos, open PRs, manage issues, and more — all from the terminal. It uses its own authentication separate from SSH keys.

### Install `gh`

=== "WSL / Ubuntu"

    ```bash
    (type -p wget >/dev/null || sudo apt install wget -y) \
      && sudo mkdir -p -m 755 /etc/apt/keyrings \
      && out=$(mktemp) && wget -nv -O$out https://cli.github.com/packages/githubcli-archive-keyring.gpg \
      && cat $out | sudo tee /etc/apt/keyrings/githubcli-archive-keyring.gpg > /dev/null \
      && sudo chmod go+r /etc/apt/keyrings/githubcli-archive-keyring.gpg \
      && echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null \
      && sudo apt update \
      && sudo apt install gh -y
    ```

=== "macOS"

    ```bash
    brew install gh
    ```

=== "Other"

    See the official installation instructions: [github.com/cli/cli#installation](https://github.com/cli/cli#installation)

### Authenticate

```bash
gh auth login
```

Walk through the interactive prompts:

1. **Where do you use GitHub?** → `GitHub.com`
2. **Preferred protocol for Git operations?** → `SSH`
3. **Upload your SSH public key?** → select your `~/.ssh/id_ed25519.pub`
4. **How would you like to authenticate?** → `Login with a web browser`
5. Copy the one-time code, press ++enter++, and authorize in the browser

Verify your login:

```bash
gh auth status
```

### Adding Scopes Later

Some GitHub features require additional OAuth scopes. Add them without re-authenticating:

```bash
gh auth refresh -s project
```

!!! info "When do you need the `project` scope?"
    The `project` scope is needed for [GitHub Projects](../contributing/github-projects.md). Add it when you start using project boards — you don't need it right away.

## Personal Access Tokens (PATs)

### When You Need a PAT

Most day-to-day Git work uses SSH keys. You need a PAT for:

- **GitHub Actions secrets** — API keys or deploy tokens used in CI workflows
- **Third-party integrations** — tools that can't use SSH (some IDEs, bots, CI services)

See [GitHub Actions & CI/CD](github-actions-ci-cd.md) for using secrets in workflows.

### Creating a Fine-Grained Token

1. Go to **GitHub** → **Settings** → **Developer settings** → **Personal access tokens** → **Fine-grained tokens**
2. **Token name:** something descriptive (e.g., `CI deploy token - my-repo`)
3. **Expiration:** 90 days (lab recommendation — set a calendar reminder to rotate)
4. **Repository access:** select only the specific repos that need it (never "All repositories")
5. **Permissions:** grant the minimum needed (usually **Contents: Read and write**)
6. Click **Generate token** and copy it immediately

!!! warning "Treat tokens like passwords"
    Never commit a token to a repository. Never paste one in a Slack message or shared doc. Store tokens in **GitHub Actions secrets** or a **password manager**. If a token leaks, revoke it immediately on GitHub.

## SSH Keys — OSC vs GitHub

SSH keys for GitHub and SSH keys for OSC are **separate key pairs for separate services**. Don't conflate them.

| | GitHub SSH Key | OSC SSH Key |
|---|---|---|
| **Authenticates to** | `github.com` | `pitzer.osc.edu` / `ascend.osc.edu` |
| **Used for** | `git push`, `git pull`, `git clone` | Cluster login, file transfer |
| **Uploaded to** | GitHub Settings → SSH keys | [OSC Portal](https://my.osc.edu/) |

**Recommendation:** use separate key pairs with different filenames (`id_ed25519` for GitHub, `id_ed25519_osc` for OSC) and configure each in `~/.ssh/config`:

```
Host github.com
    HostName github.com
    User git
    IdentityFile ~/.ssh/id_ed25519

Host pitzer
    HostName pitzer.osc.edu
    User your_osc_username
    IdentityFile ~/.ssh/id_ed25519_osc
```

For OSC SSH keys and connection setup, see [OSC SSH Connection](../osc-basics/osc-ssh-connection.md).

## Troubleshooting

| Problem | Cause | Fix |
|---|---|---|
| `Permission denied (publickey)` | SSH key not added to agent or not on GitHub | Run `ssh-add ~/.ssh/id_ed25519` and verify the key is listed on GitHub Settings → SSH keys |
| `ssh: Could not resolve hostname` | Typo in hostname or DNS issue | Check `~/.ssh/config` for typos, then test with `ssh -T git@github.com` |
| `ssh-keygen: command not found` | Git/OpenSSH not installed | WSL: `sudo apt install openssh-client`; Mac: install Xcode CLI tools with `xcode-select --install` |
| `Agent admitted failure to sign` | SSH agent not running | Run `eval "$(ssh-agent -s)" && ssh-add ~/.ssh/id_ed25519` |
| `gh auth login` hangs | Browser can't open from WSL | Use `gh auth login --web` and copy the URL manually into your Windows browser |
| Wrong GitHub account used | Multiple keys, wrong one offered first | Configure `~/.ssh/config` with a specific `IdentityFile` per `Host` alias (see [Multiple SSH Keys](#multiple-ssh-keys)) |

## Related Guides

- [Git Fundamentals](git-fundamentals.md) — core Git commands and mental model
- [Repository Setup](repository-setup.md) — create and configure repos
- [OSC SSH Connection](../osc-basics/osc-ssh-connection.md) — SSH keys for the cluster
- [Issues, PRs & Code Review](../contributing/github-issues-and-prs.md) — the collaboration workflow
