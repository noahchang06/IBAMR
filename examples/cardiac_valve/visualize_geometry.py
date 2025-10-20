#!/usr/bin/env python3
"""
Visualize and analyze valve geometries.

This script provides tools to:
1. Visualize single valve geometry
2. Compare multiple severities side-by-side
3. Analyze geometric properties
4. Generate publication-quality figures

Usage:
    python visualize_geometry.py --mode single --file valve2d_healthy_64.vertex
    python visualize_geometry.py --mode compare --severities healthy,severe
    python visualize_geometry.py --mode animate --severity healthy
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.gridspec import GridSpec
import argparse
import os


def read_vertex_file(filename):
    """Read IBAMR .vertex file."""
    with open(filename, 'r') as f:
        n_vertices = int(f.readline().strip())
        vertices = np.zeros((n_vertices, 2))
        for i in range(n_vertices):
            line = f.readline().strip().split()
            vertices[i, 0] = float(line[0])
            vertices[i, 1] = float(line[1])
    return vertices


def read_spring_file(filename):
    """Read IBAMR .spring file."""
    with open(filename, 'r') as f:
        n_springs = int(f.readline().strip())
        springs = []
        for i in range(n_springs):
            line = f.readline().strip().split()
            springs.append([int(line[0]), int(line[1]), float(line[2]), float(line[3])])
    return np.array(springs)


def read_beam_file(filename):
    """Read IBAMR .beam file."""
    with open(filename, 'r') as f:
        n_beams = int(f.readline().strip())
        beams = []
        for i in range(n_beams):
            line = f.readline().strip().split()
            beams.append([int(line[0]), int(line[1]), int(line[2]), float(line[3])])
    return np.array(beams)


def calculate_geometric_properties(vertices, springs):
    """Calculate geometric properties of the valve."""
    # Center of mass
    center = np.mean(vertices, axis=0)

    # Radial extents
    radii = np.linalg.norm(vertices - center, axis=1)
    min_radius = np.min(radii)
    max_radius = np.max(radii)

    # Effective orifice area (approximation: convex hull area)
    from scipy.spatial import ConvexHull
    try:
        hull = ConvexHull(vertices)
        orifice_area = hull.volume  # In 2D, volume is area
    except:
        orifice_area = np.pi * min_radius**2

    # Leaflet span angles
    angles = np.arctan2(vertices[:, 1] - center[1], vertices[:, 0] - center[0])

    # Average spring stiffness
    avg_stiffness = np.mean(springs[:, 2])
    max_stiffness = np.max(springs[:, 2])

    properties = {
        'center': center,
        'min_radius': min_radius,
        'max_radius': max_radius,
        'radial_extent': max_radius - min_radius,
        'orifice_area': orifice_area,
        'avg_stiffness': avg_stiffness,
        'max_stiffness': max_stiffness,
        'n_vertices': len(vertices),
        'n_springs': len(springs)
    }

    return properties


def plot_single_geometry(vertices, springs, beams, title="Valve Geometry", ax=None):
    """Plot a single valve geometry."""
    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 10))

    # Plot springs with color based on stiffness
    if len(springs) > 0:
        stiffness_norm = (springs[:, 2] - springs[:, 2].min()) / (springs[:, 2].max() - springs[:, 2].min() + 1e-10)
        for i, s in enumerate(springs):
            idx1, idx2 = int(s[0]), int(s[1])
            color = plt.cm.Reds(0.3 + 0.7 * stiffness_norm[i])
            ax.plot([vertices[idx1, 0], vertices[idx2, 0]],
                   [vertices[idx1, 1], vertices[idx2, 1]],
                   color=color, alpha=0.5, linewidth=1.5)

    # Plot beams (structural elements)
    if len(beams) > 0:
        for b in beams[:10]:  # Plot subset to avoid clutter
            idx1, idx2, idx3 = int(b[0]), int(b[1]), int(b[2])
            ax.plot([vertices[idx1, 0], vertices[idx2, 0], vertices[idx3, 0]],
                   [vertices[idx1, 1], vertices[idx2, 1], vertices[idx3, 1]],
                   'b-', alpha=0.2, linewidth=0.5)

    # Plot vertices
    ax.plot(vertices[:, 0], vertices[:, 1], 'ko', markersize=2, alpha=0.6)

    # Highlight base (annulus) vertices
    n_per_leaflet = len(vertices) // 3
    base_indices = [0, n_per_leaflet, 2*n_per_leaflet]
    ax.plot(vertices[base_indices, 0], vertices[base_indices, 1],
           'go', markersize=8, label='Annulus attachment', zorder=5)

    # Highlight leaflet tips
    tip_indices = [n_per_leaflet-1, 2*n_per_leaflet-1, len(vertices)-1]
    ax.plot(vertices[tip_indices, 0], vertices[tip_indices, 1],
           'ro', markersize=8, label='Leaflet tips', zorder=5)

    # Reference circle (annulus)
    theta = np.linspace(0, 2*np.pi, 100)
    ax.plot(1.0 * np.cos(theta), 1.0 * np.sin(theta),
           'k--', alpha=0.4, linewidth=2, label='Annulus (r=1.0cm)')

    # Flow direction arrow
    ax.arrow(-2.5, 0, 1.0, 0, head_width=0.3, head_length=0.2,
            fc='blue', ec='blue', alpha=0.5, linewidth=2)
    ax.text(-2.0, 0.5, 'Blood Flow', fontsize=12, color='blue', weight='bold')

    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3)
    ax.set_xlabel('x (cm)', fontsize=12)
    ax.set_ylabel('y (cm)', fontsize=12)
    ax.set_title(title, fontsize=14, weight='bold')
    ax.legend(loc='upper right', fontsize=10)
    ax.set_xlim(-3, 3)
    ax.set_ylim(-3, 3)

    return ax


def compare_severities(severities=['healthy', 'mild', 'moderate', 'severe'],
                       resolution=64, output_file='valve_comparison.png'):
    """Compare multiple valve severities side-by-side."""
    n_severities = len(severities)
    fig = plt.figure(figsize=(6*n_severities, 7))
    gs = GridSpec(2, n_severities, height_ratios=[3, 1], hspace=0.3)

    all_properties = {}

    for i, severity in enumerate(severities):
        # Read geometry files
        prefix = f"valve2d_{severity}_{resolution}"
        try:
            vertices = read_vertex_file(f"{prefix}.vertex")
            springs = read_spring_file(f"{prefix}.spring")
            beams = read_beam_file(f"{prefix}.beam")
        except FileNotFoundError:
            print(f"Warning: Files for {severity} not found, skipping...")
            continue

        # Calculate properties
        props = calculate_geometric_properties(vertices, springs)
        all_properties[severity] = props

        # Plot geometry
        ax = fig.add_subplot(gs[0, i])
        plot_single_geometry(vertices, springs, beams,
                           title=f"{severity.capitalize()}", ax=ax)

        # Plot properties table
        ax_table = fig.add_subplot(gs[1, i])
        ax_table.axis('off')

        table_data = [
            ['Vertices', f"{props['n_vertices']}"],
            ['Springs', f"{props['n_springs']}"],
            ['Extent (cm)', f"{props['radial_extent']:.3f}"],
            ['Area (cm²)', f"{props['orifice_area']:.3f}"],
            ['Avg k', f"{props['avg_stiffness']:.1e}"],
        ]

        table = ax_table.table(cellText=table_data,
                              cellLoc='left',
                              loc='center',
                              colWidths=[0.6, 0.4])
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1, 2)

        # Color code by severity
        severity_colors = {
            'healthy': '#90EE90',
            'mild': '#FFD700',
            'moderate': '#FFA500',
            'severe': '#FF6B6B'
        }
        color = severity_colors.get(severity, 'white')
        for (row, col), cell in table.get_celld().items():
            if col == 0:
                cell.set_facecolor('#E0E0E0')
            else:
                cell.set_facecolor(color)

    plt.suptitle('Aortic Valve Disease Progression',
                fontsize=16, weight='bold', y=0.98)

    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"Comparison saved to {output_file}")

    # Print summary statistics
    print("\nGeometric Comparison Summary:")
    print("-" * 80)
    print(f"{'Severity':<12} {'Area (cm²)':<12} {'Extent (cm)':<12} {'Avg Stiffness':<15}")
    print("-" * 80)

    for severity in severities:
        if severity in all_properties:
            p = all_properties[severity]
            print(f"{severity.capitalize():<12} {p['orifice_area']:<12.3f} "
                  f"{p['radial_extent']:<12.3f} {p['avg_stiffness']:<15.2e}")

    if 'healthy' in all_properties and 'severe' in all_properties:
        area_reduction = (1 - all_properties['severe']['orifice_area'] /
                         all_properties['healthy']['orifice_area']) * 100
        stiffness_increase = (all_properties['severe']['avg_stiffness'] /
                            all_properties['healthy']['avg_stiffness'])
        print("-" * 80)
        print(f"Healthy → Severe:")
        print(f"  Area reduction: {area_reduction:.1f}%")
        print(f"  Stiffness increase: {stiffness_increase:.1f}x")

    plt.close()


def plot_with_coordinate_system(vertices, springs, severity='healthy',
                                output_file='valve_coordinates.png'):
    """Plot valve with coordinate system and measurements."""
    fig, ax = plt.subplots(figsize=(12, 10))

    # Plot geometry
    plot_single_geometry(vertices, springs, [],
                        title=f"Valve Coordinate System - {severity.capitalize()}",
                        ax=ax)

    # Add coordinate system annotations
    ax.axhline(y=0, color='gray', linestyle=':', linewidth=1, alpha=0.5)
    ax.axvline(x=0, color='gray', linestyle=':', linewidth=1, alpha=0.5)

    # Measure and annotate valve dimensions
    n_per_leaflet = len(vertices) // 3

    # Mark leaflet centerlines
    for i in range(3):
        base_idx = i * n_per_leaflet
        tip_idx = base_idx + n_per_leaflet - 1
        ax.plot([vertices[base_idx, 0], vertices[tip_idx, 0]],
               [vertices[base_idx, 1], vertices[tip_idx, 1]],
               'g--', linewidth=2, alpha=0.7)

        # Label leaflet
        mid = (vertices[base_idx] + vertices[tip_idx]) / 2
        ax.text(mid[0]*1.3, mid[1]*1.3, f'Leaflet {i+1}',
               fontsize=11, weight='bold',
               bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.7))

    # Annotate key dimensions
    ax.annotate('', xy=(1.0, 0), xytext=(0, 0),
               arrowprops=dict(arrowstyle='<->', color='red', lw=2))
    ax.text(0.5, -0.2, 'Annulus radius\n1.0 cm',
           ha='center', fontsize=10, color='red', weight='bold')

    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"Annotated geometry saved to {output_file}")
    plt.close()


def main():
    parser = argparse.ArgumentParser(description='Visualize valve geometries')
    parser.add_argument('--mode', type=str, default='compare',
                       choices=['single', 'compare', 'annotate'],
                       help='Visualization mode')
    parser.add_argument('--severity', type=str, default='healthy',
                       help='Severity for single mode')
    parser.add_argument('--severities', type=str,
                       default='healthy,mild,moderate,severe',
                       help='Comma-separated severities for compare mode')
    parser.add_argument('--resolution', type=int, default=64,
                       help='Geometry resolution')
    parser.add_argument('--output', type=str, default='valve_visualization.png',
                       help='Output filename')

    args = parser.parse_args()

    if args.mode == 'single':
        # Visualize single geometry
        prefix = f"valve2d_{args.severity}_{args.resolution}"
        vertices = read_vertex_file(f"{prefix}.vertex")
        springs = read_spring_file(f"{prefix}.spring")
        beams = read_beam_file(f"{prefix}.beam")

        props = calculate_geometric_properties(vertices, springs)

        fig, ax = plt.subplots(figsize=(10, 10))
        plot_single_geometry(vertices, springs, beams,
                           title=f"Valve Geometry - {args.severity.capitalize()}",
                           ax=ax)

        plt.savefig(args.output, dpi=150, bbox_inches='tight')
        print(f"Visualization saved to {args.output}")

        print("\nGeometric Properties:")
        for key, value in props.items():
            if isinstance(value, (int, np.integer)):
                print(f"  {key}: {value}")
            elif isinstance(value, float):
                print(f"  {key}: {value:.6f}")

        plt.close()

    elif args.mode == 'compare':
        # Compare multiple severities
        severities = [s.strip() for s in args.severities.split(',')]
        compare_severities(severities, args.resolution, args.output)

    elif args.mode == 'annotate':
        # Annotated diagram
        prefix = f"valve2d_{args.severity}_{args.resolution}"
        vertices = read_vertex_file(f"{prefix}.vertex")
        springs = read_spring_file(f"{prefix}.spring")
        plot_with_coordinate_system(vertices, springs, args.severity, args.output)


if __name__ == "__main__":
    main()
