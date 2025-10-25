# 🧠 AI-Powered API Inspector  
**Analyze • Summarize • Test — Any REST API → LangChain × Groq × Streamlit**

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)
![Streamlit](https://img.shields.io/badge/Frontend-Streamlit-red?logo=streamlit)
![LangChain](https://img.shields.io/badge/LangChain-Framework-green)
![Groq](https://img.shields.io/badge/LLM-Groq-orange)
![Docker](https://img.shields.io/badge/Docker-Ready-blue)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

---

## 🚀 Overview
**AI-Powered API Inspector** is an intelligent developer tool that lets you  
analyze 🔍 → summarize 🧠 → and test 🧪 any REST API from one place.  
It automatically discovers endpoints (via OpenAPI, Swagger, or HTML fallback), explains them in plain English using **LangChain + Groq**, visualizes API structure, and lets you fire live requests with an integrated Postman-like tester.

---

## ✨ Key Features
| Category | Description |
|-----------|-------------|
| 🧩 **Automatic Endpoint Discovery** | Fetches OpenAPI specs / Swagger JSON / HTML fallback for undocumented APIs. |
| 🤖 **AI Summarization (LangChain + Groq)** | Converts raw endpoints into human-readable summaries. |
| 📊 **Interactive Dashboard** | Metrics + tables + Altair bar charts showing endpoint distribution. |
| 🧠 **Smart Tester** | Auto-prefills query/body JSON for POST & PUT endpoints. |
| 💡 **Contextual Hints** | Detects 4xx/5xx responses → suggests fixes or missing data. |
| 💾 **Caching & Persistence** | Uses `st.cache_data` + `st.session_state` for snappy reloads. |
| 📥 **Export Options** | Download AI summary as Markdown + raw JSON of endpoints. |
| 🐳 **Docker-Ready** | Build & run anywhere in one command. |

---

## 🧰 Tech Stack
- **Frontend:** Streamlit (Python)  
- **Backend:** LangChain + Groq LLM  
- **Visualization:** Altair + Pandas  
- **HTTP Engine:** Requests  
- **Containerization:** Docker  

---

## ⚙️ Installation

### 🔹 Local Setup
```bash
# 1️⃣ Clone repository
git clone https://github.com/<your-username>/api-inspector.git
cd api-inspector

# 2️⃣ Create virtual environment
python -m venv venv
source venv/bin/activate       # Windows → venv\Scripts\activate

# 3️⃣ Install dependencies
pip install -r requirements.txt

# 4️⃣ Configure environment
cp .env.example .env
# → edit .env and add your GROQ_API_KEY

# 5️⃣ Run app
streamlit run ui/app.py
```
→ Opens at **http://localhost:8501**

---

### 🔹 Docker

```bash
docker build -t api-inspector .
docker run -p 8501:8501 api-inspector
```

→ Visit **http://localhost:8501**

---

## 🔑 Environment Variables

```bash
# Example .env
GROQ_API_KEY=your_groq_api_key_here
```

> Don’t forget: your real `.env` is ignored in `.gitignore` — only `.env.example` is committed.

---

## 🧠 Usage Guide
1. **Enter Base API URL** — e.g. `https://petstore3.swagger.io/api/v3/`  
2. **(Optional) Provide Token** — paste your Bearer token (for `Authorization` header).  
   > For APIs like **CoinMarketCap**, change header key to `X-CMC_PRO_API_KEY` in `app.py`.
3. **Click “Analyze API”** — Inspector auto-detects endpoints.  
4. **Explore Dashboard** — metrics, tables, & endpoint distribution chart.  
5. **Open “🧠 AI Summary”** — view Groq-generated explanations.  
6. **Try Endpoints** — select one → edit JSON → “Send Test Request.”  
7. **Export Results** — download Markdown or JSON summaries.  

If no OpenAPI spec is found, the app now displays  
> “ℹ️ No OpenAPI spec detected — manual input only.”  

so you can still test endpoints manually.

---

## 🔍 Example APIs to Try
| API | Base URL | Works with |
|------|-----------|-----------|
| 🐶 Swagger Petstore 3.0 | `https://petstore3.swagger.io/api/v3/` | ✅ Full auto + AI summary |
| 🧠 ReqRes API | `https://reqres.in/api` | ⚙️ Manual testing |
| 💾 DummyJSON | `https://dummyjson.com` | ⚙️ HTML fallback |
| ⚙️ httpbin | `https://httpbin.org` | ✅ Tests auth header via `/anything` |
| 💰 CoinMarketCap Pro | `https://pro-api.coinmarketcap.com/v1/` | ✅ Use `X-CMC_PRO_API_KEY` header |

---


## 🧩 Architecture
```
┌──────────────────────────┐
│        Streamlit UI      │
│ Inputs · Charts · Tester │
└────────────┬─────────────┘
             │
             ▼
┌──────────────────────────┐
│      Backend (Python)    │
│ parser.py → Scan         │
│ summarizer.py → Groq AI  │
│ utils/verify.py → Ping   │
└────────────┬─────────────┘
             │
             ▼
┌──────────────────────────┐
│   External APIs / LLMs   │
│   – Any REST API         │
│   – Groq via LangChain   │
└──────────────────────────┘
```

---

## 🧭 Future Enhancements
- 🌙 Dark mode toggle  
- 🔐 OAuth2 / JWT auth presets  
- 🧾 Integrated API logging  
- 📈 Latency analytics & response-time charts  
- 🧩 VS Code / Chrome extension  
- ☁️ Deploy to Streamlit Cloud or Hugging Face Spaces  


---

## 📄 License
Licensed under the **MIT License** — free for personal & commercial use.

---
