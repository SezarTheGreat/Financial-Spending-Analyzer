# Project Plan: FinWise AI Chatbot Validation and Testing

## Objective
Automate end-to-end browser and API validation of all 9 institutional FinWise AI Chatbot test prompts, verifying mathematical/statutory precision (MFAPI, Budget 2024, Section 112A/111A/50AA, SEBI mandates) and verifying interactive UI chart artifacts and continuous ordered list markdown rendering.

## Step-by-Step Plan
1. **Phase 0: Survey & Scope Mapping**
   - Dispatch 3 parallel Explorers:
     - Explorer 1 (API & Server Architecture): Map server startup, backend endpoints (/dashboard, /api/chat), request/response structures for all 9 prompts.
     - Explorer 2 (Quantitative & Statutory Logic): Map mathematical calculations (XIRR, Newton-Raphson, 4-tier rolling, alpha attribution, drag simulation, overlap, asset drift, real estate 0.00%, spending summary, Z-score anomalies) and Budget 2024 tax rules.
     - Explorer 3 (Frontend, Charts & Markdown Rendering): Map browser/UI layer, Chart.js artifact structures, markdown list renderer (<ol> with nested <ul>).
2. **Phase 1: PROJECT.md & TEST_INFRA.md Synthesis**
   - Synthesize survey findings into `PROJECT.md` (Feature Inventory, Architecture, Milestones, Interface Contracts).
   - Establish `TEST_INFRA.md` for the E2E testing framework.
3. **Phase 2: Dual Track Execution**
   - **Track 1 (E2E Testing Track)**: Build automated test suite for all 9 prompts (API + browser Playwright/Puppeteer/Selenium if available or headless browser harness), Chart.js validation, and markdown parsing checks -> Publish `TEST_READY.md`.
   - **Track 2 (Implementation/Validation/Fix Track)**: Validate each prompt, identify any calculation, taxation, chart payload, or UI markdown rendering bugs, and implement fixes.
4. **Phase 3: Final E2E Test Suite Run**
   - Execute full test suite against live server. Ensure 100% pass rate across all tiers.
5. **Phase 4: Adversarial Hardening & Forensic Audit**
   - Stress test edge cases with Challengers.
   - Run Forensic Auditor for integrity and authenticity verification.
6. **Phase 5: Synthesis & Handoff**
   - Produce comprehensive final report and message Sentinel for Victory Audit.
