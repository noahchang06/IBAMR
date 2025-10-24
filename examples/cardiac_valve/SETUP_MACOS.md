# macOS Setup Guide - Cardiac Valve Simulation

Complete installation guide for running the cardiac valve visualization project on macOS.

---

## Prerequisites

- **macOS**: 10.15 (Catalina) or newer
- **RAM**: 8 GB minimum, 16 GB recommended
- **Disk Space**: 20 GB free space
- **Time**: 2-4 hours for full installation

---

## Installation Methods

Choose one:
- **Method 1**: Docker (Easiest, ~1 hour)
- **Method 2**: Native Build (Advanced, ~3 hours)
- **Method 3**: Python Tools Only (Quick start, ~15 minutes)

---

# Method 1: Docker Installation (Recommended)

## Step 1: Install Docker Desktop

### 1.1 Download Docker
```bash
# Visit Docker website
open https://www.docker.com/products/docker-desktop/

# Or use Homebrew
brew install --cask docker
```

### 1.2 Start Docker Desktop
- Open Docker Desktop from Applications
- Wait for Docker to start (whale icon in menu bar)

### 1.3 Verify Installation
```bash
docker --version
# Should show: Docker version 20.x or newer
```

## Step 2: Pull IBAMR Docker Image

```bash
# Pull pre-built IBAMR image
docker pull ibamr/ibamr:latest

# Verify image
docker images | grep ibamr
```

## Step 3: Clone the Project

```bash
# Create workspace directory
mkdir -p ~/cardiac-valve-sim
cd ~/cardiac-valve-sim

# Clone repository (if on GitHub)
git clone https://github.com/noahchang06/IBAMR.git
cd IBAMR/examples/cardiac_valve

# Or download files directly
curl -o cardiac_valve.zip [URL to your files]
unzip cardiac_valve.zip
```

## Step 4: Run Docker Container

```bash
# Start interactive container with project mounted
docker run -it \
  --name cardiac-valve \
  -v ~/cardiac-valve-sim:/workspace \
  -p 8080:8080 \
  ibamr/ibamr:latest \
  /bin/bash

# You're now inside the container!
```

## Step 5: Setup Python Environment (Inside Container)

```bash
# Install Python packages
pip3 install numpy matplotlib scipy

# Navigate to project
cd /workspace/IBAMR/examples/cardiac_valve

# Test geometry generation
python3 generate_valve_geometry.py --resolution 64 --severity healthy --visualize
```

## Step 6: Run Simulation (Inside Container)

```bash
# Navigate to IBAMR examples
cd /ibamr/examples/IB/explicit/ex1

# Copy valve files
cp /workspace/IBAMR/examples/cardiac_valve/input2d .
cp /workspace/IBAMR/examples/cardiac_valve/valve2d_healthy_64.* .

# Run simulation (single core)
./main2d input2d

# Or parallel (4 cores)
mpirun -np 4 ./main2d input2d
```

## Step 7: View Results on macOS

Exit container and visualize on host:

```bash
# Exit container
exit

# Results are in mounted directory
cd ~/cardiac-valve-sim/IBAMR/examples/cardiac_valve

# View with Preview
open valve_full_comparison.png

# Or install Python viewer
pip3 install matplotlib pillow
python3 -c "from PIL import Image; Image.open('valve_full_comparison.png').show()"
```

---

# Method 2: Native macOS Build

## Step 1: Install Homebrew

```bash
# Install Homebrew if not present
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Add to PATH (for Apple Silicon Macs)
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
eval "$(/opt/homebrew/bin/brew shellenv)"
```

## Step 2: Install Dependencies

### 2.1 System Tools
```bash
brew install git cmake wget
brew install gcc open-mpi
```

### 2.2 Python Environment
```bash
# Install Python 3
brew install python@3.11

# Create virtual environment
python3 -m venv ~/cardiac-valve-env
source ~/cardiac-valve-env/bin/activate

# Install Python packages
pip install numpy scipy matplotlib pillow
```

### 2.3 Scientific Libraries
```bash
# HDF5
brew install hdf5

# Boost
brew install boost

# Eigen
brew install eigen

# Silo (for visualization)
brew install silo
```

## Step 3: Install PETSc

```bash
cd ~/Downloads

# Download PETSc
wget https://ftp.mcs.anl.gov/pub/petsc/release-snapshots/petsc-3.18.0.tar.gz
tar -xzf petsc-3.18.0.tar.gz
cd petsc-3.18.0

# Configure PETSc
./configure \
  --prefix=$HOME/petsc \
  --with-cc=gcc-13 \
  --with-cxx=g++-13 \
  --with-fc=gfortran-13 \
  --download-hypre \
  --download-fblaslapack \
  --with-debugging=0 \
  COPTFLAGS='-O3' \
  CXXOPTFLAGS='-O3' \
  FOPTFLAGS='-O3'

# Build and install
make PETSC_DIR=$PWD PETSC_ARCH=arch-darwin-c-opt all
make PETSC_DIR=$PWD PETSC_ARCH=arch-darwin-c-opt install

# Set environment variables
echo 'export PETSC_DIR=$HOME/petsc' >> ~/.zshrc
echo 'export PETSC_ARCH=arch-darwin-c-opt' >> ~/.zshrc
source ~/.zshrc
```

**Time**: ~30-60 minutes

## Step 4: Install SAMRAI

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
  --with-hdf5=/opt/homebrew/opt/hdf5

# Build and install
make -j4
make install

# Set environment variable
echo 'export SAMRAI_DIR=$HOME/samrai' >> ~/.zshrc
source ~/.zshrc
```

**Time**: ~20-40 minutes

## Step 5: Install libMesh

```bash
cd ~/Downloads

# Download libMesh
git clone https://github.com/libMesh/libmesh.git
cd libmesh
git checkout v1.6.2

# Configure
./configure \
  --prefix=$HOME/libmesh \
  --with-methods="opt" \
  --enable-petsc \
  --with-petsc=$PETSC_DIR

# Build and install
make -j4
make install

# Set environment variable
echo 'export LIBMESH_DIR=$HOME/libmesh' >> ~/.zshrc
source ~/.zshrc
```

**Time**: ~30-60 minutes

## Step 6: Build IBAMR

```bash
cd ~/Downloads

# Clone IBAMR
git clone https://github.com/IBAMR/IBAMR.git
cd IBAMR

# Create build directory
mkdir build
cd build

# Configure with CMake
cmake .. \
  -DCMAKE_INSTALL_PREFIX=$HOME/ibamr \
  -DSAMRAI_ROOT=$SAMRAI_DIR \
  -DPETSC_ROOT=$PETSC_DIR \
  -DLIBMESH_ROOT=$LIBMESH_DIR \
  -DCMAKE_BUILD_TYPE=Release

# Build
make -j4

# Install
make install
```

**Time**: ~45-90 minutes

## Step 7: Setup Cardiac Valve Project

```bash
# Copy project files to IBAMR
cp -r ~/cardiac-valve-sim/IBAMR/examples/cardiac_valve \
      ~/Downloads/IBAMR/examples/

# Or clone from GitHub
cd ~/Downloads/IBAMR/examples
git clone [your-repo-url] cardiac_valve
```

## Step 8: Run Simulation

```bash
# Navigate to project
cd ~/Downloads/IBAMR/build/examples/cardiac_valve

# Copy geometry files
cp ../../../examples/cardiac_valve/*.py .
cp ../../../examples/cardiac_valve/input2d .

# Generate geometries
python3 generate_valve_geometry.py --resolution 64 --severity healthy

# Run simulation (use existing IB example executable)
cd ~/Downloads/IBAMR/build/examples/IB/explicit/ex1
cp ~/Downloads/IBAMR/examples/cardiac_valve/input2d .
cp ~/Downloads/IBAMR/examples/cardiac_valve/valve2d_healthy_64.* .

./main2d input2d
```

---

# Method 3: Python Tools Only (Quick Start)

If you only want to generate and visualize geometries (no simulation):

## Step 1: Install Python
```bash
# Install Python 3 via Homebrew
brew install python@3.11

# Or download from python.org
open https://www.python.org/downloads/
```

## Step 2: Install Python Packages
```bash
pip3 install numpy scipy matplotlib pillow
```

## Step 3: Download Project Files
```bash
# Create directory
mkdir -p ~/cardiac-valve
cd ~/cardiac-valve

# Download Python scripts (adjust URLs)
curl -O [URL]/generate_valve_geometry.py
curl -O [URL]/visualize_geometry.py
curl -O [URL]/analyze_results.py
```

## Step 4: Generate Geometries
```bash
# Generate all severities
python3 generate_valve_geometry.py --resolution 64 --severity healthy --visualize
python3 generate_valve_geometry.py --resolution 64 --severity mild --visualize
python3 generate_valve_geometry.py --resolution 64 --severity moderate --visualize
python3 generate_valve_geometry.py --resolution 64 --severity severe --visualize
```

## Step 5: Create Comparison
```bash
# Compare all severities
python3 visualize_geometry.py --mode compare \
  --severities healthy,mild,moderate,severe \
  --output comparison.png

# View result
open comparison.png
```

---

# Installing VisIt for Visualization

## Option 1: Pre-built Binary
```bash
# Download from VisIt website
open https://visit-dav.github.io/visit-website/

# Download macOS .dmg file
# Drag VisIt to Applications

# Run VisIt
/Applications/VisIt.app/Contents/MacOS/VisIt
```

## Option 2: Homebrew
```bash
brew install --cask visit
```

## Using VisIt
```bash
# After simulation completes, open results
visit ~/cardiac-valve-sim/viz_IB2d/dumps.visit
```

---

# Troubleshooting

## Issue: "Command not found: brew"
**Solution**: Install Homebrew (see Step 1)

## Issue: "Library not loaded: libmpi.dylib"
**Solution**:
```bash
brew reinstall open-mpi
export DYLD_LIBRARY_PATH=/opt/homebrew/lib:$DYLD_LIBRARY_PATH
```

## Issue: "Python module not found"
**Solution**:
```bash
# Use pip3, not pip
pip3 install --user numpy matplotlib scipy
```

## Issue: Docker container won't start
**Solution**:
```bash
# Increase Docker memory limit
# Docker Desktop → Settings → Resources → Memory: 8 GB
# Restart Docker
```

## Issue: Compilation errors with native build
**Solution**:
```bash
# Ensure Xcode Command Line Tools installed
xcode-select --install

# Use correct compiler
export CC=gcc-13
export CXX=g++-13
export FC=gfortran-13
```

## Issue: Python visualization doesn't display
**Solution**:
```bash
# Install backend for matplotlib
pip3 install pillow

# Or save to file instead
python3 generate_valve_geometry.py --visualize
# Opens PNG file automatically
```

---

# Performance Tips for macOS

## Apple Silicon (M1/M2/M3) Specific

```bash
# Use ARM-optimized packages
arch -arm64 brew install python numpy

# For Docker, use ARM images when available
docker pull --platform linux/arm64 ibamr/ibamr:latest
```

## Parallel Execution

```bash
# Check available cores
sysctl -n hw.ncpu

# Use appropriate MPI processes (typically ncpu - 1)
mpirun -np 7 ./main2d input2d  # For 8-core system
```

## Memory Management

```bash
# Check available memory
sysctl hw.memsize

# Monitor during simulation
top -o MEM
```

---

# Quick Command Reference

```bash
# Activate Python environment
source ~/cardiac-valve-env/bin/activate

# Start Docker container
docker start -i cardiac-valve

# Generate geometries
python3 generate_valve_geometry.py --resolution 64 --severity healthy --visualize

# Compare all severities
python3 visualize_geometry.py --mode compare

# Run simulation (in Docker)
docker exec -it cardiac-valve bash
cd /ibamr/examples/IB/explicit/ex1
mpirun -np 4 ./main2d input2d

# View results
open valve_full_comparison.png
visit viz_IB2d/dumps.visit
```

---

# Recommended Workflow

**For beginners**:
1. Start with Method 3 (Python only)
2. Generate geometries and visualizations
3. Move to Docker (Method 1) when ready to simulate

**For researchers**:
1. Use Docker (Method 1) initially
2. Build natively (Method 2) for production runs
3. Optimize for your specific Mac hardware

**For developers**:
1. Native build (Method 2)
2. Full control over compilation options
3. Easier debugging and development

---

# Next Steps

After successful installation:

1. **Test geometry generation**:
   ```bash
   python3 generate_valve_geometry.py --resolution 32 --severity healthy
   ```

2. **Run quick visualization**:
   ```bash
   python3 visualize_geometry.py --mode compare
   ```

3. **Run small test simulation** (low resolution):
   ```bash
   # Edit input2d: Set MAX_LEVELS=3, END_TIME=0.1
   ./main2d input2d
   ```

4. **Full production run**:
   ```bash
   # Use default input2d settings
   mpirun -np 4 ./main2d input2d
   ```

---

# Additional Resources

- **IBAMR Documentation**: https://ibamr.github.io
- **Homebrew Packages**: https://formulae.brew.sh
- **Docker Documentation**: https://docs.docker.com/desktop/mac/
- **VisIt User Manual**: https://visit-sphinx-github-user-manual.readthedocs.io

---

# Support

**Installation issues**: Check IBAMR GitHub issues
**Python errors**: Verify package versions with `pip3 list`
**Docker problems**: Check Docker Desktop logs
**macOS-specific**: Check compatibility with your macOS version

---

*Estimated total time: 1-4 hours depending on method chosen*
*Last updated: 2025-10-20*
