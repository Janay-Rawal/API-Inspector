import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import streamlit as st
from backend.parser import fetch_openapi_spec, extract_endpoints, fallback_html_scan, verify_live_endpoints, probe_common_paths, get_example_request_from_spec, get_example_query_from_spec
from backend.summarizer import summarize_endpoints_groq
import json
import requests
import pandas as pd
import altair as alt
from io import BytesIO

endpoints = st.session_state.get("endpoints", [])
summary = st.session_state.get("summary", "")

@st.cache_data(ttl=3600)
def cached_openapi(base_url: str):
    return fetch_openapi_spec(base_url)

@st.cache_data(ttl=3600)
def cached_html_fallback(base_url: str):
    return fallback_html_scan(base_url)

@st.cache_data(ttl=1800)
def cached_probe(base_url: str):
    return probe_common_paths(base_url)

st.set_page_config(page_title="AI-Powered API Inspector", layout="wide")
st.markdown("""
<div style="text-align:center;">
    <h1>AI-Powered API Inspector</h1>
    <p style="color:gray;font-size:16px;">
        Analyze, summarize, and test any REST API — powered by LangChain + Groq
    </p>
</div>
<hr style="border: 0.5px solid #444;">
""", unsafe_allow_html=True)

if "base_url" not in st.session_state:
    st.session_state.base_url = ""
if "endpoints" not in st.session_state:
    st.session_state["endpoints"] = []
if "spec" not in st.session_state:
    st.session_state["spec"] = None


col1, col2 = st.columns([3,1])
with col1:
    base_url = st.text_input(
        "Enter base API URL (e.g. http://127.0.0.1:8000):",
        value=st.session_state.base_url,
    ).strip()
with col2:
    st.markdown("<div style='margin-top:27px'></div>", unsafe_allow_html=True)
    if st.button("Load Demo"):
        base_url = "https://petstore3.swagger.io/api/v3/"
        st.session_state.base_url = base_url
        st.rerun()

token = st.text_input("API Token (optional)", type="password")

if st.button("Analyze API"):
    with st.spinner("Fetching OpenAPI spec..."):
        headers = {"Authorization": f"Bearer {token}"} if token else {}
        spec = cached_openapi(base_url)
        endpoints = []

        if spec:
            st.session_state["spec"] = spec
            endpoints = extract_endpoints(spec)
        else:
            st.warning("No OpenAPI spec found, trying HTML fallback...")
            endpoints = cached_html_fallback(base_url)
            endpoints = verify_live_endpoints(base_url, endpoints)

        if not endpoints:
            st.warning("Could not find any endpoints via OpenAPI or HTML. Trying JSON probing...")
            endpoints = cached_probe(base_url)

        if not endpoints:
            st.error("Could not find any endpoints.")
        else:
            st.success(f"Found {len(endpoints)} endpoints")
            st.session_state["endpoints"] = endpoints  

            with st.expander("📜 View All Endpoints (JSON)", expanded=False):
                st.json(endpoints)

            with st.expander("### 📊 Endpoint Overview", expanded=False):
                df = pd.DataFrame(endpoints)
                if not df.empty:
                    colA, colB = st.columns(2, vertical_alignment="center")
                    with colA:
                        st.metric("Total endpoints", len(df))
                        st.table(df.groupby("method").size().reset_index(name="count"))
                    with colB:
                        st.markdown("<br>" * 3, unsafe_allow_html=True)
                        seg_counts = (
                            df["path"]
                            .apply(lambda p: p.split("/")[1] if p.startswith("/") and len(p.split("/")) > 1 else "root")
                            .value_counts()
                            .reset_index()
                        )
                        seg_counts.columns = ["path", "count"]
                        st.table(seg_counts)

            st.markdown("### 🔎 Endpoint Distribution")
            chart = (
                alt.Chart(df)
                .mark_bar()
                .encode(
                    x=alt.X("method:N", title="HTTP Method"),
                    y=alt.Y("count()", title="Number of Endpoints"),
                    color="method:N",
                )
            )
            st.altair_chart(chart, use_container_width=True)

            with st.expander("🧠 AI Summary", expanded=False):
                with st.spinner("Generating AI summary..."):
                    summary = summarize_endpoints_groq(endpoints)
                    st.session_state["summary"] = summary 
                    st.markdown(summary)

def render_markdown_doc(base_url: str, endpoints: list, ai_summary: str) -> str:
    lines = []
    lines.append(f"# API Summary for `{base_url}`\n")
    lines.append("## Endpoints (Table)\n")
    lines.append("| Method | Path | Note |")
    lines.append("|---|---|---|")
    for e in endpoints:
        note = e.get("summary","").replace("\n"," ").strip()
        lines.append(f"| {e['method']} | `{e['path']}` | {note} |")
    lines.append("\n## AI Notes\n")
    lines.append(ai_summary if ai_summary else "_No AI summary available._")
    return "\n".join(lines)

if endpoints:
    md = render_markdown_doc(base_url, endpoints, summary)
    st.download_button(
        "📄 Download Structured Markdown",
        data=md.encode("utf-8"),
        file_name="api_summary.md",
        mime="text/markdown",
    )

    import json
    st.download_button(
        "🧾 Download Raw JSON",
        data=json.dumps(endpoints, indent=2).encode("utf-8"),
        file_name="endpoints.json",
        mime="application/json",
    )

st.markdown("### 🔍 Try an Endpoint")

if "endpoints" in st.session_state and st.session_state["endpoints"]:
    endpoints = st.session_state["endpoints"]
    options = [f"{e['method']} {e['path']}" for e in endpoints]
    choice = st.selectbox("Choose endpoint", options)
    method, path = choice.split(" ", 1)

    st.caption("Optional: query params and body (JSON)")
    query_prefill = "{}"
    body_prefill = "{}"
    
    spec = st.session_state.get("spec")

    if spec and isinstance(spec, dict):
        paths = spec.get("paths", {})
        if path in paths:
            path_key = path
            q_ex = get_example_query_from_spec(spec, path_key, method)
            if q_ex:
                query_prefill = json.dumps(q_ex, indent=2)
            b_ex = get_example_request_from_spec(spec, path_key, method)
            if b_ex:
                body_prefill = json.dumps(b_ex, indent=2)
        else:
            path_key = None
    else:
        path_key = None

    raw_qs = st.text_area(
        "Query params (JSON)",
        value=query_prefill,
        height=100,
        key=f"qs_{path}_{method}"
    )
    raw_body = st.text_area(
        "Request body (JSON)",
        value=body_prefill,
        height=140,
        key=f"body_{path}_{method}"
    )
    try:
        qs = json.loads(raw_qs or "{}")
    except Exception:
        st.error("Invalid query params JSON")
        qs = {}
    try:
        body = json.loads(raw_body or "{}")
    except Exception:
        st.error("Invalid body JSON")
        body = {}

    if st.button("Send Test Request"):
        url = base_url.rstrip("/") + path
        try:
            resp = requests.request(method, url, params=qs, json=body, timeout=10)
            status = resp.status_code
            if 200 <= status < 300:
                st.success(f"✅ Success ({status})")
            elif 400 <= status < 500:
                st.warning(f"⚠️ Client error {status} — check query/body parameters.")
            elif 500 <= status < 600:
                st.error(f"🚨 Server error {status} — API may be unstable or require authentication.")
            else:
                st.info(f"ℹ️ Response code: {status}")
            if method in ["POST", "PUT"] and body == {}:
                st.info("💡 Hint: This endpoint likely requires a request body.")
            if method == "GET" and qs == {}:
                st.info("💡 Hint: You can add query parameters above (e.g., ?id=123).")
            st.write(f"**Status:** {resp.status_code}")
            try:
                data = resp.json()
                if isinstance(data, list):
                    st.write(f"Showing {min(len(data), 5)} of {len(data)} results:")
                    st.json(data[:5])
                else:
                    st.json(data)
            except Exception:
                st.code(resp.text[:1000])
        except Exception as e:
            st.error(f"Request failed: {e}")
else:
    st.info("Run 'Analyze API' first to load endpoints.")