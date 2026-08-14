"""
Unit tests for Structured AI Insight Layer (Gemini SDK & Schemas)
"""
import pytest
from mf_analyzer.ai_engine import AIEngine
from mf_analyzer.cas_parser import load_demo_portfolio
from mf_analyzer.quant_engine import QuantEngine
from mf_analyzer.schemas import AIAnalysisReport


@pytest.mark.asyncio
async def test_deterministic_insights_schema():
    engine = QuantEngine()
    ai_engine = AIEngine()
    portfolio = load_demo_portfolio()

    quant_diag = await engine.run_diagnostics(portfolio, "Moderate")
    report = ai_engine.generate_deterministic_insights(portfolio, quant_diag, "Moderate")

    assert isinstance(report, AIAnalysisReport)
    assert 0 <= report.health_score <= 100
    assert len(report.key_alerts) > 0
    assert len(report.fund_recommendations) == len(portfolio.holdings)
    assert len(report.step_by_step_rebalance_checklist) > 0

    # Ensure actions adhere to allowed literals
    valid_actions = {"HOLD", "CONTINUE_SIP", "PAUSE_SIP", "SWITCH_TO_DIRECT", "EXIT_AND_REINVEST"}
    for rec in report.fund_recommendations:
        assert rec.action in valid_actions
        assert len(rec.rationale) > 0

    # Check alert severities
    valid_severities = {"HIGH", "MEDIUM", "LOW"}
    for alert in report.key_alerts:
        assert alert.severity in valid_severities


@pytest.mark.asyncio
async def test_ai_engine_generate_insights():
    engine = QuantEngine()
    ai_engine = AIEngine()
    portfolio = load_demo_portfolio()

    quant_diag = await engine.run_diagnostics(portfolio, "Conservative")
    report = await ai_engine.generate_insights(portfolio, quant_diag, "Conservative")

    assert isinstance(report, AIAnalysisReport)
    assert 0 <= report.health_score <= 100
    assert "Conservative" in report.risk_alignment_verdict or "conservative" in report.risk_alignment_verdict.lower()
