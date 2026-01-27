"""
Test suite for Planner and Executor agents
"""
import pytest
import pandas as pd
from agents.planner import PlannerAgent
from agents.executor import ExecutorAgent
from utils.memory_manager import ConversationMemory


class TestPlannerAgent:
    """Test cases for Planner Agent"""
    
    @pytest.fixture
    def planner(self):
        """Create planner instance"""
        return PlannerAgent()
    
    @pytest.fixture
    def sample_schema(self):
        """Sample dataset schema"""
        return "Columns: Sales, Profit, Category, Region, Discount"
    
    def test_planner_creates_valid_plan(self, planner, sample_schema):
        """Test that planner creates a valid plan structure"""
        query = "Show total sales by category"
        plan = planner.create_plan(query, sample_schema)
        
        assert "intent" in plan
        assert "steps" in plan
        assert "chart_type" in plan
        assert "columns_needed" in plan
        assert isinstance(plan["steps"], list)


class TestExecutorAgent:
    """Test cases for Executor Agent"""
    
    @pytest.fixture
    def executor(self):
        """Create executor instance"""
        return ExecutorAgent()
    
    @pytest.fixture
    def sample_data(self):
        """Create sample DataFrame"""
        return pd.DataFrame({
            "Category": ["Furniture", "Office", "Technology"] * 10,
            "Sales": [100, 200, 300] * 10,
            "Profit": [20, 40, 60] * 10,
            "Region": ["East", "West", "South"] * 10,
        })
    
    @pytest.fixture
    def sample_plan(self):
        """Sample execution plan"""
        return {
            "intent": "aggregation",
            "steps": ["Group by Category", "Sum Sales"],
            "chart_type": "bar",
            "columns_needed": ["Category", "Sales"],
            "reasoning": "Aggregate sales by category",
        }
    
    def test_executor_returns_result(self, executor, sample_data, sample_plan):
        """Test that executor returns a result"""
        result = executor.execute_plan(sample_plan, sample_data)
        
        assert "success" in result
        assert "data" in result
        assert "chart" in result


class TestMemoryManager:
    """Test cases for Conversation Memory"""
    
    def test_memory_stores_exchanges(self):
        """Test that memory stores exchanges"""
        memory = ConversationMemory()
        memory.add_exchange("test query", "test result")
        
        context = memory.get_context()
        assert len(context) == 1
    
    def test_memory_context_string(self):
        """Test context string generation"""
        memory = ConversationMemory()
        memory.add_exchange("test query", "test result")
        
        context_str = memory.get_context_string()
        assert "test query" in context_str
