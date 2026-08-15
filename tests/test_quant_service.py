"""
Unit & Integration Tests for FinWise Quant Microservice (FastAPI + pyxirr)
"""
import pytest
from datetime import date
from fastapi.testclient import TestClient
from quant_service.main import app, compute_xirr_core, classify_form_tier_core

client = TestClient(app)

def test_health_endpoint():
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "healthy"
    assert "pyxirr" in data["libraries"]

def test_xirr_endpoint_exact():
    payload = {
        "cash_flows": [
            {"date": "2023-01-01", "amount": -100000.0},
            {"date": "2024-01-01", "amount": 115000.0}
        ]
    }
    resp = client.post("/quant/xirr", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["xirr"] is not None
    assert round(data["xirr"], 1) == 15.0
    assert data["absolute_return_pct"] == 15.0

def test_xirr_endpoint_short_vintage_guard():
    # 15-day investment with 3.69% gain should not explode to 200%+ XIRR
    payload = {
        "cash_flows": [
            {"date": "2026-05-15", "amount": -10412.25},
            {"date": "2026-08-14", "amount": 10796.28}
        ]
    }
    resp = client.post("/quant/xirr", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["xirr"] is not None
    assert 12.0 <= data["xirr"] <= 18.0
    assert data["is_linearized_guard_applied"] is True

def test_classify_form_tier_all_categories():
    # 1. Equity In-Form
    tier1, _ = classify_form_tier_core("Bandhan Small Cap", "Small Cap", 35.0, 28.0, 8.0, 5.0)
    assert tier1 == "In-Form"

    # 2. Equity On-Track
    tier2, _ = classify_form_tier_core("Parag Parikh Flexi Cap", "Flexi Cap", 22.0, 18.0, -0.75, 1.2)
    assert tier2 == "On-Track"

    # 3. Debt On-Track
    tier3, _ = classify_form_tier_core("SBI Ultra Short", "Ultra Short Debt", 6.43, 7.20, -0.37, 0.70)
    assert tier3 == "On-Track"

    # 4. Commodities On-Track
    tier4, _ = classify_form_tier_core("Invesco Gold ETF", "Commodities", 45.0, 32.0, 0.0, 0.0)
    assert tier4 == "On-Track"

    # 5. Out-of-Form
    tier5, _ = classify_form_tier_core("Laggard Fund", "Large Cap", 8.0, 9.0, -8.0, -5.5)
    assert tier5 == "Out-of-Form"

def test_performance_audit_endpoint():
    payload = {
        "holdings": [
            {
                "folio_number": "FOLIO-01",
                "scheme_name": "Parag Parikh Flexi Cap Fund - Direct Plan - Growth",
                "amfi_code": "122639",
                "plan_type": "DIRECT",
                "current_value": 1011.79,
                "cost_value": 1000.00,
                "transactions": [
                    {"date": "2026-05-15", "amount": 1000.00}
                ]
            },
            {
                "folio_number": "FOLIO-02",
                "scheme_name": "SBI Ultra Short Duration Fund - Direct Plan - Growth",
                "amfi_code": "120828",
                "plan_type": "DIRECT",
                "current_value": 3015.29,
                "cost_value": 3000.00,
                "transactions": [
                    {"date": "2026-05-15", "amount": 3000.00}
                ]
            }
        ],
        "risk_profile": "Moderate"
    }
    resp = client.post("/quant/performance-audit", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_current_value"] == 4027.08
    assert data["total_cost_value"] == 4000.00
    assert data["total_gain"] == 27.08
    assert data["portfolio_xirr"] is not None
    assert len(data["fund_rolling_diagnostics"]) == 2
