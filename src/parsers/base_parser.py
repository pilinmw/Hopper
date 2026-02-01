"""
Base Parser

Defines unified interface for all document parsers
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any, List
import pandas as pd
from datetime import datetime


class BaseParser(ABC):
    """Abstract base class for document parsers"""
    
    def __init__(self, file_path: str):
        """
        Initialize parser
        
        Args:
            file_path: Path to the file
        """
        self.file_path = Path(file_path)
        
        if not self.file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
    
    @abstractmethod
    def parse(self) -> Dict[str, Any]:
        """
        Parse document and return standardized data structure
        
        Returns:
            {
                'metadata': {...},     # File metadata
                'content': {...},      # Content (text, tables, etc.)
                'metrics': {...}       # Statistical metrics
            }
        """
        pass
    
    @abstractmethod
    def extract_text(self) -> str:
        """
        Extract plain text content
        
        Returns:
            Plain text content of the document
        """
        pass
    
    @abstractmethod
    def extract_tables(self) -> List[pd.DataFrame]:
        """
        Extract all tables
        
        Returns:
            List of tables (DataFrame format)
        """
        pass
    
    def get_metadata(self) -> Dict[str, Any]:
        """
        Get file metadata
        
        Returns:
            Dictionary containing file information
        """
        stat = self.file_path.stat()
        
        return {
            'file_name': self.file_path.name,
            'file_path': str(self.file_path.absolute()),
            'file_format': self.get_format(),
            'file_size': stat.st_size,
            'file_size_mb': round(stat.st_size / (1024 * 1024), 2),
            'modified_at': datetime.fromtimestamp(stat.st_mtime).isoformat(),
            'parsed_at': datetime.now().isoformat()
        }
    
    def get_format(self) -> str:
        """
        Get file format
        
        Returns:
            File format name
        """
        ext_to_format = {
            '.xlsx': 'excel',
            '.xls': 'excel',
            '.csv': 'csv',
            '.docx': 'word',
            '.doc': 'word',
            '.pdf': 'pdf'
        }
        
        ext = self.file_path.suffix.lower()
        return ext_to_format.get(ext, 'unknown')
