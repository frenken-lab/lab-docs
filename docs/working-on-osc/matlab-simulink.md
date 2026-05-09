<!-- last-reviewed: 2026-02-26 -->
# MATLAB & Simulink on OSC

How to use MATLAB and Simulink on OSC for computation, simulation, and batch processing.

## Overview

OSC provides MATLAB installations that all users can access through the module system. You can:

- Run MATLAB scripts in batch mode via SLURM jobs
- Use the MATLAB GUI through OSC OnDemand
- Run Simulink models headlessly on compute nodes
- Leverage the Parallel Computing Toolbox for multi-core and multi-node work

## Loading MATLAB

### Find Available Versions

```bash
module spider matlab
```

### Load MATLAB

```bash
# Load default version
module load matlab

# Load a specific version
module load matlab/r2025b
```

### Verify Installation

```bash
matlab -batch "disp(version)"
```

## Running MATLAB Interactively

### Option 1: MATLAB GUI via OnDemand

The easiest way to use MATLAB interactively on OSC:

1. Log in at [ondemand.osc.edu](https://ondemand.osc.edu)
2. Go to **Interactive Apps > MATLAB**
3. Select your project account, number of cores, and time limit
4. Click **Launch** and wait for the session to start
5. Click **Connect** to open the MATLAB desktop

This gives you the full MATLAB IDE with editor, workspace, plots, and Simulink.

### Option 2: Command-Line Interactive Session

```bash
# Request an interactive session
srun --account=PAS1234 -p serial --cpus-per-task=4 \
     --mem=16G --time=02:00:00 --pty bash

# Load MATLAB
module load matlab

# Start MATLAB in command-line mode (no GUI)
matlab -nodesktop -nosplash
```

From the MATLAB prompt you can run commands, scripts, and test code before submitting batch jobs.

## Running MATLAB in Batch Mode

For production runs, submit MATLAB scripts as SLURM batch jobs.

### Basic Batch Job

`scripts/run_matlab.sh`:

```bash
#!/bin/bash
#SBATCH --job-name=matlab_job
#SBATCH --account=PAS1234
#SBATCH --nodes=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --time=04:00:00
#SBATCH --output=logs/matlab_%j.out

echo "Job started at: $(date)"
echo "Node: $(hostname)"

module load matlab

# Run a MATLAB script (without the .m extension)
matlab -batch "run_analysis"

echo "Job finished at: $(date)"
```

!!! warning "Use `-batch` not `-r`"
    The `-batch` flag (introduced in R2019a) is preferred over the older `-r` flag. It automatically sets `-nodesktop -nosplash`, exits MATLAB when the script finishes, and returns a nonzero exit code on error so SLURM can detect failures.

### Passing Arguments to MATLAB Scripts

MATLAB scripts don't take command-line arguments directly. Use environment variables or wrapper patterns:

#### Method 1: Environment Variables

```bash
#!/bin/bash
#SBATCH --job-name=matlab_param
#SBATCH --account=PAS1234
#SBATCH --time=02:00:00
#SBATCH --output=logs/matlab_%j.out

module load matlab

export PARAM_ALPHA=0.5
export PARAM_BETA=100
export OUTPUT_DIR="/fs/scratch/PAS1234/$USER/results"

matlab -batch "run_experiment"
```

In your MATLAB script `run_experiment.m`:

```matlab
% Read parameters from environment variables
alpha = str2double(getenv('PARAM_ALPHA'));
beta = str2double(getenv('PARAM_BETA'));
output_dir = getenv('OUTPUT_DIR');

fprintf('Running with alpha=%.2f, beta=%d\n', alpha, beta);

% Your computation
result = my_simulation(alpha, beta);

% Save results
if ~exist(output_dir, 'dir')
    mkdir(output_dir);
end
save(fullfile(output_dir, 'results.mat'), 'result', 'alpha', 'beta');
fprintf('Results saved to %s\n', output_dir);
```

#### Method 2: Inline MATLAB Commands

```bash
#!/bin/bash
#SBATCH --job-name=matlab_inline
#SBATCH --account=PAS1234
#SBATCH --time=02:00:00
#SBATCH --output=logs/matlab_%j.out

module load matlab

ALPHA=0.5
BETA=100

matlab -batch "alpha=$ALPHA; beta=$BETA; run_experiment"
```

### Parameter Sweeps with Job Arrays

`scripts/matlab_sweep.sh`:

```bash
#!/bin/bash
#SBATCH --job-name=matlab_sweep
#SBATCH --account=PAS1234
#SBATCH --array=1-20
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --time=02:00:00
#SBATCH --output=logs/matlab_sweep_%A_%a.out

module load matlab

export TASK_ID=$SLURM_ARRAY_TASK_ID
export OUTPUT_DIR="/fs/scratch/PAS1234/$USER/sweep_results"

matlab -batch "sweep_runner"
```

`sweep_runner.m`:

```matlab
% Read task ID and set parameters accordingly
task_id = str2double(getenv('TASK_ID'));
output_dir = getenv('OUTPUT_DIR');

% Define parameter grid
alphas = linspace(0.1, 1.0, 5);   % 5 values
betas = [10, 50, 100, 200];       % 4 values

% Map task_id (1-20) to parameter indices
[alpha_idx, beta_idx] = ind2sub([5, 4], task_id);
alpha = alphas(alpha_idx);
beta = betas(beta_idx);

fprintf('Task %d: alpha=%.2f, beta=%d\n', task_id, alpha, beta);

% Run simulation
result = my_simulation(alpha, beta);

% Save individual result
out_file = fullfile(output_dir, sprintf('result_task_%03d.mat', task_id));
save(out_file, 'result', 'alpha', 'beta', 'task_id');
fprintf('Saved: %s\n', out_file);
```

## Using Simulink on OSC

### Running Simulink Models in Batch Mode

Simulink models can be run without a GUI using the `sim` command:

`run_simulink.m`:

```matlab
% Load and run a Simulink model in batch mode
model_name = 'my_vehicle_model';

% Open the model (does not require a display)
load_system(model_name);

% Set simulation parameters
set_param(model_name, 'StopTime', '100');
set_param(model_name, 'Solver', 'ode45');
set_param(model_name, 'MaxStep', '0.01');

% Configure any model parameters
set_param([model_name '/Controller'], 'Gain', '2.5');

% Run simulation
simOut = sim(model_name);

% Extract results
t = simOut.tout;
y = simOut.yout;

% Save results
output_dir = getenv('OUTPUT_DIR');
if isempty(output_dir)
    output_dir = '.';
end
save(fullfile(output_dir, 'sim_results.mat'), 't', 'y');

% Generate and save figures
figure('Visible', 'off');
plot(t, y);
xlabel('Time (s)');
ylabel('Output');
title('Simulation Results');
saveas(gcf, fullfile(output_dir, 'sim_plot.png'));

fprintf('Simulation complete. Results saved to %s\n', output_dir);
```

SLURM job script:

```bash
#!/bin/bash
#SBATCH --job-name=simulink_job
#SBATCH --account=PAS1234
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --time=04:00:00
#SBATCH --output=logs/simulink_%j.out

module load matlab

export OUTPUT_DIR="/fs/scratch/PAS1234/$USER/simulink_results/$SLURM_JOB_ID"
mkdir -p $OUTPUT_DIR

# Change to the directory containing your .slx model file
cd ~/projects/my_simulink_project

matlab -batch "run_simulink"
```

### Simulink Parameter Sweeps

`sweep_simulink.m`:

```matlab
model_name = 'my_vehicle_model';
load_system(model_name);

task_id = str2double(getenv('TASK_ID'));
output_dir = getenv('OUTPUT_DIR');

% Parameter grid
gains = [0.5, 1.0, 2.0, 5.0, 10.0];
damping_ratios = [0.1, 0.3, 0.5, 0.7, 0.9];

[g_idx, d_idx] = ind2sub([5, 5], task_id);
gain = gains(g_idx);
damping = damping_ratios(d_idx);

fprintf('Task %d: gain=%.1f, damping=%.1f\n', task_id, gain, damping);

% Set model parameters
set_param([model_name '/Controller'], 'Gain', num2str(gain));
set_param([model_name '/Plant'], 'DampingRatio', num2str(damping));

% Run simulation
simOut = sim(model_name, 'StopTime', '50');

% Save
out_file = fullfile(output_dir, sprintf('sim_task_%03d.mat', task_id));
save(out_file, 'simOut', 'gain', 'damping', 'task_id');
fprintf('Saved: %s\n', out_file);
```

```bash
#!/bin/bash
#SBATCH --job-name=sim_sweep
#SBATCH --account=PAS1234
#SBATCH --array=1-25
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --time=02:00:00
#SBATCH --output=logs/sim_sweep_%A_%a.out

module load matlab

export TASK_ID=$SLURM_ARRAY_TASK_ID
export OUTPUT_DIR="/fs/scratch/PAS1234/$USER/sim_sweep"
mkdir -p $OUTPUT_DIR

cd ~/projects/my_simulink_project
matlab -batch "sweep_simulink"
```

## Parallel Computing with MATLAB

### Using `parfor` with Local Workers

MATLAB's Parallel Computing Toolbox can use multiple CPU cores on a single node:

```matlab
% Start a parallel pool using available cores
num_workers = str2double(getenv('SLURM_CPUS_PER_TASK'));
if isnan(num_workers)
    num_workers = 4;
end
parpool('local', num_workers);

% Parallel loop
results = zeros(1000, 1);
parfor i = 1:1000
    results(i) = expensive_computation(i);
end

delete(gcp('nocreate'));  % Shut down parallel pool
```

Job script:

```bash
#!/bin/bash
#SBATCH --job-name=matlab_par
#SBATCH --account=PAS1234
#SBATCH --cpus-per-task=16
#SBATCH --mem=64G
#SBATCH --time=04:00:00
#SBATCH --output=logs/matlab_par_%j.out

module load matlab

matlab -batch "my_parallel_script"
```

!!! tip "Match `--cpus-per-task` to your parallel pool size"
    Request the same number of CPUs from SLURM as you plan to use in your `parpool`. Requesting more wastes resources; requesting fewer causes contention.

### GPU Computing with MATLAB

MATLAB supports GPU computation through `gpuArray`:

```matlab
% Check GPU availability
if gpuDeviceCount > 0
    gpu = gpuDevice(1);
    fprintf('GPU: %s (%.1f GB)\n', gpu.Name, gpu.TotalMemory/1e9);
end

% Move data to GPU
A = gpuArray(rand(5000));
B = gpuArray(rand(5000));

% Computation runs on GPU
C = A * B;

% Move result back to CPU
C_cpu = gather(C);
```

Job script with GPU:

```bash
#!/bin/bash
#SBATCH --job-name=matlab_gpu
#SBATCH --account=PAS1234
#SBATCH --partition=gpu
#SBATCH --gpus-per-node=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=32G
#SBATCH --time=04:00:00
#SBATCH --output=logs/matlab_gpu_%j.out

module load matlab
module load cuda/12.x

matlab -batch "my_gpu_script"
```

## Working with Files and Data

### Using Scratch Space

```matlab
% Build paths using environment variables
scratch = fullfile('/fs/scratch/PAS1234', getenv('USER'));
data_dir = fullfile(scratch, 'datasets');
results_dir = fullfile(scratch, 'results');

% Create output directory
if ~exist(results_dir, 'dir')
    mkdir(results_dir);
end

% Load data
data = load(fullfile(data_dir, 'input_data.mat'));

% Save results
save(fullfile(results_dir, 'output.mat'), 'result');
```

### Saving Figures Without a Display

On compute nodes there is no display, so use the `Visible` property:

```matlab
fig = figure('Visible', 'off');
plot(x, y);
xlabel('X');
ylabel('Y');
title('Results');
saveas(fig, 'results.png');
% Or for higher quality:
exportgraphics(fig, 'results.pdf', 'ContentType', 'vector');
close(fig);
```

## MATLAB with Toolboxes

OSC's MATLAB installation includes many toolboxes. Check what's available:

```matlab
ver   % Lists all installed toolboxes
```

Common toolboxes used in research:

| Toolbox | Use Case |
|---------|----------|
| Simulink | Dynamic system simulation |
| Signal Processing | Filtering, FFT, spectral analysis |
| Control System | Transfer functions, state-space models |
| Automated Driving | Scenario design, sensor simulation |

!!! note "License availability"
    Toolbox licenses are shared across all OSC users. If a license is unavailable, your job may fail or wait. Check license status with:
    ```bash
    module load matlab
    matlab -batch "license('test', 'Simulink')"
    ```

## Troubleshooting

### MATLAB Fails to Start

```bash
# Check module is loaded
module list | grep matlab

# Try with verbose output
matlab -batch "disp('hello')" 2>&1 | head -50

# Check license server
matlab -batch "license('inuse')"
```

### "License checkout failed"

This usually means all licenses are in use by other users. Options:

- Wait and retry
- Check license availability: `matlab -batch "license('test', 'MATLAB')"`
- Submit during off-peak hours (evenings, weekends)

### Simulink "Cannot open model"

```bash
# Verify the .slx file is in the MATLAB path
# In your job script, cd to the model directory first:
cd ~/projects/my_project
matlab -batch "run_simulink"
```

Or add the path inside MATLAB:

```matlab
addpath('~/projects/my_project/models');
load_system('my_model');
```

### Figures / Plots Fail Without Display

Use `figure('Visible', 'off')` or set the default:

```matlab
set(0, 'DefaultFigureVisible', 'off');
```

### Out of Memory

- Request more memory in your SLURM script (`--mem=64G` or `--mem=128G`)
- Use memory-efficient data types (`single` instead of `double`)
- Process data in chunks
- Clear unused variables with `clear`

## Next Steps

- Learn [Job Submission](osc-job-submission.md) for SLURM details
- Review [Environment Management](osc-environment-management.md) for module handling
- Explore the [Notebook-to-Script Workflow](../ml-workflows/notebook-to-script.md) for Python-based experiments

## Resources

- [OSC MATLAB Documentation](https://www.osc.edu/resources/available_software/software_list/matlab)
- [Troubleshooting Guide](../resources/troubleshooting.md)
