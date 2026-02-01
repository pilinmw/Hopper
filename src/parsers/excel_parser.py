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


class ExcelParser:
    """Excel 数据解析器"""
    
    def __init__(self, file_path: str):
        """
        初始化解析器
        
        Args:
            file_path: Excel 文件路径
        """
        self.file_path = Path(file_path)
        self.workbook = None
        self.data = {}
        
    def parse(self) -> Dict[str, Any]:
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
        if not self.data:
            self.parse()
        
        # 使用第一个工作表
        if sheet_name is None:
            sheet_name = list(self.data.keys())[0]
        
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
        if not self.data:
            self.parse()
        
        if sheet_name is None:
            sheet_name = list(self.data.keys())[0]
        
        return self.data.get(sheet_name)


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
