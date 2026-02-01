"""
Merge Service

Handles document merging operations
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from mergers.excel_merger import ExcelMerger
from api.models.task import Task, TaskStatus
from typing import Dict
import traceback


class MergeService:
    """Service for handling merge operations"""
    
    def __init__(self):
        """Initialize merge service"""
        self.tasks: Dict[str, Task] = {}
    
    def create_task(self) -> Task:
        """Create a new task"""
        task = Task()
        self.tasks[task.id] = task
        return task
    
    def get_task(self, task_id: str) -> Task:
        """Get task by ID"""
        if task_id not in self.tasks:
            raise ValueError(f"Task {task_id} not found")
        return self.tasks[task_id]
    
    def update_task_status(self, task_id: str, status: TaskStatus, error: str = None):
        """Update task status"""
        task = self.get_task(task_id)
        task.status = status
        
        if error:
            task.error = error
        
        if status == TaskStatus.COMPLETED or status == TaskStatus.FAILED:
            from datetime import datetime
            task.completed_at = datetime.now()
    
    def merge_files(self, task_id: str, output_path: str) -> bool:
        """
        Merge files for a task
        
        Args:
            task_id: Task ID
            output_path: Output file path
            
        Returns:
            True if successful
        """
        try:
            task = self.get_task(task_id)
            
            if not task.files:
                raise ValueError("No files to merge")
            
            # Update status
            self.update_task_status(task_id, TaskStatus.PROCESSING)
            
            # Create merger
            merger = ExcelMerger()
            
            # Add all files
            success_count = merger.add_files(task.files)
            
            if success_count == 0:
                raise ValueError("No files were successfully processed")
            
            # Merge to Excel
            if not merger.merge_to_excel(output_path):
                raise ValueError("Merge operation failed")
            
            # Update task
            task.result_path = output_path
            self.update_task_status(task_id, TaskStatus.COMPLETED)
            
            return True
            
        except Exception as e:
            error_msg = f"Merge failed: {str(e)}"
            print(error_msg)
            traceback.print_exc()
            self.update_task_status(task_id, TaskStatus.FAILED, error=error_msg)
            return False
    
    def get_task_progress(self, task_id: str) -> int:
        """
        Get task progress percentage
        
        Args:
            task_id: Task ID
            
        Returns:
            Progress percentage (0-100)
        """
        task = self.get_task(task_id)
        
        if task.status == TaskStatus.QUEUED:
            return 0
        elif task.status == TaskStatus.PROCESSING:
            return 50
        elif task.status == TaskStatus.COMPLETED:
            return 100
        elif task.status == TaskStatus.FAILED:
            return 0
        
        return 0
