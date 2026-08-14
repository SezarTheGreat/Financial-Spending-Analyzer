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
    assert response.status_code == 422


def test_analyze_cas_invalid_file():
    # Sending dummy bytes that are not a valid CAS PDF
    response = client.post(
        "/api/portfolio/analyze-cas",
        files={"file": ("test.pdf", b"this is not a valid pdf content", "application/pdf")},
        data={"password": "ABCDE1234F", "risk_profile": "Moderate"},
    )
    assert response.status_code == 400
