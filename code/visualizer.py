import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import plotly.offline as pyo
from plotly.subplots import make_subplots
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
import os
from config import Config

class Visualizer:
    """Class for creating visualizations from Smartsheet data"""
    
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
        self.figure_size = (Config.DEFAULT_CHART_WIDTH, Config.DEFAULT_CHART_HEIGHT)
        self.dpi = Config.DEFAULT_DPI
    
    def create_bar_chart(self, x_column: str, y_column: str, title: str = None, 
                        save_path: str = None, interactive: bool = False, 
                        color_column: str = None) -> Optional[str]:
        """
        Create a bar chart
        
        Args:
            x_column: Column for x-axis (categories)
            y_column: Column for y-axis (values)
            title: Chart title
            save_path: Path to save the chart
            interactive: Whether to create an interactive plotly chart
            color_column: Column to use for color coding
        
        Returns:
            Path to saved chart or None
        """
        if x_column not in self.df.columns or y_column not in self.df.columns:
            raise ValueError(f"Columns {x_column} or {y_column} not found in data")
        
        # Group data to handle duplicates
        grouped_df = self.df.groupby(x_column)[y_column].sum().reset_index()
        
        if interactive:
            fig = px.bar(
                grouped_df, 
                x=x_column, 
                y=y_column,
                title=title or f"{y_column} by {x_column}",
                color=color_column if color_column in self.df.columns else None
            )
            fig.update_layout(
                xaxis_title=x_column,
                yaxis_title=y_column,
                showlegend=True if color_column else False
            )
            
            if save_path:
                pyo.plot(fig, filename=save_path, auto_open=False)
                return save_path
            else:
                fig.show()
                return None
        else:
            plt.figure(figsize=self.figure_size, dpi=self.dpi)
            
            if color_column and color_column in self.df.columns:
                # Create grouped bar chart
                pivot_df = self.df.pivot_table(
                    index=x_column, 
                    columns=color_column, 
                    values=y_column, 
                    aggfunc='sum', 
                    fill_value=0
                )
                pivot_df.plot(kind='bar', ax=plt.gca())
            else:
                plt.bar(grouped_df[x_column], grouped_df[y_column])
            
            plt.title(title or f"{y_column} by {x_column}")
            plt.xlabel(x_column)
            plt.ylabel(y_column)
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            
            if save_path:
                plt.savefig(save_path, dpi=self.dpi, bbox_inches='tight')
                plt.close()
                return save_path
            else:
                plt.show()
                return None
    
    def create_line_chart(self, x_column: str, y_column: str, title: str = None,
                         save_path: str = None, interactive: bool = False,
                         group_column: str = None) -> Optional[str]:
        """
        Create a line chart
        
        Args:
            x_column: Column for x-axis
            y_column: Column for y-axis
            title: Chart title
            save_path: Path to save the chart
            interactive: Whether to create an interactive plotly chart
            group_column: Column to group lines by
        
        Returns:
            Path to saved chart or None
        """
        if x_column not in self.df.columns or y_column not in self.df.columns:
            raise ValueError(f"Columns {x_column} or {y_column} not found in data")
        
        if interactive:
            fig = px.line(
                self.df,
                x=x_column,
                y=y_column,
                title=title or f"{y_column} over {x_column}",
                color=group_column if group_column in self.df.columns else None
            )
            
            if save_path:
                pyo.plot(fig, filename=save_path, auto_open=False)
                return save_path
            else:
                fig.show()
                return None
        else:
            plt.figure(figsize=self.figure_size, dpi=self.dpi)
            
            if group_column and group_column in self.df.columns:
                for group in self.df[group_column].unique():
                    group_data = self.df[self.df[group_column] == group]
                    plt.plot(group_data[x_column], group_data[y_column], label=group, marker='o')
                plt.legend()
            else:
                plt.plot(self.df[x_column], self.df[y_column], marker='o')
            
            plt.title(title or f"{y_column} over {x_column}")
            plt.xlabel(x_column)
            plt.ylabel(y_column)
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            
            if save_path:
                plt.savefig(save_path, dpi=self.dpi, bbox_inches='tight')
                plt.close()
                return save_path
            else:
                plt.show()
                return None
    
    def create_pie_chart(self, category_column: str, value_column: str = None,
                        title: str = None, save_path: str = None,
                        interactive: bool = False) -> Optional[str]:
        """
        Create a pie chart
        
        Args:
            category_column: Column containing categories
            value_column: Column containing values (if None, uses count)
            title: Chart title
            save_path: Path to save the chart
            interactive: Whether to create an interactive plotly chart
        
        Returns:
            Path to saved chart or None
        """
        if category_column not in self.df.columns:
            raise ValueError(f"Column {category_column} not found in data")
        
        if value_column:
            if value_column not in self.df.columns:
                raise ValueError(f"Column {value_column} not found in data")
            pie_data = self.df.groupby(category_column)[value_column].sum()
        else:
            pie_data = self.df[category_column].value_counts()
        
        if interactive:
            fig = px.pie(
                values=pie_data.values,
                names=pie_data.index,
                title=title or f"Distribution of {category_column}"
            )
            
            if save_path:
                pyo.plot(fig, filename=save_path, auto_open=False)
                return save_path
            else:
                fig.show()
                return None
        else:
            plt.figure(figsize=self.figure_size, dpi=self.dpi)
            plt.pie(pie_data.values, labels=pie_data.index, autopct='%1.1f%%')
            plt.title(title or f"Distribution of {category_column}")
            
            if save_path:
                plt.savefig(save_path, dpi=self.dpi, bbox_inches='tight')
                plt.close()
                return save_path
            else:
                plt.show()
                return None
    
    def create_scatter_plot(self, x_column: str, y_column: str, title: str = None,
                           save_path: str = None, interactive: bool = False,
                           color_column: str = None, size_column: str = None) -> Optional[str]:
        """
        Create a scatter plot
        
        Args:
            x_column: Column for x-axis
            y_column: Column for y-axis
            title: Chart title
            save_path: Path to save the chart
            interactive: Whether to create an interactive plotly chart
            color_column: Column to use for color coding
            size_column: Column to use for point sizes
        
        Returns:
            Path to saved chart or None
        """
        if x_column not in self.df.columns or y_column not in self.df.columns:
            raise ValueError(f"Columns {x_column} or {y_column} not found in data")
        
        # Convert to numeric
        x_data = pd.to_numeric(self.df[x_column], errors='coerce')
        y_data = pd.to_numeric(self.df[y_column], errors='coerce')
        
        if interactive:
            fig = px.scatter(
                self.df,
                x=x_column,
                y=y_column,
                title=title or f"{y_column} vs {x_column}",
                color=color_column if color_column in self.df.columns else None,
                size=size_column if size_column in self.df.columns else None
            )
            
            if save_path:
                pyo.plot(fig, filename=save_path, auto_open=False)
                return save_path
            else:
                fig.show()
                return None
        else:
            plt.figure(figsize=self.figure_size, dpi=self.dpi)
            
            if color_column and color_column in self.df.columns:
                for category in self.df[color_column].unique():
                    mask = self.df[color_column] == category
                    plt.scatter(x_data[mask], y_data[mask], label=category, alpha=0.7)
                plt.legend()
            else:
                plt.scatter(x_data, y_data, alpha=0.7)
            
            plt.title(title or f"{y_column} vs {x_column}")
            plt.xlabel(x_column)
            plt.ylabel(y_column)
            plt.tight_layout()
            
            if save_path:
                plt.savefig(save_path, dpi=self.dpi, bbox_inches='tight')
                plt.close()
                return save_path
            else:
                plt.show()
                return None
    
    def create_histogram(self, column: str, bins: int = 20, title: str = None,
                        save_path: str = None, interactive: bool = False) -> Optional[str]:
        """
        Create a histogram
        
        Args:
            column: Column to create histogram for
            bins: Number of bins
            title: Chart title
            save_path: Path to save the chart
            interactive: Whether to create an interactive plotly chart
        
        Returns:
            Path to saved chart or None
        """
        if column not in self.df.columns:
            raise ValueError(f"Column {column} not found in data")
        
        # Convert to numeric
        data = pd.to_numeric(self.df[column], errors='coerce').dropna()
        
        if interactive:
            fig = px.histogram(
                x=data,
                nbins=bins,
                title=title or f"Distribution of {column}"
            )
            fig.update_xaxis(title=column)
            fig.update_yaxis(title="Frequency")
            
            if save_path:
                pyo.plot(fig, filename=save_path, auto_open=False)
                return save_path
            else:
                fig.show()
                return None
        else:
            plt.figure(figsize=self.figure_size, dpi=self.dpi)
            plt.hist(data, bins=bins, alpha=0.7, edgecolor='black')
            plt.title(title or f"Distribution of {column}")
            plt.xlabel(column)
            plt.ylabel("Frequency")
            plt.tight_layout()
            
            if save_path:
                plt.savefig(save_path, dpi=self.dpi, bbox_inches='tight')
                plt.close()
                return save_path
            else:
                plt.show()
                return None
    
    def create_box_plot(self, column: str, group_column: str = None, title: str = None,
                       save_path: str = None, interactive: bool = False) -> Optional[str]:
        """
        Create a box plot
        
        Args:
            column: Column to create box plot for
            group_column: Column to group by
            title: Chart title
            save_path: Path to save the chart
            interactive: Whether to create an interactive plotly chart
        
        Returns:
            Path to saved chart or None
        """
        if column not in self.df.columns:
            raise ValueError(f"Column {column} not found in data")
        
        if interactive:
            fig = px.box(
                self.df,
                y=column,
                x=group_column if group_column in self.df.columns else None,
                title=title or f"Box Plot of {column}"
            )
            
            if save_path:
                pyo.plot(fig, filename=save_path, auto_open=False)
                return save_path
            else:
                fig.show()
                return None
        else:
            plt.figure(figsize=self.figure_size, dpi=self.dpi)
            
            if group_column and group_column in self.df.columns:
                groups = self.df[group_column].unique()
                data_by_group = [pd.to_numeric(self.df[self.df[group_column] == group][column], errors='coerce').dropna() 
                               for group in groups]
                plt.boxplot(data_by_group, labels=groups)
            else:
                data = pd.to_numeric(self.df[column], errors='coerce').dropna()
                plt.boxplot(data)
            
            plt.title(title or f"Box Plot of {column}")
            if group_column:
                plt.xlabel(group_column)
            plt.ylabel(column)
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            
            if save_path:
                plt.savefig(save_path, dpi=self.dpi, bbox_inches='tight')
                plt.close()
                return save_path
            else:
                plt.show()
                return None
    
    def create_dashboard(self, charts_config: List[Dict[str, Any]], 
                        title: str = "Dashboard", save_path: str = None) -> Optional[str]:
        """
        Create a dashboard with multiple charts
        
        Args:
            charts_config: List of chart configurations
            title: Dashboard title
            save_path: Path to save the dashboard
        
        Returns:
            Path to saved dashboard or None
        """
        n_charts = len(charts_config)
        cols = 2
        rows = (n_charts + 1) // 2
        
        fig = make_subplots(
            rows=rows, 
            cols=cols,
            subplot_titles=[config.get('title', f'Chart {i+1}') for i, config in enumerate(charts_config)]
        )
        
        for i, config in enumerate(charts_config):
            row = (i // cols) + 1
            col = (i % cols) + 1
            
            chart_type = config.get('type', 'bar')
            x_col = config.get('x_column')
            y_col = config.get('y_column')
            
            if chart_type == 'bar':
                grouped_df = self.df.groupby(x_col)[y_col].sum().reset_index()
                trace = go.Bar(x=grouped_df[x_col], y=grouped_df[y_col], name=f"Chart {i+1}")
            elif chart_type == 'line':
                trace = go.Scatter(x=self.df[x_col], y=self.df[y_col], mode='lines+markers', name=f"Chart {i+1}")
            elif chart_type == 'scatter':
                trace = go.Scatter(x=self.df[x_col], y=self.df[y_col], mode='markers', name=f"Chart {i+1}")
            else:
                continue
            
            fig.add_trace(trace, row=row, col=col)
        
        fig.update_layout(
            title=title,
            showlegend=False,
            height=300 * rows
        )
        
        if save_path:
            pyo.plot(fig, filename=save_path, auto_open=False)
            return save_path
        else:
            fig.show()
            return None
    
    def get_suggested_charts(self, numeric_columns: List[str], 
                            categorical_columns: List[str]) -> List[Dict[str, Any]]:
        """
        Get suggested chart configurations based on column types
        
        Args:
            numeric_columns: List of numeric columns
            categorical_columns: List of categorical columns
        
        Returns:
            List of suggested chart configurations
        """
        suggestions = []
        
        # Bar charts: categorical x numeric
        for cat_col in categorical_columns[:3]:  # Limit to first 3
            for num_col in numeric_columns[:2]:  # Limit to first 2
                suggestions.append({
                    'type': 'bar',
                    'x_column': cat_col,
                    'y_column': num_col,
                    'title': f'{num_col} by {cat_col}',
                    'description': f'Bar chart showing {num_col} grouped by {cat_col}'
                })
        
        # Scatter plots: numeric x numeric
        if len(numeric_columns) >= 2:
            for i in range(min(2, len(numeric_columns)-1)):
                suggestions.append({
                    'type': 'scatter',
                    'x_column': numeric_columns[i],
                    'y_column': numeric_columns[i+1],
                    'title': f'{numeric_columns[i+1]} vs {numeric_columns[i]}',
                    'description': f'Scatter plot of {numeric_columns[i+1]} against {numeric_columns[i]}'
                })
        
        # Pie charts: categorical columns
        for cat_col in categorical_columns[:2]:  # Limit to first 2
            suggestions.append({
                'type': 'pie',
                'category_column': cat_col,
                'title': f'Distribution of {cat_col}',
                'description': f'Pie chart showing distribution of {cat_col}'
            })
        
        # Histograms: numeric columns
        for num_col in numeric_columns[:2]:  # Limit to first 2
            suggestions.append({
                'type': 'histogram',
                'column': num_col,
                'title': f'Distribution of {num_col}',
                'description': f'Histogram showing distribution of {num_col}'
            })
        
        return suggestions 