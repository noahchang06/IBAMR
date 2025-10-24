#!/usr/bin/env python3
"""
Create animated visualization of cardiac valve cycle.

Generates a looping animation showing:
- Valve opening and closing
- Blood flow patterns
- Pressure and velocity changes
- Side-by-side healthy vs diseased comparison

Output: animated GIF showing one complete heartbeat
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from matplotlib.patches import Circle
from matplotlib.animation import FuncAnimation, PillowWriter
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


def simulate_valve_deformation(base_verts, time_in_cycle, severity='healthy'):
    """
    Simulate valve opening/closing during cardiac cycle.

    This shows how the leaflets move - in full IBAMR, this is
    solved from the fluid forces and elastic equations.
    """
    severity_params = {
        'healthy': {'max_opening': 0.95, 'stiffness': 1.0},
        'severe': {'max_opening': 0.5, 'stiffness': 3.0}
    }
    params = severity_params[severity]

    # Determine opening amount based on cardiac phase
    if time_in_cycle < 0.3:  # Systole
        # Sinusoidal opening
        opening_fraction = np.sin(np.pi * time_in_cycle / 0.3)
        opening = params['max_opening'] * opening_fraction
    else:  # Diastole
        opening = 0.05  # Nearly closed

    # Deform vertices to simulate opening
    # In reality, this comes from solving elastic equations
    deformed_verts = base_verts.copy()

    # Calculate radial positions
    center = np.array([0, 0])
    radii = np.linalg.norm(base_verts - center, axis=1)
    angles = np.arctan2(base_verts[:, 1], base_verts[:, 0])

    # Leaflets pull inward when opening
    # More stiff valves don't open as much
    radial_displacement = opening * (1 - radii / radii.max()) * 0.3

    # Apply deformation
    deformed_verts[:, 0] = base_verts[:, 0] * (1 - radial_displacement)
    deformed_verts[:, 1] = base_verts[:, 1] * (1 - radial_displacement)

    return deformed_verts, opening


def calculate_flow_field(time_in_cycle, severity='healthy'):
    """Calculate simplified flow field at this time point."""
    x = np.linspace(-3, 3, 60)
    y = np.linspace(-3, 3, 60)
    X, Y = np.meshgrid(x, y)
    R = np.sqrt(X**2 + Y**2)

    severity_params = {
        'healthy': {'opening': 0.9, 'resistance': 1.0},
        'severe': {'opening': 0.4, 'resistance': 5.0}
    }
    params = severity_params[severity]

    if time_in_cycle < 0.3:  # Systole
        flow_strength = np.sin(np.pi * time_in_cycle / 0.3)

        # Velocity field
        U = np.where(X < 0,
                     flow_strength * 40 * (1 + X/4),
                     flow_strength * 80 / params['opening'])
        U = np.where(X > 0, U * np.exp(-X/2), U)

        V = -Y * flow_strength * 8 * np.exp(-X**2/3)

        # Reduce outside valve
        in_valve = R < (1.5 * params['opening'])
        U = np.where(in_valve | (X < -1), U, U * 0.2)
        V = np.where(in_valve | (X < -1), V, V * 0.2)
    else:  # Diastole
        U = -3 * np.exp(-R**2/2)
        V = np.zeros_like(U)

    vel_mag = np.sqrt(U**2 + V**2)

    return X, Y, U, V, vel_mag


def create_frame(frame_num, healthy_verts, severe_verts, axes,
                total_frames=60, cycle_duration=0.8):
    """Create one frame of the animation."""

    # Calculate time in cardiac cycle
    time_in_cycle = (frame_num / total_frames) * cycle_duration

    # Get deformed geometries
    healthy_deformed, healthy_opening = simulate_valve_deformation(
        healthy_verts, time_in_cycle, 'healthy'
    )
    severe_deformed, severe_opening = simulate_valve_deformation(
        severe_verts, time_in_cycle, 'severe'
    )

    # Get flow fields
    X_h, Y_h, U_h, V_h, vel_h = calculate_flow_field(time_in_cycle, 'healthy')
    X_s, Y_s, U_s, V_s, vel_s = calculate_flow_field(time_in_cycle, 'severe')

    # Determine phase
    phase = 'SYSTOLE' if time_in_cycle < 0.3 else 'DIASTOLE'
    phase_color = '#FFD700' if phase == 'SYSTOLE' else '#87CEEB'

    # Clear all axes
    for ax in axes:
        ax.clear()

    # Plot healthy valve
    ax_healthy = axes[0]

    # Flow field
    speed_h = np.sqrt(U_h**2 + V_h**2)
    if speed_h.max() > 0.1:
        strm_h = ax_healthy.streamplot(X_h, Y_h, U_h, V_h,
                                       color=vel_h, cmap='jet',
                                       linewidth=1.5, density=1.8,
                                       arrowsize=1.2)

    # Valve geometry
    ax_healthy.fill(healthy_deformed[:, 0], healthy_deformed[:, 1],
                   color='darkred', alpha=0.8, edgecolor='black', linewidth=2)

    # Annulus
    circle_h = Circle((0, 0), 1.0, fill=False, edgecolor='gray',
                     linestyle='--', linewidth=2, alpha=0.7)
    ax_healthy.add_patch(circle_h)

    # Flow arrow
    if phase == 'SYSTOLE':
        ax_healthy.arrow(-2.5, 0, 0.8, 0, head_width=0.25, head_length=0.15,
                        fc='blue', ec='blue', alpha=0.6, linewidth=2)
        ax_healthy.text(-2.1, 0.4, 'FLOW', fontsize=10, color='blue', weight='bold')

    ax_healthy.set_xlim(-3.5, 3.5)
    ax_healthy.set_ylim(-3.5, 3.5)
    ax_healthy.set_aspect('equal')
    ax_healthy.set_title(f'HEALTHY VALVE\nOpening: {healthy_opening*100:.0f}%',
                        fontsize=12, weight='bold', color='darkgreen')
    ax_healthy.set_xlabel('Position (cm)', fontsize=10)
    ax_healthy.set_ylabel('Position (cm)', fontsize=10)
    ax_healthy.grid(True, alpha=0.2)

    # Plot severe valve
    ax_severe = axes[1]

    # Flow field
    speed_s = np.sqrt(U_s**2 + V_s**2)
    if speed_s.max() > 0.1:
        strm_s = ax_severe.streamplot(X_s, Y_s, U_s, V_s,
                                      color=vel_s, cmap='jet',
                                      linewidth=1.5, density=1.8,
                                      arrowsize=1.2)

    # Valve geometry
    ax_severe.fill(severe_deformed[:, 0], severe_deformed[:, 1],
                  color='darkred', alpha=0.8, edgecolor='black', linewidth=2)

    # Annulus
    circle_s = Circle((0, 0), 1.0, fill=False, edgecolor='gray',
                     linestyle='--', linewidth=2, alpha=0.7)
    ax_severe.add_patch(circle_s)

    # Flow arrow
    if phase == 'SYSTOLE':
        ax_severe.arrow(-2.5, 0, 0.8, 0, head_width=0.25, head_length=0.15,
                       fc='blue', ec='blue', alpha=0.6, linewidth=2)
        ax_severe.text(-2.1, 0.4, 'FLOW', fontsize=10, color='blue', weight='bold')

    ax_severe.set_xlim(-3.5, 3.5)
    ax_severe.set_ylim(-3.5, 3.5)
    ax_severe.set_aspect('equal')
    ax_severe.set_title(f'SEVERE STENOSIS\nOpening: {severe_opening*100:.0f}%',
                       fontsize=12, weight='bold', color='darkred')
    ax_severe.set_xlabel('Position (cm)', fontsize=10)
    ax_severe.set_ylabel('Position (cm)', fontsize=10)
    ax_severe.grid(True, alpha=0.2)

    # Timeline indicator (bottom)
    ax_timeline = axes[2]

    # Draw timeline
    timeline_x = np.linspace(0, cycle_duration, 100)
    timeline_y = np.zeros(100)
    ax_timeline.plot(timeline_x, timeline_y, 'k-', linewidth=3)

    # Mark systole and diastole regions
    ax_timeline.axvspan(0, 0.3, alpha=0.3, color='#FFD700', label='Systole')
    ax_timeline.axvspan(0.3, 0.8, alpha=0.3, color='#87CEEB', label='Diastole')

    # Current time marker
    ax_timeline.plot(time_in_cycle, 0, 'ro', markersize=15, zorder=10)
    ax_timeline.plot([time_in_cycle, time_in_cycle], [-0.1, 0.1], 'r-',
                    linewidth=3, zorder=9)

    # Labels
    ax_timeline.text(0.15, 0.15, 'SYSTOLE\n(Pumping)', ha='center',
                    fontsize=10, weight='bold')
    ax_timeline.text(0.55, 0.15, 'DIASTOLE\n(Filling)', ha='center',
                    fontsize=10, weight='bold')

    ax_timeline.set_xlim(0, cycle_duration)
    ax_timeline.set_ylim(-0.2, 0.3)
    ax_timeline.set_xlabel('Time in Cardiac Cycle (s)', fontsize=11, weight='bold')
    ax_timeline.set_yticks([])
    ax_timeline.spines['left'].set_visible(False)
    ax_timeline.spines['right'].set_visible(False)
    ax_timeline.spines['top'].set_visible(False)

    # Metrics display
    ax_metrics = axes[3]
    ax_metrics.axis('off')

    metrics_text = f"""
    CURRENT PHASE: {phase}
    Time: {time_in_cycle:.2f} s / {cycle_duration:.2f} s

    VALVE OPENING:
      Healthy: {healthy_opening*100:5.0f}%
      Severe:  {severe_opening*100:5.0f}%

    PEAK VELOCITY:
      Healthy: ~{120 * healthy_opening:.0f} cm/s
      Severe:  ~{500 * severe_opening:.0f} cm/s

    HEMODYNAMICS:
      • Healthy valve opens wide
      • Diseased valve restricted
      • Higher velocities in stenosis
      • Turbulent jet formation
    """

    ax_metrics.text(0.1, 0.5, metrics_text, transform=ax_metrics.transAxes,
                   fontsize=9, verticalalignment='center', fontfamily='monospace',
                   bbox=dict(boxstyle='round', facecolor=phase_color, alpha=0.6))

    return axes


def create_animation(healthy_verts, severe_verts,
                    output_file='cardiac_valve_animation.gif',
                    fps=30, duration=8):
    """Create animated GIF of cardiac valve cycle."""

    print("\n" + "="*80)
    print("CREATING CARDIAC VALVE ANIMATION")
    print("="*80)

    total_frames = fps * duration
    print(f"\nAnimation parameters:")
    print(f"  Duration: {duration} seconds")
    print(f"  Frame rate: {fps} FPS")
    print(f"  Total frames: {total_frames}")
    print(f"  Cardiac cycles: {duration / 0.8:.1f}")
    print(f"  Output: {output_file}")

    # Create figure
    fig = plt.figure(figsize=(16, 10))
    gs = GridSpec(3, 2, figure=fig, height_ratios=[3, 1, 1],
                  hspace=0.3, wspace=0.3)

    ax_healthy = fig.add_subplot(gs[0, 0])
    ax_severe = fig.add_subplot(gs[0, 1])
    ax_timeline = fig.add_subplot(gs[1, :])
    ax_metrics = fig.add_subplot(gs[2, :])

    axes = [ax_healthy, ax_severe, ax_timeline, ax_metrics]

    # Title
    fig.suptitle('Cardiac Valve Disease - Flow Simulation (Looping Animation)',
                fontsize=16, weight='bold', y=0.98)

    print("\nGenerating frames...")

    # Animation update function
    def update(frame):
        if frame % 10 == 0:
            print(f"  Frame {frame}/{total_frames} ({frame/total_frames*100:.0f}%)", end='\r')
        return create_frame(frame, healthy_verts, severe_verts, axes, total_frames)

    # Create animation
    anim = FuncAnimation(fig, update, frames=total_frames,
                        interval=1000/fps, blit=False)

    # Save as GIF
    print(f"\n\nSaving animation to {output_file}...")
    writer = PillowWriter(fps=fps)
    anim.save(output_file, writer=writer, dpi=100)

    file_size_mb = os.path.getsize(output_file) / (1024 * 1024)

    print("\n" + "="*80)
    print("ANIMATION COMPLETE!")
    print("="*80)
    print(f"\nOutput file: {output_file}")
    print(f"File size: {file_size_mb:.1f} MB")
    print(f"Duration: {duration} seconds")
    print(f"Loops: {duration / 0.8:.1f} cardiac cycles")
    print("\nThe animation shows:")
    print("  • Valve opening during systole (heart pumps)")
    print("  • Valve closing during diastole (heart fills)")
    print("  • Blood flow patterns (streamlines)")
    print("  • Healthy vs diseased valve side-by-side")
    print("  • Timeline indicator with current phase")
    print("  • Real-time hemodynamic metrics")
    print("\n" + "="*80)

    plt.close()
    return output_file


if __name__ == "__main__":
    import os

    # Read geometries
    print("\nLoading valve geometries...")
    healthy_verts = read_vertex_file('demo_healthy_healthy_96.vertex')
    severe_verts = read_vertex_file('demo_severe_severe_96.vertex')

    print(f"  Healthy: {len(healthy_verts)} vertices")
    print(f"  Severe: {len(severe_verts)} vertices")

    # Create animation
    create_animation(healthy_verts, severe_verts,
                    output_file='cardiac_valve_animation.gif',
                    fps=30, duration=8)
