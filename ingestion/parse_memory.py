import io
import httpx
import pymupdf4llm
from typing import Optional

async def stream_and_parse_pdf(pdf_url: str) -> Optional[str]:
    """
    JIT Document Streamer:
    Downloads a PDF into memory and extracts Markdown (tables + text) 
    using PyMuPDF4LLM without hitting the ephemeral Vercel disk.
    """
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(pdf_url, follow_redirects=True)
            response.raise_for_status()
        except Exception as e:
            print(f"Failed to fetch PDF: {e}")
            return None
            
    # Load raw bytes directly into memory buffer
    pdf_bytes = io.BytesIO(response.content)
    
    try:
        # Convert PDF bytes to markdown
        md_text = pymupdf4llm.to_markdown(pdf_bytes)
        return md_text
    except Exception as e:
        print(f"Failed to parse PDF: {e}")
        return None
