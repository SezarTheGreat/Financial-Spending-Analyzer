"""
Gemini Multimodal Document Parser for Mutual Fund CAS PDFs
Uses Google GenAI SDK (Gemini 2.5/2.0 Flash) to visually parse complex CAMS/KFintech
Consolidated Account Statement (CAS) PDFs into structured Portfolio models.
"""
import io
import os
import json
import logging
from typing import Optional, Dict, Any, List
import pypdf

from google import genai
from google.genai import types

from .schemas import Portfolio, Holding, Transaction, PlanType
from .market_data import market_data_service

logger = logging.getLogger(__name__)


def decrypt_pdf_bytes(pdf_bytes: bytes, password: Optional[str] = None) -> bytes:
    """
    Decrypts password-protected PDF in-memory using pypdf.
    Returns decrypted PDF bytes.
    """
    try:
        reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
        if reader.is_encrypted:
            if not password:
                raise ValueError("CAS PDF is password-protected. Please provide your CAS password or PAN.")
            
            decrypt_res = reader.decrypt(password)
            if decrypt_res == 0:
                raise ValueError("Incorrect CAS password. Please check your CAMS/KFintech password or PAN.")

        writer = pypdf.PdfWriter()
        for page in reader.pages:
            writer.add_page(page)

        out_io = io.BytesIO()
        writer.write(out_io)
        out_io.seek(0)
        return out_io.getvalue()
    except ValueError:
        raise
    except Exception as e:
        logger.warning(f"pypdf decryption encountered issue: {e}. Passing raw bytes.")
        return pdf_bytes


class GeminiDocParser:
    def __init__(self, api_key: Optional[str] = None, model_name: str = "gemini-2.5-flash"):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        self.model_name = model_name
        self._client: Optional[genai.Client] = None

        if self.api_key:
            try:
                self._client = genai.Client(api_key=self.api_key)
                logger.info(f"GeminiDocParser initialized with model {self.model_name}")
            except Exception as e:
                logger.warning(f"Failed to initialize Gemini client for DocParser: {e}")
                self._client = None
        else:
            logger.info("No GEMINI_API_KEY detected for GeminiDocParser.")

    def is_available(self) -> bool:
        return self._client is not None

    async def parse_cas_pdf(self, pdf_bytes: bytes, password: Optional[str] = None) -> Optional[Portfolio]:
        """
        Parses CAS PDF directly into structured Portfolio using Gemini Multimodal Document Understanding.
        """
        if not self.is_available():
            logger.info("Gemini client not available. Skipping multimodal PDF parse.")
            return None

        # 1. Decrypt PDF in-memory if needed
        decrypted_bytes = decrypt_pdf_bytes(pdf_bytes, password)

        # 2. Build extraction prompt & schema instructions
        prompt = """
You are an expert institutional Indian Mutual Fund auditor and Consolidated Account Statement (CAS) data extractor.
Analyze this CAMS / KFintech Consolidated Account Statement (CAS) PDF and extract the complete mutual fund portfolio details into strict JSON.

CRITICAL INSTRUCTION FOR SUMMARY TABLES:
If the document contains a "PORTFOLIO SUMMARY" table (listing Mutual Fund AMC names, Cost Value INR, and Market Value INR), you MUST extract the exact "Cost Value (INR)" and "Market Value (INR)" from that table for every mutual fund!
Ensure that:
- total_cost_value matches the exact Total in the Cost Value column (e.g. 10,412.25).
- total_current_value matches the exact Total in the Market Value column (e.g. 10,796.28).
- total_gain is total_current_value - total_cost_value.

Extract:
1. "investor_name": Exact name of the investor as stated in the CAS.
2. "pan": PAN number if available, else null.
3. "email": Email address if available, else null.
4. "statement_period": Exact statement date range (e.g., "15-Aug-2025 to 14-Aug-2026").
5. "total_current_value": Total current valuation in INR across all mutual fund holdings.
6. "total_cost_value": Total invested purchase cost in INR across all mutual fund holdings.
7. "total_gain": Total unrealized gain/loss in INR (total_current_value - total_cost_value).
8. "holdings": An array of every mutual fund holding in the document:
   - "folio_number": Folio number for this scheme.
   - "scheme_name": Full official scheme name including plan and option (e.g., "Parag Parikh Flexi Cap Fund - Direct Plan - Growth").
   - "isin": ISIN code if listed, else null.
   - "amfi_code": AMFI scheme code if listed, else null.
   - "plan_type": "DIRECT" or "REGULAR" (check if word DIRECT or REGULAR appears).
   - "category": Sector/SEBI category (e.g. "Flexi Cap", "Large Cap", "Mid Cap", "Small Cap", "Multi Asset", "Debt", "Commodities", "Liquid", "International Equity").
   - "units": Closing unit balance.
   - "nav": Closing Net Asset Value (NAV) per unit on the valuation date.
   - "cost_value": Total purchase/cost value in INR invested into this scheme (sum of all purchase amounts).
   - "current_value": Current market value in INR (units * nav).
   - "unrealized_gain": current_value - cost_value.
   - "return_percentage": Absolute gain percentage ((unrealized_gain / cost_value) * 100).
   - "portfolio_weight_pct": Weight percentage of this scheme relative to the total portfolio value.
   - "transactions": Array of all historical purchase / SIP / redemption transactions listed for this scheme:
     - "date": "YYYY-MM-DD"
     - "description": Description (e.g. "SIP Purchase", "Lump sum Purchase")
     - "amount": Transaction amount in INR (positive for purchases, negative for redemptions)
     - "units": Units transacted
     - "nav": NAV on transaction date
     - "type": "PURCHASE", "SIP", "REDEMPTION", "SWITCH_IN", "SWITCH_OUT", or "DIVIDEND"

Return ONLY valid JSON matching this structure.
"""

        try:
            pdf_part = types.Part.from_bytes(data=decrypted_bytes, mime_type="application/pdf")
            response = self._client.models.generate_content(
                model=self.model_name,
                contents=[pdf_part, prompt],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.0,
                )
            )

            raw_text = response.text.strip()
            if raw_text.startswith("```json"):
                raw_text = raw_text.replace("```json", "", 1).replace("```", "").strip()
            elif raw_text.startswith("```"):
                raw_text = raw_text.replace("```", "").strip()

            parsed_json = json.loads(raw_text)

            # Ensure portfolio weights and totals are accurate
            holdings = []
            total_val = 0.0
            total_cost = 0.0

            for h in parsed_json.get("holdings", []):
                h_name = h.get("scheme_name", "")
                h_units = float(h.get("units", 0.0) or 0.0)
                h_nav = float(h.get("nav", 0.0) or 0.0)
                h_val = float(h.get("current_value", 0.0) or (h_units * h_nav))
                h_cost = float(h.get("cost_value", 0.0) or h_val)
                h_gain = round(h_val - h_cost, 2)
                h_ret = round((h_gain / h_cost * 100.0), 2) if h_cost > 0 else 0.0

                # Resolve AMFI code & category if not explicit
                amfi = h.get("amfi_code") or market_data_service.resolve_amfi_code(h_name, None)
                cat = h.get("category") or market_data_service.classify_category(h_name)
                plan = "DIRECT" if "DIRECT" in h_name.upper() else "REGULAR"

                txns = []
                for tx in h.get("transactions", []):
                    txns.append(
                        Transaction(
                            date=str(tx.get("date", "")),
                            description=str(tx.get("description", "Purchase")),
                            amount=float(tx.get("amount", 0.0) or 0.0),
                            units=float(tx.get("units", 0.0) or 0.0),
                            nav=float(tx.get("nav", 0.0) or 0.0),
                            type=str(tx.get("type", "PURCHASE")).upper(),
                        )
                    )

                holding_obj = Holding(
                    folio_number=str(h.get("folio_number", "–")),
                    scheme_name=h_name,
                    isin=h.get("isin"),
                    amfi_code=amfi,
                    plan_type=plan,
                    category=cat,
                    units=round(h_units, 4),
                    nav=round(h_nav, 4),
                    current_value=round(h_val, 2),
                    cost_value=round(h_cost, 2),
                    unrealized_gain=h_gain,
                    return_percentage=h_ret,
                    portfolio_weight_pct=float(h.get("portfolio_weight_pct", 0.0) or 0.0),
                    transactions=txns,
                )
                holdings.append(holding_obj)
                total_val += h_val
                total_cost += h_cost

            if total_val > 0:
                for h in holdings:
                    h.portfolio_weight_pct = round((h.current_value / total_val) * 100.0, 2)

            portfolio = Portfolio(
                investor_name=parsed_json.get("investor_name", "Valued Investor"),
                pan=parsed_json.get("pan"),
                email=parsed_json.get("email"),
                statement_period=parsed_json.get("statement_period"),
                total_current_value=round(parsed_json.get("total_current_value") or total_val, 2),
                total_cost_value=round(parsed_json.get("total_cost_value") or total_cost, 2),
                total_gain=round(total_val - total_cost, 2),
                holdings=holdings,
            )
            logger.info(f"Gemini DocParser successfully extracted {len(holdings)} holdings from CAS PDF.")
            return portfolio
        except Exception as e:
            logger.warning(f"Gemini DocParser error: {e}. Falling back to standard parser.")
            return None


gemini_doc_parser = GeminiDocParser()
