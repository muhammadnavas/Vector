"""
LangGraph Agent Nodes for Vector Pipeline
Each node represents one of the 6 intelligent agents
"""

import json
from typing import Any
from graph_state import VectorAgentState, CodeChange, TestCase, TestResult, TestStatus


# ============================================================================

# ============================================================================
# NODE 1: GITHUB INTEGRATION AGENT (with real endpoint extraction)
# ============================================================================
import os
import re

def extract_fastapi_endpoints_from_file(filepath):
    """
    Extract FastAPI endpoints from a Python file by looking for @router or @app route decorators.
    Returns a list of (method, path, snippet) tuples.
    """
    endpoints = []
    route_pattern = re.compile(r"@(router|app)\.(get|post|put|delete|patch)\(([^)]*)\)")
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            lines = f.readlines()
        for i, line in enumerate(lines):
            match = route_pattern.search(line)
            if match:
                method = match.group(2).upper()
                # Extract path argument (may be quoted or not)
                path_args = match.group(3).split(",")[0].strip()
                path = path_args.strip("'\" ")
                # Get a code snippet (decorator + next 2 lines)
                snippet = line.strip()
                if i+1 < len(lines):
                    snippet += "\n" + lines[i+1].strip()
                if i+2 < len(lines):
                    snippet += "\n" + lines[i+2].strip()
                endpoints.append((method, path, snippet))
    except Exception as e:
        pass
    return endpoints

def scan_directory_for_fastapi_routes(directory):
    """
    Recursively scan a directory for .py files and extract FastAPI endpoints.
    Returns a list of CodeChange objects for API route files.
    """
    code_changes = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                endpoints = extract_fastapi_endpoints_from_file(filepath)
                if endpoints:
                    methods_affected = [f"{m} {p}" for m, p, _ in endpoints]
                    snippet = "\n---\n".join([s for _, _, s in endpoints])
                    code_changes.append(CodeChange(
                        file=os.path.relpath(filepath, directory),
                        lines_added=0,  # Not tracked here
                        lines_removed=0,
                        is_api_route=True,
                        methods_affected=methods_affected,
                        content_snippet=snippet
                    ))
    return code_changes

async def github_integration_agent(state: VectorAgentState) -> dict:
    """
    Webhook receiver that processes GitHub push events
    Scans the repo for FastAPI endpoints and populates files_changed
    """
    print(f"\n🔗 [GITHUB AGENT] Processing webhook: {state.webhook_id}")
    print(f"   Repo: {state.repo_name} | Commit: {state.commit_sha[:7]}")

    # For demo: scan the local Agents/routes directory for endpoints
    repo_dir = os.path.join(os.path.dirname(__file__), "routes")
    changes = scan_directory_for_fastapi_routes(repo_dir)

    state.files_changed = changes
    state.status = "files_analyzed"

    print(f"   ✓ Found {len(changes)} API route files")
    for c in changes:
        print(f"     - {c.file}: {c.methods_affected}")
    return state.dict()


# ============================================================================
# NODE 2: CODE UNDERSTANDING AGENT
# ============================================================================
async def code_understanding_agent(state: VectorAgentState) -> dict:
    """
    Uses LLM to analyze API routes, detect auth logic,
    understand request/response structures
    """
    print(f"\n🧠 [CODE AGENT] Analyzing {len(state.files_changed)} files...")

    api_files = [f for f in state.files_changed if f.is_api_route]

    # Simulate LLM analysis
    endpoints = []
    for change in api_files:
        for method in change.methods_affected:
            endpoints.append({
                "method": method.split()[0],
                "path": method.split()[1],
                "file": change.file,
                "auth_required": "email" in change.content_snippet.lower()
            })

    state.analyzed_endpoints = endpoints
    state.auth_requirements = "Bearer token required for all endpoints"
    state.security_notes = [
        "Input validation should be added for email field",
        "Rate limiting recommended for POST endpoints"
    ]

    print(f"   ✓ Analyzed {len(endpoints)} endpoints")
    print(f"   ✓ Auth: {state.auth_requirements}")
    for note in state.security_notes:
        print(f"   ⚠️  {note}")

    state.status = "code_analyzed"
    return state.dict()


# ============================================================================
# NODE 3: TEST CASE GENERATOR AGENT
# ============================================================================
async def test_case_generator_agent(state: VectorAgentState) -> dict:
    """
    Generates adaptive test cases:
    - Positive tests (happy path)
    - Negative tests (invalid inputs)
    - Edge cases
    - Auth failure tests
    - Rate limit tests
    """
    print(f"\n🧪 [TEST GENERATOR] Generating test cases for {len(state.analyzed_endpoints)} endpoints...")

    test_cases = []
    test_id = 1

    for endpoint in state.analyzed_endpoints:
        # Positive test
        test_cases.append(TestCase(
            id=f"test_{test_id}",
            name=f"[POSITIVE] {endpoint['method']} {endpoint['path']} - Valid request",
            method=endpoint["method"],
            endpoint=endpoint["path"],
            headers={"Content-Type": "application/json", "Authorization": "Bearer token123"},
            body={"email": "user@test.com", "name": "Test User"},
            expected_status=201 if endpoint["method"] == "POST" else 200,
            expected_response_keys=["id", "email", "name"]
        ))
        test_id += 1

        # Negative test - Missing required field
        test_cases.append(TestCase(
            id=f"test_{test_id}",
            name=f"[NEGATIVE] {endpoint['method']} {endpoint['path']} - Missing email",
            method=endpoint["method"],
            endpoint=endpoint["path"],
            headers={"Content-Type": "application/json"},
            body={"name": "Test User"},
            expected_status=400,
            expected_response_keys=["error", "message"]
        ))
        test_id += 1

        # Edge case - Empty string
        test_cases.append(TestCase(
            id=f"test_{test_id}",
            name=f"[EDGE CASE] {endpoint['method']} {endpoint['path']} - Empty email",
            method=endpoint["method"],
            endpoint=endpoint["path"],
            headers={"Content-Type": "application/json"},
            body={"email": "", "name": "Test"},
            expected_status=400,
        ))
        test_id += 1

        # Auth failure
        if endpoint.get("auth_required"):
            test_cases.append(TestCase(
                id=f"test_{test_id}",
                name=f"[AUTH] {endpoint['method']} {endpoint['path']} - No auth token",
                method=endpoint["method"],
                endpoint=endpoint["path"],
                headers={"Content-Type": "application/json"},
                body={"email": "user@test.com", "name": "Test"},
                expected_status=401,
            ))
            test_id += 1

    state.generated_tests = test_cases
    state.test_count = len(test_cases)
    state.status = "tests_generated"

    print(f"   ✓ Generated {len(test_cases)} test cases")
    print(f"      - {len([t for t in test_cases if 'POSITIVE' in t.name])} positive tests")
    print(f"      - {len([t for t in test_cases if 'NEGATIVE' in t.name])} negative tests")
    print(f"      - {len([t for t in test_cases if 'EDGE CASE' in t.name])} edge case tests")
    print(f"      - {len([t for t in test_cases if 'AUTH' in t.name])} auth tests")

    return state.dict()


# ============================================================================
# NODE 4: TEST EXECUTOR AGENT
# ============================================================================
async def test_executor_agent(state: VectorAgentState) -> dict:
    """
    Executes tests using Pytest/Newman integration
    Tracks pass/fail status and timing
    """
    print(f"\n⚙️  [TEST EXECUTOR] Running {len(state.generated_tests)} tests...")

    results = []
    passed = 0
    failed = 0

    for test in state.generated_tests:
        # Simulate test execution
        # In real scenario, this would make actual API calls
        is_pass = "POSITIVE" in test.name or "missing email" not in test.name.lower()

        result = TestResult(
            test_id=test.id,
            test_name=test.name,
            status=TestStatus.PASSED if is_pass else TestStatus.FAILED,
            actual_status=test.expected_status if is_pass else 500,
            expected_status=test.expected_status,
            response_body={"id": 1, "email": "user@test.com"} if is_pass else None,
            error_message=None if is_pass else "Internal Server Error - Null check missing for user.email",
            execution_time_ms=45.2 if is_pass else 120.5
        )
        results.append(result)

        if result.status == TestStatus.PASSED:
            passed += 1
        else:
            failed += 1

    state.test_results = results
    state.tests_passed = passed
    state.tests_failed = failed
    state.total_tests_run = len(results)
    state.status = "tests_executed"

    print(f"   ✓ Tests completed: {passed} passed, {failed} failed")
    if failed > 0:
        print(f"   ⚠️  {failed} test(s) need failure analysis")

    return state.dict()


# ============================================================================
# NODE 5: FAILURE ANALYSIS AGENT
# ============================================================================
async def failure_analysis_agent(state: VectorAgentState) -> dict:
    """
    Analyzes failed tests:
    - Reads error messages and stack traces
    - Compares expected vs actual responses
    - Provides actionable fix suggestions
    """
    print(f"\n🔍 [FAILURE ANALYZER] Analyzing {state.tests_failed} failures...")

    failed_tests = [r for r in state.test_results if r.status == TestStatus.FAILED]

    if not failed_tests:
        print("   ✓ All tests passed! No failures to analyze.")
        state.status = "no_failures"
        return state.dict()

    analysis = []
    for failure in failed_tests:
        analysis_item = {
            "test_id": failure.test_id,
            "test_name": failure.test_name,
            "error": failure.error_message,
            "root_cause": "Null pointer exception in validation layer",
            "suggested_fix": "Add null check: if not user.email: raise ValueError('Email required')",
            "severity": "HIGH",
            "affected_file": "routes/users.py",
            "line_number": 42
        }
        analysis.append(analysis_item)

    state.failure_analysis = analysis
    state.suggested_fixes = [a["suggested_fix"] for a in analysis]
    state.status = "failures_analyzed"

    for item in analysis:
        print(f"   ⚠️  [{item['severity']}] {item['test_name']}")
        print(f"       Root cause: {item['root_cause']}")
        print(f"       Fix: {item['suggested_fix']}")

    return state.dict()


# ============================================================================
# NODE 6: REPORT GENERATOR AGENT
# ============================================================================
async def report_generator_agent(state: VectorAgentState) -> dict:
    """
    Creates comprehensive reports:
    - Markdown report (for PR comments, docs)
    - JSON logs (for metrics, dashboards)
    - Slack/Email alerts
    """
    print(f"\n📊 [REPORT GENERATOR] Creating reports...")

    # Generate Markdown Report
    markdown_report = f"""# Vector API Testing Report

**Commit**: {state.commit_sha[:7]} - {state.commit_message}
**Repository**: {state.repo_name}
**Date**: {state.webhook_id}

## Summary
- **Total Tests**: {state.total_tests_run}
- **Passed**: {state.tests_passed} ✓
- **Failed**: {state.tests_failed} ✗
- **Success Rate**: {(state.tests_passed/state.total_tests_run*100):.1f}%

## Analyzed Endpoints
"""
    for endpoint in state.analyzed_endpoints:
        markdown_report += f"- `{endpoint['method']} {endpoint['path']}`\n"

    if state.failure_analysis:
        markdown_report += "\n## Failures & Fixes\n"
        for item in state.failure_analysis:
            markdown_report += f"""
### {item['test_name']}
- **Error**: {item['error']}
- **Root Cause**: {item['root_cause']}
- **Fix**: `{item['suggested_fix']}`
- **File**: {item['affected_file']}:{item['line_number']}
"""

    state.report_markdown = markdown_report

    # Generate JSON Report
    state.report_json = {
        "summary": {
            "total": state.total_tests_run,
            "passed": state.tests_passed,
            "failed": state.tests_failed,
            "success_rate": (state.tests_passed / state.total_tests_run * 100) if state.total_tests_run > 0 else 0
        },
        "commit": {
            "sha": state.commit_sha,
            "message": state.commit_message
        },
        "endpoints": state.analyzed_endpoints,
        "test_results": [r.dict() for r in state.test_results],
        "failures": state.failure_analysis
    }

    state.status = "completed"
    print(f"   ✓ Reports generated")
    print(f"   📄 Markdown: {len(state.report_markdown)} characters")
    print(f"   📋 JSON: {len(str(state.report_json))} characters")

    return state.dict()
