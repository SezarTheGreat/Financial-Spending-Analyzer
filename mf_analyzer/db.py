"""
Database Layer (Supabase Integration)
Persists mutual fund holdings and complete quant/AI audit payloads with resilient offline fallback.
"""
import os
import logging
import uuid
from typing import Optional, Dict, Any, List
from datetime import datetime
from supabase import create_client, Client

from .schemas import Portfolio, Holding, PortfolioAuditResponse

logger = logging.getLogger(__name__)


class SupabasePortfolioDB:
    def __init__(self, supabase_url: Optional[str] = None, supabase_key: Optional[str] = None):
        self.url = supabase_url or os.environ.get("SUPABASE_URL")
        self.key = supabase_key or os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("SUPABASE_SERVICE_KEY")
        self.client: Optional[Client] = None
        self._memory_holdings: Dict[str, List[Dict[str, Any]]] = {}
        self._memory_audits: Dict[str, Dict[str, Any]] = {}
        self._memory_portfolios: Dict[str, Portfolio] = {}

        if self.url and self.key:
            try:
                self.client = create_client(self.url, self.key)
                logger.info("Supabase client initialized successfully for mf_analyzer.")
            except Exception as e:
                logger.warning(f"Failed to initialize Supabase client: {e}. Defaulting to in-memory store.")
                self.client = None
        else:
            logger.info("Supabase credentials not provided. Using in-memory persistence.")

    def save_portfolio(self, audit_id: str, portfolio: Portfolio):
        """
        Caches portfolio model for fast re-evaluation.
        """
        self._memory_portfolios[audit_id] = portfolio

    def get_portfolio(self, audit_id: str) -> Optional[Portfolio]:
        """
        Retrieves cached portfolio model by audit_id.
        """
        return self._memory_portfolios.get(audit_id)

    def save_holdings(self, portfolio_id: str, holdings: List[Holding]) -> bool:
        """
        Persists extracted user holdings into `mf_holdings`.
        """
        records = []
        for h in holdings:
            records.append({
                "portfolio_id": portfolio_id,
                "folio_number": h.folio_number,
                "scheme_name": h.scheme_name,
                "isin": h.isin,
                "amfi_code": h.amfi_code,
                "plan_type": h.plan_type,
                "category": h.category,
                "units": h.units,
                "nav": h.nav,
                "current_value": h.current_value,
                "cost_value": h.cost_value,
                "unrealized_gain": h.unrealized_gain,
                "return_percentage": h.return_percentage,
                "created_at": datetime.now().isoformat(),
            })

        self._memory_holdings[portfolio_id] = records

        if self.client:
            try:
                # Upsert / insert into mf_holdings table
                self.client.table("mf_holdings").upsert(records).execute()
                logger.info(f"Persisted {len(records)} holdings to Supabase table 'mf_holdings'.")
                return True
            except Exception as e:
                logger.warning(f"Supabase mf_holdings insert failed: {e}. Saved in local memory.")
                return False
        return True

    def save_audit_report(self, audit: PortfolioAuditResponse) -> bool:
        """
        Persists full audit payload into `portfolio_audits`.
        """
        record = {
            "audit_id": audit.audit_id,
            "timestamp": audit.timestamp.isoformat(),
            "risk_profile": audit.risk_profile,
            "health_score": audit.ai_insights.health_score,
            "total_valuation": audit.portfolio_summary.get("total_current_value", 0.0),
            "quant_diagnostics": audit.quant_diagnostics.model_dump(),
            "ai_insights": audit.ai_insights.model_dump(),
            "portfolio_summary": audit.portfolio_summary,
            "created_at": datetime.now().isoformat(),
        }

        self._memory_audits[audit.audit_id] = record

        if self.client:
            try:
                self.client.table("portfolio_audits").insert(record).execute()
                logger.info(f"Persisted audit {audit.audit_id} to Supabase table 'portfolio_audits'.")
                return True
            except Exception as e:
                logger.warning(f"Supabase portfolio_audits insert failed: {e}. Saved in local memory.")
                return False
        return True

    def get_audit_report(self, audit_id: str) -> Optional[Dict[str, Any]]:
        """
        Fetches an audit report by audit_id.
        """
        if self.client:
            try:
                resp = self.client.table("portfolio_audits").select("*").eq("audit_id", audit_id).execute()
                if resp.data and len(resp.data) > 0:
                    return resp.data[0]
            except Exception as e:
                logger.warning(f"Failed to fetch audit from Supabase: {e}")

        return self._memory_audits.get(audit_id)


# Global singleton instance
db_service = SupabasePortfolioDB()
