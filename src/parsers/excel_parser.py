"""
Excel Parser Module

Features:
1. Read Excel files
2. Extract key data and metrics
3. Handle merged cells and formatting
"""

import pandas as pd
from typing import Dict, Any, List
from pathlib import Path
from .base_parser import BaseParser


class ExcelParser(BaseParser):
    """Excel data parser"""
    
    def __init__(self, file_path: str):
        """
        Initialize parser
        
        Args:
            file_path: Path to Excel file
        """
        super().__init__(file_path)
        self.workbook = None
        self.data = {}
        
    def parse(self) -> Dict[str, Any]:
        """
        Parse Excel file and return standardized data structure
        
        Returns:
            Standardized data dictionary
        """
        # Load all sheets
        self._load_sheets()
        
        # Get first sheet
        first_sheet = list(self.data.keys())[0] if self.data else None
        df = self.data.get(first_sheet) if first_sheet else pd.DataFrame()
        
        # Extract metrics
        metrics = self.extract_metrics(first_sheet)
        
        return {
            'metadata': self.get_metadata(),
            'content': {
                'text': df.to_string(index=False) if not df.empty else "",
                'tables': list(self.data.values()),
                'structure': {
                    'sheet_names': list(self.data.keys()),
                    'sheet_count': len(self.data)
                 }
            },
            'metrics': {
                'sheet_count': len(self.data),
                'row_count': metrics.get('row_count', 0),
                'column_count': metrics.get('column_count', 0),
                'total_cells': metrics.get('row_count', 0) * metrics.get('column_count', 0)
            }
        }
    
    def _load_sheets(self):
        """Internal method: load all sheets"""
        if not self.data:
            if not self.file_path.exists():
                raise FileNotFoundError(f"File not found: {self.file_path}")
            
            excel_file = pd.ExcelFile(self.file_path)
            for sheet_name in excel_file.sheet_names:
                df = pd.read_excel(
                    self.file_path, 
                    sheet_name=sheet_name,
                    engine='openpyxl'
                )
                self.data[sheet_name] = df
    
    def extract_text(self) -> str:
        """
        Extract plain text
        
        Returns:
            String representation of Excel content
        """
        self._load_sheets()
        text_parts = []
        for sheet_name, df in self.data.items():
            text_parts.append(f"=== {sheet_name} ===\n{df.to_string(index=False)}")
        return '\n\n'.join(text_parts)
    
    def extract_tables(self) -> List[pd.DataFrame]:
        """
        Extract all tables (each sheet is a table)
        
        Returns:
            List of tables
        """
        self._load_sheets()
        return list(self.data.values())
    
    def parse_old(self) -> Dict[str, Any]:
        """
        Parse Excel file and extract structured data
        
        Returns:
            Dictionary containing parsed data
        """
        if not self.file_path.exists():
            raise FileNotFoundError(f"File not found: {self.file_path}")
        
        # Read all sheets
        excel_file = pd.ExcelFile(self.file_path)
        
        for sheet_name in excel_file.sheet_names:
            df = pd.read_excel(
                self.file_path, 
                sheet_name=sheet_name,
                engine='openpyxl'
            )
            self.data[sheet_name] = df
        
        return self.data
    
    def extract_metrics(self, sheet_name: str = None) -> Dict[str, Any]:
        """
        Extract key metrics (for financial report scenarios)
        
        Args:
            sheet_name: Sheet name, defaults to first sheet
            
        Returns:
            Dictionary containing key metrics
        """
        self._load_sheets()
        
        # Use first sheet
        if sheet_name is None:
            sheet_name = list(self.data.keys())[0] if self.data else None
        
        if not sheet_name or sheet_name not in self.data:
            return {}
        
        df = self.data[sheet_name]
        
        metrics = {
            'sheet_name': sheet_name,
            'row_count': len(df),
            'column_count': len(df.columns),
            'columns': df.columns.tolist(),
            'summary': {}
        }
        
        # Extract statistics for numeric columns
        numeric_cols = df.select_dtypes(include=['number']).columns
        for col in numeric_cols:
            metrics['summary'][col] = {
                'mean': df[col].mean(),
                'max': df[col].max(),
                'min': df[col].min(),
                'sum': df[col].sum()
            }
        
        return metrics
    
    def get_dataframe(self, sheet_name: str = None) -> pd.DataFrame:
        """
        Get DataFrame for specified sheet
        
        Args:
            sheet_name: Sheet name
            
        Returns:
            pandas DataFrame
        """
        self._load_sheets()
        
        if sheet_name is None:
            sheet_name = list(self.data.keys())[0] if self.data else None
        
        return self.data.get(sheet_name, pd.DataFrame())


def main():
    """Test function"""
    # Sample usage
    parser = ExcelParser('data/input/sample.xlsx')
    data = parser.parse()
    print(f"✅ Successfully parsed {len(data)} sheets")
    
    metrics = parser.extract_metrics()
    print(f"\n📊 Key metrics:")
    print(f"  - Rows: {metrics['row_count']}")
    print(f"  - Columns: {metrics['column_count']}")
    print(f"  - Column names: {metrics['columns']}")


if __name__ == '__main__':
    main()
