# Web Interface

Modern web interface for Smart Document Factory.

## 🚀 Quick Start

### 1. Start Backend API
```bash
cd src/api
python main.py
```

Backend will run at: `http://localhost:8000`

### 2. Open Web Interface
```bash
# Option 1: Open directly in browser
open web/index.html

# Option 2: Use Python HTTP server (recommended)
cd web
python3 -m http.server 8080
# Then visit: http://localhost:8080
```

---

## ✨ Features

- **Drag & Drop Upload** - Easy file selection
- **Multiple File Support** - Excel, CSV, Word, PDF
- **Template Selection** - 3 professional templates
- **Data Cleaning** - Auto-clean toggle
- **Real-time Progress** - Upload and processing feedback
- **Instant Download** - One-click result download

---

## 🎨 Design

- Modern glassmorphism UI
- Gradient backgrounds
- Smooth animations
- Fully responsive
- Mobile-friendly

---

## 📁 Structure

```
web/
├── index.html        # Main page
├── css/
│   └── main.css      # Styles
└── js/
    ├── api.js        # API communication
    ├── upload.js     # File upload logic
    └── app.js        # Main application
```

---

## 🔧 Configuration

Edit `js/api.js` to change API URL:
```javascript
const API_BASE_URL = 'http://localhost:8000/api/v1';
```

---

## ⚙️ How It Works

1. User uploads files via drag & drop or browse
2. Files are validated (type and size)
3. Click "Merge Files" to start
4. Files uploaded to backend API
5. Backend processes and merges
6. Progress bar shows status
7. Download button appears when complete
8. Click to download merged Excel file

---

## 🌐 Browser Support

- Chrome ✅
- Safari ✅
- Firefox ✅
- Edge ✅

---

## 📝 Notes

- Requires backend API to be running
- Maximum 50MB per file
- Supports up to 10 files per merge
- Results cleared on page refresh
