import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
import os
from config import Config

class Visualizer:
    """Class for creating visualizations from Smartsheet data using matplotlib"""
    
    def __init__(self, df: pd.DataFrame, output_dir: Optional[str] = None):
        """
        Initialize the visualizer
        
        Args:
            df: pandas DataFrame containing the data to visualize
            output_dir: Directory to save plots. If None, uses config default.
        """
        self.df = df
        self.output_dir = output_dir or Config.OUTPUT_DIR
        
        # Ensure output directory exists
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        
        # Set up matplotlib style
        plt.style.use('default')
        
    def create_bar_chart(self, x_column: str, y_column: str = None, 
                        title: str = "Bar Chart", save_path: str = None,
                        interactive: bool = False) -> str:
        """
        Create a bar chart using matplotlib
        
        Args:
            x_column: Column for x-axis (categories)
            y_column: Column for y-axis (values). If None, counts x_column values
            title: Title for the chart
            save_path: Custom save path. If None, auto-generates
            interactive: Ignored (kept for compatibility)
            
        Returns:
            Path to saved chart file
        """
        # Prepare data
        if y_column is None:
            # Count occurrences of x_column values
            data = self.df[x_column].value_counts()
        else:
            # Group by x_column and sum y_column
            data = self.df.groupby(x_column)[y_column].sum()
        
        # Create plot
        fig, ax = plt.subplots(figsize=(10, 6))
        data.plot(kind='bar', ax=ax)
        ax.set_title(title)
        ax.set_xlabel(x_column)
        ax.set_ylabel(y_column or 'Count')
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        # Save plot
        if save_path is None:
            timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
            filename = f"bar_chart_{title.replace(' ', '_')}_{timestamp}.png"
            save_path = os.path.join(self.output_dir, filename)
        
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return save_path
    
    def create_pie_chart(self, category_column: str, value_column: str = None,
                        title: str = "Pie Chart", save_path: str = None,
                        interactive: bool = False) -> str:
        """
        Create a pie chart using matplotlib
        
        Args:
            category_column: Column for categories
            value_column: Column for values. If None, counts category_column values
            title: Title for the chart
            save_path: Custom save path. If None, auto-generates
            interactive: Ignored (kept for compatibility)
            
        Returns:
            Path to saved chart file
        """
        # Prepare data
        if value_column is None:
            data = self.df[category_column].value_counts()
        else:
            data = self.df.groupby(category_column)[value_column].sum()
        
        # Create plot
        fig, ax = plt.subplots(figsize=(8, 8))
        data.plot(kind='pie', ax=ax, autopct='%1.1f%%')
        ax.set_title(title)
        ax.set_ylabel('')  # Remove ylabel for pie chart
        
        # Save plot
        if save_path is None:
            timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
            filename = f"pie_chart_{title.replace(' ', '_')}_{timestamp}.png"
            save_path = os.path.join(self.output_dir, filename)
        
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return save_path
    
    def create_scatter_plot(self, x_column: str, y_column: str,
                           title: str = "Scatter Plot", save_path: str = None,
                           interactive: bool = False) -> str:
        """
        Create a scatter plot using matplotlib
        
        Args:
            x_column: Column for x-axis
            y_column: Column for y-axis  
            title: Title for the chart
            save_path: Custom save path. If None, auto-generates
            interactive: Ignored (kept for compatibility)
            
        Returns:
            Path to saved chart file
        """
        # Create plot
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.scatter(self.df[x_column], self.df[y_column], alpha=0.6)
        ax.set_title(title)
        ax.set_xlabel(x_column)
        ax.set_ylabel(y_column)
        plt.tight_layout()
        
        # Save plot
        if save_path is None:
            timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
            filename = f"scatter_plot_{title.replace(' ', '_')}_{timestamp}.png"
            save_path = os.path.join(self.output_dir, filename)
        
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return save_path
    
    def create_line_chart(self, x_column: str, y_column: str,
                         title: str = "Line Chart", save_path: str = None,
                         interactive: bool = False) -> str:
        """
        Create a line chart using matplotlib
        
        Args:
            x_column: Column for x-axis
            y_column: Column for y-axis
            title: Title for the chart
            save_path: Custom save path. If None, auto-generates
            interactive: Ignored (kept for compatibility)
            
        Returns:
            Path to saved chart file
        """
        # Create plot
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(self.df[x_column], self.df[y_column])
        ax.set_title(title)
        ax.set_xlabel(x_column)
        ax.set_ylabel(y_column)
        plt.tight_layout()
        
        # Save plot
        if save_path is None:
            timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
            filename = f"line_chart_{title.replace(' ', '_')}_{timestamp}.png"
            save_path = os.path.join(self.output_dir, filename)
        
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return save_path
    
    def create_histogram(self, x_column: str, title: str = "Histogram",
                        save_path: str = None, interactive: bool = False) -> str:
        """
        Create a histogram using matplotlib
        
        Args:
            x_column: Column for histogram
            title: Title for the chart
            save_path: Custom save path. If None, auto-generates
            interactive: Ignored (kept for compatibility)
            
        Returns:
            Path to saved chart file
        """
        # Create plot
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.hist(self.df[x_column].dropna(), bins=20, alpha=0.7)
        ax.set_title(title)
        ax.set_xlabel(x_column)
        ax.set_ylabel('Frequency')
        plt.tight_layout()
        
        # Save plot
        if save_path is None:
            timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
            filename = f"histogram_{title.replace(' ', '_')}_{timestamp}.png"
            save_path = os.path.join(self.output_dir, filename)
        
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return save_path
    
    def get_suggested_charts(self, max_suggestions: int = 5) -> List[Dict[str, Any]]:
        """
        Get suggested chart types based on data
        
        Args:
            max_suggestions: Maximum number of suggestions to return
            
        Returns:
            List of chart suggestions
        """
        suggestions = []
        
        # Get numeric and categorical columns
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = self.df.select_dtypes(include=['object', 'category']).columns.tolist()
        
        # Suggest charts based on column types
        if categorical_cols:
            for col in categorical_cols[:2]:  # Limit to avoid too many suggestions
                suggestions.append({
                    'type': 'bar_chart',
                    'x_column': col,
                    'y_column': None,
                    'title': f'Distribution of {col}',
                    'description': f'Bar chart showing counts of {col} values'
                })
                
                suggestions.append({
                    'type': 'pie_chart', 
                    'category_column': col,
                    'value_column': None,
                    'title': f'{col} Distribution',
                    'description': f'Pie chart showing proportions of {col} values'
                })
        
        if len(numeric_cols) >= 2:
            suggestions.append({
                'type': 'scatter_plot',
                'x_column': numeric_cols[0],
                'y_column': numeric_cols[1],
                'title': f'{numeric_cols[1]} vs {numeric_cols[0]}',
                'description': f'Scatter plot of {numeric_cols[1]} against {numeric_cols[0]}'
            })
        
        return suggestions[:max_suggestions] 