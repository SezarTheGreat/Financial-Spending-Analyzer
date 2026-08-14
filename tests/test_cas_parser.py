"""
Unit tests for CAS Ingestion & Statement Parser
"""
import pytest
from mf_analyzer.cas_parser import detect_plan_type, detect_category, load_demo_portfolio, parse_cas_pdf
from mf_analyzer.schemas import Portfolio


def test_detect_plan_type():
    assert detect_plan_type("Parag Parikh Flexi Cap Fund - Direct Plan - Growth") == "DIRECT"
    assert detect_plan_type("Mirae Asset Large Cap Fund - Regular Plan - Growth") == "REGULAR"
    assert detect_plan_type("HDFC Top 100 Fund - Growth", advisor="ARN-12345") == "REGULAR"
    assert detect_plan_type("SBI Small Cap Fund - Growth", advisor="INA000000000") == "DIRECT"
    assert detect_plan_type("Nippon India Growth Fund") == "REGULAR"


def test_detect_category():
    assert detect_category("ICICI Prudential Liquid Fund") == "Liquid"
    assert detect_category("SBI Magnum Medium Duration Fund") == "Debt"
    assert detect_category("Kotak Balanced Advantage Fund") == "Hybrid"
    assert detect_category("Quant Small Cap Fund") == "Equity"


def test_load_demo_portfolio():
    portfolio = load_demo_portfolio()
    assert isinstance(portfolio, Portfolio)
    assert len(portfolio.holdings) == 7
    assert portfolio.total_current_value > 0
    assert portfolio.total_cost_value > 0
    assert portfolio.total_gain == round(portfolio.total_current_value - portfolio.total_cost_value, 2)
    
    direct_funds = [h for h in portfolio.holdings if h.plan_type == "DIRECT"]
    regular_funds = [h for h in portfolio.holdings if h.plan_type == "REGULAR"]
    assert len(direct_funds) == 4
    assert len(regular_funds) == 3


def test_parse_cas_pdf_empty_password():
    with pytest.raises(ValueError, match="password.*required"):
        parse_cas_pdf(b"dummy pdf bytes", password="")


def test_parse_cas_pdf_invalid_bytes():
    with pytest.raises(ValueError):
        parse_cas_pdf(b"invalid pdf content", password="ABCDE1234F")
