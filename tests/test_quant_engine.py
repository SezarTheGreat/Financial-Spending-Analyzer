"""
Unit tests for Deterministic Python Quant Diagnostics Engine
"""
import pytest
from mf_analyzer.quant_engine import QuantEngine
from mf_analyzer.cas_parser import load_demo_portfolio
from mf_analyzer.schemas import Holding, Transaction


def test_compute_cagr():
    engine = QuantEngine()
    # 100 to 200 in 3 years -> (2)^(1/3) - 1 = 25.99%
    cagr = engine.compute_cagr(100.0, 200.0, 3.0)
    assert cagr == 25.99

    # Edge cases
    assert engine.compute_cagr(0, 100, 1) is None
    assert engine.compute_cagr(100, 0, 1) is None
    assert engine.compute_cagr(100, 100, 0) is None


def test_4_tier_form_classification():
    engine = QuantEngine()

    # In-Form: High positive alpha
    tier, _ = engine.classify_form_tier(
        "Fund A", "Flexi Cap", "DIRECT", cagr_1y=26.0, cagr_3y=22.0, alpha_1y=4.0, alpha_3y=3.5
    )
    assert tier == "In-Form"

    # On-Track: Matching benchmark
    tier, _ = engine.classify_form_tier(
        "Fund B", "Large Cap", "DIRECT", cagr_1y=19.0, cagr_3y=16.5, alpha_1y=0.5, alpha_3y=0.3
    )
    assert tier == "On-Track"

    # Off-Track: Lagging recent performance
    tier, _ = engine.classify_form_tier(
        "Fund C", "Mid Cap", "REGULAR", cagr_1y=23.0, cagr_3y=22.0, alpha_1y=-3.0, alpha_3y=-0.5
    )
    assert tier == "Off-Track"

    # Out-of-Form: Severe chronic underperformance
    tier, _ = engine.classify_form_tier(
        "Fund D", "Small Cap", "REGULAR", cagr_1y=25.0, cagr_3y=21.0, alpha_1y=-7.0, alpha_3y=-6.0
    )
    assert tier == "Out-of-Form"


def test_cost_drag_calculator():
    engine = QuantEngine()
    portfolio = load_demo_portfolio()
    cost_drag = engine.calculate_cost_drag(portfolio.holdings)

    assert cost_drag.total_regular_corpus == 1050000.00  # 500k Mirae + 350k HDFC + 200k Nippon
    assert cost_drag.affected_schemes_count == 3
    assert cost_drag.annual_expense_drag_amount == round(1050000.00 * 0.0085, 2)  # 8,925.00
    assert cost_drag.projected_10yr_cost_drag > 0
    assert cost_drag.projected_10yr_direct_value > cost_drag.projected_10yr_regular_value


def test_asset_drift_conservative():
    engine = QuantEngine()
    portfolio = load_demo_portfolio()
    allocation = engine.calculate_asset_allocation(portfolio.holdings)
    
    # Portfolio is ~80%+ Equity
    drift = engine.calculate_asset_drift(allocation, "Conservative")
    assert drift.risk_profile == "Conservative"
    assert drift.drift_status in ["High Risk Drift", "Over-Allocated to Equity"]
    assert drift.drift_pct > 0


def test_asset_drift_aggressive():
    engine = QuantEngine()
    portfolio = load_demo_portfolio()
    allocation = engine.calculate_asset_allocation(portfolio.holdings)
    
    drift = engine.calculate_asset_drift(allocation, "Aggressive")
    assert drift.risk_profile == "Aggressive"
    assert drift.target_equity_range == [75.0, 95.0]


def test_overlap_matrix():
    engine = QuantEngine()
    portfolio = load_demo_portfolio()
    overlap = engine.calculate_overlap_matrix(portfolio.holdings)

    assert len(overlap.pairs) > 0
    # Overlap between Mirae Large Cap and HDFC Top 100 should be substantial (>30%)
    mirae_hdfc_pair = next(
        (p for p in overlap.pairs if "Mirae" in p.fund_a and "HDFC" in p.fund_b or "HDFC" in p.fund_a and "Mirae" in p.fund_b),
        None
    )
    assert mirae_hdfc_pair is not None
    assert mirae_hdfc_pair.overlap_percentage > 25.0


@pytest.mark.asyncio
async def test_full_quant_diagnostics():
    engine = QuantEngine()
    portfolio = load_demo_portfolio()
    diagnostics = await engine.run_diagnostics(portfolio, "Moderate")

    assert len(diagnostics.rolling_cagrs) == len(portfolio.holdings)
    assert len(diagnostics.form_ratings) == len(portfolio.holdings)
    assert diagnostics.cost_drag.total_regular_corpus > 0
    assert diagnostics.asset_allocation.equity_pct > 0
