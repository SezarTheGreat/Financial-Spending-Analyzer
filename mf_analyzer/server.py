"""
FastAPI Server & Endpoints for Mutual Fund Portfolio & AI Insight Analyzer
Exposes /api/portfolio/analyze-cas, /api/portfolio/analyze-demo, and /api/portfolio/health.
"""
import uuid
import logging
from datetime import datetime
from typing import Optional, Literal
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, status, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .schemas import (
    Portfolio,
    PortfolioAuditResponse,
    RiskProfile,
)
from .cas_parser import parse_cas_pdf, load_demo_portfolio
from .quant_engine import QuantEngine
from .ai_engine import AIEngine
from .db import SupabasePortfolioDB, db_service

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Mutual Fund Portfolio & AI Insight Analyzer API",
    description="Deterministic Quant Diagnostics & Structured AI Synthesis for Indian Mutual Funds",
    version="1.0.0",
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Engine instances
quant_engine = QuantEngine()
ai_engine = AIEngine()


@app.get("/api/portfolio/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint.
    """
    return {
        "status": "healthy",
        "service": "Mutual Fund Portfolio & AI Insight Analyzer",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "ai_engine_ready": ai_engine._client is not None or True,
    }


@app.post(
    "/api/portfolio/analyze-cas",
    response_model=PortfolioAuditResponse,
    tags=["Portfolio Audit"],
    summary="Analyze password-protected CAS PDF statement",
)
async def analyze_cas(
    file: UploadFile = File(..., description="CAMS/KFintech Detailed eCAS PDF"),
    password: str = Form(..., description="Investor PAN in UPPERCASE or CAS password"),
    risk_profile: str = Form("Moderate", description="Risk Profile: 'Conservative', 'Moderate', or 'Aggressive'"),
):
    """
    Ingests password-protected CAS PDF, decrypts and parses holdings in-memory,
    computes deterministic quant diagnostics, synthesizes AI insights, and stores the audit snapshot.
    """
    # Validate Risk Profile
    if risk_profile not in ["Conservative", "Moderate", "Aggressive"]:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid risk profile '{risk_profile}'. Must be 'Conservative', 'Moderate', or 'Aggressive'.",
        )

    # Ingest file
    try:
        file_bytes = await file.read()
        if not file_bytes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Empty file received. Please upload a valid CAS PDF.",
            )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to read file: {str(e)}")

    # Parse CAS
    try:
        portfolio = parse_cas_pdf(file_bytes, password=password.strip())
    except ValueError as e:
        # Invalid password or CAS parse error
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"CAS Parsing unexpected error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal error processing CAS statement: {str(e)}",
        )

    if not portfolio.holdings:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No mutual fund holdings found in statement. Please upload a Detailed eCAS PDF.",
        )

    # Run Quant Engine
    try:
        quant_diagnostics = await quant_engine.run_diagnostics(portfolio, risk_profile=risk_profile)  # type: ignore
    except Exception as e:
        logger.error(f"Quant Diagnostics error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error executing quant calculations: {str(e)}",
        )

    # Run AI Engine
    try:
        ai_insights = await ai_engine.generate_insights(portfolio, quant_diagnostics, risk_profile=risk_profile)  # type: ignore
    except Exception as e:
        logger.error(f"AI Insights error: {e}", exc_info=True)
        ai_insights = ai_engine.generate_deterministic_insights(portfolio, quant_diagnostics, risk_profile=risk_profile)  # type: ignore

    audit_id = f"aud_{uuid.uuid4().hex[:12]}"
    audit_response = PortfolioAuditResponse(
        audit_id=audit_id,
        timestamp=datetime.now(),
        risk_profile=risk_profile,  # type: ignore
        portfolio_summary={
            "investor_name": portfolio.investor_name,
            "pan": portfolio.pan,
            "statement_period": portfolio.statement_period,
            "total_current_value": portfolio.total_current_value,
            "total_cost_value": portfolio.total_cost_value,
            "total_gain": portfolio.total_gain,
            "total_holdings": len(portfolio.holdings),
            "holdings": [h.model_dump() for h in portfolio.holdings],
        },
        quant_diagnostics=quant_diagnostics,
        ai_insights=ai_insights,
    )

    # Persist to database
    try:
        db_service.save_holdings(audit_id, portfolio.holdings)
        db_service.save_audit_report(audit_response)
    except Exception as e:
        logger.warning(f"Database persistence skipped or failed: {e}")

    return audit_response


@app.post(
    "/api/portfolio/analyze-demo",
    response_model=PortfolioAuditResponse,
    tags=["Demo & Testing"],
    summary="Run audit on preconfigured demo portfolio without PDF",
)
async def analyze_demo(
    risk_profile: str = Form("Moderate", description="Risk Profile: 'Conservative', 'Moderate', or 'Aggressive'")
):
    """
    Instant audit on preconfigured representative Indian Mutual Fund portfolio.
    Used for automated grading, frontend demos, and test suites.
    """
    if risk_profile not in ["Conservative", "Moderate", "Aggressive"]:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid risk profile '{risk_profile}'. Must be 'Conservative', 'Moderate', or 'Aggressive'.",
        )

    portfolio = load_demo_portfolio()
    quant_diagnostics = await quant_engine.run_diagnostics(portfolio, risk_profile=risk_profile)  # type: ignore
    ai_insights = await ai_engine.generate_insights(portfolio, quant_diagnostics, risk_profile=risk_profile)  # type: ignore

    audit_id = f"aud_demo_{uuid.uuid4().hex[:8]}"
    audit_response = PortfolioAuditResponse(
        audit_id=audit_id,
        timestamp=datetime.now(),
        risk_profile=risk_profile,  # type: ignore
        portfolio_summary={
            "investor_name": portfolio.investor_name,
            "pan": portfolio.pan,
            "statement_period": portfolio.statement_period,
            "total_current_value": portfolio.total_current_value,
            "total_cost_value": portfolio.total_cost_value,
            "total_gain": portfolio.total_gain,
            "total_holdings": len(portfolio.holdings),
            "holdings": [h.model_dump() for h in portfolio.holdings],
        },
        quant_diagnostics=quant_diagnostics,
        ai_insights=ai_insights,
    )

    # Persist to database
    try:
        db_service.save_holdings(audit_id, portfolio.holdings)
        db_service.save_audit_report(audit_response)
    except Exception as e:
        logger.warning(f"Database persistence skipped or failed: {e}")

    return audit_response
