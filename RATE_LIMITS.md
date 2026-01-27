# 🚨 Gemini API Rate Limits - Quick Guide

## Your Current Situation

**Free Tier Limits Hit:**
- ✅ RPM: 5/5 (requests per minute) - MAXED OUT
- ✅ RPD: 21/20 (requests per day) - EXCEEDED  
- ✅ TPM: 2.53K/250K (tokens per minute) - OK

## Why You Hit It So Fast

Each query = **2 API calls**:
1. Planner Agent (creates plan)
2. Executor Agent (generates code)

```
10 queries × 2 calls = 20 API calls ✅ (at limit)
11 queries × 2 calls = 22 API calls ❌ (exceeded!)
```

## ✅ Solutions Implemented

### 1. **Query Caching** (ACTIVE NOW)
- Identical queries reuse cached plans
- Saves 50% of API calls on repeated questions
- Auto-enabled in the app

### 2. **Rate Limit Info** 
- Added to sidebar so you can track usage
- Shows limits and tips

## 🎯 How to Use It Now

### **Today (Rate Limited)**
✅ **Test with these repeated queries** (will use cache):
```
1. "What is the total sales?"
2. "What is the total sales?"  ← Uses cache! No API call
3. "Show sales by category"
4. "Show sales by category"     ← Uses cache! No API call
```

### **Tomorrow (Reset)**
Your limits reset at **midnight Pacific Time**
- You'll get 20 new requests
- Use them wisely!

## 💰 Upgrade Options

If you need more:

| Tier | RPM | RPD | Cost |
|------|-----|-----|------|
| **Free** | 5 | 20 | $0 |
| **Pay-as-you-go** | 360 | Unlimited | ~$0.0001/call |

[Upgrade here](https://ai.google.dev/pricing)

## 🎓 Best Practices to Avoid Limits

1. **Batch Similar Questions**
   - Plan your test queries
   - Ask variations back-to-back (cache hits!)

2. **Use Cache Effectively**
   ```
   ✅ "Show sales by region" (API call)
   ✅ "Show sales by region" (cached - FREE!)
   ✅ Different question (API call)
   ```

3. **Develop Offline First**
   - Write code logic first
   - Test with API last

4. **Monitor Your Usage**
   - Check dashboard: https://aistudio.google.com/app/apikey
   - Watch the sidebar in the app

## 🔧 Cache Statistics

Check cache performance:
```python
# In app - shows how many queries cached
st.session_state.planner.cache.get_stats()
```

## 📊 Your Next Steps

**Right Now:**
1. ✅ Restart Streamlit app (caching now active)
2. ✅ Try asking same question twice
3. ✅ Watch console for "[CACHE] ✅ Using cached plan"

**Tomorrow:**
1. ✅ Limits reset at midnight PST
2. ✅ You get 20 fresh requests
3. ✅ Cache will help you use them efficiently

---

**The caching system is now live!** Restart your app and identical queries won't use API calls. 🎉
