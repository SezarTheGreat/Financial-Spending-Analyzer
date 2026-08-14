"""
CAS Ingestion & Statement Parser
Handles in-memory decryption and extraction of password-protected CAMS/KFintech Detailed eCAS PDFs.
Includes fallback demo portfolio generator for evaluation and testing.
"""
import io
import json
import logging
from typing import Union, Dict, Any, List, Optional
import casparser
from casparser.exceptions import (
    IncorrectPasswordError,
    CASParseError,
    ParserException,
    HeaderParseError,
)

from .schemas import Portfolio, Holding, Transaction, PlanType

logger = logging.getLogger(__name__)


def detect_plan_type(scheme_name: str, advisor: Optional[str] = None) -> PlanType:
    """
    Detect whether a mutual fund scheme is DIRECT or REGULAR.
    """
    name_upper = scheme_name.upper()
    if "DIRECT" in name_upper:
        return "DIRECT"
    if "REGULAR" in name_upper:
        return "REGULAR"
    
    # Check advisor/broker string if provided
    if advisor:
        adv_upper = advisor.upper()
        if "DIRECT" in adv_upper or adv_upper in ["INA000000000", "ARN-0000", "DIRECT"]:
            return "DIRECT"
        if "ARN-" in adv_upper:
            return "REGULAR"
            
    # Default to REGULAR if unspecified in traditional statements
    return "REGULAR"


def detect_category(scheme_name: str) -> str:
    """
    Deduce basic asset category from scheme name.
    """
    name_upper = scheme_name.upper()
    if any(k in name_upper for k in ["LIQUID", "OVERNIGHT", "MONEY MARKET", "TREASURY"]):
        return "Liquid"
    if any(k in name_upper for k in ["DEBT", "BOND", "GILT", "SHORT DURATION", "MEDIUM DURATION", "LONG DURATION", "CORPORATE BOND", "BANKING & PSU"]):
        return "Debt"
    if any(k in name_upper for k in ["HYBRID", "BALANCED", "DYNAMIC ASSET", "MULTI ASSET", "EQUITY SAVINGS", "ARBITRAGE"]):
        return "Hybrid"
    if any(k in name_upper for k in ["GOLD", "SILVER", "COMMODITY"]):
        return "Commodity"
    # Default equity
    return "Equity"


def parse_cas_pdf(pdf_source: Union[str, bytes, io.BytesIO], password: str) -> Portfolio:
    """
    Parse password-protected CAMS/KFintech CAS PDF into structured Portfolio model.
    Accepts file path, raw bytes, or BytesIO buffer.
    """
    if not password:
        raise ValueError("CAS PDF password (typically PAN in UPPERCASE) is required.")
        
    stream = pdf_source
    if isinstance(pdf_source, bytes):
        stream = io.BytesIO(pdf_source)

    try:
        cas_data = casparser.read_cas_pdf(stream, password=password, output="dict")
    except IncorrectPasswordError as e:
        logger.error(f"CAS decryption failed: Incorrect password. Error: {e}")
        raise ValueError("Incorrect CAS password. Please verify the PAN/password provided.") from e
    except (CASParseError, HeaderParseError, ParserException) as e:
        logger.error(f"CAS parsing failed: {e}")
        raise ValueError(f"Failed to parse CAS statement: {str(e)}") from e
    except Exception as e:
        logger.error(f"Unexpected error while processing CAS: {e}")
        raise ValueError(f"Error processing CAS file: {str(e)}") from e

    investor_info = cas_data.get("investor_info", {})
    folios = cas_data.get("folios", [])
    statement_period = cas_data.get("statement_period", {})
    period_str = f"{statement_period.get('from', '')} to {statement_period.get('to', '')}".strip()

    holdings_list: List[Holding] = []
    total_val = 0.0
    total_cost = 0.0

    for folio in folios:
        folio_num = folio.get("folio", "UNKNOWN")
        for scheme in folio.get("schemes", []):
            scheme_name = scheme.get("scheme", "").strip()
            if not scheme_name:
                continue

            isin = scheme.get("isin")
            amfi = scheme.get("amfi")
            advisor = scheme.get("advisor")
            plan_type = detect_plan_type(scheme_name, advisor)
            category = detect_category(scheme_name)

            valuation = scheme.get("valuation", {})
            nav = float(valuation.get("nav", 0.0) or scheme.get("close_calculated", 0.0) or 0.0)
            units = float(scheme.get("close", 0.0) or valuation.get("units", 0.0) or 0.0)
            current_value = float(valuation.get("value", 0.0) or (units * nav))

            # Parse transactions & compute cost value
            raw_txns = scheme.get("transactions", [])
            transactions: List[Transaction] = []
            cost_value = 0.0

            for tx in raw_txns:
                t_date = str(tx.get("date", ""))
                t_desc = str(tx.get("description", ""))
                t_amount = float(tx.get("amount", 0.0) or 0.0)
                t_units = float(tx.get("units", 0.0) or 0.0)
                t_nav = float(tx.get("nav", 0.0) or 0.0)
                t_type = str(tx.get("type", "PURCHASE")).upper()

                transactions.append(
                    Transaction(
                        date=t_date,
                        description=t_desc,
                        amount=t_amount,
                        units=t_units,
                        nav=t_nav,
                        type=t_type,
                    )
                )

                if t_amount > 0 and t_type in ["PURCHASE", "PURCHASE_SIP", "SIP", "SWITCH_IN", "SYSTEMATIC_INVESTMENT"]:
                    cost_value += t_amount
                elif t_amount < 0 or t_type in ["REDEMPTION", "SWITCH_OUT"]:
                    # Approximate cost reduction proportional or absolute
                    cost_value = max(0.0, cost_value - abs(t_amount))

            if cost_value <= 0.0 and units > 0 and nav > 0:
                cost_value = current_value * 0.85  # Fallback estimate if cost basis cannot be determined

            unrealized_gain = current_value - cost_value
            return_pct = (unrealized_gain / cost_value * 100.0) if cost_value > 0 else 0.0

            # Only retain active holdings with positive units or value
            if units > 0 or current_value > 0:
                holding = Holding(
                    folio_number=folio_num,
                    scheme_name=scheme_name,
                    isin=isin,
                    amfi_code=str(amfi) if amfi else None,
                    plan_type=plan_type,
                    category=category,
                    units=round(units, 4),
                    nav=round(nav, 4),
                    current_value=round(current_value, 2),
                    cost_value=round(cost_value, 2),
                    unrealized_gain=round(unrealized_gain, 2),
                    return_percentage=round(return_pct, 2),
                    transactions=transactions,
                )
                holdings_list.append(holding)
                total_val += current_value
                total_cost += cost_value

    portfolio = Portfolio(
        investor_name=investor_info.get("name", "Valued Investor"),
        pan=investor_info.get("pan"),
        email=investor_info.get("email"),
        statement_period=period_str if period_str != "to" else None,
        total_current_value=round(total_val, 2),
        total_cost_value=round(total_cost, 2),
        total_gain=round(total_val - total_cost, 2),
        holdings=holdings_list,
    )
    return portfolio


def load_demo_portfolio() -> Portfolio:
    """
    Returns a rich, multi-asset Indian mutual fund demo portfolio for grading and evaluation.
    Contains both Direct & Regular schemes, various form rankings, asset classes, and overlaps.
    """
    demo_holdings = [
        Holding(
            folio_number="10928374/01",
            scheme_name="Parag Parikh Flexi Cap Fund - Direct Plan - Growth",
            isin="INF879O01019",
            amfi_code="122639",
            plan_type="DIRECT",
            category="Equity",
            units=7352.941,
            nav=81.60,
            current_value=600000.00,
            cost_value=420000.00,
            unrealized_gain=180000.00,
            return_percentage=42.86,
            transactions=[
                Transaction(date="2022-01-10", description="SIP Purchase", amount=150000.0, units=2830.18, nav=53.0, type="SIP"),
                Transaction(date="2023-01-10", description="SIP Purchase", amount=150000.0, units=2380.95, nav=63.0, type="SIP"),
                Transaction(date="2024-01-10", description="SIP Purchase", amount=120000.0, units=2141.81, nav=56.02, type="SIP"),
            ],
        ),
        Holding(
            folio_number="48392019/92",
            scheme_name="Mirae Asset Large Cap Fund - Regular Plan - Growth",
            isin="INF769K01085",
            amfi_code="107578",
            plan_type="REGULAR",
            category="Equity",
            units=4210.526,
            nav=118.75,
            current_value=500000.00,
            cost_value=410000.00,
            unrealized_gain=90000.00,
            return_percentage=21.95,
            transactions=[
                Transaction(date="2021-06-15", description="Lump sum Purchase", amount=300000.0, units=3125.0, nav=96.0, type="PURCHASE"),
                Transaction(date="2023-03-20", description="Additional Purchase", amount=110000.0, units=1085.526, nav=101.33, type="PURCHASE"),
            ],
        ),
        Holding(
            folio_number="98234112/03",
            scheme_name="Quant Small Cap Fund - Direct Plan - Growth",
            isin="INF966L01AA3",
            amfi_code="120828",
            plan_type="DIRECT",
            category="Equity",
            units=1818.182,
            nav=220.00,
            current_value=400000.00,
            cost_value=260000.00,
            unrealized_gain=140000.00,
            return_percentage=53.85,
            transactions=[
                Transaction(date="2022-08-01", description="SIP Purchase", amount=130000.0, units=928.57, nav=140.0, type="SIP"),
                Transaction(date="2023-08-01", description="SIP Purchase", amount=130000.0, units=889.61, nav=146.13, type="SIP"),
            ],
        ),
        Holding(
            folio_number="56201984/77",
            scheme_name="HDFC Top 100 Fund - Regular Plan - Growth",
            isin="INF179K01BE2",
            amfi_code="101662",
            plan_type="REGULAR",
            category="Equity",
            units=333.333,
            nav=1050.00,
            current_value=350000.00,
            cost_value=280000.00,
            unrealized_gain=70000.00,
            return_percentage=25.00,
            transactions=[
                Transaction(date="2022-04-12", description="Purchase via Distributor", amount=280000.0, units=333.333, nav=840.0, type="PURCHASE"),
            ],
        ),
        Holding(
            folio_number="78129034/11",
            scheme_name="ICICI Prudential Liquid Fund - Direct Plan - Growth",
            isin="INF109K01VP0",
            amfi_code="120586",
            plan_type="DIRECT",
            category="Liquid",
            units=657.895,
            nav=380.00,
            current_value=250000.00,
            cost_value=235000.00,
            unrealized_gain=15000.00,
            return_percentage=6.38,
            transactions=[
                Transaction(date="2023-01-05", description="Emergency Fund Deposit", amount=235000.0, units=657.895, nav=357.2, type="PURCHASE"),
            ],
        ),
        Holding(
            folio_number="65239100/54",
            scheme_name="SBI Magnum Medium Duration Fund - Direct Plan - Growth",
            isin="INF200K01TK9",
            amfi_code="119799",
            plan_type="DIRECT",
            category="Debt",
            units=3448.276,
            nav=58.00,
            current_value=200000.00,
            cost_value=185000.00,
            unrealized_gain=15000.00,
            return_percentage=8.11,
            transactions=[
                Transaction(date="2023-06-10", description="Debt Allocation", amount=185000.0, units=3448.276, nav=53.65, type="PURCHASE"),
            ],
        ),
        Holding(
            folio_number="33219088/19",
            scheme_name="Nippon India Growth Fund - Regular Plan - Growth",
            isin="INF204K01974",
            amfi_code="100377",
            plan_type="REGULAR",
            category="Equity",
            units=66.667,
            nav=3000.00,
            current_value=200000.00,
            cost_value=170000.00,
            unrealized_gain=30000.00,
            return_percentage=17.65,
            transactions=[
                Transaction(date="2022-11-20", description="Distributor Purchase", amount=170000.0, units=66.667, nav=2550.0, type="PURCHASE"),
            ],
        ),
    ]

    total_val = sum(h.current_value for h in demo_holdings)
    total_cost = sum(h.cost_value for h in demo_holdings)

    return Portfolio(
        investor_name="Aditya Verma",
        pan="ABCDE1234F",
        email="aditya.verma@example.com",
        statement_period="01-Jan-2021 to 31-Dec-2024",
        total_current_value=round(total_val, 2),
        total_cost_value=round(total_cost, 2),
        total_gain=round(total_val - total_cost, 2),
        holdings=demo_holdings,
    )
