"""Logging configuration for the travel agent system."""
import logging
import sys
from datetime import datetime
from typing import List, Dict, Any
from travel_agent.core.config import VERBOSE


class TravelAgentLogger:
    """Custom logger for travel agent operations."""
    
    def __init__(self):
        self.logs: List[Dict[str, Any]] = []
        self.logger = logging.getLogger("TravelAgent")
        self.logger.setLevel(logging.DEBUG if VERBOSE else logging.INFO)
        
        # Prevent duplicate handlers - only add if no handlers exist
        if not self.logger.handlers:
            # Console handler
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(logging.INFO)
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)
            # Prevent propagation to root logger to avoid duplicate logs
            self.logger.propagate = False
    
    def log_operation(self, agent: str, operation: str, details: str = "", 
                     status: str = "info", duration: float = None):
        """Log an operation with details."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "agent": agent,
            "operation": operation,
            "details": details,
            "status": status,
            "duration": duration
        }
        self.logs.append(log_entry)
        
        # Also log to standard logger
        message = f"[{agent}] {operation}"
        if details:
            message += f": {details[:200]}"  # Truncate long details
        if duration:
            message += f" (Duration: {duration:.2f}s)"
        
        if status == "error":
            self.logger.error(message)
        elif status == "warning":
            self.logger.warning(message)
        elif status == "success":
            self.logger.info(f"✓ {message}")
        else:
            self.logger.info(message)
    
    def log_llm_call(self, agent: str, prompt_length: int, response_length: int, 
                    duration: float = None):
        """Log an LLM API call."""
        self.log_operation(
            agent=agent,
            operation="LLM Call",
            details=f"Prompt: {prompt_length} chars, Response: {response_length} chars",
            status="info",
            duration=duration
        )
    
    def log_state_transition(self, from_agent: str, to_agent: str, state_summary: str = ""):
        """Log a state transition in the workflow."""
        self.log_operation(
            agent="Orchestrator",
            operation=f"State Transition: {from_agent} → {to_agent}",
            details=state_summary,
            status="info"
        )
    
    def get_logs(self, agent: str = None, limit: int = None) -> List[Dict[str, Any]]:
        """Get logs, optionally filtered by agent."""
        logs = self.logs
        if agent:
            logs = [log for log in logs if log["agent"] == agent]
        if limit:
            logs = logs[-limit:]
        return logs
    
    def clear_logs(self):
        """Clear all logs."""
        self.logs = []
        self.logger.info("Logs cleared")
    
    def get_log_summary(self) -> Dict[str, Any]:
        """Get a summary of logs."""
        if not self.logs:
            return {"total": 0, "by_agent": {}, "by_status": {}}
        
        by_agent = {}
        by_status = {}
        
        for log in self.logs:
            agent = log["agent"]
            status = log["status"]
            
            by_agent[agent] = by_agent.get(agent, 0) + 1
            by_status[status] = by_status.get(status, 0) + 1
        
        return {
            "total": len(self.logs),
            "by_agent": by_agent,
            "by_status": by_status,
            "last_log": self.logs[-1] if self.logs else None
        }


# Global logger instance - singleton pattern to prevent duplicate handlers
_logger_instance = None

def get_logger():
    """Get or create the global logger instance."""
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = TravelAgentLogger()
    return _logger_instance

# Create logger instance
logger = get_logger()
