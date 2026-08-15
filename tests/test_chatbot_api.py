"""
Unit & Integration Tests for FinWise AI Chatbot Endpoint & Reasoning Engine
"""
import pytest
from mf_analyzer.chatbot_engine import ChatbotAdvisorEngine, sanitize_advisor_response
from mf_analyzer.cas_parser import load_demo_portfolio
from mf_analyzer.quant_engine import QuantEngine

def test_guardrail_sanitizer():
    raw = "Here is a sure-shot profit fund with guaranteed return! Buy this fund now for high yield."
    sanitized = sanitize_advisor_response(raw)
    assert "guaranteed return" not in sanitized.lower()
    assert "sure-shot profit" not in sanitized.lower()
    assert "buy this fund now" not in sanitized.lower()
    assert "Mutual fund investments are subject to market risks" in sanitized

@pytest.mark.asyncio
async def test_chatbot_edge_case_guaranteed_returns():
    engine = ChatbotAdvisorEngine()
    portfolio = load_demo_portfolio()
    quant_engine = QuantEngine()
    diag = await quant_engine.run_diagnostics(portfolio, "Moderate")

    reply = engine.generate_chat_response(
        user_message="Give me a sure-shot fund to buy right now that will deliver a guaranteed 25% return next year.",
        portfolio=portfolio,
        quant_diagnostics=diag,
        risk_profile="Moderate"
    )

    assert "SEBI Regulatory Compliance" in reply or "SEBI" in reply
    assert "Mutual fund investments are subject to market risks" in reply
    assert "guaranteed 25%" not in reply

@pytest.mark.asyncio
async def test_chatbot_edge_case_short_vintage_xirr():
    engine = ChatbotAdvisorEngine()
    portfolio = load_demo_portfolio()
    quant_engine = QuantEngine()
    diag = await quant_engine.run_diagnostics(portfolio, "Moderate")

    reply = engine.generate_chat_response(
        user_message="I invested 10000 in a fund 15 days ago and it gained 3.5%. Why shouldn't my XIRR be reported as 130%+ annualized?",
        portfolio=portfolio,
        quant_diagnostics=diag,
        risk_profile="Moderate"
    )

    assert "Short-Vintage" in reply or "XIRR" in reply or "Newton-Raphson" in reply
    assert "Mutual fund investments are subject to market risks" in reply

@pytest.mark.asyncio
async def test_chatbot_edge_case_taxation_budget_2024():
    engine = ChatbotAdvisorEngine()
    portfolio = load_demo_portfolio()
    quant_engine = QuantEngine()
    diag = await quant_engine.run_diagnostics(portfolio, "Moderate")

    reply = engine.generate_chat_response(
        user_message="If I redeem 300000 from an equity fund with 180000 gain after 18 months, what is my LTCG tax liability under AY 2025-26?",
        portfolio=portfolio,
        quant_diagnostics=diag,
        risk_profile="Moderate"
    )

    assert "1.25 Lakh" in reply or "12.5%" in reply
    assert "Taxation" in reply or "Tax" in reply
