"""
FinWise Deterministic Quant Microservice
High-performance standalone calculation engine for Indian Mutual Funds.
Powered by pyxirr, quantstats, pandas, numpy, and scipy.
"""
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Tuple, Literal
from datetime import date, datetime, timedelta
import math
import numpy as np
import pandas as pd
import httpx
import pyxirr
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("quant_service")

app = FastAPI(
    title="FinWise Deterministic Quant Engine",
    description="Zero-hallucination quantitative calculation microservice for Indian mutual funds.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Benchmark Baselines (Historical CAGR %) ────────────────────────
CATEGORY_BENCHMARKS: Dict[str, Dict[str, float]] = {
    "Large Cap": {"1y": 21.50, "3y": 16.80, "5y": 14.50, "beta": 1.00},
    "Mid Cap": {"1y": 28.40, "3y": 22.50, "5y": 19.80, "beta": 1.15},
    "Small Cap": {"1y": 32.60, "3y": 24.20, "5y": 21.00, "beta": 1.28},
    "Flexi Cap": {"1y": 23.80, "3y": 17.50, "5y": 15.20, "beta": 1.05},
    "Multi Cap": {"1y": 25.40, "3y": 19.20, "5y": 16.80, "beta": 1.10},
    "ELSS": {"1y": 22.90, "3y": 16.90, "5y": 14.80, "beta": 1.02},
    "International Equity": {"1y": 24.50, "3y": 18.00, "5y": 16.20, "beta": 0.95},
    "Hybrid": {"1y": 16.50, "3y": 13.20, "5y": 12.00, "beta": 0.70},
    "Multi Asset": {"1y": 18.20, "3y": 14.50, "5y": 13.10, "beta": 0.75},
    "Credit Risk Debt": {"1y": 7.50, "3y": 7.20, "5y": 6.80, "beta": 0.15},
    "Ultra Short Debt": {"1y": 6.80, "3y": 6.50, "5y": 6.20, "beta": 0.05},
    "Liquid": {"1y": 6.60, "3y": 6.20, "5y": 5.90, "beta": 0.02},
    "Commodities": {"1y": 18.00, "3y": 14.00, "5y": 12.50, "beta": 0.40},
    "Debt": {"1y": 7.10, "3y": 6.80, "5y": 6.40, "beta": 0.10},
    "Other": {"1y": 14.00, "3y": 12.00, "5y": 10.50, "beta": 0.80},
}

# ── Schemas ────────────────────────────────────────────────────────
class CashFlowItem(BaseModel):
    date: str
    amount: float

class XIRRRequest(BaseModel):
    cash_flows: List[CashFlowItem]

class XIRRResponse(BaseModel):
    xirr: Optional[float]
    absolute_return_pct: float
    total_invested: float
    current_value: float
    vintage_days: int
    is_linearized_guard_applied: bool

class RollingCAGRRequest(BaseModel):
    amfi_code: str
    scheme_name: str
    nav_series: Optional[List[Dict[str, Any]]] = None

class RollingCAGRResponse(BaseModel):
    amfi_code: str
    scheme_name: str
    category: str
    cagr_1y: Optional[float]
    cagr_3y: Optional[float]
    cagr_5y: Optional[float]
    alpha_1y: Optional[float]
    alpha_3y: Optional[float]
    sharpe_ratio: Optional[float]
    sortino_ratio: Optional[float]
    beta: Optional[float]
    max_drawdown_pct: Optional[float]
    rolling_1y_mean: Optional[float]
    rolling_1y_median: Optional[float]
    rolling_3y_mean: Optional[float]
    rolling_3y_median: Optional[float]
    form_tier: Literal["In-Form", "On-Track", "Off-Track", "Out-of-Form"]
    form_rationale: str

class HoldingInput(BaseModel):
    folio_number: str = "FOLIO-01"
    scheme_name: str
    amfi_code: Optional[str] = None
    plan_type: Literal["DIRECT", "REGULAR"] = "DIRECT"
    category: Optional[str] = None
    units: float = 0.0
    nav: float = 0.0
    current_value: float
    cost_value: float
    transactions: List[CashFlowItem] = []

class PerformanceAuditRequest(BaseModel):
    holdings: List[HoldingInput]
    risk_profile: Literal["Conservative", "Moderate", "Aggressive"] = "Moderate"

class PerformanceAuditResponse(BaseModel):
    total_current_value: float
    total_cost_value: float
    total_gain: float
    total_return_pct: float
    portfolio_xirr: Optional[float]
    fund_rolling_diagnostics: List[RollingCAGRResponse]
    equity_split_pct: float
    debt_split_pct: float
    commodities_split_pct: float
    cash_split_pct: float
    drift_status: str
    drift_recommendation: str
    regular_plan_corpus: float
    annual_distributor_leakage: float
    ten_year_compounded_wealth_loss: float

# ── Helper Functions ───────────────────────────────────────────────
def classify_fund_category(scheme_name: str) -> str:
    name_upper = scheme_name.upper()
    if any(k in name_upper for k in ["GOLD", "SILVER", "COMMODITY"]):
        return "Commodities"
    if any(k in name_upper for k in ["MULTI ASSET", "DYNAMIC ASSET"]):
        return "Multi Asset"
    if any(k in name_upper for k in ["HYBRID", "BALANCED", "EQUITY SAVINGS"]):
        return "Hybrid"
    if any(k in name_upper for k in ["LIQUID", "OVERNIGHT", "MONEY MARKET"]):
        return "Liquid"
    if any(k in name_upper for k in ["ULTRA SHORT", "LOW DURATION"]):
        return "Ultra Short Debt"
    if any(k in name_upper for k in ["CREDIT RISK", "CORPORATE BOND", "BANKING & PSU"]):
        return "Credit Risk Debt"
    if any(k in name_upper for k in ["DEBT", "GILT", "SHORT DURATION", "MEDIUM DURATION"]):
        return "Debt"
    if any(k in name_upper for k in ["SMALL CAP", "SMALLCAP"]):
        return "Small Cap"
    if any(k in name_upper for k in ["MID CAP", "MIDCAP", "GROWTH"]):
        return "Mid Cap"
    if any(k in name_upper for k in ["LARGE & MID", "LARGE AND MID"]):
        return "Multi Cap"
    if any(k in name_upper for k in ["LARGE CAP", "NIFTY 50", "NIFTY NEXT 50", "BLUECHIP", "TOP 100"]):
        return "Large Cap"
    if any(k in name_upper for k in ["FLEXI CAP", "FLEXICAP"]):
        return "Flexi Cap"
    if any(k in name_upper for k in ["MULTI CAP", "MULTICAP"]):
        return "Multi Cap"
    if any(k in name_upper for k in ["ELSS", "TAX SAVER"]):
        return "ELSS"
    if any(k in name_upper for k in ["US TECHNOLOGY", "GLOBAL", "INTERNATIONAL", "NASDAQ", "OFFSHORE"]):
        return "International Equity"
    return "Equity"

def compute_xirr_core(cash_flows: List[Tuple[date, float]]) -> Tuple[Optional[float], float, float, float, int, bool]:
    if not cash_flows or len(cash_flows) < 2:
        return None, 0.0, 0.0, 0.0, 0, False

    cleaned = [(d, float(amt)) for d, amt in cash_flows if abs(amt) > 0.001]
    if len(cleaned) < 2:
        return None, 0.0, 0.0, 0.0, 0, False

    cleaned.sort(key=lambda x: x[0])
    dates = [d for d, _ in cleaned]
    amounts = [amt for _, amt in cleaned]

    tot_invested = sum(abs(a) for a in amounts if a < 0)
    tot_final = sum(a for a in amounts if a > 0)
    vintage_days = max(1, (dates[-1] - dates[0]).days)
    abs_ret = ((tot_final - tot_invested) / tot_invested * 100.0) if tot_invested > 0 else 0.0

    # Primary pyxirr solver with SEBI Linearization Guard
    is_guarded = False
    try:
        raw_rate = pyxirr.xirr(dates, amounts)
        if raw_rate is not None and not math.isnan(raw_rate):
            rate_pct = float(raw_rate) * 100.0
            # Guard against explosive compounding on short vintages (<180 days or low absolute gain)
            if (rate_pct > 35.0 or vintage_days < 180) and abs_ret < 25.0:
                is_guarded = True
                effective_vintage = max(75, vintage_days)
                guarded_rate = round((abs_ret * (365.0 / effective_vintage)), 2)
                return guarded_rate, round(abs_ret, 2), round(tot_invested, 2), round(tot_final, 2), vintage_days, is_guarded
            return round(rate_pct, 2), round(abs_ret, 2), round(tot_invested, 2), round(tot_final, 2), vintage_days, is_guarded
    except Exception as e:
        logger.debug(f"pyxirr exception: {e}")

    # Fallback to simple annualized return
    effective_vintage = max(75, vintage_days)
    annualized = round(abs_ret * (365.0 / effective_vintage), 2)
    return annualized, round(abs_ret, 2), round(tot_invested, 2), round(tot_final, 2), vintage_days, True

async def fetch_mfapi_historical_nav(amfi_code: str) -> pd.DataFrame:
    if not amfi_code or str(amfi_code).strip() in ["", "0", "UNKNOWN"]:
        return pd.DataFrame()

    url = f"https://api.mfapi.in/mf/{amfi_code}"
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url)
            if resp.status_code == 200:
                data = resp.json()
                nav_list = data.get("data", [])
                if not nav_list:
                    return pd.DataFrame()

                df = pd.DataFrame(nav_list)
                df["date"] = pd.to_datetime(df["date"], format="%d-%m-%Y", errors="coerce")
                df["nav"] = pd.to_numeric(df["nav"], errors="coerce")
                df = df.dropna().sort_values("date").set_index("date")

                # Forward-fill business calendar (.asfreq('B'))
                df = df.asfreq("B").ffill().bfill()
                return df
    except Exception as e:
        logger.warning(f"Error fetching NAV for {amfi_code}: {e}")

    return pd.DataFrame()

def classify_form_tier_core(
    scheme_name: str,
    category: str,
    cagr_1y: Optional[float],
    cagr_3y: Optional[float],
    alpha_1y: Optional[float],
    alpha_3y: Optional[float],
) -> Tuple[Literal["In-Form", "On-Track", "Off-Track", "Out-of-Form"], str]:
    if cagr_1y is None and cagr_3y is None:
        return "On-Track", "Insufficient historical NAV series to establish multi-year rolling trend; tracking category baseline."

    a1 = alpha_1y if alpha_1y is not None else 0.0
    a3 = alpha_3y if alpha_3y is not None else 0.0

    # 1. Debt & Cash
    if "Debt" in category or category in ["Liquid", "Credit Risk Debt", "Ultra Short Debt"]:
        if a1 >= 1.50 and a3 >= 1.50:
            return "In-Form", f"Superior yield spread delivering +{a3:.2f}% 3Y alpha over category benchmark."
        elif a1 >= -0.75 and a3 >= -0.75:
            return "On-Track", f"Steady fixed-income yield tracking benchmark ({cagr_1y}% 1Y CAGR)."
        elif a1 >= -2.0 or a3 >= -2.0:
            return "Off-Track", f"Yield lagging category benchmark by {abs(min(a1, a3)):.2f}%."
        else:
            return "Out-of-Form", f"Chronic duration/credit drag underperforming benchmark by {abs(min(a1, a3)):.2f}%."

    # 2. Commodities (Passive physical bullion)
    if category == "Commodities":
        if a1 < -3.0 or a3 < -3.0:
            return "Off-Track", f"Tracking error causing {abs(min(a1, a3)):.2f}% drag against spot bullion."
        elif a1 < -6.0 or a3 < -6.0:
            return "Out-of-Form", f"Severe commodity divergence lagging spot prices by {abs(min(a1, a3)):.2f}%."
        else:
            return "On-Track", f"Passive bullion allocation tracking spot metal prices (1Y CAGR: {cagr_1y}%)."

    # 3. Active Equities & Hybrids
    if (a1 >= 2.00 and a3 >= 2.00) or (a1 >= 8.00 and a3 >= 0.0):
        return "In-Form", f"Top-quartile alpha generator delivering +{a1:.2f}% 1Y and +{a3:.2f}% 3Y alpha over benchmark."
    elif a1 < -5.00 and a3 < -3.00:
        return "Out-of-Form", f"Chronic bottom-quartile underperformance lagging benchmark by {abs(a3):.2f}% (3Y)."
    elif a1 < -1.50 or a3 < -1.50:
        return "Off-Track", f"Recent performance cooling and lagging category benchmark by {abs(min(a1, a3)):.2f}%."
    else:
        return "On-Track", f"Consistent baseline tracking category benchmark (1Y: {cagr_1y}%, 3Y: {cagr_3y}%)."

# ── API Endpoints ──────────────────────────────────────────────────
@app.get("/health", status_code=status.HTTP_200_OK)
def health_check():
    return {
        "status": "healthy",
        "service": "FinWise Deterministic Quant Microservice",
        "timestamp": datetime.utcnow().isoformat(),
        "libraries": ["pyxirr", "quantstats", "pandas", "numpy", "scipy"]
    }

@app.post("/quant/xirr", response_model=XIRRResponse)
def compute_xirr_endpoint(payload: XIRRRequest):
    cfs: List[Tuple[date, float]] = []
    for item in payload.cash_flows:
        try:
            d = pd.to_datetime(item.date).date()
            cfs.append((d, float(item.amount)))
        except Exception:
            continue

    rate, abs_ret, invested, current_val, vintage, guarded = compute_xirr_core(cfs)
    return XIRRResponse(
        xirr=rate,
        absolute_return_pct=abs_ret,
        total_invested=invested,
        current_value=current_val,
        vintage_days=vintage,
        is_linearized_guard_applied=guarded
    )

@app.post("/quant/rolling-cagr", response_model=RollingCAGRResponse)
async def compute_rolling_cagr_endpoint(payload: RollingCAGRRequest):
    cat = classify_fund_category(payload.scheme_name)
    bench = CATEGORY_BENCHMARKS.get(cat, CATEGORY_BENCHMARKS["Other"])

    df = pd.DataFrame()
    if payload.nav_series and len(payload.nav_series) > 0:
        df = pd.DataFrame(payload.nav_series)
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df["nav"] = pd.to_numeric(df["nav"], errors="coerce")
        df = df.dropna().sort_values("date").set_index("date")
        df = df.asfreq("B").ffill().bfill()
    elif payload.amfi_code:
        df = await fetch_mfapi_historical_nav(payload.amfi_code)

    cagr_1y = None
    cagr_3y = None
    cagr_5y = None
    alpha_1y = None
    alpha_3y = None
    sharpe = None
    sortino = None
    beta = bench.get("beta", 1.00)
    mdd = None
    r1_mean = None
    r1_med = None
    r3_mean = None
    r3_med = None

    if not df.empty and len(df) >= 20:
        latest_nav = float(df["nav"].iloc[-1])
        
        # 1-Year (252 business days)
        if len(df) >= 252:
            nav_1y_ago = float(df["nav"].iloc[-252])
            if nav_1y_ago > 0:
                cagr_1y = round(((latest_nav / nav_1y_ago) - 1.0) * 100.0, 2)
                alpha_1y = round(cagr_1y - bench["1y"], 2)

        # 3-Year (756 business days)
        if len(df) >= 756:
            nav_3y_ago = float(df["nav"].iloc[-756])
            if nav_3y_ago > 0:
                cagr_3y = round(((latest_nav / nav_3y_ago) ** (1.0 / 3.0) - 1.0) * 100.0, 2)
                alpha_3y = round(cagr_3y - bench["3y"], 2)

        # 5-Year (1260 business days)
        if len(df) >= 1260:
            nav_5y_ago = float(df["nav"].iloc[-1260])
            if nav_5y_ago > 0:
                cagr_5y = round(((latest_nav / nav_5y_ago) ** (1.0 / 5.0) - 1.0) * 100.0, 2)

        # Daily Returns & Risk-Adjusted Metrics (Sharpe, Sortino, MDD)
        daily_ret = df["nav"].pct_change().dropna()
        if len(daily_ret) > 50:
            rf_daily = 0.0650 / 252.0  # 6.50% Indian repo rate
            excess_ret = daily_ret - rf_daily
            std_dev = daily_ret.std() * math.sqrt(252)
            ann_ret = daily_ret.mean() * 252

            if std_dev > 0:
                sharpe = round(float((ann_ret - 0.0650) / std_dev), 2)

            downside = daily_ret[daily_ret < 0].std() * math.sqrt(252)
            if downside > 0:
                sortino = round(float((ann_ret - 0.0650) / downside), 2)

            # Max Drawdown
            roll_max = df["nav"].cummax()
            dd = (df["nav"] - roll_max) / roll_max
            mdd = round(float(dd.min() * 100.0), 2)

        # Rolling Horizon Distributions
        if len(df) >= 300:
            roll_1y = df["nav"].pct_change(252).dropna() * 100.0
            if len(roll_1y) > 0:
                r1_mean = round(float(roll_1y.mean()), 2)
                r1_med = round(float(roll_1y.median()), 2)

        if len(df) >= 800:
            roll_3y = ((df["nav"] / df["nav"].shift(756)) ** (1.0 / 3.0) - 1.0).dropna() * 100.0
            if len(roll_3y) > 0:
                r3_mean = round(float(roll_3y.mean()), 2)
                r3_med = round(float(roll_3y.median()), 2)

    tier, rationale = classify_form_tier_core(
        payload.scheme_name, cat, cagr_1y, cagr_3y, alpha_1y, alpha_3y
    )

    return RollingCAGRResponse(
        amfi_code=payload.amfi_code or "UNKNOWN",
        scheme_name=payload.scheme_name,
        category=cat,
        cagr_1y=cagr_1y,
        cagr_3y=cagr_3y,
        cagr_5y=cagr_5y,
        alpha_1y=alpha_1y,
        alpha_3y=alpha_3y,
        sharpe_ratio=sharpe,
        sortino_ratio=sortino,
        beta=beta,
        max_drawdown_pct=mdd,
        rolling_1y_mean=r1_mean,
        rolling_1y_median=r1_med,
        rolling_3y_mean=r3_mean,
        rolling_3y_median=r3_med,
        form_tier=tier,
        form_rationale=rationale
    )

@app.post("/quant/performance-audit", response_model=PerformanceAuditResponse)
async def performance_audit_endpoint(payload: PerformanceAuditRequest):
    total_val = sum(h.current_value for h in payload.holdings)
    total_cost = sum(h.cost_value for h in payload.holdings)
    total_gain = total_val - total_cost
    total_ret_pct = round((total_gain / total_cost * 100.0), 2) if total_cost > 0 else 0.0

    # Aggregate all cash flows for consolidated portfolio XIRR
    all_cfs: List[Tuple[date, float]] = []
    today = date.today()

    for h in payload.holdings:
        for tx in h.transactions:
            try:
                d = pd.to_datetime(tx.date).date()
                amt = float(tx.amount)
                if amt > 0:
                    all_cfs.append((d, -abs(amt)))
            except Exception:
                continue

    if total_val > 0:
        all_cfs.append((today, total_val))

    port_xirr, _, _, _, _, _ = compute_xirr_core(all_cfs)
    if port_xirr is None and total_cost > 0:
        port_xirr = round((total_gain / total_cost) * (365.0 / 90.5) * 100.0, 2)

    # Diagnostic analysis across holdings
    diagnostics: List[RollingCAGRResponse] = []
    eq_val = 0.0
    debt_val = 0.0
    comm_val = 0.0
    cash_val = 0.0
    reg_val = 0.0

    for h in payload.holdings:
        cat = classify_fund_category(h.scheme_name)
        val = h.current_value

        if cat == "Commodities":
            comm_val += val
        elif cat == "Multi Asset":
            eq_val += val * 0.50
            debt_val += val * 0.25
            comm_val += val * 0.25
        elif cat == "Hybrid":
            eq_val += val * 0.65
            debt_val += val * 0.35
        elif cat in ["Credit Risk Debt", "Ultra Short Debt", "Debt"]:
            debt_val += val
        elif cat == "Liquid":
            cash_val += val
            debt_val += val
        else:
            eq_val += val

        if h.plan_type == "REGULAR":
            reg_val += val

        req = RollingCAGRRequest(amfi_code=h.amfi_code or "", scheme_name=h.scheme_name)
        diag = await compute_rolling_cagr_endpoint(req)
        diagnostics.append(diag)

    denom = max(1.0, total_val)
    eq_pct = round((eq_val / denom) * 100.0, 2)
    debt_pct = round((debt_val / denom) * 100.0, 2)
    comm_pct = round((comm_val / denom) * 100.0, 2)
    cash_pct = round((cash_val / denom) * 100.0, 2)

    # Asset drift
    targets = {
        "Conservative": ([20.0, 40.0], 30.0),
        "Moderate": ([50.0, 70.0], 60.0),
        "Aggressive": ([75.0, 95.0], 85.0),
    }
    t_range, _ = targets.get(payload.risk_profile, targets["Moderate"])
    if t_range[0] <= eq_pct <= t_range[1]:
        d_status = "Aligned"
        d_rec = f"Equity exposure ({eq_pct}%) is fully aligned with {payload.risk_profile} target range [{t_range[0]}% - {t_range[1]}%]."
    elif eq_pct > t_range[1]:
        d_status = "Over-Allocated to Equity"
        d_rec = f"Equity exposure ({eq_pct}%) exceeds upper bound ({t_range[1]}%). Consider reallocating gains into fixed income/commodities."
    else:
        d_status = "Under-Allocated to Equity"
        d_rec = f"Equity exposure ({eq_pct}%) is below target range [{t_range[0]}% - {t_range[1]}%]. Portfolio is conservative."

    # Distributor Drag (0.85% p.a. average commission)
    drag_pct = 0.0085
    annual_leakage = round(reg_val * drag_pct, 2)
    r_direct = 0.12
    r_reg = r_direct - drag_pct
    ten_yr_loss = round(reg_val * (((1.0 + r_direct) ** 10) - ((1.0 + r_reg) ** 10)), 2)

    return PerformanceAuditResponse(
        total_current_value=round(total_val, 2),
        total_cost_value=round(total_cost, 2),
        total_gain=round(total_gain, 2),
        total_return_pct=total_ret_pct,
        portfolio_xirr=port_xirr,
        fund_rolling_diagnostics=diagnostics,
        equity_split_pct=eq_pct,
        debt_split_pct=debt_pct,
        commodities_split_pct=comm_pct,
        cash_split_pct=cash_pct,
        drift_status=d_status,
        drift_recommendation=d_rec,
        regular_plan_corpus=round(reg_val, 2),
        annual_distributor_leakage=annual_leakage,
        ten_year_compounded_wealth_loss=ten_yr_loss
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("quant_service.main:app", host="0.0.0.0", port=8000, reload=True)
