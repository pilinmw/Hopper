"""
Chat Routes

WebSocket and REST endpoints for conversational agent
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from typing import List
import json
import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agents.chat_agent import ChatAgent, AgentResponse
from agents.data_analyzer import DataAnalyzer
from agents.session_manager import SessionManager
from agents.visualization_engine import VisualizationEngine
from parsers.parser_factory import ParserFactory
import pandas as pd

router = APIRouter()

# Global managers (in production, use dependency injection)
session_manager = SessionManager()
viz_engine = VisualizationEngine()


@router.post("/sessions")
async def create_chat_session():
    """Create new chat session"""
    session = session_manager.create_session()
    
    # Initialize chat agent
    session.chat_agent = ChatAgent()
    
    return {
        "session_id": session.id,
        "created_at": session.created_at.isoformat(),
        "message": "Session created. You can now upload data and start chatting!"
    }


@router.post("/sessions/{session_id}/upload")
async def upload_file_to_session(session_id: str, file: UploadFile = File(...)):
    """Upload file to chat session"""
    session = session_manager.get_session(session_id)
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    try:
        # Save file temporarily
        temp_path = Path(f"/tmp/{file.filename}")
        with open(temp_path, 'wb') as f:
            content = await file.read()
            f.write(content)
        
        # Parse file
        parser = ParserFactory.create_parser(str(temp_path))
        parsed_data = parser.parse()
        
        # Get tables
        tables = parsed_data['content'].get('tables', [])
        
        if not tables:
            raise HTTPException(status_code=400, detail="No tables found in file")
        
        # Use first table (or let user choose)
        df = tables[0]
        
        # Create data analyzer
        analyzer = DataAnalyzer(df)
        
        # Update session
        session.data = df
        session.data_analyzer = analyzer
        
        # Get data summary for agent
        summary = analyzer.get_summary()
        
        # Update agent context
        if session.chat_agent:
            session.chat_agent.data_context = summary
        
        return {
            "message": "File uploaded successfully",
            "file_name": file.filename,
            "data_summary": summary
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.websocket("/ws/{session_id}")
async def websocket_chat(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for real-time chat"""
    await websocket.accept()
    
    session = session_manager.get_session(session_id)
    
    if not session:
        await websocket.send_json({"error": "Session not found"})
        await websocket.close()
        return
    
    try:
        while True:
            # Receive message
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            user_message = message_data.get('message', '')
            
            if not user_message:
                continue
            
            # Process with chat agent
            if not session.chat_agent:
                session.chat_agent = ChatAgent()
            
            response = await session.chat_agent.process_message(
                user_message,
                context=session.data_analyzer.get_summary() if session.data_analyzer else None
            )
            
            # Execute intent if present
            result_data = None
            if response.intent and session.data_analyzer:
                result_data = await execute_intent(
                    response.intent,
                    session.data_analyzer,
                    session_id
                )
            
            # Send response
            await websocket.send_json({
                "type": "message",
                "message": response.message,
                "intent": response.intent.to_dict() if response.intent else None,
                "quick_actions": response.quick_actions,
                "result": result_data
            })
            
    except WebSocketDisconnect:
        print(f"Client disconnected from session {session_id}")


async def execute_intent(intent, analyzer: DataAnalyzer, session_id: str):
    """Execute user intent and return results"""
    
    if intent.action == 'filter':
        # Apply filters
        params = intent.parameters
        if 'category' in params:
            # Find category column
            categories = analyzer.metadata.categories
            if categories:
                category_col = list(categories.keys())[0]
                analyzer.apply_filter(category_col, params['category'])
                
                return {
                    "action": "filter_applied",
                    "preview": analyzer.get_preview(5)
                }
    
    elif intent.action == 'pivot':
        # Create pivot table
        params = intent.parameters
        # This would create pivot based on params
        pass
    
    elif intent.action == 'export':
        # Generate requested formats
        formats = intent.parameters.get('formats', ['excel'])
        data = analyzer.get_current_data()
        
        results = {}
        for format_type in formats:
            if format_type == 'ppt':
                path = viz_engine.generate_ppt(data)
                results['ppt'] = {"path": path, "download_url": f"/api/v1/chat/download/{session_id}/ppt"}
            # Add other formats...
        
        return {
            "action": "export_complete",
            "results": results
        }
    
    return None


@router.get("/sessions/{session_id}")
async def get_session_info(session_id: str):
    """Get session information"""
    info = session_manager.get_session_info(session_id)
    
    if not info:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return info


@router.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    """Delete session"""
    session_manager.delete_session(session_id)
    return {"message": "Session deleted"}
