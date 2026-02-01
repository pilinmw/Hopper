"""
CSV File Parser

Supports automatic encoding detection and standardized data output
"""

import pandas as pd
import chardet
from pathlib import Path
from typing import Dict, Any, List
from .base_parser import BaseParser


class CSVParser(BaseParser):
    """CSV file parser"""
    
    def __init__(self, file_path: str):
        """
        Initialize CSV parser
        
        Args:
            file_path: Path to CSV file
        """
        super().__init__(file_path)
        self.encoding = self._detect_encoding()
        self._df = None
    
    def _detect_encoding(self) -> str:
        """
        Auto-detect file encoding
        
        Returns:
            Encoding name (e.g. 'utf-8', 'gbk')
        """
        with open(self.file_path, 'rb') as f:
            # Read first 10000 bytes for detection
            raw_data = f.read(10000)
            result = chardet.detect(raw_data)
            detected_encoding = result['encoding']
            
            print(f"  🔍 Detected encoding: {detected_encoding} (confidence: {result['confidence']:.2%})")
            
            return detected_encoding or 'utf-8'
    
    def _load_dataframe(self) -> pd.DataFrame:
        """Load DataFrame (lazy loading)"""
        if self._df is None:
            try:
                self._df = pd.read_csv(
                    self.file_path,
                    encoding=self.encoding,
                    encoding_errors='replace'  # Replace undecodable characters
                )
            except Exception as e:
                # If failed, try UTF-8
                print(f"  ⚠️  Failed with {self.encoding}, trying UTF-8")
                self._df = pd.read_csv(
                    self.file_path,
                    encoding='utf-8',
                    encoding_errors='replace'
                )
        
        return self._df
    
    def parse(self) -> Dict[str, Any]:
        """
        Parse CSV file
        
        Returns:
            Standardized data structure
        """
        df = self._load_dataframe()
        
        return {
            'metadata': self.get_metadata(),
            'content': {
                'text': df.to_string(index=False),
                'tables': [df],
                'structure': {
                    'columns': df.columns.tolist(),
                    'rows': len(df),
                    'encoding': self.encoding
                }
            },
            'metrics': {
                'row_count': len(df),
                'column_count': len(df.columns),
                'data_types': {col: str(dtype) for col, dtype in df.dtypes.items()},
                'numeric_columns': len(df.select_dtypes(include=['number']).columns),
                'text_columns': len(df.select_dtypes(include=['object']).columns)
            }
        }
    
    def extract_text(self) -> str:
        """
        Extract plain text
        
        Returns:
            String representation of CSV content
        """
        df = self._load_dataframe()
        return df.to_string(index=False)
    
    def extract_tables(self) -> List[pd.DataFrame]:
        """
        Extract tables
        
        Returns:
            List containing a single DataFrame
        """
        df = self._load_dataframe()
        return [df]


def main():
    """Test function"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python csv_parser.py <csv_file_path>")
        return
    
    file_path = sys.argv[1]
    
    parser = CSVParser(file_path)
    data = parser.parse()
    
    print(f"\n✅ Parsing successful:")
    print(f"  - File: {data['metadata']['file_name']}")
    print(f"  - Size: {data['metadata']['file_size_mb']} MB")
    print(f"  - Rows: {data['metrics']['row_count']}")
    print(f"  - Columns: {data['metrics']['column_count']}")
    print(f"  - Encoding: {data['content']['structure']['encoding']}")


if __name__ == '__main__':
    main()
