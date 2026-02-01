"""
解析器工厂类

根据文件类型自动选择合适的解析器
"""

from pathlib import Path
from typing import Union
from .excel_parser import ExcelParser
from .csv_parser import CSVParser
from .word_parser import WordParser
from .pdf_parser import PDFParser
from .base_parser import BaseParser


class ParserFactory:
    """解析器工厂类 - 自动选择合适的解析器"""
    
    # 文件扩展名到解析器的映射
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
        根据文件扩展名自动创建解析器
        
        Args:
            file_path: 文件路径
            
        Returns:
            对应的解析器实例
            
        Raises:
            FileNotFoundError: 文件不存在
            ValueError: 不支持的文件格式
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        ext = path.suffix.lower()
        
        parser_class = ParserFactory.PARSERS.get(ext)
        
        if parser_class is None:
            supported = ', '.join(ParserFactory.PARSERS.keys())
            raise ValueError(
                f"不支持的文件格式: {ext}\n"
                f"支持的格式: {supported}"
            )
        
        print(f"  📄 检测到格式: {ext} -> 使用 {parser_class.__name__}")
        
        return parser_class(file_path)
    
    @staticmethod
    def get_supported_formats():
        """
        获取支持的文件格式列表
        
        Returns:
            支持的扩展名列表
        """
        return list(ParserFactory.PARSERS.keys())
    
    @staticmethod
    def is_supported(file_path: str) -> bool:
        """
        检查文件格式是否支持
        
        Args:
            file_path: 文件路径
            
        Returns:
            是否支持该格式
        """
        ext = Path(file_path).suffix.lower()
        return ext in ParserFactory.PARSERS


def main():
    """测试函数"""
    import sys
    
    if len(sys.argv) < 2:
        print("用法: python parser_factory.py <文件路径>")
        print(f"\n支持的格式: {', '.join(ParserFactory.get_supported_formats())}")
        return
    
    file_path = sys.argv[1]
    
    try:
        # 自动创建解析器
        parser = ParserFactory.create_parser(file_path)
        
        # 解析文件
        data = parser.parse()
        
        # 显示结果
        print(f"\n✅ 解析成功:")
        print(f"  - 文件: {data['metadata']['file_name']}")
        print(f"  - 格式: {data['metadata']['file_format']}")
        print(f"  - 大小: {data['metadata']['file_size_mb']} MB")
        
        metrics = data['metrics']
        for key, value in metrics.items():
            print(f"  - {key}: {value}")
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        return 1


if __name__ == '__main__':
    main()
