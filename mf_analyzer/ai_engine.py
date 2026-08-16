"""
Structured AI Insight Layer (Gemini)
Uses the Google GenAI SDK with strict Pydantic responseSchema to synthesize
quantitative outputs into risk-aware, actionable rebalancing recommendations.
"""
import os
import json
import logging
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv

load_dotenv()
from pydantic import ValidationError

from google import genai
from google.genai import types

from .schemas import (
    Portfolio,
    QuantDiagnostics,
    AIAnalysisReport,
    KeyAlert,
    FundRecommendation,
    StepByStepChecklist,
    RiskProfile,
    AlertSeverity,
    FundAction,
    StepPriority,
)

logger = logging.getLogger(__name__)


class AIEngine:
    def __init__(self, api_key: Optional[str] = None, model_name: str = "gemini-3.7-flash"):
        if api_key is None:
            self.api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        else:
            self.api_key = api_key if api_key else None
        self.model_name = model_name
        self._client: Optional[genai.Client] = None

        if self.api_key:
            try:
                self._client = genai.Client(api_key=self.api_key)
                logger.info(f"Google GenAI client initialized with model {self.model_name}")
            except Exception as e:
                logger.warning(f"Failed to initialize Google GenAI client: {e}")
                self._client = None
        else:
            logger.info("No GEMINI_API_KEY / GOOGLE_API_KEY detected. AI Engine will operate in high-precision rule fallback mode.")

    def _build_quant_context_prompt(self, portfolio: Portfolio, quant: QuantDiagnostics, risk_profile: RiskProfile) -> str:
        """
        Builds a comprehensive, zero-hallucination quant prompt injecting exact figures.
        """
        portfolio_summary = {
            "investor_name": portfolio.investor_name,
            "total_current_value_inr": portfolio.total_current_value,
            "total_cost_value_inr": portfolio.total_cost_value,
            "total_gain_inr": portfolio.total_gain,
            "portfolio_xirr_pct": quant.portfolio_xirr,
            "risk_profile": risk_profile,
            "holdings_count": len(portfolio.holdings),
        }

        holdings_data = []
        for h in portfolio.holdings:
            holdings_data.append({
                "scheme_name": h.scheme_name,
                "category": h.category,
                "plan_type": h.plan_type,
                "current_value": h.current_value,
                "cost_value": h.cost_value,
                "portfolio_weight_pct": h.portfolio_weight_pct,
                "return_percentage": h.return_percentage,
                "xirr": h.xirr,
            })

        rolling_cagrs = [c.model_dump() for c in quant.rolling_cagrs]
        form_ratings = [f.model_dump() for f in quant.form_ratings]
        cost_drag = quant.cost_drag.model_dump()
        asset_allocation = quant.asset_allocation.model_dump()
        asset_drift = quant.asset_drift.model_dump()
        overlap_matrix = {
            "high_overlap_pairs": [p.model_dump() for p in quant.overlap_matrix.high_overlap_pairs],
            "total_pairs_evaluated": len(quant.overlap_matrix.pairs),
        }

        prompt = f"""
You are an institutional Quant Architect and Chief Investment Officer analyzing an Indian Mutual Fund portfolio.
All numerical computations below have been deterministically computed by our quantitative engine.
DO NOT recalculate or hallucinate mathematical figures. Reason strictly over the provided quantitative diagnostics to generate actionable rebalancing insights.

### 1. INVESTOR & PORTFOLIO CONTEXT
{json.dumps(portfolio_summary, indent=2)}

### 2. HOLDINGS BREAKDOWN
{json.dumps(holdings_data, indent=2)}

### 3. QUANTITATIVE DIAGNOSTICS
- **Portfolio & Fund XIRR / Rolling CAGR & Alpha vs Category Benchmarks**:
{json.dumps(rolling_cagrs, indent=2)}

- **4-Tier Form Classifications (In-Form, On-Track, Off-Track, Out-of-Form)**:
{json.dumps(form_ratings, indent=2)}

- **Cost Drag Analysis (Regular vs Direct Expense Drag & 10-Year Compounding Loss)**:
{json.dumps(cost_drag, indent=2)}

- **Asset Allocation (Equity / Debt / Commodities / Liquid)**:
{json.dumps(asset_allocation, indent=2)}

- **Asset Drift vs {risk_profile} Target Range**:
{json.dumps(asset_drift, indent=2)}

- **Portfolio Overlap Matrix**:
{json.dumps(overlap_matrix, indent=2)}

### INSTRUCTIONS FOR DETERMINISTIC QUANT HEALTH SCORE (0-100):
Synthesize this quantitative audit into a structured output conforming strictly to the requested schema.
Calculate 'health_score' using this strict institutional quantitative deduction model starting at 100:
1. Asset Allocation Drift Penalty (0 to 35 pts):
   - Aligned (within target range): 0 pts
   - Under-Allocation shortfall: deduct 0.9 pts per 1.0% equity shortfall below target floor (e.g. 37% gap = -33 pts)
   - Over-Allocation surplus: deduct 1.0 pts per 1.0% equity excess above target ceiling (e.g. 20% gap = -20 pts)
2. Cost Drag & Commission Penalty (0 to 30 pts):
   - Deduct (Regular_Corpus / Total_Corpus) * 30 pts (+ 5 pts baseline if any regular plans exist)
3. Fund Form & Alpha Drag Penalty (0 to 30 pts):
   - Deduct 15 pts per Out-of-Form fund, 8 pts per Off-Track fund, 4 pts per Lagging Alpha fund
4. Stock Overlap & Duplication Penalty (0 to 20 pts):
   - Deduct 8 pts per High Overlap Pair (>=30% stock overlap)
Final Health Score must strictly equal: max(10, min(98, 100 - total_penalties)).

Output fields:
1. 'health_score': An integer (0-100) computed using the above strict formula.
2. 'risk_alignment_verdict': Detailed synthesis of risk drift and suitability for a '{risk_profile}' investor.
3. 'key_alerts': Severity-tagged alerts (HIGH, MEDIUM, LOW) capturing critical risks.
4. 'fund_recommendations': Actionable advice for EVERY holding ('HOLD', 'CONTINUE_SIP', 'PAUSE_SIP', 'SWITCH_TO_DIRECT', 'EXIT_AND_REINVEST') with concrete rationale.
5. 'step_by_step_rebalance_checklist': A prioritized chronological roadmap for the investor to execute.
"""
        return prompt

    def generate_deterministic_insights(self, portfolio: Portfolio, quant: QuantDiagnostics, risk_profile: RiskProfile) -> AIAnalysisReport:
        """
        Deterministic rule-based AI synthesizer used when GenAI API key is unavailable or in offline environments.
        Guarantees 100% schema compliance and rigorous, conservative institutional quant reasoning.
        """
        # Calculate Base Health Score (out of 100)
        score = 100

        # 1. Asset Allocation Drift Penalty (Continuous proportional penalty up to -35 points)
        target_range = quant.asset_drift.target_equity_range
        actual_eq = quant.asset_drift.actual_equity_pct
        if target_range[0] <= actual_eq <= target_range[1]:
            drift_penalty = 0
        elif actual_eq < target_range[0]:
            gap = target_range[0] - actual_eq
            drift_penalty = int(min(35, max(8, gap * 0.9)))
        else:
            gap = actual_eq - target_range[1]
            drift_penalty = int(min(35, max(8, gap * 1.0)))
        score -= drift_penalty

        # 2. Cost Drag Penalty: up to -30 points
        if quant.cost_drag.affected_schemes_count > 0:
            reg_ratio = quant.cost_drag.total_regular_corpus / max(1.0, portfolio.total_current_value)
            drag_penalty = int(min(30.0, reg_ratio * 25.0 + 5.0))
            score -= drag_penalty

        # 3. Form Rating & Alpha Drag Penalty: up to -30 points
        out_of_form_count = sum(1 for f in quant.form_ratings if f.form_tier == "Out-of-Form")
        off_track_count = sum(1 for f in quant.form_ratings if f.form_tier == "Off-Track")
        lagging_alpha_count = sum(1 for f in quant.form_ratings if (f.alpha_1y or 0.0) < -2.0)
        score -= min(30, (out_of_form_count * 15 + off_track_count * 8 + lagging_alpha_count * 4))

        # 4. High Overlap Penalty: up to -20 points
        if len(quant.overlap_matrix.high_overlap_pairs) > 0:
            score -= min(20, len(quant.overlap_matrix.high_overlap_pairs) * 8)

        # 5. Over-diversification (>10 fragmented funds): up to -10 points
        if len(portfolio.holdings) > 10:
            score -= min(10, (len(portfolio.holdings) - 10) * 2)

        health_score = max(10, min(98, score))

        # Risk Alignment Verdict
        drift = quant.asset_drift
        if drift.drift_status == "Aligned":
            verdict = (
                f"Your portfolio is strongly aligned with your {risk_profile} risk profile. "
                f"Your equity allocation of {drift.actual_equity_pct}% sits squarely within your target range of {drift.target_equity_range[0]}% to {drift.target_equity_range[1]}%."
            )
        elif drift.drift_status == "High Risk Drift":
            verdict = (
                f"Critical risk mismatch detected for your {risk_profile} profile. "
                f"Your equity allocation of {drift.actual_equity_pct}% significantly breaches the target ceiling of {drift.target_equity_range[1]}% (drift of {drift.drift_pct:+.2f}% vs mid-target). "
                f"This exposes your capital to heightened drawdown risk during equity market corrections."
            )
        elif drift.drift_status == "Over-Allocated to Equity":
            verdict = (
                f"Moderate equity over-allocation detected for your {risk_profile} profile. "
                f"Your equity exposure is {drift.actual_equity_pct}%, which is above the target range ceiling of {drift.target_equity_range[1]}%. "
                f"Rebalancing surplus equity profits into debt or hybrid funds will restore optimal risk-reward balance."
            )
        else:
            verdict = (
                f"Portfolio is under-allocated to growth assets for your {risk_profile} profile. "
                f"Your equity exposure is {drift.actual_equity_pct}%, lagging the target range of {drift.target_equity_range[0]}% to {drift.target_equity_range[1]}%. "
                f"Increasing equity participation will ensure long-term purchasing power beats inflation."
            )

        # Key Alerts
        alerts: List[KeyAlert] = []

        if quant.cost_drag.affected_schemes_count > 0:
            alerts.append(
                KeyAlert(
                    severity="HIGH" if quant.cost_drag.total_regular_corpus > 200000 else "MEDIUM",
                    title="Substantial Distributor Commission Drag (Regular Plans)",
                    description=(
                        f"You hold {quant.cost_drag.affected_schemes_count} Regular plan fund(s) totaling ₹{quant.cost_drag.total_regular_corpus:,.2f}. "
                        f"Intermediary commissions drain ~₹{quant.cost_drag.annual_expense_drag_amount:,.2f} annually, projected to cause a ₹{quant.cost_drag.projected_10yr_cost_drag:,.2f} compounded wealth loss over 10 years."
                    ),
                    affected_schemes=quant.cost_drag.affected_schemes,
                )
            )

        if quant.asset_drift.drift_status in ["High Risk Drift", "Over-Allocated to Equity", "Under-Allocated to Equity"]:
            alerts.append(
                KeyAlert(
                    severity="HIGH" if quant.asset_drift.drift_status == "High Risk Drift" else "MEDIUM",
                    title=f"Asset Allocation Drift ({quant.asset_drift.drift_status})",
                    description=quant.asset_drift.recommendation,
                    affected_schemes=[h.scheme_name for h in portfolio.holdings if h.category in ["Equity", "Large Cap", "Mid Cap", "Small Cap", "Flexi Cap"]],
                )
            )

        underperforming_funds = [f.scheme_name for f in quant.form_ratings if f.form_tier in ["Out-of-Form", "Off-Track"]]
        if underperforming_funds:
            alerts.append(
                KeyAlert(
                    severity="HIGH" if any(f.form_tier == "Out-of-Form" for f in quant.form_ratings) else "MEDIUM",
                    title="Funds Lagging Category Benchmarks",
                    description=f"{len(underperforming_funds)} fund(s) exhibit sub-benchmark alpha or persistent performance drag over 1-year and 3-year rolling horizons.",
                    affected_schemes=underperforming_funds,
                )
            )

        if len(quant.overlap_matrix.high_overlap_pairs) > 0:
            overlap_descs = [f"{p.fund_a} & {p.fund_b} ({p.overlap_percentage}% overlap)" for p in quant.overlap_matrix.high_overlap_pairs]
            alerts.append(
                KeyAlert(
                    severity="LOW",
                    title="Redundant Stock Holdings Overlap",
                    description=f"High portfolio duplication detected across: {'; '.join(overlap_descs)}. Multiple funds hold identical top constituents.",
                    affected_schemes=[p.fund_a for p in quant.overlap_matrix.high_overlap_pairs] + [p.fund_b for p in quant.overlap_matrix.high_overlap_pairs],
                )
            )

        # Fund Recommendations
        recommendations: List[FundRecommendation] = []
        form_map = {f.scheme_name: f for f in quant.form_ratings}

        for h in portfolio.holdings:
            f_diag = form_map.get(h.scheme_name)
            tier = f_diag.form_tier if f_diag else "On-Track"

            if h.plan_type == "REGULAR":
                if tier == "Out-of-Form":
                    action: FundAction = "EXIT_AND_REINVEST"
                    rat = f"Regular plan suffering from severe negative alpha and distributor fee drag. Exit and switch into a top-quartile Direct counterpart."
                    target = f"Direct Index / Top-Tier Direct {h.category} Fund"
                elif tier == "Off-Track":
                    action = "SWITCH_TO_DIRECT"
                    rat = f"Off-track performance exacerbated by 0.85% p.a. commission leakage. Switch to Direct plan to instantly boost net CAGR."
                    target = h.scheme_name.replace("Regular", "Direct")
                else:
                    action = "SWITCH_TO_DIRECT"
                    rat = f"Fund demonstrates solid form, but distributor commission is eroding net gains. Switch to Direct plan to save expense drag."
                    target = h.scheme_name.replace("Regular", "Direct")
            else:
                # Direct Plan
                if tier == "In-Form":
                    action = "CONTINUE_SIP"
                    rat = f"Top-quartile generator delivering consistent positive alpha over benchmark. Maintain or scale SIP allocations."
                    target = None
                elif tier == "On-Track":
                    action = "HOLD"
                    rat = f"Consistently tracking category benchmarks with zero intermediary commission drag. Maintain current position."
                    target = None
                elif tier == "Off-Track":
                    action = "PAUSE_SIP"
                    rat = f"Recent quarters demonstrate negative alpha. Pause fresh SIPs and monitor next two quarters before full reallocation."
                    target = f"Benchmark Direct {h.category} Index"
                else:
                    action = "EXIT_AND_REINVEST"
                    rat = f"Persistent multi-quarter underperformance against category benchmark. Reallocate corpus into higher conviction fund."
                    target = f"Top Quartile Direct {h.category} Fund"

            recommendations.append(
                FundRecommendation(
                    scheme_name=h.scheme_name,
                    action=action,
                    rationale=rat,
                    target_alternative=target,
                )
            )

        # Step-by-Step Checklist
        checklist: List[StepByStepChecklist] = []
        step_num = 1

        if quant.cost_drag.affected_schemes_count > 0:
            checklist.append(
                StepByStepChecklist(
                    step=step_num,
                    title="Convert Regular Plans to Direct Plans",
                    description=(
                        f"Initiate switch/redemption on {quant.cost_drag.affected_schemes_count} Regular fund(s) into Direct plans via AMC portals, CAMS/KFintech, or MF Central to capture ₹{quant.cost_drag.projected_10yr_cost_drag:,.2f} in projected 10-year compounding savings."
                    ),
                    priority="IMMEDIATE",
                )
            )
            step_num += 1

        if any(f.form_tier == "Out-of-Form" for f in quant.form_ratings):
            out_funds = [f.scheme_name for f in quant.form_ratings if f.form_tier == "Out-of-Form"]
            checklist.append(
                StepByStepChecklist(
                    step=step_num,
                    title="Prune Out-of-Form Underperformers",
                    description=f"Redeem capital from persistent laggards ({', '.join(out_funds[:2])}) and reinvest into broad-market Direct index or top-tier flexi cap funds.",
                    priority="IMMEDIATE",
                )
            )
            step_num += 1

        if quant.asset_drift.drift_status in ["High Risk Drift", "Over-Allocated to Equity"]:
            checklist.append(
                StepByStepChecklist(
                    step=step_num,
                    title=f"Rebalance Equity to Target {risk_profile} Band",
                    description=(
                        f"Reallocate excess equity profits into high-quality Short Duration / Banking & PSU Debt or Arbitrage funds to bring total equity exposure down to your target mid-point of {quant.asset_drift.target_equity_mid}%."
                    ),
                    priority="SHORT_TERM",
                )
            )
            step_num += 1

        if len(quant.overlap_matrix.high_overlap_pairs) > 0:
            checklist.append(
                StepByStepChecklist(
                    step=step_num,
                    title="Consolidate Overlapping Equity Funds",
                    description="Eliminate redundant schemes with >30% common stock overlap to reduce portfolio clutter and streamline management.",
                    priority="SHORT_TERM",
                )
            )
            step_num += 1

        checklist.append(
            StepByStepChecklist(
                step=step_num,
                title="Automate Bi-Annual Portfolio Audits",
                description="Establish a bi-annual review cadence to ensure new SIP installments continue tracking target risk thresholds and zero commission leakage.",
                priority="LONG_TERM",
            )
        )

        return AIAnalysisReport(
            health_score=health_score,
            risk_alignment_verdict=verdict,
            key_alerts=alerts,
            fund_recommendations=recommendations,
            step_by_step_rebalance_checklist=checklist,
        )

    async def generate_insights(self, portfolio: Portfolio, quant: QuantDiagnostics, risk_profile: RiskProfile = "Moderate") -> AIAnalysisReport:
        """
        Synthesizes quant metrics into an AIAnalysisReport using Google GenAI SDK (Gemini)
        with strict Pydantic JSON schema enforcement, falling back to deterministic synthesis if offline.
        """
        if not self._client:
            logger.info("Operating in deterministic quant AI synthesis mode.")
            return self.generate_deterministic_insights(portfolio, quant, risk_profile)

        prompt = self._build_quant_context_prompt(portfolio, quant, risk_profile)

        for m in [self.model_name, "gemini-3.7-flash", "gemini-3.5-flash", "gemini-flash-latest"]:
            try:
                # Using google-genai Client with Pydantic response_schema
                response = self._client.models.generate_content(
                    model=m,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=AIAnalysisReport,
                        temperature=0.1,
                    ),
                )
                
                if response and response.text:
                    report = AIAnalysisReport.model_validate_json(response.text)
                    return report
            except Exception as e:
                logger.warning(f"Google GenAI API call with {m} encountered error: {e}. Trying fallback.")
                continue

        return self.generate_deterministic_insights(portfolio, quant, risk_profile)
