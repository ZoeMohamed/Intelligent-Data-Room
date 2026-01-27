# 🚀 Deploying to Render.com

## Quick Deploy

### Option 1: One-Click Deploy

1. Push your code to GitHub
2. Go to [Render.com](https://render.com)
3. Click "New +" → "Web Service"
4. Connect your GitHub repository
5. Configure:
   - **Name**: `intelligent-data-room-api`
   - **Root Directory**: `backend`
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn api:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120`
6. Add Environment Variables:
   - `GEMINI_API_KEY` = your_api_key
   - `GEMINI_API_KEY_2` = backup_key (optional)
   - `GEMINI_API_KEY_3` = backup_key (optional)
7. Click "Create Web Service"

### Option 2: Using render.yaml (Blueprint)

1. Push code to GitHub with `backend/render.yaml`
2. Go to Render Dashboard
3. Click "New +" → "Blueprint"
4. Connect repository
5. Select `backend/render.yaml`
6. Add environment variables in dashboard
7. Deploy!

---

## API Endpoints

Once deployed, your API will be available at: `https://your-app-name.onrender.com`

### Available Endpoints:

**Health Check**
```
GET /health
```

**Get Available Models**
```
GET /api/models
```

**Upload Data File**
```
POST /api/upload
Content-Type: multipart/form-data
Body: file (CSV or XLSX)
```

**Process Query**
```
POST /api/query
Content-Type: application/json
Body: {
  "query": "Show top 5 customers",
  "filepath": "/tmp/data.csv",
  "model": "gemini-2.5-flash"
}
```

**Clear Memory**
```
POST /api/memory/clear
```

**Get Memory**
```
GET /api/memory
```

---

## Frontend Integration

Update your frontend `.env`:

```bash
VITE_API_URL=https://your-app-name.onrender.com
VITE_BACKEND_URL=https://your-app-name.onrender.com
```

---

## Testing Deployment

### Test Health Check
```bash
curl https://your-app-name.onrender.com/health
```

### Test Upload
```bash
curl -X POST https://your-app-name.onrender.com/api/upload \
  -F "file=@data.csv"
```

### Test Query
```bash
curl -X POST https://your-app-name.onrender.com/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Show total sales by category",
    "filepath": "/tmp/data.csv"
  }'
```

---

## Troubleshooting

### Build Fails

Check logs in Render dashboard. Common issues:
- Missing dependencies in `requirements.txt`
- Python version mismatch (check `runtime.txt`)

### API Not Responding

- Check health endpoint: `/health`
- Verify environment variables are set
- Check logs for errors

### CORS Errors

Flask-CORS is already configured. If issues persist:
- Verify frontend URL is correct
- Check browser console for specific errors

---

## Cost & Performance

**Free Tier:**
- 750 hours/month free
- Spins down after 15min inactivity
- First request after spin-down takes ~30s

**Paid Tier ($7/month):**
- Always running
- Better performance
- Custom domains

---

## Monitoring

Access logs in Render Dashboard:
- Build logs
- Deploy logs
- Application logs
- Metrics

---

## Updating Deployment

1. Push changes to GitHub
2. Render auto-deploys from main branch
3. Monitor deployment in dashboard

Or manually:
- Go to Render Dashboard
- Click "Manual Deploy" → "Clear build cache & deploy"

---

## Environment Variables

Set in Render Dashboard → Environment:

```
GEMINI_API_KEY=your_key_here
GEMINI_API_KEY_2=backup_key
GEMINI_API_KEY_3=backup_key
PORT=10000 (auto-set by Render)
```

---

## Need Help?

- [Render Docs](https://render.com/docs)
- [Render Community](https://community.render.com)
- [GitHub Issues](https://github.com/yourusername/intelligent-data-room/issues)
