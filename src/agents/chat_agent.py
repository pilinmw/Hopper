"""
Chat Agent

Intelligent conversational agent using OpenAI API
"""

import os
import json
from typing import Optional, Dict, List, Any
from dataclasses import dataclass, asdict
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


@dataclass
class Intent:
    """User intent parsed from message"""
    action: str  # 'filter', 'pivot', 'visualize', 'export', 'query'
    parameters: Dict[str, Any]
    confidence: float
    
    def to_dict(self):
        return asdict(self)


@dataclass
class AgentResponse:
    """Agent response to user"""
    message: str
    intent: Optional[Intent] = None
    data_preview: Optional[Dict] = None
    quick_actions: Optional[List[str]] = None
    needs_confirmation: bool = False
    
    def to_dict(self):
        return {
            'message': self.message,
            'intent': self.intent.to_dict() if self.intent else None,
            'data_preview': self.data_preview,
            'quick_actions': self.quick_actions,
            'needs_confirmation': self.needs_confirmation
        }


class ChatAgent:
    """Intelligent chat agent for data analysis"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o-mini"):
        """
        Initialize chat agent
        
        Args:
            api_key: OpenAI API key (defaults to env var)
            model: OpenAI model to use
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        self.model = model or os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
        
        if not self.api_key or self.api_key == 'your-api-key-here':
            print("⚠️  Warning: OpenAI API key not configured. Set OPENAI_API_KEY in .env file")
            self.client = None
        else:
            self.client = OpenAI(api_key=self.api_key)
        
        self.conversation_history: List[Dict] = []
        self.data_context: Dict = {}
        self.system_prompt = self._build_system_prompt()
    
    def _build_system_prompt(self) -> str:
        """Build system prompt for the agent"""
        return """You are a helpful data analysis assistant. Your role is to help users analyze and visualize their data through natural conversation.

Your capabilities:
1. Filter data by categories, values, dates
2. Create pivot tables with user-specified rows/columns
3. Generate visualizations (PPT, PDF, charts, Excel)
4. Suggest appropriate analyses

Always:
- Be concise and helpful
- Confirm your understanding before taking actions
- Show data previews when relevant
- Offer quick action buttons for common tasks
- Ask clarifying questions if intent is unclear

When user uploads data, acknowledge it and describe what you see.
When user requests filtering or pivoting, extract the specific fields and values.
When user wants visualizations, ask about format preferences (PPT/PDF/Chart/Excel).

Respond in JSON format with:
{
    "message": "Your response to the user",
    "intent": {
        "action": "filter|pivot|visualize|export|query",
        "parameters": {...},
        "confidence": 0.0-1.0
    },
    "quick_actions": ["Action 1", "Action 2"],
    "needs_confirmation": true/false
}"""
    
    async def process_message(self, user_message: str, context: Optional[Dict] = None) -> AgentResponse:
        """
        Process user message and return intelligent response
        
        Args:
            user_message: User's message
            context: Current data context
            
        Returns:
            AgentResponse with message and extracted intent
        """
        if not self.client:
            return AgentResponse(
                message="⚠️ OpenAI API not configured. Please set your API key in .env file.",
                quick_actions=["View Documentation"]
            )
        
        # Update context
        if context:
            self.data_context = context
        
        # Build messages for API call
        messages = [{"role": "system", "content": self.system_prompt}]
        
        # Add context if available
        if self.data_context:
            context_msg = f"\n\nCurrent data context:\n{json.dumps(self.data_context, indent=2)}"
            messages[0]["content"] += context_msg
        
        # Add conversation history
        messages.extend(self.conversation_history[-5:])  # Keep last 5 messages
        
        # Add current user message
        messages.append({"role": "user", "content": user_message})
        
        try:
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                response_format={"type": "json_object"},
                temperature=0.7,
                max_tokens=1000
            )
            
            # Parse response
            content = response.choices[0].message.content
            parsed = json.loads(content)
            
            # Update conversation history
            self.conversation_history.append({"role": "user", "content": user_message})
            self.conversation_history.append({"role": "assistant", "content": content})
            
            # Build AgentResponse
            intent = None
            if 'intent' in parsed and parsed['intent']:
                intent = Intent(
                    action=parsed['intent'].get('action', 'query'),
                    parameters=parsed['intent'].get('parameters', {}),
                    confidence=parsed['intent'].get('confidence', 0.5)
                )
            
            return AgentResponse(
                message=parsed.get('message', 'I understand. Let me help you with that.'),
                intent=intent,
                quick_actions=parsed.get('quick_actions'),
                needs_confirmation=parsed.get('needs_confirmation', False)
            )
            
        except json.JSONDecodeError as e:
            print(f"Error parsing OpenAI response: {e}")
            # Fall back to simple response
            return AgentResponse(
                message="I understand your request. Let me process that for you.",
                intent=self.extract_intent(user_message),
                quick_actions=["Try again", "View help"]
            )
        except Exception as e:
            print(f"Error calling OpenAI API: {e}")
            # Provide helpful error message
            error_msg = str(e)
            if "API key" in error_msg or "authentication" in error_msg.lower():
                return AgentResponse(
                    message="⚠️ OpenAI API key is invalid or missing. Please check your .env configuration.",
                    quick_actions=["View documentation"]
                )
            elif "rate limit" in error_msg.lower():
                return AgentResponse(
                    message="⚠️ API rate limit exceeded. Please wait a moment and try again.",
                    quick_actions=["Try again"]
                )
            else:
                # Use fallback intent extraction
                return AgentResponse(
                    message=f"I'll help you with that using local processing.",
                    intent=self.extract_intent(user_message),
                    quick_actions=["Continue", "Try again"]
                )
    
    def extract_intent(self, message: str) -> Intent:
        """
        Extract intent from user message (fallback method)
        
        Args:
            message: User message
            
        Returns:
            Intent object
        """
        message_lower = message.lower()
        
        # Filter intent
        if any(word in message_lower for word in ['only', 'filter', 'just', 'where', 'show me']):
            return Intent(
                action='filter',
                parameters=self._extract_filter_params(message),
                confidence=0.7
            )
        
        # Pivot intent
        if any(word in message_lower for word in ['pivot', 'rows', 'columns', 'table']):
            return Intent(
                action='pivot',
                parameters=self._extract_pivot_params(message),
                confidence=0.7
            )
        
        # Visualization intent
        if any(word in message_lower for word in ['chart', 'graph', 'visualize', 'plot', 'show']):
            return Intent(
                action='visualize',
                parameters=self._extract_viz_params(message),
                confidence=0.6
            )
        
        # Export intent
        if any(word in message_lower for word in ['export', 'download', 'save', 'generate', 'create']):
            return Intent(
                action='export',
                parameters=self._extract_export_params(message),
                confidence=0.6
            )
        
        # Default: query
        return Intent(
            action='query',
            parameters={},
            confidence=0.3
        )
    
    def _extract_filter_params(self, message: str) -> Dict:
        """Extract filter parameters from message"""
        params = {}
        
        # Simple keyword extraction (can be enhanced)
        words = message.split()
        for i, word in enumerate(words):
            if word.lower() in ['only', 'just'] and i + 1 < len(words):
                params['category'] = words[i + 1]
        
        return params
    
    def _extract_pivot_params(self, message: str) -> Dict:
        """Extract pivot parameters from message"""
        params = {}
        
        message_lower = message.lower()
        
        # Extract rows
        if 'rows' in message_lower or 'row' in message_lower:
            # Simple pattern matching
            words = message.split()
            for i, word in enumerate(words):
                if 'row' in word.lower() and i + 1 < len(words):
                    params['rows'] = words[i + 1]
        
        # Extract columns
        if 'columns' in message_lower or 'column' in message_lower or 'cols' in message_lower:
            words = message.split()
            for i, word in enumerate(words):
                if 'col' in word.lower() and i + 1 < len(words):
                    params['columns'] = words[i + 1]
        
        return params
    
    def _extract_viz_params(self, message: str) -> Dict:
        """Extract visualization parameters"""
        params = {'chart_type': 'auto'}
        
        message_lower = message.lower()
        
        if 'bar' in message_lower:
            params['chart_type'] = 'bar'
        elif 'line' in message_lower:
            params['chart_type'] = 'line'
        elif 'pie' in message_lower:
            params['chart_type'] = 'pie'
        
        return params
    
    def _extract_export_params(self, message: str) -> Dict:
        """Extract export parameters"""
        params = {'formats': []}
        
        message_lower = message.lower()
        
        if 'ppt' in message_lower or 'powerpoint' in message_lower:
            params['formats'].append('ppt')
        if 'pdf' in message_lower:
            params['formats'].append('pdf')
        if 'excel' in message_lower or 'xlsx' in message_lower:
            params['formats'].append('excel')
        if 'chart' in message_lower or 'interactive' in message_lower:
            params['formats'].append('chart')
        
        # If no specific format mentioned, ask
        if not params['formats']:
            params['formats'] = ['ask']
        
        return params
    
    def reset_conversation(self):
        """Reset conversation history"""
        self.conversation_history = []
        self.data_context = {}
    
    def get_conversation_summary(self) -> str:
        """Get summary of conversation"""
        return f"Messages: {len(self.conversation_history)}, Context: {bool(self.data_context)}"
