"""
Tri-Hybrid RAG Router
Decides whether to hit Supabase (Tier 1), LanceDB (Tier 2), or JIT PyMuPDF4LLM (Tier 3).
"""
from typing import Dict, Any
from db.supabase_client import db as supabase_db
from db.lancedb_r2 import semantic_search
from ingestion.offline_indexer import mock_embedding
from ingestion.parse_memory import stream_and_parse_pdf
from core.gemini_client import generate_rag_response

async def route_and_resolve_query(query: str) -> str:
    """
    Very basic heuristic router for ponytail implementation.
    In a full implementation, we would use Gemini Function Calling here.
    """
    query_lower = query.lower()
    
    context = ""
    
    # Tier 1: Exact statutory rules
    if "exit load" in query_lower or "mandate" in query_lower:
        # Example Supabase fetch (mocking condition for brevity)
        try:
            res = supabase_db.table("exit_load_schedules").select("*").limit(3).execute()
            context += f"Supabase Tier 1 Context:\n{res.data}\n"
        except Exception:
            context += "Supabase Tier 1 Context: Database connection error.\n"
            
    # Tier 2: Narrative / Factsheet search
    elif "strategy" in query_lower or "philosophy" in query_lower:
        # LanceDB hybrid search
        vec = mock_embedding(query)
        results = semantic_search("factsheet_chunks", vec)
        context += f"LanceDB Tier 2 Context:\n{results}\n"
        
    # Tier 3: JIT Document streaming
    elif "latest sid" in query_lower or "pdf" in query_lower:
        # Example dummy PDF URL
        pdf_url = "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf"
        md_text = await stream_and_parse_pdf(pdf_url)
        context += f"JIT Streamer Tier 3 Context:\n{md_text[:1000]}...\n"
        
    else:
        context = "No specific RAG tier matched. Fallback to general knowledge."
        
    # Final resolution
    return generate_rag_response(query, context)
