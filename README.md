# 💰 Personal Finance Spending Analyzer


[![Live Demo](https://img.shields.io/badge/Live%20Demo-View%20App-brightgreen?style=for-the-badge)](https://financial-spending-analyzer-ioyg.vercel.app/)

## 📌 Overview
 
Managing personal finances gets hard once hundreds of transactions pile up. Most people know how much they earn but have little visibility into where it actually goes.
 
The **Personal Finance Spending Analyzer** turns raw transaction data into meaningful financial insight. It cleans, categorizes, stores, analyzes, and visualizes financial transactions to help users understand their spending habits and overall financial health - going beyond basic expense tracking with an automated Financial Health Score, statistical anomaly detection, and budget recommendations based on historical patterns.
 
An interactive dashboard lets users explore their financial data directly in the browser, backed by a persistent PostgreSQL database (via Supabase) so uploaded data isn't lost between sessions.
 
## 🎯 Project Objectives
 
- Analyze personal transaction data effectively
- Understand spending behavior across categories
- Identify areas where expenses can be reduced
- Track savings and financial performance over time
- Detect unusually large or suspicious expenses
- Generate meaningful financial insights automatically
- Persist user data reliably across sessions via a real database
- Provide a user-friendly analytics dashboard for decision-making
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
 
## 📊 Exploratory Data Analysis
 
- **Transaction Distribution:** distribution of amounts, common spending ranges
- **Category Analysis:** total spend by category, average transaction value, category frequency
- **Time-Series Analysis:** monthly spending/income trends, savings trends
- **Spending Composition:** category breakdown, percentage contribution
- **Heatmap Analysis:** monthly spending intensity across categories, seasonal behavior
- **Correlation Analysis:** relationships between numerical financial metrics

- 
## 🏥 Financial Health Score
 
A single 0-100 metric combining:
- Savings Rate
- Expense Consistency
- Category Spending Distribution


| Score Range | Financial Status |
|---|---|
| 80–100 | Excellent |
| 60–79 | Good |
| 40–59 | Average |
| Below 40 | Needs Improvement |

### 6. Smart Insights Generation

The system automatically identifies:

* Highest spending category
* Lowest spending category
* Best savings month
* Worst savings month
* Spending warnings
* Budget recommendations

### 7. Anomaly Detection

Statistical methods are used to detect unusually large transactions that may indicate:

* Overspending
* Unexpected purchases
* Financial irregularities

### 8. Dashboard Development

An interactive Streamlit dashboard is created to present all insights visually.

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
* Transactions significantly different from normal behavior

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

The Streamlit dashboard includes:

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

### Machine Learning & Analytics

* Scikit-Learn

---

## 📁 Project Structure

```text
Personal-Finance-Spending-Analyzer/

├── data/
│   └── transactions.csv
│
├── notebooks/
│   └── finance_analyzer.ipynb
│
├── app.py
│
├── requirements.txt
│
├── README.md
│
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

---

## 🛠 Tech Stack

### Backend

* Python
* Flask
* Pandas
* NumPy

### Frontend

* HTML5
* CSS3
* JavaScript
* Chart.js

### Development Tools

* VS Code
* Git
* GitHub

---

# 🚀 Running the Project Locally

## 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/financial-analyzer.git
```

```bash
cd financial-analyzer
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

---

# 📸 Screenshots

## Landing Page

![Landing Page](assets/LandingPage.png)

----

## Dashboard Overview

![Dashboard](assets/Dashboard.png)

----
## Financial Health Score

![Health Score](assets/HealthScore.png)

---

# 📌 Current Status

### Working

* CSV Upload
* Financial Analytics
* Dashboard Visualizations
* AI Insights
* Anomaly Detection
* Local Execution

### Under Development

* Production Deployment
* Deployment-specific API compatibility
* Performance Optimization
* Enhanced CSV Compatibility

---

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
* Problem Solving

---
## 🏆 Key Takeaways

This project showcases how data analytics can be applied to personal finance management. By transforming raw transaction data into actionable insights, the analyzer helps users understand spending behavior, improve financial awareness, and make informed budgeting decisions.

The project combines data science, visualization, and dashboard development into a complete end-to-end analytics solution suitable for portfolio presentation and real-world applications.

---

# 📄 License

This project is intended for educational and portfolio purposes.


