"""
CrewAI Log Streamer
Captures CrewAI logs and streams them to frontend via WebSocket
"""

import logging
import json
import time
from typing import Dict, Any, Optional
from datetime import datetime
import re
import asyncio

def safe_broadcast_message(websocket_manager, message: Dict):
    """Thread-safe utility for broadcasting WebSocket messages"""
    if not websocket_manager:
        return
    
    try:
        # Try to get the current event loop
        loop = asyncio.get_running_loop()
        # Schedule the broadcast in the existing event loop
        loop.call_soon_threadsafe(
            lambda: asyncio.create_task(websocket_manager.broadcast(message))
        )
    except RuntimeError:
        # No event loop running - skip gracefully
        pass

class CrewAILogStreamer:
    """Captures and streams CrewAI logs to WebSocket clients"""
    
    def __init__(self):
        self.websocket_manager = None
        self.session_id = None
        self.log_handler = None
        self.setup_log_handler()
    
    def setup_log_handler(self):
        """Setup custom log handler to capture CrewAI logs"""
        self.log_handler = CrewAIWebSocketHandler(self)
        
        # Add handler to capture logs from CrewAI and related modules
        crewai_loggers = [
            logging.getLogger('crewai'),
            logging.getLogger('crew'),  
            logging.getLogger('agent'),
            logging.getLogger('task'),
            logging.getLogger('langchain'),
            logging.getLogger('openai'),
            logging.getLogger('anthropic'),
            logging.getLogger(),  # Root logger as fallback
        ]
        
        for logger in crewai_loggers:
            logger.addHandler(self.log_handler)
            # Make sure we capture INFO level and above
            if logger.level > logging.INFO:
                logger.setLevel(logging.INFO)
    
    def set_websocket_manager(self, manager):
        """Set the WebSocket manager for broadcasting logs"""
        self.websocket_manager = manager
        self.log_handler.websocket_manager = manager
    
    def set_session_id(self, session_id: str):
        """Set current session ID for log context"""
        self.session_id = session_id
        self.log_handler.session_id = session_id
    
    def log_crewai_event(self, event_type: str, message: str, data: Dict = None):
        """Manually log a CrewAI event"""
        log_entry = {
            "timestamp": time.time(),
            "datetime": datetime.now().isoformat(),
            "session_id": self.session_id,
            "event_type": event_type,
            "message": message,
            "data": data or {},
            "source": "crewai_manual"
        }
        
        if self.websocket_manager:
            self._broadcast_log(log_entry)
    
    def _broadcast_log(self, log_entry: Dict):
        """Broadcast log entry to all WebSocket clients"""
        if not self.websocket_manager:
            return
            
        message = {
            "type": "crewai_log",
            "timestamp": time.time(),
            "log": log_entry
        }
        
        # Schedule broadcast using thread-safe approach
        safe_broadcast_message(self.websocket_manager, message)

class CrewAIWebSocketHandler(logging.Handler):
    """Custom log handler that streams CrewAI logs to WebSocket"""
    
    def __init__(self, streamer):
        super().__init__()
        self.streamer = streamer
        self.websocket_manager = None
        self.session_id = None
        
        # Set up formatter for clean log messages
        self.setFormatter(logging.Formatter(
            '%(levelname)s - %(name)s - %(message)s'
        ))
    
    def emit(self, record):
        """Emit log record to WebSocket clients"""
        try:
            # Filter out logs we don't want to stream
            if self._should_filter_log(record):
                return
            
            # Format the log message
            formatted_message = self.format(record)
            
            # Create structured log entry
            log_entry = {
                "timestamp": time.time(),
                "datetime": datetime.fromtimestamp(record.created).isoformat(),
                "session_id": self.session_id,
                "level": record.levelname,
                "logger": record.name,
                "message": formatted_message,
                "raw_message": record.getMessage(),
                "source": "python_logger",
                "module": getattr(record, 'module', ''),
                "function": getattr(record, 'funcName', ''),
                "line": getattr(record, 'lineno', 0)
            }
            
            # Add extra context for CrewAI specific logs
            if self._is_crewai_log(record):
                log_entry["event_type"] = self._extract_event_type(record.getMessage())
                log_entry["agent_info"] = self._extract_agent_info(record.getMessage())
            
            # Broadcast to WebSocket clients
            if self.websocket_manager:
                self._broadcast_log(log_entry)
                
        except Exception as e:
            # Don't let logging errors crash the app
            print(f"Error in CrewAI log handler: {e}")
    
    def _should_filter_log(self, record) -> bool:
        """Determine if we should filter out this log record"""
        message = record.getMessage().lower()
        
        # Filter out noise logs
        noise_patterns = [
            'starting new https connection',
            'http connection pool is full',
            'connection pool is full, discarding connection',
            'retrying request',
            'urllib3',
            'connectionpool'
        ]
        
        for pattern in noise_patterns:
            if pattern in message:
                return True
        
        # Only stream INFO and above
        if record.levelno < logging.INFO:
            return True
            
        return False
    
    def _is_crewai_log(self, record) -> bool:
        """Check if this is a CrewAI related log"""
        crewai_modules = ['crewai', 'crew', 'agent', 'task']
        return any(module in record.name.lower() for module in crewai_modules)
    
    def _extract_event_type(self, message: str) -> str:
        """Extract event type from CrewAI log message"""
        message_lower = message.lower()
        
        if 'starting' in message_lower or 'begin' in message_lower:
            return 'task_start'
        elif 'completed' in message_lower or 'finished' in message_lower:
            return 'task_complete'
        elif 'delegating' in message_lower or 'asking' in message_lower:
            return 'delegation'
        elif 'thinking' in message_lower or 'analyzing' in message_lower:
            return 'thinking'
        elif 'error' in message_lower or 'failed' in message_lower:
            return 'error'
        elif 'tool' in message_lower:
            return 'tool_use'
        else:
            return 'general'
    
    def _extract_agent_info(self, message: str) -> Dict:
        """Extract agent information from log message"""
        agent_info = {}
        
        # Try to extract agent name patterns
        agent_patterns = [
            r'Agent (\w+)',
            r'agent (\w+)',
            r'(\w+) agent',
            r'(\w+Agent)',
        ]
        
        for pattern in agent_patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                agent_info['agent_name'] = match.group(1)
                break
        
        # Try to extract task information
        if 'task' in message.lower():
            task_match = re.search(r'task[:\s]+([^\.]+)', message, re.IGNORECASE)
            if task_match:
                agent_info['task'] = task_match.group(1).strip()
        
        return agent_info
    
    def _broadcast_log(self, log_entry: Dict):
        """Broadcast log entry to WebSocket clients"""
        if not self.websocket_manager:
            return
            
        message = {
            "type": "crewai_log",
            "timestamp": time.time(),
            "log": log_entry
        }
        
        # Use thread-safe broadcast scheduling
        safe_broadcast_message(self.websocket_manager, message)

# Global log streamer instance
crewai_log_streamer = CrewAILogStreamer()