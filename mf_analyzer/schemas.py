"""
Pydantic Schemas & Data Contracts for Mutual Fund Analyzer
"""
from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field
from datetime import datetime

# Plan types
PlanType = Literal["DIRECT", "REGULAR"]

# Risk Profile types
RiskProfile = Literal["Conservative", "Moderate", "Aggressive"]

# Form Classifier Tiers
FormTier = Literal["In-Form", "On-Track", "Off-Track", "Out-of-Form"]

# Action types for fund recommendations
FundAction = Literal["HOLD", "CONTINUE_SIP", "PAUSE_SIP", "SWITCH_TO_DIRECT", "EXIT_AND_REINVEST"]

# Alert severity levels
AlertSeverity = Literal["HIGH", "MEDIUM", "LOW"]

# Action checklist priority
StepPriority = Literal["IMMEDIATE", "SHORT_TERM", "LONG_TERM"]


class Transaction(BaseModel):
    date: str
    description: str
    amount: float
    units: float
    nav: float
    type: str  # e.g., 'PURCHASE', 'REDEMPTION', 'SIP', 'DIVIDEND', 'SWITCH_IN', 'SWITCH_OUT'


class Holding(BaseModel):
    folio_number: str
    scheme_name: str
    isin: Optional[str] = None
    amfi_code: Optional[str] = None
    plan_type: PlanType = "DIRECT"
    category: str = "Equity"  # Equity, Debt, Commodities, Hybrid, Liquid, Large Cap, Mid Cap, Small Cap, Flexi Cap, etc.
    units: float = 0.0
    nav: float = 0.0
    current_value: float = 0.0
    cost_value: float = 0.0
    unrealized_gain: float = 0.0
    return_percentage: float = 0.0
    portfolio_weight_pct: float = 0.0  # Holding allocation % in portfolio
    xirr: Optional[float] = None
    transactions: List[Transaction] = Field(default_factory=list)


class Portfolio(BaseModel):
    investor_name: Optional[str] = "Valued Investor"
    pan: Optional[str] = None
    email: Optional[str] = None
    statement_period: Optional[str] = None
    total_current_value: float = 0.0
    total_cost_value: float = 0.0
    total_gain: float = 0.0
    holdings: List[Holding] = Field(default_factory=list)


# --- Quant Engine Output Models ---

class FundRollingCAGR(BaseModel):
    scheme_name: str
    amfi_code: Optional[str] = None
    category: str = "Equity"
    cagr_1y: Optional[float] = None
    cagr_3y: Optional[float] = None
    category_benchmark_1y: float
    category_benchmark_3y: float
    alpha_1y: Optional[float] = None
    alpha_3y: Optional[float] = None
    portfolio_weight_pct: Optional[float] = None
    xirr: Optional[float] = None


class FundFormDiagnostic(BaseModel):
    scheme_name: str
    category: str
    plan_type: PlanType
    cagr_1y: Optional[float] = None
    cagr_3y: Optional[float] = None
    alpha_1y: Optional[float] = None
    alpha_3y: Optional[float] = None
    portfolio_weight_pct: Optional[float] = None
    xirr: Optional[float] = None
    form_tier: FormTier
    rationale: str


class CostDragAnalysis(BaseModel):
    total_regular_corpus: float
    annual_expense_drag_percentage: float = 0.85
    annual_expense_drag_amount: float
    projected_10yr_cost_drag: float
    projected_10yr_direct_value: float
    projected_10yr_regular_value: float
    affected_schemes_count: int
    affected_schemes: List[str]


class AssetAllocation(BaseModel):
    equity_value: float = 0.0
    equity_pct: float = 0.0
    debt_value: float = 0.0
    debt_pct: float = 0.0
    commodities_value: float = 0.0
    commodities_pct: float = 0.0
    cash_liquid_value: float = 0.0
    cash_liquid_pct: float = 0.0
    other_value: float = 0.0
    other_pct: float = 0.0


class AssetDriftAnalysis(BaseModel):
    risk_profile: RiskProfile
    target_equity_range: List[float]  # e.g., [50.0, 70.0]
    target_equity_mid: float          # e.g., 60.0
    actual_equity_pct: float
    drift_pct: float                  # actual - mid
    drift_status: Literal["Aligned", "Over-Allocated to Equity", "Under-Allocated to Equity", "High Risk Drift"]
    recommendation: str


class CommonStockHolding(BaseModel):
    stock_name: str
    weight_in_a: float
    weight_in_b: float
    overlap_contribution: float  # min(weight_a, weight_b)


class OverlapPair(BaseModel):
    fund_a: str
    fund_b: str
    overlap_percentage: float
    common_holdings: List[str]
    common_stocks_breakdown: List[CommonStockHolding] = []
    diversification_verdict: str = "Good Diversification"
    overlap_level: str = "Low Overlap"  # "Low Overlap", "Moderate Overlap", "High Overlap"


class FundConstituentStock(BaseModel):
    stock_name: str
    weight: float


class OverlapMatrixAnalysis(BaseModel):
    pairs: List[OverlapPair]
    high_overlap_pairs: List[OverlapPair]  # Overlap >= 30%
    fund_holdings_map: Dict[str, List[FundConstituentStock]] = {}


class QuantDiagnostics(BaseModel):
    portfolio_xirr: Optional[float] = None
    rolling_cagrs: List[FundRollingCAGR]
    form_ratings: List[FundFormDiagnostic]
    cost_drag: CostDragAnalysis
    asset_allocation: AssetAllocation
    asset_drift: AssetDriftAnalysis
    overlap_matrix: OverlapMatrixAnalysis


# --- AI Engine Structured Output Models (Gemini Schema) ---

class KeyAlert(BaseModel):
    severity: AlertSeverity = Field(description="Alert severity: HIGH, MEDIUM, or LOW")
    title: str = Field(description="Brief headline for the alert")
    description: str = Field(description="Detailed explanation of the risk or anomaly")
    affected_schemes: List[str] = Field(default_factory=list, description="List of scheme names affected")


class FundRecommendation(BaseModel):
    scheme_name: str = Field(description="Exact mutual fund scheme name")
    action: FundAction = Field(description="Recommended action: HOLD, CONTINUE_SIP, PAUSE_SIP, SWITCH_TO_DIRECT, or EXIT_AND_REINVEST")
    rationale: str = Field(description="Quant-backed rationale for the recommendation")
    target_alternative: Optional[str] = Field(default=None, description="Suggested alternative fund or category if switching or exiting")


class StepByStepChecklist(BaseModel):
    step: int = Field(description="Sequential step number starting at 1")
    title: str = Field(description="Concise action step title")
    description: str = Field(description="Detailed execution instructions for the investor")
    priority: StepPriority = Field(description="Priority: IMMEDIATE, SHORT_TERM, or LONG_TERM")


class AIAnalysisReport(BaseModel):
    health_score: int = Field(ge=0, le=100, description="Overall portfolio health score from 0 (critical) to 100 (flawless)")
    risk_alignment_verdict: str = Field(description="In-depth analysis of portfolio risk vs target risk profile")
    key_alerts: List[KeyAlert] = Field(description="List of prioritized risk alerts")
    fund_recommendations: List[FundRecommendation] = Field(description="Specific actionable recommendations per fund")
    step_by_step_rebalance_checklist: List[StepByStepChecklist] = Field(description="Chronological rebalancing checklist")


# --- Top-Level Audit Response & Request Models ---

class ReEvaluateRiskRequest(BaseModel):
    audit_id: Optional[str] = None
    portfolio: Optional[Portfolio] = None
    risk_profile: RiskProfile = "Moderate"


class PortfolioAuditResponse(BaseModel):
    audit_id: str
    timestamp: datetime
    risk_profile: RiskProfile
    portfolio_summary: Dict[str, Any]
    quant_diagnostics: QuantDiagnostics
    ai_insights: AIAnalysisReport
