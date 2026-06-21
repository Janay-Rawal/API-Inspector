# API Inspector

A developer tool built with Streamlit and LangChain for discovering, summarizing, and testing REST APIs. 

API Inspector automatically extracts endpoints from an OpenAPI specification, summarizes their purpose using a Groq LLM (`llama-3.3-70b-versatile`), and provides an interactive UI to test HTTP methods with auto-generated JSON request payloads. If no specification is found, it falls back to static HTML scraping, JS-rendered page scraping (via Playwright), or brute-force common endpoint probing.

---

## 🚀 Project Overview

**Problem:** Exploring an undocumented or poorly documented API often requires manually hunting through network tabs, guessing endpoints, and piecing together `curl` commands just to get a basic understanding of the system. 

**Solution:** API Inspector accelerates the initial API discovery phase. By simply providing a base URL, developers can instantly view available endpoints, generate human-readable documentation via an LLM, and fire test requests—all within a single dashboard.

**Target Audience:** Backend engineers, API testers, and frontend developers integrating third-party services.

---

## ✨ Key Features

*   **OpenAPI Specification Parsing:** Automatically detects and parses `openapi.json`, `swagger.json`, or `spec.json`, resolving nested `$ref` schema references.
*   **Multi-Tier Endpoint Discovery:** 
    *   Tier 1: Specification parsing.
    *   Tier 2: Static HTML and Playwright-driven JS rendering to scrape documentation pages.
    *   Tier 3: Probing common API paths (`/api/v1/users`, `/products`, etc.).
*   **Interactive Testing:** Allows immediate testing of discovered endpoints, auto-prefilling request bodies and query parameters directly from the OpenAPI schema.
*   **AI Summarization:** Utilizes LangChain and Groq to generate a concise, developer-friendly markdown summary of endpoint purposes.
*   **Data Export:** Download structured Markdown documentation or raw JSON dumps of discovered endpoints.

---

## 🔍 Demo Workflows

To test the strongest capabilities of the application, try the following public APIs:

1.  **JSONPlaceholder (Full CRUD & Specs)**
    *   **URL:** `https://jsonplaceholder.typicode.com`
    *   **Workflow:** Enter the URL and click analyze. HTML scraping will discover standard GET methods. 
2.  **Httpbin (Robust OpenAPI Discovery)**
    *   **URL:** `https://httpbin.org`
    *   **Workflow:** The parser will automatically locate `/spec.json` and extract over 100 endpoints, clearly separating POST, PUT, DELETE, and GET methods with interactive schema generation.
3.  **DummyJSON (E-commerce Data)**
    *   **URL:** `https://dummyjson.com`

---

## 🧰 Tech Stack

**Frontend / UI:**
*   Streamlit
*   Altair (Data visualization)
*   Pandas (Data structuring)

**Backend / Logic:**
*   Python 3.12
*   Requests & HTTPX (Network requests)
*   Playwright & BeautifulSoup4 (HTML and JS-rendered DOM scraping)

**AI Components:**
*   LangChain Core
*   ChatGroq (`llama-3.3-70b-versatile`)

**Deployment:**
*   Docker

---

## 🧩 Architecture Flow

```text
User Input (Base URL & Token)
  │
  ▼
OpenAPI Specification Parsing ──(Failure)──► Playwright JS / HTML Scraping
  │                                                  │
  │                                           (Failure)
  │                                                  │
  ▼                                                  ▼
Endpoint Extraction ◄──────────────────────── Common Path Probing
  │
  ├──► AI Summarization (LangChain + Groq)
  │
  └──► Interactive Testing Layer (Auto-prefills Schema JSON)
         │
         ▼
       Response Inspection
```

---

## 📂 Project Structure

```text
api-inspector/
├── .env.example          # Environment variable template
├── README.md             # Project documentation
├── dockerfile            # Docker configuration
├── requirements.txt      # Python dependencies
├── backend/
│   ├── parser.py         # Spec detection, schema resolution, and Playwright scraping
│   └── summarizer.py     # LangChain LCEL chain for Groq LLM summarization
└── ui/
    └── app.py            # Streamlit dashboard and testing execution
```

---

## ⚙️ Local Setup

Ensure you have Python 3.12+ installed.

```bash
# 1. Clone repository
git clone https://github.com/<your-username>/api-inspector.git
cd api-inspector

# 2. Create and activate virtual environment
python -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Install Playwright browser binaries (Required for JS scraping)
playwright install chromium

# 5. Configure environment variables
cp .env.example .env
# Edit .env and add your GROQ_API_KEY

# 6. Run the application
streamlit run ui/app.py
```
*The application will be accessible at `http://localhost:8501`*

---

## ⚠️ Current Limitations

*   **Authentication Rigidity:** The UI currently only supports injecting `Bearer {token}` headers. APIs utilizing custom keys (e.g., `X-API-KEY`) require manual modification of `ui/app.py`.
*   **Method Detection without Specs:** If no OpenAPI specification is found, the HTML/Probing fallbacks default to registering endpoints as `GET`. `POST/PUT/DELETE` endpoints are difficult to infer reliably without a formal specification.
*   **Rate Limits:** Scanning public APIs without a spec triggers multiple fallback probes, which may result in temporary IP bans or 429 Too Many Requests errors.

---

## 🧭 Roadmap

*   **Dynamic Authentication:** UI support for OAuth2, Basic Auth, and custom Header injection.
*   **Expanded Specification Support:** Add parsers for Postman Collections and GraphQL schemas.
*   **MCP Integration:** Integrate a Model Context Protocol (MCP) server for local tool utilization.
*   **Persistent Histories:** SQLite implementation for maintaining request histories across sessions.
