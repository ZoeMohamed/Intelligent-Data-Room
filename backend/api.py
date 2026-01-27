from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import os
from agents.planner import PlannerAgent
from agents.executor import ExecutorAgent
from utils.memory_manager import ConversationMemory
from utils.logger import get_logger
from utils.model_config import ModelConfig
from dotenv import load_dotenv
import json
from werkzeug.utils import secure_filename
import tempfile

load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend access

# Initialize agents
default_model = ModelConfig.get_default_model()
planner = PlannerAgent(model_name=default_model)
executor = ExecutorAgent(model_name=default_model)
memory = ConversationMemory()
logger = get_logger(enable_file_logging=True)

# Store uploaded files temporarily
UPLOAD_FOLDER = tempfile.gettempdir()
ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

LOW_INTENT_QUERIES = {'test', 'hi', 'hello', 'hey', 'ok', 'yes', 'no'}
DATA_KEYWORDS = [
    'sales', 'profit', 'revenue', 'customer', 'product', 'order', 'total', 'average',
    'show', 'display', 'chart', 'plot', 'visualize', 'trend', 'compare', 'top', 'bottom',
    'category', 'region', 'state', 'segment', 'discount', 'quantity', 'ship'
]

def is_low_intent_query(query: str) -> bool:
    """Detect too-short or meaningless prompts to avoid unnecessary model calls."""
    query_lower = query.lower().strip()
    if len(query_lower) < 5:
        return True
    if query_lower in LOW_INTENT_QUERIES:
        return True
    return False

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "Intelligent Data Room API"}), 200

@app.route('/api/models', methods=['GET'])
def get_models():
    """Get available AI models"""
    models = ModelConfig.get_available_models()
    return jsonify({"models": models}), 200

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Upload and preview data file"""
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    
    if not allowed_file(file.filename):
        return jsonify({"error": "Invalid file type. Only CSV and XLSX allowed"}), 400
    
    try:
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        # Read file
        if filename.endswith('.csv'):
            df = pd.read_csv(filepath)
        else:
            df = pd.read_excel(filepath)
        
        # Get preview
        preview = {
            "filename": filename,
            "rows": len(df),
            "columns": len(df.columns),
            "column_names": df.columns.tolist(),
            "preview": df.head(10).to_dict(orient='records'),
            "dtypes": df.dtypes.astype(str).to_dict(),
            "filepath": filepath  # Store for later use
        }
        
        return jsonify(preview), 200
        
    except Exception as e:
        logger.log_error("upload", f"Error uploading file: {str(e)}")
        return jsonify({"error": f"Error processing file: {str(e)}"}), 500

@app.route('/api/query', methods=['POST'])
def process_query():
    """Process user query with agents"""
    data = request.get_json()
    
    if not data or 'query' not in data:
        return jsonify({"error": "No query provided"}), 400
    
    query = data.get('query')
    filepath = data.get('filepath')
    model = data.get('model', default_model)

    if not filepath or not os.path.exists(filepath):
        return jsonify({"error": "No data file uploaded or file not found"}), 400
    
    try:
        # Reject low-intent or meaningless queries early
        if is_low_intent_query(query):
            return jsonify({
                "success": False,
                "error": "Please ask a specific question about your data.",
                "suggestions": [
                    "What are the total sales by category?",
                    "Show me the top 10 customers by profit",
                    "Create a scatter plot of discount vs profit",
                    "Which products are unprofitable?"
                ]
            }), 400

        # Read data
        if filepath.endswith('.csv'):
            df = pd.read_csv(filepath)
        else:
            df = pd.read_excel(filepath)

        # Check if the query references data context
        query_lower = query.lower().strip()
        has_data_keyword = any(keyword in query_lower for keyword in DATA_KEYWORDS)
        has_column_name = any(col.lower() in query_lower for col in df.columns)

        if not has_data_keyword and not has_column_name and len(query.split()) < 4:
            return jsonify({
                "success": False,
                "error": "Please mention specific columns or metrics from your data.",
                "available_columns": df.columns.tolist()[:10],
                "suggestions": [
                    "What is the total sales?",
                    "Show profit by region",
                    "List top customers"
                ]
            }), 400
        
        # Get conversation context
        context = memory.get_context_string()
        
        # Create planner with specified model
        current_planner = PlannerAgent(model_name=model)
        current_executor = ExecutorAgent(model_name=model)
        
        # Step 1: Create plan
        # User query: {query}
        schema_info = f"Columns: {', '.join(df.columns.tolist())}"
        plan = current_planner.create_plan(query, schema_info, context)
        # Plan created: {plan}
        
        # Step 2: Execute plan
        result = current_executor.execute_plan(plan, df)
        # Execution result: {result.get('success', False)}
        
        # Store in memory
        memory.add_exchange(query, str(result.get('data', '')))
        
        # Convert chart to JSON if it's a Plotly figure
        chart_data = result.get('chart')
        if chart_data is not None:
            try:
                # Check if it's a Plotly figure and convert to JSON
                if hasattr(chart_data, 'to_json'):
                    import json as json_module
                    chart_data = json_module.loads(chart_data.to_json())
                elif hasattr(chart_data, 'to_dict'):
                    chart_data = chart_data.to_dict()
            except Exception as chart_err:
                logger.log_error("api", f"Error converting chart: {str(chart_err)}")
                chart_data = None
        
        # Prepare response
        response = {
            "success": result.get('success', False),
            "plan": plan,
            "result": result.get('data'),  # executor returns 'data' not 'result'
            "chart": chart_data,
            "error": result.get('error'),
            "model_used": model
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        logger.log_error("api", f"Error processing query: {str(e)}")
        return jsonify({
            "success": False,
            "error": f"Error processing query: {str(e)}"
        }), 500

@app.route('/api/memory/clear', methods=['POST'])
def clear_memory():
    """Clear conversation memory"""
    global memory
    memory = ConversationMemory()
    return jsonify({"message": "Memory cleared"}), 200

@app.route('/api/memory', methods=['GET'])
def get_memory():
    """Get conversation history"""
    context = memory.get_context()
    return jsonify({"context": context}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=False)
