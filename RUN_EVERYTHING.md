# 🚀 Vector - Run Everything (5 Minutes)

## Step 1: Start Backend (Terminal 1)

```bash
cd Agents

# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the server
python main.py
```

**Wait for**: `Uvicorn running on http://0.0.0.0:8000`

---

## Step 2: Start Frontend (Terminal 2)

```bash
cd frontend

npm run dev
```

**Wait for**: `Local: http://localhost:5173`

---

## Step 3: Open in Browser

```
http://localhost:5173
```

You'll see:
- ✅ Beautiful landing page
- ✅ Navigation bar (Home, Test Runner, History)
- ✅ Animated floating lines background

---

## Step 4: Trigger a Test

1. Click **"Test Runner"** in navigation
2. See form with sample data pre-filled:
   - Repository: `api-service`
   - URL: `https://github.com/company/api-service`
   - Commit SHA: (auto-generated)
   - Message: `Add new API endpoints with validation`
3. Click **"▶️ Run Tests"** button

---

## Step 5: Watch Results Appear

As the backend processes, you'll see:

```
⏳ Start
  ↓
🔗 GitHub Agent (detect files) - ~500ms
  ↓
🧠 Code Agent (analyze APIs) - ~2s
  ↓
🧪 Test Generator (create tests) - ~500ms
  ↓
⚙️  Test Executor (run tests) - ~5-10s
  ↓
🔍 Failure Analyzer (if failures) - ~500ms
  ↓
📊 Report Generator (final report) - ~100ms
  ↓
✅ Complete (Results displayed)
```

**Total time**: ~10-15 seconds

---

## Step 6: See Results

After completion, view:

### Summary Card
- Repository name & commit
- Overall status (✅ Completed)
- Timestamp

### Statistics
- Total tests: **16**
- Passed: **14** ✓ (green)
- Failed: **2** ✗ (red)
- Success rate: **87.5%** (violet)

### Tested Endpoints
```
POST /users       [🔐 Auth Required]
GET /users/{id}   [🔐 Auth Required]
```

### Failures & Fixes
```
⚠️ [HIGH] [NEGATIVE] POST /users - Missing email

Error: Internal Server Error - Null check missing for user.email

Root Cause: Null pointer exception in validation layer

💡 Fix: Add null check: if not user.email: raise ValueError('Email required')

File: routes/users.py : 42
```

### Full Report
```markdown
# Vector API Testing Report

**Commit**: abc123d - Add new API endpoints with validation
**Repository**: api-service
**Date**: ...

## Summary
- **Total Tests**: 16
- **Passed**: 14 ✓
- **Failed**: 2 ✗
- **Success Rate**: 87.5%

## Analyzed Endpoints
- `POST /users`
- `GET /users/{id}`

## Failures & Fixes
[detailed failures...]
```

Copy the report markdown to create PR comments, docs, or email updates!

---

## Step 7: Check History

1. Click **"History"** in navigation
2. See all past test runs
3. Click any execution to see details
4. History auto-refreshes every 5 seconds

---

## 📊 Real Example Output

```
Webhook ID: test-1710000000000
Repository: api-service
Commit: abc123d

Total Tests: 16
├─ Passed: 14 ✓
├─ Failed: 2 ✗
└─ Success Rate: 87.5%

Endpoints Tested:
├─ POST /users (auth required)
├─ GET /users/{id} (auth required)
└─ PUT /users/{id} (auth required)

Failures Found:
1. [NEGATIVE] POST /users - Missing email
   └─ Root cause: Null check missing
   └─ Fix: Add validation

2. [EDGE CASE] POST /users - Empty email
   └─ Root cause: Input validation too loose
   └─ Fix: Add email format validation
```

---

## 🔧 Troubleshooting

### "Cannot connect to backend"
```bash
# Check backend is running
curl http://localhost:8000

# Should return JSON with API info
# If not, check Terminal 1 logs
```

### "Frontend won't load"
```bash
# Check frontend is running
# http://localhost:5173 in browser

# If not, check Terminal 2 logs
# npm run dev errors
```

### "Tests don't run"
```bash
# Check backend logs for errors
# Look at Terminal 1 output

# Try backend directly:
curl -X POST http://localhost:8000/pipeline/test-run \
  -H "Content-Type: application/json" \
  -d '{
    "webhook_id": "test-123",
    "repo_name": "my-api",
    "repo_url": "https://github.com/user/repo",
    "commit_sha": "abc123",
    "commit_message": "test"
  }'
```

### "Results not updating"
```bash
# Check browser console (F12)
# Look for JavaScript errors

# Manually check backend:
curl http://localhost:8000/pipeline/executions/test-123
```

---

## 📝 Optional: Test Backend Directly

Test the pipeline without frontend (see all agent output):

```bash
cd Agents
python demo.py
```

Output shows each agent processing:
```
🚀 STARTING VECTOR PIPELINE: demo-webhook-001

🔗 [GITHUB AGENT] Processing webhook: demo-webhook-001
   ✓ Found 2 changed files (62 lines added)

🧠 [CODE AGENT] Analyzing 1 files...
   ✓ Analyzed 2 endpoints
   ✓ Auth: Bearer token required for all endpoints

🧪 [TEST GENERATOR] Generating test cases for 2 endpoints...
   ✓ Generated 16 test cases

⚙️  [TEST EXECUTOR] Running 16 tests...
   ✓ Tests completed: 14 passed, 2 failed

🔍 [FAILURE ANALYZER] Analyzing 2 failures...
   ⚠️  [HIGH] [NEGATIVE] POST /users - Missing email
       Root cause: Null pointer exception in validation layer
       Fix: Add null check: if not user.email: raise ValueError(...)

📊 [REPORT GENERATOR] Creating reports...
   ✓ Reports generated

✅ PIPELINE COMPLETED

📊 Results:
   Tests Run: 16
   Passed: 14 ✓
   Failed: 2 ✗
   Success Rate: 87.5%
```

---

## 🎯 You're Ready!

Everything is set up and working. The platform is:

✅ **Backend** - LangGraph pipeline ready
✅ **API** - Webhooks & REST endpoints ready
✅ **Frontend** - Test runner & history ready
✅ **Integration** - All connected & working

## Next Steps

### Immediate (Now)
- [ ] Run both services
- [ ] Trigger a test from frontend
- [ ] Watch results populate
- [ ] Check execution history

### Short Term (Today)
- [ ] Read `Agents/ARCHITECTURE.md`
- [ ] Read `FRONTEND_UPDATES.md`
- [ ] Understand the 6-agent flow

### Medium Term (This Week)
- [ ] Add custom LLM keys (OpenAI, Gemini)
- [ ] Modify test types in `Agents/nodes.py`
- [ ] Customize test case generation
- [ ] Connect to real GitHub webhooks

### Long Term (Production)
- [ ] Add database for persistence
- [ ] Deploy backend to cloud
- [ ] Deploy frontend CDN
- [ ] Set up monitoring & alerts
- [ ] Integrate GitHub, Slack, email

---

## 🎉 Success Indicators

You'll know everything works when:

✅ Frontend loads at http://localhost:5173
✅ Can navigate between Home, Test Runner, History
✅ Form in Test Runner pre-fills automatically
✅ Run Tests button starts the pipeline
✅ Results appear and update in real-time
✅ Can view all past executions in History
✅ Backend logs show all 6 agents processing
✅ Full markdown report displays

---

## 📞 Getting Help

**Read these in order:**
1. `Agents/QUICKSTART.md` - Quick start (you're reading it!)
2. `Agents/ARCHITECTURE.md` - How it all works
3. `FRONTEND_UPDATES.md` - Frontend integration
4. `Agents/README.md` - Complete API reference

**Or test directly:**
- Backend test: `python Agents/demo.py`
- API docs: http://localhost:8000/docs (Swagger UI)

---

**Ready? Let's go!** 🚀

```bash
# Terminal 1
cd Agents && python main.py

# Terminal 2
cd frontend && npm run dev

# Browser
http://localhost:5173 → "Test Runner" → "Run Tests"
```

Enjoy your new AI-powered API testing platform! 🎊
