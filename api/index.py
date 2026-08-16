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
    Normalizes WSGI PATH_INFO so Flask router handles root '/', '/dashboard', and all APIs seamlessly on Vercel
    """
    def __init__(self, wsgi_app):
        self.wsgi_app = wsgi_app

    def __call__(self, environ, start_response):
        # 1. First check if Vercel passed the original request path header
        orig_path = (
            environ.get("HTTP_X_MATCHED_PATH")
            or environ.get("HTTP_X_FORWARDED_PATH")
            or environ.get("HTTP_X_FORWARDED_URI")
            or environ.get("RAW_URI")
            or environ.get("REQUEST_URI")
        )
        
        path = environ.get("PATH_INFO", "/")
        
        if orig_path and not (orig_path.startswith("/api/index") or orig_path == "/api"):
            path = orig_path.split("?")[0]
        else:
            # 2. Strip serverless dispatcher rewrite prefixes
            if path.startswith("/api/index.py"):
                path = path[len("/api/index.py"):] or "/"
            elif path.startswith("/api/index"):
                path = path[len("/api/index"):] or "/"
            elif path == "" or path == "/api":
                path = "/"
                
        if not path.startswith("/"):
            path = "/" + path

        environ["PATH_INFO"] = path
        return self.wsgi_app(environ, start_response)

app.wsgi_app = VercelPathMiddleware(app.wsgi_app)


