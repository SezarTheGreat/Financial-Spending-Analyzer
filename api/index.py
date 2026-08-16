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
        path = environ.get("PATH_INFO", "/")
        
        orig_uri = (
            environ.get("HTTP_X_FORWARDED_URI")
            or environ.get("HTTP_X_ORIGINAL_URI")
            or environ.get("HTTP_X_VERCEL_SC_PATH")
            or environ.get("HTTP_X_VERCEL_PROXY_PATH")
            or environ.get("RAW_URI")
            or environ.get("REQUEST_URI")
        )
        
        if orig_uri and not (orig_uri.startswith("/api/index") or orig_uri == "/api"):
            path = orig_uri.split("?")[0]
        elif "HTTP_X_NOW_ROUTE_MATCHES" in environ:
            import urllib.parse
            matches = urllib.parse.parse_qs(environ["HTTP_X_NOW_ROUTE_MATCHES"])
            if "1" in matches and matches["1"]:
                matched_sub = matches["1"][0]
                path = "/" + matched_sub.lstrip("/")
            elif path.startswith("/api/index.py") or path.startswith("/api/index"):
                path = "/"
        else:
            for prefix in ["/api/index.py", "/api/index", "/index.py"]:
                if path.startswith(prefix):
                    path = path[len(prefix):] or "/"
                    break

        if not path or path == "":
            path = "/"
        if not path.startswith("/"):
            path = "/" + path

        environ["PATH_INFO"] = path
        return self.wsgi_app(environ, start_response)

app.wsgi_app = VercelPathMiddleware(app.wsgi_app)


