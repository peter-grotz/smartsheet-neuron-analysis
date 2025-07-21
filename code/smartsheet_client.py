"""
Smartsheet API Client Module

Provides a clean interface for interacting with the Smartsheet API
with proper error handling and logging.
"""

import smartsheet
import pandas as pd
from typing import Optional, Dict, List, Any, Union
from config import Config, ConfigError

class SmartsheetError(Exception):
    """Custom exception for Smartsheet-related errors"""
    pass

class SmartsheetClient:
    """Client for interacting with the Smartsheet API"""
    
    def __init__(self, access_token: Optional[str] = None):
        """
        Initialize the Smartsheet client
        
        Args:
            access_token: Smartsheet API access token. If None, uses config default.
            
        Raises:
            SmartsheetError: If access token is missing or invalid
        """
        self.access_token = access_token or Config.SMARTSHEET_ACCESS_TOKEN
        if not self.access_token:
            raise SmartsheetError("Access token is required")
        
        self.logger = Config.get_logger(__name__)
        
        try:
            self.smartsheet_client = smartsheet.Smartsheet(self.access_token)
            self.smartsheet_client.errors_as_exceptions(True)
            self.current_sheet = None
            self.current_sheet_data = None
            self.logger.info("Smartsheet client initialized successfully")
        except Exception as e:
            raise SmartsheetError(f"Failed to initialize Smartsheet client: {e}")
    
    def get_sheet_by_id(self, sheet_id: Union[str, int]) -> Dict[str, Any]:
        """
        Get a sheet by its ID
        
        Args:
            sheet_id: The ID of the sheet to retrieve
            
        Returns:
            Sheet data as a dictionary
            
        Raises:
            SmartsheetError: If sheet retrieval fails
        """
        try:
            self.logger.info(f"Retrieving sheet with ID: {sheet_id}")
            sheet = self.smartsheet_client.Sheets.get_sheet(sheet_id)
            self.current_sheet = sheet
            self.logger.info(f"Successfully retrieved sheet: {sheet.name}")
            return sheet
        except Exception as e:
            error_msg = f"Failed to retrieve sheet {sheet_id}: {str(e)}"
            self.logger.error(error_msg)
            raise SmartsheetError(error_msg)
    
    def get_sheet_by_name(self, sheet_name: str) -> Dict[str, Any]:
        """
        Get a sheet by its name
        
        Args:
            sheet_name: The name of the sheet to retrieve
            
        Returns:
            Sheet data as a dictionary
            
        Raises:
            SmartsheetError: If sheet is not found or retrieval fails
        """
        try:
            self.logger.info(f"Searching for sheet: {sheet_name}")
            sheets = self.list_sheets()
            
            for sheet in sheets:
                if sheet['name'] == sheet_name:
                    self.logger.info(f"Found sheet '{sheet_name}' with ID: {sheet['id']}")
                    return self.get_sheet_by_id(sheet['id'])
            
            available_names = [sheet['name'] for sheet in sheets[:10]]  # Show first 10 for reference
            error_msg = f"Sheet '{sheet_name}' not found. Available sheets: {available_names}"
            self.logger.error(error_msg)
            raise SmartsheetError(error_msg)
            
        except SmartsheetError:
            raise  # Re-raise our custom exceptions
        except Exception as e:
            error_msg = f"Failed to find sheet '{sheet_name}': {str(e)}"
            self.logger.error(error_msg)
            raise SmartsheetError(error_msg)
    
    def to_dataframe(self, sheet: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
        """
        Convert sheet data to pandas DataFrame
        
        Args:
            sheet: Sheet data. If None, uses current_sheet
            
        Returns:
            DataFrame containing the sheet data
            
        Raises:
            SmartsheetError: If conversion fails or no sheet is available
        """
        if sheet is None:
            sheet = self.current_sheet
            
        if sheet is None:
            raise SmartsheetError("No sheet data available. Load a sheet first.")
        
        try:
            self.logger.info(f"Converting sheet '{sheet.name}' to DataFrame")
            
            # Extract column information
            columns = []
            for column in sheet.columns:
                columns.append({
                    'id': column.id,
                    'title': column.title,
                    'type': column.type,
                    'index': column.index
                })
            
            # Sort columns by index to maintain order
            columns.sort(key=lambda x: x['index'])
            column_map = {col['id']: col['title'] for col in columns}
            
            # Extract row data
            rows_data = []
            for row in sheet.rows:
                row_data = {}
                for cell in row.cells:
                    column_title = column_map.get(cell.column_id, f"Column_{cell.column_id}")
                    
                    # Handle different cell value types
                    if hasattr(cell, 'display_value') and cell.display_value is not None:
                        row_data[column_title] = cell.display_value
                    elif hasattr(cell, 'value') and cell.value is not None:
                        row_data[column_title] = cell.value
                    else:
                        row_data[column_title] = None
                
                rows_data.append(row_data)
            
            # Create DataFrame
            df = pd.DataFrame(rows_data)
            
            # Ensure all columns are present (in case some rows are missing certain columns)
            for col_title in [col['title'] for col in columns]:
                if col_title not in df.columns:
                    df[col_title] = None
            
            # Reorder columns to match original sheet order
            column_order = [col['title'] for col in columns]
            df = df.reindex(columns=column_order)
            
            self.logger.info(f"Successfully converted sheet to DataFrame: {len(df)} rows × {len(df.columns)} columns")
            return df
            
        except Exception as e:
            error_msg = f"Failed to convert sheet to DataFrame: {str(e)}"
            self.logger.error(error_msg)
            raise SmartsheetError(error_msg)
    
    def get_sheet_info(self, sheet: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Get basic information about a sheet
        
        Args:
            sheet: Sheet data. If None, uses current_sheet
            
        Returns:
            Dictionary with sheet information
        """
        if sheet is None:
            sheet = self.current_sheet
            
        if sheet is None:
            raise SmartsheetError("No sheet data available")
        
        return {
            'id': sheet.id,
            'name': sheet.name,
            'total_rows': len(sheet.rows) if hasattr(sheet, 'rows') else 0,
            'column_count': len(sheet.columns) if hasattr(sheet, 'columns') else 0,
            'columns': [col.title for col in sheet.columns] if hasattr(sheet, 'columns') else [],
            'permalink': getattr(sheet, 'permalink', None),
            'created_at': getattr(sheet, 'created_at', None),
            'modified_at': getattr(sheet, 'modified_at', None)
        }
    
    def list_sheets(self) -> List[Dict[str, Any]]:
        """
        List all available sheets
        
        Returns:
            List of dictionaries containing sheet information
            
        Raises:
            SmartsheetError: If listing sheets fails
        """
        try:
            self.logger.info("Retrieving list of available sheets")
            response = self.smartsheet_client.Sheets.list_sheets(include_all=True)
            
            sheets = []
            for sheet in response.data:
                sheets.append({
                    'id': sheet.id,
                    'name': sheet.name,
                    'permalink': getattr(sheet, 'permalink', None),
                    'created_at': getattr(sheet, 'created_at', None),
                    'modified_at': getattr(sheet, 'modified_at', None)
                })
            
            self.logger.info(f"Found {len(sheets)} available sheets")
            return sheets
            
        except Exception as e:
            error_msg = f"Failed to list sheets: {str(e)}"
            self.logger.error(error_msg)
            raise SmartsheetError(error_msg)
    
    def search_sheets(self, query: str) -> List[Dict[str, Any]]:
        """
        Search for sheets by name
        
        Args:
            query: Search query string
            
        Returns:
            List of matching sheets
            
        Raises:
            SmartsheetError: If search fails
        """
        try:
            self.logger.info(f"Searching for sheets matching: {query}")
            response = self.smartsheet_client.Search.search(query)
            
            sheets = []
            if hasattr(response, 'results'):
                for result in response.results:
                    if hasattr(result, 'object_type') and result.object_type == 'sheet':
                        sheets.append({
                            'id': result.object_id,
                            'name': getattr(result, 'text', 'Unknown'),
                            'context_data': getattr(result, 'context_data', [])
                        })
            
            self.logger.info(f"Search found {len(sheets)} matching sheets")
            return sheets
            
        except Exception as e:
            error_msg = f"Failed to search sheets: {str(e)}"
            self.logger.error(error_msg)
            raise SmartsheetError(error_msg)
    
    def validate_connection(self) -> bool:
        """
        Validate the Smartsheet connection by attempting to list sheets
        
        Returns:
            True if connection is valid, False otherwise
        """
        try:
            self.list_sheets()
            self.logger.info("Smartsheet connection validated successfully")
            return True
        except Exception as e:
            self.logger.error(f"Smartsheet connection validation failed: {e}")
            return False 