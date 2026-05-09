<!-- last-reviewed: 2026-02-26 -->
# Assignment 1: Personal Academic Website

|                    |                                              |
| ------------------ | -------------------------------------------- |
| **Author**         | Robert Frenken                               |
| **Estimated time** | 3--4 hours                                   |
| **Prerequisites**  | A computer (Windows or Mac), internet access |

---

## What You'll Build

A live personal website at `https://YOURUSERNAME.github.io` using Quarto + GitHub Pages. Along the way you'll learn the Git workflow (clone, edit, commit, push, pull) we use daily in the lab.

!!! warning "Windows users: use Git Bash"
    Use **Git Bash** for all terminal commands in this assignment — **not** PowerShell or Command Prompt. Git Bash is installed alongside Git (Part 0.1) and gives you the same Linux-style commands you'll see in tutorials. You can also use the VS Code integrated terminal set to Git Bash.

---

## Part 0: Environment Setup

If you get stuck on any install step, ask in the lab Slack/Teams channel — setup issues are normal.

### 0.1 Install Git

=== "Windows"

    1. Download from [git-scm.com/downloads/win](https://git-scm.com/downloads/win)
    2. Run the installer with defaults, but on these screens choose:
        - **Adjusting your PATH** → "Git from the command line and also from 3rd-party software"
        - **Default editor** → "Use Visual Studio Code as Git's default editor"
        - **Default branch name** → Override with `main`
    3. Open **Git Bash** and verify: `git --version`

=== "Mac"

    1. Open **Terminal** and run `git --version`
    2. If Git isn't installed, macOS will prompt you to install Xcode Command Line Tools — click "Install"
    3. Verify again: `git --version`

### 0.2 Install VS Code

Download from [code.visualstudio.com](https://code.visualstudio.com/). Then install the **Quarto** extension (++ctrl+shift+x++ → search "quarto").

??? note "Windows: Set Git Bash as your default VS Code terminal"
    1. ++ctrl+shift+p++ → "Terminal: Select Default Profile" → choose **Git Bash**
    2. Open a new terminal (++ctrl+grave++) — it should say "bash" in the top-right

### 0.3 Install Quarto CLI

Download from [quarto.org/docs/get-started](https://quarto.org/docs/get-started/) and run the installer. **Open a new terminal** after installing, then verify:

```bash
quarto --version
```

### 0.4 Create a GitHub Account

Sign up at [github.com/signup](https://github.com/signup). **Use your university email** to qualify for [GitHub Education](https://education.github.com/) benefits.

### 0.5 Set Up SSH Keys for GitHub

SSH keys let you push/pull without entering your password every time.

=== "Windows (Git Bash)"

    ```bash
    # Generate key
    ssh-keygen -t ed25519 -C "your.email@osu.edu"
    # Press Enter for all prompts (defaults are fine)

    # Start SSH agent and add key
    eval "$(ssh-agent -s)"
    ssh-add ~/.ssh/id_ed25519

    # Copy public key to clipboard
    clip < ~/.ssh/id_ed25519.pub
    ```

=== "Mac (Terminal)"

    ```bash
    # Generate key
    ssh-keygen -t ed25519 -C "your.email@osu.edu"
    # Press Enter for all prompts (defaults are fine)

    # Start SSH agent and add key
    eval "$(ssh-agent -s)"
    ssh-add --apple-use-keychain ~/.ssh/id_ed25519

    # Copy public key to clipboard
    pbcopy < ~/.ssh/id_ed25519.pub
    ```

**Add the key to GitHub:**

1. Go to [github.com/settings/keys](https://github.com/settings/keys) → **"New SSH key"**
2. Title: something like "My Laptop" — Key type: **Authentication Key**
3. Paste the key (starts with `ssh-ed25519`) → **"Add SSH key"**

**Test it:**

```bash
ssh -T git@github.com
```

Type `yes` if prompted. You should see: `Hi YOURUSERNAME! You've successfully authenticated...`

### 0.6 Configure Git Identity

```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@osu.edu"
```

---

## Part 1: Create Your Website Repository

### 1.1 Use the Template

1. Go to: **[github.com/OSU-CAR-MSL/quarto-lab-templates](https://github.com/OSU-CAR-MSL/quarto-lab-templates)** (the website template is in the `website/` directory)
2. Click the green **"Use this template"** button → **"Create a new repository"**
3. Repository name: **`YOURUSERNAME.github.io`** (your actual GitHub username, case-sensitive)
4. Set to **Public** → click **"Create repository"**

### 1.2 Clone to Your Computer

```bash
cd ~/Documents
git clone git@github.com:YOURUSERNAME/YOURUSERNAME.github.io.git
cd YOURUSERNAME.github.io
code .
```

!!! note "If `code .` doesn't work"
    Open VS Code manually → File → Open Folder → navigate to the cloned folder. On Mac, press ++cmd+shift+p++ in VS Code → "Shell Command: Install 'code' command in PATH".

### 1.3 Enable GitHub Pages

1. Go to your repo on GitHub → **Settings** → **Pages**
2. Source: select **GitHub Actions**
3. Go to **Settings** → **Actions** → **General** → "Workflow permissions" → select **"Read and write permissions"** → **Save**

---

## Template Overview

Here's what each file in your site does:

| File           | What to do with it                                                |
| -------------- | ----------------------------------------------------------------- |
| `_quarto.yml`  | **Edit** — update your name, site URL, GitHub/email links, footer |
| `index.qmd`    | **Edit** — your home page (bio, photo, research interests)        |
| `cv.qmd`       | **Edit** — your CV                                                |
| `posts.qmd`    | **Don't touch** — auto-lists everything in `posts/`               |
| `research.qmd` | **Don't touch** — auto-lists everything in `research/`            |
| `posts/`       | **Add files here** — each `.qmd` file becomes a blog post         |
| `research/`    | **Add files here** — each `.qmd` file becomes a project page      |
| `images/`      | **Put your profile photo here** as `profile.jpg`                  |

To add a new blog post or research page, create a `.qmd` file in the right folder with a YAML header:

```yaml
---
title: "Your Title"
description: "A short summary."
date: "2026-02-19"
categories: [topic1, topic2]
---
Your content here.
```

The listing pages pick up new files automatically — no config changes needed.

---

## Part 2: Personalize Your Site

Run all commands in the **VS Code integrated terminal** (++ctrl+grave++). Do the tasks in order.

### Task 1: Edit Your Home Page

1. Open `_quarto.yml` — update your name, `site-url`, navbar links (GitHub/email), and footer
2. Open `index.qmd` — replace the placeholder bio, interests, education, and links
3. Add a profile photo: put a square image (400x400+) named `profile.jpg` in the `images/` folder
4. Preview locally:

   ```bash
   quarto preview
   ```

   Press ++ctrl+c++ to stop.

5. Commit and push:

   ```bash
   git add .
   git commit -m "Add personal info and profile photo"
   git push
   ```

6. Wait 1--2 minutes, then check `https://YOURUSERNAME.github.io`

### Task 2: Edit via GitHub, Then Pull Locally

1. On GitHub, click `cv.qmd` → pencil icon → fill in your CV details → commit
2. Back in VS Code terminal:
   ```bash
   git pull
   ```
3. Open `cv.qmd` locally — your edits from GitHub are now here

!!! tip "Why this matters"
    In research collaboration, teammates push changes you don't have locally. `git pull` keeps you in sync.

### Task 3: Add a Blog Post

1. In VS Code, create `posts/my-first-post.qmd` with this header:
   ```yaml
   ---
   title: "Getting Started in the CAR Lab"
   description: "My first week in the Mobility Systems Lab."
   date: "2026-02-19"
   categories: [lab, onboarding]
   ---
   ```
2. Write 2--3 paragraphs below (what you're excited about, what you learned, a brief intro)
3. Commit and push:
   ```bash
   git add posts/my-first-post.qmd
   git commit -m "Add first blog post"
   git push
   ```

### Task 4: Add a Research Project Page

1. Create `research/my-project.qmd` with a similar YAML header (title, description, date, categories)
2. Write a short summary of the project you'll be working on
3. Commit and push:
   ```bash
   git add research/my-project.qmd
   git commit -m "Add research project page"
   git push
   ```

---

## Final Deliverables

1. **Your live website URL:** `https://YOURUSERNAME.github.io`
2. **Your GitHub repo URL:** `https://github.com/YOURUSERNAME/YOURUSERNAME.github.io`

---

## Troubleshooting

| Problem                                         | Fix                                                          |
| ----------------------------------------------- | ------------------------------------------------------------ |
| `quarto: command not found`                     | Close and reopen your terminal after installing Quarto       |
| `git push` says "permission denied (publickey)" | Redo Part 0.5 — SSH key isn't set up correctly               |
| `git push` rejected (non-fast-forward)          | Run `git pull` first, then push again                        |
| Site not deploying                              | Check Settings → Pages → Source is "GitHub Actions"          |
| `ssh-keygen` or `eval` not recognized (Windows) | You're in PowerShell — switch to Git Bash                    |
| Images not showing                              | Check that the file path and name are case-sensitive matches |
