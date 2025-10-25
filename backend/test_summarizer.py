# backend/test_summarizer.py
from parser import fetch_openapi_spec, extract_endpoints
from summarizer import summarize_endpoints_groq

base_url = "http://127.0.0.1:8000"  # your local FastAPI test app
spec = fetch_openapi_spec(base_url)
if not spec:
    print(f"❌ No OpenAPI spec at {base_url}")
else:
    eps = extract_endpoints(spec)
    print(f"✅ Found {len(eps)} endpoints")
    print(summarize_endpoints_groq(eps))