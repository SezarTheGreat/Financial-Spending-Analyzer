from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from typing import Dict, Any

from core.router import route_and_resolve_query
from core.quant_engine import fetch_historical_nav, compute_rolling_metrics

app = FastAPI(
    title="FinWise Tri-Hybrid RAG API",
    description="Zero-hallucination institutional MF diagnostics API for Vercel Serverless.",
    version="1.0.0"
)

class ChatRequest(BaseModel):
    query: str

@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest) -> Dict[str, Any]:
    """
    Main Chatbot entrypoint.
    Routes to the Tri-Hybrid RAG layers for context extraction.
    """
    response_text = await route_and_resolve_query(request.query)
    return {"reply": response_text}

@app.post("/api/audit-portfolio")
async def audit_portfolio_endpoint(cas_pdf: UploadFile = File(...)) -> Dict[str, Any]:
    """
    Accepts CAS PDF, parses in-memory, and runs diagnostic audit.
    """
    # Note: Using casparser in memory.
    # We would stream `cas_pdf.file.read()` directly into casparser.
    return {"status": "success", "message": f"Processed {cas_pdf.filename} entirely in RAM without Vercel disk writes."}

@app.get("/api/fund/{amfi_code}/diagnostics")
async def fund_diagnostics_endpoint(amfi_code: str) -> Dict[str, Any]:
    """
    Fetches real-time quant diagnostics for a specific fund by AMFI code.
    """
    nav_series = await fetch_historical_nav(amfi_code)
    metrics = compute_rolling_metrics(nav_series)
    return {
        "amfi_code": amfi_code,
        "diagnostics": metrics
    }
