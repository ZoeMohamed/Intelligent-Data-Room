"""
Agent Communication Logger
Tracks and logs interactions between agents for debugging and transparency.
"""
import json
import os
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path


class AgentLogger:
    """Logs agent communications and decisions"""
    
    def __init__(self, log_dir: str = "logs", enable_file_logging: bool = True):
        self.log_dir = Path(log_dir)
        self.enable_file_logging = enable_file_logging
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if self.enable_file_logging:
            self.log_dir.mkdir(exist_ok=True)
            self.log_file = self.log_dir / f"agent_session_{self.session_id}.log"
    
    def log_planner_input(self, query: str, schema: str, history: str):
        """Log input to planner agent"""
        # Convert schema to string if it's a DataFrame
        schema_str = str(schema) if not isinstance(schema, str) else schema
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "agent": "planner",
            "type": "input",
            "query": query,
            "schema_preview": schema_str[:200] + "..." if len(schema_str) > 200 else schema_str,
            "has_history": bool(history and history != "No previous conversation.")
        }
        self._write_log(log_entry)
    
    def log_planner_output(self, plan: Dict[str, Any]):
        """Log planner agent output"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "agent": "planner",
            "type": "output",
            "intent": plan.get("intent"),
            "chart_type": plan.get("chart_type"),
            "steps": plan.get("steps"),
            "columns_needed": plan.get("columns_needed"),
            "complexity": plan.get("complexity"),
            "reasoning": plan.get("reasoning", "")[:150]
        }
        self._write_log(log_entry)
    
    def log_executor_input(self, plan: Dict[str, Any], df_shape: tuple):
        """Log input to executor agent"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "agent": "executor",
            "type": "input",
            "plan_intent": plan.get("intent"),
            "plan_steps_count": len(plan.get("steps", [])),
            "data_shape": {"rows": df_shape[0], "columns": df_shape[1]}
        }
        self._write_log(log_entry)
    
    def log_executor_output(self, result: Dict[str, Any]):
        """Log executor agent output"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "agent": "executor",
            "type": "output",
            "success": result.get("success"),
            "has_chart": result.get("chart") is not None,
            "result_preview": str(result.get("data", ""))[:200]
        }
        self._write_log(log_entry)
    
    def log_error(self, agent: str, error: str, context: Optional[Dict] = None):
        """Log errors from agents"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "agent": agent,
            "type": "error",
            "error": str(error),
            "context": context or {}
        }
        self._write_log(log_entry)
    
    def log_interaction_summary(
        self, 
        query: str, 
        plan: Dict[str, Any], 
        result: Dict[str, Any],
        execution_time: float
    ):
        """Log complete interaction summary"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "summary",
            "query": query,
            "plan_complexity": plan.get("complexity"),
            "execution_success": result.get("success"),
            "execution_time_seconds": round(execution_time, 2),
            "visualization_created": result.get("chart") is not None
        }
        self._write_log(log_entry)
    
    def _write_log(self, log_entry: Dict[str, Any]):
        """Write log entry to file and console"""
        # Console output (condensed)
        log_type = log_entry.get("type", "unknown")
        agent = log_entry.get("agent", "system")
        
        if log_type == "input":
            print(f"[{agent.upper()}]  Received input")
        elif log_type == "output":
            print(f"[{agent.upper()}]  Generated output")
        elif log_type == "error":
            print(f"[{agent.upper()}]  Error: {log_entry.get('error', '')[:100]}")
        elif log_type == "summary":
            print(f"[SUMMARY]  Query completed in {log_entry.get('execution_time_seconds')}s")
        
        # File output (detailed)
        if self.enable_file_logging:
            try:
                with open(self.log_file, 'a') as f:
                    f.write(json.dumps(log_entry, indent=2) + "\n")
                    f.write("-" * 80 + "\n")
            except Exception as e:
                print(f"Warning: Could not write to log file: {e}")
    
    def get_session_logs(self) -> list:
        """Retrieve all logs from current session"""
        if not self.enable_file_logging or not self.log_file.exists():
            return []
        
        logs = []
        try:
            with open(self.log_file, 'r') as f:
                content = f.read()
                # Split by separator and parse JSON
                for block in content.split("-" * 80):
                    block = block.strip()
                    if block:
                        try:
                            logs.append(json.loads(block))
                        except json.JSONDecodeError:
                            continue
        except Exception as e:
            print(f"Error reading logs: {e}")
        
        return logs


# Singleton instance
_logger_instance = None


def get_logger(enable_file_logging: bool = True) -> AgentLogger:
    """Get or create logger instance"""
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = AgentLogger(enable_file_logging=enable_file_logging)
    return _logger_instance
