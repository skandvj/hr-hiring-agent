import json
import os
from datetime import datetime
from typing import Dict, Any, Optional, List

class SessionMemory:
    def __init__(self, session_id: Optional[str] = None):
        self.session_id = session_id or f"session_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        self.data_dir = os.path.join("data", "session_data")
        os.makedirs(self.data_dir, exist_ok=True)
        self.memory_file = os.path.join(self.data_dir, f"{self.session_id}.json")
        self.state = self._load_or_create_state()
    
    def _load_or_create_state(self) -> Dict[str, Any]:
        """Load existing state or create a new one"""
        if os.path.exists(self.memory_file):
            with open(self.memory_file, 'r') as f:
                return json.load(f)
        else:
            # Initialize with empty state
            initial_state = {
                "session_id": self.session_id,
                "created_at": datetime.now().isoformat(),
                "hiring_needs": {},
                "conversation_history": [],
                "job_descriptions": {},
                "hiring_checklists": {},
                "user_info": {}
            }
            self._save_state(initial_state)
            return initial_state
    
    def _save_state(self, state: Dict[str, Any]) -> None:
        """Save state to file"""
        with open(self.memory_file, 'w') as f:
            json.dump(state, f, indent=2)
    
    def update(self, key: str, value: Any) -> None:
        """Update a specific key in the state"""
        self.state[key] = value
        self._save_state(self.state)
    
    def get(self, key: str) -> Any:
        """Get a value from the state"""
        return self.state.get(key)
    
    def add_to_conversation(self, role: str, content: str) -> None:
        """Add a message to the conversation history"""
        if "conversation_history" not in self.state:
            self.state["conversation_history"] = []
        
        self.state["conversation_history"].append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        self._save_state(self.state)
    
    def add_hiring_need(self, role: str, details: Dict[str, Any]) -> None:
        """Add or update hiring need"""
        if "hiring_needs" not in self.state:
            self.state["hiring_needs"] = {}
        
        self.state["hiring_needs"][role] = details
        self._save_state(self.state)
    
    def add_job_description(self, role: str, description: str) -> None:
        """Add a job description"""
        if "job_descriptions" not in self.state:
            self.state["job_descriptions"] = {}
        
        self.state["job_descriptions"][role] = description
        self._save_state(self.state)
    
    def add_hiring_checklist(self, role: str, checklist: Dict[str, Any]) -> None:
        """Add a hiring checklist"""
        if "hiring_checklists" not in self.state:
            self.state["hiring_checklists"] = {}
        
        self.state["hiring_checklists"][role] = checklist
        self._save_state(self.state)
    
    def get_full_state(self) -> Dict[str, Any]:
        """Get the complete state"""
        return self.state

class AnalyticsTracker:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.analytics_dir = os.path.join("data", "analytics")
        os.makedirs(self.analytics_dir, exist_ok=True)
        self.analytics_file = os.path.join(self.analytics_dir, "usage_stats.json")
        self.session_started = datetime.now()
        self._track_session_start()
    
    def _load_analytics(self) -> Dict[str, Any]:
        """Load existing analytics or create new"""
        if os.path.exists(self.analytics_file):
            with open(self.analytics_file, 'r') as f:
                return json.load(f)
        else:
            return {"sessions": [], "tool_usage": {}, "role_requests": {}}
    
    def _save_analytics(self, data: Dict[str, Any]) -> None:
        """Save analytics data"""
        with open(self.analytics_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _track_session_start(self) -> None:
        """Track a new session"""
        analytics = self._load_analytics()
        
        # Check if this session already exists
        for session in analytics["sessions"]:
            if session["session_id"] == self.session_id:
                # Update existing session
                session["last_active"] = self.session_started.isoformat()
                self._save_analytics(analytics)
                return
        
        # Add new session
        session_data = {
            "session_id": self.session_id,
            "start_time": self.session_started.isoformat(),
            "last_active": self.session_started.isoformat(),
            "duration_seconds": 0,
            "messages_count": 0,
            "tools_used": []
        }
        
        analytics["sessions"].append(session_data)
        self._save_analytics(analytics)
    
    def track_message(self, role: str, content: str) -> None:
        """Track a message in the conversation"""
        analytics = self._load_analytics()
        
        # Find this session
        for session in analytics["sessions"]:
            if session["session_id"] == self.session_id:
                session["messages_count"] += 1
                session["last_active"] = datetime.now().isoformat()
                # Update duration
                start_time = datetime.fromisoformat(session["start_time"])
                session["duration_seconds"] = (datetime.now() - start_time).total_seconds()
                break
        
        self._save_analytics(analytics)
    
    def track_tool_usage(self, tool_name: str) -> None:
        """Track tool usage"""
        analytics = self._load_analytics()
        
        # Update tool usage
        if tool_name not in analytics["tool_usage"]:
            analytics["tool_usage"][tool_name] = 0
        
        analytics["tool_usage"][tool_name] += 1
        
        # Also add to this session's tools used
        for session in analytics["sessions"]:
            if session["session_id"] == self.session_id:
                if "tools_used" not in session:
                    session["tools_used"] = []
                if tool_name not in session["tools_used"]:
                    session["tools_used"].append(tool_name)
                break
        
        self._save_analytics(analytics)
    
    def track_role_request(self, role: str) -> None:
        """Track which roles are being requested"""
        analytics = self._load_analytics()
        
        # Update role requests
        if role not in analytics["role_requests"]:
            analytics["role_requests"][role] = 0
        
        analytics["role_requests"][role] += 1
        self._save_analytics(analytics)
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get usage statistics for display"""
        analytics = self._load_analytics()
        
        # Compile stats
        stats = {
            "total_sessions": len(analytics["sessions"]),
            "avg_session_duration": sum(s.get("duration_seconds", 0) for s in analytics["sessions"]) / max(1, len(analytics["sessions"])),
            "most_requested_role": max(analytics["role_requests"].items(), key=lambda x: x[1])[0] if analytics["role_requests"] else None,
            "top_tools": sorted(analytics["tool_usage"].items(), key=lambda x: x[1], reverse=True)[:3]
        }
        
        return stats