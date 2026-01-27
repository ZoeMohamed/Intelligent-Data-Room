import google.generativeai as genai
import json
import os
from dotenv import load_dotenv
from typing import Dict, Any
from utils.logger import get_logger
from utils.cache import QueryCache

load_dotenv()
logger = get_logger()

class PlannerAgent:
    def __init__(self, model_name: str = 'gemini-2.5-flash', use_cache: bool = True):
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        self.model_name = model_name
        self.model = genai.GenerativeModel(model_name)
        self.use_cache = use_cache
        self.cache = QueryCache() if use_cache else None
        print(f"[PLANNER]  Using model: {model_name}")
    
    def create_plan(self, query: str, schema: str, history: str = "") -> Dict[str, Any]:
        """Create execution plan with robust error handling"""
        
        # Check cache first
        if self.use_cache and self.cache:
            cached_plan = self.cache.get_plan(query, schema)
            if cached_plan:
                logger.log_planner_output(cached_plan)
                print("[CACHE]  Using cached plan")
                return cached_plan
        
        # Log input
        logger.log_planner_input(query, schema, history)
        
        system_prompt = f"""Analyze query and return ONLY valid JSON (no extra text).

DATASET COLUMNS:
{schema}

QUERY: {query}

Return JSON in this EXACT format:
{{
  "intent": "visualization",
  "steps": ["step 1", "step 2"],
  "chart_type": "bar",
  "columns_needed": ["col1", "col2"],
  "reasoning": "brief explanation",
  "complexity": "medium"
}}

Rules:
- Top N → chart_type="bar"
- Trend → chart_type="line"
- Correlation → chart_type="scatter"
- Distribution → chart_type="pie"

Return ONLY the JSON object now:"""

        try:
            response = self.model.generate_content(system_prompt)
            text = response.text.strip()
            
            # Aggressive JSON cleanup
            text = text.replace("```json", "").replace("```", "").strip()
            
            # Extract JSON from response
            if "{" in text and "}" in text:
                start = text.find("{")
                end = text.rfind("}") + 1
                text = text[start:end]
            
            # Fix common JSON issues
            import re
            
            # First, handle escaped quotes within strings (from AI model)
            # Replace \" with a placeholder, then fix quotes, then restore
            text = text.replace('\\"', '<<<QUOTE>>>')
            text = text.replace("'", '"')  # Single quotes to double quotes
            text = text.replace('<<<QUOTE>>>', '\\"')  # Restore escaped quotes
            
            text = re.sub(r',(\s*[}\]])', r'\1', text)  # Remove trailing commas
            text = re.sub(r'([{,]\s*)(\w+)(\s*:)', r'\1"\2"\3', text)  # Quote unquoted keys
            
            plan = json.loads(text)
            
            # Validate and add missing keys
            required_keys = ["intent", "steps", "chart_type", "columns_needed", "reasoning"]
            if not all(k in plan for k in required_keys):
                # Add defaults for missing keys
                if "intent" not in plan:
                    plan["intent"] = "visualization"
                if "steps" not in plan:
                    plan["steps"] = ["Analyze data", "Create visualization"]
                if "chart_type" not in plan:
                    plan["chart_type"] = "bar"
                if "columns_needed" not in plan:
                    plan["columns_needed"] = []
                if "reasoning" not in plan:
                    plan["reasoning"] = "Auto-generated plan"
            
            # Cache the plan
            if self.use_cache and self.cache:
                self.cache.set_plan(query, schema, plan)
            
            # Log output
            logger.log_planner_output(plan)
            return plan
            
        except Exception as e:
            logger.log_error("planner", f"JSON parsing error: {e}", {"raw_text": text[:500] if 'text' in locals() else 'N/A'})
            
            # Manual plan creation for common patterns
            import re
            
            # Detect intent from query
            query_lower = query.lower()
            
            # Check for explicit chart type mentions first
            if "bar chart" in query_lower or "bar graph" in query_lower:
                chart_type = "bar"
                intent = "visualization"
            elif "line chart" in query_lower or "line graph" in query_lower or "multi-line" in query_lower:
                chart_type = "line"
                intent = "trend"
            elif "scatter plot" in query_lower or "scatter chart" in query_lower:
                chart_type = "scatter"
                intent = "comparison"
            elif "pie chart" in query_lower or "pie graph" in query_lower:
                chart_type = "pie"
                intent = "visualization"
            # Check for "chart" keyword without specific type - default to bar
            elif " chart" in query_lower or "visualize" in query_lower or "show" in query_lower or "display" in query_lower:
                chart_type = "bar"
                intent = "visualization"
            # Check for intent keywords
            elif any(word in query_lower for word in ["top", "highest", "largest", "best", "lowest", "worst", "unprofitable"]):
                chart_type = "bar"
                intent = "visualization"
            elif any(word in query_lower for word in ["trend", "over time", "change"]):
                chart_type = "line"
                intent = "trend"
            elif any(word in query_lower for word in ["correlation", "relationship", "vs"]):
                chart_type = "scatter"
                intent = "comparison"
            elif any(word in query_lower for word in ["distribution", "breakdown", "share"]):
                chart_type = "pie"
                intent = "visualization"
            else:
                chart_type = "table"
                intent = "aggregation"
            
            # Extract column names from query
            columns_needed = []
            for col in ["Sub-Category", "Customer Name", "Profit", "Sales", "Discount", "Category", "Region", "State", "Ship Mode"]:
                if col.lower() in query_lower or col.replace("-", " ").lower() in query_lower:
                    columns_needed.append(col)
            
            # Fallback plan based on query analysis
            fallback_plan = {
                "intent": intent,
                "steps": ["Parse query", "Extract relevant data", "Aggregate results", "Create visualization"],
                "chart_type": chart_type,
                "columns_needed": columns_needed if columns_needed else ["Profit", "Sales"],
                "reasoning": f"Fallback plan for: {query[:100]}",
                "complexity": "medium"
            }
            logger.log_planner_output(fallback_plan)
            return fallback_plan
        except Exception as e:
            logger.log_error("planner", str(e), {"query": query})
            fallback_plan = {
                "intent": "error",
                "steps": ["Analyze data directly"],
                "chart_type": "table",
                "columns_needed": [],
                "reasoning": f"Error creating plan: {str(e)}",
                "complexity": "simple"
            }
            logger.log_planner_output(fallback_plan)
            return fallback_plan