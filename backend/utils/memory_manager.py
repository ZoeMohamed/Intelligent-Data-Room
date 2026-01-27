from typing import List, Dict, Any, Optional, Union

class ConversationMemory:
    def __init__(self, max_history: int = 5):
        self.history: List[Dict[str, Any]] = []
        self.max_history = max_history
    
    def add_exchange(self, query: str, plan_or_result: Union[Dict, str], result: Optional[Any] = None):
        """Add an exchange to memory. Supports both:
        - add_exchange(query, plan_dict, result) - original format
        - add_exchange(query, result_string) - simplified format from api.py
        """
        if result is None:
            # Called with 2 args: query and result string
            self.history.append({
                "query": query,
                "intent": "query",
                "columns": [],
                "result_type": "string",
                "result_preview": str(plan_or_result)[:100]
            })
        else:
            # Called with 3 args: query, plan dict, result
            plan = plan_or_result if isinstance(plan_or_result, dict) else {}
            self.history.append({
                "query": query,
                "intent": plan.get("intent", "unknown"),
                "columns": plan.get("columns_needed", []),
                "result_type": type(result).__name__,
                "result_preview": str(result)[:100]
            })
        
        if len(self.history) > self.max_history:
            self.history.pop(0)
    
    def get_context_string(self) -> str:
        if not self.history:
            return "No previous conversation."
        
        context = "Previous exchanges:\n"
        for i, ex in enumerate(self.history, 1):
            query_preview = ex['query'][:50] + '...' if len(ex['query']) > 50 else ex['query']
            context += f"{i}. Q: {query_preview} | Intent: {ex.get('intent', 'unknown')}\n"
        
        return context
    
    def get_context(self) -> List[Dict[str, Any]]:
        """Get raw conversation history"""
        return self.history
    
    def clear(self):
        """Clear conversation history"""
        self.history = []