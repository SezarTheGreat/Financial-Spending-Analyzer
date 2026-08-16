"""
Vercel Serverless Entrypoint for FinWise AI Platform
"""
import os
import sys

# Ensure root directory is on Python path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app import app

class VercelPathMiddleware:
    """
    Normalizes WSGI PATH_INFO so Flask router handles root '/' and all subpaths seamlessly on Vercel
    """
    def __init__(self, wsgi_app):
        self.wsgi_app = wsgi_app

    def __call__(self, environ, start_response):
        raw_uri = environ.get("HTTP_X_FORWARDED_URI") or environ.get("RAW_URI") or environ.get("REQUEST_URI") or ""
        if raw_uri:
            path = raw_uri.split("?")[0]
            environ["PATH_INFO"] = path
        elif environ.get("PATH_INFO") in ["/api/index.py", "/api/index", "/api", ""]:
            environ["PATH_INFO"] = "/"
        return self.wsgi_app(environ, start_response)

app.wsgi_app = VercelPathMiddleware(app.wsgi_app)


