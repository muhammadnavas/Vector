import io
import re
import zipfile
from typing import Optional, Tuple
from urllib.parse import urlparse

import requests


HTTP_METHODS = ("GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD")


def validate_github_repo_url(repo_url: str) -> Tuple[bool, Optional[str]]:
    """Validate that the URL is a public GitHub repository URL."""
    try:
        parsed = urlparse(repo_url)
    except Exception:
        return False, "Invalid URL format"

    if parsed.scheme not in {"http", "https"}:
        return False, "URL must start with http:// or https://"
    if parsed.netloc.lower() != "github.com":
        return False, "Only github.com repository URLs are supported"

    path_parts = [p for p in parsed.path.split("/") if p]
    if len(path_parts) < 2:
        return False, "Repository URL must be in format https://github.com/<owner>/<repo>"

    return True, None


def _owner_repo_from_url(repo_url: str) -> Tuple[str, str]:
    parsed = urlparse(repo_url)
    parts = [p for p in parsed.path.split("/") if p]
    owner = parts[0]
    repo = parts[1].replace(".git", "")
    return owner, repo


def _download_repo_zip(repo_url: str) -> bytes:
    owner, repo = _owner_repo_from_url(repo_url)
    zip_url = f"https://codeload.github.com/{owner}/{repo}/zip/refs/heads/main"

    response = requests.get(zip_url, timeout=45)
    if response.status_code == 404:
        zip_url = f"https://codeload.github.com/{owner}/{repo}/zip/refs/heads/master"
        response = requests.get(zip_url, timeout=45)

    if not response.ok:
        raise ValueError("Repository could not be downloaded. Ensure it exists and is public.")

    return response.content


def _extract_text_files(zip_bytes: bytes, max_files: int = 500, max_size_bytes: int = 5_000_000) -> list[tuple[str, str]]:
    collected: list[tuple[str, str]] = []

    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
        infos = [i for i in zf.infolist() if not i.is_dir()]

        for info in infos[:max_files]:
            if info.file_size > max_size_bytes:
                continue

            lower_name = info.filename.lower()
            if not lower_name.endswith((".py", ".js", ".ts", ".tsx", ".jsx")):
                continue

            try:
                content = zf.read(info.filename).decode("utf-8", errors="ignore")
            except Exception:
                continue

            collected.append((info.filename, content))

    return collected


def _normalize_path(path: str) -> str:
    # Zip root folder is usually <repo>-<branch>/, keep repo-relative path for output clarity.
    return "/".join(path.split("/")[1:]) if "/" in path else path


def _extract_path_from_url_literal(url: str) -> str:
    cleaned = url.strip()

    if cleaned.startswith("http://") or cleaned.startswith("https://"):
        parsed = urlparse(cleaned)
        cleaned = parsed.path or "/"

    if "${" in cleaned:
        # Keep deterministic prefix for template literals.
        cleaned = cleaned.split("${", 1)[0]

    if "/" not in cleaned and cleaned:
        cleaned = "/" + cleaned

    return cleaned or "/"


def _discover_fastapi(path: str, content: str) -> list[dict]:
    results = []
    pattern = re.compile(r"@(?:\w+\.)?(get|post|put|patch|delete|options|head)\(\s*['\"]([^'\"]+)['\"]")
    for method, route in pattern.findall(content):
        results.append({
            "method": method.upper(),
            "path": route,
            "file": _normalize_path(path),
            "framework": "FastAPI",
            "auth_required": bool(re.search(r"Depends\(|Authorization|Bearer", content)),
            "confidence": 0.95,
        })
    return results


def _discover_flask(path: str, content: str) -> list[dict]:
    results = []
    route_pattern = re.compile(r"@(?:\w+\.)?route\(\s*['\"]([^'\"]+)['\"][^\)]*\)")
    method_pattern = re.compile(r"methods\s*=\s*\[([^\]]+)\]")

    for match in route_pattern.finditer(content):
        route = match.group(1)
        window = content[match.start():match.end() + 200]
        methods_match = method_pattern.search(window)
        methods = ["GET"]
        if methods_match:
            methods = [m.strip().strip("'\"").upper() for m in methods_match.group(1).split(",") if m.strip()]

        for method in methods:
            if method in HTTP_METHODS:
                results.append({
                    "method": method,
                    "path": route,
                    "file": _normalize_path(path),
                    "framework": "Flask",
                    "auth_required": bool(re.search(r"@login_required|Authorization|Bearer", content)),
                    "confidence": 0.9,
                })
    return results


def _discover_django(path: str, content: str) -> list[dict]:
    results = []
    for route in re.findall(r"path\(\s*['\"]([^'\"]+)['\"]", content):
        results.append({
            "method": "ANY",
            "path": "/" + route if not route.startswith("/") else route,
            "file": _normalize_path(path),
            "framework": "Django",
            "auth_required": bool(re.search(r"login_required|permission_classes|IsAuthenticated", content)),
            "confidence": 0.7,
        })
    return results


def _discover_express(path: str, content: str) -> list[dict]:
    results = []
    pattern = re.compile(r"(?:app|router)\.(get|post|put|patch|delete|options|head)\(\s*['\"]([^'\"]+)['\"]")
    for method, route in pattern.findall(content):
        results.append({
            "method": method.upper(),
            "path": route,
            "file": _normalize_path(path),
            "framework": "Express",
            "auth_required": bool(re.search(r"auth|jwt|Authorization|Bearer", content, re.IGNORECASE)),
            "confidence": 0.9,
        })
    return results


def _discover_nest(path: str, content: str) -> list[dict]:
    results = []
    controller_prefix = ""
    controller_match = re.search(r"@Controller\(\s*['\"]([^'\"]*)['\"]\s*\)", content)
    if controller_match:
        controller_prefix = controller_match.group(1)

    pattern = re.compile(r"@(Get|Post|Put|Patch|Delete|Options|Head)\(\s*['\"]?([^'\")\n]*)['\"]?\s*\)")
    for method, sub_path in pattern.findall(content):
        full_path = "/" + "/".join([p for p in [controller_prefix, sub_path] if p]).strip("/")
        if full_path == "/":
            full_path = "/"
        results.append({
            "method": method.upper(),
            "path": full_path,
            "file": _normalize_path(path),
            "framework": "NestJS",
            "auth_required": bool(re.search(r"@UseGuards|AuthGuard|Bearer", content)),
            "confidence": 0.85,
        })
    return results


def _discover_frontend_fetch(path: str, content: str) -> list[dict]:
    results = []

    # fetch('...') and fetch("...")
    fetch_pattern = re.compile(r"fetch\(\s*['\"]([^'\"]+)['\"]")
    for raw_url in fetch_pattern.findall(content):
        results.append({
            "method": "GET",
            "path": _extract_path_from_url_literal(raw_url),
            "file": _normalize_path(path),
            "framework": "Frontend Fetch",
            "auth_required": bool(re.search(r"Authorization|Bearer", content, re.IGNORECASE)),
            "confidence": 0.78,
        })

    # fetch(`...`) with template literals
    fetch_template_pattern = re.compile(r"fetch\(\s*`([^`]+)`")
    for raw_url in fetch_template_pattern.findall(content):
        results.append({
            "method": "GET",
            "path": _extract_path_from_url_literal(raw_url),
            "file": _normalize_path(path),
            "framework": "Frontend Fetch",
            "auth_required": bool(re.search(r"Authorization|Bearer", content, re.IGNORECASE)),
            "confidence": 0.72,
        })

    # Best-effort method extraction from options object near fetch call.
    method_pattern = re.compile(r"fetch\([^\)]*\{[^\}]*method\s*:\s*['\"](GET|POST|PUT|PATCH|DELETE|OPTIONS|HEAD)['\"]", re.IGNORECASE)
    methods = [m.upper() for m in method_pattern.findall(content)]
    if methods and results:
        for idx, method in enumerate(methods):
            if idx < len(results):
                results[idx]["method"] = method

    return results


def _discover_frontend_axios(path: str, content: str) -> list[dict]:
    results = []

    # axios.get('/x'), axios.post('/x')
    direct_pattern = re.compile(r"axios\.(get|post|put|patch|delete|options|head)\(\s*['\"]([^'\"]+)['\"]", re.IGNORECASE)
    for method, raw_url in direct_pattern.findall(content):
        results.append({
            "method": method.upper(),
            "path": _extract_path_from_url_literal(raw_url),
            "file": _normalize_path(path),
            "framework": "Frontend Axios",
            "auth_required": bool(re.search(r"Authorization|Bearer", content, re.IGNORECASE)),
            "confidence": 0.88,
        })

    # axios({ method: 'GET', url: '/x' })
    object_pattern = re.compile(
        r"axios\(\s*\{[^\}]*method\s*:\s*['\"](GET|POST|PUT|PATCH|DELETE|OPTIONS|HEAD)['\"][^\}]*url\s*:\s*['\"]([^'\"]+)['\"]",
        re.IGNORECASE,
    )
    for method, raw_url in object_pattern.findall(content):
        results.append({
            "method": method.upper(),
            "path": _extract_path_from_url_literal(raw_url),
            "file": _normalize_path(path),
            "framework": "Frontend Axios",
            "auth_required": bool(re.search(r"Authorization|Bearer", content, re.IGNORECASE)),
            "confidence": 0.84,
        })

    return results


def _discover_frontend_routes(path: str, content: str) -> list[dict]:
    results = []

    # React Router style: <Route path="/foo" ...>
    jsx_route_pattern = re.compile(r"<Route[^>]*path=\{?['\"]([^'\"]+)['\"]\}?")
    for route in jsx_route_pattern.findall(content):
        results.append({
            "method": "ROUTE",
            "path": _extract_path_from_url_literal(route),
            "file": _normalize_path(path),
            "framework": "Frontend Route",
            "auth_required": False,
            "confidence": 0.9,
        })

    return results


def discover_endpoints_from_repo(repo_url: str) -> dict:
    """Discover API endpoints from a public GitHub repository using static analysis."""
    zip_bytes = _download_repo_zip(repo_url)
    files = _extract_text_files(zip_bytes)

    endpoints: list[dict] = []
    framework_counts: dict[str, int] = {}

    for file_path, content in files:
        discovered = []

        if file_path.endswith(".py"):
            discovered.extend(_discover_fastapi(file_path, content))
            discovered.extend(_discover_flask(file_path, content))
            discovered.extend(_discover_django(file_path, content))

        if file_path.endswith((".js", ".ts", ".jsx", ".tsx")):
            discovered.extend(_discover_express(file_path, content))
            discovered.extend(_discover_nest(file_path, content))
            discovered.extend(_discover_frontend_fetch(file_path, content))
            discovered.extend(_discover_frontend_axios(file_path, content))
            discovered.extend(_discover_frontend_routes(file_path, content))

        for endpoint in discovered:
            framework = endpoint["framework"]
            framework_counts[framework] = framework_counts.get(framework, 0) + 1

        endpoints.extend(discovered)

    # Deduplicate by method+path+file
    dedup = {}
    for endpoint in endpoints:
        key = (endpoint["method"], endpoint["path"], endpoint["file"])
        if key not in dedup or endpoint["confidence"] > dedup[key]["confidence"]:
            dedup[key] = endpoint

    unique_endpoints = list(dedup.values())
    unique_endpoints.sort(key=lambda e: (e["path"], e["method"], e["file"]))

    return {
        "repo_url": repo_url,
        "endpoints": unique_endpoints,
        "scan_summary": {
            "files_scanned": len(files),
            "endpoints_found": len(unique_endpoints),
            "framework_counts": framework_counts,
        },
    }
