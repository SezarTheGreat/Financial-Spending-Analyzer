"""
Unit tests for Market Data & Concurrent Enrichment Service
"""
import pytest
from mf_analyzer.market_data import MarketDataService, CATEGORY_BENCHMARKS


@pytest.mark.asyncio
async def test_fetch_historical_nav():
    service = MarketDataService()
    # Test with AMFI code 122639 (Parag Parikh Flexi Cap)
    nav_series = await service.fetch_historical_nav("122639")
    assert isinstance(nav_series, list)
    assert len(nav_series) > 0
    assert "date" in nav_series[0]
    assert "nav" in nav_series[0]
    assert nav_series[0]["nav"] > 0


@pytest.mark.asyncio
async def test_caching_behavior():
    service = MarketDataService()
    # First call
    data1 = await service.fetch_historical_nav("120828")
    # Second call (from cache)
    data2 = await service.fetch_historical_nav("120828")
    assert data1 == data2
    assert "120828" in service._nav_history_cache


def test_category_classification():
    service = MarketDataService()
    assert service.classify_category("Parag Parikh Flexi Cap Fund") == "Flexi Cap"
    assert service.classify_category("HDFC Top 100 Large Cap Fund") == "Large Cap"
    assert service.classify_category("Nippon India Small Cap Fund") == "Small Cap"
    assert service.classify_category("SBI Liquid Fund") == "Liquid"
    assert service.classify_category("ICICI Corporate Bond Debt Fund") == "Debt"


def test_top_holdings_resolution():
    service = MarketDataService()
    holdings = service.get_scheme_top_holdings("Parag Parikh Flexi Cap Fund", "122639")
    assert isinstance(holdings, list)
    assert any("HDFC Bank" in h for h in holdings) or any("Alphabet" in h for h in holdings)
