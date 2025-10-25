import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import streamlit as st
from backend.parser import fetch_openapi_spec, extract_endpoints, fallback_html_scan, verify_live_endpoints, probe_common_paths
from backend.summarizer import summarize_endpoints_groq


st.set_page_config(page_title="AI-Powered API Inspector", layout="wide")
st.title("🧠 AI-Powered API Inspector (LangChain + Groq)")

base_url = st.text_input("Enter base API URL (e.g. http://127.0.0.1:8000):").strip()
token = st.text_input("API Token (optional)", type="password")

if st.button("Analyze API"):
    with st.spinner("Fetching OpenAPI spec..."):
        headers = {"Authorization": f"Bearer {token}"} if token else {}
        spec = fetch_openapi_spec(base_url)
        endpoints = []
        
        if spec:
            endpoints = extract_endpoints(spec)
        else:
            st.warning("No OpenAPI spec found, trying HTML fallback...")
            endpoints = fallback_html_scan(base_url)
            endpoints = verify_live_endpoints(base_url, endpoints)  # 🔍 filter here
        
        if not endpoints:
            st.warning("Could not find any endpoints via OpenAPI or HTML. Trying JSON probing...")
            endpoints = probe_common_paths(base_url)
        
        if not endpoints:
            st.error("Could not find any endpoints.")
        else:
            st.success(f"Found {len(endpoints)} endpoints")
            st.json(endpoints)
            with st.spinner("Generating AI summary..."):
                summary = summarize_endpoints_groq(endpoints)
                st.markdown("### 🧠 AI Summary")
                st.markdown(summary)