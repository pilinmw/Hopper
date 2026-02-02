"""
Session Manager

Manage user sessions and conversation context
"""

import uuid
from typing import Dict, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, field
import pandas as pd


@dataclass
class Session:
    """User session"""
    id: str
    created_at: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)
    data: Optional[pd.DataFrame] = None
    data_analyzer: Optional[Any] = None
    chat_agent: Optional[Any] = None
    conversation_history: list = field(default_factory=list)
    user_data: Dict = field(default_factory=dict)
    
    def is_expired(self, timeout_seconds: int = 3600) -> bool:
        """Check if session has expired"""
        return (datetime.now() - self.last_activity).total_seconds() > timeout_seconds
    
    def touch(self):
        """Update last activity timestamp"""
        self.last_activity = datetime.now()


class SessionManager:
    """Manage user sessions"""
    
    def __init__(self, timeout_seconds: int = 3600, max_sessions: int = 100):
        """
        Initialize session manager
        
        Args:
            timeout_seconds: Session timeout in seconds
            max_sessions: Maximum number of active sessions
        """
        self.timeout_seconds = timeout_seconds
        self.max_sessions = max_sessions
        self.sessions: Dict[str, Session] = {}
    
    def create_session(self, user_id: Optional[str] = None) -> Session:
        """
        Create new session
        
        Args:
            user_id: Optional user identifier
            
        Returns:
            New Session object
        """
        # Cleanup expired sessions
        self.cleanup_expired()
        
        # Check session limit
        if len(self.sessions) >= self.max_sessions:
            # Remove oldest session
            oldest_id = min(self.sessions.keys(), 
                          key=lambda k: self.sessions[k].last_activity)
            del self.sessions[oldest_id]
        
        # Create new session
        session_id = str(uuid.uuid4())
        session = Session(id=session_id)
        
        if user_id:
            session.user_data['user_id'] = user_id
        
        self.sessions[session_id] = session
        
        return session
    
    def get_session(self, session_id: str) -> Optional[Session]:
        """
        Get session by ID
        
        Args:
            session_id: Session ID
            
        Returns:
            Session object or None if not found/expired
        """
        session = self.sessions.get(session_id)
        
        if session and session.is_expired(self.timeout_seconds):
            # Session expired, remove it
            del self.sessions[session_id]
            return None
        
        if session:
            session.touch()
        
        return session
    
    def update_session(self, session_id: str, **kwargs):
        """
        Update session data
        
        Args:
            session_id: Session ID
            **kwargs: Data to update
        """
        session = self.get_session(session_id)
        
        if not session:
            raise ValueError(f"Session {session_id} not found or expired")
        
        for key, value in kwargs.items():
            if hasattr(session, key):
                setattr(session, key, value)
            else:
                session.user_data[key] = value
        
        session.touch()
    
    def delete_session(self, session_id: str):
        """Delete session"""
        if session_id in self.sessions:
            del self.sessions[session_id]
    
    def cleanup_expired(self):
        """Cleanup expired sessions"""
        expired = [
            sid for sid, session in self.sessions.items()
            if session.is_expired(self.timeout_seconds)
        ]
        
        for sid in expired:
            del self.sessions[sid]
    
    def get_active_session_count(self) -> int:
        """Get number of active sessions"""
        self.cleanup_expired()
        return len(self.sessions)
    
    def get_session_info(self, session_id: str) -> Optional[Dict]:
        """Get session information"""
        session = self.get_session(session_id)
        
        if not session:
            return None
        
        return {
            'id': session.id,
            'created_at': session.created_at.isoformat(),
            'last_activity': session.last_activity.isoformat(),
            'has_data': session.data is not None,
            'conversation_length': len(session.conversation_history)
        }


# Typing import fix
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    Any = object
else:
    from typing import Any
