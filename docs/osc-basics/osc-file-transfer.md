---
tags:
  - OSC
  - Git
  - rsync
---
<!-- last-reviewed: 2026-05-09 -->
# File Transfer Guide

Use the simplest tool that fits the size and shape of the transfer.

## Quick Reference

| Method | Best for |
|---|---|
| VS Code | Small files and quick edits |
| SCP | Individual files |
| Rsync | Large files and directories |
| SFTP | Interactive browsing |
| OnDemand | Browser-based uploads |
| Git | Code and small text files |

## VS Code

If you are already using Remote-SSH, drag-and-drop and right-click upload/download are the fastest path for small files.

## SCP

```bash
scp local_file.txt pitzer:~/
scp -r local_directory/ pitzer:~/remote_directory/
scp pitzer:~/remote_file.txt ./
```

## Rsync

Rsync is the default choice for large or repeatable transfers.

```bash
rsync -avz --progress source/ pitzer:~/destination/
rsync -avz --progress --partial source/ pitzer:~/destination/
```

- `-a` preserves timestamps and permissions
- `-v` shows files
- `-z` compresses during transfer
- `--partial` helps resume interrupted transfers

Use `.rsyncignore` or `--exclude-from` to skip logs, caches, and other generated files.

## OnDemand

Use OSC OnDemand when you want a browser UI for uploads and downloads.

## Git

Use Git for code, scripts, and configuration files. Do not use it for large datasets or checkpoints.

## Best Practices

- Keep large data on scratch or shared storage
- Compress before transferring when a directory has many small files
- Verify permissions if an upload lands but is not readable
- Use `tmux` or `screen` for long transfers if your connection drops

## Troubleshooting

- Interrupted transfer: use `rsync --partial`
- Slow transfer: compress or archive first
- Permission denied: check destination permissions
- Disk quota exceeded: clean up or move data to project storage

## Next Steps

- [Remote Development](osc-remote-development.md)
- [Job Submission](../working-on-osc/osc-job-submission.md)

## Resources

- [OSC Getting Connected](https://www.osc.edu/resources/getting_started/getting_connected)
- [Rsync Manual](https://linux.die.net/man/1/rsync)
