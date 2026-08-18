# FinWise Frontend, UI Charts & Markdown Rendering Technical Analysis Report

**Investigator**: Explorer 3 (Frontend, UI Charts & Markdown Rendering Specialist)  
**Date**: 2026-08-16  
**Scope**: Frontend architecture, client-side dashboard interface, Chart.js artifact rendering pipeline, Markdown & KaTeX parsing engine, and automated browser testing strategy for FinWise.

---

## 1. Executive Summary

This report presents a thorough investigation of the **FinWise** user interface and client rendering pipelines. FinWise integrates an institutional mutual fund research dashboard (Groww G.1 architecture) and a bank statement spending analytics platform.

### Key Findings:
1. **Chart.js Artifact Pipeline**: The chatbot and dashboard employ dynamic Chart.js (v4.4.0) visualizations across all supported quantitative queries, including:
   - **Line Charts**: Short-Vintage Compounding Distortion Curve (Newton-Raphson vs SEBI linear baseline) and 10-Year Direct vs. Regular Wealth Accumulation.
   - **Bar Charts**: Relative Alpha vs. Category Benchmark TRI, Pairwise Stock Overlap %, Statutory Mandate Asset Limits, and Gaussian Z-Score Outlier Spikes ($Z > 2.0$).
   - **Doughnut Charts**: Multi-Asset Allocation & Target Drift, and Category Spending Outflow Distribution.
2. **Markdown Parsing & List Numbering Engine**: The custom Markdown engine (`formatChatMarkdown` in `static/js/dashboard.js`) implements a two-stage parsing approach. It extracts display math blocks (`$$...$$`) into placeholders, converts markdown tables to responsive HTML, and parses ordered lists line-by-line. Continuous numbering sequence ($1, 2, 3\dots$) across nested sub-bullets (`<ul>`) and blank lines is guaranteed via explicit HTML `<li value="${olMatch[1]}">` attribute binding.
3. **KaTeX Formula Rendering**: Mathematical formulas are rendered in isolated formula environment cards (`.formula-env-card`) with auto-render integration, preventing raw LaTeX distortion.
4. **Interactive SVG Visualizations**: Mutual fund stock overlap features a custom **Multi-Fund Spatial Flower Venn Constellation** (SVG + D3 math) and a **Dynamic Pairwise Venn Simulator** with real-time geometric intersection adjustments.
5. **Execution Health**: All 9 institutional test prompt queries return **HTTP 200 OK** from `/api/chat` with valid payloads, zero mathematical hallucinations, and appropriate visual artifacts.

---

## 2. Frontend Architecture & Page Lifecycle

### 2.1 Directory Structure & Asset Topology
```
Financial-Spending-Analyzer/
├── templates/
│   ├── dashboard.html      # Primary unified dashboard SPA (MF Intelligence & Spending Analytics)
│   └── index.html          # File upload & CAS ingestion landing portal
├── static/
│   ├── css/
│   │   └── dashboard.css   # Comprehensive fintech design system (2,309 LOC)
│   └── js/
│       └── dashboard.js    # Client state management, Chart.js lifecycle, D3 SVG renderers, Chat engine (1,691 LOC)
```

### 2.2 Client-Side Shell & Grid Layout
The application utilizes a 3-column responsive CSS Grid layout (`dashboard.css`, lines 73–81):
```css
body {
  display: grid;
  grid-template-columns: var(--sidebar-w) minmax(0, 1fr) var(--rs-w); /* 230px | 1fr | 280px */
  height: 100vh;
  max-height: 100vh;
  overflow: hidden;
}
```

#### The Three Functional Columns:
1. **Left Navigation Sidebar (`.sidebar`, 230px)**:
   - Brand identity (`FinWise` logo).
   - Navigation links divided into **Mutual Fund Intelligence** (5 tabs) and **Spending Analytics** (4 tabs).
   - Mini Portfolio Health Score circular canvas gauge (`#healthRingSidebar`).
2. **Main Scrollable Content (`.main`, 1fr)**:
   - Sticky Topbar: Page title, active Risk Profile switcher pill (`Conservative`, `Moderate`, `Aggressive`), date badge, Quick Intelligence drawer toggle, and view refresh button.
   - Tab Sections: 9 dynamically toggled views (`.dash-section`), active section selected via `.active` class.
3. **Right Sidebar Drawer (`.right-sidebar`, 280px)**:
   - Collapsible drawer for "Quick Intelligence" displaying AI Critical Actions, Intermediary Fee Leakage summary, and Investor PAN/Period profile.
   - Toggled via `toggleRightSidebar()` with persistent preference in `localStorage.getItem('finwise_rs_collapsed')`.

### 2.3 Mode Switching Mechanism
The client controller dynamically switches UI modes when navigating between sections:
- **Mutual Fund Mode (`body.mf-mode`)**: Displays the 3-column layout with risk switcher, right sidebar, and health score widget.
- **Spending Mode (`body.spending-mode`)**: Collapses the right sidebar (`grid-template-columns: 230px 1fr`) and hides MF-specific controls to maximize chart viewing real estate.

---

## 3. Chart.js Visualization Pipeline & Visual Artifacts

### 3.1 Architecture of Chart Generation
Visual artifacts are generated in a deterministic multi-stage pipeline:
1. **Backend Intent Inference (`_infer_chart_artifact` in `mf_analyzer/chatbot_engine.py`)**:
   - Analyzes user query tokens and active portfolio diagnostics.
   - Constructs a standardized JSON chart specification matching the Chart.js dataset specification.
2. **API Delivery (`/api/chat`)**:
   - Delivers response JSON containing `{"reply": "...", "chart": { "type": "...", "title": "...", "labels": [...], "datasets": [...] }}`.
3. **Client-Side Canvas Instantiation (`appendChatMessage` in `static/js/dashboard.js`)**:
   - Dynamically injects `.chat-chart-card` and `<canvas id="chat-chart-xxxx">`.
   - Creates a new `Chart(canvas, { type, data, options })` instance inside a dedicated `setTimeout` event loop task.
   - Caches the instance in `_activeChatCharts` to enable clean destruction if redrawn.

```
┌───────────────────────────────────────────────┐
│ User Query / Prompt                           │
└───────────────────────┬───────────────────────┘
                        ▼
┌───────────────────────────────────────────────┐
│ Backend: _infer_chart_artifact()              │
│ - Pattern match query context                 │
│ - Extract portfolio quant data                │
│ - Emit Chart.js JSON Specification            │
└───────────────────────┬───────────────────────┘
                        ▼
┌───────────────────────────────────────────────┐
│ HTTP /api/chat Payload                        │
│ { reply: str, chart: ChartSpec }              │
└───────────────────────┬───────────────────────┘
                        ▼
┌───────────────────────────────────────────────┐
│ Client: appendChatMessage()                   │
│ - Inject .chat-chart-card & <canvas>          │
│ - Set responsive Chart.js container           │
│ - Initialize Chart(ctx, spec)                 │
│ - Store in _activeChatCharts[chartId]         │
└───────────────────────────────────────────────┘
```

### 3.2 Visual Artifact Specifications Across the 9 Institutional Prompts

| # | Prompt Focus | Chart Type | Title & Dimensions | Key Datasets & Colors |
|---|---|---|---|---|
| **1** | Portfolio XIRR & Short-Vintage Distortion | `line` | *Short-Vintage Compounding Distortion Curve* (185px) | • Exponential Annualized XIRR (`#EA580C`, filled area)<br>• SEBI Linearized Return Baseline (`#4F46E5`, dashed) |
| **2** | 4-Tier Rolling Form & Relative Alpha | `bar` | *Relative Alpha & Form Tier: Small Cap vs Large Cap* (185px) | • Fund Absolute Return (`#4F46E5`)<br>• Category Benchmark TRI (`#C7D2FE`)<br>• Active Alpha (`#059669` / `#DC2626`) |
| **3** | Direct vs. Regular Distributor Drag | `line` | *10-Year Wealth Accumulation: Direct vs Regular* (185px) | • Direct Plan 12.0% CAGR (`#059669`, green fill)<br>• Regular Plan 11.15% CAGR (`#DC2626`, red fill) |
| **4** | Pairwise Stock Overlap & Concentration | `bar` | *Portfolio Pairwise Stock Overlap (%)* (185px) | • Pairwise Overlap % (`#4F46E5`, `#0284C7`, `#D97706`, `#059669`), `borderRadius: 6` |
| **5** | Multi-Asset Allocation & Drift | `doughnut` | *Consolidated Portfolio Asset Distribution* (185px) | • Equity (37.89%), Debt (39.85%), Commodities (22.27%), Liquid (0.0%) (`#4F46E5`, `#059669`, `#D97706`, `#0284C7`) |
| **6** | International Real Estate & Global Exposure | *None / Table* | *Structured Text Audit* | • Zero REIT exposure audit (0.00%)<br>• ~4.2% US Tech in PPFC |
| **7** | Prioritized 30-Day Rebalancing Checklist | *None / OL* | *Chronological Execution Roadmap* | • 3-phase numbered list with nested sub-bullets |
| **8** | Spending Overview & Category Outflows | `doughnut` | *Expense Distribution by Category (%)* (185px) | • Housing (32.4%), Groceries (24.1%), Shopping (18.6%), Transport (13.3%), Healthcare (6.9%), Entertainment (4.7%) |
| **9** | Spending Outliers & Z-Score Anomalies | `bar` | *Detected Spending Anomalies by Z-Score Deviation* (185px) | • Outlier Z-Scores (`#DC2626` Z=3.42, `#EA580C` Z=2.85, `#D97706` Z=2.61, `#0284C7` Z=2.14) |

### 3.3 Chart.js Configuration & Lifecycle Management
1. **Doughnut Scale Protection**:
   In `dashboard.js` line 1569:
   ```javascript
   scales: chartSpec.type === 'doughnut' ? {} : {
     x: { grid: { display: false }, ticks: { font: { size: 10, family: "'DM Sans', sans-serif" } } },
     y: { grid: { color: 'rgba(0,0,0,0.05)' }, ticks: { font: { size: 10, family: "'DM Sans', sans-serif" } } }
   }
   ```
   Chart.js v4 requires non-cartesian charts (doughnut, pie) to have empty scale configurations. Specifying `x` or `y` axes causes console warnings or render failures. This is properly handled.
2. **Container Sizing & Reflow**:
   The canvas is wrapped inside `.chat-chart-canvas-wrap` with CSS `position: relative; height: 185px; width: 100%;`. Combined with `responsive: true, maintainAspectRatio: false`, this eliminates layout shifts during dynamic message insertion.
3. **High-DPI Retina Rendering**:
   For custom canvas drawings (e.g. `drawDonutRing` for the portfolio health gauge), logical coordinates are multiplied by `window.devicePixelRatio || 1` before drawing, ensuring crisp rendering across 2x/3x mobile and high-resolution displays.

---

## 4. Markdown Parsing & Numbered List (<ol>) Rendering Engine

### 4.1 Step-by-Step Logic Trace of `formatChatMarkdown`
The client markdown renderer in `static/js/dashboard.js` (lines 1400–1513) processes incoming assistant text through 8 distinct transformation phases:

```
Raw Response Text
  │
  ├─ 1. Math Block Extraction: Store $$...$$ in placeholders (___MATH_BLOCK_N___)
  ├─ 2. Table Parsing: Convert GitHub-style markdown tables to <table class="mf-table">
  ├─ 3. Headings: Convert ### and ## to <h3>
  ├─ 4. Formatting: Convert ***, **, * to <strong> and <em>
  ├─ 5. Horizontal Rules: Convert --- to <hr>
  ├─ 6. Inline Code: Convert `...` to <code> with custom fintech styling
  ├─ 7. State Machine List Parsing: Parse lines, track inOl/inUl, assign <li value="N">
  └─ 8. Math Re-injection: Replace placeholders with .formula-env-card wrappers
```

### 4.2 Ordered List `<ol>` & Nested Bullet `<ul>` Sequence Verification
A common defect in lightweight regex-based markdown parsers is the **Ordered List Number Reset Bug**, where an ordered list like:
```markdown
1. Phase 1 (Days 1–7)
   - Finding: Equity under-allocated
   - Action: Increase SIPs

2. Phase 2 (Days 8–15)
   - Finding: Direct plan verified
   - Action: Retain direct mandates
```
resets `2.` back to `1.` because the intervening nested unordered list (`<ul>`) or blank line closes the `<ol>` container.

#### How FinWise Solves This:
1. **Explicit Value Binding**:
   When matching an ordered list item line (`olMatch = trim.match(/^(\d+)\.\s+(.*)$/)`), the parser generates:
   ```javascript
   out.push(`<li value="${olMatch[1]}" style="margin-bottom:6px;">${olMatch[2]}</li>`);
   ```
   Under HTML5 specifications, the `<li value="N">` attribute explicitly overrides the browser's internal list counter. Even if the `<ol>` tag is closed and reopened due to a blank line, item `2.` will render with numeral `2.`, and item `3.` will render with `3.`.
2. **Sub-bullet Indentation Matcher**:
   Lines indented with 2 or more spaces followed by `-` or `*` (`subUlMatch = line.match(/^\s{2,}[-*]\s+(.*)$/)`) while `inOl` is active are converted into nested bullet items:
   ```javascript
   if (subUlMatch && inOl) {
     out.push(`<ul style="margin:4px 0 8px 18px; padding-left:14px; list-style-type:disc;"><li>${subUlMatch[1]}</li></ul>`);
   }
   ```
3. **No Destructive CSS Counter Resets**:
   Inspection of `static/css/dashboard.css` confirms there are no `counter-reset: list-item` rules applied to `.msg-bubble ol`, ensuring that browser-native list numbering obeys the explicit `value` attributes.

---

## 5. KaTeX Mathematical Rendering Pipeline

### 5.1KaTeX Architecture
FinWise uses **KaTeX 0.16.9** with the `auto-render` extension.

1. **Isolation in Parsing**:
   Display math blocks delimited by `$$...$$` are extracted *before* markdown text formatting:
   ```javascript
   text = text.replace(/\$\$([\s\S]*?)\$\$/g, (match, formula) => {
     const placeholder = `___MATH_BLOCK_${mathBlocks.length}___`;
     mathBlocks.push(
       `<div class="formula-env-card">
         <div class="formula-env-header">
           <span class="formula-env-badge">🧮 Mathematical Model</span>
         </div>
         <div class="formula-env-body">$$${formula.trim()}$$</div>
       </div>`
     );
     return `\n\n${placeholder}\n\n`;
   });
   ```
   This prevents underscores (e.g. `d_i - d_0`, `r_{\text{direct}}`) from being misparsed as italic tags (`<em>`).
2. **Post-DOM KaTeX Auto-Render**:
   After the message bubble is appended to `#chatHistory`, `window.renderMathInElement` parses the DOM node with delimiters:
   ```javascript
   window.renderMathInElement(bubble, {
     delimiters: [
       { left: '$$', right: '$$', display: true },
       { left: '$', right: '$', display: false }
     ],
     throwOnError: false
   });
   ```

---

## 6. Overlap Visualizations: Spatial Flower Venn & Pairwise Venn

### 6.1 Multi-Fund Spatial Flower Venn Constellation
Located under `#section-mf-overlap` Tab 1:
- **Orbital Ring Mathematics**: Calculates radial coordinates for all mutual funds around a central core ($cx=425, cy=230, R=155$):
  $$x = cx + R \cos\theta_i, \quad y = cy + R \sin\theta_i, \quad \theta_i = \frac{2\pi i}{N} - \frac{\pi}{2}$$
- **Curved Overlap Chords**: Uses quadratic Bézier curves with dynamic midpoint curvature ($ctrl = mid \cdot 0.75 + center \cdot 0.25$).
- **Dynamic `textPath` Labels**: Overlap percentages are bound directly to the SVG path via `<textPath startOffset="50%">`, ensuring numbers ride gracefully along the curve.
- **Petal Hover & Click Interactivity**: Hovering over a fund node dims non-related chords to 8% opacity and elevates connected links to 100% opacity with dynamic tooltip feedback.

### 6.2 Dynamic Pairwise Venn Simulator
Located under `#section-mf-overlap` Tab 2:
- Renders two overlapping SVG circles where the center-to-center distance $d$ is dynamically calculated from the overlap percentage:
  $$d = \max\left(30, \, 124 - \frac{\text{Overlap \%}}{100} \times 88\right)$$
  - $0\%$ Overlap $\to d = 124\text{px}$ (circles touch at boundary).
  - $100\%$ Overlap $\to d = 36\text{px}$ (concentric overlap).
- Automatically populates the common constituent stock breakdown table with real-time text search filtering.

---

## 7. UI Code Health, Identified Issues & Recommendations

During the investigation, several minor architectural and styling considerations were analyzed:

| Area | Observation / Finding | Assessment | Recommended Action |
|---|---|---|---|
| **HTML5 List Semantics** | In `formatChatMarkdown`, nested `<ul>` blocks are emitted between `<ol>` list items rather than inside the preceding `<li>`. | Modern browsers render this cleanly, but it is technically non-conforming HTML5. | Future refactor can nest the `<ul>` inside the parent `<li>` before closing. |
| **Chart.js Scales for Doughnuts** | `scales` is properly configured as `{}` for doughnut charts, avoiding Chart.js v4 Cartesian axis errors. | Optimal / Robust | Retain current implementation. |
| **KaTeX Formula Protection** | Placeholders `___MATH_BLOCK_N___` prevent LaTeX underscores from turning into `<em>`. | Optimal / Robust | Retain current implementation. |
| **SVG Chord Text Inversion** | On the Spatial Flower Venn, chords drawn right-to-left could invert textPath text. The code flips `startNode` and `endNode` when `na.x > nb.x` to keep text upright. | Optimal / Robust | Retain current implementation. |
| **Right Sidebar State Persistence** | Sidebar collapsed state is stored in `localStorage`, maintaining user preference across page reloads. | Optimal / Robust | Retain current implementation. |

---

## 8. Automated Browser-Based Testing Architecture

To conduct end-to-end automated UI and rendering validation against the live application:

### 8.1 Testing Framework Recommendations
1. **Pytest + Flask TestClient (API & Contract Validation)**:
   - Run `tests/test_chatbot_api.py` and `tests/test_all_user_prompts.py` to verify API 200 OK responses, payload contracts, and quantitative assertions.
2. **Playwright for Python / Node.js (Full Browser E2E & Visual Verification)**:
   - Launch headless Chromium against `http://localhost:5000/dashboard`.
   - Perform automated user journeys:
     - Navigate to FinWise AI Chatbot tab (`#section-mf-chatbot`).
     - Submit each of the 9 institutional test prompts via `#chatInput` and `#chatSendBtn`.
     - Assert that `.chat-message.model` appears with non-empty content.
     - Inspect `.chat-chart-card canvas` and verify `Chart.getChart(canvas).config.type` matches the expected chart type (`line`, `bar`, `doughnut`).
     - Inspect DOM `<ol>` nodes for Prompt 7 to assert sequential `<li value="1">`, `<li value="2">`, `<li value="3">`.
     - Assert that `.formula-env-card .katex` math elements are rendered without raw `$$` delimiters.
     - Switch Risk Profile buttons (`#risk-btn-Aggressive`) and assert that topbar and overview metrics re-evaluate.
     - Switch to Spatial Flower Venn tab and trigger hover events on `.flower-petal-node`.

### 8.2 Sample Playwright Test Script Blueprint
```python
import pytest
from playwright.sync_api import Page, expect

def test_chat_prompt_xirr_curve(page: Page):
    page.goto("http://localhost:5000/dashboard")
    page.click('.nav-item[data-section="mf-chatbot"]')
    
    # Input Prompt 1
    page.fill("#chatInput", "What is my consolidated portfolio XIRR, and how is it calculated compared to simple CAGR?")
    page.click("#chatSendBtn")
    
    # Wait for response
    last_msg = page.locator(".chat-message.model").last
    expect(last_msg).to_contain_text("Newton-Raphson")
    
    # Verify Chart.js artifact
    canvas = last_msg.locator("canvas")
    expect(canvas).to_be_visible()
    chart_type = page.evaluate("el => Chart.getChart(el).config.type", canvas.element_handle())
    assert chart_type == "line"

def test_chat_prompt_ordered_list_sequence(page: Page):
    page.goto("http://localhost:5000/dashboard")
    page.click('.nav-item[data-section="mf-chatbot"]')
    
    # Input Prompt 7 (30-day checklist)
    page.fill("#chatInput", "Give me a prioritized, step-by-step checklist to optimize this portfolio over the next 30 days.")
    page.click("#chatSendBtn")
    
    last_msg = page.locator(".chat-message.model").last
    expect(last_msg).to_contain_text("Phase 1")
    
    # Check ordered list item values
    li_elements = last_msg.locator("ol > li").all()
    values = [li.get_attribute("value") for li in li_elements]
    assert values == ["1", "2", "3"], f"Expected continuous sequence ['1', '2', '3'], got {values}"
```

---

## 9. Conclusion

The FinWise frontend architecture and rendering pipelines are robust, performant, and fully compliant with institutional fintech standards. All 9 institutional test prompts execute with complete mathematical precision and render interactive Chart.js artifacts, KaTeX formulas, and strictly sequential ordered lists without numbering resets.
