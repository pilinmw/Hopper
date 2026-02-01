"""
PDF Document Parser

Supports text extraction and table recognition
"""

import pdfplumber
import pandas as pd
from pathlib import Path
from typing import Dict, Any, List
from .base_parser import BaseParser


class PDFParser(BaseParser):
    """PDF document parser"""
    
    def __init__(self, file_path: str):
        super().__init__(file_path)
        self.pdf = pdfplumber.open(str(self.file_path))
    
    def parse(self) -> Dict[str, Any]:
        text = self.extract_text()
        tables = self.extract_tables()
        
        metadata = self.get_metadata()
        metadata['pdf_metadata'] = self.pdf.metadata or {}
        metadata['page_count'] = len(self.pdf.pages)
        
        return {
            'metadata': metadata,
            'content': {
                'text': text,
                'tables': tables,
                'structure': {
                    'pages': len(self.pdf.pages)
                }
            },
            'metrics': {
                'page_count': len(self.pdf.pages),
                'word_count': len(text.split()),
                'character_count': len(text),
                'table_count': len(tables),
                'line_count': text.count('\n') + 1
            }
        }
    
    def extract_text(self) -> str:
        text_parts = []
        for page_num, page in enumerate(self.pdf.pages, 1):
            text = page.extract_text()
            if text:
                text_parts.append(f"=== Page {page_num} ===\n{text}")
        return '\n\n'.join(text_parts)
    
    def extract_tables(self) -> List[pd.DataFrame]:
        all_tables = []
        for page_num, page in enumerate(self.pdf.pages, 1):
            tables = page.extract_tables()
            for table_idx, table in enumerate(tables):
                if not table or len(table) < 2:
                    continue
                try:
                    cleaned_table = [[( cell or '').strip() for cell in row] for row in table]
                    headers = cleaned_table[0]
                    rows = [row for row in cleaned_table[1:] if any(cell for cell in row)]
                    if not rows:
                        continue
                    df = pd.DataFrame(rows, columns=headers)
                    df.attrs['page_number'] = page_num
                    df.attrs['table_index'] = table_idx
                    df.attrs['source'] = 'pdf_document'
                    all_tables.append(df)
                except Exception as e:
                    print(f"  ⚠️  Page {page_num} table {table_idx + 1} parsing failed: {e}")
        return all_tables
    
    def extract_page_text(self, page_num: int) -> str:
        if 1 <= page_num <= len(self.pdf.pages):
            return self.pdf.pages[page_num - 1].extract_text() or ""
        return ""
    
    def __del__(self):
        if hasattr(self, 'pdf'):
            try:
                self.pdf.close()
            except:
                pass



def main():
    import sys
    if len(sys.argv) < 2:
        print("Usage: python pdf_parser.py <pdf_file_path>")
        return
    parser = PDFParser(sys.argv[1])
    data = parser.parse()
    print(f"\n✅ Parsing successful:")
    print(f"  - File: {data['metadata']['file_name']}")
    print(f"  - Size: {data['metadata']['file_size_mb']} MB")
    print(f"  - Pages: {data['metrics']['page_count']}")
    print(f"  - Tables: {data['metrics']['table_count']}")
    print(f"  - Words: {data['metrics']['word_count']}")


if __name__ == '__main__':
    main()
