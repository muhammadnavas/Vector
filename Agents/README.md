# Vector Backend API with LangGraph Pipeline

A sophisticated AI-powered automated API testing platform orchestrated with **LangGraph**, featuring 6 coordinated agents that work together to automatically test, analyze, and report on API changes.

## 🏗️ Architecture Overview

### **LangGraph Multi-Agent Pipeline**

```
GitHub Webhook Event
        ↓
┌─────────────────────────────────────┐
│ 1️⃣  GITHUB INTEGRATION AGENT       │
│ • Receives webhook                  │
│ • Detects changed files             │
│ • Identifies modified endpoints     │
└─────────────────────────────────────┘
        ↓
┌─────────────────────────────────────┐
│ 2️⃣  CODE UNDERSTANDING AGENT       │
│ • Uses LLM to analyze routes        │
│ • Detects request/response schemas  │
│ • Identifies auth requirements      │
│ • Notes security concerns           │
└─────────────────────────────────────┘
        ↓
┌─────────────────────────────────────┐
│ 3️⃣  TEST CASE GENERATOR AGENT      │
│ • Generates positive tests          │
│ • Creates negative test cases       │
│ • Designs edge case tests           │
│ • Adds auth failure tests           │
└─────────────────────────────────────┘
        ↓
┌─────────────────────────────────────┐
│ 4️⃣  TEST EXECUTOR AGENT            │
│ • Runs tests with Pytest/Newman     │
│ • Tracks pass/fail status           │
│ • Records execution timing          │
└─────────────────────────────────────┘
        ↓
       [Decision: Any failures?]
       ↙                    ↘
     YES                      NO
      ↓                       ↓
┌──────────────────┐     Skip to
│ 5️⃣  FAILURE     │     Report
│ ANALYZER AGENT   │     Generator
│ • Analyzes stack │
│   traces         │
│ • Identifies     │
│   root causes    │
│ • Suggests fixes │
└──────────────────┘
      ↓
┌─────────────────────────────────────┐
│ 6️⃣  REPORT GENERATOR AGENT         │
│ • Creates Markdown reports          │
│ • Generates JSON logs               │
│ • Posts PR comments                 │
│ • Sends Slack alerts                │
└─────────────────────────────────────┘
        ↓
    Execution Complete
    Results stored in history
```

## 📁 Project Structure

```
Agents/
├── main.py                 # FastAPI application entry point
├── config.py              # Configuration management
├── models.py              # Pydantic data models
│
├── graph_state.py         # LangGraph state definition
├── graph.py               # LangGraph workflow compilation
├── nodes.py               # 6 agent node implementations
│
├── routes/
│   ├── __init__.py
│   ├── health.py          # Health check endpoints
│   ├── items.py           # CRUD operations (example)
│   └── pipeline.py        # LangGraph pipeline endpoints
│
├── requirements.txt       # Python dependencies
├── .env.example           # Environment variables
└── README.md              # This file
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd Agents
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Run the Server

```bash
python main.py
```

Or with uvicorn directly:

```bash
uvicorn main:app --reload
```

Server runs at: `http://localhost:8000`

### 3. Access Documentation

- **Interactive Docs (Swagger)**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📡 API Endpoints

### Pipeline & Testing

#### **Receive GitHub Webhook**
```bash
POST /pipeline/webhook/github
```

Payload:
```json
{
  "webhook_id": "unique-webhook-id",
  "repo_name": "my-api-repo",
  "repo_url": "https://github.com/user/repo",
  "commit_sha": "abcdef1234567890",
  "commit_message": "Add new user endpoints"
}
```

Response:
```json
{
  "status": "queued",
  "webhook_id": "unique-webhook-id",
  "message": "Pipeline execution started",
  "repo": "my-api-repo",
  "commit": "abcdef1"
}
```

#### **Manual Test Run** (for testing without GitHub)
```bash
POST /pipeline/test-run
```

Same payload and response as webhook endpoint.

#### **Get All Executions**
```bash
GET /pipeline/executions
```

Returns:
```json
{
  "total": 5,
  "executions": ["webhook-id-1", "webhook-id-2", ...]
}
```

#### **Get Execution Results**
```bash
GET /pipeline/executions/{webhook_id}
```

Returns:
```json
{
  "webhook_id": "webhook-id-123",
  "timestamp": "2024-03-21T10:30:45.123456",
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
    },
    {
      "method": "GET",
      "path": "/users/{id}",
      "auth_required": true
    }
  ],
  "failures": [
    {
      "test_id": "test_5",
      "test_name": "[NEGATIVE] POST /users - Missing email",
      "error": "Internal Server Error - Null check missing for user.email",
      "root_cause": "Null pointer exception in validation layer",
      "suggested_fix": "Add null check: if not user.email: raise ValueError('Email required')",
      "severity": "HIGH",
      "affected_file": "routes/users.py",
      "line_number": 42
    }
  ],
  "report_markdown": "# Vector API Testing Report\n..."
}
```

### Basic CRUD (Example Items)

#### **Get All Items**
```bash
GET /api/items
```

#### **Get Item by ID**
```bash
GET /api/items/{id}
```

#### **Create Item**
```bash
POST /api/items
Content-Type: application/json

{
  "name": "Sample Item",
  "description": "A test item",
  "price": 99.99
}
```

#### **Update Item**
```bash
PUT /api/items/{id}
Content-Type: application/json

{
  "name": "Updated Name",
  "price": 149.99
}
```

#### **Delete Item**
```bash
DELETE /api/items/{id}
```

## 🔧 LangGraph Implementation

### State Flow

```python
# Initial state from webhook
VectorAgentState(
    webhook_id="...",
    repo_name="...",
    commit_sha="...",
    # ... gradually enriched by each agent
)

# After each agent processes:
# GitHub Agent → adds files_changed
# Code Agent → adds analyzed_endpoints, auth_requirements
# Test Generator → adds generated_tests
# Test Executor → adds test_results, pass/fail counts
# Failure Analyzer → adds failure_analysis, suggested_fixes
# Report Generator → adds report_markdown, report_json
```

### Conditional Routing

The pipeline uses **conditional edges** to make intelligent routing decisions:

```python
def should_analyze_failures(state: dict) -> str:
    if state.tests_failed > 0:
        return "analyze_failures"  # Route to failure analysis
    else:
        return "generate_report"   # Skip to final report
```

This means:
- **If all tests pass** → Skip failure analysis, go straight to report
- **If tests fail** → Route through failure analysis first

## 🔌 Extending the Architecture

### Adding a New Agent

1. **Create the node function** in `nodes.py`:
```python
async def my_new_agent(state: VectorAgentState) -> dict:
    # Process state
    # Modify state
    return state.dict()
```

2. **Add to graph** in `graph.py`:
```python
workflow.add_node("my_agent", my_new_agent)
workflow.add_edge("previous_agent", "my_agent")
```

### Modifying State

Update `graph_state.py` to add new fields to `VectorAgentState`:
```python
class VectorAgentState(BaseModel):
    # existing fields...
    my_new_field: str = ""
```

## 📊 Real-World Integration

### GitHub Actions

```yaml
name: Vector API Testing

on: [push]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Trigger Vector Pipeline
        run: |
          curl -X POST http://your-vector-api.com/pipeline/webhook/github \
            -H "Content-Type: application/json" \
            -d '{
              "webhook_id": "${{ github.run_id }}",
              "repo_name": "${{ github.repository }}",
              "repo_url": "${{ github.server_url }}/${{ github.repository }}",
              "commit_sha": "${{ github.sha }}",
              "commit_message": "${{ github.event.head_commit.message }}"
            }'
```

### Environment Variables

Create `.env` file:
```
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=...
GITHUB_TOKEN=ghp_...
SLACK_WEBHOOK_URL=https://hooks.slack.com/...
```

## 📝 Testing the Pipeline

### Using Swagger UI

1. Go to http://localhost:8000/docs
2. Find **POST /pipeline/test-run**
3. Click "Try it out"
4. Fill in test data:
```json
{
  "webhook_id": "test-webhook-001",
  "repo_name": "test-api-repo",
  "repo_url": "https://github.com/test/repo",
  "commit_sha": "abc123def456",
  "commit_message": "Add new endpoints"
}
```
5. Click "Execute"
6. Check results: **GET /pipeline/executions/{webhook_id}**

### Using cURL

```bash
curl -X POST http://localhost:8000/pipeline/test-run \
  -H "Content-Type: application/json" \
  -d '{
    "webhook_id": "test-001",
    "repo_name": "my-repo",
    "repo_url": "https://github.com/user/repo",
    "commit_sha": "abc123",
    "commit_message": "Test commit"
  }'
```

## 🎯 Key Features

✅ **Stateful Orchestration** - LangGraph manages complex agent workflows
✅ **Conditional Routing** - Intelligent decision-making between agents
✅ **Parallel Processing Ready** - Can be extended for concurrent agent execution
✅ **Type-Safe** - Full Pydantic type validation
✅ **Background Processing** - Webhooks processed asynchronously
✅ **Persistent History** - All executions tracked and queryable
✅ **Extensible** - Easy to add new agents or modify existing ones

## 🐛 Debugging

Enable detailed logs:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

Each agent prints status to console:
```
🔗 [GITHUB AGENT] Processing webhook...
🧠 [CODE AGENT] Analyzing files...
🧪 [TEST GENERATOR] Generating test cases...
⚙️  [TEST EXECUTOR] Running tests...
🔍 [FAILURE ANALYZER] Analyzing failures...
📊 [REPORT GENERATOR] Creating reports...
```

## 📚 Resources

- **LangGraph Docs**: https://langchain-ai.github.io/langgraph/
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **Pydantic Docs**: https://docs.pydantic.dev/

## 📝 License

MIT
