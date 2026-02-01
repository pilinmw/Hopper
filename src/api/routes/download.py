"""
Download Routes

Handles file download endpoints
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from api.services.file_service import FileService
from api.services.merge_service import MergeService

router = APIRouter()

# Services
file_service = FileService()
merge_service = MergeService()


@router.get("/download/{task_id}")
async def download_result(task_id: str):
    """
    Download merged result file
    
    Args:
        task_id: Task ID
        
    Returns:
        File download response
    """
    try:
        # Get task
        task = merge_service.get_task(task_id)
        
        if task.status != "completed":
            raise HTTPException(
                status_code=400,
                detail=f"Task not completed. Current status: {task.status}"
            )
        
        if not task.result_path:
            raise HTTPException(
                status_code=404,
                detail="Result file not found"
            )
        
        # Get result file
        result_path = Path(task.result_path)
        
        if not result_path.exists():
            raise HTTPException(
                status_code=404,
                detail="Result file not found on server"
            )
        
        # Return file
        return FileResponse(
            path=str(result_path),
            filename=result_path.name,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Download failed: {str(e)}")
