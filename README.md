# 🧠 Intelligent Data Room

An AI-powered data analysis application with **Multi-Agent System**. Ask questions about your data in natural language and get intelligent answers with visualizations.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![React](https://img.shields.io/badge/react-18.3+-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-1.31.0-red.svg)

---

## 🎯 What is This?

Instead of writing SQL or pandas code, just ask in plain English:
- "Show me the top 5 customers by profit with a bar chart"
- "Is there a correlation between discount and profit?"
- "Which sub-categories are unprofitable?"

**🤖 Two AI Agents:**
- **Planner Agent** - Analyzes your question, creates execution plan
- **Executor Agent** - Generates Python code, creates visualizations

**💻 Three Ways to Use:**
1. **Backend Only (Streamlit)** - Quick start, perfect for data analysis
2. **Frontend + Backend (React + Flask API)** - Full-featured web app with REST API
3. **API Only** - Deploy Flask API to Render.com for production

---

## 🚀 Quick Start

### ⚡ Option 1: Backend Only (Streamlit)

```bash
# 1. Clone and navigate
git clone https://github.com/yourusername/intelligent-data-room.git
cd intelligent-data-room/backend

# 2. Setup Python environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Add your API key
cp .env.example .env
# Edit .env: GEMINI_API_KEY=your_key_here

# 5. Run!
streamlit run app.py
```

**→ Open http://localhost:8501** 🎉

### 🎨 Option 2: Full Stack (React + Flask API)

**Terminal 1 - Backend API:**
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Add GEMINI_API_KEY to .env
python api.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm install
cp .env.example .env
# Edit .env: VITE_API_URL=http://localhost:5000
npm run dev
```

**→ API: http://localhost:5000**  
**→ Frontend: http://localhost:5173**

### 🌐 Option 3: Deploy to Render.com

See **[backend/DEPLOY.md](backend/DEPLOY.md)** for full deployment guide.

**Quick Deploy:**
1. Push to GitHub
2. Connect to [Render.com](https://render.com)
3. Set root directory: `backend`
4. Start command: `gunicorn api:app --bind 0.0.0.0:$PORT`
5. Add env var: `GEMINI_API_KEY`
6. Deploy!

---

## 📋 Prerequisites

**Backend:**
- Python 3.11+
- Google Gemini API Key ([Get free](https://ai.google.dev/))

**Frontend (optional):**
- Node.js 16+
- npm or yarn

---

## ✨ Features

### 🤖 Intelligent AI System
- **Smart Planning** - Planner analyzes intent and data schema
- **Code Generation** - Executor generates Python/pandas code
- **Transparent** - See the execution plan before results
- **Multi-Model** - Choose from 4 Gemini models

### 📊 Powerful Visualizations
- **Auto-Detection** - Creates charts automatically when needed
- **Multiple Types** - Bar, Line, Scatter, Pie with Plotly
- **Statistical Analysis** - Correlation, trendlines with statsmodels
- **Multi-Series** - Time series with multiple lines

### 💬 Conversational Memory
- **Context Aware** - Remembers last 5 conversations
- **Follow-ups** - "Now show their locations" works!
- **Query Cache** - Reduces API calls by 50%
- **Model Selection** - Switch models to manage rate limits

### 📁 Data Support
- CSV, XLSX files up to 10MB
- Interactive preview
- 9,995-row sample dataset included

---

## 🎯 Sample Queries

### ✅ Easy Level
- "Create a bar chart showing total Sales and Profit for each Category"
- "Visualize distribution of Sales across Regions using a pie chart"
- "Which Customer Segment places the most orders?"
- "Top 5 States by total Sales using horizontal bar chart"
- "How has Profit changed over Years 2018–2021? Use line chart"

### ✅ Medium Level
- "Which Sub-Categories are unprofitable? Visualize with bar chart"
- "Compare Sales Trend of different Ship Modes over time"
- "List Top 10 Customers by Profit in a bar chart"
- "Is there correlation between Discount and Profit? Create scatter plot"

---

## 📖 How to Use

### 1. Upload Data
- **Streamlit**: Click "Browse files" in sidebar
- **React**: Drag and drop or browse
- Supports CSV/XLSX, max 10MB
- Preview your data before analysis

### 2. Ask Questions
Type natural language like:
```
"What are total sales by category?"
"Show top 10 customers"
"Create bar chart of sales by region"
"Visualize profit trend over time"
```

### 3. Get Results
- View agent's execution plan
- See data tables or insights
- Interact with visualizations
- Ask follow-up questions with context

---

## 🔧 Configuration

### Backend Environment (`backend/.env`)

```bash
# Required
GEMINI_API_KEY=your_api_key_here

# Optional - Backup keys to avoid rate limits
GEMINI_API_KEY_2=backup_key_1
GEMINI_API_KEY_3=backup_key_2
```

**Getting Your API Key:**
1. Visit [Google AI Studio](https://ai.google.dev/)
2. Sign in with Google account
3. Create API key
4. Copy into `backend/.env`

### Frontend Environment (`frontend/.env`)

```bash
# Backend API endpoint
VITE_API_URL=http://localhost:8501
VITE_BACKEND_URL=http://localhost:8501
```

### Advanced Settings

**Memory:** Edit `backend/utils/memory_manager.py`
```python
max_history = 5  # Conversation messages to remember
```

**Cache:** Edit `backend/utils/cache.py`
```python
max_cache_size = 50  # Queries to cache
```

**Models:** Choose in UI or edit `backend/utils/model_config.py`
- `gemini-2.5-flash` - Default, fastest
- `gemini-2.5-pro` - Most capable
- `gemini-2.0-flash` - Balanced
- `gemini-2.5-flash-lite` - Lightweight

---

## 🛠️ Tech Stack

### Backend
| Component | Technology |
|-----------|-----------|
| Framework | Streamlit 1.31.0 |
| AI | Google Gemini API |
| Data | Pandas 1.5.3 |
| Visualization | Plotly 5.18.0 |
| Statistics | statsmodels 0.14.6 |
| Testing | pytest 8.4.2 |
| Language | Python 3.11+ |

### Frontend
| Component | Technology |
|-----------|-----------|
| Framework | React 18.3+ |
| Build | Vite 6.0+ |
| Styling | TailwindCSS 4.0+ |
| Markdown | react-markdown |
| Highlighting | rehype-highlight |
| Language | TypeScript 5.0+ |

---

## 📁 Project Structure

```
intelligent-data-room/
│
├── 📂 backend/                    # Python Backend
│   ├── app.py                     # Streamlit app
│   ├── requirements.txt           # Dependencies
│   ├── .env.example              # Config template
│   │
│   ├── 📂 agents/
│   │   ├── planner.py           # Planning agent
│   │   └── executor.py          # Execution agent
│   │
│   ├── 📂 utils/
│   │   ├── cache.py             # Query cache
│   │   ├── logger.py            # Logging
│   │   ├── memory_manager.py    # Context memory
│   │   └── model_config.py      # Model setup
│   │
│   ├── 📂 tests/
│   │   ├── test_setup.py
│   │   ├── test_agents.py
│   │   └── test_integration.py
│   │
│   └── 📂 data/
│       └── Sample Superstore.csv
│
├── 📂 frontend/                   # React Frontend
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   │
│   └── 📂 src/
│       ├── App.tsx
│       ├── 📂 components/
│       ├── 📂 context/
│       └── 📂 assets/
│
├── README.md                      # This file
├── QUICKSTART.md                  # Quick guide
├── SYSTEM_PROMPTS.md             # AI prompts
├── RATE_LIMITS.md                # API limits
└── TESTING_REPORT.md             # Test results
```

---

## 🏗️ Architecture

```
┌─────────────────────────────┐
│    React Frontend (Optional) │
│    Modern UI • TypeScript   │
└──────────┬──────────────────┘
           │ HTTP
           ▼
┌─────────────────────────────┐
│    Streamlit Backend        │
│    Upload • Chat • Charts   │
└──────────┬──────────────────┘
           │
    ┌──────┴──────┐
    │             │
    ▼             ▼
┌─────────┐   ┌─────────┐
│ Planner │──▶│Executor │
│         │   │         │
│ Gemini  │   │ Pandas  │
│ Intent  │   │ Plotly  │
└────┬────┘   └────┬────┘
     │             │
     │   ┌─────┐   │
     └──▶│Cache│◀──┘
         │ Log │
         └─────┘
```

---

## 🧪 Testing

### Backend Tests

```bash
cd backend

# All tests
pytest tests/ -v

# Specific tests
pytest tests/test_agents.py -v

# With coverage
pytest tests/ --cov=. --cov-report=html
```

**Status:** 18/19 tests passing ✅

### Frontend (if using)

```bash
cd frontend
npm run lint
npm test
```

### Manual Testing

Use `backend/data/Sample Superstore.csv` (9,995 rows)

**Try:**
- "Show sales and profit by category as bar chart"
- "Which sub-categories are unprofitable?"
- "Compare sales trends over time"

---

## 🚀 Deployment

### Deploy Backend API to Render.com

**See [backend/DEPLOY.md](backend/DEPLOY.md) for detailed guide.**

**Quick Steps:**
1. Push code to GitHub
2. Go to [Render.com](https://render.com) → New Web Service
3. Connect repository
4. Configure:
   - Root Directory: `backend`
   - Build: `pip install -r requirements.txt`
   - Start: `gunicorn api:app --bind 0.0.0.0:$PORT --workers 2`
5. Environment Variables:
   - `GEMINI_API_KEY=your_key`
6. Deploy! 🚀

**Your API will be at:** `https://your-app.onrender.com`

### Deploy Frontend to Vercel/Netlify

**Vercel:**
```bash
cd frontend
vercel
```

**Netlify:**
- Base: `frontend`
- Build: `npm run build`
- Publish: `dist`
- Env: `VITE_API_URL=https://your-api.onrender.com`

### Test Deployment

```bash
# Test health
curl https://your-app.onrender.com/health

# Test API
cd backend
python test_api.py
```

---

## 🐛 Troubleshooting

### Backend

**"Module not found":**
```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

**"API key not found":**
- Check `backend/.env` exists
- Format: `GEMINI_API_KEY=key` (no quotes)

**"Rate limit exceeded":**
- Add `GEMINI_API_KEY_2`, `GEMINI_API_KEY_3`
- Switch model in UI
- See [RATE_LIMITS.md](RATE_LIMITS.md)

**Port in use:**
```bash
streamlit run app.py --server.port 8502
```

### Frontend

**Can't connect:**
- Check backend runs on `localhost:8501`
- Verify `VITE_API_URL` in `frontend/.env`

**Build errors:**
```bash
rm -rf node_modules
npm install
```

---

## 🤝 Contributing

1. Fork repo
2. Create branch: `git checkout -b feature/name`
3. Commit: `git commit -m 'Add feature'`
4. Push: `git push origin feature/name`
5. Open Pull Request

**Dev Setup:**
```bash
# Backend
cd backend
pip install -r requirements.txt
pytest tests/

# Frontend
cd frontend
npm install
npm run lint
```

---

## 📚 Documentation

- **[QUICKSTART.md](QUICKSTART.md)** - Fast setup
- **[SYSTEM_PROMPTS.md](SYSTEM_PROMPTS.md)** - AI prompts
- **[RATE_LIMITS.md](RATE_LIMITS.md)** - API limits
- **[TESTING_REPORT.md](TESTING_REPORT.md)** - Test results

---

## 📝 License

MIT License - see LICENSE file

---

## 🙏 Acknowledgments

- Google Gemini API
- Streamlit & React communities
- Tableau Superstore dataset

---
**Made with ❤️ by Zo**
