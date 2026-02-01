"""
解析器基类

定义所有文档解析器的统一接口
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any, List
import pandas as pd
from datetime import datetime


class BaseParser(ABC):
    """文档解析器抽象基类"""
    
    def __init__(self, file_path: str):
        """
        初始化解析器
        
        Args:
            file_path: 文件路径
        """
        self.file_path = Path(file_path)
        
        if not self.file_path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")
    
    @abstractmethod
    def parse(self) -> Dict[str, Any]:
        """
        解析文档，返回标准化数据结构
        
        Returns:
            {
                'metadata': {...},     # 文件元数据
                'content': {...},      # 内容（文本、表格等）
                'metrics': {...}       # 统计指标
            }
        """
        pass
    
    @abstractmethod
    def extract_text(self) -> str:
        """
        提取纯文本内容
        
        Returns:
            文档的纯文本内容
        """
        pass
    
    @abstractmethod
    def extract_tables(self) -> List[pd.DataFrame]:
        """
        提取所有表格
        
        Returns:
            表格列表（DataFrame 格式）
        """
        pass
    
    def get_metadata(self) -> Dict[str, Any]:
        """
        获取文件元数据
        
        Returns:
            包含文件信息的字典
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
        获取文件格式
        
        Returns:
            文件格式名称
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
