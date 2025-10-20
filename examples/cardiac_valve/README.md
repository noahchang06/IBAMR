# Cardiac Valve Disease Visualization Project

## Overview

This project simulates blood flow through an aortic valve using IBAMR's Immersed Boundary (IB) method. The simulation models fluid-structure interaction between blood and valve leaflets under physiological conditions, with support for different disease severities (healthy to severe stenosis).

## Real-World Application

**Clinical Impact**: This simulation helps visualize:
- Blood flow patterns through diseased heart valves
- Pressure gradients across stenotic valves
- Vortex formation and turbulence
- Wall shear stress on leaflets
- Effective orifice area during cardiac cycle

**Use Cases**:
- Surgical planning (repair vs. replacement decisions)
- Patient education (visualizing their specific condition)
- Medical training (teaching hemodynamics)
- Research (understanding disease progression)

## Project Structure

```
cardiac_valve/
├── README.md                          # This file
├── generate_valve_geometry.py         # Python script to generate valve geometries
├── input2d                            # IBAMR configuration file
├── run_simulation.sh                  # Helper script to run simulations
├── visualize_geometry.py              # Geometry visualization script
└── [Generated files]
    ├── valve2d_healthy_64.vertex      # Healthy valve vertices
    ├── valve2d_healthy_64.spring      # Healthy valve springs
    ├── valve2d_healthy_64.beam        # Healthy valve beams
    ├── valve2d_severe_64.*            # Severe stenosis geometry
    └── *.png                          # Geometry visualizations
```

## Quick Start

### 1. Generate Valve Geometries

Generate geometries for different disease severities:

```bash
# Healthy valve
python3 generate_valve_geometry.py --resolution 64 --severity healthy --visualize

# Mild stenosis
python3 generate_valve_geometry.py --resolution 64 --severity mild --visualize

# Moderate stenosis
python3 generate_valve_geometry.py --resolution 64 --severity moderate --visualize

# Severe stenosis
python3 generate_valve_geometry.py --resolution 64 --severity severe --visualize
```

**Parameters**:
- `--resolution`: Points per leaflet (32, 64, 128) - higher = more accurate but slower
- `--severity`: Disease level (healthy, mild, moderate, severe)
- `--visualize`: Generate PNG visualization of geometry

### 2. Understand the Configuration

The `input2d` file contains simulation parameters:

**Physical Parameters** (physiologically accurate):
- Blood density: 1.06 g/cm³
- Blood viscosity: 0.035 Poise (0.0035 Pa·s)
- Peak velocity: 100 cm/s (during systole)
- Valve diameter: 2 cm
- Reynolds number: ~6000

**Computational Parameters**:
- Domain: 12 cm × 12 cm (valve centered)
- AMR levels: 5 (adaptive mesh refinement)
- Time: 2 cardiac cycles (1.6 seconds at 75 bpm)
- CFL: 0.3
- Delta function: IB_4 (4-point stencil)

**Boundary Conditions**:
- Inflow (left): Pulsatile flow (systole 0.3s, diastole 0.5s)
- Outflow (right): Open boundary
- Top/Bottom: No-slip walls

### 3. Run the Simulation

Option A: Using existing IB example executable (if IBAMR is compiled):

```bash
# Navigate to the IB example directory
cd /path/to/IBAMR/build/examples/IB/explicit/ex1

# Copy our files
cp /home/user/IBAMR/examples/cardiac_valve/input2d .
cp /home/user/IBAMR/examples/cardiac_valve/valve2d_healthy_64.* .

# Run simulation (single processor)
./main2d input2d

# Run parallel (4 processors)
mpirun -np 4 ./main2d input2d
```

Option B: Compile and run directly:

```bash
cd /home/user/IBAMR/examples/cardiac_valve
# [Build instructions depend on IBAMR installation]
```

### 4. Visualize Results

Use VisIt to visualize the output:

```bash
visit viz_valve2d/dumps.visit
```

**Recommended Visualizations**:
1. **Velocity field**: Pseudocolor of velocity magnitude + vector glyphs
2. **Pressure**: Pseudocolor of pressure + contour lines
3. **Vorticity**: Pseudocolor showing vortex formation
4. **Streamlines**: Particle traces through valve
5. **Structure**: Valve leaflet positions over time

## Geometry Details

### Valve Structure

The aortic valve is modeled with **three leaflets** (cusps) in 2D:
- Each leaflet: 64 vertices (default)
- Total: 192 vertices, 210 springs, 186 beams
- Annulus radius: 1.0 cm
- Leaflet length: 1.2 cm (varies with severity)

### Disease Severity Parameters

| Severity | Spring Stiffness | Beam Rigidity | Leaflet Length | Mobility |
|----------|------------------|---------------|----------------|----------|
| Healthy  | 5.0e2           | 1.0e-2        | 100%           | 100%     |
| Mild     | 8.0e2           | 2.0e-2        | 95%            | 90%      |
| Moderate | 1.5e3           | 5.0e-2        | 85%            | 70%      |
| Severe   | 3.0e3           | 1.0e-1        | 70%            | 40%      |

**Interpretation**:
- **Spring stiffness**: Higher = more calcified/rigid tissue
- **Beam rigidity**: Higher = less flexible leaflets
- **Leaflet length**: Shorter = restricted opening (stenosis)
- **Mobility**: Lower = reduced ability to open fully

## Expected Results

### Healthy Valve
- Peak velocity: ~100 cm/s through center
- Smooth flow pattern during systole
- Complete leaflet opening (minimal obstruction)
- Small vortices at leaflet tips
- Pressure drop: <10 mmHg

### Severe Stenosis
- Peak velocity: 300-500 cm/s (jet through narrow opening)
- Turbulent flow downstream of valve
- Restricted leaflet opening (60-70% area reduction)
- Large vortices and recirculation zones
- Pressure drop: >40 mmHg
- High wall shear stress on leaflets

## Clinical Metrics to Extract

From simulation results, calculate:

1. **Effective Orifice Area (EOA)**: Narrowest flow cross-section
2. **Pressure Gradient**: Peak and mean pressure drop
3. **Peak Jet Velocity**: Maximum velocity through valve
4. **Regurgitant Volume**: Backflow during diastole
5. **Wall Shear Stress**: Risk zones for thrombosis

## Customization

### Modify Flow Conditions

Edit `input2d` to change:

```
CARDIAC_CYCLE = 0.8        // Heart rate: 60/CARDIAC_CYCLE bpm
PEAK_VELOCITY = 100.0      // Increase for exercise conditions
SYSTOLE_DURATION = 0.24    // Adjust systolic duration
```

### Modify Valve Geometry

Edit `generate_valve_geometry.py`:
- Change `annulus_radius` for valve size
- Adjust `n_leaflets` for different valve types
- Modify curvature functions for shape

### Adjust Resolution

Higher resolution for accuracy (slower):
```bash
python3 generate_valve_geometry.py --resolution 128 --severity healthy
```

Lower resolution for quick tests:
```bash
python3 generate_valve_geometry.py --resolution 32 --severity healthy
```

## Output Files

After simulation:

```
viz_valve2d/              # Visualization data for VisIt
  ├── dumps.visit         # VisIt session file
  ├── lag_data.cycle_*    # Lagrangian structure data
  └── visit_dump.*        # Eulerian fluid data

restart_valve2d/          # Restart files
valve2d.log               # Simulation log
```

## Performance Tips

1. **Start small**: Test with resolution=32, 1 cycle, 2 AMR levels
2. **Use AMR**: Concentrates resolution near valve (10x speedup)
3. **Parallel runs**: Use MPI for large simulations
4. **Checkpoint often**: Set restart_dump_interval for long runs

## Next Steps

### Phase 1: Validation
- [ ] Compare velocity profiles with literature
- [ ] Validate pressure gradients against clinical data
- [ ] Check mesh independence (vary resolution)

### Phase 2: Analysis Pipeline
- [ ] Extract time-series data (forces, pressures)
- [ ] Calculate clinical metrics (EOA, gradients)
- [ ] Create Python post-processing scripts

### Phase 3: Interactive Visualization
- [ ] Build web interface (Three.js)
- [ ] Create slider for disease severity
- [ ] Add real-time metric dashboard

### Phase 4: Patient-Specific Models
- [ ] Import geometries from medical imaging (CT/MRI)
- [ ] Calibrate material properties from echo data
- [ ] Generate personalized simulation reports

## References

### IBAMR Documentation
- Main site: https://ibamr.github.io
- Installation: https://ibamr.github.io/installation
- Tutorials: https://ibamr.github.io/tutorials

### Cardiovascular Modeling
- Peskin CS (2002). The immersed boundary method. Acta Numerica 11:479-517
- Griffith BE et al. (2007). An adaptive, formally second order accurate version of the immersed boundary method

### Clinical Guidelines
- ACC/AHA Valve Disease Guidelines
- Doppler echocardiography criteria for stenosis severity

## Troubleshooting

### Common Issues

**Problem**: Simulation crashes with "timestep too small"
- **Solution**: Reduce CFL_MAX in input2d or increase spring stiffness

**Problem**: Leaflets pass through each other
- **Solution**: Increase spring stiffness or reduce DT_MAX

**Problem**: Too slow
- **Solution**: Reduce MAX_LEVELS, use coarser geometry, or run in parallel

**Problem**: Visualization files not generated
- **Solution**: Check viz_dump_interval, ensure VisIt writer is enabled

## Contact

For questions about:
- IBAMR: See https://github.com/ibamr/ibamr
- This project: [Your contact info]

## License

This project uses IBAMR (BSD 3-clause license).
Geometry generation scripts: MIT License
