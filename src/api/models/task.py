"""
Task Data Models

Pydantic models for API request/response
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum
import uuid


class TaskStatus(str, Enum):
    """Task status enumeration"""
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Task(BaseModel):
    """Task model"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    status: TaskStatus = TaskStatus.QUEUED
    files: List[str] = Field(default_factory=list)
    result_path: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    error: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "status": "completed",
                "files": ["file1.xlsx", "file2.csv"],
                "result_path": "results/result.xlsx",
                "created_at": "2024-02-01T10:00:00Z",
                "completed_at": "2024-02-01T10:00:05Z"
            }
        }


class UploadResponse(BaseModel):
    """Upload response model"""
    task_id: str
    files_received: int
    status: str = "queued"
    message: str = "Files uploaded successfully"


class MergeRequest(BaseModel):
    """Merge request model"""
    task_id: str
    output_filename: str = "merged_result.xlsx"


class MergeResponse(BaseModel):
    """Merge response model"""
    task_id: str
    status: str
    message: str
    estimated_time: str = "5s"


class TaskResponse(BaseModel):
    """Task status response"""
    task_id: str
    status: str
    progress: int = 0
    result_url: Optional[str] = None
    files_count: int = 0
    created_at: datetime
    completed_at: Optional[datetime] = None
    error: Optional[str] = None


class HealthResponse(BaseModel):
    """Health check response"""
    status: str = "healthy"
    version: str = "1.0.0"
    uptime: str
