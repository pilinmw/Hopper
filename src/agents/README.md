# Conversational Agent - Quick Start Guide

## 🎯 Overview

Intelligent conversational agent for interactive data analysis through natural language.

---

## 🚀 Quick Start

### 1. Setup Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your OpenAI API key
# OPENAI_API_KEY=sk-your-key-here
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Start API Server

```bash
cd src/api
python main.py

# API runs at: http://localhost:8000
# Docs: http://localhost:8000/api/docs
```

---

## 💬 Using the Chat Agent

### API Workflow

```python
import requests
import json

# 1. Create session
response = requests.post('http://localhost:8000/api/v1/chat/sessions')
session_id = response.json()['session_id']

# 2. Upload data file
files = {'file': open('sales_data.xlsx', 'rb')}
requests.post(
    f'http://localhost:8000/api/v1/chat/sessions/{session_id}/upload',
    files=files
)

# 3. Connect to WebSocket for chat
# Use JavaScript or Python websocket client
```

### WebSocket Chat Example (JavaScript)

```javascript
const ws = new WebSocket(`ws://localhost:8000/api/v1/chat/ws/${sessionId}`);

// Send message
ws.send(JSON.stringify({
    message: "Show me only electronics sales"
}));

// Receive response
ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log(data.message);
    console.log(data.intent);
};
```

---

## 🎨 Example Conversations

### Example 1: Filter Data

```
User: I only want electronics category
Agent: ✅ Filtered to Electronics (420 rows)
      [Preview shown]
      What would you like to do next?
```

### Example 2: Create Pivot Table

```
User: Create a pivot with regions as rows and months as columns
Agent: 📊 Creating pivot table...
      [Preview shown]
      Which format? PPT / PDF / Chart / Excel
```

### Example 3: Generate Multiple Outputs

```
User: Generate PPT and PDF
Agent: 🎨 Generating...
      ✅ PowerPoint created: /path/to/file.pptx
      ✅ PDF created: /path/to/file.pdf
      [Download buttons]
```

---

## 🧩 Architecture

```
ChatAgent (OpenAI)
    ↓
Intent Recognition
    ↓
DataAnalyzer (Pandas)
    ↓
VisualizationEngine
    ↓
Outputs (PPT/PDF/Chart/Excel)
```

---

## 🔧 Components

### ChatAgent
- Natural language understanding via OpenAI
- Intent extraction (filter/pivot/export/query)
- Conversation history management

### DataAnalyzer
- Data filtering by category/value/date
- Pivot table creation
- Aggregations (sum/mean/count)
- Smart visualization suggestions

### VisualizationEngine
- **PPT**: Professional presentations
- **PDF**: Formatted reports
- **Charts**: Interactive Plotly charts
- **Excel**: Pivot tables and raw data

### SessionManager
- Multi-user session management
- Auto-expiration (default 1 hour)
- Context persistence

---

## 📝 Supported Intents

| Intent | Example | Parameters |
|--------|---------|------------|
| **filter** | "Show only electronics" | category, operator, value |
| **pivot** | "Regions as rows, months as columns" | rows, columns, values, aggfunc |
| **visualize** | "Create a bar chart" | chart_type, x, y |
| **export** | "Generate PPT and PDF" | formats[] |
| **query** | "What's in this data?" | - |

---

## 🎯 Intent Parameters

### Filter
```json
{
  "action": "filter",
  "parameters": {
    "column": "Category",
    "value": "Electronics",
    "operator": "equals"
  }
}
```

### Pivot
```json
{
  "action": "pivot",
  "parameters": {
    "rows": ["Region"],
    "columns": ["Month"],
    "values": "Sales",
    "aggfunc": "sum"
  }
}
```

### Export
```json
{
  "action": "export",
  "parameters": {
    "formats": ["ppt", "pdf", "chart", "excel"]
  }
}
```

---

## 🔑 Environment Variables

```bash
# Required
OPENAI_API_KEY=sk-your-key-here

# Optional
OPENAI_MODEL=gpt-4o-mini    # Default model
API_HOST=0.0.0.0            # API host
API_PORT=8000               # API port
SESSION_TIMEOUT=3600        # Session timeout (seconds)
MAX_SESSIONS=100            # Max concurrent sessions
```

---

## 🧪 Testing

### Test ChatAgent

```python
from agents.chat_agent import ChatAgent
import asyncio

agent = ChatAgent()

async def test():
    response = await agent.process_message(
        "I only want electronics",
        context={"categories": {"Category": ["Electronics", "Clothing"]}}
    )
    print(response.message)
    print(response.intent)

asyncio.run(test())
```

### Test DataAnalyzer

```python
from agents.data_analyzer import DataAnalyzer
import pandas as pd

df = pd.DataFrame({
    'Category': ['A', 'B', 'A', 'C'],
    'Sales': [100, 200, 150, 300]
})

analyzer = DataAnalyzer(df)
filtered = analyzer.apply_filter('Category', 'A')
print(filtered)
```

---

## 🚧 Next Steps

- [ ] Complete Web chat UI
- [ ] Add chart customization
- [ ] Implement export history
- [ ] Add more visualization types
- [ ] Enhance intent recognition
- [ ] Add data validation

---

## 📖 API Documentation

Full API docs: http://localhost:8000/api/docs

### Endpoints

- `POST /api/v1/chat/sessions` - Create session
- `POST /api/v1/chat/sessions/{id}/upload` - Upload file
- `WS /api/v1/chat/ws/{id}` - WebSocket chat
- `GET /api/v1/chat/sessions/{id}` - Get session info
- `DELETE /api/v1/chat/sessions/{id}` - Delete session

---

**Status**: ✅ Core components complete  
**Branch**: `feature/conversational-agent`  
**Commit**: `a6319c5`
