# E2E Test Infra: FinWise AI Chatbot & Spending Analytics

## Test Philosophy
- Opaque-box, requirement-driven end-to-end verification.
- Validates all 9 institutional FinWise AI Chatbot test prompts through `/api/chat` and `/dashboard`.
- Strict zero-hallucination, exact penny/percentage mathematical accuracy, Budget 2024 statutory tax compliance (Sections 112A, 111A, 50AA), SEBI SID exit load fidelity, and visual Chart.js / Markdown `<ol>` integrity.

## Feature Inventory & Test Coverage
| # | Feature | Source (Requirement) | Tier 1 (Isolated) | Tier 2 (Boundary) | Tier 3 (Pairwise) | Tier 4 (Workload) |
|---|---------|----------------------|:-----------------:|:-----------------:|:-----------------:|:-----------------:|
| 1 | Portfolio XIRR & Short-Vintage Guard | ORIGINAL_REQUEST §R1.1 | 5 | 5 | ✓ | ✓ |
| 2 | 4-Tier Rolling Form & Alpha Attribution | ORIGINAL_REQUEST §R1.2 | 5 | 5 | ✓ | ✓ |
| 3 | Direct vs Regular Drag Simulation | ORIGINAL_REQUEST §R1.3 | 5 | 5 | ✓ | ✓ |
| 4 | Pairwise Stock Overlap & Concentration | ORIGINAL_REQUEST §R1.4 | 5 | 5 | ✓ | ✓ |
| 5 | Multi-Asset Allocation & Drift Blueprint | ORIGINAL_REQUEST §R1.5 | 5 | 5 | ✓ | ✓ |
| 6 | Real Estate Exposure Audit (0.00% REIT) | ORIGINAL_REQUEST §R1.6 | 5 | 5 | ✓ | ✓ |
| 7 | 30-Day Step-by-Step Optimization Checklist | ORIGINAL_REQUEST §R1.7 | 5 | 5 | ✓ | ✓ |
| 8 | Bank Spending Summary & Savings Rate | ORIGINAL_REQUEST §R1.8 | 5 | 5 | ✓ | ✓ |
| 9 | Statistical Spending Anomaly (Z > 2.0) | ORIGINAL_REQUEST §R1.9 | 5 | 5 | ✓ | ✓ |
| 10 | Budget 2024 Tax Law (112A, 111A, 50AA) | ORIGINAL_REQUEST §R2 | 5 | 5 | ✓ | ✓ |
| 11 | SEBI SID Mandates & Exit Loads | ORIGINAL_REQUEST §R2 | 5 | 5 | ✓ | ✓ |
| 12 | Visual Chart.js Artifacts (Line/Bar/Doughnut) | ORIGINAL_REQUEST §R3 | 5 | 5 | ✓ | ✓ |
| 13 | Markdown Ordered List Numbering (<ol>) | ORIGINAL_REQUEST §R3 | 5 | 5 | ✓ | ✓ |

## Test Architecture
- **Test Runner**: Pytest (`tests/`) and standalone verification scripts (`tests/test_all_user_prompts.py`, `tests/test_chatbot_api.py`, `tests/test_quant_engine.py`).
- **Invocation**:
  ```powershell
  .\venv\Scripts\python.exe -m pytest -v
  .\venv\Scripts\python.exe tests/test_all_user_prompts.py
  ```
- **Pass/Fail Semantics**: All test cases must return HTTP 200 OK, conform to strict JSON schemas, contain verified mathematical numbers, and render valid UI artifacts.

## Real-World Application Scenarios (Tier 4)
| # | Scenario | Features Exercised | Complexity |
|---|----------|--------------------|------------|
| 1 | Full Portfolio Audit & Rebalancing Flow | F1, F2, F4, F5, F7 | High |
| 2 | Statutory Tax Optimization & Exit Load Audit | F10, F11, F3, F7 | High |
| 3 | Complete Spending Diagnostics & Anomaly Alert | F8, F9, F12, F13 | Medium |
| 4 | Multi-Asset Risk Re-alignment & SIP Glidepath | F5, F6, F7, F12 | High |
| 5 | Cross-Engine Chatbot Stress & Concurrent Session Audit | F1-F13 | High |

## Coverage Thresholds
- **Tier 1 (Feature Coverage)**: ≥5 test cases per feature (Isolated happy-path checks).
- **Tier 2 (Boundary & Corner Cases)**: ≥5 test cases per feature (Zero corpus, negative returns, extreme horizons, missing inputs).
- **Tier 3 (Cross-Feature Combinations)**: Multi-feature interactions (Tax + Exit Loads, Overlap + Multi-Asset, Spending + Savings Rate).
- **Tier 4 (Real-World Application Scenarios)**: Realistic end-to-end user workflows.
