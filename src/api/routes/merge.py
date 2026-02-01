"""
Merge Routes

Handles merge operation endpoints
"""

from fastapi import APIRouter, HTTPException
import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from api.models.task import MergeRequest, MergeResponse, TaskResponse
from api.services.file_service import FileService
from api.services.merge_service import MergeService

router = APIRouter()

# Services
file_service = FileService()
merge_service = MergeService()


@router.post("/merge", response_model=MergeResponse)
async def start_merge(request: MergeRequest):
    """
    Start merge operation for uploaded files
    
    Args:
        request: Merge request with task ID
        
    Returns:
        Merge response with status
    """
    try:
        # Get task
        task = merge_service.get_task(request.task_id)
        
        if not task.files:
            raise HTTPException(
                status_code=400,
                detail="No files found for this task"
            )
        
        # Get output path
        output_path = file_service.get_result_path(
            request.task_id,
            request.output_filename
        )
        
        # Start merge (synchronous for now, can be async with Celery later)
        success = merge_service.merge_files(request.task_id, output_path)
        
        if not success:
            raise HTTPException(
                status_code=500,
                detail=f"Merge failed: {task.error}"
            )
        
        return MergeResponse(
            task_id=request.task_id,
            status="completed",
            message="Files merged successfully",
            estimated_time="0s"
        )
    
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Merge failed: {str(e)}")


@router.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task_status(task_id: str):
    """
    Get task status and progress
    
    Args:
        task_id: Task ID to query
        
    Returns:
        Task status response
    """
    try:
        task = merge_service.get_task(task_id)
        progress = merge_service.get_task_progress(task_id)
        
        # Build result URL if completed
        result_url = None
        if task.status == "completed" and task.result_path:
            result_url = f"/api/v1/download/{task_id}"
        
        return TaskResponse(
            task_id=task.id,
            status=task.status,
            progress=progress,
            result_url=result_url,
            files_count=len(task.files),
            created_at=task.created_at,
            completed_at=task.completed_at,
            error=task.error
        )
    
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get task status: {str(e)}")
