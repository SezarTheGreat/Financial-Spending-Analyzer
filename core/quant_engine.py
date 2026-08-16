from datetime import date
from typing import List, Tuple
import pyxirr
import httpx
import pandas as pd
import quantstats as qs

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
    Computes CAGR, Sharpe, Sortino, and Max Drawdown using quantstats.
    """
    if nav_series.empty or len(nav_series) < 30:
        return {}

    # Calculate daily returns
    returns = nav_series.pct_change().dropna()
    
    # Calculate metrics
    metrics = {
        "cagr": qs.stats.cagr(returns),
        "sharpe": qs.stats.sharpe(returns),
        "sortino": qs.stats.sortino(returns),
        "max_drawdown": qs.stats.max_drawdown(returns)
    }
    return metrics
