from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional
import asyncio
from datetime import datetime
from graph import vector_pipeline
from graph_state import VectorAgentState

router = APIRouter(prefix="/pipeline", tags=["pipeline"])

# In-memory storage for execution results (replace with DB in production)
execution_history = {}


class WebhookPayload(BaseModel):
    """GitHub webhook payload"""
    webhook_id: str
    repo_name: str
    repo_url: str
    commit_sha: str
    commit_message: str


@router.post("/webhook/github")
async def receive_github_webhook(payload: WebhookPayload, background_tasks: BackgroundTasks):
    """
    Receive GitHub webhook and trigger the Vector pipeline
    """
    print(f"\n📨 [WEBHOOK] Received GitHub push event: {payload.webhook_id}")

    # Initialize state
    state = VectorAgentState(
        webhook_id=payload.webhook_id,
        repo_name=payload.repo_name,
        repo_url=payload.repo_url,
        commit_sha=payload.commit_sha,
        commit_message=payload.commit_message,
        status="pending"
    )

    # Run pipeline in background
    background_tasks.add_task(execute_pipeline, state)

    return {
        "status": "queued",
        "webhook_id": payload.webhook_id,
        "message": "Pipeline execution started",
        "repo": payload.repo_name,
        "commit": payload.commit_sha[:7]
    }


async def execute_pipeline(initial_state: VectorAgentState):
    """
    Execute the full Vector pipeline with all 6 agents
    """
    print(f"\n{'='*70}")
    print(f"🚀 STARTING VECTOR PIPELINE: {initial_state.webhook_id}")
    print(f"{'='*70}")

    try:
        # Convert to dict for LangGraph
        state_dict = initial_state.dict()

        # Execute the compiled graph
        print("\n[PIPELINE] Invoking LangGraph workflow...")
        final_state_dict = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: vector_pipeline.invoke(state_dict)
        )

        # Convert back to state object
        final_state = VectorAgentState(**final_state_dict)

        # Store in history
        execution_history[initial_state.webhook_id] = {
            "timestamp": datetime.now().isoformat(),
            "state": final_state.dict(),
            "success": True
        }

        print(f"\n{'='*70}")
        print(f"✅ PIPELINE COMPLETED: {initial_state.webhook_id}")
        print(f"{'='*70}")
        print(f"📊 Results:")
        print(f"   Tests Run: {final_state.total_tests_run}")
        print(f"   Passed: {final_state.tests_passed} ✓")
        print(f"   Failed: {final_state.tests_failed} ✗")
        print(f"   Success Rate: {(final_state.tests_passed/final_state.total_tests_run*100):.1f}%")

    except Exception as e:
        print(f"\n❌ PIPELINE FAILED: {str(e)}")
        execution_history[initial_state.webhook_id] = {
            "timestamp": datetime.now().isoformat(),
            "error": str(e),
            "success": False
        }


@router.get("/executions")
def get_executions():
    """
    Get all pipeline executions
    """
    return {
        "total": len(execution_history),
        "executions": list(execution_history.keys())
    }


@router.get("/executions/{webhook_id}")
def get_execution(webhook_id: str):
    """
    Get results of a specific pipeline execution
    """
    if webhook_id not in execution_history:
        raise HTTPException(status_code=404, detail="Execution not found")

    execution = execution_history[webhook_id]

    if execution["success"]:
        state = VectorAgentState(**execution["state"])
        return {
            "webhook_id": webhook_id,
            "timestamp": execution["timestamp"],
            "status": state.status,
            "summary": {
                "total_tests": state.total_tests_run,
                "passed": state.tests_passed,
                "failed": state.tests_failed,
                "success_rate": (state.tests_passed / state.total_tests_run * 100) if state.total_tests_run > 0 else 0
            },
            "endpoints": state.analyzed_endpoints,
            "failures": state.failure_analysis,
            "report_markdown": state.report_markdown,
        }
    else:
        return {
            "webhook_id": webhook_id,
            "timestamp": execution["timestamp"],
            "success": False,
            "error": execution["error"]
        }


@router.post("/test-run")
async def manual_test_run(payload: WebhookPayload, background_tasks: BackgroundTasks):
    """
    Manually trigger a test run (for testing without actual GitHub webhook)
    """
    return await receive_github_webhook(payload, background_tasks)
