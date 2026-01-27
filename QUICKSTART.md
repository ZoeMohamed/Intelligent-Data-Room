# 🚀 Quick Start Guide

## Choose Your Setup

### Option 1: Backend Only (Recommended for Quick Start)

```bash
# 1. Navigate to backend
cd backend

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY

# 5. Run the application
streamlit run app.py
```

Visit: http://localhost:8501

---

### Option 2: Full Stack (React Frontend + Backend)

**Terminal 1 - Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
streamlit run app.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

Visit:
- Frontend: http://localhost:5173
- Backend: http://localhost:8501

---

## Getting Your API Key

1. Visit [Google AI Studio](https://ai.google.dev/)
2. Sign in with your Google account
3. Click "Get API Key"
4. Create a new API key
5. Copy and paste into `backend/.env`

---

## Sample Queries to Try

Once running, try these queries:

✅ **Easy:**
- "Create a bar chart showing total Sales and Profit for each Category"
- "Which Customer Segment places the most orders?"
- "Show the Top 5 States by total Sales"

✅ **Medium:**
- "Which Sub-Categories are unprofitable? Show with a bar chart"
- "Compare Sales Trend of different Ship Modes over time"
- "Is there a correlation between Discount and Profit?"

---

## Troubleshooting

**"Module not found" error:**
```bash
cd backend
source venv/bin/activate  # or: source ../.venv311/bin/activate
pip install -r requirements.txt
```

**"API key not found" error:**
- Check `backend/.env` file exists
- Verify GEMINI_API_KEY is set correctly
- No quotes needed around the key

**Port already in use:**
```bash
streamlit run app.py --server.port 8502
```

---

For detailed documentation, see [README.md](README.md)
