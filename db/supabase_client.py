from supabase import create_client, Client
from core.config import settings

def get_supabase_client() -> Client:
    """
    Creates and returns a Supabase client using the service role key 
    for backend administrative operations (bypassing RLS when necessary)
    or use anon key based on use-case.
    """
    url: str = settings.SUPABASE_URL
    key: str = settings.SUPABASE_SERVICE_ROLE_KEY
    return create_client(url, key)

db = get_supabase_client()
