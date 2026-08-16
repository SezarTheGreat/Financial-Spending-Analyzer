import pytest
import io
import os
import sys
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_spending_dashboard_routes(client):
    """Verify /spending-analytics and /spending routes return 200 and full component suite."""
    for route in ['/spending-analytics', '/spending']:
        res = client.get(route)
        assert res.status_code == 200
        html = res.get_data(as_text=True)

        # Brand & Header
        assert "FinWise" in html
        assert "Spending" in html
        assert "spending_dashboard.css" in html
        assert "spending_dashboard.js" in html

        # 7 Required Sections
        assert 'id="section-overview"' in html
        assert 'id="section-categories"' in html
        assert 'id="section-trends"' in html
        assert 'id="section-anomalies"' in html
        assert 'id="section-insights"' in html
        assert 'id="section-recommendations"' in html
        assert 'id="section-transactions"' in html

        # Top 4 KPI Cards
        assert 'id="statIncome"' in html
        assert 'id="statExpenses"' in html
        assert 'id="statSavings"' in html
        assert 'id="statSpendingRate"' in html

        # Mid & Bottom Visualizations
        assert 'id="donutChart"' in html
        assert 'id="incomeExpenseChart"' in html
        assert 'id="miniSpendChart"' in html
        assert 'id="trendChart"' in html
        assert 'id="monthlyChart"' in html
        assert 'id="weeklyChart"' in html

        # Right Sidebar Elements
        assert 'id="calGrid"' in html
        assert 'id="aiAlerts"' in html
        assert 'id="savingsWins"' in html

        # Sidebar Mini Health Widget
        assert 'id="healthRingSmall"' in html
        assert 'id="sidebarScore"' in html

        # Large Health Gauge in Recommendations
        assert 'id="healthRingBig"' in html
        assert 'id="healthBigScore"' in html
        assert 'id="healthBigGrade"' in html
        assert 'id="healthBars"' in html
        assert 'id="tipsGrid"' in html

def test_spending_static_assets(client):
    """Verify static CSS and JS assets are served properly."""
    css_res = client.get('/static/css/spending_dashboard.css')
    assert css_res.status_code == 200
    assert "--cream:" in css_res.get_data(as_text=True)

    js_res = client.get('/static/js/spending_dashboard.js')
    assert js_res.status_code == 200
    assert "loadAllSpendingData" in js_res.get_data(as_text=True)

def test_spending_api_suite(client):
    """Verify all 11 bank spending endpoints return valid structured JSON."""
    # 1. Sample data trigger
    res_sample = client.get('/api/sample')
    assert res_sample.status_code == 200
    data_sample = res_sample.get_json()
    assert data_sample['success'] is True
    assert 'summary' in data_sample

    # 2. Overview
    res_ov = client.get('/api/overview')
    assert res_ov.status_code == 200
    ov = res_ov.get_json()
    assert 'total_income' in ov
    assert 'total_expenses' in ov
    assert 'net_savings' in ov
    assert 'savings_rate' in ov
    assert 'spending_rate' in ov

    # 3. Categories
    res_cat = client.get('/api/categories')
    assert res_cat.status_code == 200
    cat = res_cat.get_json()
    assert 'labels' in cat and len(cat['labels']) > 0
    assert 'amounts' in cat
    assert 'percentages' in cat

    # 4. Income vs Expense
    res_ie = client.get('/api/income-expense')
    assert res_ie.status_code == 200
    ie = res_ie.get_json()
    assert 'months' in ie
    assert 'income' in ie
    assert 'expense' in ie
    assert 'savings' in ie

    # 5. Monthly & Weekly
    res_m = client.get('/api/monthly')
    assert res_m.status_code == 200
    assert 'months' in res_m.get_json()

    res_w = client.get('/api/weekly')
    assert res_w.status_code == 200
    assert 'peak_day' in res_w.get_json()

    # 6. Trends
    res_tr = client.get('/api/trends')
    assert res_tr.status_code == 200
    assert 'dates' in res_tr.get_json()

    # 7. Anomalies
    res_an = client.get('/api/anomalies')
    assert res_an.status_code == 200
    assert 'anomalies' in res_an.get_json()

    # 8. Calendar
    res_cal = client.get('/api/calendar')
    assert res_cal.status_code == 200
    assert 'dates' in res_cal.get_json()

    # 9. Health & Insights
    res_h = client.get('/api/health')
    assert res_h.status_code == 200
    h = res_h.get_json()
    assert 'score' in h
    assert 'grade' in h

    res_ins = client.get('/api/insights')
    assert res_ins.status_code == 200
    ins = res_ins.get_json()
    assert 'insights' in ins
    assert 'tips' in ins

    # 10. Transactions
    res_tx = client.get('/api/transactions?page=1')
    assert res_tx.status_code == 200
    tx = res_tx.get_json()
    assert 'transactions' in tx
    assert len(tx['transactions']) > 0
    assert 'total' in tx

def test_csv_upload_endpoint(client):
    """Verify bank statement CSV upload parsing."""
    csv_content = (
        "Date,Description,Amount,Type,Category\n"
        "2026-01-01,Salary Credit,50000,income,Income\n"
        "2026-01-05,Groceries Supermarket,2500,expense,Food & Dining\n"
        "2026-01-10,Electricity Bill,1800,expense,Utilities\n"
    )
    data = {
        'file': (io.BytesIO(csv_content.encode('utf-8')), 'test_statement.csv')
    }
    res = client.post('/api/upload', data=data, content_type='multipart/form-data')
    assert res.status_code == 200
    json_data = res.get_json()
    assert json_data['success'] is True
    assert json_data['summary']['total_income'] == 50000

def test_mutual_fund_isolation_guardrail(client):
    """Verify Mutual Fund layers remain completely intact and unaffected."""
    res_mf_health = client.get('/api/portfolio/health')
    assert res_mf_health.status_code == 200
    assert res_mf_health.get_json()['status'] == 'healthy'

    res_dash = client.get('/dashboard')
    assert res_dash.status_code == 200

    res_port = client.get('/portfolio-analytics')
    assert res_port.status_code == 200
