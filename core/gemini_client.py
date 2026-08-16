from google import genai
from google.genai import types
from core.config import settings

def get_gemini_client() -> genai.Client:
    """Instantiate the Gemini client."""
    return genai.Client(api_key=settings.GEMINI_API_KEY)

def generate_rag_response(query: str, retrieved_context: str) -> str:
    """
    Given a user query and the combined hybrid RAG context, 
    generates a strict, zero-hallucination response.
    """
    client = get_gemini_client()
    
    system_instruction = (
        "You are FinWise AI, an institutional Indian Mutual Fund research engine.\n"
        "Rely strictly on the provided RAG context.\n"
        "Never invent NAVs, exit loads, or rules."
    )
    
    full_prompt = f"Context:\n{retrieved_context}\n\nUser Query: {query}"
    
    # Model generation with fallback
    for model_name in ["gemini-3.7-flash", "gemini-3.5-flash", "gemini-flash-latest"]:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=[types.Content(role="user", parts=[types.Part.from_text(text=full_prompt)])],
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.0
                )
            )
            return response.text or "Unable to generate response."
        except Exception:
            continue
    return "Unable to generate response from AI models."
