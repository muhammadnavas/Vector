# Frontend Updates - Vector LangGraph Integration

## 🎯 What Changed

The React frontend now fully integrates with the LangGraph backend pipeline. Three new pages have been added with complete backend communication.

## 📁 New Files Created

### Services
- `src/services/api.js` - API client that communicates with the backend

### Pages/Components
- `src/style/TestRunner.jsx` - Trigger tests and view results
- `src/style/TestRunner.css` - TestRunner styling

- `src/style/ExecutionHistory.jsx` - View past test execution history
- `src/style/ExecutionHistory.css` - ExecutionHistory styling

### Updated Files
- `src/App.jsx` - Added routing and page navigation
- `src/style/Header.jsx` - Made navigation functional with page switching

---

## 🚀 How to Use

### Start Frontend
```bash
cd frontend
npm run dev
```

Frontend runs at: **http://localhost:5173**

### Start Backend (in separate terminal)
```bash
cd Agents
python main.py
```

Backend runs at: **http://localhost:8000**

---

## 📄 Page Structure

### Home Page
- Landing page explaining Vector
- Shows 6 core components
- Call-to-action buttons link to Test Runner

**Route**: `http://localhost:5173/` (or click Home in nav)

### Test Runner
- Form to trigger test runs
  - Repository name
  - Repository URL
  - Commit SHA
  - Commit message
- Live result display as tests run
  - Summary statistics (passed/failed/success rate)
  - Tested endpoints list
  - Failure details with suggested fixes
  - Full markdown report

**Route**: Click "Test Runner" in nav or click "Run Tests" button

**Features**:
- Polls backend for execution status every 1 second
- Auto-populates with sample data
- Shows real-time progress

### Execution History
- List of all past test runs (left panel)
- Click to view details (right panel)
- Shows:
  - Test summary statistics
  - Endpoints that were tested
  - Execution timestamp
  - All failure details

**Route**: Click "History" in nav

**Features**:
- Auto-refreshes every 5 seconds
- Shows webhook IDs
- Persistent history lookup

---

## 🔌 API Integration

### Services (`src/services/api.js`)

```javascript
triggerTestRun(payload)
  - POST /pipeline/test-run
  - Returns webhook execution

getExecutions()
  - GET /pipeline/executions
  - Returns list of execution IDs

getExecution(webhookId)
  - GET /pipeline/executions/{id}
  - Returns full execution details

healthCheck()
  - GET /health
  - Returns boolean (is API up?)
```

### Backend Endpoints Used
```
POST /pipeline/test-run           # Trigger test
GET  /pipeline/executions         # List executions
GET  /pipeline/executions/{id}    # Get execution details
GET  /health                      # Health check
```

---

## 🎨 Key Features

✅ **Real-time Result Polling** - Automatically fetches results
✅ **Live Status Display** - Shows pending/completed/failed status
✅ **Detailed Metrics** - Total tests, passed, failed, success rate
✅ **Failure Analysis** - Shows root causes and suggested fixes
✅ **Code References** - Shows affected files and line numbers
✅ **Report Display** - Full markdown report preview
✅ **Execution History** - Track all past test runs
✅ **Responsive Design** - Works on desktop and mobile
✅ **Dark Theme** - Matches your design system

---

## 💻 Development Workflow

### 1. Make a Test Run
Navigate to **Test Runner** → Fill form → Click "Run Tests"

### 2. See Results
Results populate automatically as backend completes each stage:
- 🔗 GitHub Agent (analyze files)
- 🧠 Code Agent (analyze code)
- 🧪 Test Generator (generate tests)
- ⚙️ Test Executor (run tests)
- 🔍 Failure Analyzer (if failures)
- 📊 Report Generator (final report)

### 3. Review History
Click **History** to see all past executions and their details

### 4. Click Logo
Clicking "Vector" logo takes you back to homepage

---

## 🔧 Customizing Pages

### Add New Page
1. Create component in `src/style/MyPage.jsx`
2. Import in `App.jsx`
3. Add case in `renderPage()` switch
4. Add navigation link in `Header.jsx`

Example:
```jsx
// In App.jsx
case 'dashboard':
  return <Dashboard />;

// In Header.jsx
{ name: 'Dashboard', page: 'dashboard' }
```

### Modify API Calls
Edit `src/services/api.js` to change:
- API base URL
- Request/response handling
- Error handling

---

## 🐛 Troubleshooting

### "Failed to fetch"
Backend might not be running. Start it:
```bash
cd Agents
python main.py
```

Check it's running: http://localhost:8000 in browser

### "Cannot find module"
Make sure you ran:
```bash
cd frontend
npm install
```

### Results not updating
Check browser console for errors (F12)
Check backend logs for issues

---

## 📊 Result Data Structure

When a test completes, you get a full execution object:

```json
{
  "webhook_id": "test-123456",
  "timestamp": "2024-03-21T10:30:00",
  "status": "completed",
  "summary": {
    "total_tests": 16,
    "passed": 14,
    "failed": 2,
    "success_rate": 87.5
  },
  "endpoints": [
    {
      "method": "POST",
      "path": "/users",
      "auth_required": true
    }
  ],
  "failures": [
    {
      "test_name": "[NEGATIVE] POST /users - Missing email",
      "error": "Internal Server Error",
      "root_cause": "Null check missing",
      "suggested_fix": "Add: if not user.email: raise ValueError(...)",
      "severity": "HIGH",
      "affected_file": "routes/users.py",
      "line_number": 42
    }
  ],
  "report_markdown": "# Testing Report\n..."
}
```

---

## 🎯 Next Steps

1. ✅ Run backend: `cd Agents && python main.py`
2. ✅ Run frontend: `cd frontend && npm run dev`
3. ✅ Go to http://localhost:5173
4. ✅ Click "Test Runner" and trigger a test
5. ✅ Watch results populate in real-time
6. ✅ Check "History" to see past runs

---

## 📚 Component Tree

```
App
├── Header
│   └── Navigation buttons (Home, Test Runner, History)
├── FloatingLines (background)
└── Page Content (based on currentPage)
    ├── HomePage
    │   ├── HeroSection
    │   ├── StatsBar
    │   └── CoreComponents
    ├── TestRunner
    │   ├── Form (repo, commit details)
    │   └── Results (stats, endpoints, failures)
    └── ExecutionHistory
        ├── Execution List
        └── Execution Details
```

---

## 🎉 You're All Set!

Frontend is fully integrated with the LangGraph backend pipeline. Every feature on the backend has a corresponding UI in the frontend.

Start testing: http://localhost:5173 → "Test Runner"
