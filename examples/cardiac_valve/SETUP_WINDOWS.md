# Windows Setup Guide - Cardiac Valve Simulation

Complete installation guide for running the cardiac valve visualization project on Windows.

---

## Prerequisites

- **Windows**: 10 or 11 (64-bit)
- **RAM**: 8 GB minimum, 16 GB recommended
- **Disk Space**: 25 GB free space
- **Time**: 1-3 hours for installation

---

## Installation Methods

Choose one:
- **Method 1**: WSL2 + Docker (Recommended, ~1 hour)
- **Method 2**: WSL2 Native Build (Advanced, ~3 hours)
- **Method 3**: Python Tools Only (Quick start, ~15 minutes)

---

# Method 1: WSL2 + Docker (Recommended)

## Step 1: Enable WSL2

### 1.1 Enable Windows Features

Open PowerShell as Administrator:

```powershell
# Enable WSL and Virtual Machine Platform
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart

# Restart computer
Restart-Computer
```

### 1.2 Install WSL2

After restart, open PowerShell as Administrator:

```powershell
# Set WSL2 as default
wsl --set-default-version 2

# Install Ubuntu (recommended distribution)
wsl --install -d Ubuntu-22.04

# Follow prompts to create username/password
```

### 1.3 Verify Installation

```powershell
# Check WSL version
wsl --list --verbose

# Should show Ubuntu-22.04 with VERSION 2
```

## Step 2: Install Docker Desktop

### 2.1 Download Docker Desktop

- Visit: https://www.docker.com/products/docker-desktop/
- Download "Docker Desktop for Windows"
- Run installer (requires restart)

### 2.2 Configure Docker Desktop

- Open Docker Desktop
- Settings → General → "Use WSL 2 based engine" ✓
- Settings → Resources → WSL Integration → Enable Ubuntu-22.04 ✓
- Click "Apply & Restart"

### 2.3 Verify Docker in WSL

```bash
# Open Ubuntu terminal from Start menu
wsl

# Check Docker
docker --version
# Should show: Docker version 20.x or newer
```

## Step 3: Setup Project in WSL

```bash
# Inside WSL Ubuntu terminal

# Update system
sudo apt update && sudo apt upgrade -y

# Install git
sudo apt install -y git

# Create workspace
mkdir -p ~/cardiac-valve-sim
cd ~/cardiac-valve-sim

# Clone repository (or download files)
git clone https://github.com/noahchang06/IBAMR.git
cd IBAMR/examples/cardiac_valve

# Or download as ZIP from Windows and copy to WSL
# Location: \\wsl$\Ubuntu-22.04\home\<username>\cardiac-valve-sim
```

## Step 4: Run Docker Container

```bash
# Pull IBAMR image
docker pull ibamr/ibamr:latest

# Start interactive container
docker run -it \
  --name cardiac-valve \
  -v ~/cardiac-valve-sim:/workspace \
  -p 8080:8080 \
  ibamr/ibamr:latest \
  /bin/bash
```

## Step 5: Setup Python Environment (Inside Container)

```bash
# Install Python packages
pip3 install numpy matplotlib scipy

# Navigate to project
cd /workspace/IBAMR/examples/cardiac_valve

# Generate geometry
python3 generate_valve_geometry.py --resolution 64 --severity healthy --visualize
```

## Step 6: Run Simulation

```bash
# Navigate to IBAMR examples
cd /ibamr/examples/IB/explicit/ex1

# Copy valve files
cp /workspace/IBAMR/examples/cardiac_valve/input2d .
cp /workspace/IBAMR/examples/cardiac_valve/valve2d_healthy_64.* .

# Run simulation
mpirun -np 4 ./main2d input2d
```

## Step 7: Access Files from Windows

Files are accessible from Windows File Explorer:

```
\\wsl$\Ubuntu-22.04\home\<username>\cardiac-valve-sim\
```

- Double-click PNG files to view
- Copy results to Windows desktop for easier access

---

# Method 2: WSL2 Native Build

## Step 1: Setup WSL2

Follow Steps 1.1-1.3 from Method 1.

## Step 2: Install Build Dependencies

```bash
# Open Ubuntu terminal
wsl

# Update system
sudo apt update && sudo apt upgrade -y

# Install build tools
sudo apt install -y \
  build-essential \
  cmake \
  git \
  wget \
  gfortran \
  libopenmpi-dev \
  openmpi-bin

# Install Python
sudo apt install -y \
  python3 \
  python3-pip \
  python3-venv

# Create virtual environment
python3 -m venv ~/cardiac-valve-env
source ~/cardiac-valve-env/bin/activate

# Install Python packages
pip install numpy scipy matplotlib pillow
```

## Step 3: Install Scientific Libraries

```bash
# HDF5
sudo apt install -y libhdf5-dev libhdf5-openmpi-dev

# Boost
sudo apt install -y libboost-all-dev

# Eigen
sudo apt install -y libeigen3-dev

# Silo
sudo apt install -y libsilo-dev
```

## Step 4: Install PETSc

```bash
cd ~/Downloads

# Download PETSc
wget https://ftp.mcs.anl.gov/pub/petsc/release-snapshots/petsc-3.18.0.tar.gz
tar -xzf petsc-3.18.0.tar.gz
cd petsc-3.18.0

# Configure
./configure \
  --prefix=$HOME/petsc \
  --with-cc=mpicc \
  --with-cxx=mpicxx \
  --with-fc=mpifort \
  --download-hypre \
  --download-fblaslapack \
  --with-debugging=0 \
  COPTFLAGS='-O3' \
  CXXOPTFLAGS='-O3' \
  FOPTFLAGS='-O3'

# Build (takes 30-60 minutes)
make PETSC_DIR=$PWD PETSC_ARCH=arch-linux-c-opt all

# Install
make PETSC_DIR=$PWD PETSC_ARCH=arch-linux-c-opt install

# Set environment variables
echo 'export PETSC_DIR=$HOME/petsc' >> ~/.bashrc
echo 'export PETSC_ARCH=arch-linux-c-opt' >> ~/.bashrc
source ~/.bashrc
```

## Step 5: Install SAMRAI

```bash
cd ~/Downloads

# Download SAMRAI
wget https://github.com/LLNL/SAMRAI/archive/refs/tags/v4.1.0.tar.gz
tar -xzf v4.1.0.tar.gz
cd SAMRAI-4.1.0

# Configure
./configure \
  --prefix=$HOME/samrai \
  --with-CXX=mpicxx \
  --with-CC=mpicc \
  --with-FC=mpifort \
  --with-hdf5=/usr

# Build (takes 20-40 minutes)
make -j$(nproc)
make install

# Set environment variable
echo 'export SAMRAI_DIR=$HOME/samrai' >> ~/.bashrc
source ~/.bashrc
```

## Step 6: Install libMesh

```bash
cd ~/Downloads

# Clone libMesh
git clone https://github.com/libMesh/libmesh.git
cd libmesh
git checkout v1.6.2

# Configure
./configure \
  --prefix=$HOME/libmesh \
  --with-methods="opt" \
  --enable-petsc \
  --with-petsc=$PETSC_DIR

# Build (takes 30-60 minutes)
make -j$(nproc)
make install

# Set environment variable
echo 'export LIBMESH_DIR=$HOME/libmesh' >> ~/.bashrc
source ~/.bashrc
```

## Step 7: Build IBAMR

```bash
cd ~/Downloads

# Clone IBAMR
git clone https://github.com/IBAMR/IBAMR.git
cd IBAMR

# Create build directory
mkdir build
cd build

# Configure
cmake .. \
  -DCMAKE_INSTALL_PREFIX=$HOME/ibamr \
  -DSAMRAI_ROOT=$SAMRAI_DIR \
  -DPETSC_ROOT=$PETSC_DIR \
  -DLIBMESH_ROOT=$LIBMESH_DIR \
  -DCMAKE_BUILD_TYPE=Release

# Build (takes 45-90 minutes)
make -j$(nproc)

# Install
make install
```

## Step 8: Setup and Run Project

```bash
# Copy project files
cp -r ~/cardiac-valve-sim/IBAMR/examples/cardiac_valve \
      ~/Downloads/IBAMR/examples/

# Navigate to build
cd ~/Downloads/IBAMR/build/examples/IB/explicit/ex1

# Copy valve files
cp ~/cardiac-valve-sim/IBAMR/examples/cardiac_valve/input2d .
cp ~/cardiac-valve-sim/IBAMR/examples/cardiac_valve/valve2d_healthy_64.* .

# Run simulation
mpirun -np 4 ./main2d input2d
```

---

# Method 3: Python Tools Only (Windows Native)

## Step 1: Install Python

### Option A: From Microsoft Store (Easiest)
1. Open Microsoft Store
2. Search "Python 3.11"
3. Click "Get" to install

### Option B: From python.org
1. Visit: https://www.python.org/downloads/
2. Download "Windows installer (64-bit)"
3. Run installer
4. ✓ Check "Add Python to PATH"
5. Click "Install Now"

## Step 2: Install Python Packages

Open Command Prompt or PowerShell:

```powershell
# Upgrade pip
python -m pip install --upgrade pip

# Install required packages
pip install numpy scipy matplotlib pillow
```

## Step 3: Download Project Files

```powershell
# Create directory
mkdir C:\cardiac-valve
cd C:\cardiac-valve

# Download files from GitHub or your source
# Using PowerShell:
Invoke-WebRequest -Uri [URL]/generate_valve_geometry.py -OutFile generate_valve_geometry.py
Invoke-WebRequest -Uri [URL]/visualize_geometry.py -OutFile visualize_geometry.py
Invoke-WebRequest -Uri [URL]/analyze_results.py -OutFile analyze_results.py
```

Or manually:
1. Download ZIP from GitHub
2. Extract to `C:\cardiac-valve`

## Step 4: Generate Geometries

```powershell
# Generate all severities
python generate_valve_geometry.py --resolution 64 --severity healthy --visualize
python generate_valve_geometry.py --resolution 64 --severity mild --visualize
python generate_valve_geometry.py --resolution 64 --severity moderate --visualize
python generate_valve_geometry.py --resolution 64 --severity severe --visualize
```

## Step 5: Create Visualizations

```powershell
# Compare all severities
python visualize_geometry.py --mode compare --severities healthy,mild,moderate,severe --output comparison.png

# View with default image viewer
start comparison.png
```

---

# Installing Windows X Server (for GUI in WSL)

If you want to run GUI applications from WSL:

## Step 1: Install VcXsrv

1. Download from: https://sourceforge.net/projects/vcxsrv/
2. Install with default options
3. Run XLaunch from Start menu
4. Select "Multiple windows", Display number: 0
5. Select "Start no client"
6. ✓ Check "Disable access control"
7. Finish

## Step 2: Configure WSL

```bash
# In WSL terminal
echo 'export DISPLAY=$(cat /etc/resolv.conf | grep nameserver | awk "{print \$2}"):0' >> ~/.bashrc
source ~/.bashrc

# Test with a GUI app
sudo apt install -y x11-apps
xeyes  # Should open a window
```

## Step 3: Run Visualization Tools

```bash
# Now you can use matplotlib GUI
python3 generate_valve_geometry.py --visualize
# Window should pop up
```

---

# Installing VisIt for Windows

## Method 1: VisIt Native Windows

1. Download from: https://visit-dav.github.io/visit-website/
2. Select "Windows 64-bit"
3. Run installer
4. Add to PATH (optional):
   ```powershell
   $env:Path += ";C:\Program Files\LLNL\VisIt 3.x\bin"
   ```

5. Open results:
   ```powershell
   visit C:\path\to\viz_IB2d\dumps.visit
   ```

## Method 2: VisIt in WSL

```bash
# In WSL terminal (requires X server running)
sudo apt install -y visit

# Open results
visit ~/cardiac-valve-sim/viz_IB2d/dumps.visit
```

---

# Troubleshooting

## Issue: WSL2 installation fails

**Solution**:
```powershell
# Run as Administrator
wsl --update
wsl --shutdown
wsl
```

## Issue: Docker Desktop won't start

**Solution**:
1. Ensure Virtualization is enabled in BIOS
2. Check Windows Features:
   - Control Panel → Programs → Turn Windows features on/off
   - ✓ Virtual Machine Platform
   - ✓ Windows Subsystem for Linux
3. Restart computer

## Issue: "Permission denied" in WSL

**Solution**:
```bash
# Fix permissions
chmod +x generate_valve_geometry.py visualize_geometry.py analyze_results.py
```

## Issue: Python module not found (Windows)

**Solution**:
```powershell
# Use pip, not pip3 on Windows
pip install numpy matplotlib scipy

# Or specify user installation
pip install --user numpy matplotlib scipy
```

## Issue: Docker runs out of memory

**Solution**:
- Docker Desktop → Settings → Resources
- Increase Memory to 8 GB
- Increase CPUs to 4+
- Click "Apply & Restart"

## Issue: Slow performance in WSL

**Solution**:
```bash
# Store files in Linux filesystem, not /mnt/c/
# Use ~/cardiac-valve-sim, NOT /mnt/c/Users/.../cardiac-valve

# Check location
pwd
# Should show: /home/<username>/... (fast)
# NOT: /mnt/c/... (slow)
```

## Issue: Cannot access WSL files from Windows

**Solution**:
```
File Explorer → Address bar → Type:
\\wsl$\Ubuntu-22.04\home\<username>\cardiac-valve-sim
```

Bookmark this location for easy access!

---

# Performance Tips for Windows

## WSL2 Optimization

```bash
# Create .wslconfig in Windows user directory
# C:\Users\<username>\.wslconfig

[wsl2]
memory=8GB
processors=4
swap=2GB
```

Restart WSL:
```powershell
wsl --shutdown
wsl
```

## Parallel Execution

```bash
# Check CPU cores
nproc

# Use appropriate MPI processes
mpirun -np 4 ./main2d input2d  # For 4+ core systems
```

## File Performance

```bash
# Keep files in Linux filesystem for speed
~/cardiac-valve-sim/  # Fast
/mnt/c/cardiac-valve/ # Slow (crosses filesystems)
```

---

# GUI Options for Results

## Option 1: VcXsrv (Free)
- Runs X11 apps from WSL
- Good for matplotlib, VisIt

## Option 2: Windows Native Viewers
- Copy PNG files to Windows
- View with Photos app
- Process in Paint, GIMP, etc.

## Option 3: VS Code Remote
- Install VS Code
- Install "Remote - WSL" extension
- Open WSL folder in VS Code
- View images inline

---

# Quick Command Reference

```powershell
# Windows PowerShell commands

# Start WSL
wsl

# Open WSL directory in Explorer
explorer.exe \\wsl$\Ubuntu-22.04\home\<username>\cardiac-valve-sim

# Copy from WSL to Windows Desktop
cp ~/cardiac-valve-sim/comparison.png /mnt/c/Users/<username>/Desktop/
```

```bash
# WSL/Ubuntu commands

# Activate Python environment
source ~/cardiac-valve-env/bin/activate

# Start Docker container
docker start -i cardiac-valve

# Generate geometries
python3 generate_valve_geometry.py --resolution 64 --severity healthy --visualize

# Run simulation
mpirun -np 4 ./main2d input2d

# Stop WSL (from PowerShell)
wsl --shutdown
```

---

# Recommended Workflow for Windows

**Best approach**:
1. Use WSL2 + Docker (Method 1)
2. Edit files in Windows (VS Code)
3. Run simulations in Docker container
4. View results in Windows

**File organization**:
```
Windows side:
C:\Users\<username>\cardiac-valve\  (for editing)

WSL side:
~/cardiac-valve-sim/  (for running)

Sync between them:
cp -r /mnt/c/Users/<username>/cardiac-valve/* ~/cardiac-valve-sim/
```

---

# VS Code Integration (Recommended)

## Setup

1. Install VS Code: https://code.visualstudio.com/
2. Install extensions:
   - "Remote - WSL"
   - "Python"
   - "Docker"

3. Open WSL folder:
   - Ctrl+Shift+P → "WSL: Open Folder in WSL"
   - Navigate to `~/cardiac-valve-sim`

4. Edit and run from integrated terminal!

---

# Next Steps

After successful installation:

1. **Test Python setup**:
   ```powershell
   python generate_valve_geometry.py --resolution 32 --severity healthy
   ```

2. **Test WSL + Docker**:
   ```bash
   wsl
   docker run hello-world
   ```

3. **Run small simulation**:
   ```bash
   # Edit input2d: MAX_LEVELS=3, END_TIME=0.1
   mpirun -np 2 ./main2d input2d
   ```

4. **Full simulation**:
   ```bash
   mpirun -np 4 ./main2d input2d
   ```

---

# Additional Resources

- **WSL Documentation**: https://docs.microsoft.com/en-us/windows/wsl/
- **Docker Desktop**: https://docs.docker.com/desktop/windows/
- **IBAMR**: https://ibamr.github.io
- **Python on Windows**: https://docs.python.org/3/using/windows.html

---

# Support

**WSL issues**: https://github.com/microsoft/WSL/issues
**Docker issues**: Docker Desktop logs (Settings → Troubleshoot)
**Python issues**: Check installed packages with `pip list`
**IBAMR issues**: https://github.com/IBAMR/IBAMR/issues

---

*Estimated total time: 1-3 hours depending on method chosen*
*Tested on: Windows 10 21H2, Windows 11 22H2*
*Last updated: 2025-10-20*
