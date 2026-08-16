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
        
        if path.startswith("/api/index.py/"):
            path = path[len("/api/index.py"):]
        elif path == "/api/index.py":
            path = "/"
        elif path.startswith("/api/index/"):
            path = path[len("/api/index"):]
        elif path == "/api/index":
            path = "/"

        if not path or path == "":
            path = "/"
        if not path.startswith("/"):
            path = "/" + path

        environ["PATH_INFO"] = path
        return self.wsgi_app(environ, start_response)

app.wsgi_app = VercelPathMiddleware(app.wsgi_app)


