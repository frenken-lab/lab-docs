---
status: new
tags:
  - git
  - troubleshooting
  - version-control
---
<!-- last-reviewed: 2026-03-30 -->
# Git Troubleshooting

A practical guide to the Git problems you will actually encounter in lab work. Almost everything in Git is recoverable — if something looks broken, take a breath and read through the relevant section below before doing anything drastic.

| | |
|---|---|
| **Audience** | All lab members |
| **Prerequisites** | Basic Git knowledge ([fundamentals](git-fundamentals.md)) |

---

## Merge Conflicts

### Why They Happen

Two branches changed the same lines in the same file. Git can auto-merge changes to *different* files (and even different parts of the same file), but when two people edit the exact same lines, Git can't decide which version to keep — so it asks you.

This is completely normal and happens in every collaborative project. It does not mean you did something wrong. Don't panic.

### Reading Conflict Markers

When a conflict occurs, Git inserts markers directly into the file. Here's what a real conflict looks like in a Python file:

```python
def load_data(path):
<<<<<<< HEAD
    df = pd.read_csv(path, index_col=0)
    df = df.dropna()
=======
    df = pd.read_parquet(path)
    df = df.fillna(0)
>>>>>>> feature/parquet-support
    return df
```

How to read this:

- Everything between `<<<<<<< HEAD` and `=======` is **your version** (the branch you're merging *into*).
- Everything between `=======` and `>>>>>>> feature/parquet-support` is the **incoming version** (the branch you're merging *from*).
- The rest of the file is unchanged and safe.

To resolve: delete the conflict markers (`<<<<<<<`, `=======`, `>>>>>>>`), keep the code you actually want, and save the file.

### Resolving Step by Step

1. Run `git status` — conflicted files are listed as **"both modified"**.
2. Open the conflicted file(s) in your editor.
3. Search for `<<<<<<<` markers (there may be more than one conflict per file).
4. Edit each conflict: keep the correct code, remove all marker lines.
5. Stage the resolved file:
   ```bash
   git add <file>
   ```
6. Once all conflicts are resolved, finalize the merge:
   ```bash
   git commit
   ```
   Git provides a default merge commit message — you can accept it as-is.

### Resolving in VS Code

VS Code detects conflict markers automatically and highlights them with color. Above each conflict you'll see clickable buttons:

- **Accept Current Change** — keep your version
- **Accept Incoming Change** — keep their version
- **Accept Both Changes** — keep both (you'll need to clean up the result)

For complex conflicts with many overlapping changes, click **"Resolve in Merge Editor"** at the bottom of the conflict. This opens a 3-way merge view showing your version, their version, and the merged result side by side.

!!! tip "You can always start over"
    If you get overwhelmed mid-merge, you can abort the entire merge and return to the state before you started:

    ```bash
    git merge --abort
    ```

    Nothing is lost. You're right back where you were.

### Preventing Conflicts

- **Pull before starting new work:** `git pull origin main`
- **Keep feature branches short-lived** — merge within days, not weeks. The longer a branch lives, the more it diverges.
- **Communicate with labmates** about who's editing which files, especially shared configs or data loaders.
- **Make small, focused commits** rather than large sweeping changes. Smaller diffs are easier to merge.

## Undoing Changes

Git gives you multiple escape hatches depending on how far along your changes are. The key question is: *have you committed yet, and have you pushed?*

### Before Committing

```bash
# Discard changes to a specific file (back to last commit)
git restore file.py

# Unstage a file (keep changes, remove from staging)
git restore --staged file.py

# Discard ALL local changes (nuclear option)
git restore .
```

!!! warning "No undo for `git restore`"
    `git restore <file>` permanently discards uncommitted changes to that file. There is no undo — those changes were never committed, so Git has no record of them. Make sure you really want to throw them away.

### After Committing (Local Only)

If you've committed but haven't pushed yet, you have several options:

```bash
# Undo the last commit, keep changes staged
git reset --soft HEAD~1

# Undo the last commit, keep changes unstaged
git reset HEAD~1

# Amend the last commit (fix message or add forgotten files)
git add forgotten-file.py
git commit --amend
```

!!! info "Local commits only"
    These commands rewrite history, which is fine as long as you haven't pushed yet. Once commits are on the remote, other people may have based work on them. After pushing, use `git revert` instead.

### After Pushing

```bash
# Create a new commit that undoes a previous commit
git revert <commit-hash>
```

`git revert` is safe for shared branches — it doesn't rewrite history. It creates a **new** commit that reverses the changes from the specified commit. Everyone on the team sees the revert in the history, and nobody's work is disrupted.

!!! danger "Never force-push shared branches"
    **Never** use `git reset --hard` or `git push --force` on branches others are using (especially `main`). This rewrites history and can destroy your labmates' work. If you need to undo something that's already pushed, `git revert` is always the right tool.

## Detached HEAD

### What It Means

Normally, `HEAD` points to a **branch** (like `main`), which in turn points to the latest commit. "Detached HEAD" means `HEAD` points directly to a specific commit — you're not on any branch.

This typically happens when:

- You checked out a specific commit: `git checkout abc123`
- You checked out a tag: `git checkout v1.0`
- A rebase went wrong

Detached HEAD isn't an error — Git is telling you that new commits you make here won't belong to any branch and could be lost if you switch away.

### How to Fix It

**If you just wanted to look at an old commit** and are done looking:

```bash
git checkout main    # Go back to your branch
```

**If you made commits while in detached HEAD** and want to keep them:

```bash
git checkout -b recovery-branch    # Create a branch from where you are
```

Your commits are now safely saved on `recovery-branch`. You can merge it into `main` or another branch whenever you're ready.

## Recovering Lost Work

One of Git's best-kept secrets: it is *extremely* hard to permanently lose committed work. Even when it looks like everything is gone, Git almost certainly still has it.

### git reflog — Your Safety Net

Git keeps a log of everywhere `HEAD` has pointed for the last 90 days. Even "deleted" commits, abandoned branches, and bad resets are recorded here.

```bash
# See the reflog
git reflog

# Output looks like:
# abc1234 HEAD@{0}: commit: Add data loader
# def5678 HEAD@{1}: checkout: moving from feature to main
# ghi9012 HEAD@{2}: commit: Fix preprocessing bug
```

To recover a specific commit:

```bash
git checkout -b recovery <commit-hash>
```

### Recovering a Deleted Branch

If you deleted a branch and need it back:

```bash
# Find the last commit on the deleted branch
git reflog | grep "branch-name"

# Recreate the branch at that commit
git branch branch-name <commit-hash>
```

### Recovering After a Bad Reset

If you accidentally ran `git reset --hard` and lost commits:

```bash
git reflog                          # Find the commit before the reset
git reset --hard <commit-hash>      # Go back to that commit
```

!!! tip "Reflog is local and temporary"
    The reflog is local to your machine only — it doesn't sync to GitHub. Entries expire after 90 days. For truly critical work, push to a remote branch as a backup. A quick `git push origin my-branch` takes seconds and gives you a permanent safety copy.

## Stashing Work in Progress

`git stash` lets you temporarily shelve uncommitted changes and come back to them later.

```bash
# Save uncommitted changes temporarily
git stash

# List stashed changes
git stash list

# Restore the most recent stash
git stash pop

# Restore a specific stash (keep it in the stash list)
git stash apply stash@{2}

# Delete all stashes
git stash clear
```

When to use stash:

- You need to **switch branches** but have uncommitted work that isn't ready to commit.
- You need to **pull** but have local modifications that would conflict.
- You want to **temporarily set aside changes** to test something on a clean working tree.

## Common Git Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `fatal: not a git repository` | You're not inside a git repo | `cd` into the repo directory, or run `git init` |
| `error: failed to push some refs` | Remote has commits you don't have locally | `git pull --rebase` then `git push` |
| `Your branch is behind 'origin/main'` | Remote has newer commits | `git pull origin main` |
| `CONFLICT (content): Merge conflict in file.py` | Both branches edited the same lines | See [Merge Conflicts](#merge-conflicts) above |
| `fatal: refusing to merge unrelated histories` | Repos have no common ancestor | `git pull origin main --allow-unrelated-histories` (rare — usually means something is misconfigured) |
| `error: pathspec 'file' did not match any files` | Typo in filename or file doesn't exist | Check `git status` for the correct filename |
| `Everything up-to-date` (but changes aren't pushed) | Changes aren't committed | `git add` and `git commit` first, then push |
| `HEAD detached at abc1234` | Not on a branch | See [Detached HEAD](#detached-head) above |

## Related Guides

- [Git Fundamentals](git-fundamentals.md) — core commands and mental model
- [Issues, PRs & Code Review](../contributing/github-issues-and-prs.md) — the branch workflow where conflicts typically arise
- [Troubleshooting](../resources/troubleshooting.md) — OSC-specific troubleshooting (not Git)
