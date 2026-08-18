"""
Integration tests for FastAPI Server Endpoints
"""
import pytest
from fastapi.testclient import TestClient
from mf_analyzer.server import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/api/portfolio/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "Mutual Fund Portfolio & AI Insight Analyzer"


def test_analyze_demo_endpoint():
    response = client.post("/api/portfolio/analyze-demo", data={"risk_profile": "Moderate"})
    assert response.status_code == 200
    data = response.json()
    assert "audit_id" in data
    assert "quant_diagnostics" in data
    assert "ai_insights" in data
    assert data["ai_insights"]["health_score"] > 0
    assert len(data["quant_diagnostics"]["rolling_cagrs"]) > 0
    assert len(data["quant_diagnostics"]["form_ratings"]) > 0
    assert "cost_drag" in data["quant_diagnostics"]
    assert "asset_drift" in data["quant_diagnostics"]
    assert "overlap_matrix" in data["quant_diagnostics"]


def test_analyze_demo_invalid_risk_profile():
    response = client.post("/api/portfolio/analyze-demo", data={"risk_profile": "SuperUltraHigh"})
    assert response.status_code in [422, 400]


def test_analyze_cas_invalid_file():
    # Sending dummy bytes that are not a valid CAS PDF
    response = client.post(
        "/api/portfolio/analyze-cas",
        files={"file": ("test.pdf", b"this is not a valid pdf content", "application/pdf")},
        data={"password": "ABCDE1234F", "risk_profile": "Moderate"},
    )
    assert response.status_code == 400


def test_re_evaluate_risk_endpoint():
    # 1. Run demo audit
    demo_resp = client.post("/api/portfolio/analyze-demo", data={"risk_profile": "Moderate"})
    assert demo_resp.status_code == 200
    audit_data = demo_resp.json()
    audit_id = audit_data["audit_id"]

    # 2. Re-evaluate with Aggressive risk profile
    reeval_resp = client.post(
        "/api/portfolio/re-evaluate-risk",
        json={"audit_id": audit_id, "risk_profile": "Aggressive"},
    )
    assert reeval_resp.status_code == 200
    reeval_data = reeval_resp.json()
    assert reeval_data["risk_profile"] == "Aggressive"
    assert reeval_data["quant_diagnostics"]["asset_drift"]["risk_profile"] == "Aggressive"
    assert reeval_data["quant_diagnostics"]["asset_drift"]["target_equity_range"] == [75.0, 95.0]
