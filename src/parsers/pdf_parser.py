"""
PDF 文档解析器

支持文本提取、表格识别
"""

import pdfplumber
import pandas as pd
from pathlib import Path
from typing import Dict, Any, List
from .base_parser import BaseParser


class PDFParser(BaseParser):
    """PDF 文档解析器"""
    
    def __init__(self, file_path: str):
        """
        初始化 PDF 解析器
        
        Args:
            file_path: PDF 文件路径
        """
        super().__init__(file_path)
        self.pdf = pdfplumber.open(str(self.file_path))
    
    def parse(self) -> Dict[str, Any]:
        """
        解析 PDF 文档
        
        Returns:
            标准化数据结构
        """
        text = self.extract_text()
        tables = self.extract_tables()
        
        metadata = self.get_metadata()
        # 添加 PDF 特有的元数据
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
        """
        提取所有页面的文本
        
        Returns:
            PDF 的纯文本内容
        """
        text_parts = []
        
        for page_num, page in enumerate(self.pdf.pages, 1):
            text = page.extract_text()
            if text:
                # 添加页码标记
                text_parts.append(f"=== 第 {page_num} 页 ===\n{text}")
        
        return '\n\n'.join(text_parts)
    
    def extract_tables(self) -> List[pd.DataFrame]:
        """
        提取所有表格
        
        Returns:
            表格列表（DataFrame 格式）
        """
        all_tables = []
        
        for page_num, page in enumerate(self.pdf.pages, 1):
            # 提取当前页的所有表格
            tables = page.extract_tables()
            
            for table_idx, table in enumerate(tables):
                if not table or len(table) < 2:
                    continue  # 跳过空表格或只有一行的表格
                
                try:
                    # 清理表格数据（去除 None 和空白）
                    cleaned_table = []
                    for row in table:
                        cleaned_row = [
                            (cell or '').strip() for cell in row
                        ]
                        cleaned_table.append(cleaned_row)
                    
                    # 第一行作为表头
                    headers = cleaned_table[0]
                    rows = cleaned_table[1:]
                    
                    # 过滤空行
                    rows = [row for row in rows if any(cell for cell in row)]
                    
                    if not rows:
                        continue
                    
                    # 创建 DataFrame
                    df = pd.DataFrame(rows, columns=headers)
                    
                    # 添加来源信息
                    df.attrs['page_number'] = page_num
                    df.attrs['table_index'] = table_idx
                    df.attrs['source'] = 'pdf_document'
                    
                    all_tables.append(df)
                    
                except Exception as e:
                    print(f"  ⚠️  第 {page_num} 页表格 {table_idx + 1} 解析失败: {e}")
                    continue
        
        return all_tables
    
    def extract_page_text(self, page_num: int) -> str:
        """
        提取指定页面的文本
        
        Args:
            page_num: 页码（从 1 开始）
            
        Returns:
            该页的文本内容
        """
        if 1 <= page_num <= len(self.pdf.pages):
            page = self.pdf.pages[page_num - 1]
            return page.extract_text() or ""
        return ""
    
    def __del__(self):
        """析构函数：关闭 PDF 文件"""
        if hasattr(self, 'pdf'):
            try:
                self.pdf.close()
            except:
                pass


def main():
    """测试函数"""
    import sys
    
    if len(sys.argv) < 2:
        print("用法: python pdf_parser.py <pdf文件路径>")
        return
    
    file_path = sys.argv[1]
    
    parser = PDFParser(file_path)
    data = parser.parse()
    
    print(f"\n✅ 解析成功:")
    print(f"  - 文件: {data['metadata']['file_name']}")
    print(f"  - 大小: {data['metadata']['file_size_mb']} MB")
    print(f"  - 页数: {data['metrics']['page_count']}")
    print(f"  - 表格数: {data['metrics']['table_count']}")
    print(f"  - 字数: {data['metrics']['word_count']}")
    
    # 显示前 500 字符
    text = data['content']['text']
    if len(text) > 500:
        print(f"\n📝 内容预览:\n{text[:500]}...")
    else:
        print(f"\n📝 内容:\n{text}")


if __name__ == '__main__':
    main()
