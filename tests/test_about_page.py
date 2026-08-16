import pytest
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_about_page_status_and_content(client):
    res = client.get('/about')
    assert res.status_code == 200
    html = res.get_data(as_text=True)
    
    # Verify title & brand
    assert "About — FinWise AI & Architecture" in html
    assert "Fin" in html and "Wise" in html
    
    # Verify Core Tech Architecture items (Dual Pillars)
    assert "Financial Spending Analyzer &amp; Cash Flow Engine" in html or "Financial Spending Analyzer & Cash Flow Engine" in html
    assert "Gaussian Outlier Engine" in html
    assert "CSV Normalization" in html
    assert "Heuristic Category Classifier" in html

    assert "Mutual Fund Intelligence &amp; Tri-Hybrid RAG Platform" in html or "Mutual Fund Intelligence & Tri-Hybrid RAG Platform" in html
    assert "Google Gemini" in html
    assert "Supabase Postgres" in html
    assert "LanceDB &amp; Cloudflare R2" in html or "LanceDB & Cloudflare R2" in html
    assert "PyMuPDF4LLM" in html
    assert "Quant Performance Engine" in html
    
    # Verify Authors & Links
    assert "Sakshi Singh Tanwar" in html
    assert "https://github.com/slashthose" in html
    assert "https://www.linkedin.com/in/sakshi-singh-tanwar/" in html
    
    assert "Sezar (Jyotishman)" in html
    assert "https://github.com/SezarTheGreat" in html
    assert "https://www.linkedin.com/in/sezarthegreat/" in html
    
    # Verify Statutory & Educational Disclaimer
    assert "Educational &amp; Portfolio Demonstration Disclaimer" in html or "Educational & Portfolio Demonstration Disclaimer" in html
    assert "SEBI-registered Investment Advisers" in html or "SEBI-registered" in html
    assert "RBI-regulated" in html

    # Verify Favicon links in html
    assert "/static/favicon.svg" in html

def test_favicon_static_assets(client):
    svg_res = client.get('/static/favicon.svg')
    assert svg_res.status_code == 200
    assert "<svg" in svg_res.get_data(as_text=True)
