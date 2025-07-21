#!/usr/bin/env python3
"""
Smartsheet Neuron Reconstruction Analysis Tool - Entry Point

Simple entry script for Code Ocean capsule.
Run this script to start the interactive analysis.
"""

import os
import sys

def check_environment():
    """Check if the required environment variables are set"""
    if not os.getenv('SMARTSHEET_ACCESS_TOKEN'):
        print("Error: SMARTSHEET_ACCESS_TOKEN environment variable not set!")
        print("\nTo fix this:")
        print("1. Go to Code Ocean capsule settings")
        print("2. Add environment variable: SMARTSHEET_ACCESS_TOKEN")
        print("3. Set it to your Smartsheet API token")
        print("\nTo get a token:")
        print("• Log in to Smartsheet")
        print("• Go to Account > Apps & Integrations > API Access")
        print("• Generate new access token")
        return False
    return True

def main():
    """Main entry point"""
    print("Smartsheet Neuron Reconstruction Analysis Tool")
    print("="*60)
    print("Welcome to the Code Ocean capsule!")
    print("")
    
    # Check environment
    if not check_environment():
        sys.exit(1)
    
    print("Environment configured correctly")
    print("Starting interactive analysis...")
    print("")
    
    # Import and run the interactive analysis
    try:
        from interactive_soma_analysis import main as run_interactive
        run_interactive()
    except Exception as e:
        print(f"Error starting analysis: {e}")
        print("\nPlease check that all dependencies are installed correctly.")
        sys.exit(1)

if __name__ == "__main__":
    main() 