"""
Unit tests for Deterministic Quant Engine & Portfolio Diagnostic Algorithms
"""
import pytest
from datetime import date
from mf_analyzer.quant_engine import QuantEngine, calculate_xirr
from mf_analyzer.cas_parser import load_demo_portfolio
from mf_analyzer.schemas import Holding, Transaction


def test_calculate_xirr_basic():
    # Regular 1-year investment with 15% return
    cash_flows = [
        (date(2023, 1, 1), -100000.0),
        (date(2024, 1, 1), 115000.0)
    ]
    xirr = calculate_xirr(cash_flows)
    assert xirr is not None
    assert round(xirr, 1) == 15.0


def test_calculate_xirr_multi_sip():
    cash_flows = [
        (date(2023, 1, 1), -10000.0),
        (date(2023, 2, 1), -10000.0),
        (date(2023, 3, 1), -10000.0),
        (date(2024, 1, 1), 35000.0)
    ]
    xirr = calculate_xirr(cash_flows)
    assert xirr is not None
    assert xirr > 0.0


def test_compute_cagr():
    engine = QuantEngine()
    # 100k grows to 144k in 2 years = 20% CAGR
    cagr = engine.compute_cagr(100000.0, 144000.0, 2.0)
    assert cagr == 20.0


def test_classify_form_tier():
    engine = QuantEngine()
    
    # In-Form: High positive alpha
    tier, _ = engine.classify_form_tier(
        "Fund A", "Small Cap", "DIRECT", cagr_1y=35.0, cagr_3y=28.0, alpha_1y=8.0, alpha_3y=5.0
    )
    assert tier == "In-Form"

    # On-Track: Moderate alpha within baseline
    tier, _ = engine.classify_form_tier(
        "Fund B", "Flexi Cap", "DIRECT", cagr_1y=21.0, cagr_3y=18.0, alpha_1y=1.0, alpha_3y=1.0
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
    test_holdings = [
        Holding(
            folio_number="123", scheme_name="Fund Reg 1 - Regular Plan",
            isin="INF1", amfi_code="100", plan_type="REGULAR", category="Equity",
            units=100.0, nav=100.0, current_value=500000.0, cost_value=400000.0,
            unrealized_gain=100000.0, return_percentage=25.0, portfolio_weight_pct=50.0
        ),
        Holding(
            folio_number="124", scheme_name="Fund Reg 2 - Regular Plan",
            isin="INF2", amfi_code="101", plan_type="REGULAR", category="Equity",
            units=100.0, nav=100.0, current_value=500000.0, cost_value=400000.0,
            unrealized_gain=100000.0, return_percentage=25.0, portfolio_weight_pct=50.0
        ),
    ]
    cost_drag = engine.calculate_cost_drag(test_holdings)

    assert cost_drag.total_regular_corpus == 1000000.00
    assert cost_drag.affected_schemes_count == 2
    assert cost_drag.annual_expense_drag_amount == round(1000000.00 * 0.0085, 2)
    assert cost_drag.projected_10yr_cost_drag > 0
    assert cost_drag.projected_10yr_direct_value > cost_drag.projected_10yr_regular_value


def test_asset_drift_conservative():
    engine = QuantEngine()
    portfolio = load_demo_portfolio()
    allocation = engine.calculate_asset_allocation(portfolio.holdings)
    
    drift = engine.calculate_asset_drift(allocation, "Conservative")
    assert drift.risk_profile == "Conservative"
    assert drift.target_equity_range == [20.0, 40.0]


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
    # Overlap between Parag Parikh and Nippon Growth
    pp_nippon = next(
        (p for p in overlap.pairs if ("Parag" in p.fund_a and "Nippon" in p.fund_b) or ("Nippon" in p.fund_a and "Parag" in p.fund_b)),
        None
    )
    assert pp_nippon is not None
    assert pp_nippon.overlap_percentage > 0.0


@pytest.mark.asyncio
async def test_full_quant_diagnostics_with_xirr():
    engine = QuantEngine()
    portfolio = load_demo_portfolio()
    diagnostics = await engine.run_diagnostics(portfolio, "Moderate")

    assert len(diagnostics.rolling_cagrs) == len(portfolio.holdings)
    assert len(diagnostics.form_ratings) == len(portfolio.holdings)
    assert diagnostics.portfolio_xirr is not None
    assert diagnostics.portfolio_xirr > 5.0


def test_forward_filled_nav_series_rolling_cagr():
    engine = QuantEngine()
    # Create a 400-day daily series with missing weekend dates
    from datetime import datetime, timedelta
    now = datetime.now()
    nav_series = []
    current_nav = 100.0
    for i in range(400):
        d = now - timedelta(days=(400 - 1 - i))
        # Skip weekends to simulate raw market feed gaps
        if d.weekday() < 5:
            current_nav *= 1.0005  # daily growth
            nav_series.append({
                "date": d.strftime("%d-%m-%Y"),
                "nav": round(current_nav, 4)
            })

    cagr_1y, cagr_3y = engine.calculate_rolling_cagr_from_series(nav_series)
    assert cagr_1y is not None
    assert cagr_1y > 0.0
    # Series is only 400 days, so 3Y should be None (insufficient history)
    assert cagr_3y is None


def test_edge_cases_short_history_and_zero_balances():
    engine = QuantEngine()
    
    # 1. Zero balance holding
    zero_holding = Holding(
        folio_number="000", scheme_name="Zero Balance Fund",
        isin="INF0", amfi_code="000", plan_type="DIRECT", category="Debt",
        units=0.0, nav=10.0, current_value=0.0, cost_value=0.0,
        unrealized_gain=0.0, return_percentage=0.0, portfolio_weight_pct=0.0
    )
    xirr_zero = engine.calculate_holding_xirr(zero_holding)
    assert xirr_zero is None

    # 2. Negative return holding
    neg_holding = Holding(
        folio_number="111", scheme_name="Negative Return Fund",
        isin="INF1", amfi_code="111", plan_type="DIRECT", category="Equity",
        units=100.0, nav=8.0, current_value=800.0, cost_value=1000.0,
        unrealized_gain=-200.0, return_percentage=-20.0, portfolio_weight_pct=100.0
    )
    xirr_neg = engine.calculate_holding_xirr(neg_holding)
    assert xirr_neg == -20.0

    # 3. Insufficient history form tier classification
    tier, rationale = engine.classify_form_tier(
        "New NFO Fund", "Large Cap", "DIRECT", cagr_1y=None, cagr_3y=None, alpha_1y=None, alpha_3y=None
    )
    assert tier == "On-Track"
    assert "insufficient" in rationale.lower()


def test_pairwise_overlap_vectorized_set_math():
    engine = QuantEngine()
    h1 = Holding(
        folio_number="1", scheme_name="Fund A", isin="A", amfi_code="122639", plan_type="DIRECT",
        category="Flexi Cap", units=10.0, nav=100.0, current_value=1000.0, cost_value=900.0,
        unrealized_gain=100.0, return_percentage=11.1, portfolio_weight_pct=50.0
    )
    h2 = Holding(
        folio_number="2", scheme_name="Fund B", isin="B", amfi_code="100377", plan_type="DIRECT",
        category="Mid Cap", units=10.0, nav=100.0, current_value=1000.0, cost_value=900.0,
        unrealized_gain=100.0, return_percentage=11.1, portfolio_weight_pct=50.0
    )
    overlap = engine.calculate_overlap_matrix([h1, h2])
    assert len(overlap.pairs) == 1
    assert overlap.pairs[0].overlap_percentage >= 0.0
