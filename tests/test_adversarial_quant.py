"""
Adversarial Stress Testing & Empirical Verification Suite
Challenger 1 — Quantitative & Mathematical Verification
"""
import math
import pytest
from datetime import date, timedelta
import pandas as pd
import numpy as np

from mf_analyzer.quant_engine import calculate_xirr, QuantEngine
from mf_analyzer.schemas import Holding, Transaction, Portfolio
from mf_analyzer.chatbot_engine import chatbot_advisor_engine
from app import detect_anomalies, preprocess, get_summary, get_health_score


# ============================================================================
# 1. SOLVER & XIRR ADVERSARIAL STRESS TESTS
# ============================================================================

def test_xirr_empty_and_insufficient_cashflows():
    """Verify solver handles empty, single, and sub-threshold flows."""
    assert calculate_xirr([]) is None
    assert calculate_xirr([(date(2024, 1, 1), -1000.0)]) is None
    # All zero / micro cashflows below 0.001
    assert calculate_xirr([(date(2024, 1, 1), 0.0001), (date(2024, 1, 2), -0.0001)]) is None


def test_xirr_single_sign_cashflows():
    """Verify solver rejects all-negative or all-positive flows (no IRR exists)."""
    # All outflows
    assert calculate_xirr([
        (date(2024, 1, 1), -1000.0),
        (date(2024, 2, 1), -1000.0),
        (date(2024, 3, 1), -1000.0),
    ]) is None

    # All inflows
    assert calculate_xirr([
        (date(2024, 1, 1), 1000.0),
        (date(2024, 2, 1), 1000.0),
    ]) is None


def test_xirr_unsorted_and_duplicate_dates():
    """Verify solver handles unsorted dates and multiple flows on same day."""
    cfs = [
        (date(2024, 6, 1), 1100.0),
        (date(2024, 1, 1), -500.0),
        (date(2024, 1, 1), -500.0), # Same day purchase
    ]
    res = calculate_xirr(cfs)
    assert res is not None
    assert isinstance(res, float)
    assert not math.isnan(res)


def test_xirr_pathological_alternating_flows():
    """Verify solver resilience with multiple sign changes (Descartes' Rule of Signs)."""
    cfs = [
        (date(2023, 1, 1), -10000.0),
        (date(2023, 4, 1), 5000.0),
        (date(2023, 7, 1), -7000.0),
        (date(2023, 10, 1), 8000.0),
        (date(2024, 1, 1), -4000.0),
        (date(2024, 4, 1), 12000.0),
    ]
    res = calculate_xirr(cfs)
    assert res is not None
    assert -100.0 < res < 1000.0


def test_xirr_total_capital_loss_boundary():
    """Verify near-100% loss cash flows."""
    cfs = [
        (date(2023, 1, 1), -100000.0),
        (date(2024, 1, 1), 0.01), # Lost almost everything
    ]
    res = calculate_xirr(cfs)
    assert res is not None
    assert res < -99.0


def test_xirr_short_vintage_guard_triggers():
    """
    Verify short-vintage holding (<180 days) with high annualized rate (>35%)
    and modest absolute return (<25%) correctly triggers SEBI linearization guard.
    """
    # 15-day holding with 3.5% absolute gain
    # Unlinearized pyxirr gives (1.035)^(365/15) - 1 ≈ 1.328 (132.8%)
    d0 = date(2024, 1, 1)
    d1 = date(2024, 1, 16) # 15 days
    cfs = [(d0, -10000.0), (d1, 10350.0)] # 3.5% return in 15 days

    res = calculate_xirr(cfs)
    assert res is not None
    # SEBI linearized: (0.035 * (365 / max(75, 15))) * 100 = 0.035 * (365 / 75) * 100 = 17.03%
    # Notice it should NOT be 132.8%
    assert res < 35.0
    assert 10.0 <= res <= 25.0


def test_xirr_short_vintage_boundary_conditions():
    """Test boundary conditions for holding days (179 vs 181 days)."""
    d0 = date(2024, 1, 1)
    
    # 179 days, 20% gain -> rate_pct would be high
    d_179 = d0 + timedelta(days=179)
    cfs_179 = [(d0, -10000.0), (d_179, 12000.0)]
    res_179 = calculate_xirr(cfs_179)
    assert res_179 is not None
    
    # 181 days, 20% gain -> outside short-vintage guard (<180d)
    d_181 = d0 + timedelta(days=181)
    cfs_181 = [(d0, -10000.0), (d_181, 12000.0)]
    res_181 = calculate_xirr(cfs_181)
    assert res_181 is not None
    # Pyxirr standard rate: (1.20)^(365/181) - 1 ≈ 44.47%
    assert 40.0 <= res_181 <= 50.0


# ============================================================================
# 2. BUDGET 2024 TAX ENGINE ADVERSARIAL STRESS TESTS
# ============================================================================

def test_budget_2024_equity_ltcg_exemption_boundary():
    """
    Test Section 112A equity LTCG:
    - Exemption = ₹1,25,000
    - Rate = 12.5% + 4% cess = 13.0% effective
    """
    bot = chatbot_advisor_engine

    # Case A: Gain exactly at exemption limit (₹1,25,000)
    p1 = bot.generate_chat_response_payload("If I redeem equity fund held for 15 months with a gain of ₹1,25,000, what is the tax?")
    assert "₹0.00" in p1["reply"] or "0.00" in p1["reply"] or "Nil" in p1["reply"]

    # Case B: Gain below exemption limit (₹80,000)
    p2 = bot.generate_chat_response_payload("If I redeem equity fund held for 18 months with a gain of ₹80,000, what is the tax?")
    assert "₹0.00" in p2["reply"] or "0.00" in p2["reply"] or "Nil" in p2["reply"]

    # Case C: Gain above exemption limit (₹1,80,000)
    # Taxable gain = 180,000 - 125,000 = 55,000
    # Base tax = 55,000 * 12.5% = 6,875
    # Total with 4% cess = 6,875 * 1.04 = ₹7,150.00
    p3 = bot.generate_chat_response_payload("If I redeem equity fund held for 14 months with a gain of ₹1,80,000, what is the exact tax?")
    assert "7,150.00" in p3["reply"]
    assert "125,000" in p3["reply"] or "1,25,000" in p3["reply"] or "1.25 Lakh" in p3["reply"]
    assert "12.5%" in p3["reply"]

    # Case D: Gain of ₹2,50,000
    # Taxable gain = 250,000 - 125,000 = 125,000
    # Base tax = 125,000 * 12.5% = 15,625
    # Total with 4% cess = 15,625 * 1.04 = ₹16,250.00
    p4 = bot.generate_chat_response_payload("If I redeem equity fund held for 24 months with a gain of ₹2,50,000, what is my tax?")
    assert "16,250.00" in p4["reply"]


def test_budget_2024_equity_stcg_calculation():
    """
    Test Section 111A equity STCG (<12 months):
    - Rate = 20% + 4% cess = 20.8% effective
    - Zero exemption
    """
    bot = chatbot_advisor_engine
    p = bot.generate_chat_response_payload("If I redeem equity fund held for 6 months with a gain of ₹1,00,000, what is the tax?")
    # Taxable gain = 100,000
    # Base tax = 100,000 * 20% = 20,000
    # Total with cess = 20,000 * 1.04 = 20,800.00
    assert "20,800.00" in p["reply"] or "20.0%" in p["reply"] or "20%" in p["reply"]


def test_section_50aa_debt_taxation():
    """
    Test Section 50AA for Specified Debt Funds purchased post April 1, 2023:
    - Taxed at individual slab rate
    - No indexation benefit
    - Deemed STCG regardless of holding period
    """
    bot = chatbot_advisor_engine
    p = bot.generate_chat_response_payload("What is the tax on SBI Ultra Short Duration fund bought in May 2024?")
    reply = p["reply"].lower()
    assert "50aa" in reply
    assert "slab rate" in reply or "income tax slab" in reply
    assert "no indexation" in reply or "without indexation" in reply or "abolished" in reply


# ============================================================================
# 3. DISTRIBUTOR DRAG SIMULATION TESTS
# ============================================================================

def test_cost_drag_zero_regular_corpus():
    """Verify $0 regular plan corpus yields exact 0.0 drag."""
    qe = QuantEngine()
    holdings = [
        Holding(scheme_name="Fund Direct", folio_number="12345", amfi_code="123", plan_type="DIRECT", current_value=100000.0, cost_value=90000.0),
    ]
    res = qe.calculate_cost_drag(holdings, annual_commission_bps=0.85)
    assert res.total_regular_corpus == 0.0
    assert res.annual_expense_drag_amount == 0.0
    assert res.projected_10yr_cost_drag == 0.0
    assert res.affected_schemes_count == 0


def test_cost_drag_hypothetical_5l_simulation():
    """
    Verify ₹5 Lakh corpus drag simulation at 0.85% commission:
    Direct (12.0%): 500,000 * (1.12)^10 = 1,552,924.11
    Regular (11.15%): 500,000 * (1.1115)^10 = 1,439,013.33
    10-Yr Wealth Drag: 1,552,924.11 - 1,439,013.33 = 113,910.78
    Annual Drag: 500,000 * 0.0085 = 4,250.00
    """
    bot = chatbot_advisor_engine
    p = bot.generate_chat_response_payload("If ₹5,00,000 of my corpus was in regular plans with 0.85% commission, calculate 10-year wealth drag.")
    reply = p["reply"]
    assert "1,552,924" in reply or "15.53" in reply or "15,52,924" in reply
    assert "1,439,012" in reply or "1,439,013" in reply or "14.39" in reply or "14,39,013" in reply
    assert "113,911" in reply or "113,910" in reply or "1.14" in reply
    assert "4,250" in reply


# ============================================================================
# 4. GAUSSIAN Z-SCORE ANOMALY DETECTION ADVERSARIAL STRESS TESTS
# ============================================================================

def test_anomaly_detection_zero_variance():
    """
    Test zero variance case: All transactions in category have exact identical amount.
    Standard deviation = 0.
    Should not throw ZeroDivisionError and should return 0 anomalies (Z <= 2.0).
    """
    data = [
        {"date": "2024-01-01", "description": "Monthly Flat Rent", "amount": 25000.0, "category": "Housing", "type": "expense"},
        {"date": "2024-02-01", "description": "Monthly Flat Rent", "amount": 25000.0, "category": "Housing", "type": "expense"},
        {"date": "2024-03-01", "description": "Monthly Flat Rent", "amount": 25000.0, "category": "Housing", "type": "expense"},
        {"date": "2024-04-01", "description": "Monthly Flat Rent", "amount": 25000.0, "category": "Housing", "type": "expense"},
    ]
    df = pd.DataFrame(data)
    df = preprocess(df)
    res = detect_anomalies(df)
    assert "anomalies" in res
    assert len(res["anomalies"]) == 0


def test_anomaly_detection_single_transaction_in_category():
    """
    Test single transaction in a category (std = NaN).
    Should handle gracefully and not crash.
    """
    data = [
        {"date": "2024-01-01", "description": "Lone Expense", "amount": 500.0, "category": "Books", "type": "expense"},
    ]
    df = pd.DataFrame(data)
    df = preprocess(df)
    res = detect_anomalies(df)
    assert "anomalies" in res
    assert len(res["anomalies"]) == 0


def test_anomaly_detection_extreme_spike():
    """
    Test clear outlier detection: routine ₹500 grocery txns vs one ₹50,000 spike.
    Z-score should be > 2.0 and correctly ranked.
    """
    data = [
        {"date": f"2024-01-{i:02d}", "description": "Supermarket", "amount": 500.0 + (i % 3)*10, "category": "Food & Dining", "type": "expense"}
        for i in range(1, 25)
    ]
    data.append({"date": "2024-01-26", "description": "Mega Banquet Dinner", "amount": 25000.0, "category": "Food & Dining", "type": "expense"})

    df = pd.DataFrame(data)
    df = preprocess(df)
    res = detect_anomalies(df)
    assert len(res["anomalies"]) >= 1
    top = res["anomalies"][0]
    assert top["description"] == "Mega Banquet Dinner"
    assert top["z_score"] > 2.0


# ============================================================================
# 5. MULTI-ASSET ALLOCATION & PAIRWISE OVERLAP TESTS
# ============================================================================

def test_pairwise_overlap_disjoint_holdings():
    """Verify disjoint holdings produce exactly 0.0% overlap and partial overlap sums min(wA, wB)."""
    qe = QuantEngine()
    # 1. Completely disjoint: Edelweiss US Tech (148332) vs HDFC Silver FoF (150064)
    h_tech = Holding(scheme_name="Edelweiss US Technology Equity FoF - Direct", folio_number="111", amfi_code="148332", current_value=4000.0, cost_value=3500.0)
    h_silver = Holding(scheme_name="HDFC Silver ETF FoF - Direct", folio_number="222", amfi_code="150064", current_value=2500.0, cost_value=2200.0)
    
    m_disjoint = qe.calculate_overlap_matrix([h_tech, h_silver])
    assert len(m_disjoint.pairs) == 1
    assert m_disjoint.pairs[0].overlap_percentage == 0.00
    assert len(m_disjoint.pairs[0].common_holdings) == 0

    # 2. Partial overlap: PPFC (122639) vs Bandhan Small Cap (147944)
    # Common: ICICI Bank (0.85%), HDFC Bank (0.65%) -> Sum = 1.50%
    h_ppfc = Holding(scheme_name="Parag Parikh Flexi Cap Fund - Direct", folio_number="333", amfi_code="122639", current_value=5000.0, cost_value=4000.0)
    h_bandhan = Holding(scheme_name="Bandhan Small Cap Fund - Direct", folio_number="444", amfi_code="147944", current_value=3000.0, cost_value=2500.0)
    
    m_overlap = qe.calculate_overlap_matrix([h_ppfc, h_bandhan])
    assert len(m_overlap.pairs) == 1
    assert m_overlap.pairs[0].overlap_percentage == 1.50
    assert "ICICI Bank Ltd" in m_overlap.pairs[0].common_holdings
    assert "HDFC Bank Ltd" in m_overlap.pairs[0].common_holdings


def test_multi_asset_decomposition():
    """Verify multi-asset fund 50% Eq / 25% Debt / 25% Comm decomposition."""
    qe = QuantEngine()
    holdings = [
        Holding(scheme_name="Quant Multi Asset Fund - Direct Plan - Growth", folio_number="11111", amfi_code="120847", current_value=10000.0, cost_value=9000.0),
    ]
    alloc = qe.calculate_asset_allocation(holdings)
    assert alloc.equity_pct == 50.0
    assert alloc.debt_pct == 25.0
    assert alloc.commodities_pct == 25.0
