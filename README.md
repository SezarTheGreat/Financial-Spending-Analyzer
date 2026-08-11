# 💰 Personal Finance Spending Analyzer


[![Live Demo](https://img.shields.io/badge/Live%20Demo-View%20App-brightgreen?style=for-the-badge)](https://financial-spending-analyzer-ioyg.vercel.app/)

## 📌 Overview

Managing personal finances can be challenging when hundreds of transactions accumulate over time. Most people know how much they earn but often lack visibility into where their money is actually being spent.

The Personal Finance Spending Analyzer is a data analytics project that transforms raw transaction data into meaningful financial insights. Using Python-based data analysis techniques, the project cleans, categorizes, analyzes, and visualizes financial transactions to help users better understand their spending habits and overall financial health.

The project goes beyond basic expense tracking by generating automated insights, calculating a custom Financial Health Score, identifying unusual spending behavior through anomaly detection, and providing budget recommendations based on historical transaction patterns.

An interactive Streamlit dashboard enables users to explore their financial data in a simple and intuitive way.

---

## 🎯 Project Objectives

The primary goals of this project are:

* Analyze personal transaction data effectively.
* Understand spending behavior across different categories.
* Identify areas where expenses can be reduced.
* Track savings and financial performance over time.
* Detect unusually large or suspicious expenses.
* Generate meaningful financial insights automatically.
* Create a user-friendly analytics dashboard for decision-making.

---

## 📂 Dataset Description

The dataset consists of personal financial transactions containing the following attributes:

| Column      | Description                                                     |
| ----------- | --------------------------------------------------------------- |
| Date        | Transaction date                                                |
| Description | Transaction description or merchant                             |
| Amount      | Transaction amount (positive for income, negative for expenses) |
| Month       | Month extracted from transaction date                           |
| Year        | Year extracted from transaction date                            |
| Day         | Day of the week extracted from transaction date                 |
| Category    | Expense category assigned through categorization rules          |

### Sample Data

| Date       | Description      | Amount | Category  |
| ---------- | ---------------- | ------ | --------- |
| 2025-01-01 | Salary           | 38751  | Income    |
| 2025-01-01 | Electricity Bill | -2311  | Household |
| 2025-01-02 | Uber             | -348   | Transport |
| 2025-01-03 | Amazon           | -2096  | Shopping  |

---

## ⚙️ Project Workflow

### 1. Data Collection

Transaction records are stored in CSV format and loaded into Python for analysis.

### 2. Data Cleaning

The dataset is cleaned by:

* Removing duplicate records
* Handling missing values
* Converting date fields into datetime format
* Validating transaction amounts

### 3. Feature Engineering

Additional features are extracted from transaction dates:

* Month
* Year
* Day of Week

Expense categories are assigned based on transaction descriptions.

### 4. Exploratory Data Analysis (EDA)

Comprehensive analysis is performed to understand:

* Income patterns
* Expense distribution
* Category-wise spending
* Monthly spending trends
* Savings trends
* Spending concentration

### 5. Financial Health Evaluation

A custom Financial Health Score is developed using:

* Savings Rate
* Expense Stability
* Spending Behavior Metrics

The score provides a quick assessment of overall financial performance.

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

# ⚠️ Important Notice

## Local Execution Recommended

The application is currently optimized for **local execution**.

Although a public deployment is available, certain dashboard features—including charts, analytics, and dynamic API responses—may not function correctly due to deployment-specific limitations that are still being resolved.

**For the complete experience, please clone the repository and run the application locally.**

This provides access to all dashboard features exactly as intended.

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


