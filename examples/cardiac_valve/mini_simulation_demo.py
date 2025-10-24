#!/usr/bin/env python3
"""
Mini Cardiac Valve Flow Simulation Demo

This simplified simulation demonstrates:
1. How blood flows through healthy vs diseased valves
2. Pressure gradients across the valve
3. Flow velocity patterns
4. Clinical metrics (EOA, pressure drop)

This is a DEMONSTRATION - not a full CFD simulation.
For full fluid-structure interaction, use IBAMR with the input2d file.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from matplotlib.patches import Circle, FancyArrowPatch
from matplotlib.colors import LinearSegmentedColormap
import sys


def read_vertex_file(filename):
    """Read valve geometry."""
    with open(filename, 'r') as f:
        n = int(f.readline())
        verts = np.zeros((n, 2))
        for i in range(n):
            line = f.readline().split()
            verts[i] = [float(line[0]), float(line[1])]
    return verts


def simulate_flow_field(valve_verts, time_in_cycle, severity='healthy'):
    """
    Simplified flow simulation through valve.

    In reality, IBAMR solves:
    - Navier-Stokes equations for fluid
    - Elastic deformation for structure
    - Fluid-structure coupling

    This demo shows the key patterns.
    """
    # Create flow field grid
    x = np.linspace(-4, 4, 80)
    y = np.linspace(-4, 4, 80)
    X, Y = np.meshgrid(x, y)

    # Determine cardiac phase
    if time_in_cycle < 0.3:  # Systole (heart contracting)
        phase = 'systole'
        flow_strength = np.sin(np.pi * time_in_cycle / 0.3)  # Ramps up and down
    else:  # Diastole (heart relaxing)
        phase = 'diastole'
        flow_strength = -0.1  # Small backflow

    # Calculate valve opening based on severity
    severity_params = {
        'healthy': {'opening': 0.9, 'resistance': 1.0},
        'mild': {'opening': 0.8, 'resistance': 1.5},
        'moderate': {'opening': 0.65, 'resistance': 2.5},
        'severe': {'opening': 0.4, 'resistance': 5.0}
    }
    params = severity_params[severity]

    # Effective opening during systole
    if phase == 'systole':
        opening_factor = params['opening'] * flow_strength
    else:
        opening_factor = 0.1  # Nearly closed

    # Velocity field (simplified)
    # In real IBAMR: solves incompressible Navier-Stokes
    # Here: analytical approximation

    # Distance from center
    R = np.sqrt(X**2 + Y**2)

    # Velocity magnitude (higher near valve, decreases downstream)
    # Stenotic valves create jet (high velocity in narrow region)
    if phase == 'systole':
        # Upstream (X < 0): accelerating flow
        U = np.where(X < 0,
                     flow_strength * 50 * (1 + X/4),  # Accelerating
                     flow_strength * 100 / params['opening'])  # Jet through valve

        # Downstream (X > 0): jet expansion and deceleration
        U = np.where(X > 0,
                     U * np.exp(-X/3) * (1 / (1 + params['resistance'])),
                     U)

        # Radial component (flow focuses toward valve center)
        V = -Y * flow_strength * 10 * np.exp(-X**2/4)

        # Reduce flow outside valve opening
        in_valve_region = R < (1.2 * opening_factor)
        U = np.where(in_valve_region | (X < -1), U, U * 0.3)
        V = np.where(in_valve_region | (X < -1), V, V * 0.3)

    else:  # Diastole
        # Small backflow (valve should close)
        U = -5 * np.exp(-R**2/2)
        V = np.zeros_like(U)

    # Velocity magnitude
    vel_mag = np.sqrt(U**2 + V**2)

    # Pressure field (from Bernoulli equation)
    # P + 0.5*rho*v^2 = constant
    rho = 1.06  # Blood density (g/cm³)
    P_base = 80  # Baseline pressure (mmHg)

    # Pressure decreases as velocity increases
    P = P_base - 0.5 * rho * vel_mag**2 * 0.0075  # Convert to mmHg

    return X, Y, U, V, vel_mag, P, phase, opening_factor


def calculate_clinical_metrics(valve_verts, severity):
    """Calculate clinical metrics from geometry and flow."""

    # Effective orifice area (from geometry)
    from scipy.spatial import ConvexHull
    try:
        hull = ConvexHull(valve_verts)
        EOA = hull.volume  # In 2D, volume is area
    except:
        EOA = np.pi * 0.5**2

    # Flow parameters based on severity
    severity_metrics = {
        'healthy': {
            'peak_velocity': 120,  # cm/s
            'mean_gradient': 5,     # mmHg
            'peak_gradient': 8,     # mmHg
            'cardiac_output': 5.0,  # L/min
            'jet_area': EOA * 0.95,
            'eoa': EOA
        },
        'mild': {
            'peak_velocity': 250,
            'mean_gradient': 15,
            'peak_gradient': 22,
            'cardiac_output': 4.8,
            'jet_area': EOA * 0.7,
            'eoa': EOA
        },
        'moderate': {
            'peak_velocity': 350,
            'mean_gradient': 30,
            'peak_gradient': 45,
            'cardiac_output': 4.3,
            'jet_area': EOA * 0.5,
            'eoa': EOA
        },
        'severe': {
            'peak_velocity': 500,
            'mean_gradient': 50,
            'peak_gradient': 75,
            'cardiac_output': 3.8,
            'jet_area': EOA * 0.3,
            'eoa': EOA
        }
    }

    return severity_metrics[severity]


def plot_simulation_frame(valve_verts, severity, time_in_cycle, ax_flow, ax_pressure):
    """Plot one frame of the simulation."""

    # Get flow field
    X, Y, U, V, vel_mag, P, phase, opening = simulate_flow_field(
        valve_verts, time_in_cycle, severity
    )

    # Plot velocity field
    ax_flow.clear()

    # Streamlines
    speed = np.sqrt(U**2 + V**2)
    max_speed = speed.max()
    if max_speed > 0.1:  # Only if there's meaningful flow
        lw = 2 * speed / max_speed  # Line width proportional to speed
        strm = ax_flow.streamplot(X, Y, U, V, color=vel_mag,
                                  cmap='jet', linewidth=lw,
                                  density=1.5, arrowsize=1.5)
    else:
        # No flow - just show velocity field as quiver
        strm = ax_flow.quiver(X[::4, ::4], Y[::4, ::4], U[::4, ::4], V[::4, ::4],
                             vel_mag[::4, ::4], cmap='jet', scale=50)

    # Valve geometry
    ax_flow.plot(valve_verts[:, 0], valve_verts[:, 1],
                'k-', linewidth=3, zorder=10)
    ax_flow.scatter(valve_verts[:, 0], valve_verts[:, 1],
                   c='darkred', s=20, zorder=11)

    # Annulus circle
    circle = Circle((0, 0), 1.0, fill=False, edgecolor='gray',
                   linestyle='--', linewidth=2)
    ax_flow.add_patch(circle)

    ax_flow.set_xlim(-4, 4)
    ax_flow.set_ylim(-4, 4)
    ax_flow.set_aspect('equal')
    ax_flow.set_xlabel('Position (cm)', fontsize=11)
    ax_flow.set_ylabel('Position (cm)', fontsize=11)
    ax_flow.set_title(f'{severity.capitalize()} Valve - {phase.capitalize()}\n'
                     f'Time: {time_in_cycle:.2f}s, Opening: {opening*100:.0f}%',
                     fontsize=12, weight='bold')

    # Add colorbar for velocity
    if max_speed > 0.1:
        cbar = plt.colorbar(strm.lines, ax=ax_flow)
    else:
        cbar = plt.colorbar(strm, ax=ax_flow)
    cbar.set_label('Velocity (cm/s)', fontsize=10)

    # Plot pressure field
    ax_pressure.clear()

    contourf = ax_pressure.contourf(X, Y, P, levels=20, cmap='RdYlBu_r')
    contour = ax_pressure.contour(X, Y, P, levels=10, colors='black',
                                  linewidths=0.5, alpha=0.3)
    ax_pressure.clabel(contour, inline=True, fontsize=8)

    # Valve geometry
    ax_pressure.plot(valve_verts[:, 0], valve_verts[:, 1],
                    'k-', linewidth=3, zorder=10)

    ax_pressure.set_xlim(-4, 4)
    ax_pressure.set_ylim(-4, 4)
    ax_pressure.set_aspect('equal')
    ax_pressure.set_xlabel('Position (cm)', fontsize=11)
    ax_pressure.set_ylabel('Position (cm)', fontsize=11)
    ax_pressure.set_title(f'Pressure Field', fontsize=12, weight='bold')

    # Add colorbar for pressure
    cbar2 = plt.colorbar(contourf, ax=ax_pressure)
    cbar2.set_label('Pressure (mmHg)', fontsize=10)

    return strm, contourf


def create_full_simulation_comparison(healthy_verts, severe_verts):
    """Create comprehensive comparison of healthy vs diseased valve."""

    print("\n" + "="*80)
    print("CARDIAC VALVE FLOW SIMULATION - MINI DEMO")
    print("="*80)

    # Analyze both valves
    print("\nANALYZING VALVE GEOMETRIES...")

    healthy_metrics = calculate_clinical_metrics(healthy_verts, 'healthy')
    severe_metrics = calculate_clinical_metrics(severe_verts, 'severe')

    print("\nGEOMETRIC COMPARISON:")
    print("-" * 80)
    print(f"{'Parameter':<30} {'Healthy':<20} {'Severe':<20} {'Change':<10}")
    print("-" * 80)
    print(f"{'Effective Orifice Area (cm²)':<30} "
          f"{healthy_metrics['eoa']:<20.2f} {severe_metrics['eoa']:<20.2f} "
          f"{((severe_metrics['eoa']/healthy_metrics['eoa']-1)*100):>8.1f}%")
    print(f"{'Peak Velocity (cm/s)':<30} "
          f"{healthy_metrics['peak_velocity']:<20.0f} {severe_metrics['peak_velocity']:<20.0f} "
          f"{((severe_metrics['peak_velocity']/healthy_metrics['peak_velocity']-1)*100):>8.1f}%")
    print(f"{'Mean Pressure Gradient (mmHg)':<30} "
          f"{healthy_metrics['mean_gradient']:<20.0f} {severe_metrics['mean_gradient']:<20.0f} "
          f"{((severe_metrics['mean_gradient']/healthy_metrics['mean_gradient']-1)*100):>8.1f}%")
    print(f"{'Cardiac Output (L/min)':<30} "
          f"{healthy_metrics['cardiac_output']:<20.1f} {severe_metrics['cardiac_output']:<20.1f} "
          f"{((severe_metrics['cardiac_output']/healthy_metrics['cardiac_output']-1)*100):>8.1f}%")
    print("-" * 80)

    # Simulate key time points in cardiac cycle
    time_points = [0.0, 0.15, 0.3, 0.5]  # Early systole, peak, end systole, diastole
    phase_names = ['Early Systole', 'Peak Systole', 'End Systole', 'Diastole']

    print("\nSIMULATING CARDIAC CYCLE...")
    print(f"Cardiac cycle duration: 0.8 seconds (75 bpm)")
    print(f"Systole: 0.0 - 0.3s (heart pumps)")
    print(f"Diastole: 0.3 - 0.8s (heart fills)")

    for i, (t, phase_name) in enumerate(zip(time_points, phase_names)):
        print(f"\nCreating visualization {i+1}/4: {phase_name} (t={t}s)...")

        fig = plt.figure(figsize=(16, 7))
        gs = GridSpec(2, 4, figure=fig, hspace=0.3, wspace=0.4)

        # Healthy valve
        ax_h_flow = fig.add_subplot(gs[0, 0:2])
        ax_h_pressure = fig.add_subplot(gs[1, 0:2])

        # Severe valve
        ax_s_flow = fig.add_subplot(gs[0, 2:4])
        ax_s_pressure = fig.add_subplot(gs[1, 2:4])

        # Plot healthy
        plot_simulation_frame(healthy_verts, 'healthy', t, ax_h_flow, ax_h_pressure)

        # Plot severe
        plot_simulation_frame(severe_verts, 'severe', t, ax_s_flow, ax_s_pressure)

        fig.suptitle(f'Cardiac Valve Flow Comparison - {phase_name} (t={t:.2f}s)',
                    fontsize=16, weight='bold', y=0.98)

        filename = f'simulation_frame_{i+1}_{phase_name.replace(" ", "_").lower()}.png'
        plt.savefig(filename, dpi=120, bbox_inches='tight')
        print(f"   Saved: {filename}")
        plt.close()

    # Create summary comparison
    print("\nCreating summary comparison...")
    create_summary_plot(healthy_verts, severe_verts,
                       healthy_metrics, severe_metrics)

    print("\n" + "="*80)
    print("SIMULATION COMPLETE!")
    print("="*80)
    print("\nGenerated files:")
    print("  - simulation_frame_1_early_systole.png")
    print("  - simulation_frame_2_peak_systole.png")
    print("  - simulation_frame_3_end_systole.png")
    print("  - simulation_frame_4_diastole.png")
    print("  - simulation_summary.png")
    print("\n" + "="*80)


def create_summary_plot(healthy_verts, severe_verts, healthy_metrics, severe_metrics):
    """Create summary comparison plot."""

    fig = plt.figure(figsize=(18, 10))
    gs = GridSpec(3, 3, figure=fig, hspace=0.4, wspace=0.4)

    # Row 1: Geometries
    ax1 = fig.add_subplot(gs[0, 0])
    ax1.plot(healthy_verts[:, 0], healthy_verts[:, 1], 'b-', linewidth=2)
    ax1.fill(healthy_verts[:, 0], healthy_verts[:, 1], alpha=0.3, color='blue')
    circle = Circle((0, 0), 1.0, fill=False, edgecolor='gray', linestyle='--')
    ax1.add_patch(circle)
    ax1.set_aspect('equal')
    ax1.set_title('Healthy Valve Geometry', fontsize=12, weight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.set_xlim(-2, 2)
    ax1.set_ylim(-2, 2)

    ax2 = fig.add_subplot(gs[0, 1])
    ax2.plot(severe_verts[:, 0], severe_verts[:, 1], 'r-', linewidth=2)
    ax2.fill(severe_verts[:, 0], severe_verts[:, 1], alpha=0.3, color='red')
    circle = Circle((0, 0), 1.0, fill=False, edgecolor='gray', linestyle='--')
    ax2.add_patch(circle)
    ax2.set_aspect('equal')
    ax2.set_title('Severe Stenosis Geometry', fontsize=12, weight='bold')
    ax2.grid(True, alpha=0.3)
    ax2.set_xlim(-2, 2)
    ax2.set_ylim(-2, 2)

    # Row 1, Col 3: Key metrics comparison
    ax3 = fig.add_subplot(gs[0, 2])
    ax3.axis('off')

    metrics_text = f"""
    KEY CLINICAL METRICS

    Effective Orifice Area:
      Healthy: {healthy_metrics['eoa']:.2f} cm²
      Severe:  {severe_metrics['eoa']:.2f} cm²
      Reduction: {(1-severe_metrics['eoa']/healthy_metrics['eoa'])*100:.0f}%

    Peak Jet Velocity:
      Healthy: {healthy_metrics['peak_velocity']:.0f} cm/s
      Severe:  {severe_metrics['peak_velocity']:.0f} cm/s
      Increase: {(severe_metrics['peak_velocity']/healthy_metrics['peak_velocity']-1)*100:.0f}%

    Pressure Gradient:
      Healthy: {healthy_metrics['mean_gradient']:.0f} mmHg
      Severe:  {severe_metrics['mean_gradient']:.0f} mmHg
      Increase: {(severe_metrics['mean_gradient']/healthy_metrics['mean_gradient']-1)*100:.0f}%

    Clinical Significance:
      Healthy: Normal function
      Severe:  SURGICAL INTERVENTION
               INDICATED
    """
    ax3.text(0.1, 0.5, metrics_text, transform=ax3.transAxes,
            fontsize=10, verticalalignment='center',
            fontfamily='monospace',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

    # Row 2: Flow velocity profiles
    ax4 = fig.add_subplot(gs[1, :])

    # Simulate velocity profile through cardiac cycle
    times = np.linspace(0, 0.8, 100)
    healthy_vel = []
    severe_vel = []

    for t in times:
        # Simplified velocity waveform
        if t < 0.3:  # Systole
            h_v = healthy_metrics['peak_velocity'] * np.sin(np.pi * t / 0.3)
            s_v = severe_metrics['peak_velocity'] * np.sin(np.pi * t / 0.3)
        else:  # Diastole
            h_v = 0
            s_v = 0
        healthy_vel.append(h_v)
        severe_vel.append(s_v)

    ax4.plot(times, healthy_vel, 'b-', linewidth=3, label='Healthy')
    ax4.plot(times, severe_vel, 'r-', linewidth=3, label='Severe Stenosis')
    ax4.axvline(0.3, color='gray', linestyle='--', alpha=0.5, label='End Systole')
    ax4.fill_between(times, 0, healthy_vel, alpha=0.2, color='blue')
    ax4.fill_between(times, 0, severe_vel, alpha=0.2, color='red')
    ax4.set_xlabel('Time in Cardiac Cycle (s)', fontsize=12)
    ax4.set_ylabel('Peak Velocity (cm/s)', fontsize=12)
    ax4.set_title('Velocity Through Cardiac Cycle', fontsize=13, weight='bold')
    ax4.legend(fontsize=11)
    ax4.grid(True, alpha=0.3)
    ax4.set_xlim(0, 0.8)

    # Add phase labels
    ax4.text(0.15, max(severe_vel)*0.9, 'SYSTOLE\n(Pumping)',
            ha='center', fontsize=10, weight='bold',
            bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.5))
    ax4.text(0.55, max(severe_vel)*0.9, 'DIASTOLE\n(Filling)',
            ha='center', fontsize=10, weight='bold',
            bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.5))

    # Row 3: Pressure gradient
    ax5 = fig.add_subplot(gs[2, :])

    healthy_pressure = []
    severe_pressure = []

    for t in times:
        if t < 0.3:
            h_p = healthy_metrics['mean_gradient'] * (np.sin(np.pi * t / 0.3))**2
            s_p = severe_metrics['mean_gradient'] * (np.sin(np.pi * t / 0.3))**2
        else:
            h_p = 0
            s_p = 0
        healthy_pressure.append(h_p)
        severe_pressure.append(s_p)

    ax5.plot(times, healthy_pressure, 'b-', linewidth=3, label='Healthy')
    ax5.plot(times, severe_pressure, 'r-', linewidth=3, label='Severe Stenosis')
    ax5.axhline(40, color='darkred', linestyle='--', alpha=0.7,
               label='Severe Stenosis Threshold (40 mmHg)')
    ax5.fill_between(times, 0, healthy_pressure, alpha=0.2, color='blue')
    ax5.fill_between(times, 0, severe_pressure, alpha=0.2, color='red')
    ax5.set_xlabel('Time in Cardiac Cycle (s)', fontsize=12)
    ax5.set_ylabel('Pressure Gradient (mmHg)', fontsize=12)
    ax5.set_title('Transvalvular Pressure Gradient', fontsize=13, weight='bold')
    ax5.legend(fontsize=11)
    ax5.grid(True, alpha=0.3)
    ax5.set_xlim(0, 0.8)

    fig.suptitle('Cardiac Valve Disease Simulation Summary',
                fontsize=16, weight='bold', y=0.98)

    plt.savefig('simulation_summary.png', dpi=150, bbox_inches='tight')
    print("   Saved: simulation_summary.png")
    plt.close()


if __name__ == "__main__":
    # Read geometries
    print("\nLoading valve geometries...")
    healthy_verts = read_vertex_file('demo_healthy_healthy_96.vertex')
    severe_verts = read_vertex_file('demo_severe_severe_96.vertex')

    print(f"  Healthy valve: {len(healthy_verts)} vertices")
    print(f"  Severe valve: {len(severe_verts)} vertices")

    # Run simulation
    create_full_simulation_comparison(healthy_verts, severe_verts)
