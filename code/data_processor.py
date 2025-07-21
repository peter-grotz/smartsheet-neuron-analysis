import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Union
from datetime import datetime

class DataProcessor:
    """Class for processing and querying Smartsheet data"""
    
    def __init__(self, df: pd.DataFrame):
        """
        Initialize the data processor
        
        Args:
            df: pandas DataFrame containing the sheet data
        """
        self.df = df.copy()
        self.original_df = df.copy()
    
    def apply_filters(self, filters: Dict[str, Any]) -> pd.DataFrame:
        """
        Apply filters to the DataFrame
        
        Args:
            filters: Dictionary of column names and filter values
                    Examples:
                    - {"Status": "Complete"}
                    - {"Priority": ["High", "Medium"]}
                    - {"Budget": {"min": 1000, "max": 5000}}
                    - {"Date": {"after": "2023-01-01", "before": "2023-12-31"}}
        
        Returns:
            Filtered DataFrame
        """
        filtered_df = self.df.copy()
        
        for column, condition in filters.items():
            if column not in filtered_df.columns:
                print(f"Warning: Column '{column}' not found in data")
                continue
            
            if isinstance(condition, (str, int, float)):
                # Simple equality filter
                filtered_df = filtered_df[filtered_df[column] == condition]
            
            elif isinstance(condition, list):
                # Multiple values filter (OR condition)
                filtered_df = filtered_df[filtered_df[column].isin(condition)]
            
            elif isinstance(condition, dict):
                # Complex filter conditions
                if 'min' in condition:
                    filtered_df = filtered_df[pd.to_numeric(filtered_df[column], errors='coerce') >= condition['min']]
                if 'max' in condition:
                    filtered_df = filtered_df[pd.to_numeric(filtered_df[column], errors='coerce') <= condition['max']]
                if 'after' in condition:
                    date_col = pd.to_datetime(filtered_df[column], errors='coerce')
                    after_date = pd.to_datetime(condition['after'])
                    filtered_df = filtered_df[date_col >= after_date]
                if 'before' in condition:
                    date_col = pd.to_datetime(filtered_df[column], errors='coerce')
                    before_date = pd.to_datetime(condition['before'])
                    filtered_df = filtered_df[date_col <= before_date]
                if 'contains' in condition:
                    filtered_df = filtered_df[filtered_df[column].astype(str).str.contains(condition['contains'], na=False, case=False)]
        
        return filtered_df
    
    def group_by_column(self, column: str, agg_func: str = 'count', value_column: Optional[str] = None) -> pd.DataFrame:
        """
        Group data by a column and apply aggregation
        
        Args:
            column: Column to group by
            agg_func: Aggregation function ('count', 'sum', 'mean', 'median', 'std')
            value_column: Column to aggregate (required for sum, mean, etc.)
        
        Returns:
            Grouped DataFrame
        """
        if column not in self.df.columns:
            raise ValueError(f"Column '{column}' not found in data")
        
        if agg_func == 'count':
            return self.df.groupby(column).size().reset_index(name='count')
        
        if not value_column:
            raise ValueError(f"value_column is required for aggregation function '{agg_func}'")
        
        if value_column not in self.df.columns:
            raise ValueError(f"Value column '{value_column}' not found in data")
        
        # Convert to numeric for aggregation
        numeric_data = pd.to_numeric(self.df[value_column], errors='coerce')
        temp_df = self.df.copy()
        temp_df[value_column] = numeric_data
        
        if agg_func == 'sum':
            return temp_df.groupby(column)[value_column].sum().reset_index()
        elif agg_func == 'mean':
            return temp_df.groupby(column)[value_column].mean().reset_index()
        elif agg_func == 'median':
            return temp_df.groupby(column)[value_column].median().reset_index()
        elif agg_func == 'std':
            return temp_df.groupby(column)[value_column].std().reset_index()
        else:
            raise ValueError(f"Unsupported aggregation function: {agg_func}")
    
    def get_numeric_columns(self) -> List[str]:
        """Get list of numeric columns in the DataFrame"""
        numeric_columns = []
        for col in self.df.columns:
            if pd.to_numeric(self.df[col], errors='coerce').notna().any():
                numeric_columns.append(col)
        return numeric_columns
    
    def get_categorical_columns(self) -> List[str]:
        """Get list of categorical (text) columns in the DataFrame"""
        categorical_columns = []
        for col in self.df.columns:
            if self.df[col].dtype == 'object' or self.df[col].dtype.name == 'category':
                categorical_columns.append(col)
        return categorical_columns
    
    def get_date_columns(self) -> List[str]:
        """Get list of potential date columns in the DataFrame"""
        date_columns = []
        for col in self.df.columns:
            try:
                parsed_dates = pd.to_datetime(self.df[col], errors='coerce')
                if parsed_dates.notna().sum() > len(self.df) * 0.5:  # More than 50% are valid dates
                    date_columns.append(col)
            except:
                continue
        return date_columns
    
    def get_column_stats(self, column: str) -> Dict[str, Any]:
        """
        Get statistics for a specific column
        
        Args:
            column: Column name
        
        Returns:
            Dictionary with column statistics
        """
        if column not in self.df.columns:
            raise ValueError(f"Column '{column}' not found in data")
        
        col_data = self.df[column]
        stats = {
            'name': column,
            'type': str(col_data.dtype),
            'non_null_count': col_data.notna().sum(),
            'null_count': col_data.isna().sum(),
            'unique_count': col_data.nunique()
        }
        
        # Try to get numeric statistics
        try:
            numeric_data = pd.to_numeric(col_data, errors='coerce')
            if numeric_data.notna().any():
                stats.update({
                    'mean': float(numeric_data.mean()),
                    'median': float(numeric_data.median()),
                    'std': float(numeric_data.std()),
                    'min': float(numeric_data.min()),
                    'max': float(numeric_data.max())
                })
        except:
            pass
        
        # Get top values
        top_values = col_data.value_counts().head(10).to_dict()
        stats['top_values'] = top_values
        
        return stats
    
    def search_data(self, search_term: str, columns: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Search for data containing a specific term
        
        Args:
            search_term: Term to search for
            columns: List of columns to search in. If None, searches all text columns.
        
        Returns:
            DataFrame with matching rows
        """
        if columns is None:
            columns = self.get_categorical_columns()
        
        # Create a mask for rows containing the search term
        mask = pd.Series([False] * len(self.df))
        
        for col in columns:
            if col in self.df.columns:
                col_mask = self.df[col].astype(str).str.contains(search_term, case=False, na=False)
                mask = mask | col_mask
        
        return self.df[mask]
    
    def reset_filters(self):
        """Reset DataFrame to original state"""
        self.df = self.original_df.copy()
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of the current DataFrame"""
        return {
            'total_rows': len(self.df),
            'total_columns': len(self.df.columns),
            'columns': list(self.df.columns),
            'numeric_columns': self.get_numeric_columns(),
            'categorical_columns': self.get_categorical_columns(),
            'date_columns': self.get_date_columns(),
            'memory_usage': self.df.memory_usage(deep=True).sum()
        } 