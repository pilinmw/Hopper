"""
Test Conversational Agent

Quick test script for the conversational agent system
"""

import asyncio
import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.chat_agent import ChatAgent
from agents.data_analyzer import DataAnalyzer
import pandas as pd


async def test_chat_agent():
    """Test ChatAgent functionality"""
    print("=" * 60)
    print("Testing ChatAgent")
    print("=" * 60)
    
    agent = ChatAgent()
    
    # Test messages
    test_messages = [
        "Hello, can you help me analyze data?",
        "I only want electronics category",
        "Create a pivot with regions as rows and months as columns",
        "Generate a PPT and PDF report"
    ]
    
    for msg in test_messages:
        print(f"\n👤 User: {msg}")
        response = await agent.process_message(msg)
        print(f"🤖 Agent: {response.message}")
        if response.intent:
            print(f"   Intent: {response.intent.action} (confidence: {response.intent.confidence})")
        if response.quick_actions:
            print(f"   Quick Actions: {response.quick_actions}")


def test_data_analyzer():
    """Test DataAnalyzer functionality"""
    print("\n" + "=" * 60)
    print("Testing DataAnalyzer")
    print("=" * 60)
    
    # Create sample data
    data = {
        'Category': ['Electronics', 'Clothing', 'Electronics', 'Food', 'Electronics'],
        'Region': ['North', 'South', 'North', 'East', 'West'],
        'Sales': [1000, 500, 1500, 300, 1200],
        'Month': ['Jan', 'Jan', 'Feb', 'Feb', 'Mar']
    }
    
    df = pd.DataFrame(data)
    print(f"\nOriginal data: {len(df)} rows")
    print(df.head())
    
    # Create analyzer
    analyzer = DataAnalyzer(df)
    
    # Get summary
    summary = analyzer.get_summary()
    print(f"\nData Summary:")
    print(f"  Rows: {summary['total_rows']}")
    print(f"  Columns: {summary['total_columns']}")
    print(f"  Categories: {list(summary['categories'].keys())}")
    
    # Test filter
    analyzer.apply_filter('Category', 'Electronics')
    print(f"\nAfter filtering (Electronics only): {len(analyzer.df)} rows")
    print(analyzer.df)
    
    # Test suggestions
    suggestions = analyzer.suggest_visualizations()
    print(f"\nVisualization suggestions: {len(suggestions)}")
    for sug in suggestions:
        print(f"  - {sug['type']}: {sug['title']}")


def main():
    """Run all tests"""
    print("\n🧪 SMART DOCUMENT FACTORY - AGENT TESTS")
    print("=" * 60)
    
    # Test Data Analyzer (synchronous)
    test_data_analyzer()
    
    # Test Chat Agent (asynchronous)
    asyncio.run(test_chat_agent())
    
    print("\n" + "=" * 60)
    print("✅ All tests completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
