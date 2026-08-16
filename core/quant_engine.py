from datetime import date
from typing import List, Tuple
import pyxirr
import httpx
import pandas as pd
import numpy as np

async def fetch_historical_nav(amfi_code: str) -> pd.Series:
    """
    Fetches NAV history from public API (api.mfapi.in).
    Returns a pandas Series with DatetimeIndex and float NAV values.
    """
    url = f"https://api.mfapi.in/mf/{amfi_code}"
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(url, timeout=10.0)
            resp.raise_for_status()
            data = resp.json().get("data", [])
        except Exception as e:
            print(f"Error fetching NAV for {amfi_code}: {e}")
            return pd.Series(dtype=float)
            
    if not data:
        return pd.Series(dtype=float)

    # Convert to pandas Series
    df = pd.DataFrame(data)
    df["date"] = pd.to_datetime(df["date"], format="%d-%m-%Y")
    df["nav"] = pd.to_numeric(df["nav"])
    df = df.set_index("date").sort_index()
    return df["nav"]

def calculate_xirr(cash_flows: List[Tuple[date, float]]) -> float:
    """
    Fast XIRR calculation using pyxirr (Rust backend).
    Expects a list of (date, amount) tuples.
    """
    try:
        res = pyxirr.xirr(cash_flows)
        return res if res is not None else 0.0
    except Exception as e:
        print(f"XIRR calculation failed: {e}")
        return 0.0

def compute_rolling_metrics(nav_series: pd.Series) -> dict:
    """
    Computes CAGR, Sharpe, Sortino, and Max Drawdown using high-performance numpy/pandas.
    """
    if nav_series.empty or len(nav_series) < 30:
        return {}

    start_val = float(nav_series.iloc[0])
    end_val = float(nav_series.iloc[-1])
    days = (nav_series.index[-1] - nav_series.index[0]).days
    
    if days > 0 and start_val > 0:
        cagr = (end_val / start_val) ** (365.25 / days) - 1.0
    else:
        cagr = 0.0

    returns = nav_series.pct_change().dropna()
    mean_ret = float(returns.mean())
    std_ret = float(returns.std())
    
    sharpe = float((mean_ret / std_ret) * np.sqrt(252)) if std_ret > 0 else 0.0
    
    neg_returns = returns[returns < 0]
    downside_std = float(neg_returns.std()) if len(neg_returns) > 0 else 0.0
    sortino = float((mean_ret / downside_std) * np.sqrt(252)) if downside_std > 0 else 0.0

    cum_max = nav_series.cummax()
    drawdown = (nav_series - cum_max) / cum_max
    max_drawdown = float(drawdown.min())

    return {
        "cagr": round(cagr * 100.0, 2),
        "sharpe": round(sharpe, 2),
        "sortino": round(sortino, 2),
        "max_drawdown": round(max_drawdown * 100.0, 2)
    }
