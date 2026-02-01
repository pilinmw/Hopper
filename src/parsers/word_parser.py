"""
Word Document Parser

Supports text and table extraction with paragraph structure analysis
"""

from docx import Document
import pandas as pd
from pathlib import Path
from typing import Dict, Any, List
from .base_parser import BaseParser


class WordParser(BaseParser):
    """Word document parser"""
    
    def __init__(self, file_path: str):
        """
        Initialize Word parser
        
        Args:
            file_path: Path to Word file
        """
        super().__init__(file_path)
        self.doc = Document(str(self.file_path))
    
    def parse(self) -> Dict[str, Any]:
        """
        Parse Word document
        
        Returns:
            Standardized data structure
        """
        text = self.extract_text()
        tables = self.extract_tables()
        
        return {
            'metadata': self.get_metadata(),
            'content': {
                'text': text,
                'tables': tables,
                'structure': {
                    'paragraphs': len(self.doc.paragraphs),
                    'tables': len(self.doc.tables),
                    'sections': len(self.doc.sections)
                }
            },
            'metrics': {
                'word_count': len(text.split()),
                'character_count': len(text),
                'paragraph_count': len(self.doc.paragraphs),
                'table_count': len(self.doc.tables),
                'line_count': text.count('\n') + 1
            }
        }
    
    def extract_text(self) -> str:
        """
        Extract all text content
        
        Returns:
            Plain text from document
        """
        paragraphs = []
        
        for para in self.doc.paragraphs:
            text = para.text.strip()
            if text:  # Ignore empty paragraphs
                paragraphs.append(text)
        
        return '\n'.join(paragraphs)
    
    def extract_tables(self) -> List[pd.DataFrame]:
        """
        Extract all tables
        
        Returns:
            List of tables (DataFrame format)
        """
        tables = []
        
        for table_idx, table in enumerate(self.doc.tables):
            # Extract table data
            data = []
            for row in table.rows:
                row_data = [cell.text.strip() for cell in row.cells]
                data.append(row_data)
            
            if not data or len(data) < 2:
                continue  # Skip empty tables or single-row tables
            
            try:
                # First row as header
                headers = data[0]
                rows = data[1:]
                
                # Create DataFrame
                df = pd.DataFrame(rows, columns=headers)
                
                # Add table index information
                df.attrs['table_index'] = table_idx
                df.attrs['source'] = 'word_document'
                
                tables.append(df)
                
            except Exception as e:
                print(f"  ⚠️  Table {table_idx + 1} parsing failed: {e}")
                continue
        
        return tables
    
    def extract_headings(self) -> List[Dict[str, Any]]:
        """
        Extract heading structure
        
        Returns:
            List of headings with level and content
        """
        headings = []
        
        for para in self.doc.paragraphs:
            if para.style.name.startswith('Heading'):
                level = int(para.style.name.replace('Heading ', ''))
                headings.append({
                    'level': level,
                    'text': para.text.strip()
                })
        
        return headings


def main():
    """Test function"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python word_parser.py <docx_file_path>")
        return
    
    file_path = sys.argv[1]
    
    parser = WordParser(file_path)
    data = parser.parse()
    
    print(f"\n✅ Parsing successful:")
    print(f"  - File: {data['metadata']['file_name']}")
    print(f"  - Size: {data['metadata']['file_size_mb']} MB")
    print(f"  - Paragraphs: {data['metrics']['paragraph_count']}")
    print(f"  - Tables: {data['metrics']['table_count']}")
    print(f"  - Words: {data['metrics']['word_count']}")
    
    # Show first 500 characters
    text = data['content']['text']
    if len(text) > 500:
        print(f"\n📝 Content preview:\n{text[:500]}...")
    else:
        print(f"\n📝 Content:\n{text}")


if __name__ == '__main__':
    main()
