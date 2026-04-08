from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from enum import Enum

class TestStatus(str, Enum):
    PENDING = "pending"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"

class TestCase(BaseModel):
    """Individual test case"""
    id: str
    name: str
    method: str
    endpoint: str
    headers: Dict[str, str]
    body: Optional[Dict[str, Any]] = None
    expected_status: int
    expected_response_keys: List[str] = []

class TestResult(BaseModel):
    """Result of a test execution"""
    test_id: str
    test_name: str
    status: TestStatus
    actual_status: int
    expected_status: int
    response_body: Optional[Any] = None  # Can be dict OR list (e.g. GET /posts returns [])
    error_message: Optional[str] = None
    execution_time_ms: float

class CodeChange(BaseModel):
    """Represents changes from GitHub diff"""
    file: str
    lines_added: int
    lines_removed: int
    is_api_route: bool
    methods_affected: List[str] = []
    content_snippet: str

class VectorAgentState(BaseModel):
    """Shared state throughout the pipeline"""
    # GitHub Webhook Data
    webhook_id: str
    repo_name: str
    repo_url: str
    base_api_url: Optional[str] = None
    commit_sha: str
    commit_message: str
    files_changed: List[CodeChange] = []

    # Code Understanding Phase
    analyzed_endpoints: List[Dict[str, Any]] = []
    request_schemas: Dict[str, Any] = {}
    response_schemas: Dict[str, Any] = {}
    auth_requirements: Optional[str] = None
    security_notes: List[str] = []

    # Test Generation Phase
    generated_tests: List[TestCase] = []
    test_count: int = 0

    # Test Execution Phase
    test_results: List[TestResult] = []
    total_tests_run: int = 0
    tests_passed: int = 0
    tests_failed: int = 0
    tests_skipped: int = 0

    # Failure Analysis Phase
    failures: List[Dict[str, Any]] = []
    failure_analysis: List[Dict[str, Any]] = []
    suggested_fixes: List[str] = []

    # Report Generation Phase
    report_markdown: Optional[str] = None
    report_json: Optional[Dict[str, Any]] = None
    status: str = "pending"  # pending, processing, completed, failed
    error_message: Optional[str] = None

    class Config:
        arbitrary_types_allowed = True
