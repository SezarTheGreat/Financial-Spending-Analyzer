# Challenger 2 Report: Adversarial Coverage, UI Invariants & Quantitative Verification

**Verdict**: `APPROVE`
**Date**: 2026-08-16
**Author**: Challenger 2 (Adversarial Coverage & UI Invariants Verifier)

---

## Executive Summary
Challenger 2 executed an exhaustive, adversarial verification across the FinWise AI Chatbot engine (`mf_analyzer/chatbot_engine.py`), quantitative calculation models (`mf_analyzer/quant_engine.py`), API routing (`app.py`), and client-side UI rendering contracts (`static/js/dashboard.js`). 

All 9 institutional prompt workflows, statutory tax rules (Budget 2024 Sections 112A, 111A, 50AA), SEBI SID mandates, Chart.js dataset invariants, sequential `<ol>` markdown rendering with nested `<ul>` sub-bullets, and real estate exposure false-positive immunity have been empirically stress-tested and validated with **100% pass rate**.

---

## Adversarial Review & Stress-Test Results

### 1. 9 Institutional Prompts & Variations Coverage
Every institutional prompt was evaluated against exact queries, fuzzy colloquial queries, and adversarial variations:

| Prompt ID | Domain | Prompt Query | Math / Statutory Assertion | Visual Chart Spec | Result |
|:---:|---|---|---|---|:---:|
| **1** | Portfolio XIRR & Newton-Raphson | *"What is my consolidated portfolio XIRR, and how is it calculated compared to simple CAGR or absolute return?"* | Solves multi-SIP cash flows via Newton-Raphson; applies SEBI short-vintage guard (<180d) | Line chart (Distortion curve) | **PASS** |
| **2** | 4-Tier Rolling Form & Active Alpha | *"Analyze the rolling form and alpha of each fund in my portfolio. Are any funds classified as Off-Track or Out-of-Form?"* | Correctly quotes form tiers (In-Form, On-Track, Off-Track, Out-of-Form) and active alpha ($\alpha_{1Y}, \alpha_{3Y}$) vs benchmark TRI | Bar chart (Relative Alpha) | **PASS** |
| **3** | Direct vs Regular Plan Distributor Drag | *"Do I have any Regular mutual fund plans? If so, what is the estimated 10-year compounded wealth leakage from intermediary commission?"* | Reports ₹0.00 actual regular corpus and dynamic ₹5L regular drag simulation at 0.85% expense differential | None (Text math) | **PASS** |
| **4** | Stock Overlap & Concentration | *"What is the stock overlap between my equity funds? Which specific common stocks have the highest concentration across multiple schemes?"* | 0.00% overlap for PPFC vs Bandhan Small Cap; highlights zero blue-chip duplication | Bar chart (Stock overlap) | **PASS** |
| **5** | Multi-Asset Allocation & Drift Blueprint | *"My current risk profile is Moderate. What is my actual equity vs debt vs commodities allocation, and what specific rebalancing actions should I take to match an Aggressive profile?"* | Actual Equity: 37.89%, Debt: 39.85%, Commodities: 22.27%; Drift: -22.11% from 60% Moderate midpoint | Doughnut chart (Allocation) | **PASS** |
| **6** | Real Estate & Global Exposure | *"What is my exposure to international real estate in this portfolio?"* | 0.00% direct REIT exposure (0 keyword false-positives); identifies ~4.2% US tech allocation | None (Audit narrative) | **PASS** |
| **7** | Prioritized 30-Day Checklist | *"Give me a prioritized, step-by-step checklist to optimize this portfolio over the next 30 days."* | Phase 1 (Days 1–7) SIP glidepath, Phase 2 (Days 8–15) Direct plan switch, Phase 3 (Days 16–30) Drift monitoring | None (Roadmap `<ol>`) | **PASS** |
| **8** | Bank Spending Summary & Savings Rate | *"What was my total expense, net savings, and savings rate for the period, and which category accounts for the largest share of my outflows?"* | Inflow: ₹8,40,000, Outflow: ₹5,12,300, Net Savings: ₹3,27,700, Savings Rate: 39.01%; Housing (32.40%) & Groceries (24.11%) | Doughnut chart (Expenses) | **PASS** |
| **9** | Statistical Spending Anomaly Detection | *"Were there any spending anomalies or irregular transaction spikes detected in my statement?"* | Two-tailed Gaussian Z-score outlier detection ($Z > 2.0$); flags Apple Store (Z=3.42), Car Insurance (Z=2.85), Flights (Z=2.61), Appliance Repair (Z=2.14) | Bar chart (Z-score spikes) | **PASS** |

---

### 2. Statutory Benchmark Cross-Validation (Budget 2024 & SEBI Mandates)

1. **Budget 2024 Equity LTCG (Section 112A)**:
   - Exemption threshold: First ₹1,25,000 exempt from long-term capital gains tax.
   - Tax rate: 12.5% on net capital gains exceeding ₹1.25 Lakh.
   - Surcharge & Cess: 4% Health and Education Cess added ($12.5\% \times 1.04 = 13.0\%$).
   - *Test Case*: ₹3,00,000 redemption with ₹2,50,000 gain held 14M $\rightarrow$ Taxable Gain ₹1,25,000 $\rightarrow$ Base Tax ₹15,625 + ₹625 Cess = **₹16,250.00**. (Verified exact calculation in API output).

2. **Specified Debt Fund Taxation (Section 50AA)**:
   - Verified that debt funds (e.g. SBI Ultra Short Duration Fund) acquired post April 1, 2023 are classified as Specified Mutual Funds under Section 50AA.
   - All capital gains are taxed at individual income tax slab rates with **zero indexation benefit** regardless of holding duration.

3. **SEBI Scheme Information Document (SID) Exit Loads**:
   - SBI Ultra Short Duration Fund: **0.00% (NIL)** exit load across all holding horizons, 0 lock-in.
   - Bandhan Small Cap Fund: **1.00%** exit load if redeemed $< 365$ days, 0.00% thereafter.
   - Parag Parikh Flexi Cap Fund: **2.00%** if $< 365$ days, **1.00%** between 366–730 days, **0.00%** after 730 days.

---

### 3. UI Chart Schemas & Doughnut Scale Invariants

- **Chart Artifact Structure**:
  - Validated that all generated chart JSON objects adhere strictly to the contract: `type` in `["line", "bar", "doughnut"]`, non-empty `title`, `labels` list, and `datasets` list containing numeric data points.
- **Doughnut Scale Suppression**:
  - Inspected `static/js/dashboard.js` line 1569:
    ```javascript
    scales: chartSpec.type === 'doughnut' ? {} : {
      x: { grid: { display: false }, ticks: { font: { size: 10, family: "'DM Sans', sans-serif" } } },
      y: { grid: { color: 'rgba(0,0,0,0.05)' }, ticks: { font: { size: 10, family: "'DM Sans', sans-serif" } } }
    }
    ```
  - Cartesian `x` and `y` scales are explicitly disabled (`scales: {}`) for Doughnut charts, completely eliminating Chart.js console warnings and canvas rendering crashes.
  - Confirmed that dataset lengths match label counts across all doughnut chart outputs (e.g. 4 labels = 4 data points for Asset Allocation, 6 labels = 6 data points for Spending Breakdown).

---

### 4. Markdown Sequential List Parsing (`<ol>` with Nested `<ul>`)

- Inspected `static/js/dashboard.js` (`formatChatMarkdown` function lines 1461–1505) and executed algorithmic emulation in `tests/test_adversarial_deep_verify.py`.
- Verified that:
  - Top-level numbered items (`1.`, `2.`, `3.`) generate `<li value="1">`, `<li value="2">`, `<li value="3">`.
  - Nested sub-bullets (`   - Sub-bullet`) are wrapped in separate `<ul>` elements without terminating the outer `<ol>` state.
  - Numbering remains strictly continuous (1, 2, 3...) across nested bullets and blank lines, never resetting to 1.

---

### 5. Real Estate False-Positive Immunity Audit

- Executed compound adversarial queries combining real estate keywords with distributor drag terms:
  - *"Do I have any real estate with regular plan distributor drag?"*
  - *"What is my real estate and REIT exposure vs direct plan commission?"*
  - *"Is there any property or REIT investment leaking 0.85% expense ratio?"*
- Confirmed zero cross-domain keyword contamination: the engine accurately identifies 0.00% direct REIT/real estate exposure in the user's portfolio and does not hallucinate REIT holdings or confuse it with distributor drag.

---

### 6. Edge Cases, Boundary Conditions & Hostile Inputs

- **Empty / Whitespace Input**: Returns clean HTTP 400 Bad Request with `"Message cannot be empty."` error payload.
- **Oversized Queries (3000+ characters)**: Returns HTTP 200 OK without buffer overflow, memory exhaustion, or unhandled exceptions.
- **SQL / XSS Injections**: Correctly sanitized; KaTeX math isolation and HTML table formatters prevent script injection vulnerabilities.
- **Speculative / Guaranteed Return Demands**: Intercepted by `sanitize_advisor_response` and SEBI compliance rules, transforming illegal return promises into objective risk-adjusted analytics.
- **Mandatory SEBI Disclaimer**: Present on 100% of generated responses.

---

## Test Execution Summary

| Test Suite | Commands Run | Tests Executed | Tests Passed | Status |
|---|---|:---:|:---:|:---:|
| **Pytest Full Suite** | `.\venv\Scripts\python.exe -m pytest -v` | 43 | 43 | **PASS (100%)** |
| **Institutional Prompts Harness** | `.\venv\Scripts\python.exe tests/test_all_user_prompts.py` | 9 | 9 | **PASS (100%)** |
| **Deep Adversarial & UI Suite** | `.\venv\Scripts\python.exe tests/test_adversarial_deep_verify.py` | 6 | 6 | **PASS (100%)** |
| **Total Automated Executions** | — | **58** | **58** | **PASS (100%)** |

---

## Conclusion & Verdict
The FinWise AI Chatbot and Financial Spending Analyzer demonstrate complete architectural robustness, strict mathematical precision, full statutory compliance with Budget 2024 and SEBI mandates, and flawless UI visual invariant integrity.

**Final Challenger Verdict: `APPROVE`**.
