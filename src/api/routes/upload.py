"""
Upload Routes

Handles file upload endpoints
"""

from fastapi import APIRouter, File, UploadFile, HTTPException
from typing import List
import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from api.models.task import UploadResponse
from api.services.file_service import FileService
from api.services.merge_service import MergeService

router = APIRouter()

# Services (these will be injected from main app)
file_service = FileService()
merge_service = MergeService()


@router.post("/upload", response_model=UploadResponse)
async def upload_files(files: List[UploadFile] = File(...)):
    """
    Upload multiple files for merging
    
    Args:
        files: List of files to upload
        
    Returns:
        Upload response with task ID
    """
    try:
        # Create new task
        task = merge_service.create_task()
        
        # Validate and save files
        saved_files = []
        for file in files:
            # Validate file
            if not file_service.validate_file(file.filename):
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid file type: {file.filename}. Supported: Excel, CSV, Word, PDF"
                )
            
            # Read and save file
            content = await file.read()
            file_path = await file_service.save_uploaded_file(
                task.id,
                file.filename,
                content
            )
            saved_files.append(file_path)
        
        # Update task with file paths
        task.files = saved_files
        
        return UploadResponse(
            task_id=task.id,
            files_received=len(saved_files),
            status="queued",
            message=f"Successfully uploaded {len(saved_files)} file(s)"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")
