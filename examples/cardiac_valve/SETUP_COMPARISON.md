# Platform Comparison Guide

Quick reference to help you choose the best setup method for your system.

---

## Quick Decision Tree

```
Do you have Windows?
├─ Yes → Use WSL2 + Docker (Method 1 in SETUP_WINDOWS.md)
└─ No → Do you have macOS?
    ├─ Yes → Do you have Apple Silicon (M1/M2/M3)?
    │   ├─ Yes → Use Docker (Method 1 in SETUP_MACOS.md)
    │   └─ No → Native Build or Docker (Methods 1 or 2)
    └─ No → You're on Linux → Native Build (fastest)

Just want to generate geometries (no simulation)?
└─ Use Python Tools Only (Method 3 on any platform)
```

---

## Platform Comparison

| Feature | Windows | macOS Intel | macOS Apple Silicon | Linux (Ubuntu) |
|---------|---------|-------------|---------------------|----------------|
| **Ease of Setup** | ⭐⭐⭐ WSL2 | ⭐⭐⭐⭐ Docker | ⭐⭐⭐⭐ Docker | ⭐⭐⭐⭐⭐ Native |
| **Performance** | ⭐⭐⭐ WSL overhead | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Setup Time** | 1-2 hours | 1-2 hours | 1-2 hours | 2-3 hours |
| **Disk Space** | 25 GB | 20 GB | 20 GB | 15 GB |
| **Recommended Method** | WSL2 + Docker | Docker | Docker | Native Build |

---

## Method Comparison

### Method 1: Docker (All Platforms)

**Pros**:
- ✅ Fastest setup (1-2 hours)
- ✅ Pre-configured environment
- ✅ Consistent across platforms
- ✅ Easy to clean up (just delete container)
- ✅ No dependency conflicts

**Cons**:
- ❌ Slight performance overhead (~5-10%)
- ❌ Requires Docker Desktop (paid for large companies)
- ❌ Extra memory usage for containers
- ❌ File I/O can be slower

**Best for**: Beginners, testing, quick prototyping

**Installation Time**:
- Windows: 1-2 hours (includes WSL2 setup)
- macOS: 1 hour
- Linux: 30 minutes

---

### Method 2: Native Build

**Pros**:
- ✅ Best performance (10-20% faster)
- ✅ Full control over compilation
- ✅ Easier debugging
- ✅ Direct file access

**Cons**:
- ❌ Long setup (2-4 hours)
- ❌ Potential dependency conflicts
- ❌ Platform-specific issues
- ❌ Harder to reproduce on other machines

**Best for**: Production runs, researchers, developers

**Installation Time**:
- Windows (WSL2): 3-4 hours
- macOS: 3-4 hours
- Linux: 2-3 hours

---

### Method 3: Python Tools Only

**Pros**:
- ✅ Very quick setup (15-30 minutes)
- ✅ No IBAMR compilation needed
- ✅ Works on any OS
- ✅ Lightweight

**Cons**:
- ❌ Cannot run simulations
- ❌ Only geometry generation and visualization
- ❌ No fluid-structure interaction

**Best for**: Learning, visualization only, presentations

**Installation Time**: 15-30 minutes (all platforms)

---

## Detailed Platform Guides

Click to jump to platform-specific instructions:

- **[Windows Setup Guide](SETUP_WINDOWS.md)** - WSL2, Docker, or Python-only
- **[macOS Setup Guide](SETUP_MACOS.md)** - Docker, native build, or Python-only

---

## Performance Benchmarks

Estimated time for **1 cardiac cycle simulation** (64 pts/leaflet, 5 AMR levels):

### Windows (WSL2 + Docker)
- **4 cores**: 1.5-2 hours
- **8 cores**: 45-60 minutes
- **16 cores**: 25-35 minutes

### macOS Intel (Docker)
- **4 cores**: 1.5-2 hours
- **8 cores**: 45-60 minutes
- **16 cores**: 25-35 minutes

### macOS Apple Silicon (Docker ARM)
- **8 cores (M1)**: 40-55 minutes
- **10 cores (M2)**: 35-45 minutes
- **12+ cores (M3)**: 25-35 minutes

### Linux Native Build (Best Performance)
- **4 cores**: 1-1.5 hours
- **8 cores**: 30-45 minutes
- **16 cores**: 18-25 minutes
- **32 cores**: 12-18 minutes

*Note: Times vary based on CPU speed, memory, and disk I/O*

---

## Storage Requirements

### Full Installation

| Component | Windows | macOS | Linux |
|-----------|---------|-------|-------|
| WSL2 | 5 GB | - | - |
| Docker | 3 GB | 3 GB | 2 GB |
| IBAMR + deps | 8 GB | 8 GB | 6 GB |
| Build files | 4 GB | 4 GB | 3 GB |
| Project files | 0.5 GB | 0.5 GB | 0.5 GB |
| Simulation output | 2-10 GB | 2-10 GB | 2-10 GB |
| **Total** | **22-30 GB** | **17-25 GB** | **13-21 GB** |

### Python Tools Only

| Component | All Platforms |
|-----------|---------------|
| Python + packages | 500 MB |
| Project files | 500 KB |
| Generated geometries | 100 KB |
| Visualizations | 1 MB |
| **Total** | **~600 MB** |

---

## Hardware Recommendations

### Minimum (Educational Use)

- **CPU**: 4 cores @ 2.0 GHz
- **RAM**: 8 GB
- **Storage**: 25 GB free space
- **Expected simulation time**: 2-4 hours

### Recommended (Research Use)

- **CPU**: 8+ cores @ 3.0 GHz
- **RAM**: 16 GB
- **Storage**: 50 GB SSD
- **Expected simulation time**: 30-60 minutes

### Optimal (Production Use)

- **CPU**: 16+ cores @ 3.5 GHz
- **RAM**: 32+ GB
- **Storage**: 100+ GB NVMe SSD
- **Expected simulation time**: 15-30 minutes

---

## Software Versions Tested

### Windows
- Windows 10 21H2, Windows 11 22H2
- WSL2 with Ubuntu 22.04
- Docker Desktop 4.25+
- Python 3.10-3.11

### macOS
- macOS 12 (Monterey), macOS 13 (Ventura), macOS 14 (Sonoma)
- Docker Desktop 4.25+ (Intel and Apple Silicon)
- Homebrew 4.0+
- Python 3.10-3.11

### Linux
- Ubuntu 20.04 LTS, 22.04 LTS
- Debian 11, 12
- RHEL 8, 9
- Python 3.8-3.11

---

## Common Issues by Platform

### Windows-Specific

**Issue**: WSL2 won't enable
- **Cause**: Virtualization disabled in BIOS
- **Fix**: Enable VT-x (Intel) or AMD-V in BIOS settings

**Issue**: Docker Desktop stuck on "Starting"
- **Cause**: WSL2 backend not initialized
- **Fix**: `wsl --shutdown`, restart Docker Desktop

**Issue**: Files in /mnt/c/ are very slow
- **Cause**: Cross-filesystem access
- **Fix**: Store files in Linux filesystem (`~/`)

### macOS-Specific

**Issue**: "Library not loaded" errors
- **Cause**: Homebrew paths not configured
- **Fix**: `eval "$(/opt/homebrew/bin/brew shellenv)"`

**Issue**: Docker on Apple Silicon crashes
- **Cause**: Incompatible image architecture
- **Fix**: Use `--platform linux/arm64` flag

**Issue**: Compilation fails on macOS
- **Cause**: Xcode Command Line Tools missing
- **Fix**: `xcode-select --install`

### Cross-Platform

**Issue**: Python module not found
- **Windows**: Use `pip` (not `pip3`)
- **macOS/Linux**: Use `pip3` (or `pip` in virtual environment)

**Issue**: Out of memory during simulation
- **Docker**: Increase memory limit in Docker Desktop settings
- **Native**: Reduce AMR levels or resolution

---

## Network Requirements

### During Installation

- **Docker images**: 2-5 GB download
- **Dependencies** (native build): 500 MB - 2 GB
- **Python packages**: 100-500 MB

**Estimated download time**:
- Fast connection (100 Mbps): 5-15 minutes
- Medium connection (25 Mbps): 20-45 minutes
- Slow connection (10 Mbps): 1-2 hours

### During Use

- No internet required after installation
- Optional: VisIt download (1-2 GB)

---

## Upgrading Between Methods

### From Python-Only → Docker

```bash
# Your geometry files are compatible!
# Just start Docker and copy files

# Windows (PowerShell)
cp C:\cardiac-valve\*.vertex \\wsl$\Ubuntu-22.04\home\<user>\cardiac-valve-sim\

# macOS
cp ~/cardiac-valve/*.vertex ~/cardiac-valve-sim/
```

### From Docker → Native Build

```bash
# Copy entire project
cp -r /workspace/IBAMR ~/ibamr-native

# Rebuild IBAMR natively
# Follow Method 2 instructions for your platform
```

### From Native → Docker

```bash
# Your input files work in Docker too
# Just mount your directory

docker run -v ~/ibamr-native:/workspace ...
```

---

## Installation Checklist

### Pre-Installation

- [ ] Check system requirements (RAM, disk space)
- [ ] Enable virtualization (Windows: BIOS, macOS: automatic)
- [ ] Ensure stable internet connection
- [ ] Backup important data
- [ ] Allocate 2-4 hours for installation

### Post-Installation

- [ ] Test Python import: `python -c "import numpy; print('OK')"`
- [ ] Test Docker: `docker run hello-world`
- [ ] Generate test geometry
- [ ] Run small test simulation (low resolution)
- [ ] Visualize results

### Verification

```bash
# Test geometry generation
python3 generate_valve_geometry.py --resolution 32 --severity healthy

# Test visualization
python3 visualize_geometry.py --mode single --severity healthy

# Test simulation (if IBAMR installed)
./main2d input2d  # Should run without errors

# Check output files
ls viz_*/  # Should contain dump files
```

---

## Getting Help

### Platform-Specific Support

- **Windows**: [SETUP_WINDOWS.md](SETUP_WINDOWS.md) → Troubleshooting section
- **macOS**: [SETUP_MACOS.md](SETUP_MACOS.md) → Troubleshooting section

### General Support

- **IBAMR**: https://github.com/IBAMR/IBAMR/issues
- **Docker**: https://docs.docker.com/
- **WSL**: https://github.com/microsoft/WSL/issues

### Project Support

- **Documentation**: README.md, PROJECT_SUMMARY.md
- **Quick Start**: QUICKSTART.md

---

## Recommended Path for Different Users

### Medical Students / Researchers (No Programming Background)

1. Start with **Method 3** (Python Tools Only)
2. Generate geometries and visualizations
3. Learn about the physics
4. Move to Docker when ready for simulations

**Total time**: 30 min (Method 3) + 1 hour (Docker later)

### Graduate Students / Postdocs (Computational Background)

1. Use **Method 1** (Docker) immediately
2. Run simulations and analyze results
3. Build natively (Method 2) if needed for production
4. Customize and extend the project

**Total time**: 1-2 hours (Docker) + 3 hours (Native, optional)

### Faculty / Developers (Full Control Needed)

1. Go straight to **Method 2** (Native Build)
2. Optimize compilation for your hardware
3. Modify IBAMR source if needed
4. Run large parameter studies

**Total time**: 3-4 hours (one-time setup)

---

## Cost Comparison

### Software Licenses

| Software | Cost | Notes |
|----------|------|-------|
| Windows | $0-199 | Usually pre-installed |
| macOS | $0 | Included with Mac |
| Linux | Free | Open source |
| Docker Desktop | Free* | *For personal/education/small business |
| IBAMR | Free | Open source (BSD license) |
| Python | Free | Open source |
| VisIt | Free | Open source |

**Total software cost**: $0 for most users

### Hardware Costs (if upgrading)

- **Budget setup** (8 GB RAM, 4 cores): Usable, but slow
- **Recommended setup** (16 GB RAM, 8 cores): $800-1500
- **High-end setup** (32 GB RAM, 16+ cores): $2000-4000

### Cloud Computing (Alternative)

- **AWS EC2 c6i.4xlarge** (16 vCPU, 32 GB): ~$0.68/hour
- **Run time for 4 severities**: ~2-3 hours = $2-3 per study
- **Good for**: Occasional use, no hardware investment

---

## Summary Table

| Criterion | Windows WSL2+Docker | macOS Docker | macOS Native | Linux Native | Python-Only |
|-----------|---------------------|--------------|--------------|--------------|-------------|
| **Setup Time** | 1-2 hrs | 1 hr | 3-4 hrs | 2-3 hrs | 15 min |
| **Performance** | Good | Good | Excellent | Best | N/A |
| **Ease of Use** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Flexibility** | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| **Can Simulate** | ✅ | ✅ | ✅ | ✅ | ❌ |
| **Can Visualize** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Recommended** | First-time | First-time | Production | Production | Quick start |

---

**Choose your platform and follow the detailed guide:**
- **[Windows Users → SETUP_WINDOWS.md](SETUP_WINDOWS.md)**
- **[Mac Users → SETUP_MACOS.md](SETUP_MACOS.md)**

*Good luck with your installation!*
