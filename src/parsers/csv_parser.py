"""
CSV 文件解析器

支持自动编码检测和标准化数据输出
"""

import pandas as pd
import chardet
from pathlib import Path
from typing import Dict, Any, List
from .base_parser import BaseParser


class CSVParser(BaseParser):
    """CSV 文件解析器"""
    
    def __init__(self, file_path: str):
        """
        初始化 CSV 解析器
        
        Args:
            file_path: CSV 文件路径
        """
        super().__init__(file_path)
        self.encoding = self._detect_encoding()
        self._df = None
    
    def _detect_encoding(self) -> str:
        """
        自动检测文件编码
        
        Returns:
            编码名称（如 'utf-8', 'gbk'）
        """
        with open(self.file_path, 'rb') as f:
            # 读取前 10000 字节用于检测
            raw_data = f.read(10000)
            result = chardet.detect(raw_data)
            detected_encoding = result['encoding']
            
            print(f"  🔍 检测到编码: {detected_encoding} (置信度: {result['confidence']:.2%})")
            
            return detected_encoding or 'utf-8'
    
    def _load_dataframe(self) -> pd.DataFrame:
        """加载 DataFrame（懒加载）"""
        if self._df is None:
            try:
                self._df = pd.read_csv(
                    self.file_path,
                    encoding=self.encoding,
                    encoding_errors='replace'  # 遇到无法解码的字符时替换
                )
            except Exception as e:
                # 如果失败，尝试使用 UTF-8
                print(f"  ⚠️  使用 {self.encoding} 失败，尝试 UTF-8")
                self._df = pd.read_csv(
                    self.file_path,
                    encoding='utf-8',
                    encoding_errors='replace'
                )
        
        return self._df
    
    def parse(self) -> Dict[str, Any]:
        """
        解析 CSV 文件
        
        Returns:
            标准化数据结构
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
        提取纯文本
        
        Returns:
            CSV 内容的字符串表示
        """
        df = self._load_dataframe()
        return df.to_string(index=False)
    
    def extract_tables(self) -> List[pd.DataFrame]:
        """
        提取表格
        
        Returns:
            包含一个 DataFrame 的列表
        """
        df = self._load_dataframe()
        return [df]


def main():
    """测试函数"""
    import sys
    
    if len(sys.argv) < 2:
        print("用法: python csv_parser.py <csv文件路径>")
        return
    
    file_path = sys.argv[1]
    
    parser = CSVParser(file_path)
    data = parser.parse()
    
    print(f"\n✅ 解析成功:")
    print(f"  - 文件: {data['metadata']['file_name']}")
    print(f"  - 大小: {data['metadata']['file_size_mb']} MB")
    print(f"  - 行数: {data['metrics']['row_count']}")
    print(f"  - 列数: {data['metrics']['column_count']}")
    print(f"  - 编码: {data['content']['structure']['encoding']}")


if __name__ == '__main__':
    main()
