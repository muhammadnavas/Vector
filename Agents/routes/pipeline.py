from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional
import asyncio
from datetime import datetime
import json
from pathlib import Path
import uuid
from graph import vector_pipeline
from graph_state import VectorAgentState
from discovery.service import discover_endpoints_from_repo, validate_github_repo_url

router = APIRouter(prefix="/pipeline", tags=["pipeline"])

HISTORY_FILE = Path(__file__).resolve().parent.parent / "execution_history.json"


def _load_execution_history() -> dict:
    if not HISTORY_FILE.exists():
        return {}

    try:
        raw = json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}

    # Background tasks are interrupted on reload, so pending/processing jobs cannot continue.
    for execution in raw.values():
        status = execution.get("status")
        if status in {"pending", "processing"}:
            execution["status"] = "failed"
            execution["success"] = False
            execution["error"] = "Server reloaded before job completion. Please retry."
            execution["timestamp"] = datetime.now().isoformat()
    return raw


def _save_execution_history() -> None:
    HISTORY_FILE.write_text(json.dumps(execution_history, indent=2), encoding="utf-8")


# In-memory storage backed by disk to survive development reloads.
execution_history = _load_execution_history()


class WebhookPayload(BaseModel):
    """GitHub webhook payload"""
    webhook_id: str
    repo_name: str
    repo_url: str
    commit_sha: str
    commit_message: str


class DiscoverRepoPayload(BaseModel):
    """Payload for endpoint discovery from a public GitHub repository."""
    repo_url: str
    repo_name: Optional[str] = None
    base_api_url: Optional[str] = None


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

    execution_history[payload.webhook_id] = {
        "type": "pipeline",
        "timestamp": datetime.now().isoformat(),
        "status": "pending",
        "repo": payload.repo_name,
        "repo_url": payload.repo_url,
        "success": True,
    }
    _save_execution_history()

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

    execution_history[initial_state.webhook_id] = {
        "type": "pipeline",
        "timestamp": datetime.now().isoformat(),
        "status": "processing",
        "repo": initial_state.repo_name,
        "repo_url": initial_state.repo_url,
        "success": True,
    }
    _save_execution_history()

    try:
        # Convert to dict for LangGraph
        state_dict = initial_state.dict()

        # Execute the compiled graph via async API because nodes are async.
        print("\n[PIPELINE] Invoking LangGraph workflow...")
        final_state_result = await vector_pipeline.ainvoke(state_dict)

        # LangGraph can return either dict or typed state depending on runtime path.
        final_state = (
            final_state_result
            if isinstance(final_state_result, VectorAgentState)
            else VectorAgentState(**final_state_result)
        )

        # Store in history
        execution_history[initial_state.webhook_id] = {
            "type": "pipeline",
            "timestamp": datetime.now().isoformat(),
            "status": "completed",
            "repo": initial_state.repo_name,
            "repo_url": initial_state.repo_url,
            "state": final_state.dict(),
            "success": True
        }
        _save_execution_history()

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
            "type": "pipeline",
            "timestamp": datetime.now().isoformat(),
            "status": "failed",
            "repo": initial_state.repo_name,
            "repo_url": initial_state.repo_url,
            "error": str(e),
            "success": False
        }
        _save_execution_history()


@router.post("/discover-endpoints")
async def discover_repo_endpoints(payload: DiscoverRepoPayload, background_tasks: BackgroundTasks):
    """
    Discover API endpoints from a public GitHub repository.
    Runs asynchronously and can be polled via /pipeline/executions/{webhook_id}.
    """
    is_valid, validation_error = validate_github_repo_url(payload.repo_url)
    if not is_valid:
        raise HTTPException(status_code=400, detail=validation_error)

    webhook_id = f"discover-{uuid.uuid4().hex[:12]}"
    repo_name = payload.repo_name or payload.repo_url.rstrip("/").split("/")[-1]

    execution_history[webhook_id] = {
        "type": "discovery",
        "timestamp": datetime.now().isoformat(),
        "status": "pending",
        "repo": repo_name,
        "repo_url": payload.repo_url,
        "base_api_url": payload.base_api_url,
        "success": True,
    }
    _save_execution_history()

    background_tasks.add_task(execute_discovery, webhook_id, payload.repo_url, repo_name, payload.base_api_url)

    return {
        "status": "queued",
        "webhook_id": webhook_id,
        "message": "Endpoint discovery started",
        "repo": repo_name,
        "repo_url": payload.repo_url,
        "base_api_url": payload.base_api_url,
    }


async def execute_discovery(webhook_id: str, repo_url: str, repo_name: str, base_api_url: Optional[str] = None):
    """Run repository endpoint discovery and store results in execution history."""
    execution_history[webhook_id] = {
        "type": "discovery",
        "timestamp": datetime.now().isoformat(),
        "status": "processing",
        "repo": repo_name,
        "repo_url": repo_url,
        "base_api_url": base_api_url,
        "success": True,
    }
    _save_execution_history()

    try:
        discovery_result = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: discover_endpoints_from_repo(repo_url, base_api_url=base_api_url)
        )

        execution_history[webhook_id] = {
            "type": "discovery",
            "timestamp": datetime.now().isoformat(),
            "status": "completed",
            "repo": repo_name,
            "repo_url": repo_url,
            "base_api_url": base_api_url,
            "success": True,
            "discovery": discovery_result,
        }
        _save_execution_history()
    except Exception as e:
        execution_history[webhook_id] = {
            "type": "discovery",
            "timestamp": datetime.now().isoformat(),
            "status": "failed",
            "repo": repo_name,
            "repo_url": repo_url,
            "base_api_url": base_api_url,
            "success": False,
            "error": str(e),
        }
        _save_execution_history()


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

    if execution.get("type") == "discovery":
        live_summary = execution.get("discovery", {}).get("live_test_summary") or {}
        tested = live_summary.get("tested", 0)
        passed = live_summary.get("passed", 0)
        failed = live_summary.get("failed", 0)
        success_rate = live_summary.get("success_rate", 0)

        return {
            "webhook_id": webhook_id,
            "timestamp": execution["timestamp"],
            "status": execution.get("status", "pending"),
            "repo": execution.get("repo"),
            "repo_url": execution.get("repo_url"),
            "base_api_url": execution.get("base_api_url"),
            "summary": {
                "total_tests": tested,
                "passed": passed,
                "failed": failed,
                "success_rate": success_rate,
                "endpoints_found": execution.get("discovery", {}).get("scan_summary", {}).get("endpoints_found", 0),
            },
            "endpoints": execution.get("discovery", {}).get("endpoints", []),
            "scan_summary": execution.get("discovery", {}).get("scan_summary", {}),
            "live_test_summary": live_summary,
            "failures": execution.get("discovery", {}).get("corrections", []),
            "report_markdown": None,
            "success": execution.get("success", True),
            "error": execution.get("error"),
        }

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
