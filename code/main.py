#!/usr/bin/env python3
"""
Smartsheet API Visualization Tool
Main application that integrates all components for accessing Smartsheet data and creating visualizations.
"""

import os
import pandas as pd
from typing import Dict, List, Any, Optional
from datetime import datetime

from config import Config, ConfigError
from smartsheet_client import SmartsheetClient, SmartsheetError
from data_processor import DataProcessor
from visualizer import Visualizer
from soma_analyzer import SomaAnalyzer

class SmartsheetVisualizer:
    """Main application class for Smartsheet data visualization"""
    
    def __init__(self, access_token: Optional[str] = None):
        """
        Initialize the SmartsheetVisualizer
        
        Args:
            access_token: Smartsheet API access token. If None, uses config default.
        """
        # Validate configuration
        Config.validate_config()
        
        # Initialize components
        try:
            self.client = SmartsheetClient(access_token)
            self.logger = Config.get_logger(__name__)
            self.current_sheet = None
            self.current_df = None
            self.processor = None
            self.visualizer = None
            self.soma_analyzer = None
            
            self.logger.info("SmartsheetVisualizer initialized successfully")
            self.logger.info(f"Output directory: {Config.OUTPUT_DIR}")
        except (SmartsheetError, ConfigError) as e:
            raise RuntimeError(f"Failed to initialize SmartsheetVisualizer: {e}")
    
    def list_available_sheets(self) -> List[Dict[str, Any]]:
        """
        List all available sheets
        
        Returns:
            List of sheet information dictionaries
        """
        try:
            sheets = self.client.list_sheets()
            print(f"\nFound {len(sheets)} available sheets:")
            for i, sheet in enumerate(sheets, 1):
                print(f"{i}. {sheet['name']} (ID: {sheet['id']})")
            return sheets
        except Exception as e:
            print(f"Error listing sheets: {e}")
            return []
    
    def load_sheet(self, sheet_identifier: str) -> bool:
        """
        Load a sheet by ID or name
        
        Args:
            sheet_identifier: Sheet ID or name
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Try to load by ID first, then by name
            if str(sheet_identifier).isdigit():
                sheet_data = self.client.get_sheet_by_id(str(sheet_identifier))
            else:
                sheet_data = self.client.get_sheet_by_name(sheet_identifier)
            
            # Convert to DataFrame
            self.current_df = self.client.to_dataframe(sheet_data)
            self.current_sheet = sheet_data
            
            # Initialize processor and visualizer
            self.processor = DataProcessor(self.current_df)
            self.visualizer = Visualizer(self.current_df)
            self.soma_analyzer = SomaAnalyzer(self.current_df)
            
            # Display sheet info
            info = self.client.get_sheet_info(sheet_data)
            print(f"\nLoaded sheet: {info['name']}")
            print(f"Rows: {info['total_rows']}, Columns: {info['column_count']}")
            print(f"Columns: {', '.join(info['columns'])}")
            
            return True
            
        except Exception as e:
            print(f"Error loading sheet '{sheet_identifier}': {e}")
            return False
    
    def get_data_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the current data
        
        Returns:
            Data summary dictionary
        """
        if not self.processor:
            raise ValueError("No sheet loaded. Call load_sheet() first.")
        
        return self.processor.get_summary()
    
    def explore_data(self) -> None:
        """Print data exploration information"""
        if not self.current_df is not None:
            raise ValueError("No sheet loaded. Call load_sheet() first.")
        
        print("\n" + "="*50)
        print("DATA EXPLORATION")
        print("="*50)
        
        # Basic info
        summary = self.get_data_summary()
        print(f"Total rows: {summary['total_rows']}")
        print(f"Total columns: {summary['total_columns']}")
        
        # Column types
        print(f"\nNumeric columns ({len(summary['numeric_columns'])}): {', '.join(summary['numeric_columns'])}")
        print(f"Categorical columns ({len(summary['categorical_columns'])}): {', '.join(summary['categorical_columns'])}")
        print(f"Date columns ({len(summary['date_columns'])}): {', '.join(summary['date_columns'])}")
        
        # Data sample
        print(f"\nFirst 5 rows:")
        print(self.current_df.head())
        
        # Suggested visualizations
        suggestions = self.visualizer.get_suggested_charts(
            summary['numeric_columns'], 
            summary['categorical_columns']
        )
        
        print(f"\nSuggested visualizations ({len(suggestions)}):")
        for i, suggestion in enumerate(suggestions[:5], 1):  # Show first 5
            print(f"{i}. {suggestion['description']}")
    
    def apply_filters(self, filters: Dict[str, Any]) -> pd.DataFrame:
        """
        Apply filters to the current data
        
        Args:
            filters: Dictionary of filter conditions
        
        Returns:
            Filtered DataFrame
        """
        if not self.processor:
            raise ValueError("No sheet loaded. Call load_sheet() first.")
        
        filtered_df = self.processor.apply_filters(filters)
        print(f"Applied filters. Rows: {len(self.current_df)} -> {len(filtered_df)}")
        
        # Update visualizer with filtered data
        self.visualizer = Visualizer(filtered_df)
        
        return filtered_df
    
    def create_bar_chart(self, x_column: str, y_column: str, title: str = None,
                        filters: Dict[str, Any] = None, save: bool = True, 
                        interactive: bool = False) -> Optional[str]:
        """
        Create a bar chart
        
        Args:
            x_column: Column for x-axis
            y_column: Column for y-axis  
            title: Chart title
            filters: Optional filters to apply
            save: Whether to save the chart
            interactive: Whether to create interactive chart
        
        Returns:
            Path to saved chart or None
        """
        if not self.visualizer:
            raise ValueError("No sheet loaded. Call load_sheet() first.")
        
        # Apply filters if provided
        if filters:
            self.apply_filters(filters)
        
        # Generate filename if saving
        save_path = None
        if save:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"bar_chart_{x_column}_{y_column}_{timestamp}.{'html' if interactive else 'png'}"
            save_path = os.path.join(Config.OUTPUT_DIR, filename)
        
        return self.visualizer.create_bar_chart(
            x_column=x_column,
            y_column=y_column,
            title=title,
            save_path=save_path,
            interactive=interactive
        )
    
    def create_pie_chart(self, category_column: str, value_column: str = None,
                        title: str = None, filters: Dict[str, Any] = None,
                        save: bool = True, interactive: bool = False) -> Optional[str]:
        """
        Create a pie chart
        
        Args:
            category_column: Column containing categories
            value_column: Column containing values (optional)
            title: Chart title
            filters: Optional filters to apply
            save: Whether to save the chart
            interactive: Whether to create interactive chart
        
        Returns:
            Path to saved chart or None
        """
        if not self.visualizer:
            raise ValueError("No sheet loaded. Call load_sheet() first.")
        
        # Apply filters if provided
        if filters:
            self.apply_filters(filters)
        
        # Generate filename if saving
        save_path = None
        if save:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"pie_chart_{category_column}_{timestamp}.{'html' if interactive else 'png'}"
            save_path = os.path.join(Config.OUTPUT_DIR, filename)
        
        return self.visualizer.create_pie_chart(
            category_column=category_column,
            value_column=value_column,
            title=title,
            save_path=save_path,
            interactive=interactive
        )
    
    def create_scatter_plot(self, x_column: str, y_column: str, title: str = None,
                           filters: Dict[str, Any] = None, save: bool = True,
                           interactive: bool = False, color_column: str = None) -> Optional[str]:
        """
        Create a scatter plot
        
        Args:
            x_column: Column for x-axis
            y_column: Column for y-axis
            title: Chart title
            filters: Optional filters to apply
            save: Whether to save the chart
            interactive: Whether to create interactive chart
            color_column: Column for color coding
        
        Returns:
            Path to saved chart or None
        """
        if not self.visualizer:
            raise ValueError("No sheet loaded. Call load_sheet() first.")
        
        # Apply filters if provided
        if filters:
            self.apply_filters(filters)
        
        # Generate filename if saving
        save_path = None
        if save:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"scatter_plot_{x_column}_{y_column}_{timestamp}.{'html' if interactive else 'png'}"
            save_path = os.path.join(Config.OUTPUT_DIR, filename)
        
        return self.visualizer.create_scatter_plot(
            x_column=x_column,
            y_column=y_column,
            title=title,
            save_path=save_path,
            interactive=interactive,
            color_column=color_column
        )
    
    def query_and_visualize(self, filters: Dict[str, Any], chart_type: str,
                           x_column: str = None, y_column: str = None,
                           category_column: str = None, value_column: str = None,
                           title: str = None, interactive: bool = False) -> Optional[str]:
        """
        Apply query filters and create visualization in one step
        
        Args:
            filters: Dictionary of filter conditions
            chart_type: Type of chart ('bar', 'pie', 'scatter', 'line', 'histogram')
            x_column: X-axis column (for bar, scatter, line charts)
            y_column: Y-axis column (for bar, scatter, line charts)
            category_column: Category column (for pie charts)
            value_column: Value column (for pie charts)
            title: Chart title
            interactive: Whether to create interactive chart
        
        Returns:
            Path to saved chart or None
        """
        if not self.visualizer:
            raise ValueError("No sheet loaded. Call load_sheet() first.")
        
        # Apply filters
        filtered_df = self.apply_filters(filters)
        print(f"Filtered data: {len(filtered_df)} rows")
        
        # Generate timestamp for filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create visualization based on type
        if chart_type == 'bar':
            if not x_column or not y_column:
                raise ValueError("x_column and y_column required for bar chart")
            filename = f"query_bar_{x_column}_{y_column}_{timestamp}.{'html' if interactive else 'png'}"
            save_path = os.path.join(Config.OUTPUT_DIR, filename)
            return self.visualizer.create_bar_chart(x_column, y_column, title, save_path, interactive)
            
        elif chart_type == 'pie':
            if not category_column:
                raise ValueError("category_column required for pie chart")
            filename = f"query_pie_{category_column}_{timestamp}.{'html' if interactive else 'png'}"
            save_path = os.path.join(Config.OUTPUT_DIR, filename)
            return self.visualizer.create_pie_chart(category_column, value_column, title, save_path, interactive)
            
        elif chart_type == 'scatter':
            if not x_column or not y_column:
                raise ValueError("x_column and y_column required for scatter plot")
            filename = f"query_scatter_{x_column}_{y_column}_{timestamp}.{'html' if interactive else 'png'}"
            save_path = os.path.join(Config.OUTPUT_DIR, filename)
            return self.visualizer.create_scatter_plot(x_column, y_column, title, save_path, interactive)
            
        elif chart_type == 'line':
            if not x_column or not y_column:
                raise ValueError("x_column and y_column required for line chart")
            filename = f"query_line_{x_column}_{y_column}_{timestamp}.{'html' if interactive else 'png'}"
            save_path = os.path.join(Config.OUTPUT_DIR, filename)
            return self.visualizer.create_line_chart(x_column, y_column, title, save_path, interactive)
            
        elif chart_type == 'histogram':
            if not x_column:
                raise ValueError("x_column required for histogram")
            filename = f"query_histogram_{x_column}_{timestamp}.{'html' if interactive else 'png'}"
            save_path = os.path.join(Config.OUTPUT_DIR, filename)
            return self.visualizer.create_histogram(x_column, title=title, save_path=save_path, interactive=interactive)
            
        else:
            raise ValueError(f"Unsupported chart type: {chart_type}")
    
    def search_data(self, search_term: str) -> pd.DataFrame:
        """
        Search for data containing a specific term
        
        Args:
            search_term: Term to search for
        
        Returns:
            DataFrame with matching rows
        """
        if not self.processor:
            raise ValueError("No sheet loaded. Call load_sheet() first.")
        
        results = self.processor.search_data(search_term)
        print(f"Search for '{search_term}' found {len(results)} rows")
        return results
    
    def get_column_stats(self, column: str) -> Dict[str, Any]:
        """
        Get statistics for a specific column
        
        Args:
            column: Column name
        
        Returns:
            Dictionary with column statistics
        """
        if not self.processor:
            raise ValueError("No sheet loaded. Call load_sheet() first.")
        
        return self.processor.get_column_stats(column)
    
    def analyze_soma_location(self, soma_location: str, save_csv: bool = True, 
                            create_plots: bool = True, plot_format: str = 'svg',
                            hive_filter: bool = False) -> pd.DataFrame:
        """
        Analyze neuron reconstructions by soma location
        
        Provides comprehensive analysis including:
        - Sample-level summary with status counts
        - CSV export with sample data
        - Stacked bar plot visualization
        
        Includes ALL neurons where the target location appears in 
        EITHER the CCF Soma Compartment OR Manual Estimated Soma Compartment
        Use "all" to analyze all neurons regardless of soma location
        Optionally filters for only HIVE-marked cells if hive_filter is True
        
        Args:
            soma_location: Target soma location (e.g., "VM", "PVT", "LC") or "all" for all neurons
            save_csv: Whether to save results as CSV
            create_plots: Whether to create stacked bar plot
            plot_format: Format for plots ('svg', 'png', 'html') - defaults to 'svg'
            hive_filter: If True, only include cells marked as "HIVE" - defaults to False
        
        Returns:
            Summary DataFrame with sample-level statistics
        """
        if not self.soma_analyzer:
            raise ValueError("No sheet loaded. Call load_sheet() first.")
        
        summary_df, csv_path, plot_path = self.soma_analyzer.analyze_soma_location(
            soma_location, save_csv, create_plots, plot_format, hive_filter
        )
        
        if csv_path:
                          print(f"\nResults saved to: {csv_path}")
        if plot_path:
            print(f"Visualization saved to: {plot_path}")
        
        return summary_df
    
    def get_available_soma_locations(self) -> Dict[str, int]:
        """
        Get all available soma locations in the dataset
        
        Returns:
            Dictionary mapping soma locations to neuron counts
        """
        if not self.soma_analyzer:
            raise ValueError("No sheet loaded. Call load_sheet() first.")
        
        locations = self.soma_analyzer.get_available_soma_locations()
        
        print("\nAVAILABLE SOMA LOCATIONS:")
        for location, count in list(locations.items())[:15]:  # Show top 15
            print(f"   {location}: {count} neurons")
        
        if len(locations) > 15:
            print(f"   ... and {len(locations) - 15} more")
        
        return locations
    
    def compare_soma_locations(self, locations: List[str]) -> pd.DataFrame:
        """
        Compare multiple soma locations side by side
        
        Args:
            locations: List of soma locations to compare
        
        Returns:
            Comparison DataFrame with aggregate statistics
        """
        if not self.soma_analyzer:
            raise ValueError("No sheet loaded. Call load_sheet() first.")
        
        comparison_df = self.soma_analyzer.compare_soma_locations(locations)
        
        print(f"\nSOMA LOCATION COMPARISON:")
        if not comparison_df.empty:
            print(comparison_df.to_string(index=False))
        
        return comparison_df


def main():
    """Example usage of the SmartsheetVisualizer"""
    print("Smartsheet API Visualization Tool")
    print("="*40)
    
    try:
        # Initialize the visualizer
        viz = SmartsheetVisualizer()
        
        # List available sheets
        sheets = viz.list_available_sheets()
        
        if not sheets:
            print("No sheets found. Please check your access token and permissions.")
            return
        
        # Example: Load the first sheet
        sheet_to_load = sheets[0]['id']
        print(f"\nLoading sheet: {sheets[0]['name']}")
        
        if viz.load_sheet(sheet_to_load):
            # Explore the data
            viz.explore_data()
            
            # Get data summary
            summary = viz.get_data_summary()
            
            # Create some example visualizations if we have appropriate columns
            if summary['numeric_columns'] and summary['categorical_columns']:
                numeric_col = summary['numeric_columns'][0]
                categorical_col = summary['categorical_columns'][0]
                
                print(f"\nCreating example visualizations...")
                
                # Bar chart
                viz.create_bar_chart(
                    x_column=categorical_col,
                    y_column=numeric_col,
                    title=f"{numeric_col} by {categorical_col}",
                    interactive=True
                )
                
                # Pie chart
                viz.create_pie_chart(
                    category_column=categorical_col,
                    title=f"Distribution of {categorical_col}",
                    interactive=True
                )
                
                print("Example visualizations created successfully!")
                print(f"Check the '{Config.OUTPUT_DIR}' directory for saved charts.")
        
        else:
            print("Failed to load sheet.")
    
    except Exception as e:
        print(f"Error: {e}")
        print("\nPlease ensure:")
        print("1. You have a valid .env file with SMARTSHEET_ACCESS_TOKEN")
        print("2. Your access token has proper permissions")
        print("3. You have access to at least one sheet")


if __name__ == "__main__":
    main() 