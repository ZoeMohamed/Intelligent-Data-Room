"""
Integration tests for complete system (Flask API + Streamlit)
"""
import pytest
import pandas as pd
from pathlib import Path


class TestDataLoading:
    """Test data loading functionality"""
    
    def test_sample_data_exists(self):
        """Verify sample data file exists"""
        data_path = Path("data/Sample Superstore.csv")
        assert data_path.exists(), "Sample Superstore.csv should exist"
    
    def test_sample_data_loads(self):
        """Test loading sample dataset"""
        df = pd.read_csv("data/Sample Superstore.csv")
        assert len(df) > 0, "Dataset should have rows"
        assert len(df.columns) > 0, "Dataset should have columns"
        
        # Check expected columns
        expected_cols = ["Sales", "Profit", "Category", "Region"]
        for col in expected_cols:
            assert col in df.columns, f"Column {col} should exist"


class TestPrompts:
    """Test prompts for both Streamlit and Flask API"""
    
    EASY_PROMPTS = [
        "Create a bar chart showing the total Sales and Profit for each Category.",
        "Visualize the distribution of total Sales across different Regions using a pie chart.",
        "Which Customer Segment places the most orders? Show this with a count plot.",
        "Identify the Top 5 States by total Sales using a horizontal bar chart.",
        "How has the total Profit changed over the Years (2018-2021)? Use a line chart.",
    ]
    
    MEDIUM_PROMPTS = [
        "Which Sub-Categories are currently unprofitable on average? Visualize this with a bar chart.",
        "Compare the Sales Trend of different Ship Modes over time using a multi-line chart.",
        "List the Top 10 Customers by total Profit and display them in a bar chart.",
        "Is there a correlation between Discount and Profit? Create a scatter plot to show the relationship.",
        "Calculate and chart the Return Rate (percentage of orders returned) for each Region.",
    ]
    
    def test_easy_prompts_defined(self):
        """Verify easy prompts are defined"""
        assert len(self.EASY_PROMPTS) == 5
    
    def test_medium_prompts_defined(self):
        """Verify medium prompts are defined"""
        assert len(self.MEDIUM_PROMPTS) == 5
