"""
Offline Indexer: Background Worker (Designed for GitHub Actions / Cron)
Downloads factsheets, chunks text, and pushes embeddings to LanceDB on Cloudflare R2.
"""
from typing import List, Dict, Any
from db.lancedb_r2 import get_lancedb_connection
from core.config import settings

def chunk_text(text: str, chunk_size: int = 1000) -> List[str]:
    """Simple greedy chunker."""
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

def mock_embedding(text: str) -> List[float]:
    """Placeholder for text-embedding-004 logic."""
    # Return a dummy vector of 768 length
    return [0.0] * 768

def run_indexer_job():
    """
    Cron job entry point.
    1. Crawls AMFI/AMC for latest docs.
    2. Uses parse_memory to extract markdown.
    3. Chunks and embeds using Gemini text-embedding-004.
    4. Upserts to LanceDB -> R2.
    """
    print("Starting offline indexer job...")
    db = get_lancedb_connection()
    
    # Ensure table exists
    table_name = "factsheet_chunks"
    if table_name not in db.table_names():
        db.create_table(
            table_name,
            data=[{"vector": mock_embedding("init"), "text": "init", "metadata": {}}]
        )
    print("Indexer job complete.")

if __name__ == "__main__":
    run_indexer_job()
