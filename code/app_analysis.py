#!/usr/bin/env python3
"""
Smartsheet Neuron Reconstruction Analysis - App Builder Version

This script is designed for Code Ocean's App Builder interface.
It accepts parameters via command-line arguments instead of interactive prompts.
"""

import argparse
import sys
import os
from main import SmartsheetVisualizer

def create_parser():
    """Create argument parser for App Builder parameters"""
    parser = argparse.ArgumentParser(
        description="Analyze neuron reconstruction data from Smartsheet",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python app_analysis.py --soma-location LC
  python app_analysis.py --soma-location all --hive-filter
  python app_analysis.py --soma-location SI --hive-filter --plot-format png
        """
    )
    
    # Core analysis parameters
    parser.add_argument(
        '--soma-location',
        type=str,
        required=True,
        help='Target soma location (e.g., "VM", "PVT", "LC") or "all" for all neurons'
    )
    
    parser.add_argument(
        '--hive-filter',
        action='store_true',
        help='Apply HIVE filter to show only HIVE-marked cells (default: False)'
    )
    
    # Output options
    parser.add_argument(
        '--save-csv',
        action='store_true',
        default=True,
        help='Save results as CSV file (default: True)'
    )
    
    parser.add_argument(
        '--no-csv',
        action='store_true',
        help='Do not save CSV file (overrides --save-csv)'
    )
    
    parser.add_argument(
        '--create-plots',
        action='store_true',
        default=True,
        help='Create visualization plots (default: True)'
    )
    
    parser.add_argument(
        '--no-plots',
        action='store_true',
        help='Do not create plots (overrides --create-plots)'
    )
    
    parser.add_argument(
        '--plot-format',
        type=str,
        choices=['svg', 'png', 'html'],
        default='svg',
        help='Plot output format (default: svg)'
    )
    
    return parser

def validate_environment():
    """Validate that required environment variables are set"""
    if not os.getenv('SMARTSHEET_ACCESS_TOKEN'):
        print("Error: SMARTSHEET_ACCESS_TOKEN environment variable not set!")
        print("\nPlease set the environment variable in Code Ocean:")
        print("1. Go to capsule settings")
        print("2. Add environment variable: SMARTSHEET_ACCESS_TOKEN")
        print("3. Set it to your Smartsheet API token")
        return False
    return True

def main():
    """Main analysis function for App Builder"""
    parser = create_parser()
    args = parser.parse_args()
    
    print("Smartsheet Neuron Reconstruction Analysis")
    print("="*60)
    print("App Builder Mode - Running with parameters:")
    print(f"  Soma Location: {args.soma_location}")
    print(f"  HIVE Filter: {'Yes' if args.hive_filter else 'No'}")
    print(f"  Save CSV: {'Yes' if args.save_csv and not args.no_csv else 'No'}")
    print(f"  Create Plots: {'Yes' if args.create_plots and not args.no_plots else 'No'}")
    if args.create_plots and not args.no_plots:
        print(f"  Plot Format: {args.plot_format}")
    print("")
    
    # Validate environment
    if not validate_environment():
        sys.exit(1)
    
    try:
        # Initialize visualizer
        print("Initializing Smartsheet connection...")
        viz = SmartsheetVisualizer()
        
        # Load the default sheet
        sheets = viz.list_available_sheets()
        if not sheets:
            print("No sheets found. Please check your access token.")
            sys.exit(1)
        
        # Find and load Neuron Reconstructions sheet
        target_sheet = None
        for sheet in sheets:
            if sheet['name'] == "Neuron Reconstructions":
                target_sheet = sheet
                break
        
        if not target_sheet:
            print("Could not find 'Neuron Reconstructions' sheet")
            sys.exit(1)
        
        print(f"Loading sheet: {target_sheet['name']}")
        if not viz.load_sheet(target_sheet['id']):
            print("Failed to load sheet")
            sys.exit(1)
        
        # Process arguments
        save_csv = args.save_csv and not args.no_csv
        create_plots = args.create_plots and not args.no_plots
        
        # Run analysis
        print(f"\nRunning analysis for '{args.soma_location}'...")
        summary_df = viz.analyze_soma_location(
            soma_location=args.soma_location,
            save_csv=save_csv,
            create_plots=create_plots,
            plot_format=args.plot_format,
            hive_filter=args.hive_filter
        )
        
        if not summary_df.empty:
            print(f"\nAnalysis completed successfully!")
            print(f"   Found data for {len(summary_df)} samples")
            print(f"   Total neurons analyzed: {summary_df['Total_Neurons'].sum()}")
            print(f"\nOutput files saved to 'outputs' directory")
        else:
            print(f"\nNo data found matching your criteria.")
            print(f"   Try a different soma location or check if HIVE filter is too restrictive.")
    
    except Exception as e:
        print(f"\nError during analysis: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 