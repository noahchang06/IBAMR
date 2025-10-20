#!/usr/bin/env python3
"""
Generate 2D aortic valve geometry for IBAMR simulation.

This script creates a simplified 2D aortic valve with three leaflets (cusps)
suitable for fluid-structure interaction simulations.

Usage:
    python generate_valve_geometry.py --resolution 64 --severity healthy

Severity options: healthy, mild, moderate, severe
"""

import numpy as np
import argparse
import matplotlib.pyplot as plt


def generate_aortic_valve(n_points_per_leaflet=32, annulus_radius=1.0,
                          leaflet_length=1.2, severity='healthy'):
    """
    Generate 2D aortic valve geometry with three leaflets.

    Parameters:
    -----------
    n_points_per_leaflet : int
        Number of points along each leaflet edge
    annulus_radius : float
        Radius of the valve annulus (attachment ring)
    leaflet_length : float
        Length of each leaflet from attachment to free edge
    severity : str
        Disease severity: 'healthy', 'mild', 'moderate', 'severe'
        Controls leaflet mobility and calcification

    Returns:
    --------
    vertices : ndarray
        Array of vertex coordinates (N x 2)
    springs : list
        List of spring connections [idx1, idx2, stiffness, damping]
    beams : list
        List of beam connections [idx1, idx2, idx3, bend_rigidity]
    """

    # Define material properties based on disease severity
    severity_params = {
        'healthy': {
            'spring_stiffness': 5.0e2,
            'beam_rigidity': 1.0e-2,
            'leaflet_length_factor': 1.0,
            'mobility': 1.0
        },
        'mild': {
            'spring_stiffness': 8.0e2,
            'beam_rigidity': 2.0e-2,
            'leaflet_length_factor': 0.95,
            'mobility': 0.9
        },
        'moderate': {
            'spring_stiffness': 1.5e3,
            'beam_rigidity': 5.0e-2,
            'leaflet_length_factor': 0.85,
            'mobility': 0.7
        },
        'severe': {
            'spring_stiffness': 3.0e3,
            'beam_rigidity': 1.0e-1,
            'leaflet_length_factor': 0.7,
            'mobility': 0.4
        }
    }

    params = severity_params[severity]
    leaflet_length *= params['leaflet_length_factor']

    vertices = []
    springs = []
    beams = []

    # Generate three leaflets at 120-degree intervals
    n_leaflets = 3

    for leaflet_idx in range(n_leaflets):
        # Angle for this leaflet's center
        theta_center = leaflet_idx * (2 * np.pi / n_leaflets)

        # Angular width of each leaflet (slightly less than 120 degrees for gaps)
        leaflet_arc = (2 * np.pi / n_leaflets) * 0.8

        # Generate points along the leaflet
        # Leaflet shape: curved from annulus (base) to free edge (tip)
        for i in range(n_points_per_leaflet):
            t = i / (n_points_per_leaflet - 1)  # Parameter from 0 (base) to 1 (tip)

            # Radial distance from center
            r = annulus_radius + leaflet_length * t

            # Angular position (leaflets curve inward when closed)
            # Curvature controlled by severity (more calcified = less mobile)
            curvature = 0.3 * (1 - t**2) * params['mobility']
            theta = theta_center + curvature * np.sin(np.pi * t)

            # Vertex position
            x = r * np.cos(theta)
            y = r * np.sin(theta)
            vertices.append([x, y])

    vertices = np.array(vertices)
    n_vertices = len(vertices)

    # Generate springs connecting adjacent vertices within each leaflet
    for leaflet_idx in range(n_leaflets):
        base_idx = leaflet_idx * n_points_per_leaflet

        # Longitudinal springs (along leaflet length)
        for i in range(n_points_per_leaflet - 1):
            idx1 = base_idx + i
            idx2 = base_idx + i + 1
            stiffness = params['spring_stiffness']
            damping = 0.0
            springs.append([idx1, idx2, stiffness, damping])

    # Generate beam elements for bending resistance
    for leaflet_idx in range(n_leaflets):
        base_idx = leaflet_idx * n_points_per_leaflet

        # Beam elements along leaflet
        for i in range(n_points_per_leaflet - 2):
            idx1 = base_idx + i
            idx2 = base_idx + i + 1
            idx3 = base_idx + i + 2
            rigidity = params['beam_rigidity']
            beams.append([idx1, idx2, idx3, rigidity])

    # Add cross-springs for structural stability
    for leaflet_idx in range(n_leaflets):
        base_idx = leaflet_idx * n_points_per_leaflet

        # Cross springs (every few points)
        skip = max(1, n_points_per_leaflet // 8)
        for i in range(0, n_points_per_leaflet - skip - 1, skip):
            idx1 = base_idx + i
            idx2 = base_idx + i + skip
            stiffness = params['spring_stiffness'] * 0.5
            damping = 0.0
            springs.append([idx1, idx2, stiffness, damping])

    return vertices, springs, beams, params


def write_vertex_file(filename, vertices):
    """Write vertices to IBAMR .vertex file format."""
    with open(filename, 'w') as f:
        f.write(f"{len(vertices)}\n")
        for v in vertices:
            f.write(f"{v[0]:e}\t{v[1]:e}\n")
    print(f"Written {len(vertices)} vertices to {filename}")


def write_spring_file(filename, springs):
    """Write springs to IBAMR .spring file format."""
    with open(filename, 'w') as f:
        f.write(f"{len(springs)}\n")
        for s in springs:
            f.write(f"{s[0]:6d} {s[1]:6d} {s[2]:e} {s[3]:e}\n")
    print(f"Written {len(springs)} springs to {filename}")


def write_beam_file(filename, beams):
    """Write beams to IBAMR .beam file format."""
    with open(filename, 'w') as f:
        f.write(f"{len(beams)}\n")
        for b in beams:
            f.write(f"{b[0]:6d} {b[1]:6d} {b[2]:6d} {b[3]:e}\n")
    print(f"Written {len(beams)} beams to {filename}")


def visualize_geometry(vertices, springs, beams, severity, output_file=None):
    """Visualize the valve geometry."""
    fig, ax = plt.subplots(figsize=(10, 10))

    # Plot springs
    for s in springs:
        idx1, idx2 = int(s[0]), int(s[1])
        ax.plot([vertices[idx1, 0], vertices[idx2, 0]],
                [vertices[idx1, 1], vertices[idx2, 1]],
                'b-', alpha=0.3, linewidth=0.5)

    # Plot vertices
    ax.plot(vertices[:, 0], vertices[:, 1], 'ro', markersize=3)

    # Plot circular annulus reference
    theta = np.linspace(0, 2*np.pi, 100)
    ax.plot(1.0 * np.cos(theta), 1.0 * np.sin(theta), 'k--', alpha=0.5, label='Annulus')

    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3)
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_title(f'Aortic Valve Geometry - {severity.capitalize()} Condition')
    ax.legend()

    if output_file:
        plt.savefig(output_file, dpi=150, bbox_inches='tight')
        print(f"Visualization saved to {output_file}")
    else:
        plt.show()

    plt.close()


def main():
    parser = argparse.ArgumentParser(description='Generate 2D aortic valve geometry')
    parser.add_argument('--resolution', type=int, default=32,
                        help='Number of points per leaflet (default: 32)')
    parser.add_argument('--severity', type=str, default='healthy',
                        choices=['healthy', 'mild', 'moderate', 'severe'],
                        help='Disease severity (default: healthy)')
    parser.add_argument('--output-prefix', type=str, default='valve2d',
                        help='Output file prefix (default: valve2d)')
    parser.add_argument('--visualize', action='store_true',
                        help='Generate visualization plot')

    args = parser.parse_args()

    # Generate geometry
    print(f"\nGenerating {args.severity} aortic valve with {args.resolution} points per leaflet...")
    vertices, springs, beams, params = generate_aortic_valve(
        n_points_per_leaflet=args.resolution,
        severity=args.severity
    )

    # Create filenames
    prefix = f"{args.output_prefix}_{args.severity}_{args.resolution}"
    vertex_file = f"{prefix}.vertex"
    spring_file = f"{prefix}.spring"
    beam_file = f"{prefix}.beam"

    # Write files
    write_vertex_file(vertex_file, vertices)
    write_spring_file(spring_file, springs)
    write_beam_file(beam_file, beams)

    # Print summary
    print(f"\nGeometry Summary:")
    print(f"  Disease severity: {args.severity}")
    print(f"  Total vertices: {len(vertices)}")
    print(f"  Total springs: {len(springs)}")
    print(f"  Total beams: {len(beams)}")
    print(f"  Spring stiffness: {params['spring_stiffness']:.2e}")
    print(f"  Beam rigidity: {params['beam_rigidity']:.2e}")
    print(f"  Leaflet mobility factor: {params['mobility']:.2f}")

    # Visualize if requested
    if args.visualize:
        viz_file = f"{prefix}_geometry.png"
        visualize_geometry(vertices, springs, beams, args.severity, viz_file)

    print("\nGeometry generation complete!")


if __name__ == "__main__":
    main()
