"""Vercel serverless entry point: exposes the FastAPI ASGI app.

vercel.json rewrites /api/*, /health and /ready here; the original path is preserved, so the
app's own routing applies unchanged. The built web app is served by Vercel's CDN, not by this function.
"""

from app.main import app

__all__ = ["app"]
