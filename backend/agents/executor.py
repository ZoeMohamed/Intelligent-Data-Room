import google.generativeai as genai
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
from dotenv import load_dotenv
from typing import Dict, Any, Optional
from utils.logger import get_logger
import json

load_dotenv()
logger = get_logger()

class ExecutorAgent:
    def __init__(self, model_name: str = 'gemini-2.5-flash'):
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        self.model_name = model_name
        self.model = genai.GenerativeModel(model_name)
        print(f"[EXECUTOR]  Using model: {model_name}")
    
    def execute_plan(self, plan: Dict[str, Any], df: pd.DataFrame) -> Dict[str, Any]:
        # Log input
        logger.log_executor_input(plan, df.shape)
        
        try:
            # Build prompt for Gemini to generate pandas code
            code_prompt = self._build_code_generation_prompt(plan, df)
            
            # Generate pandas code using Gemini
            response = self.model.generate_content(code_prompt)
            code = self._extract_code(response.text)
            
            # Execute the generated code safely
            result_data, result_df = self._execute_pandas_code(code, df)
            
            # Create visualization if needed
            chart = None
            if plan["chart_type"] != "table":
                chart = self._create_visualization(result_df, plan, df)
            
            final_result = {
                "success": True,
                "data": result_data,
                "chart": chart,
                "query_used": code
            }
            
            # Log output
            logger.log_executor_output(final_result)
            return final_result
            
        except Exception as e:
            logger.log_error("executor", str(e), {"plan_intent": plan.get("intent")})
            error_result = {
                "success": False,
                "data": f"Execution error: {str(e)}",
                "chart": None,
                "query_used": None
            }
            logger.log_executor_output(error_result)
            return error_result
    
    def _build_code_generation_prompt(self, plan: Dict[str, Any], df: pd.DataFrame) -> str:
        """Create prompt for Gemini to generate pandas code"""
        
        # Get column info
        columns_info = ", ".join([f"{col} ({dtype})" for col, dtype in df.dtypes.items()])
        sample_data = df.head(3).to_string()
        chart_type = plan.get('chart_type', 'table')
        
        # Special handling for scatter plots
        if chart_type == 'scatter':
            prompt = f"""Generate Python pandas code to prepare data for a SCATTER PLOT.

DATASET INFO:
- Shape: {df.shape[0]} rows, {df.shape[1]} columns
- Columns: {columns_info}

SAMPLE DATA:
{sample_data}

EXECUTION PLAN:
Intent: {plan['intent']}
Columns Needed: {', '.join(plan['columns_needed'])}

REQUIREMENTS FOR SCATTER PLOT:
1. Return RAW DATA POINTS (not aggregated)
2. Select only the two columns needed: {plan['columns_needed']}
3. Remove missing values with .dropna()
4. If more than 5000 rows, sample 5000 random rows
5. Store result in variable 'result'

Example output:
```python
result = df[{plan['columns_needed']}].dropna()
if len(result) > 5000:
    result = result.sample(5000, random_state=42)
```

Generate the code now:"""
        elif chart_type == 'line' and 'trend' in plan.get('intent', '').lower():
            # Multi-series line chart for trends over time
            prompt = f"""Generate Python pandas code for a MULTI-LINE TIME SERIES chart.

DATASET INFO:
- Shape: {df.shape[0]} rows, {df.shape[1]} columns
- Columns: {columns_info}

SAMPLE DATA:
{sample_data}

EXECUTION PLAN:
Intent: {plan['intent']}
Columns Needed: {', '.join(plan['columns_needed'])}

REQUIREMENTS:
1. Extract year/month from 'Order Date' column
2. Group by time period AND category (e.g., Ship Mode)
3. Create a pivot table with time as index, categories as columns
4. Result should have format: time_period | category1 | category2 | category3
5. Store result in variable 'result'

Example output:
```python
import pandas as pd
df['Order Date'] = pd.to_datetime(df['Order Date'])
df['YearMonth'] = df['Order Date'].dt.to_period('M').astype(str)
result = df.pivot_table(values='Sales', index='YearMonth', columns='Ship Mode', aggfunc='sum').reset_index()
result.columns.name = None
```

Generate the code now:"""
        else:
            prompt = f"""Generate Python pandas code to analyze the following dataset.

DATASET INFO:
- Shape: {df.shape[0]} rows, {df.shape[1]} columns
- Columns: {columns_info}

SAMPLE DATA:
{sample_data}

EXECUTION PLAN:
Intent: {plan['intent']}
Steps: {', '.join(plan['steps'])}
Columns Needed: {', '.join(plan['columns_needed'])}
Reasoning: {plan['reasoning']}

REQUIREMENTS:
1. Write ONLY executable Python pandas code
2. Use the variable name 'df' for the DataFrame
3. Store the final result in a variable called 'result'
4. For visualizations, return a DataFrame with 2 columns: category and value (aggregated, max 50 rows)
5. For calculations, return a single numeric value or small DataFrame
6. ALWAYS aggregate data - never return individual row IDs or thousands of rows
7. Keep code simple and efficient
8. Handle missing values gracefully

OUTPUT FORMAT:
Return ONLY the Python code, wrapped in ```python markers.

Example output:
```python
result = df.groupby('Category')['Sales'].sum().reset_index()
```

Generate the code now:"""

        return prompt
    
    def _extract_code(self, response_text: str) -> str:
        """Extract Python code from Gemini response"""
        # Remove markdown code blocks
        code = response_text.strip()
        if "```python" in code:
            code = code.split("```python")[1].split("```")[0]
        elif "```" in code:
            code = code.split("```")[1].split("```")[0]
        
        return code.strip()
    
    def _execute_pandas_code(self, code: str, df: pd.DataFrame) -> tuple:
        """Safely execute generated pandas code"""
        # Create safe execution context
        exec_globals = {
            'df': df,
            'pd': pd,
            'result': None
        }
        
        # Execute code
        exec(code, exec_globals)
        
        # Get result
        result = exec_globals.get('result')
        result_df = None
        
        # Convert to readable format
        if isinstance(result, pd.DataFrame):
            result_df = result.copy()
            if len(result) <= 20:
                formatted = result.to_markdown(index=False) if len(result.columns) <= 5 else result.to_string(index=False)
            else:
                formatted = result.head(20).to_markdown(index=False) if len(result.columns) <= 5 else result.head(20).to_string(index=False)
                formatted += f"\n\n*Showing top 20 of {len(result)} rows*"
            return formatted, result_df
        elif isinstance(result, pd.Series):
            # Convert Series to DataFrame for visualization
            result_df = result.reset_index()
            result_df.columns = ['Category', 'Value']
            formatted = result.head(20).to_string() if len(result) > 20 else result.to_string()
            if len(result) > 20:
                formatted += f"\n\n*Showing top 20 of {len(result)} items*"
            return formatted, result_df
        else:
            # Scalar or simple value
            return f"**Result:** {result:,.2f}" if isinstance(result, (int, float)) else str(result), None
    
    def _create_visualization(
        self, 
        result_df: Optional[pd.DataFrame], 
        plan: Dict[str, Any], 
        df: pd.DataFrame
    ) -> Optional[go.Figure]:
        """Generate Plotly visualization based on result and plan"""
        
        try:
            chart_type = plan.get("chart_type", "bar")
            
            # Use result_df if available, otherwise fall back to aggregating from plan
            if result_df is not None and not result_df.empty:
                data = result_df.copy()
            else:
                # Fallback: use columns from plan
                columns = plan.get("columns_needed", [])
                if not columns or len(columns) < 1:
                    return None
                
                # Prepare data based on plan
                if len(columns) >= 2:
                    data = df.groupby(columns[0])[columns[1]].sum().reset_index()
                elif len(columns) == 1:
                    data = df[columns[0]].value_counts().reset_index()
                    data.columns = [columns[0], 'count']
                else:
                    return None
            
            # Ensure we have at least 2 columns for visualization
            if len(data.columns) < 2:
                return None
            
            # Get column names
            x_col = data.columns[0]
            y_col = data.columns[1]
            
            # Limit data for readability
            if chart_type in ['bar', 'pie'] and len(data) > 20:
                data = data.nlargest(20, y_col) if chart_type == 'bar' else data.nlargest(10, y_col)
            
            # Create chart based on type
            if chart_type == "bar":
                fig = px.bar(
                    data,
                    x=x_col, 
                    y=y_col,
                    title=f"{y_col} by {x_col}",
                    labels={x_col: x_col.replace('_', ' ').title(), 
                           y_col: y_col.replace('_', ' ').title()}
                )
                
            elif chart_type == "line":
                # Check if data has multiple value columns (multi-series)
                if len(data.columns) > 2:
                    # Multi-series line chart
                    fig = go.Figure()
                    x_col = data.columns[0]
                    
                    # Add a line for each series
                    for col in data.columns[1:]:
                        fig.add_trace(go.Scatter(
                            x=data[x_col],
                            y=data[col],
                            mode='lines+markers',
                            name=str(col),
                            line=dict(width=2)
                        ))
                    
                    fig.update_layout(
                        title="Sales Trend by Ship Mode Over Time",
                        xaxis_title=str(x_col).replace('_', ' ').title(),
                        yaxis_title="Sales",
                        hovermode='x unified',
                        height=450,
                        template="plotly_white"
                    )
                else:
                    # Single-series line chart
                    fig = px.line(
                        data,
                        x=x_col,
                        y=y_col,
                        title=f"{y_col} Trend Over {x_col}",
                        markers=True
                    )
                
            elif chart_type == "scatter":
                # For scatter, use the result_df which should contain raw data points
                if result_df is not None and len(result_df.columns) >= 2:
                    plot_data = result_df
                    x_col = plot_data.columns[0]
                    y_col = plot_data.columns[1]
                else:
                    # Fallback: use raw data from original df
                    if len(columns) < 2:
                        return None
                    plot_data = df[columns[:2]].dropna()
                    if len(plot_data) > 5000:
                        plot_data = plot_data.sample(5000)
                    x_col = columns[0]
                    y_col = columns[1]
                
                fig = px.scatter(
                    plot_data,
                    x=x_col,
                    y=y_col,
                    title=f"{y_col} vs {x_col}",
                    trendline="ols",
                    opacity=0.6
                )
                fig.update_traces(marker=dict(size=5))
                
            elif chart_type == "pie":
                fig = px.pie(
                    data,
                    names=x_col,
                    values=y_col,
                    title=f"Distribution of {y_col} by {x_col}"
                )
            else:
                return None
            
            # Enhance layout
            fig.update_layout(
                height=450,
                template="plotly_white",
                showlegend=True
            )
            
            return fig
            
        except Exception as e:
            print(f"Visualization error: {e}")
            logger.log_error("executor", f"Visualization error: {e}", {"chart_type": plan.get("chart_type")})
            return None