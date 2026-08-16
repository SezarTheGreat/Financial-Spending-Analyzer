import lancedb
from core.config import settings
from typing import Optional, List, Dict, Any

def get_lancedb_connection() -> lancedb.DBConnection:
    """
    Connects to LanceDB embedded vector storage backed by Cloudflare R2 (S3-compatible).
    Provides zero-infrastructure vector search.
    """
    storage_options = {
        "aws_access_key_id": settings.R2_ACCESS_KEY_ID,
        "aws_secret_access_key": settings.R2_SECRET_ACCESS_KEY,
        "endpoint_url": settings.R2_ENDPOINT,
        "region_name": "auto",
    }
    uri = f"s3://{settings.R2_BUCKET_NAME}/vectors"
    return lancedb.connect(uri, storage_options=storage_options)

def semantic_search(table_name: str, query_vector: List[float], limit: int = 5) -> List[Dict[str, Any]]:
    """
    Perform a vector similarity search on a specific LanceDB table.
    """
    db = get_lancedb_connection()
    try:
        table = db.open_table(table_name)
        results = table.search(query_vector).limit(limit).to_list()
        return results
    except Exception as e:
        # Table might not exist yet or connection error
        print(f"LanceDB search error: {e}")
        return []
