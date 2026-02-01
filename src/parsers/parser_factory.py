"""
Parser Factory

Automatically selects appropriate parser based on file type
"""

from pathlib import Path
from typing import Union
from .excel_parser import ExcelParser
from .csv_parser import CSVParser
from .word_parser import WordParser
from .pdf_parser import PDFParser
from .base_parser import BaseParser


class ParserFactory:
    """Parser factory class - automatically selects the appropriate parser"""
    
    # File extension to parser mapping
    PARSERS = {
        '.xlsx': ExcelParser,
        '.xls': ExcelParser,
        '.csv': CSVParser,
        '.docx': WordParser,
        '.doc': WordParser,
        '.pdf': PDFParser
    }
    
    @staticmethod
    def create_parser(file_path: str) -> BaseParser:
        """
        Automatically create parser based on file extension
        
        Args:
            file_path: File path
            
        Returns:
            Corresponding parser instance
            
        Raises:
            FileNotFoundError: File does not exist
            ValueError: Unsupported file format
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        ext = path.suffix.lower()
        
        parser_class = ParserFactory.PARSERS.get(ext)
        
        if parser_class is None:
            supported = ', '.join(ParserFactory.PARSERS.keys())
            raise ValueError(
                f"Unsupported file format: {ext}\n"
                f"Supported formats: {supported}"
            )
        
        print(f"  📄 Detected format: {ext} -> using {parser_class.__name__}")
        
        return parser_class(file_path)
    
    @staticmethod
    def get_supported_formats():
        """
        Get list of supported file formats
        
        Returns:
            List of supported extensions
        """
        return list(ParserFactory.PARSERS.keys())
    
    @staticmethod
    def is_supported(file_path: str) -> bool:
        """
        Check if file format is supported
        
        Args:
            file_path: File path
            
        Returns:
            Whether the format is supported
        """
        ext = Path(file_path).suffix.lower()
        return ext in ParserFactory.PARSERS


def main():
    """Test function"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python parser_factory.py <file_path>")
        print(f"\nSupported formats: {', '.join(ParserFactory.get_supported_formats())}")
        return
    
    file_path = sys.argv[1]
    
    try:
        # Automatically create parser
        parser = ParserFactory.create_parser(file_path)
        
        # Parse file
        data = parser.parse()
        
        # Display results
        print(f"\n✅ Parsing successful:")
        print(f"  - File: {data['metadata']['file_name']}")
        print(f"  - Format: {data['metadata']['file_format']}")
        print(f"  - Size: {data['metadata']['file_size_mb']} MB")
        
        metrics = data['metrics']
        for key, value in metrics.items():
            print(f"  - {key}: {value}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return 1


if __name__ == '__main__':
    main()
