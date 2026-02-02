# Smart Document Factory - Complete User Guide

## 🎯 Overview

Smart Document Factory is an intelligent document processing system with AI-powered conversational analysis.

---

## 🌟 Key Features

### 1. Multi-Format Document Processing
- **Excel** (.xlsx, .xls)
- **CSV** (.csv)
- **Word** (.docx, .doc)  
- **PDF** (text and tables)

### 2. AI Conversational Agent
- Natural language data analysis
- Filter data by category
- Create pivot tables
- Generate visualizations

### 3. Multi-Format Output
- **PowerPoint**: Professional presentations
- **PDF**: Formatted reports
- **Interactive Charts**: Web-based visualizations
- **Excel**: Pivot tables and raw data

### 4. Smart Data Cleaning
- Remove duplicates
- Handle missing values
- Normalize column names
- Detect outliers

### 5. Template System
- Professional
- Modern
- Financial
- Custom branding

---

## 🚀 Quick Start Guide

### Installation

```bash
# Clone repository
git clone https://github.com/pilinmw/Hopper.git
cd Hopper/smart-doc-factory

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add: OPENAI_API_KEY=sk-your-key-here
```

### Usage Methods

#### Method 1: AI Chat Interface (Recommended)

```bash
# 1. Start API server
cd src/api
python main.py

# 2. Open chat interface
open ../web/chat.html
# OR use: python3 -m http.server 8080 (in web/ directory)
```

**Example Conversation:**
```
You: [Upload sales.xlsx]
AI: I see 1,250 rows with categories: Electronics, Clothing, Food
    What would you like to analyze?

You: Show me only electronics
AI: ✅ Filtered to 420 rows
    [Preview shown]

You: Create pivot with regions as rows and months as columns
AI: 📊 Pivot table created
    [Preview shown]
    Which format? PPT / PDF / Chart / Excel

You: PPT and PDF
AI: ✅ Files generated
    [Download buttons]
```

#### Method 2: Web Interface (Simple Upload)

```bash
# Start server
cd src/api
python main.py

# Open browser
open http://localhost:8080  # (use python -m http.server 8080 in web/)
```

#### Method 3: Command Line

```bash
# Basic merge
python src/mergers/excel_merger.py \
  --files "file1.xlsx,file2.csv,file3.pdf" \
  --output "result.xlsx"

# With template and cleaning
python src/mergers/excel_merger.py \
  --files "data1.xlsx,data2.csv" \
  --output "report.xlsx" \
  --template "professional" \
  --clean
```

#### Method 4: Python API

```python
from src.mergers.excel_merger import ExcelMerger
from src.templates.template_engine import TemplateEngine

# Create merger with template
template = TemplateEngine('professional')
merger = ExcelMerger(
    auto_clean=True,
    template_engine=template
)

# Add files and merge
merger.add_files(['sales_q1.xlsx', 'sales_q2.csv'])
merger.merge_to_excel('annual_report.xlsx')
```

---

## 📖 Detailed Guides

### AI Chat Agent Usage

**Supported Commands:**

1. **Filtering**
   - "Show me only electronics"
   - "Filter by region = North"
   - "Only data from 2023"

2. **Pivot Tables**
   - "Create pivot with regions as rows"
   - "Regions as rows, months as columns, sum sales"
   - "Pivot by category and region"

3. **Visualizations**
   - "Create a bar chart"
   - "Show sales trend over time"
   - "Generate pie chart by category"

4. **Export**
   - "Generate PPT"
   - "Create PDF report"
   - "Export to Excel with pivot"
   - "Generate all formats"

### Data Cleaning Options

```python
from src.cleaners.data_cleaner import CleaningConfig

config = CleaningConfig(
    remove_duplicates=True,      # Remove duplicate rows
    handle_nulls=True,            # Fill missing values
    fill_strategy='median',       # mean/median/mode/ffill/bfill
    normalize_names=True,         # Standardize column names
    detect_outliers=True,         # Flag outliers
    outlier_method='iqr'          # iqr/zscore
)
```

### Template Customization

```python
from src.templates.template_engine import TemplateConfig

config = TemplateConfig(
    primary_color="4A90E2",      # Blue
    secondary_color="50C878",    # Green
    accent_color="FFD700",       # Gold
    company_name="Acme Corp"
)
```

---

## 🔧 Configuration

### Environment Variables (.env)

```bash
# Required for AI features
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4o-mini

# API Settings
API_HOST=0.0.0.0
API_PORT=8000

# Session Settings
SESSION_TIMEOUT=3600      # 1 hour
MAX_SESSIONS=100
```

### File Limits

- Max file size: 50MB per file
- Max files per merge: No hard limit (memory dependent)
- Supported formats: .xlsx, .xls, .csv, .docx, .doc, .pdf

---

## 🎨 Examples

### Example 1: Sales Analysis

```python
# Upload quarterly sales files
# Chat: "Show me electronics sales only"
# Chat: "Create pivot by region and month"
# Chat: "Generate PPT with charts"
```

### Example 2: Financial Report

```python
from src.mergers.excel_merger import ExcelMerger
from src.templates.template_engine import TemplateEngine

# Use financial template
template = TemplateEngine('financial')
merger = ExcelMerger(template_engine=template)

merger.add_files([
    'revenue.xlsx',
    'expenses.csv',
    'projections.xlsx'
])

merger.merge_to_excel('financial_report.xlsx')
```

### Example 3: Multi-Source Report

```python
# Merge data from multiple sources
merger = ExcelMerger(auto_clean=True)

merger.add_files([
    'excel_data.xlsx',
    'csv_data.csv',
    'word_tables.docx',
    'pdf_report.pdf'
])

merger.merge_to_excel('combined_report.xlsx')
```

---

## 🐛 Troubleshooting

### Issue: OpenAI API Error

**Solution:**
1. Check API key in `.env` file
2. Verify key is valid at https://platform.openai.com/api-keys
3. Check you have credit balance

### Issue: File Upload Fails

**Solution:**
1. Check file size (< 50MB)
2. Verify file format is supported
3. Check API server is running

### Issue: Charts Not Generating

**Solution:**
1. Ensure proper dependencies: `pip install plotly reportlab`
2. Check output directory permissions
3. Verify data has appropriate columns

---

## 📝 API Documentation

Full API docs: `http://localhost:8000/api/docs`

### Key Endpoints

```
POST   /api/v1/upload          - Upload files
POST   /api/v1/merge           - Merge files
GET    /api/v1/tasks/{id}      - Get task status
GET    /api/v1/download/{id}   - Download result
POST   /api/v1/chat/sessions   - Create chat session
WS     /api/v1/chat/ws/{id}    - WebSocket chat
```

---

## 🤝 Contributing

See `CONTRIBUTING.md` for development guidelines.

---

## 📄 License

MIT License - see `LICENSE` file

---

## 🙏 Support

- Documentation: `/docs`
- Issues: GitHub Issues
- Discussions: GitHub Discussions

---

**Version**: 1.0.0  
**Last Updated**: 2026-02-02
