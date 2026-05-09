<!-- last-reviewed: 2026-02-26 -->
# CARLA Simulator on OSC

How to install, run, and develop with the CARLA autonomous driving simulator on OSC.

## Overview

[CARLA](https://carla.org/) is an open-source simulator for autonomous driving research. It provides realistic urban environments, vehicle physics, sensor models (cameras, LiDAR, GNSS, IMU), and a Python API for controlling simulations programmatically.

Running CARLA on OSC lets you leverage GPU compute nodes for large-scale data collection, reinforcement learning training, and scenario evaluation without needing a local workstation with a powerful GPU.

### What You Can Do

- Collect synthetic sensor data (camera, LiDAR, radar) at scale
- Train and evaluate autonomous driving agents
- Run closed-loop simulation experiments in parallel
- Test perception, planning, and control pipelines

## Prerequisites

- An OSC account with an active project allocation (see [Account Setup](../osc-basics/osc-account-setup.md))
- Familiarity with [Job Submission](osc-job-submission.md) and [Environment Management](osc-environment-management.md)
- A Python virtual environment with your project dependencies

## Installing CARLA

CARLA is not pre-installed on OSC, so you need to download the release package to your scratch space.

### Download the CARLA Release

```bash
# Use scratch space for the large installation (~15-30 GB)
SCRATCH=/fs/scratch/PAS1234/$USER
mkdir -p $SCRATCH/carla && cd $SCRATCH/carla

# Download CARLA (check https://github.com/carla-simulator/carla/releases for latest)
wget https://carla-releases.s3.us-east-005.backblazeb2.com/Linux/CARLA_0.9.15.tar.gz

# Extract
tar -xzf CARLA_0.9.15.tar.gz
rm CARLA_0.9.15.tar.gz
```

### Install the CARLA Python Client

```bash
module load python/3.12
source ~/venvs/carla_project/bin/activate

# Install the CARLA Python package
pip install carla==0.9.15

# Install other common dependencies
pip install numpy opencv-python pygame matplotlib
```

!!! note "Match versions"
    The CARLA Python client version must match the server version. If you downloaded CARLA 0.9.15, install `carla==0.9.15`.

## Running CARLA on OSC

CARLA has a client-server architecture:

1. **CARLA Server** — renders the 3D world (requires a GPU)
2. **Python Client** — connects to the server to control the simulation

On OSC, the server runs in **headless mode** (no display) using offscreen rendering.

### Interactive Testing

Start with an interactive GPU session to verify everything works:

```bash
# Request an interactive GPU session
srun --account=PAS1234 -p gpu --gpus-per-node=1 --cpus-per-task=4 \
     --mem=32G --time=01:00:00 --pty bash
```

#### Start the CARLA Server

```bash
SCRATCH=/fs/scratch/PAS1234/$USER

# Launch CARLA in headless mode (no display needed)
$SCRATCH/carla/CarlaUE4.sh -RenderOffScreen -carla-port=2000 &

# Wait for the server to initialize
sleep 30

# Verify it's running
ps aux | grep CarlaUE4
```

#### Connect with a Python Client

```bash
module load python/3.12
source ~/venvs/carla_project/bin/activate

python - <<'EOF'
import carla

client = carla.Client("localhost", 2000)
client.set_timeout(10.0)

world = client.get_world()
print(f"Connected to CARLA")
print(f"Map: {world.get_map().name}")
print(f"Available maps: {client.get_available_maps()}")

# Spawn a vehicle
blueprint_library = world.get_blueprint_library()
vehicle_bp = blueprint_library.find("vehicle.tesla.model3")
spawn_point = world.get_map().get_spawn_points()[0]
vehicle = world.spawn_actor(vehicle_bp, spawn_point)
print(f"Spawned vehicle: {vehicle.type_id}")

# Clean up
vehicle.destroy()
EOF
```

### Batch Job for Data Collection

`scripts/carla_collect.sh`:

```bash
#!/bin/bash
#SBATCH --job-name=carla_collect
#SBATCH --account=PAS1234
#SBATCH --partition=gpu
#SBATCH --gpus-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=08:00:00
#SBATCH --output=logs/carla_collect_%j.out

echo "Job started at: $(date)"
echo "Node: $(hostname)"

module load python/3.12
module load cuda/12.x
source ~/venvs/carla_project/bin/activate

SCRATCH=/fs/scratch/PAS1234/$USER
CARLA_ROOT=$SCRATCH/carla
OUTPUT_DIR=$SCRATCH/carla_data/collection_$SLURM_JOB_ID

mkdir -p $OUTPUT_DIR

# --- Start CARLA server ---
echo "Starting CARLA server..."
$CARLA_ROOT/CarlaUE4.sh -RenderOffScreen -carla-port=2000 &
CARLA_PID=$!
sleep 45  # Give CARLA time to start

# Verify server is running
if ! kill -0 $CARLA_PID 2>/dev/null; then
    echo "ERROR: CARLA server failed to start"
    exit 1
fi
echo "CARLA server running (PID: $CARLA_PID)"

# --- Run data collection script ---
python src/collect_data.py \
    --host localhost \
    --port 2000 \
    --output-dir $OUTPUT_DIR \
    --num-episodes 50 \
    --steps-per-episode 1000

# --- Clean up ---
echo "Stopping CARLA server..."
kill $CARLA_PID
wait $CARLA_PID 2>/dev/null

echo "Data saved to: $OUTPUT_DIR"
echo "Job finished at: $(date)"
```

### Example Data Collection Script

`src/collect_data.py`:

```python
"""Collect camera and LiDAR data from CARLA."""
import argparse
import os
import time
import numpy as np
import carla


def setup_sensors(world, vehicle):
    """Attach camera and LiDAR sensors to the vehicle."""
    bp_lib = world.get_blueprint_library()

    # RGB Camera
    camera_bp = bp_lib.find("sensor.camera.rgb")
    camera_bp.set_attribute("image_size_x", "1280")
    camera_bp.set_attribute("image_size_y", "720")
    camera_bp.set_attribute("fov", "90")
    camera_transform = carla.Transform(carla.Location(x=1.5, z=2.4))
    camera = world.spawn_actor(camera_bp, camera_transform, attach_to=vehicle)

    # LiDAR
    lidar_bp = bp_lib.find("sensor.lidar.ray_cast")
    lidar_bp.set_attribute("range", "50.0")
    lidar_bp.set_attribute("channels", "64")
    lidar_bp.set_attribute("points_per_second", "1200000")
    lidar_bp.set_attribute("rotation_frequency", "20")
    lidar_transform = carla.Transform(carla.Location(x=0.0, z=2.5))
    lidar = world.spawn_actor(lidar_bp, lidar_transform, attach_to=vehicle)

    return camera, lidar


def run_episode(client, output_dir, episode_idx, steps):
    """Run one data collection episode."""
    world = client.get_world()
    bp_lib = world.get_blueprint_library()

    # Spawn vehicle
    vehicle_bp = bp_lib.find("vehicle.tesla.model3")
    spawn_points = world.get_map().get_spawn_points()
    spawn_point = spawn_points[episode_idx % len(spawn_points)]
    vehicle = world.spawn_actor(vehicle_bp, spawn_point)

    # Enable autopilot
    vehicle.set_autopilot(True)

    # Attach sensors
    camera, lidar = setup_sensors(world, vehicle)

    # Storage for sensor data
    episode_dir = os.path.join(output_dir, f"episode_{episode_idx:04d}")
    os.makedirs(os.path.join(episode_dir, "camera"), exist_ok=True)
    os.makedirs(os.path.join(episode_dir, "lidar"), exist_ok=True)

    frame_count = [0]

    def save_image(image):
        array = np.frombuffer(image.raw_data, dtype=np.uint8)
        array = array.reshape((image.height, image.width, 4))[:, :, :3]
        path = os.path.join(episode_dir, "camera", f"{frame_count[0]:06d}.npy")
        np.save(path, array)

    def save_lidar(data):
        points = np.frombuffer(data.raw_data, dtype=np.float32).reshape(-1, 4)
        path = os.path.join(episode_dir, "lidar", f"{frame_count[0]:06d}.npy")
        np.save(path, points)

    camera.listen(save_image)
    lidar.listen(save_lidar)

    # Run simulation
    for step in range(steps):
        world.tick()
        frame_count[0] += 1

    # Cleanup
    camera.stop()
    lidar.stop()
    camera.destroy()
    lidar.destroy()
    vehicle.destroy()

    print(f"Episode {episode_idx}: saved {frame_count[0]} frames to {episode_dir}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="localhost")
    parser.add_argument("--port", type=int, default=2000)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--num-episodes", type=int, default=10)
    parser.add_argument("--steps-per-episode", type=int, default=500)
    args = parser.parse_args()

    client = carla.Client(args.host, args.port)
    client.set_timeout(30.0)

    # Use synchronous mode for deterministic data collection
    settings = client.get_world().get_settings()
    settings.synchronous_mode = True
    settings.fixed_delta_seconds = 0.05  # 20 FPS
    client.get_world().apply_settings(settings)

    for ep in range(args.num_episodes):
        run_episode(client, args.output_dir, ep, args.steps_per_episode)

    # Restore async mode
    settings.synchronous_mode = False
    client.get_world().apply_settings(settings)
    print("Data collection complete.")


if __name__ == "__main__":
    main()
```

## Running Parallel CARLA Jobs

You can run multiple independent CARLA instances using job arrays. Each job starts its own server on a different port:

`scripts/carla_parallel.sh`:

```bash
#!/bin/bash
#SBATCH --job-name=carla_par
#SBATCH --account=PAS1234
#SBATCH --array=0-4
#SBATCH --partition=gpu
#SBATCH --gpus-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=04:00:00
#SBATCH --output=logs/carla_par_%A_%a.out

module load python/3.12
module load cuda/12.x
source ~/venvs/carla_project/bin/activate

SCRATCH=/fs/scratch/PAS1234/$USER
CARLA_ROOT=$SCRATCH/carla

# Use different port per array task to avoid conflicts
PORT=$((2000 + SLURM_ARRAY_TASK_ID * 2))
OUTPUT_DIR=$SCRATCH/carla_data/batch_${SLURM_ARRAY_JOB_ID}/task_${SLURM_ARRAY_TASK_ID}
mkdir -p $OUTPUT_DIR

# Start CARLA server on unique port
$CARLA_ROOT/CarlaUE4.sh -RenderOffScreen -carla-port=$PORT &
CARLA_PID=$!
sleep 45

python src/collect_data.py \
    --host localhost \
    --port $PORT \
    --output-dir $OUTPUT_DIR \
    --num-episodes 10 \
    --steps-per-episode 1000

kill $CARLA_PID
wait $CARLA_PID 2>/dev/null
```

## Changing Maps and Weather

```python
# Load a different map
client.load_world("Town03")

# Set weather
world = client.get_world()
weather = carla.WeatherParameters(
    cloudiness=80.0,
    precipitation=60.0,
    sun_altitude_angle=30.0,
    fog_density=20.0,
)
world.set_weather(weather)

# Or use a preset
world.set_weather(carla.WeatherParameters.ClearNoon)
world.set_weather(carla.WeatherParameters.HardRainSunset)
```

## Training an Agent with CARLA

For reinforcement learning or imitation learning, a common pattern is to run the CARLA server and your training script in the same job:

`scripts/carla_train.sh`:

```bash
#!/bin/bash
#SBATCH --job-name=carla_train
#SBATCH --account=PAS1234
#SBATCH --partition=gpu
#SBATCH --gpus-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=24:00:00
#SBATCH --output=logs/carla_train_%j.out

module load python/3.12
module load cuda/12.x
source ~/venvs/carla_project/bin/activate

SCRATCH=/fs/scratch/PAS1234/$USER
CARLA_ROOT=$SCRATCH/carla

# Start CARLA server
$CARLA_ROOT/CarlaUE4.sh -RenderOffScreen -carla-port=2000 \
    -quality-level=Low &
CARLA_PID=$!
sleep 45

# Run RL training (your script interacts with CARLA via the Python API)
python src/train_agent.py \
    --carla-host localhost \
    --carla-port 2000 \
    --total-timesteps 500000 \
    --checkpoint-dir $SCRATCH/carla_checkpoints

kill $CARLA_PID
wait $CARLA_PID 2>/dev/null
```

!!! tip "Use `-quality-level=Low` for training"
    Lower rendering quality uses less GPU memory and runs faster. Use higher quality only for final evaluation or data collection where visual fidelity matters.

## Troubleshooting

### CARLA Server Won't Start

```bash
# Check if the binary is executable
chmod +x $SCRATCH/carla/CarlaUE4.sh

# Check GPU is available
nvidia-smi

# Try with verbose output
$SCRATCH/carla/CarlaUE4.sh -RenderOffScreen -carla-port=2000 -log 2>&1 | head -100
```

### Client Can't Connect

```bash
# Verify server is running
ps aux | grep CarlaUE4

# Give the server more time to start (increase sleep)
sleep 60

# Check the port is correct
ss -tlnp | grep 2000
```

### Out of GPU Memory

- Use `-quality-level=Low` to reduce VRAM usage
- Reduce the number of sensors attached to vehicles
- Lower camera resolution
- Use `Town01` (smallest map) for testing

### Vulkan/Rendering Errors

```bash
# CARLA may need Vulkan libraries — check if they're available
module load vulkan
# Or try OpenGL fallback
$SCRATCH/carla/CarlaUE4.sh -RenderOffScreen -carla-port=2000 -opengl
```

## Next Steps

- Learn about [Job Submission](osc-job-submission.md) and job arrays for parallel experiments
- Set up [Data & Experiment Tracking](../ml-workflows/data-experiment-tracking.md) for your CARLA runs
- Review [PyTorch & GPU Setup](../ml-workflows/pytorch-setup.md) for multi-GPU setups
- Use the [Notebook-to-Script Workflow](../ml-workflows/notebook-to-script.md) to prototype CARLA experiments interactively

## Resources

- [CARLA GitHub Repository](https://github.com/carla-simulator/carla) — releases, issue tracker
- [Troubleshooting Guide](../resources/troubleshooting.md)
