"""
Routes Module
"""

from .upload import router as upload_router
from .merge import router as merge_router
from .download import router as download_router

__all__ = ['upload_router', 'merge_router', 'download_router']
