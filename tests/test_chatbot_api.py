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
    engine = ChatbotAdvisorEngine(api_key="")
    portfolio = load_demo_portfolio()
    quant_engine = QuantEngine()
    diag = await quant_engine.run_diagnostics(portfolio, "Moderate")

    payload = engine.generate_chat_response_payload(
        user_message="Give me a sure-shot fund to buy right now that will deliver a guaranteed 25% return next year.",
        portfolio=portfolio,
        quant_diagnostics=diag,
        risk_profile="Moderate"
    )

    reply = payload["reply"]
    assert "SEBI Regulatory Compliance" in reply or "SEBI" in reply
    assert "Mutual fund investments are subject to market risks" in reply
    assert "guaranteed 25%" not in reply

@pytest.mark.asyncio
async def test_chatbot_edge_case_short_vintage_xirr():
    engine = ChatbotAdvisorEngine(api_key="")
    portfolio = load_demo_portfolio()
    quant_engine = QuantEngine()
    diag = await quant_engine.run_diagnostics(portfolio, "Moderate")

    payload = engine.generate_chat_response_payload(
        user_message="How does the quant engine calculate XIRR for a portfolio with multiple SIPs and sudden lump-sum redemptions?",
        portfolio=portfolio,
        quant_diagnostics=diag,
        risk_profile="Moderate"
    )

    reply = payload["reply"]
    chart = payload.get("chart")
    assert "XIRR" in reply and "Newton-Raphson" in reply
    assert chart is not None
    assert chart["type"] == "line"

@pytest.mark.asyncio
async def test_chatbot_edge_case_taxation_budget_2024():
    engine = ChatbotAdvisorEngine(api_key="")
    portfolio = load_demo_portfolio()
    quant_engine = QuantEngine()
    diag = await quant_engine.run_diagnostics(portfolio, "Moderate")

    payload = engine.generate_chat_response_payload(
        user_message="If I redeem ₹3,00,000 from an equity fund after holding for 18 months with a gain of ₹1,80,000, what is my exact LTCG tax liability under AY 2025-26?",
        portfolio=portfolio,
        quant_diagnostics=diag,
        risk_profile="Moderate"
    )

    reply = payload["reply"]
    chart = payload.get("chart")
    assert "125,000" in reply or "1.25 Lakh" in reply
    assert "7,150" in reply
    assert chart is not None
    assert chart["type"] == "bar"

@pytest.mark.asyncio
async def test_chatbot_edge_case_debt_taxation_sec_50aa():
    engine = ChatbotAdvisorEngine(api_key="")
    portfolio = load_demo_portfolio()
    quant_engine = QuantEngine()
    diag = await quant_engine.run_diagnostics(portfolio, "Moderate")

    payload = engine.generate_chat_response_payload(
        user_message="I bought SBI Ultra Short Duration Fund in May 2024 and want to exit now. Will I get indexation benefit or 20% LTCG?",
        portfolio=portfolio,
        quant_diagnostics=diag,
        risk_profile="Moderate"
    )

    reply = payload["reply"]
    chart = payload.get("chart")
    assert "Section 50AA" in reply or "50AA" in reply
    assert "No Indexation" in reply or "no indexation" in reply.lower()
    assert "Slab Rate" in reply or "slab rate" in reply.lower()
    assert chart is not None
    assert chart["type"] == "bar"

@pytest.mark.asyncio
async def test_chatbot_edge_case_target_nav_and_debt_switch():
    engine = ChatbotAdvisorEngine(api_key="")
    portfolio = load_demo_portfolio()
    quant_engine = QuantEngine()
    diag = await quant_engine.run_diagnostics(portfolio, "Moderate")

    payload = engine.generate_chat_response_payload(
        user_message="What is the target NAV for Parag Parikh Flexi Cap Fund for December 2026? Should I immediately sell my debt funds to buy it?",
        portfolio=portfolio,
        quant_diagnostics=diag,
        risk_profile="Moderate"
    )

    reply = payload["reply"]
    assert "SEBI" in reply
    assert "Target NAV" in reply or "target NAV" in reply or "speculative" in reply.lower()
    assert "Stock Overlap" not in reply  # Ensuring it is NOT incorrectly routed to stock overlap

@pytest.mark.asyncio
async def test_chatbot_edge_case_small_vs_large_cap_alpha():
    engine = ChatbotAdvisorEngine(api_key="")
    portfolio = load_demo_portfolio()
    quant_engine = QuantEngine()
    diag = await quant_engine.run_diagnostics(portfolio, "Moderate")

    payload = engine.generate_chat_response_payload(
        user_message="Why is a Small Cap fund with a 35% 1-year return classified as 'In-Form', but a Large Cap fund with 14% return might be 'Off-Track'?",
        portfolio=portfolio,
        quant_diagnostics=diag,
        risk_profile="Moderate"
    )

    reply = payload["reply"]
    chart = payload.get("chart")
    assert "Benchmark" in reply or "Alpha" in reply
    assert "In-Form" in reply and "Off-Track" in reply
    assert chart is not None

@pytest.mark.asyncio
async def test_chatbot_edge_case_asset_drift_and_rebalance():
    engine = ChatbotAdvisorEngine(api_key="")
    portfolio = load_demo_portfolio()
    quant_engine = QuantEngine()
    diag = await quant_engine.run_diagnostics(portfolio, "Moderate")

    payload = engine.generate_chat_response_payload(
        user_message="My risk profile is Moderate (target 50%-70% Equity). If my actual equity allocation is 37.5%, what is my drift and how should I rebalance?",
        portfolio=portfolio,
        quant_diagnostics=diag,
        risk_profile="Moderate"
    )

    reply = payload["reply"]
    chart = payload.get("chart")
    assert "Drift" in reply
    assert "Rebalancing" in reply or "rebalance" in reply.lower()
    assert chart is not None

@pytest.mark.asyncio
async def test_chatbot_edge_case_stock_overlap_ppfc_bandhan():
    engine = ChatbotAdvisorEngine(api_key="")
    portfolio = load_demo_portfolio()
    quant_engine = QuantEngine()
    diag = await quant_engine.run_diagnostics(portfolio, "Moderate")

    payload = engine.generate_chat_response_payload(
        user_message="I hold Parag Parikh Flexi Cap and Bandhan Small Cap. What is our stock overlap, and do they share major holdings?",
        portfolio=portfolio,
        quant_diagnostics=diag,
        risk_profile="Moderate"
    )

    reply = payload["reply"]
    chart = payload.get("chart")
    assert "0.00%" in reply or "Overlap" in reply
    assert chart is not None
    assert chart["type"] == "bar"

@pytest.mark.asyncio
async def test_chatbot_edge_case_regular_plan_drag():
    engine = ChatbotAdvisorEngine(api_key="")
    portfolio = load_demo_portfolio()
    quant_engine = QuantEngine()
    diag = await quant_engine.run_diagnostics(portfolio, "Moderate")

    payload = engine.generate_chat_response_payload(
        user_message="What is the 10-year wealth impact if ₹5,00,000 of my corpus is in Regular Plans with a 0.85% distributor commission drag at 12% gross CAGR?",
        portfolio=portfolio,
        quant_diagnostics=diag,
        risk_profile="Moderate"
    )

    reply = payload["reply"]
    chart = payload.get("chart")
    assert "113,911" in reply or "1,13,911" in reply or "4,250" in reply
    assert chart is not None
    assert chart["type"] == "line"
