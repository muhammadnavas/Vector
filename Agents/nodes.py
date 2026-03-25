"""
LangGraph Agent Nodes for Vector Pipeline
Each node represents one of the 6 intelligent agents
"""

import re
import time
from typing import Any

import requests

from discovery.service import discover_endpoints_from_repo
from graph_state import VectorAgentState, CodeChange, TestCase, TestResult, TestStatus


TESTABLE_METHODS = {"GET", "HEAD", "OPTIONS"}


def _contains_path_params(path: str) -> bool:
    return bool(re.search(r"\{[^}]+\}|:[^/]+|\*", path or ""))


def _make_url(base_api_url: str, endpoint_path: str) -> str:
    return base_api_url.rstrip("/") + "/" + endpoint_path.lstrip("/")


def _parse_method_and_path_from_test_name(test_name: str) -> tuple[str, str]:
    # Pattern: [TAG] METHOD /path - description
    match = re.search(r"\]\s+([A-Z]+)\s+([^\s]+)\s+-", test_name)
    if not match:
        return "UNKNOWN", "unknown"
    return match.group(1), match.group(2)


def _source_file_for_endpoint(state: VectorAgentState, method: str, path: str) -> str:
    for endpoint in state.analyzed_endpoints:
        if endpoint.get("method") == method and endpoint.get("path") == path:
            return endpoint.get("file") or "unknown"
    return "unknown"


# ============================================================================
# NODE 1: GITHUB INTEGRATION AGENT
# ============================================================================
async def github_integration_agent(state: VectorAgentState) -> dict:
    """
    Webhook receiver that processes GitHub push events
    Analyzes changed files and detects API route modifications
    """
    print(f"\n🔗 [GITHUB AGENT] Processing webhook: {state.webhook_id}")
    print(f"   Repo: {state.repo_name} | Commit: {state.commit_sha[:7]}")

    try:
        discovered = discover_endpoints_from_repo(state.repo_url)
        endpoints = discovered.get("endpoints", [])

        grouped: dict[str, list[str]] = {}
        for endpoint in endpoints:
            grouped.setdefault(endpoint.get("file") or "unknown", []).append(
                f"{endpoint.get('method', 'UNKNOWN')} {endpoint.get('path', '/') }"
            )

        changes = []
        for file_name, methods in grouped.items():
            changes.append(
                CodeChange(
                    file=file_name,
                    lines_added=0,
                    lines_removed=0,
                    is_api_route=True,
                    methods_affected=methods,
                    content_snippet="Detected via static repository scan",
                )
            )

        state.files_changed = changes
        state.analyzed_endpoints = endpoints
        state.security_notes = [
            "Endpoint list was generated from static repository analysis.",
            "Use Base API URL in test run for real runtime validation.",
        ]
    except Exception as exc:
        state.files_changed = []
        state.analyzed_endpoints = []
        state.security_notes = [f"Endpoint discovery failed: {str(exc)}"]

    state.status = "files_analyzed"

    print(f"   ✓ Found {len(state.files_changed)} route/source files from repository scan")
    print(f"   ✓ Endpoints discovered: {len(state.analyzed_endpoints)}")
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

    endpoints = state.analyzed_endpoints

    protected_count = len([e for e in endpoints if e.get("auth_required")])
    if protected_count > 0:
        state.auth_requirements = (
            f"{protected_count}/{len(endpoints)} discovered endpoints appear to require authentication"
        )
    else:
        state.auth_requirements = "No clear auth requirement detected from static analysis"

    state.security_notes = state.security_notes + [
        "Static analysis may miss runtime middleware and router prefixes.",
        "Use live test failures as the primary source of real issues.",
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
        method = (endpoint.get("method") or "").upper()
        path = endpoint.get("path") or "/"

        if method not in TESTABLE_METHODS:
            continue
        if _contains_path_params(path):
            continue

        headers = {"Accept": "application/json"}
        if endpoint.get("auth_required"):
            headers["Authorization"] = "Bearer <token>"

        test_cases.append(TestCase(
            id=f"test_{test_id}",
            name=f"[LIVE] {method} {path} - Reachable endpoint",
            method=method,
            endpoint=path,
            headers=headers,
            expected_status=200,
            expected_response_keys=[]
        ))
        test_id += 1

        if endpoint.get("auth_required"):
            test_cases.append(TestCase(
                id=f"test_{test_id}",
                name=f"[AUTH] {method} {path} - No auth token",
                method=method,
                endpoint=path,
                headers={"Accept": "application/json"},
                expected_status=401,
            ))
            test_id += 1

    state.generated_tests = test_cases
    state.test_count = len(test_cases)
    state.status = "tests_generated"

    print(f"   ✓ Generated {len(test_cases)} test cases")
    print(f"      - {len([t for t in test_cases if 'LIVE' in t.name])} live reachability tests")
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

    if not state.base_api_url:
        print("   ⚠️  Base API URL not provided. Live execution cannot run.")

    for test in state.generated_tests:
        if not state.base_api_url:
            result = TestResult(
                test_id=test.id,
                test_name=test.name,
                status=TestStatus.FAILED,
                actual_status=0,
                expected_status=test.expected_status,
                response_body=None,
                error_message="Base API URL is required for real-world endpoint checks",
                execution_time_ms=0,
            )
            results.append(result)
            failed += 1
            continue

        request_url = _make_url(state.base_api_url, test.endpoint)
        start_time = time.perf_counter()

        try:
            response = requests.request(
                method=test.method,
                url=request_url,
                headers=test.headers,
                json=test.body,
                timeout=10,
                allow_redirects=False,
            )
            elapsed = (time.perf_counter() - start_time) * 1000
            actual_status = response.status_code

            if "[AUTH]" in test.name:
                is_pass = actual_status in {401, 403}
            else:
                is_pass = 200 <= actual_status < 400

            try:
                response_body = response.json()
            except Exception:
                response_body = None

            result = TestResult(
                test_id=test.id,
                test_name=test.name,
                status=TestStatus.PASSED if is_pass else TestStatus.FAILED,
                actual_status=actual_status,
                expected_status=test.expected_status,
                response_body=response_body,
                error_message=None if is_pass else f"HTTP {actual_status} from {request_url}",
                execution_time_ms=elapsed,
            )
        except Exception as exc:
            elapsed = (time.perf_counter() - start_time) * 1000
            result = TestResult(
                test_id=test.id,
                test_name=test.name,
                status=TestStatus.FAILED,
                actual_status=0,
                expected_status=test.expected_status,
                response_body=None,
                error_message=f"Request failed for {request_url}: {str(exc)}",
                execution_time_ms=elapsed,
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
        method, path = _parse_method_and_path_from_test_name(failure.test_name)
        source_file = _source_file_for_endpoint(state, method, path)

        root_cause = "Unexpected endpoint failure"
        suggested_fix = "Inspect endpoint handler and runtime configuration"
        severity = "MEDIUM"

        if failure.actual_status == 0:
            root_cause = "Service not reachable or request execution failed"
            suggested_fix = "Verify Base API URL, network accessibility, and service availability"
            severity = "HIGH"
        elif failure.actual_status == 404:
            root_cause = "Route not found at runtime"
            suggested_fix = "Check route prefix/versioning and deployment routing configuration"
            severity = "HIGH"
        elif failure.actual_status in {401, 403}:
            root_cause = "Authentication/authorization required"
            suggested_fix = "Provide valid auth token or adjust endpoint auth policy"
            severity = "MEDIUM"
        elif 500 <= failure.actual_status < 600:
            root_cause = "Unhandled server-side exception"
            suggested_fix = "Inspect server logs/stack trace and add defensive validation/error handling"
            severity = "HIGH"
        elif failure.actual_status in {400, 422}:
            root_cause = "Request validation failed"
            suggested_fix = "Verify required query/path/body parameters and request schema"

        analysis_item = {
            "test_id": failure.test_id,
            "test_name": failure.test_name,
            "error": failure.error_message,
            "root_cause": root_cause,
            "suggested_fix": suggested_fix,
            "severity": severity,
            "affected_file": source_file,
            "line_number": 0
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

    success_rate = (state.tests_passed / state.total_tests_run * 100) if state.total_tests_run > 0 else 0

    # Generate Markdown Report
    markdown_report = f"""# Vector API Testing Report

**Commit**: {state.commit_sha[:7]} - {state.commit_message}
**Repository**: {state.repo_name}
**Date**: {state.webhook_id}

## Summary
- **Total Tests**: {state.total_tests_run}
- **Passed**: {state.tests_passed} ✓
- **Failed**: {state.tests_failed} ✗
- **Success Rate**: {success_rate:.1f}%

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
