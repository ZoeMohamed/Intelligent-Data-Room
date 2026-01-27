# 📡 API Documentation

## Base URL

**Local Development:** `http://localhost:5000`  
**Production:** `https://your-app.onrender.com`

---

## Authentication

Currently, the API uses environment variables for AI model authentication. No user authentication is required for API endpoints.

**Required Environment Variable:**
```
GEMINI_API_KEY=your_google_gemini_api_key
```

---

## Endpoints

### 1. Health Check

Check if the API is running.

**Endpoint:** `GET /health`

**Response:**
```json
{
  "status": "healthy",
  "service": "Intelligent Data Room API"
}
```

**Example:**
```bash
curl https://your-app.onrender.com/health
```

---

### 2. Get Available Models

Get list of available AI models.

**Endpoint:** `GET /api/models`

**Response:**
```json
{
  "models": [
    "gemini-2.5-flash",
    "gemini-2.5-pro",
    "gemini-2.0-flash",
    "gemini-2.5-flash-lite"
  ]
}
```

**Example:**
```bash
curl https://your-app.onrender.com/api/models
```

---

### 3. Upload Data File

Upload CSV or XLSX file for analysis.

**Endpoint:** `POST /api/upload`

**Request:**
- Content-Type: `multipart/form-data`
- Body: `file` (CSV or XLSX file, max 10MB)

**Response:**
```json
{
  "filename": "sales_data.csv",
  "rows": 9994,
  "columns": 21,
  "column_names": ["Order ID", "Sales", "Profit", ...],
  "preview": [
    {"Order ID": "CA-2018-100001", "Sales": 261.96, ...},
    ...
  ],
  "dtypes": {
    "Order ID": "object",
    "Sales": "float64",
    ...
  },
  "filepath": "/tmp/sales_data.csv"
}
```

**Example:**
```bash
curl -X POST https://your-app.onrender.com/api/upload \
  -F "file=@data.csv"
```

**JavaScript Example:**
```javascript
const formData = new FormData();
formData.append('file', fileInput.files[0]);

const response = await fetch('https://your-app.onrender.com/api/upload', {
  method: 'POST',
  body: formData
});

const data = await response.json();
console.log(`Uploaded: ${data.rows} rows, ${data.columns} columns`);
```

---

### 4. Process Query

Ask a question about your data using natural language.

**Endpoint:** `POST /api/query`

**Request:**
- Content-Type: `application/json`
- Body:
  ```json
  {
    "query": "Show me the top 5 customers by profit",
    "filepath": "/tmp/sales_data.csv",
    "model": "gemini-2.5-flash"
  }
  ```

**Parameters:**
- `query` (required): Natural language question
- `filepath` (required): Path from upload response
- `model` (optional): AI model to use (default: gemini-2.5-flash)

**Response:**
```json
{
  "success": true,
  "plan": {
    "intent": "Find top customers by profit",
    "steps": ["Sort by profit", "Take top 5"],
    "visualization": "bar_chart"
  },
  "result": "| Customer Name | Total Profit |\n|---------------|-------------|\n| ...",
  "chart": {
    "type": "bar",
    "data": {...},
    "layout": {...}
  },
  "model_used": "gemini-2.5-flash"
}
```

**Example:**
```bash
curl -X POST https://your-app.onrender.com/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the total sales by category?",
    "filepath": "/tmp/sales_data.csv",
    "model": "gemini-2.5-flash"
  }'
```

**JavaScript Example:**
```javascript
const response = await fetch('https://your-app.onrender.com/api/query', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    query: 'Show top 5 products by sales',
    filepath: uploadedFilePath,
    model: 'gemini-2.5-flash'
  })
});

const data = await response.json();
if (data.success) {
  console.log('Result:', data.result);
  if (data.chart) {
    console.log('Chart data:', data.chart);
  }
}
```

---

### 5. Clear Memory

Clear conversation history/context.

**Endpoint:** `POST /api/memory/clear`

**Response:**
```json
{
  "message": "Memory cleared"
}
```

**Example:**
```bash
curl -X POST https://your-app.onrender.com/api/memory/clear
```

---

### 6. Get Memory

Get current conversation history/context.

**Endpoint:** `GET /api/memory`

**Response:**
```json
{
  "context": "Previous: User asked 'top 5 customers', Result: ..."
}
```

**Example:**
```bash
curl https://your-app.onrender.com/api/memory
```

---

## Error Responses

All endpoints return error responses in this format:

```json
{
  "error": "Error message description"
}
```

**Common Error Codes:**
- `400` - Bad Request (missing parameters)
- `404` - Not Found (endpoint doesn't exist)
- `500` - Internal Server Error (processing failed)

---

## Usage Flow

### Typical workflow:

1. **Upload data file**
   ```bash
   POST /api/upload
   # Get filepath from response
   ```

2. **Ask questions**
   ```bash
   POST /api/query
   # Use filepath from step 1
   # Get results and charts
   ```

3. **Ask follow-up questions**
   ```bash
   POST /api/query
   # Memory maintains context
   ```

4. **Clear memory (optional)**
   ```bash
   POST /api/memory/clear
   ```

---

## Rate Limits

The API uses Google Gemini API which has these limits:

- **Free Tier:** 5 requests/minute, 20 requests/day per model
- **To handle limits:**
  - Add multiple API keys (`GEMINI_API_KEY_2`, `GEMINI_API_KEY_3`)
  - Switch between models
  - Cache queries (built-in)

See [RATE_LIMITS.md](../RATE_LIMITS.md) for details.

---

## CORS

CORS is enabled for all origins in development. For production, you may want to configure specific allowed origins in `api.py`:

```python
CORS(app, origins=["https://your-frontend-domain.com"])
```

---

## Testing

### Run Test Suite

```bash
cd backend
python test_api.py
```

### Manual Testing

```bash
# Health check
curl http://localhost:5000/health

# Models
curl http://localhost:5000/api/models

# Upload (replace with your file)
curl -X POST http://localhost:5000/api/upload \
  -F "file=@data/Sample Superstore.csv"

# Query
curl -X POST http://localhost:5000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Show sales by category", "filepath": "/tmp/sample.csv"}'
```

---

## Examples

### React Frontend Integration

```typescript
// Upload file
const uploadFile = async (file: File) => {
  const formData = new FormData();
  formData.append('file', file);
  
  const res = await fetch(`${API_URL}/api/upload`, {
    method: 'POST',
    body: formData
  });
  
  return await res.json();
};

// Send query
const sendQuery = async (query: string, filepath: string) => {
  const res = await fetch(`${API_URL}/api/query`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query, filepath })
  });
  
  return await res.json();
};

// Usage
const data = await uploadFile(selectedFile);
const result = await sendQuery("Show top 5 customers", data.filepath);
```

### Python Client

```python
import requests

API_URL = "http://localhost:5000"

# Upload
with open('data.csv', 'rb') as f:
    files = {'file': f}
    response = requests.post(f"{API_URL}/api/upload", files=files)
    filepath = response.json()['filepath']

# Query
payload = {
    "query": "What are the total sales?",
    "filepath": filepath
}
response = requests.post(f"{API_URL}/api/query", json=payload)
print(response.json()['result'])
```

---

## Support

For issues or questions:
- [GitHub Issues](https://github.com/yourusername/intelligent-data-room/issues)
- [API Documentation](API.md)
- [Deployment Guide](DEPLOY.md)
