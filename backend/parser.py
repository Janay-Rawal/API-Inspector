# backend/parser.py
import re
import requests
from bs4 import BeautifulSoup
import json
from requests_html import HTMLSession
from playwright.sync_api import sync_playwright

def fetch_openapi_spec(base_url: str):
    """Try to fetch /openapi.json or /swagger.json and return spec JSON."""
    candidates = ["/openapi.json", "/swagger.json", "/api/openapi.json"]
    for path in candidates:
        try:
            url = base_url.rstrip("/") + path
            r = requests.get(url, timeout=5)
            if r.status_code == 200 and "openapi" in r.text:
                return r.json()
        except Exception:
            continue
    return None


def extract_endpoints(spec_json: dict):
    """Extract method, path, and summary from OpenAPI spec."""
    paths = spec_json.get("paths", {})
    endpoints = []
    for path, methods in paths.items():
        for method, info in methods.items():
            summary = info.get("summary") or info.get("description") or ""
            endpoints.append({
                "method": method.upper(),
                "path": path,
                "summary": summary.strip()
            })
    return endpoints


def fallback_html_scan(base_url: str):
    """
    Fallback parser that scans HTML (static + JS-rendered) for endpoints.
    Uses Playwright for JS rendering (Streamlit-safe).
    """
    possible_docs = ["", "/docs", "/swagger", "/swagger-ui", "/api/docs", "/redoc"]
    endpoints, seen = [], set()

    def extract_endpoints_from_html(html_text: str):
        soup = BeautifulSoup(html_text, "lxml")
        text = " ".join(
            tag.get_text(" ", strip=True)
            for tag in soup.find_all(["code", "pre", "div", "p"])
        )
        pattern = re.compile(r"(?:(GET|POST|PUT|PATCH|DELETE)\s+)?(/[A-Za-z0-9_\-/{}/\.]+)")
        local_eps = []
        for method, path_str in pattern.findall(text):
            path_str = path_str.strip()
            if len(path_str) < 3 or len(path_str) > 80:
                continue
            if any(bad in path_str for bad in ["//", " ", ","]):
                continue
            if path_str.lower() in ["/", "/api", "/v1", "/v2"]:
                continue
            if re.search(r"PUT/?PATCH/?DELETE", path_str, re.IGNORECASE):
                continue
            if re.match(r"^/[0-9\.]+$", path_str):
                continue
            if path_str in seen:
                continue
            seen.add(path_str)
            local_eps.append({
                "method": method if method else "GET",
                "path": path_str,
                "summary": "Found via HTML fallback"
            })
        return local_eps

    for path in possible_docs:
        try:
            url = base_url.rstrip("/") + path
            print(f"🔍 Checking {url}")
            r = requests.get(url, timeout=6)
            if r.status_code != 200:
                continue

            # 🧱 Step 1: static parse
            eps = extract_endpoints_from_html(r.text)
            if eps:
                print(f"✅ Found {len(eps)} endpoints (static HTML)")
                endpoints.extend(eps)
                continue

            # 🧩 Step 2: JS-rendered parse
            print(f"⚙️ Rendering {url} with Playwright...")
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.goto(url, timeout=20000)
                html = page.content()
                browser.close()

            eps = extract_endpoints_from_html(html)
            if eps:
                print(f"✅ Found {len(eps)} endpoints (JS-rendered)")
                endpoints.extend(eps)

        except Exception as e:
            print(f"⚠️ Fallback parse failed for {path}: {e}")
            continue

    return endpoints

def verify_live_endpoints(base_url: str, endpoints: list):
    """
    Test each discovered endpoint; keep only those returning a sensible response.
    """
    valid = []
    for ep in endpoints:
        url = base_url.rstrip("/") + ep["path"]
        try:
            r = requests.request(ep["method"], url, timeout=4)
            # drop empty 200s that look like HTML placeholders
            if 200 <= r.status_code < 500 and "text/html" not in r.headers.get("Content-Type", ""):
                valid.append(ep)
        except Exception:
            continue
    return valid

def probe_common_paths(base_url: str):
    common_paths = [
        "/api", "/api/v1", "/api/v2",
        "/products", "/users", "/posts", "/comments",
        "/auth/login", "/auth/register", "/todos", "/items"
    ]
    found = []
    print(f"🔍 Probing common endpoints on {base_url} ...")

    for path in common_paths:
        url = base_url.rstrip("/") + path
        try:
            r = requests.get(url, timeout=4)
            print(f"Checked {url} -> {r.status_code}")
            if r.status_code < 500:
                try:
                    r.json()
                    print(f"✅ Found JSON endpoint: {url}")
                    found.append({"method": "GET", "path": path, "summary": "Detected via JSON probe"})
                except Exception:
                    pass
        except Exception as e:
            print(f"❌ Failed {url} -> {e}")
            continue

    print(f"Total found: {len(found)}")
    return found

if __name__ == "__main__":
    from parser import fetch_openapi_spec, extract_endpoints

    base_url = input("Enter base URL (e.g. http://127.0.0.1:8000): ").strip()
    spec = fetch_openapi_spec(base_url)

    if spec is None:
        print(f"❌ No OpenAPI spec found at {base_url}")
    else:
        endpoints = extract_endpoints(spec)
        print(f"✅ Found {len(endpoints)} endpoints:")
        for e in endpoints:
            print(f"{e['method']} {e['path']} - {e['summary']}")