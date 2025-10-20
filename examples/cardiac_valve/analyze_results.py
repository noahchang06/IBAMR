#!/usr/bin/env python3
"""
Post-processing and analysis of IBAMR valve simulation results.

This script extracts clinical metrics from simulation output:
- Pressure gradients (peak and mean)
- Peak jet velocity
- Effective orifice area
- Wall shear stress
- Flow rate through valve

Usage:
    python analyze_results.py --viz-dir viz_valve2d --output metrics.csv
"""

import numpy as np
import argparse
import os
import csv


def analyze_simulation_results(viz_dir, output_file='metrics.csv'):
    """
    Analyze IBAMR simulation results and extract clinical metrics.

    Note: This is a template function. Actual implementation requires
    reading IBAMR output files (VisIt-compatible format).
    """

    print(f"Analyzing results from: {viz_dir}")

    # Check if visualization directory exists
    if not os.path.exists(viz_dir):
        print(f"Error: Directory {viz_dir} not found.")
        print("Have you run the simulation yet?")
        return

    # Placeholder for actual data reading
    # In practice, you would use libraries like:
    # - vtk/pyvista to read .vtk files
    # - h5py to read HDF5 files
    # - visit_utils for VisIt databases

    print("\nTo implement full analysis, you'll need to:")
    print("1. Read velocity field data from VisIt dumps")
    print("2. Read pressure field data")
    print("3. Read Lagrangian structure positions")
    print("4. Calculate metrics over time")

    # Example metrics structure
    metrics = {
        'time': [],
        'peak_velocity': [],
        'mean_pressure_gradient': [],
        'peak_pressure_gradient': [],
        'flow_rate': [],
        'effective_orifice_area': [],
        'max_shear_stress': []
    }

    print("\nExample Clinical Metrics (Template):")
    print("-" * 60)
    print(f"{'Metric':<30} {'Value':<15} {'Units':<15}")
    print("-" * 60)

    # Template values (these would come from actual data)
    example_metrics = [
        ("Peak Jet Velocity", "150.0", "cm/s"),
        ("Mean Pressure Gradient", "25.0", "mmHg"),
        ("Peak Pressure Gradient", "40.0", "mmHg"),
        ("Effective Orifice Area", "1.2", "cm²"),
        ("Max Wall Shear Stress", "80.0", "dyne/cm²"),
        ("Cardiac Output", "5.0", "L/min"),
    ]

    for metric, value, units in example_metrics:
        print(f"{metric:<30} {value:<15} {units:<15}")

    print("-" * 60)
    print("\nClinical Interpretation:")
    print("  Stenosis Severity: MODERATE-SEVERE")
    print("  Recommendation: Consider valve replacement")
    print("  (Based on ACC/AHA guidelines)")

    # Save template CSV
    with open(output_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Metric', 'Value', 'Units'])
        writer.writerows(example_metrics)

    print(f"\nMetrics saved to: {output_file}")


def calculate_clinical_severity(mean_gradient, peak_velocity, eoa):
    """
    Classify valve stenosis severity based on clinical criteria.

    Parameters from ACC/AHA guidelines:
    - Mild: Mean gradient <25 mmHg, Peak velocity <3 m/s, EOA >1.5 cm²
    - Moderate: Mean gradient 25-40 mmHg, Peak velocity 3-4 m/s, EOA 1.0-1.5 cm²
    - Severe: Mean gradient >40 mmHg, Peak velocity >4 m/s, EOA <1.0 cm²
    """

    if mean_gradient > 40 or peak_velocity > 400 or eoa < 1.0:
        return "SEVERE"
    elif mean_gradient > 25 or peak_velocity > 300 or eoa < 1.5:
        return "MODERATE"
    elif mean_gradient > 10 or peak_velocity > 200 or eoa < 2.0:
        return "MILD"
    else:
        return "NORMAL"


def plot_temporal_metrics(time_data, velocity_data, pressure_data,
                         output_file='temporal_metrics.png'):
    """
    Plot metrics over the cardiac cycle.

    Shows how velocity and pressure evolve during systole/diastole.
    """
    import matplotlib.pyplot as plt

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)

    # Velocity plot
    ax1.plot(time_data, velocity_data, 'b-', linewidth=2)
    ax1.axhline(y=100, color='g', linestyle='--', label='Peak normal')
    ax1.axhline(y=400, color='r', linestyle='--', label='Severe stenosis threshold')
    ax1.set_ylabel('Peak Velocity (cm/s)', fontsize=12)
    ax1.set_title('Hemodynamic Metrics Over Cardiac Cycle', fontsize=14, weight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.legend()

    # Pressure gradient plot
    ax2.plot(time_data, pressure_data, 'r-', linewidth=2)
    ax2.axhline(y=40, color='r', linestyle='--', label='Severe stenosis threshold')
    ax2.axhline(y=25, color='orange', linestyle='--', label='Moderate threshold')
    ax2.set_xlabel('Time (s)', fontsize=12)
    ax2.set_ylabel('Pressure Gradient (mmHg)', fontsize=12)
    ax2.grid(True, alpha=0.3)
    ax2.legend()

    plt.tight_layout()
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"Temporal plot saved to: {output_file}")
    plt.close()


def generate_clinical_report(severity, metrics, output_file='clinical_report.txt'):
    """Generate a clinical report summary."""

    report = f"""
{'='*70}
                    AORTIC VALVE SIMULATION REPORT
{'='*70}

Patient Condition: {severity.upper()}

HEMODYNAMIC MEASUREMENTS:
{'-'*70}
{'Peak Jet Velocity:':<35} {metrics.get('peak_velocity', 'N/A'):>10} cm/s
{'Mean Pressure Gradient:':<35} {metrics.get('mean_gradient', 'N/A'):>10} mmHg
{'Peak Pressure Gradient:':<35} {metrics.get('peak_gradient', 'N/A'):>10} mmHg
{'Effective Orifice Area:':<35} {metrics.get('eoa', 'N/A'):>10} cm²

STRUCTURAL PARAMETERS:
{'-'*70}
{'Leaflet Mobility:':<35} {metrics.get('mobility', 'N/A'):>10}
{'Calcification Index:':<35} {metrics.get('calcification', 'N/A'):>10}

FLOW CHARACTERISTICS:
{'-'*70}
{'Cardiac Output:':<35} {metrics.get('cardiac_output', 'N/A'):>10} L/min
{'Regurgitant Volume:':<35} {metrics.get('regurgitation', 'N/A'):>10} mL
{'Peak Wall Shear Stress:':<35} {metrics.get('max_shear', 'N/A'):>10} dyne/cm²

CLINICAL INTERPRETATION:
{'-'*70}
Based on ACC/AHA Guidelines for Valvular Heart Disease:

"""

    # Add severity-specific recommendations
    if severity.upper() == 'SEVERE':
        report += """
Severity: SEVERE AORTIC STENOSIS
Recommendation: AORTIC VALVE REPLACEMENT INDICATED
  - Symptomatic patients: Class I recommendation (immediate intervention)
  - Asymptomatic with EF <50%: Class I recommendation
  - Consider TAVR vs. surgical AVR based on risk assessment

Risk Factors:
  - High transvalvular pressure gradient (>40 mmHg)
  - Significantly reduced orifice area (<1.0 cm²)
  - Risk of sudden cardiac death if untreated
"""
    elif severity.upper() == 'MODERATE':
        report += """
Severity: MODERATE AORTIC STENOSIS
Recommendation: CLOSE MONITORING, CONSIDER INTERVENTION IF SYMPTOMATIC
  - Serial echocardiography every 6-12 months
  - Exercise testing if asymptomatic
  - Intervention if symptoms develop

Watchpoints:
  - Monitor for symptom development (angina, syncope, dyspnea)
  - Track progression rate
  - Optimize medical management of comorbidities
"""
    elif severity.upper() == 'MILD':
        report += """
Severity: MILD AORTIC STENOSIS
Recommendation: PERIODIC MONITORING
  - Echocardiography every 12-24 months
  - No intervention needed at this time
  - Lifestyle modifications as appropriate

Management:
  - Control cardiovascular risk factors
  - Regular follow-up
  - Patient education on symptoms to watch for
"""
    else:
        report += """
Severity: NORMAL VALVE FUNCTION
Recommendation: NO INTERVENTION NEEDED
  - Routine cardiovascular health maintenance
  - Standard screening intervals
"""

    report += f"""
{'='*70}
Report Generated: [Simulation Date]
Simulation Method: Immersed Boundary Method (IBAMR)
Model: 2D Aortic Valve FSI Simulation
{'='*70}

DISCLAIMER: This simulation is for educational and research purposes.
Clinical decisions should be based on comprehensive patient evaluation
including physical examination, medical imaging, and laboratory studies.
{'='*70}
"""

    with open(output_file, 'w') as f:
        f.write(report)

    print(report)
    print(f"\nReport saved to: {output_file}")


def main():
    parser = argparse.ArgumentParser(description='Analyze valve simulation results')
    parser.add_argument('--viz-dir', type=str, default='viz_valve2d',
                       help='Visualization data directory')
    parser.add_argument('--output', type=str, default='metrics.csv',
                       help='Output CSV file for metrics')
    parser.add_argument('--severity', type=str, default='moderate',
                       help='Disease severity for report generation')
    parser.add_argument('--generate-report', action='store_true',
                       help='Generate clinical report')

    args = parser.parse_args()

    # Analyze results
    analyze_simulation_results(args.viz_dir, args.output)

    # Generate report if requested
    if args.generate_report:
        # Example metrics (would be computed from actual data)
        example_metrics = {
            'peak_velocity': '150.0',
            'mean_gradient': '25.0',
            'peak_gradient': '40.0',
            'eoa': '1.2',
            'mobility': '0.7',
            'calcification': 'Moderate',
            'cardiac_output': '5.0',
            'regurgitation': '5.0',
            'max_shear': '80.0'
        }

        generate_clinical_report(args.severity, example_metrics,
                               f'clinical_report_{args.severity}.txt')


if __name__ == "__main__":
    main()
