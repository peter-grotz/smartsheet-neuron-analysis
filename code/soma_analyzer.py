#!/usr/bin/env python3
"""
Soma Location Analysis Module for Neuron Reconstructions

This module provides specialized analysis for neuron reconstruction data
based on soma location queries with intelligent filtering logic.
"""

import pandas as pd
import numpy as np
import re
from typing import Dict, List, Any, Optional, Tuple
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from datetime import datetime
import os

from config import Config, ConfigError
from utils import NEURON_STATUSES, PLOT_COLORS, validate_required_columns

class SomaAnalyzer:
    """Analyzer for soma location-based queries on neuron reconstruction data"""
    
    # Required columns for analysis
    REQUIRED_COLUMNS = [
        'ID', 'CCF Soma Compartment', 'Manual Estimated Soma Compartment',
        'Status 1', 'Genotype', 'Registered?'
    ]
    
    # Status columns for aggregation
    STATUS_COLUMNS = ['Completed', 'Pending_Review', 'Hold', 'Untraceable', 'In_Progress', 'Incomplete', 'Other']
    
    def __init__(self, df: pd.DataFrame):
        """
        Initialize the analyzer with neuron reconstruction data
        
        Args:
            df: DataFrame containing neuron reconstruction data
            
        Raises:
            ValueError: If DataFrame is empty or missing required columns
        """
        if df.empty:
            raise ValueError("Input DataFrame cannot be empty")
            
        self.df = df.copy()
        self.logger = Config.get_logger(__name__)
        
        # Validate required columns
        missing_cols = validate_required_columns(df, self.REQUIRED_COLUMNS, self.logger)
        if missing_cols:
            self.logger.warning(f"Analysis may be incomplete due to missing columns: {missing_cols}")
    
    def _extract_sample_id(self, id_value: str) -> Optional[str]:
        """
        Extract sample ID from the ID column
        Example: "N030-657676" -> "657676"
        
        Args:
            id_value: Value from the ID column
            
        Returns:
            Extracted sample ID or None if extraction fails
        """
        if pd.isna(id_value) or not isinstance(id_value, str):
            return None
        
        # Look for pattern like "N030-657676" and extract the number after the dash
        match = re.search(r'-(\d+)', str(id_value))
        if match:
            return match.group(1)
        
        # If no dash pattern, look for any sequence of digits
        match = re.search(r'(\d+)', str(id_value))
        if match:
            return match.group(1)
        
        return str(id_value).strip()
    
    def _find_hive_column(self) -> Optional[str]:
        """
        Find the column that contains HIVE data
        
        Returns:
            Column name that contains HIVE markings, or None if not found
        """
        # First look for columns with "hive" in the name (most reliable)
        for col in self.df.columns:
            if 'hive' in col.lower():
                self.logger.debug(f"Found HIVE column by name: {col}")
                return col
        
        # Look for columns that contain boolean True values that might be HIVE data
        for col in self.df.columns:
            if (self.df[col] == True).any():
                self.logger.debug(f"Found potential HIVE column with boolean values: {col}")
                return col
                
        self.logger.warning("No HIVE column found in data")
        return None
    
    def _apply_soma_location_filter(self, soma_location: str, hive_filter: bool = False) -> pd.DataFrame:
        """
        Apply filtering logic for soma location and optionally HIVE
        
        Args:
            soma_location: Target soma location (e.g., "VM", "PVT", "LC") or "all" for all neurons
            hive_filter: If True, only include cells marked as "HIVE"
            
        Returns:
            Filtered DataFrame
        """
        # Check if user wants all neurons regardless of location
        if soma_location.lower() == 'all':
            filtered_df = self.df.copy()
            self.logger.info("Including all neurons regardless of soma location")
        else:
            # Apply soma location filter
            soma_mask = (
                (self.df['CCF Soma Compartment'].astype(str).str.contains(soma_location, case=False, na=False)) |
                (self.df['Manual Estimated Soma Compartment'].astype(str).str.contains(soma_location, case=False, na=False))
            )
            filtered_df = self.df[soma_mask]
            self.logger.info(f"Soma location filter '{soma_location}' found {len(filtered_df)} neurons")
        
        # Apply HIVE filter if requested
        if hive_filter:
            hive_column = self._find_hive_column()
            if hive_column:
                initial_count = len(filtered_df)
                hive_mask = filtered_df[hive_column] == True
                filtered_df = filtered_df[hive_mask]
                
                self.logger.info(f"HIVE filter reduced {initial_count} to {len(filtered_df)} neurons")
            else:
                self.logger.error("HIVE filter requested but no HIVE column found")
                return pd.DataFrame()
        
        if filtered_df.empty:
            self.logger.warning("No neurons found matching the specified criteria")
            
        return filtered_df
    
    def _create_summary_data(self, filtered_df: pd.DataFrame, hive_filter: bool) -> List[Dict[str, Any]]:
        """
        Create summary data grouped by sample ID
        
        Args:
            filtered_df: Filtered DataFrame
            hive_filter: Whether HIVE filter was applied
            
        Returns:
            List of summary dictionaries
        """
        # Extract sample IDs
        filtered_df = filtered_df.copy()
        filtered_df['Sample_ID'] = filtered_df['ID'].apply(self._extract_sample_id)
        
        summary_data = []
        
        for sample_id in filtered_df['Sample_ID'].dropna().unique():
            sample_data = filtered_df[filtered_df['Sample_ID'] == sample_id]
            
            if len(sample_data) == 0:
                continue
                
            # Get sample-level information
            genotype = sample_data['Genotype'].iloc[0] if 'Genotype' in sample_data.columns else 'Unknown'
            registration_status = sample_data['Registered?'].iloc[0] if 'Registered?' in sample_data.columns else 'Unknown'
            
            # Count status types
            status_counts = sample_data['Status 1'].value_counts()
            
            summary_row = {
                'Sample_ID': sample_id,
                'Genotype': genotype,
                'Completed': status_counts.get(NEURON_STATUSES['COMPLETED'], 0),
                'Pending_Review': status_counts.get(NEURON_STATUSES['PENDING_REVIEW'], 0),
                'Hold': status_counts.get(NEURON_STATUSES['HOLD'], 0),
                'Untraceable': status_counts.get(NEURON_STATUSES['UNTRACEABLE'], 0),
                'In_Progress': status_counts.get(NEURON_STATUSES['IN_PROGRESS'], 0),
                'Incomplete': status_counts.get(NEURON_STATUSES['INCOMPLETE'], 0),
                'Other': sum([count for status, count in status_counts.items() 
                            if status not in NEURON_STATUSES.values()]),
                'Registration_Status': registration_status,
                'Total_Neurons': len(sample_data),
                'HIVE_Filter': 'Yes' if hive_filter else 'No'
            }
            summary_data.append(summary_row)
        
        return summary_data
    
    def analyze_soma_location(self, soma_location: str, save_csv: bool = True, 
                            create_plots: bool = True, plot_format: str = None,
                            hive_filter: bool = False) -> Tuple[pd.DataFrame, Optional[str], Optional[str]]:
        """
        Perform comprehensive soma location analysis
        
        Args:
            soma_location: Target soma location (e.g., "VM", "PVT", "LC") or "all" for all neurons
            save_csv: Whether to save results as CSV
            create_plots: Whether to create visualization plots
            plot_format: Format for plots (uses config default if None)
            hive_filter: If True, only include cells marked as "HIVE"
            
        Returns:
            Tuple of (summary_df, csv_path, plot_path)
        """
        if plot_format is None:
            plot_format = Config.DEFAULT_PLOT_FORMAT
            
        hive_suffix = "_HIVE" if hive_filter else ""
        location_display = "ALL_LOCATIONS" if soma_location.lower() == 'all' else soma_location.upper()
        
        self.logger.info(f"Starting soma location analysis: {location_display}{hive_suffix}")
        
        try:
            # Apply filtering
            filtered_df = self._apply_soma_location_filter(soma_location, hive_filter)
            
            if filtered_df.empty:
                return pd.DataFrame(), None, None
            
            # Create summary data
            summary_data = self._create_summary_data(filtered_df, hive_filter)
            summary_df = pd.DataFrame(summary_data)
            
            # Display summary statistics
            self._print_summary_stats(summary_df, location_display, hive_filter)
            
            # Save CSV
            csv_path = None
            if save_csv and not summary_df.empty:
                csv_path = self._save_csv(summary_df, location_display, hive_suffix)
            
            # Create plots
            plot_path = None
            if create_plots and not summary_df.empty:
                plot_path = self._create_stacked_bar_plot(summary_df, location_display, plot_format, hive_filter)
            
            self.logger.info("Analysis completed successfully")
            return summary_df, csv_path, plot_path
            
        except Exception as e:
            self.logger.error(f"Analysis failed: {e}")
            raise
    
    def _save_csv(self, summary_df: pd.DataFrame, location_display: str, hive_suffix: str) -> str:
        """Save summary data to CSV file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_location = "ALL" if location_display == "ALL_LOCATIONS" else location_display
        csv_filename = f"soma_analysis_{file_location}{hive_suffix}_{timestamp}.csv"
        csv_path = os.path.join(Config.OUTPUT_DIR, csv_filename)
        
        summary_df.to_csv(csv_path, index=False)
        self.logger.info(f"CSV saved: {csv_path}")
        return csv_path
    
    def _print_summary_stats(self, summary_df: pd.DataFrame, location_display: str, hive_filter: bool = False):
        """Print summary statistics"""
        if summary_df.empty:
            return
        
        hive_suffix = " (HIVE only)" if hive_filter else ""
        total_samples = len(summary_df)
        total_neurons = summary_df['Total_Neurons'].sum()
        
        print(f"\nSUMMARY STATISTICS for {location_display}{hive_suffix}:")
        print(f"   Total Samples: {total_samples}")
        print(f"   Total Neurons: {total_neurons}")
        
        # Status breakdown
        for status_col in self.STATUS_COLUMNS[:-1]:  # Exclude 'Other'
            total = summary_df[status_col].sum()
            percentage = total/total_neurons*100 if total_neurons > 0 else 0
            print(f"   {status_col.replace('_', ' ')}: {total} ({percentage:.1f}%)")
        
        # Genotype distribution
        if 'Genotype' in summary_df.columns:
            genotypes = summary_df['Genotype'].value_counts()
            print(f"\nGENOTYPE DISTRIBUTION:")
            for genotype, count in genotypes.items():
                print(f"   {genotype}: {count} samples")
        
        # Registration status
        if 'Registration_Status' in summary_df.columns:
            reg_status = summary_df['Registration_Status'].value_counts()
            print(f"\nREGISTRATION STATUS:")
            for status, count in reg_status.items():
                print(f"   {status}: {count} samples")
    
    def _create_stacked_bar_plot(self, summary_df: pd.DataFrame, location_display: str, 
                                plot_format: str, hive_filter: bool = False) -> str:
        """Create stacked bar plot using matplotlib"""
        try:
            # Prepare data for stacked bar plot
            plot_data = summary_df[['Sample_ID'] + self.STATUS_COLUMNS].set_index('Sample_ID')
            
            # Limit samples for readability
            if len(plot_data) > Config.MAX_SAMPLES_TO_DISPLAY:
                self.logger.warning(f"Too many samples ({len(plot_data)}), showing first {Config.MAX_SAMPLES_TO_DISPLAY}")
                plot_data = plot_data.head(Config.MAX_SAMPLES_TO_DISPLAY)
            
            # Create the matplotlib figure
            fig, ax = plt.subplots(figsize=(max(12, len(plot_data) * 0.8), 8))
            
            # Colors for each status (convert plotly colors to matplotlib format)
            colors = [PLOT_COLORS.get(status, '#B0B0B0') for status in self.STATUS_COLUMNS]
            
            # Create stacked bar chart
            bottom = np.zeros(len(plot_data))
            bars = []
            
            for i, status in enumerate(self.STATUS_COLUMNS):
                if status in plot_data.columns:
                    bars.append(ax.bar(
                        plot_data.index, 
                        plot_data[status], 
                        bottom=bottom,
                        color=colors[i],
                        label=status.replace('_', ' '),
                        edgecolor='white',
                        linewidth=0.5
                    ))
                    bottom += plot_data[status]
            
            # Customize the plot
            hive_suffix = " (HIVE only)" if hive_filter else ""
            ax.set_title(f'Neuron Reconstruction Status by Sample - {location_display}{hive_suffix}', 
                        fontsize=14, fontweight='bold', pad=20)
            ax.set_xlabel('Sample ID', fontsize=12)
            ax.set_ylabel('Number of Neurons', fontsize=12)
            
            # Rotate x-axis labels if many samples
            if len(plot_data) > 10:
                plt.xticks(rotation=45, ha='right')
            
            # Add legend
            ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
            
            # Adjust layout to prevent label cutoff
            plt.tight_layout()
            
            # Save plot
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            hive_file_suffix = "_HIVE" if hive_filter else ""
            file_location = "ALL" if location_display == "ALL_LOCATIONS" else location_display
            plot_filename = f"soma_analysis_plot_{file_location}{hive_file_suffix}_{timestamp}.{plot_format}"
            plot_path = os.path.join(Config.OUTPUT_DIR, plot_filename)
            
            # Save in requested format
            if plot_format.lower() in ['png', 'svg', 'pdf']:
                plt.savefig(plot_path, format=plot_format, dpi=300, bbox_inches='tight')
            else:
                # Default to PNG if unsupported format
                plot_path = plot_path.replace(f".{plot_format}", ".png")
                plt.savefig(plot_path, format='png', dpi=300, bbox_inches='tight')
            
            plt.close()  # Close the figure to free memory
            
            self.logger.info(f"Plot saved: {plot_path}")
            return plot_path
            
        except Exception as e:
            self.logger.error(f"Failed to create plot: {e}")
            raise
    
    def get_available_soma_locations(self) -> Dict[str, int]:
        """Get list of available soma locations in the dataset"""
        locations = {}
        
        # Collect from CCF Soma Compartment
        if 'CCF Soma Compartment' in self.df.columns:
            ccf_locations = self.df['CCF Soma Compartment'].dropna().astype(str)
            for location in ccf_locations:
                if location != 'nan':
                    locations[location] = locations.get(location, 0) + 1
        
        # Collect from Manual Estimated Soma Compartment  
        if 'Manual Estimated Soma Compartment' in self.df.columns:
            manual_locations = self.df['Manual Estimated Soma Compartment'].dropna().astype(str)
            for location in manual_locations:
                if location != 'nan':
                    locations[location] = locations.get(location, 0) + 1
        
        return dict(sorted(locations.items(), key=lambda x: x[1], reverse=True))
    
    def compare_soma_locations(self, locations: List[str], save_csv: bool = True, 
                             create_plots: bool = True, plot_format: str = None) -> pd.DataFrame:
        """Compare multiple soma locations side by side"""
        if plot_format is None:
            plot_format = Config.DEFAULT_PLOT_FORMAT
            
        comparison_data = []
        
        for location in locations:
            try:
                summary_df, _, _ = self.analyze_soma_location(
                    location, save_csv=False, create_plots=False, plot_format=plot_format
                )
                
                if not summary_df.empty:
                    totals = {
                        'Soma_Location': location,
                        'Total_Samples': len(summary_df),
                        'Total_Neurons': summary_df['Total_Neurons'].sum(),
                        **{col: summary_df[col].sum() for col in self.STATUS_COLUMNS}
                    }
                    comparison_data.append(totals)
            except Exception as e:
                self.logger.error(f"Failed to analyze location '{location}': {e}")
        
        comparison_df = pd.DataFrame(comparison_data)
        
        if save_csv and not comparison_df.empty:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            csv_filename = f"soma_comparison_{timestamp}.csv"
            csv_path = os.path.join(Config.OUTPUT_DIR, csv_filename)
            comparison_df.to_csv(csv_path, index=False)
            self.logger.info(f"Comparison CSV saved: {csv_path}")
        
        return comparison_df 