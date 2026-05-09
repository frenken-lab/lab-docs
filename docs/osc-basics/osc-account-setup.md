<!-- last-reviewed: 2026-02-19 -->
# OSC Account Setup

The Ohio Supercomputer Center (OSC) provides high-performance computing resources for research and education. This guide will help you get started with OSC access.

## Prerequisites

- Active Ohio State University affiliation (student, faculty, or staff)
- Valid OSU name.# (username)
- Participation in an approved OSC project

## Getting an OSC Account

### Step 1: Check if You Already Have Access

If you're already part of a lab project, your PI may have already added you to their OSC project.

1. Visit [my.osc.edu](https://my.osc.edu)
2. Try logging in with your OSU credentials
3. If successful, skip to [Verify Your Access](#verify-your-access)

### Step 2: Request Access (If Needed)

If you don't have access yet:

#### Option A: Join Existing Project (Most Common)
1. Contact your PI or lab manager
2. Provide your OSU username (name.#)
3. They will add you to the lab's OSC project
4. You'll receive an email notification when added

#### Option B: Request New Project
If your lab doesn't have an OSC project:

1. Visit [OSC Project Request](https://www.osc.edu/resources/getting_started/allocations_and_accounts)
2. Your PI should submit a project request
3. Follow the allocation request process
4. Wait for approval (typically 1-2 business days)

### Step 3: Activate Your Account

1. After being added to a project, visit [my.osc.edu](https://my.osc.edu)
2. Log in with your OSU credentials
3. Accept the terms of service
4. Set up two-factor authentication (if prompted)

## Verify Your Access

### Check Your Projects

1. Log into [my.osc.edu](https://my.osc.edu)
2. Click on "Projects" in the top menu
3. Verify you see your lab's project listed
4. Note your project code (e.g., `PAS1234`)

!!! warning "PAS1234 is a placeholder"
    Throughout this documentation, `PAS1234` is used as a placeholder project code. Replace it with your actual OSC project code, which you can find at [my.osc.edu](https://my.osc.edu) under your project list.

### Check Your Allocations

1. In the my.osc.edu portal, navigate to "Allocations"
2. Verify you have access to computing resources
3. Note which clusters you can access (Pitzer, Ascend, Cardinal)

For cluster specs, GPU types, and partition details, see the [Clusters Overview](osc-clusters-overview.md).

To set up SSH keys for password-less login, see the [SSH Connection Guide](osc-ssh-connection.md#ssh-keys-setup).

## Test Your Connection

Try connecting via SSH:

```bash
# Replace username with your OSU name.#
ssh username@pitzer.osc.edu
```

If successful, you should see:
```
Welcome to the Ohio Supercomputer Center
Pitzer Cluster
...
[username@pitzer-login01 ~]$
```

## Next Steps

Now that you have OSC access:

1. [Configure SSH Connection](osc-ssh-connection.md) - Set up convenient SSH access
2. [Set Up Remote Development](osc-remote-development.md) - Use VS Code with OSC
3. [Learn Job Submission](../working-on-osc/osc-job-submission.md) - Submit and manage SLURM jobs

## Important Resources

- **OSC Documentation**: [https://www.osc.edu/resources/technical_support/supercomputers](https://www.osc.edu/resources/technical_support/supercomputers)
- **OSC Help**: Email [oschelp@osc.edu](mailto:oschelp@osc.edu)
- **Office Hours**: OSC offers walk-in office hours - check their website
- **Status Page**: [https://www.osc.edu/resources/system-status](https://www.osc.edu/resources/system-status)

## Troubleshooting

### Can't log into my.osc.edu
- Verify you're using your OSU credentials (name.#)
- Try resetting your OSU password
- Contact OSC Help at oschelp@osc.edu

### SSH connection refused
- Verify you're on OSU network or VPN
- Check system status: [https://www.osc.edu/resources/system-status](https://www.osc.edu/resources/system-status)
- Verify the correct hostname (pitzer.osc.edu, not pitzer.org)

### Not listed on any projects
- Contact your PI to be added to the lab project
- Verify with PI that they have an active OSC allocation

### Two-factor authentication issues
- Use the Duo Mobile app
- Contact OSU IT if you have 2FA problems

For more help, see the [Troubleshooting Guide](../resources/troubleshooting.md).
