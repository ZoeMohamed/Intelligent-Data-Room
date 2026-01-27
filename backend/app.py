import streamlit as st
import pandas as pd
import time
from agents.planner import PlannerAgent
from agents.executor import ExecutorAgent
from utils.memory_manager import ConversationMemory
from utils.logger import get_logger
from utils.model_config import ModelConfig

st.set_page_config(page_title="Intelligent Data Room", page_icon="", layout="wide")

# Initialize
if 'planner' not in st.session_state:
    default_model = ModelConfig.get_default_model()
    st.session_state.planner = PlannerAgent(model_name=default_model)
    st.session_state.executor = ExecutorAgent(model_name=default_model)
    st.session_state.memory = ConversationMemory()
    st.session_state.messages = []
    st.session_state.logger = get_logger(enable_file_logging=True)
    st.session_state.current_model = default_model

# Sidebar
with st.sidebar:
    st.header("️ Configuration")
    
    # Model Selection
    st.subheader(" AI Model")
    available_models = ModelConfig.get_available_models()
    
    selected_model = st.selectbox(
        "Choose Model",
        options=list(available_models.keys()),
        format_func=lambda x: available_models[x],
        index=list(available_models.keys()).index(st.session_state.get('current_model', ModelConfig.get_default_model())),
        help="Different models have different rate limits and capabilities"
    )
    
    # Update model if changed
    if selected_model != st.session_state.get('current_model'):
        with st.spinner("Switching model..."):
            st.session_state.planner = PlannerAgent(model_name=selected_model)
            st.session_state.executor = ExecutorAgent(model_name=selected_model)
            st.session_state.current_model = selected_model
            st.success(f" Switched to {ModelConfig.get_model_info(selected_model)['name']}")
            st.rerun()
    
    # Show current model info
    model_info = ModelConfig.get_model_info(selected_model)
    st.caption(f" **Limits:** {model_info['limits']}")
    st.caption(f"ℹ️ {model_info['description']}")
    
    st.divider()
    st.header(" Upload Data")
    uploaded = st.file_uploader("CSV/XLSX (Max 10MB)", type=['csv', 'xlsx'])
    
    if uploaded:
        # File size validation (10MB = 10 * 1024 * 1024 bytes)
        MAX_FILE_SIZE = 10 * 1024 * 1024
        
        if uploaded.size > MAX_FILE_SIZE:
            st.error(f" File size ({uploaded.size / 1024 / 1024:.2f}MB) exceeds 10MB limit")
        else:
            try:
                df = pd.read_csv(uploaded) if uploaded.name.endswith('.csv') else pd.read_excel(uploaded)
                st.session_state.data = df
                st.success(f" {len(df)} rows loaded ({uploaded.size / 1024:.2f}KB)")
                with st.expander("Preview"):
                    st.dataframe(df.head())
                    st.caption(f"Columns: {', '.join(df.columns.tolist()[:5])}{'...' if len(df.columns) > 5 else ''}")
            except Exception as e:
                st.error(f" Error loading file: {e}")
    
    # Rate limit info
    st.divider()
    with st.expander("ℹ️ API Usage Tips"):
        st.caption("**Rate Limits (Free Tier):**")
        st.caption("• Gemini Flash: 5 RPM, 20 RPD")
        st.caption("• Gemini Pro: 2 RPM, 10 RPD")
        st.caption("• Gemini Lite: 10 RPM, 40 RPD")
        st.caption("")
        st.caption(" **Caching enabled** to save API calls!")
        st.caption(" **Switch models** if you hit limits!")

# Main
st.title(" Intelligent Data Room")

if 'data' not in st.session_state:
    st.info(" Upload data to start")
else:
    # Display chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            if msg.get("chart"):
                st.plotly_chart(msg["chart"], use_container_width=True)
    
    # Chat input
    if query := st.chat_input("Ask about your data..."):
        # Validate query
        query_lower = query.lower().strip()
        
        # Check for too short or meaningless queries
        if len(query) < 5 or query_lower in ['test', 'hi', 'hello', 'hey', 'ok', 'yes', 'no']:
            st.session_state.messages.append({"role": "user", "content": query})
            with st.chat_message("user"):
                st.write(query)
            
            with st.chat_message("assistant"):
                st.warning("️ Please ask a specific question about your data.")
                st.info("""
**Try asking questions like:**
- "What are the total sales by category?"
- "Show me the top 10 customers by profit"
- "Create a scatter plot of discount vs profit"
- "Which products are unprofitable?"
                """)
            
            st.session_state.messages.append({
                "role": "assistant", 
                "content": "Please ask a more specific question about your data."
            })
            st.stop()
        
        # Check if query is data-related
        data_keywords = ['sales', 'profit', 'revenue', 'customer', 'product', 'order', 'total', 'average', 
                        'show', 'display', 'chart', 'plot', 'visualize', 'trend', 'compare', 'top', 'bottom',
                        'category', 'region', 'state', 'segment', 'discount', 'quantity', 'ship']
        
        has_data_keyword = any(keyword in query_lower for keyword in data_keywords)
        has_column_name = any(col.lower() in query_lower for col in st.session_state.data.columns)
        
        if not has_data_keyword and not has_column_name and len(query.split()) < 4:
            st.session_state.messages.append({"role": "user", "content": query})
            with st.chat_message("user"):
                st.write(query)
            
            with st.chat_message("assistant"):
                st.warning("️ I'm not sure what you're asking about. Please mention specific columns or metrics.")
                st.info(f"""
**Available columns in your data:**
{', '.join(st.session_state.data.columns.tolist()[:10])}

**Example questions:**
- "What is the total sales?"
- "Show profit by region"
- "List top customers"
                """)
            
            st.session_state.messages.append({
                "role": "assistant",
                "content": "Please ask a question that mentions specific data columns or metrics."
            })
            st.stop()
        
        # User message
        st.session_state.messages.append({"role": "user", "content": query})
        with st.chat_message("user"):
            st.write(query)
        
        # Assistant response
        with st.chat_message("assistant"):
            start_time = time.time()
            
            with st.spinner(" Planning..."):
                schema = st.session_state.data.dtypes.to_string()
                history = st.session_state.memory.get_context_string()
                plan = st.session_state.planner.create_plan(query, schema, history)
                
                with st.expander(" View Plan"):
                    st.json(plan)
            
            with st.spinner("️ Executing..."):
                result = st.session_state.executor.execute_plan(plan, st.session_state.data)
                execution_time = time.time() - start_time
                
                # Log summary
                st.session_state.logger.log_interaction_summary(query, plan, result, execution_time)
                
                if result["success"]:
                    st.write(result["data"])
                    if result["chart"]:
                        st.plotly_chart(result["chart"], use_container_width=True)
                    
                    # Save to memory
                    st.session_state.memory.add_exchange(query, plan, result["data"])
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": result["data"],
                        "chart": result["chart"]
                    })
                else:
                    st.error(result["data"])