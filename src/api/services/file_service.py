"""
File Storage Service

Manages file uploads and storage
"""

import aiofiles
from pathlib import Path
from typing import List
import shutil
from datetime import datetime, timedelta
import os


class FileService:
    """Service for managing file uploads and storage"""
    
    def __init__(self, upload_dir: str = "uploads", result_dir: str = "results"):
        """
        Initialize file service
        
        Args:
            upload_dir: Directory for uploaded files
            result_dir: Directory for result files
        """
        self.upload_dir = Path(upload_dir)
        self.result_dir = Path(result_dir)
        
        # Create directories if they don't exist
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.result_dir.mkdir(parents=True, exist_ok=True)
    
    def get_task_upload_dir(self, task_id: str) -> Path:
        """Get upload directory for a specific task"""
        task_dir = self.upload_dir / task_id
        task_dir.mkdir(parents=True, exist_ok=True)
        return task_dir
    
    async def save_uploaded_file(self, task_id: str, filename: str, content: bytes) -> str:
        """
        Save uploaded file
        
        Args:
            task_id: Task ID
            filename: Original filename
            content: File content
            
        Returns:
            Path to saved file
        """
        task_dir = self.get_task_upload_dir(task_id)
        file_path = task_dir / filename
        
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(content)
        
        return str(file_path)
    
    def get_task_files(self, task_id: str) -> List[str]:
        """Get all files for a task"""
        task_dir = self.get_task_upload_dir(task_id)
        
        if not task_dir.exists():
            return []
        
        return [str(f) for f in task_dir.iterdir() if f.is_file()]
    
    def get_result_path(self, task_id: str, filename: str = "merged_result.xlsx") -> str:
        """Get path for result file"""
        return str(self.result_dir / f"{task_id}_{filename}")
    
    def get_result(self, task_id: str) -> Path:
        """Get result file for a task"""
        # Find result file starting with task_id
        for file_path in self.result_dir.iterdir():
            if file_path.name.startswith(task_id):
                return file_path
        
        raise FileNotFoundError(f"No result file found for task {task_id}")
    
    def cleanup_task(self, task_id: str):
        """Clean up all files for a task"""
        # Remove upload directory
        task_dir = self.get_task_upload_dir(task_id)
        if task_dir.exists():
            shutil.rmtree(task_dir)
        
        # Remove result files
        for file_path in self.result_dir.iterdir():
            if file_path.name.startswith(task_id):
                file_path.unlink()
    
    def cleanup_old_files(self, hours: int = 24):
        """Clean up files older than specified hours"""
        cutoff = datetime.now() - timedelta(hours=hours)
        
        # Cleanup uploads
        for task_dir in self.upload_dir.iterdir():
            if task_dir.is_dir():
                mtime = datetime.fromtimestamp(task_dir.stat().st_mtime)
                if mtime < cutoff:
                    shutil.rmtree(task_dir)
        
        # Cleanup results
        for file_path in self.result_dir.iterdir():
            if file_path.is_file():
                mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                if mtime < cutoff:
                    file_path.unlink()
    
    def get_file_size(self, file_path: str) -> int:
        """Get file size in bytes"""
        return Path(file_path).stat().st_size
    
    def validate_file(self, filename: str, max_size_mb: int = 50) -> bool:
        """
        Validate file
        
        Args:
            filename: Filename to validate
            max_size_mb: Maximum file size in MB
            
        Returns:
            True if valid
        """
        # Check extension
        allowed_extensions = {'.xlsx', '.xls', '.csv', '.docx', '.doc', '.pdf'}
        ext = Path(filename).suffix.lower()
        
        return ext in allowed_extensions
