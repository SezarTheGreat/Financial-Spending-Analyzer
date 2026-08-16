# 💰 Personal Finance Spending & Mutual Fund AI Portfolio Analyzer


[![Live Demo](https://img.shields.io/badge/Live%20Demo-View%20App-brightgreen?style=for-the-badge)](https://financial-spending-analyzer-ioyg.vercel.app/)

## 📌 Overview
 
Managing personal finances gets hard once hundreds of transactions pile up. Most people know how much they earn but have little visibility into where it actually goes.
 
The **Personal Finance Spending Analyzer** turns raw transaction data into meaningful financial insight. It cleans, categorizes, stores, analyzes, and visualizes financial transactions to help users understand their spending habits and overall financial health - going beyond basic expense tracking with an automated Financial Health Score, statistical anomaly detection, and budget recommendations based on historical patterns.
 
An interactive dashboard lets users explore their financial data directly in the browser, backed by a persistent PostgreSQL database (via Supabase) so uploaded data isn't lost between sessions.

In addition to bank transaction intelligence, the platform features the **FinWise Mutual Fund Intelligence & AI Advisor**, extending capabilities to Consolidated Account Statement (CAS) audits, cashflow-level Newton-Raphson XIRR solvers, 4-tier rolling return form ratings, distributor expense drag calculations, pairwise stock overlap matrices, and an interactive Gemini-powered conversational advisor with dynamic Chart.js generation.
 
## 🎯 Project Objectives
 
- Analyze personal transaction data effectively
- Understand spending behavior across categories
- Identify areas where expenses can be reduced
- Track savings and financial performance over time
- Detect unusually large or suspicious expenses
- Generate meaningful financial insights automatically
- Persist user data reliably across sessions via a real database
- Provide a user-friendly analytics dashboard for decision-making
- Audit Consolidated Account Statements (CAS PDFs, Excel, CSV) for Indian Mutual Funds
- Evaluate portfolio performance using exact Newton-Raphson XIRR with short-vintage linearization guards
- Benchmark scheme performance using 4-tier rolling form and active alpha attribution
- Detect redundant equity diversification using pairwise weighted stock overlap matrices
- Calculate distributor commission drag (Direct vs Regular plans) over 5, 10, and 20-year horizons
- Provide real-time conversational AI financial advisory with Budget 2024 statutory tax calculations and SEBI SID exit load validations

## 📂 Dataset Description
 
Transactions are uploaded via CSV and persisted to a PostgreSQL database (Supabase), with the following core fields:
 
| Column | Description |
|---|---|
| Date | Transaction date |
| Description | Transaction description or merchant |
| Amount | Transaction amount (positive for income, negative for expenses) |
| Month | Month extracted from transaction date |
| Year | Year extracted from transaction date |
| Day | Day of the week extracted from transaction date |
| Category | Expense category assigned through categorization rules |
 
**Sample Data**
 
| Date | Description | Amount | Category |
|---|---|---|---|
| 2026-04-01 | Salary | 38751 | Income |
| 2026-04-02 | Electricity Bill | -2311 | Household |
| 2026-04-03 | Uber | -348 | Transport |
| 2026-04-04 | Amazon | -2096 | Shopping |
 
## ⚙️ Project Workflow
 
**1. Data Collection**
Transactions are uploaded as CSV through the dashboard and written to a PostgreSQL database hosted on Supabase, replacing the earlier local-CSV-only flow.
 
**2. Data Cleaning**
- Removing duplicate records
- Handling missing values
- Converting date fields into datetime format
- Validating transaction amounts before persisting to the database
 
**3. Feature Engineering**
- Month, Year, Day of Week extracted from transaction dates
- Expense categories assigned based on transaction descriptions
  
**4. Exploratory Data Analysis (EDA)**
- Income patterns
- Expense distribution
- Category-wise spending
- Monthly spending trends
- Savings trends
- Spending concentration
  
**5. Financial Health Evaluation**
A custom Financial Health Score (0-100) built from:
- Savings Rate
- Expense Stability
- Spending Behavior Metrics
  
**6. Automated Insights Generation**
Rule-based logic identifies:
- Highest / lowest spending category
- Best / worst savings month
- Spending warnings
- Budget recommendations
  
**7. Anomaly Detection**
Statistical methods (e.g. deviation from category-wise spending norms) flag unusually large transactions that may indicate overspending, unexpected purchases, or irregularities.
 
**8. Dashboard Development**
An interactive dashboard presents all insights visually, reading live from the Postgres database.
 
---

## 🚀 Mutual Fund Intelligence & AI Quant Engine *(Extended Features by Jyotishman)*

**1. CAS Statement Parsing & Decryption**  
Ingests CAMS and KFintech Consolidated Account Statements (CAS PDFs, Excel, CSV) in-memory with password decryption, extracting scheme holdings, folios, units, purchase NAVs, and current valuations.

**2. Cashflow XIRR & Linearization Guards**  
Computes cashflow-level internal rate of return using Newton-Raphson solvers with short-vintage holding (<180 days) compounding distortion linearization guards.

**3. 4-Tier Rolling Form & Active Alpha Attribution**  
Classifies schemes into `In-Form`, `On-Track`, `Off-Track`, and `Out-of-Form` by benchmarking 1-year and 3-year rolling performance ($\alpha_{1Y}, \alpha_{3Y}$) against AMFI category Total Return Indices (TRI).

**4. Direct vs. Regular Distributor Drag Calculator**  
Models cumulative wealth leakage and opportunity cost over 5, 10, and 20-year horizons caused by intermediary regular plan commission differentials (0.85%).

**5. Pairwise Weighted Stock Overlap & Concentration**  
Computes pairwise stock overlaps $\sum \min(w_{A,k}, w_{B,k})$ across equity schemes to detect portfolio duplication and concentration risk.

**6. Multi-Asset Allocation & 3-Step SIP Rebalancing Blueprint**  
Decomposes holdings into Equity, Debt, and Commodities, evaluates drift against user risk profiles (Conservative, Moderate, Aggressive), and outlines a 3-step SIP rebalancing glidepath.

**7. FinWise Conversational AI Advisor & Dynamic Chart Generation**  
Provides multi-turn AI advisory powered by Google Gemini (with an instant deterministic fallback engine), rendering interactive Chart.js artifacts (Line, Bar, Doughnut), computing Budget 2024 capital gains tax liabilities (Section 112A equity LTCG at 12.5%, Section 111A STCG at 20.0%, Section 50AA debt fund taxation), and verifying SEBI SID exit load schedules.

---

## 📊 Exploratory Data Analysis

The project includes several analytical visualizations:

### Transaction Distribution Analysis

* Distribution of transaction amounts
* Identification of common spending ranges

### Category Analysis

* Total spending by category
* Average transaction value per category
* Category frequency distribution

### Time-Series Analysis

* Monthly spending trends
* Monthly income trends
* Savings trends over time

### Spending Composition

* Category spending breakdown
* Percentage contribution of each category

### Heatmap Analysis

* Monthly spending intensity across categories
* Seasonal spending behavior

### Correlation Analysis

* Relationships between numerical financial metrics

---

## 🏥 Financial Health Score

One of the unique features of this project is the Financial Health Score.

The score combines multiple financial indicators into a single metric ranging from 0 to 100.

### Factors Considered

* Savings Rate
* Expense Consistency
* Category Spending Distribution

### Score Interpretation

| Score Range | Financial Status  |
| ----------- | ----------------- |
| 80 - 100    | Excellent         |
| 60 - 79     | Good              |
| 40 - 59     | Average           |
| Below 40    | Needs Improvement |

This metric provides a quick overview of a user's financial condition.

---

## 🚨 Anomaly Detection

The project uses statistical techniques to identify unusually large expenses.

Examples include:

* Unexpected purchases
* Excessive spending events
* Transactions significantly different from normal behavior ($Z = (x - \mu) / \sigma > 2.0$)

This feature helps users recognize financial outliers that may require attention.

---

## 💡 Smart Insights

The analyzer automatically generates insights such as:

* Highest spending category
* Monthly savings performance
* Expense trends
* Overspending alerts
* Budget optimization suggestions
* Financial health recommendations

These insights help convert raw transaction data into actionable information.

---

## 📈 Dashboard Features

The dashboard includes:

### KPI Cards

* Total Income
* Total Expenses
* Total Savings
* Financial Health Score

### Interactive Visualizations

* Category Spending Analysis
* Monthly Expense Trends
* Income vs Expense Comparison
* Spending Distribution

### User Controls

* CSV Upload
* Category Filters
* Dynamic Data Exploration

### Insights Section

* Automated recommendations
* Spending observations
* Financial warnings

---

## 🏛️ System Architecture

```mermaid
flowchart TD
    subgraph Client ["Client Layer (Browser)"]
        UI["SPA Dashboard (HTML5 / Vanilla CSS / JS)"]
        Charts["Chart.js Renderers & KaTeX Math"]
        ChatModal["FinWise AI Chatbot Interface"]
    end

    subgraph Gateway ["Routing & Serverless Gateway"]
        Vercel["Vercel Serverless (api/index.py)"]
        WSGI["WSGIPathNormalizer Middleware"]
        Flask["Flask 3.0 Web Application (app.py)"]
    end

    subgraph CoreEngines ["Core Analytical Engines"]
        SpendEng["Spending Analytics & Anomaly Engine"]
        QuantEng["Quantitative Engine (XIRR, Overlap, Alpha)"]
        TaxEng["Budget 2024 Tax & SEBI Mandate Engine"]
        CASParser["CAMS / KFintech CAS Ingestion Parser"]
    end

    subgraph AIEngine ["AI & Advisory Engine"]
        Gemini["Google Gemini LLM Client"]
        Heuristic["Deterministic Heuristic Fallback Engine"]
        ChartGen["Dynamic Chart Artifact Generator"]
    end

    subgraph DataPersistence ["Persistence & External Services"]
        Supabase[("Supabase Cloud PostgreSQL")]
        MFAPI["AMFI / MFAPI.in NAV Live Feed"]
        R2[("Vector Storage / R2 Cache")]
    end

    UI --> Vercel --> WSGI --> Flask
    Flask --> SpendEng
    Flask --> QuantEng
    Flask --> CASParser
    Flask --> ChatModal
    ChatModal --> AIEngine
    AIEngine --> Gemini
    AIEngine --> Heuristic
    AIEngine --> ChartGen
    QuantEng --> MFAPI
    SpendEng --> Supabase
    QuantEng --> Supabase
    AIEngine --> Supabase
    QuantEng --> R2
```

---

## 📡 REST API Specification

### Spending & Cashflow Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/api/upload` | `POST` | Upload and normalize a bank transaction CSV |
| `/api/sample` | `GET` | Load default sample transaction dataset |
| `/api/overview` | `GET` | Retrieve total income, total expenses, net savings, and savings rate |
| `/api/categories` | `GET` | Category-wise expense aggregation and transaction counts |
| `/api/income-expense` | `GET` | Monthly income vs. expense comparison series |
| `/api/monthly` | `GET` | Monthly category expenditure matrix |
| `/api/weekly` | `GET` | Weekly spending patterns and weekday distribution |
| `/api/trends` | `GET` | Category spending trends over time |
| `/api/anomalies` | `GET` | Statistical two-tailed Gaussian Z-score outlier transactions |
| `/api/calendar` | `GET` | Daily expenditure intensity map for calendar heatmap |
| `/api/health` | `GET` | Financial Health Score (0-100) and breakdown metrics |
| `/api/insights` | `GET` | Rule-based budget recommendations and spending warnings |
| `/api/transactions` | `GET` | Paginated, searchable, and filtered transaction records |

### Mutual Fund & AI Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/api/portfolio/health` | `GET` | Check mutual fund engine and database connectivity |
| `/api/portfolio/analyze-cas` | `POST` | Parse and audit CAMS/KFintech CAS statement PDF (with optional password) |
| `/api/portfolio/analyze-demo` | `POST` | Load and audit the institutional demo mutual fund portfolio |
| `/api/portfolio/re-evaluate-risk` | `POST` | Recalculate portfolio health score and asset drift for a target risk profile |
| `/api/chat` | `POST` | Multi-turn conversational AI advisor with dynamic Chart.js generation |

---

## 🛠️ Technologies Used

### Programming Language

* Python

### Data Analysis

* Pandas
* NumPy

### Data Visualization

* Matplotlib
* Seaborn
* Plotly
* Chart.js

### Machine Learning & Analytics

* Scikit-Learn
* PyXIRR
* Casparser
* Google Gemini API (`google-genai`)

---

## 📁 Project Structure

```text
Personal-Finance-Spending-Analyzer/

├── transactions.csv
├── finance.ipynb
├── static/
│   ├── css/
│   │   ├── dashboard.css
│   │   └── style.css
│   └── js/
│       ├── app.js
│       └── dashboard.js
├── templates/
│   ├── index.html
│   ├── dashboard.html
│   └── about.html
├── mf_analyzer/
│   ├── ai_engine.py
│   ├── cas_parser.py
│   ├── chatbot_engine.py
│   ├── market_data.py
│   ├── quant_engine.py
│   └── schemas.py
├── api/
│   └── index.py
├── tests/
├── app.py
├── requirements.txt
├── README.md
└── assets/
```
---

## ✨ Features

* 📂 Upload your own bank transaction CSV
* 💰 Income, Expense & Savings Overview
* 📈 Monthly Spending Trends
* 🥧 Category-wise Expense Breakdown
* 📅 Weekly & Calendar Heatmaps
* ⚠️ Anomaly Detection for unusual transactions
* ❤️ Financial Health Score
* 🤖 AI-powered Financial Insights & Recommendations
* 📋 Transaction History with Pagination
* 🎨 Clean and responsive dashboard UI
* 📑 CAMS & KFintech CAS Statement PDF Parser with Password Support
* 📐 Precision Newton-Raphson Portfolio XIRR Calculation
* 📊 4-Tier Rolling CAGR Form Ratings & Benchmark Alpha Attribution
* 🔄 Pairwise Stock Overlap Matrix & Concentration Analysis
* 📉 Direct vs. Regular Plan 10-Year Expense Drag Simulation
* 💬 Multi-Turn AI Portfolio Chatbot Advisor with Dynamic Chart Artifacts
* ⚖️ Budget 2024 Statutory Capital Gains Tax Engine (LTCG 12.5%, STCG 20.0%, Section 50AA)

---

## 🛠 Tech Stack

### Backend

* Python
* Flask
* Pandas
* NumPy
* PyXIRR
* Pydantic
* Supabase PostgreSQL

### Frontend

* HTML5
* CSS3
* JavaScript
* Chart.js
* KaTeX

### Development Tools

* VS Code
* Git
* GitHub
* Vercel Serverless

---

# 🚀 Running the Project Locally

## 1. Clone the repository

```bash
git clone https://github.com/SezarTheGreat/Financial-Spending-Analyzer.git
```

```bash
cd Financial-Spending-Analyzer
```

---

## 2. Create a virtual environment

### Windows

```bash
python -m venv venv
```

Activate:

```bash
venv\Scripts\activate
```

---

### macOS / Linux

```bash
python3 -m venv venv
```

Activate:

```bash
source venv/bin/activate
```

---

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## 4. Start the Flask server

```bash
python app.py
```

---

## 5. Open your browser

Visit

```
http://127.0.0.1:5000
```

---

# 📁 Supported CSV Format

Your CSV should contain transaction records with columns similar to:

| Date       | Description   | Category      | Type    | Amount |
| ---------- | ------------- | ------------- | ------- | ------ |
| 2026-04-01 | Salary Credit | Income        | Income  | 45000  |
| 2026-04-02 | House Rent    | Housing       | Expense | 14000  |
| 2026-04-03 | Swiggy        | Food & Dining | Expense | 520    |

The application automatically normalizes many common CSV formats, including different column names for dates, descriptions, and amounts.

---

# 📊 Dashboard Modules

* Overview
* Income vs Expense
* Monthly Overview
* Category Analysis
* Spending Trends
* Weekly Breakdown
* Calendar Heatmap
* Anomaly Detection
* Financial Health Score
* AI Insights
* Transaction History
* MF Overview & Risk Drift
* Holdings & Rolling Form
* Stock Overlap Matrix
* AI Chatbot Advisor

---

# 📸 Screenshots

## Bank Spending Analytics *(Original Core Features)*

### Landing Page

![Landing Page](assets/LandingPage.png)

----

### Dashboard Overview

![Dashboard](assets/Dashboard.png)

----

### Financial Health Score

![Health Score](assets/HealthScore.png)

---

## Mutual Fund Portfolio Intelligence & AI Advisor *(Jyotishman's Features)*

### Portfolio Overview, XIRR & Risk Drift

![MF Portfolio Audit](assets/MFPortfolioAudit.png)

----

### Pairwise Stock Overlap Matrix & Concentration Analysis

![Stock Overlap Matrix](assets/StockOverlap.png)

----

### Holdings Breakdown & 4-Tier Rolling Return Form Ratings

![Holdings & Rolling Form](assets/HoldingsRollingForm.png)

----

### FinWise AI Conversational Advisor with Dynamic Chart Artifacts

![AI Chatbot Advisor](assets/AIChatbotAdvisor.png)

----

### System Architecture & Contributor Attribution

![Architecture & About](assets/ArchitectureAbout.png)

---

# 📌 Current Status

### Working

* CSV Upload
* Financial Analytics
* Dashboard Visualizations
* AI Insights
* Anomaly Detection
* CAS Statement PDF/Excel/CSV Parsing
* Newton-Raphson XIRR Engine
* 4-Tier Rolling Form Ratings & Alpha Attribution
* Stock Overlap Matrix & Concentration Analysis
* Direct vs Regular Plan Expense Drag Simulation
* FinWise Gemini AI Chatbot with Dynamic Chart Artifacts
* Budget 2024 Tax Schedules (Section 112A/111A/50AA)
* Supabase PostgreSQL Database Persistence
* Vercel Serverless Deployment
* Local Execution

### Under Development

* Multi-account banking API aggregation
* Automated SIP mandate management
* Advanced macroeconomic scenario stress-testing

---

## 🚀 Future Enhancements

Planned improvements include:

* Bank statement integration
* AI-powered transaction categorization
* Advanced expense forecasting
* Personalized financial recommendations
* Goal-based savings tracking
* Automated PDF report generation
* Cloud deployment
* Multi-user support

---

## 🎓 Skills Demonstrated

This project demonstrates practical experience in:

* Data Cleaning
* Data Wrangling
* Feature Engineering
* Exploratory Data Analysis
* Statistical Analysis
* Data Visualization
* Dashboard Development
* Anomaly Detection
* Business Insight Generation
* Financial Mathematics (Newton-Raphson XIRR, Rolling CAGRs, Alpha Attribution)
* Portfolio Optimization (Overlap Matrix, Asset Drift, Fee Drag Simulation)
* Conversational AI & LLM Structured Tool Calling
* Problem Solving

---

## 👥 Contributors & Attribution

* **Sakshi Singh Tanwar** ([@slashthose](https://github.com/slashthose))
  * **Role**: Original Creator & Core Foundation
  * **Contributions**: Designed and engineered the core **Financial Spending Analyzer** framework. Built the end-to-end bank statement parsing pipelines, category classification engine, expense trend heuristics, and statistical spending anomaly detection algorithms.
  * **Original Repository**: [slashthose/Financial-Spending-Analyzer](https://github.com/slashthose/Financial-Spending-Analyzer)

* **Jyotishman Barman** ([@SezarTheGreat](https://github.com/SezarTheGreat))
  * **Role**: Mutual Fund AI & Quantitative Architecture Contributor
  * **Contributions**: Architected and implemented the **Mutual Fund Intelligence Layer**, CAMS/KFintech CAS statement parsing, Newton-Raphson XIRR cashflow engine, 4-tier rolling form rating, stock overlap matrix, Budget 2024 taxation engine, interactive FinWise AI Chatbot advisor with dynamic Chart.js generation, Supabase PostgreSQL persistence, and Vercel serverless integration.
  * **Extended Repository**: [SezarTheGreat/Financial-Spending-Analyzer](https://github.com/SezarTheGreat/Financial-Spending-Analyzer)

---

## 🏆 Key Takeaways

This project showcases how data analytics and artificial intelligence can be applied to personal finance and wealth management. By transforming raw transaction data and mutual fund statements into actionable insights, the analyzer helps users understand spending behavior, eliminate hidden expense drag, improve financial awareness, and make informed budgeting and investment decisions.

The project combines data science, quantitative financial math, visualization, and dashboard development into a complete end-to-end analytics solution suitable for portfolio presentation and real-world applications.

---

# 📄 License

This project is open source and available under the **MIT License**. Intended for educational and portfolio purposes.
