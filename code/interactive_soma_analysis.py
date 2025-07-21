#!/usr/bin/env python3
"""
Interactive Soma Location Analysis
A command-line interface for analyzing neuron reconstructions by soma location with optional HIVE filtering.
"""

import sys
from typing import Optional
from main import SmartsheetVisualizer

def get_user_input(prompt: str, default: str = None, valid_options: list = None) -> str:
    """
    Get user input with optional default value and validation
    
    Args:
        prompt: The prompt to display to the user
        default: Default value if user presses enter without input
        valid_options: List of valid options (case-insensitive)
    
    Returns:
        User input string
    """
    while True:
        if default:
            user_input = input(f"{prompt} (default: {default}): ").strip()
            if not user_input:
                user_input = default
        else:
            user_input = input(f"{prompt}: ").strip()
        
        if valid_options:
            if user_input.lower() in [option.lower() for option in valid_options]:
                return user_input.lower()
            else:
                print(f"Please enter one of: {', '.join(valid_options)}")
                continue
        
        if user_input:
            return user_input
        else:
            print("Input cannot be empty. Please try again.")

def select_sheet(viz: SmartsheetVisualizer) -> bool:
    """
    Load the default neuron reconstructions sheet
    
    Args:
        viz: SmartsheetVisualizer instance
    
    Returns:
        True if sheet loaded successfully, False otherwise
    """
    print("\n" + "="*60)
    print("SHEET SELECTION")
    print("="*60)
    
    # List available sheets
    sheets = viz.list_available_sheets()
    
    if not sheets:
        print("No sheets found. Please check your access token and permissions.")
        return False
    
    # Look for the neuron reconstructions sheet
    target_sheet_name = "Neuron Reconstructions"
    target_sheet = None
    
    for sheet in sheets:
        if sheet['name'] == target_sheet_name:
            target_sheet = sheet
            break
    
    if target_sheet:
        print(f"\n🔄 Auto-loading default sheet: {target_sheet['name']}")
        return viz.load_sheet(target_sheet['id'])
    else:
        print(f"Could not find '{target_sheet_name}' sheet")
        print("Available sheets:")
        for sheet in sheets[:10]:  # Show first 10 sheets
            print(f"  - {sheet['name']}")
        if len(sheets) > 10:
            print(f"  ... and {len(sheets) - 10} more")
        return False

def run_soma_analysis(viz: SmartsheetVisualizer) -> None:
    """
    Run interactive soma location analysis
    
    Args:
        viz: SmartsheetVisualizer instance with loaded sheet
    """
    print("\n" + "="*60)
    print("SOMA LOCATION ANALYSIS")
    print("="*60)
    
    # Show available soma locations
    print("\nGetting available soma locations...")
    available_locations = viz.get_available_soma_locations()
    
    # Get soma location from user
    print(f"\nExample locations: {', '.join(list(available_locations.keys())[:10])}")
    print(f"💡 TIP: Enter 'all' to analyze all neurons regardless of soma location")
    soma_location = get_user_input("Enter target soma location (e.g., VM, PVT, LC, all)")
    
    # Get HIVE filter preference
    print(f"\nHIVE FILTERING OPTION")
    print("This will filter results to show only cells marked as 'HIVE' in the smartsheet.")
    hive_choice = get_user_input("Apply HIVE filter? (yes/no)", default="no", valid_options=["yes", "no", "y", "n"])
    hive_filter = hive_choice.lower() in ['yes', 'y']
    
    # Get output preferences
    print(f"\nOUTPUT OPTIONS")
    save_csv = get_user_input("Save results as CSV? (yes/no)", default="yes", valid_options=["yes", "no", "y", "n"])
    save_csv = save_csv.lower() in ['yes', 'y']
    
    create_plots = get_user_input("Create visualization plots? (yes/no)", default="yes", valid_options=["yes", "no", "y", "n"])
    create_plots = create_plots.lower() in ['yes', 'y']
    
    plot_format = "svg"
    if create_plots:
        plot_format = get_user_input("Plot format (svg/png/html)", default="svg", valid_options=["svg", "png", "html"])
    
    # Run the analysis
    print(f"\n🔬 RUNNING ANALYSIS...")
    print(f"   Soma Location: {soma_location}")
    print(f"   HIVE Filter: {'Yes' if hive_filter else 'No'}")
    print(f"   Save CSV: {'Yes' if save_csv else 'No'}")
    print(f"   Create Plots: {'Yes' if create_plots else 'No'}")
    if create_plots:
        print(f"   Plot Format: {plot_format}")
    
    try:
        summary_df = viz.analyze_soma_location(
            soma_location=soma_location,
            save_csv=save_csv,
            create_plots=create_plots,
            plot_format=plot_format,
            hive_filter=hive_filter
        )
        
        if not summary_df.empty:
                    print(f"\nAnalysis completed successfully!")
        print(f"   Found data for {len(summary_df)} samples")
            print(f"   Total neurons analyzed: {summary_df['Total_Neurons'].sum()}")
        else:
            print(f"\nNo data found matching your criteria.")
            print(f"   Try a different soma location or check if HIVE filter is too restrictive.")
    
    except Exception as e:
        print(f"\nError during analysis: {e}")

def main():
    """Main interactive function"""
    print("Interactive Soma Location Analysis Tool")
    print("="*60)
    print("This tool analyzes neuron reconstructions by soma location")
    print("with optional HIVE filtering capabilities.")
    
    try:
        # Initialize the visualizer
        print("\n🔄 Initializing Smartsheet connection...")
        viz = SmartsheetVisualizer()
        
        # Select and load sheet
        if not select_sheet(viz):
            print("\nFailed to load sheet. Exiting.")
            return
        
        # Run analysis
        while True:
            run_soma_analysis(viz)
            
            # Ask if user wants to run another analysis
            print(f"\n" + "="*60)
            continue_choice = get_user_input("Run another analysis? (yes/no)", default="no", valid_options=["yes", "no", "y", "n"])
            
            if continue_choice.lower() not in ['yes', 'y']:
                break
        
                  print(f"\nThank you for using the Soma Location Analysis Tool!")
        print(f"Check the 'outputs' directory for your saved results.")
    
    except KeyboardInterrupt:
                  print(f"\n\nAnalysis interrupted by user. Goodbye!")
    except Exception as e:
        print(f"\nError: {e}")
        print("\nPlease ensure:")
        print("1. You have a valid .env file with SMARTSHEET_ACCESS_TOKEN")
        print("2. Your access token has proper permissions")
        print("3. You have access to at least one sheet")
        sys.exit(1)

if __name__ == "__main__":
    main() 