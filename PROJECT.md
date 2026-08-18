# Project: FinWise AI Chatbot Validation and Testing

## Architecture
- **Web & API Framework**: Flask 3.0 (`app.py`) with WSGI path normalization (`WSGIPathNormalizer`) supporting local runtime (port 5000) and Vercel serverless (`api/index.py`).
- **Core Endpoints**:
  - `/dashboard`: Unified single-page application (SPA) with dual modes (Mutual Fund Portfolio Audit & Bank Spending Analytics).
  - `/api/chat`: Multi-turn conversational AI chatbot advisor handling 9 institutional financial analysis prompts.
  - `/api/portfolio/*`: Mutual fund CAS statement parsing, health diagnostics, risk evaluation, and portfolio rebalancing.
  - `/api/*`: Bank transaction ingestion, category aggregation, income/expense tracking, trend analysis, and Gaussian anomaly detection.
- **Quantitative Engine**: `mf_analyzer/quant_engine.py` (XIRR Newton-Raphson, rolling returns, alpha attribution, cost drag, multi-asset decomposition, pairwise overlap).
- **Market Data & Tax Engine**: `mf_analyzer/market_data.py` (MFAPI.in NAV integration, caching) & `mf_analyzer/chatbot_engine.py` (Budget 2024 Section 112A/111A/50AA rules, SEBI SID mandates).
- **Client Visualization & Markdown Engine**: `static/js/dashboard.js` (Chart.js Line/Bar/Doughnut renderers, KaTeX math isolation, continuous sequential `<ol>` markdown parser).

## Feature Inventory
Every feature from the user request and survey is enumerated below with its assigned milestone:

| # | Feature | Description | Milestone | Source |
|---|---------|-------------|-----------|--------|
| 1 | Portfolio XIRR & Newton-Raphson Calculation | Newton-Raphson solver with short-vintage holding (<180d) compounding distortion linearization guard and Line chart artifact | M1 | ORIGINAL_REQUEST §R1.1 |
| 2 | 4-Tier Rolling Form & Alpha Attribution | 4-Tier classification (In-Form, On-Track, Off-Track, Out-of-Form) and active alpha ($\alpha_{1Y}, \alpha_{3Y}$) vs benchmark TRI with Bar chart | M1 | ORIGINAL_REQUEST §R1.2 |
| 3 | Direct vs Regular Distributor Drag Simulation | $0 actual regular corpus audit and dynamic ₹5L regular drag simulation at 0.85% expense differential | M1 | ORIGINAL_REQUEST §R1.3 |
| 4 | Pairwise Stock Overlap & Concentration | Pairwise weighted overlap $\sum \min(w_{A,k}, w_{B,k})$ (0.00% PPFC vs Bandhan Small Cap) and Bar chart | M2 | ORIGINAL_REQUEST §R1.4 |
| 5 | Multi-Asset Allocation & Drift Blueprint | 3-way fund decomposition (50% Eq / 25% Debt / 25% Comm), drift from 60% Moderate target, and 3-step SIP rebalancing blueprint with Doughnut chart | M2 | ORIGINAL_REQUEST §R1.5 |
| 6 | Real Estate & Geographic Exposure Audit | 0.00% direct REIT exposure audit without keyword false-positives and ~4.2% global tech exposure reporting | M2 | ORIGINAL_REQUEST §R1.6 |
| 7 | 30-Day Step-by-Step Optimization Checklist | Prioritized 30-day checklist (Phase 1 SIP glidepath, Phase 2 Direct plan switch, Phase 3 quarterly drift check) | M3 | ORIGINAL_REQUEST §R1.7 |
| 8 | Bank Spending Summary & Savings Rate | Consolidated inflow (₹8.40L), outflow (₹5.12L), net savings (₹3.27L), savings rate (39.01%), and category breakdown with Doughnut chart | M3 | ORIGINAL_REQUEST §R1.8 |
| 9 | Statistical Spending Anomaly Detection | Two-tailed Gaussian Z-score outlier detection ($Z = (x-\mu)/\sigma > 2.0$) with Bar chart | M3 | ORIGINAL_REQUEST §R1.9 |
| 10 | Budget 2024 Statutory Tax Benchmark | Section 112A equity LTCG (12.5% above ₹1.25L exemption), Section 111A STCG (20.0%), Section 50AA debt fund slab taxation without indexation post 1-Apr-2023 | M4 | ORIGINAL_REQUEST §R2 |
| 11 | SEBI Scheme Mandates & Exit Loads | Scheme Information Documents (SIDs) exit load verification (SBI Ultra Short 0.00% NIL, Bandhan Small Cap 1.0% <1Y, PPFC 2% <1Y/1% 1-2Y/NIL >2Y) | M4 | ORIGINAL_REQUEST §R2 |
| 12 | Visual Chart.js Artifact Rendering | Interactive Line, Bar, and Doughnut charts with valid datasets and disabled Cartesian scales for Doughnut charts | M5 | ORIGINAL_REQUEST §R3 |
| 13 | Continuous Ordered List Markdown Rendering | Ordered list markdown parsing retaining continuous sequence (1, 2, 3...) across nested child `<ul>` bullets and blank lines | M5 | ORIGINAL_REQUEST §R3 |
| 14 | Opaque-Box E2E Testing Suite | Multi-tier automated browser and API test harness validating 100% of institutional prompts and UI invariants | E2E | ORIGINAL_REQUEST Acceptance Criteria |

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| M1 | Portfolio Performance & Drag Engine Verification | Features 1, 2, 3 (XIRR, Rolling Form, Alpha, Cost Drag) | none | DONE |
| M2 | Asset Allocation, Overlap & Geographic Audit | Features 4, 5, 6 (Overlap, Multi-asset drift, 0.00% REIT) | M1 | DONE |
| M3 | Action Plan & Spending Analytics Verification | Features 7, 8, 9 (30-day checklist, Spending summary, Z-score anomalies) | M1 | DONE |
| M4 | Statutory & SEBI Benchmark Verification | Features 10, 11 (Budget 2024 Sec 112A/111A/50AA, SEBI SID Exit loads) | M1, M2 | DONE |
| M5 | UI Chart Artifacts & Markdown Rendering Verification | Features 12, 13 (Chart.js Line/Bar/Doughnut schemas, sequential `<ol>`) | M1, M2, M3 | DONE |
| E2E | Dual-Track E2E Test Suite Creation & Execution | Feature 14 (Tiers 1-4 comprehensive automated test suite) | none | DONE |
| M-Final | Final Acceptance & Adversarial Hardening | Pass 100% E2E tests + Tier 5 Adversarial Hardening + Forensic Audit | M1-M5, E2E | DONE |

## Interface Contracts
### Client `/api/chat` Request Contract
```json
{
  "message": "string (mandatory user query)",
  "session_id": "string (optional session uuid)",
  "audit_id": "string (optional audit uuid)",
  "history": [
    { "role": "user | assistant", "content": "string" }
  ],
  "risk_profile": "Conservative | Moderate | Aggressive"
}
```

### Server `/api/chat` Response Contract
```json
{
  "reply": "string (markdown formatted response with KaTeX math and sequential lists)",
  "chart": {
    "type": "line | bar | doughnut",
    "title": "string",
    "data": {
      "labels": ["string"],
      "datasets": [
        {
          "label": "string",
          "data": [number],
          "borderColor": "string | string[]",
          "backgroundColor": "string | string[]"
        }
      ]
    }
  } | null,
  "session_id": "string",
  "risk_profile": "string"
}
```

## Code Layout
- `app.py`: Flask application server, web routes, REST API endpoints, WSGI normalizer.
- `mf_analyzer/chatbot_engine.py`: ChatbotAdvisorEngine, prompt handlers, rule engine, chart generation.
- `mf_analyzer/quant_engine.py`: Financial math, XIRR, rolling returns, overlap matrix, asset allocation.
- `mf_analyzer/market_data.py`: AMFI NAV integration, MFAPI.in client, caching.
- `mf_analyzer/cas_parser.py`: CAMS/KFintech CAS statement parsing.
- `static/js/dashboard.js`: Client-side application controller, Chart.js renderers, markdown list parser.
- `static/css/dashboard.css`: Styling, layout grid, dark theme, responsive design.
- `templates/dashboard.html`: Main dashboard SPA layout.
- `tests/`: Automated test suite (`test_all_user_prompts.py`, `test_chatbot_api.py`, `test_quant_engine.py`, `test_adversarial_quant.py`, `test_adversarial_deep_verify.py`, etc.).
