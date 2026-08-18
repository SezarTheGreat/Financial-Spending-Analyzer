# Original User Request

## Initial Request — 2026-08-16T21:39:41+05:30

Automated end-to-end browser and API validation of all FinWise AI Chatbot prompts, verifying quantitative accuracy against live MFAPI data, Budget 2024 taxation rules, SEBI mandates, and verifying interactive UI chart artifacts.

Working directory: c:\Users\jyoti\OneDrive\Desktop\Financial-Spending-Analyzer
Integrity mode: development

## Requirements

### R1. Live Browser & API Prompt Execution
Execute all 9 institutional test prompts through the FinWise Chatbot interface (/dashboard and /api/chat):
1. Portfolio XIRR & Newton-Raphson short-vintage calculation.
2. 4-Tier rolling form classification and active alpha attribution table.
3. Direct vs. Regular Plan distributor commission drag simulation ($0 corpus audit).
4. Portfolio-wide pairwise stock overlap and stock concentration metrics.
5. Multi-asset allocation, target drift calculation, and SIP rebalancing blueprint.
6. International real estate and geographical exposure audit (0.00% REIT exposure).
7. Prioritized 30-day step-by-step portfolio optimization checklist.
8. Consolidated bank spending summary, net savings, and savings rate.
9. Statistical spending anomaly detection with Gaussian Z-score outliers (Z > 2.0).

### R2. Mathematical & Statutory Benchmark Cross-Validation
Cross-validate the chatbot's generated figures against official references:
- MFAPI.in: Historical daily NAV data for AMFI scheme codes (e.g. 122639 PPFC, 103176 SBI Ultra Short).
- Budget 2024 (AY 2025-26): Section 112A equity LTCG (12.5% above ₹1.25L), Section 111A STCG (20.0%), Section 50AA debt fund taxation at individual slab rates.
- SEBI Scheme Mandates: Scheme Information Documents (SIDs) for exit load schedules and asset limits.

### R3. Visual Chart Artifact & UI Markdown Rendering Verification
Verify that interactive Chart.js visualizations render properly in the browser:
- Line chart for Short-Vintage Compounding Distortion Curve.
- Bar chart for Relative Alpha and Stock Overlap.
- Doughnut chart for Asset Allocation and Expense Breakdown.
- Bar chart for Statistical Spending Anomalies (Z > 2.0).
- Confirm markdown ordered list numbering (<ol>) retains continuous sequence (1, 2, 3...) with nested <ul> sub-bullets.

## Acceptance Criteria

### Execution & HTTP Health
- [ ] All 9 prompt test requests return HTTP 200 OK from /api/chat.
- [ ] Response payloads contain zero mathematical hallucinations or undefined variables.

### Quantitative & Statutory Precision
- [ ] Equity LTCG calculations apply the ₹1.25 Lakh statutory exemption and 12.5% rate under Budget 2024.
- [ ] Debt schemes post April 1, 2023 are classified under Section 50AA without indexation.
- [ ] Real estate exposure correctly reports 0.00% without keyword false-positives from distributor drag.

### UI & Visual Verification
- [ ] Interactive Chart.js artifacts render with valid dataset structures on supported queries.
- [ ] Numbered list items in chat bubbles render sequentially (1, 2, 3...) without resetting to 1. on child bullet points.
