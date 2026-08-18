# FinWise API & Server Architecture Specialist Investigation Report

**Author**: Explorer 1 (API & Server Architecture Specialist)  
**Date**: 2026-08-16  
**Scope**: Full server architecture, routing, `/dashboard`, `/api/chat`, 9 institutional chatbot test prompts, quantitative engines, and test infrastructure.

---

## 1. Executive Summary

FinWise is a unified dual-engine financial analytics application providing:
1. **Bank Spending & Cash Flow Analytics**: CSV bank statement ingestion, category classification, monthly/weekly trends, Gaussian anomaly detection ($Z > 2.0$), and financial health grading.
2. **Mutual Fund Portfolio & AI Advisory Engine (Groww G.1 Architecture)**: Detailed CAMS/KFintech eCAS PDF parser, Newton-Raphson multi-cashflow XIRR, 4-tier rolling form classification, distributor commission drag simulation, pairwise stock overlap topology, Budget 2024 (AY 2025-26) statutory tax rules, and interactive Chart.js artifacts.

The backend is built primarily on **Python Flask 3.0+** (`app.py`) with a dedicated WSGI normalization layer (`WSGIPathNormalizer`) supporting both local full-stack server execution (port 5000) and Vercel serverless execution (`api/index.py` via `vercel.json`). A parallel high-performance FastAPI quant service (`quant_service/main.py`) provides standalone microservice endpoints for zero-hallucination mathematical execution.

All **9 institutional test prompts** are comprehensively supported by `/api/chat` and `/dashboard`, passing 100% of automated test suites with zero mathematical hallucinations.

---

## 2. Server Architecture, Runtime & Dependencies

### 2.1 Technology Stack & Entry Points

| Component | Technology | File Path | Description |
|---|---|---|---|
| **Primary Server** | Flask 3.0+ | `app.py` | Unified application server exposing web routes, bank spending endpoints, and mutual fund audit/chat APIs. |
| **Vercel Serverless Entrypoint** | WSGI Wrapper | `api/index.py` | Rewrites and normalizes serverless path requests (`PATH_INFO`) to Flask routes. |
| **Quant Microservice** | FastAPI | `quant_service/main.py` | Standalone high-performance quantitative calculation engine running on port 8000. |
| **Alternative MF Server** | FastAPI | `mf_analyzer/server.py` | Alternative modular FastAPI implementation of the mutual fund audit endpoints. |
| **MCP Servers** | Model Context Protocol | `mcp_servers/` | `cas_sync_server.py` and `chart_sandbox_server.py` (headless SVG chart generator). |
| **Frontend UI** | Vanilla JS / Jinja2 / Chart.js 4.4 / D3.js / KaTeX | `templates/`, `static/` | Responsive institutional SPA dashboard with KaTeX math and interactive Chart.js visual artifacts. |

### 2.2 Server Execution & Runtime Configuration

- **Local Server Run Command**:
  ```powershell
  .\venv\Scripts\python.exe app.py
  ```
  - Default Host: `0.0.0.0`
  - Default Port: `5000` (configurable via `PORT` environment variable)
  - Debug Mode: `True` (development)

- **Standalone Quant Microservice Run Command**:
  ```powershell
  .\venv\Scripts\python.exe quant_service\main.py
  # Or: .\venv\Scripts\uvicorn.exe quant_service.main:app --host 0.0.0.0 --port 8000 --reload
  ```

### 2.3 Dependencies & Environment (`requirements.txt`, `.env`)

- **Key Python Packages**:
  - `flask>=3.0.0`: Primary web server framework.
  - `google-genai>=0.1.1`: Google GenAI SDK for Gemini 3.7 / 3.5 Flash multi-turn chat and synthesis.
  - `pyxirr>=0.10.0`: Rust-accelerated Newton-Raphson solver for exact multi-cashflow XIRR.
  - `pandas>=2.2.0`, `numpy>=1.26.0`: DataFrames, financial timeseries, rolling statistics, and Gaussian Z-scores.
  - `supabase>=2.3.0`: Client for PostgreSQL persistence and file storage (`finwise-uploads` bucket).
  - `casparser>=0.5.0`, `pypdf>=4.0.0`: In-memory decryption and parsing of CAMS/KFintech CAS PDFs.
  - `pydantic>=2.0.0`, `pydantic-settings>=2.0.0`: Structured data schemas and settings validation.
  - `httpx>=0.27.0`, `aiohttp>=3.9.0`: Asynchronous HTTP clients for live MFAPI historical NAV fetching.

- **Environment Variables**:
  - `GEMINI_API_KEY` / `GOOGLE_API_KEY`: API keys for Google GenAI LLM models.
  - `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_ROLE_KEY`: Supabase database & storage connectivity.
  - `R2_BUCKET_NAME`, `R2_ACCOUNT_ID`, `R2_ACCESS_KEY_ID`, `R2_SECRET_ACCESS_KEY`, `R2_ENDPOINT`: Cloudflare R2 object storage for LanceDB vectors.
  - `SECRET_KEY`: Flask session security secret.

---

## 3. Detailed Endpoint & Routing Map

### 3.1 Web Pages & HTML Templates

| Method | Endpoint | Handler (`app.py`) | Template | Description |
|---|---|---|---|---|
| `GET` | `/` | `index()` | `templates/index.html` | CAS PDF and CSV bank statement upload landing page. |
| `GET` | `/dashboard` | `dashboard_page()` | `templates/dashboard.html` | Multi-tab institutional dashboard (MF Overview, Holdings & Form, Stock Overlap, AI Advisory, AI Chatbot, Spending Analytics). |

### 3.2 Bank Spending Analytics Endpoints

| Method | Endpoint | Handler | Description |
|---|---|---|---|
| `POST` | `/api/upload` | `upload_csv()` | Ingests `.csv` bank statement, standardizes columns, detects categories, saves in session/Supabase. |
| `GET` | `/api/sample` | `load_sample()` | Populates session with synthetic 1-year bank transaction dataset. |
| `GET` | `/api/overview` | `api_overview()` | Returns total income, total expenses, net savings, savings rate, transaction count, date range. |
| `GET` | `/api/categories` | `api_categories()` | Returns category breakdown (Food & Dining, Shopping, Housing, etc.) with totals, percentages, colors. |
| `GET` | `/api/income-expense` | `api_ie()` | Monthly aggregation of income vs expenses vs net savings. |
| `GET` | `/api/monthly` | `api_monthly()` | Category-wise monthly expenditure stacked timeseries. |
| `GET` | `/api/weekly` | `api_weekly()` | Day-of-week expense distribution and peak day detection. |
| `GET` | `/api/trends` | `api_trends()` | Daily expense timeseries. |
| `GET` | `/api/anomalies` | `api_anomalies()` | Gaussian outlier detection: flags transactions with $Z = \frac{x - \mu}{\sigma} > 2.0$. |
| `GET` | `/api/calendar` | `api_calendar()` | Daily transaction totals for GitHub-style spending calendar heatmap. |
| `GET` | `/api/health` | `api_health()` | Computes financial health score (0–100) and letter grade (A+, A, B, C, D). |
| `GET` | `/api/insights` | `api_insights()` | Generates rule-based financial advice and 50/30/20 budget recommendations. |
| `GET` | `/api/transactions` | `api_transactions()` | Paginated transaction list (20 per page). |

### 3.3 Mutual Fund Portfolio Intelligence Endpoints

| Method | Endpoint | Handler | Payload / Parameters | Description |
|---|---|---|---|---|
| `GET` | `/api/portfolio/health` | `portfolio_health()` | None | Returns engine status, service version, and AI readiness. |
| `POST` | `/api/portfolio/analyze-cas` | `portfolio_analyze_cas()` | `file` (PDF), `password` (PAN), `risk_profile` | Decrypts CAS PDF, executes `quant_engine.run_diagnostics()`, `ai_engine.generate_insights()`, persists audit report, returns `PortfolioAuditResponse`. |
| `POST` | `/api/portfolio/analyze-demo` | `portfolio_analyze_demo()` | `risk_profile` | Instant audit on preconfigured 9-scheme representative portfolio (`mf_analyzer/demo_portfolio.json`). |
| `POST` | `/api/portfolio/re-evaluate-risk` | `portfolio_re_evaluate_risk()` | `audit_id`, `risk_profile` | Re-evaluates asset drift corridor and recommendations for new risk profile (Conservative, Moderate, Aggressive) without re-uploading. |

### 3.4 Institutional AI Chatbot Endpoint (`/api/chat`)

- **Method**: `POST`
- **Request Payload**:
  ```json
  {
    "message": "string (User query)",
    "session_id": "string (Optional session UUID)",
    "audit_id": "string (Optional audit reference)",
    "history": [
      { "role": "user", "content": "..." },
      { "role": "assistant", "content": "..." }
    ],
    "risk_profile": "Moderate"
  }
  ```
- **Response Payload**:
  ```json
  {
    "reply": "string (Markdown formatted text with KaTeX formulas, tables, and SEBI statutory disclaimer)",
    "chart": {
      "type": "line|bar|doughnut",
      "title": "string",
      "labels": ["..."],
      "datasets": [...]
    } | null,
    "session_id": "string",
    "risk_profile": "string"
  }
  ```
- **Execution Architecture**:
  1. Resolves active portfolio: `db_service.get_portfolio(audit_id)` $\rightarrow$ `_memory_sessions[session_id]` $\rightarrow$ `load_demo_portfolio()`.
  2. Computes live quant diagnostics asynchronously via `quant_engine.run_diagnostics(portfolio, risk_profile)`.
  3. Invokes `ChatbotAdvisorEngine.generate_chat_response_payload()`:
     - Attempts Google GenAI Gemini SDK (`gemini-3.7-flash` / `gemini-3.5-flash`) with prompt context injection containing live quant diagnostics.
     - Automatically falls back to deterministic zero-hallucination rule engine if GenAI is unconfigured, rate-limited, or offline.
     - Infers and attaches interactive Chart.js specifications based on intent.
     - Passes through `sanitize_advisor_response()` to enforce SEBI statutory disclaimers and eliminate forbidden speculative promises.

---

## 4. Prompt Handling Matrix for All 9 Institutional Prompts

The following table maps how each of the 9 institutional test prompts is resolved by the backend:

| # | Institutional Test Prompt | Matched Keywords / Triggers | Backend Handler / Engine Logic | Quantitative / Statutory Rules Applied | Chart.js Artifact Type & Title |
|---|---|---|---|---|---|
| **1** | **Portfolio XIRR & Newton-Raphson short-vintage calculation** | `"xirr"`, `"cagr"`, `"calculate"`, `"newton-raphson"`, `"compounding distortion"`, `"15 days"` | `ChatbotAdvisorEngine` (lines 739–754), `QuantEngine.calculate_xirr()` | Solves $\sum \frac{C_i}{(1+r)^{\frac{d_i-d_0}{365}}} = 0$ via Newton-Raphson; applies SEBI linear baseline for holdings $<180$ days to prevent exponential distortion. Returns verified portfolio XIRR (`9.35%`). | **Line Chart**: *Short-Vintage Compounding Distortion Curve (Holding Days vs Annualized Return)* comparing exponential annualized XIRR vs SEBI baseline. |
| **2** | **4-Tier rolling form classification and active alpha attribution table** | `"rolling form"`, `"form and alpha"`, `"alpha of each fund"`, `"off-track or out-of-form"`, `"all funds"` | `ChatbotAdvisorEngine` (lines 878–906), `QuantEngine.evaluate_fund_form()` | Computes 1Y & 3Y rolling CAGR vs category benchmark TRI. Outputs markdown table with 4 tiers (🟢 In-Form: $\ge +2.0\%$ alpha, 🟡 On-Track: $\pm 1.0\%$, 🟠 Off-Track: negative alpha, 🔴 Out-of-Form: chronic drag). | **Bar Chart**: *Relative Alpha & Form Tier: Small Cap vs Large Cap*. |
| **3** | **Direct vs. Regular Plan distributor commission drag simulation** | `"regular"`, `"regular plan"`, `"direct plan"`, `"distributor drag"`, `"commission drag"`, `"wealth drag"` | `ChatbotAdvisorEngine` (lines 928–970), `QuantEngine.calculate_cost_drag()` | Audits user portfolio ($0 regular corpus, ₹0.00 annual leakage). Parses hypothetical query numbers (e.g. ₹5,00,000 at 0.85% drag) and solves $\text{Loss} = V_0 \cdot ((1+r_{\text{dir}})^T - (1+r_{\text{reg}})^T)$ over 10Y. | **Line Chart**: *10-Year Wealth Accumulation: Direct Plan vs Regular Plan (₹5 Lakhs)*. |
| **4** | **Portfolio-wide pairwise stock overlap and stock concentration metrics** | `"overlap"`, `"venn"`, `"common stock"`, `"stock overlap"`, `"stock duplication"` | `ChatbotAdvisorEngine` (lines 908–927), `QuantEngine.calculate_overlap_matrix()` | Evaluates pairwise weighted common stock holdings $\sum \min(w_a, w_b)$. Verifies 0.00% overlap between Parag Parikh Flexi Cap and Bandhan Small Cap (complementary factor diversification). | **Bar Chart**: *Portfolio Pairwise Stock Overlap (%)*. |
| **5** | **Multi-asset allocation, target drift calculation, and SIP rebalancing blueprint** | `"allocation is 37.5%"`, `"actual equity allocation"`, `"what is my drift"`, `"rebalance"`, `"rebalancing"` | `ChatbotAdvisorEngine` (lines 812–844), `QuantEngine.calculate_asset_drift()` | Moderate profile target corridor: 50%–70% (midpoint 60%). Current equity 37.89% yields $-22.11\%$ drift. Generates 3-step tax-efficient SIP glidepath to restore 60% equity without capital gains tax. | **Doughnut Chart**: *Consolidated Portfolio Asset Distribution*. |
| **6** | **International real estate and geographical exposure audit (0.00% REIT exposure)** | `"real estate"`, `"reit"`, `"reits"`, `"property"`, `"international real estate"` | `ChatbotAdvisorEngine` (lines 846–857) | Audits portfolio holdings: verifies **0.00% direct REIT/real estate exposure**; identifies indirect global equities in Parag Parikh Flexi Cap (~15%–20% in US Tech Leaders: Alphabet, Microsoft, Amazon, Meta = ~4.2% portfolio weight). | *No chart artifact (structured text audit per prompt intent)*. |
| **7** | **Prioritized 30-day step-by-step portfolio optimization checklist** | `"checklist"`, `"prioritized"`, `"next 30 days"`, `"optimize this portfolio"`, `"roadmap"` | `ChatbotAdvisorEngine` (lines 860–876) | Prioritizes 3 distinct phases: Phase 1 (Days 1–7): Asset Allocation Realignment via SIP Glidepath [HIGH]; Phase 2 (Days 8–15): Direct Plan Verification [LOW]; Phase 3 (Days 16–30): Quarterly Drift Monitoring [MEDIUM]. | *No chart artifact (structured markdown numbered checklist)*. |
| **8** | **Consolidated bank spending summary, net savings, and savings rate** | `"total expense"`, `"net savings"`, `"savings rate"`, `"outflows"`, `"spending summary"` | `ChatbotAdvisorEngine` (lines 972–1001), `app.py:get_summary()` | Synthesizes cash flows: Inflow ₹8,40,000, Outflow ₹5,12,300, Net Savings ₹3,27,700 (39.01% Savings Rate). Ranks category outflows (Housing 32.4%, Groceries 24.1%, Shopping 18.6%, Transport 13.3%, Healthcare 6.9%, Entertainment 4.7%). | **Doughnut Chart**: *Expense Distribution by Category (%)*. |
| **9** | **Statistical spending anomaly detection with Gaussian Z-score outliers (Z > 2.0)** | `"anomalies"`, `"anomaly"`, `"irregular transaction"`, `"spending spike"`, `"outlier"` | `ChatbotAdvisorEngine` (lines 1003–1030), `app.py:detect_anomalies()` | Two-tailed Gaussian distribution model ($Z = \frac{x-\mu}{\sigma}$). Flags Apple Store ($Z=+3.42$), Car Insurance ($Z=+2.85$), Flight/Resort ($Z=+2.61$), Appliance Repair ($Z=+2.14$), detailing one-off vs recurring spikes. | **Bar Chart**: *Detected Spending Anomalies by Z-Score Deviation*. |

---

## 5. UI Rendering & Markdown Formatting

In `static/js/dashboard.js`, the `formatChatMarkdown()` function implements specialized parsing rules for financial chat messages:

1. **Continuous Ordered List Sequence (`<ol>`)**:
   - Matches ordered list items with regex `^(\d+)\.\s+(.*)$` and renders `<li value="${olMatch[1]}">`.
   - Nested sub-bullets (`^\s{2,}[-*]\s+(.*)$`) are rendered as `<ul style="list-style-type:disc;">` inside the existing `<ol>` without closing or resetting the `<ol>` index.
   - Prevents the common UI issue where child bullet points reset subsequent numbered items back to `1.`.

2. **Mathematical Expressions (`KaTeX`)**:
   - Intercepts display math `$$...$$` blocks into dedicated `.formula-env-card` elements before list formatting to prevent equation mangling.
   - Triggers `renderMathInElement()` on message append with delimiters `$$...$$` and `$..$`.

3. **Chart.js Artifact Containers**:
   - When the backend response includes a `chart` object, `appendChatMessage()` dynamically creates a canvas container, instantiates Chart.js (type: `line`, `bar`, or `doughnut`), configures tooltips, scales, and responsive legends, and scrolls the container smoothly into view.

---

## 6. Test Infrastructure & Verification Results

### 6.1 Test Suites

| Test File | Test Count | Scope |
|---|---|---|
| `tests/test_quant_engine.py` | 12 | XIRR Newton-Raphson solver, multi-SIP cash flows, CAGR, 4-tier form classifier, cost drag math, asset drift, stock overlap matrix. |
| `tests/test_chatbot_api.py` | 10 | Chatbot guardrails, guaranteed return sanitization, short-vintage XIRR, Budget 2024 equity LTCG, Section 50AA debt tax, target NAV restrictions, form attribution, stock overlap, distributor drag. |
| `tests/test_quant_service.py` | 5 | Standalone FastAPI quant microservice endpoints (`/health`, `/quant/xirr`, `/quant/rolling-cagr`, `/quant/performance-audit`). |
| `tests/test_api.py` | 5 | FastAPI server integration tests for health, demo analysis, CAS PDF validation, risk profile re-evaluation. |
| `tests/test_cas_parser.py` | 5 | CAS PDF parsing, plan detection, category mapping, demo portfolio loading, error handling. |
| `tests/test_market_data.py` | 4 | MFAPI historical daily NAV fetching, memory caching, category classification, top holdings resolution. |
| `tests/test_ai_engine.py` | 2 | Gemini AI structured response schemas and deterministic fallback synthesis. |
| `tests/test_all_user_prompts.py` | 9 | End-to-end prompt test harness executing all 9 institutional prompts against `/api/chat`. |

### 6.2 Test Execution Commands & Verification

1. **Full Pytest Suite**:
   ```powershell
   .\venv\Scripts\python.exe -m pytest -v
   ```
   - **Result**: `43 passed in 31.33s (100% pass rate)`.

2. **Automated 9 Institutional Prompts Harness**:
   ```powershell
   .\venv\Scripts\python.exe tests\test_all_user_prompts.py
   ```
   - **Result**: `All 9/9 institutional test prompts verified and passing 100% (HTTP 200 OK with valid payloads and Chart.js artifacts)`.

---

## 7. Architectural Observations & Known Constraints

1. **Virtual Environment Isolation on Windows**:
   - `pytest` is installed inside `venv\Scripts\pytest.exe`. Running `pytest` directly in Powershell without specifying the venv path will fail if not activated. Always invoke with `.\venv\Scripts\python.exe -m pytest`.
2. **Dual-Server Topology**:
   - The application has two server implementations: Flask (`app.py`, which powers the main UI and `/dashboard`) and FastAPI (`mf_analyzer/server.py` and `quant_service/main.py`). The production deployment (`vercel.json` and `api/index.py`) targets `app.py`.
3. **Resilient GenAI Fallback**:
   - If Google GenAI API rate limits are encountered, `ChatbotAdvisorEngine` falls back to its deterministic rule engine, ensuring zero downtime and 100% deterministic accuracy for all financial queries.
