"""
Excel 解析器模块

功能：
1. 读取 Excel 文件
2. 提取关键数据和指标
3. 处理合并单元格和格式
"""

import pandas as pd
from typing import Dict, Any, List
from pathlib import Path
from .base_parser import BaseParser


class ExcelParser(BaseParser):
    """Excel 数据解析器"""
    
    def __init__(self, file_path: str):
        """
        初始化解析器
        
        Args:
            file_path: Excel 文件路径
        """
        super().__init__(file_path)
        self.workbook = None
        self.data = {}
        
    def parse(self) -> Dict[str, Any]:
        """
        解析 Excel 文件，返回标准化数据结构
        
        Returns:
            标准化数据字典
        """
        # 读取所有工作表
        self._load_sheets()
        
        # 获取第一个工作表
        first_sheet = list(self.data.keys())[0] if self.data else None
        df = self.data.get(first_sheet) if first_sheet else pd.DataFrame()
        
        # 提取指标
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
        """内部方法：加载所有工作表"""
        if not self.data:
            if not self.file_path.exists():
                raise FileNotFoundError(f"文件不存在: {self.file_path}")
            
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
        提取纯文本
        
        Returns:
            Excel 内容的字符串表示
        """
        self._load_sheets()
        text_parts = []
        for sheet_name, df in self.data.items():
            text_parts.append(f"=== {sheet_name} ===\n{df.to_string(index=False)}")
        return '\n\n'.join(text_parts)
    
    def extract_tables(self) -> List[pd.DataFrame]:
        """
        提取所有表格（每个工作表是一个表格）
        
        Returns:
            表格列表
        """
        self._load_sheets()
        return list(self.data.values())
    
    def parse_old(self) -> Dict[str, Any]:
        """
        解析 Excel 文件，提取结构化数据
        
        Returns:
            包含解析后数据的字典
        """
        if not self.file_path.exists():
            raise FileNotFoundError(f"文件不存在: {self.file_path}")
        
        # 读取所有工作表
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
        提取关键指标（针对金融报表场景）
        
        Args:
            sheet_name: 工作表名称，默认使用第一个表
            
        Returns:
            包含关键指标的字典
        """
        self._load_sheets()
        
        # 使用第一个工作表
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
        
        # 提取数值列的统计信息
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
        获取指定工作表的 DataFrame
        
        Args:
            sheet_name: 工作表名称
            
        Returns:
            pandas DataFrame
        """
        self._load_sheets()
        
        if sheet_name is None:
            sheet_name = list(self.data.keys())[0] if self.data else None
        
        return self.data.get(sheet_name, pd.DataFrame())


def main():
    """测试函数"""
    # 示例用法
    parser = ExcelParser('data/input/sample.xlsx')
    data = parser.parse()
    print(f"✅ 成功解析 {len(data)} 个工作表")
    
    metrics = parser.extract_metrics()
    print(f"\n📊 关键指标:")
    print(f"  - 行数: {metrics['row_count']}")
    print(f"  - 列数: {metrics['column_count']}")
    print(f"  - 列名: {metrics['columns']}")


if __name__ == '__main__':
    main()
