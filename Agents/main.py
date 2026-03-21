from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import health, items, pipeline

app = FastAPI(
    title="Vector API",
    description="AI-powered automated API testing platform with LangGraph multi-agent orchestration",
    version="1.0.0"
)

# Enable CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router)
app.include_router(items.router, prefix="/api")
app.include_router(pipeline.router)

@app.get("/")
def read_root():
    return {
        "message": "Vector API is running",
        "version": "1.0.0",
        "docs": "http://localhost:8000/docs",
        "pipeline_webhook": "POST /pipeline/webhook/github",
        "manual_test": "POST /pipeline/test-run"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
