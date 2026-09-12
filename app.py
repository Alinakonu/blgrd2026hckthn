"""Vercel Python entrypoint — serves the static AgriSense deck.

The interactive UI is Streamlit: ``streamlit run streamlit_app.py``.
Vercel auto-detects a root ``app.py`` and requires a top-level ``app``,
``application``, or ``handler``. This WSGI callable satisfies that check
and returns the field app (not the slide deck).
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent
INDEX_CANDIDATES = (
    ROOT / "public" / "index.html",
    ROOT / "AgriSense-demo.html",
)


def _index_bytes() -> bytes:
    for path in INDEX_CANDIDATES:
        if path.is_file():
            return path.read_bytes()
    return (
        b"<!DOCTYPE html><html><body><p>AgriSense app missing. "
        b"Run <code>streamlit run streamlit_app.py</code>.</p></body></html>"
    )


def app(environ, start_response):
    """WSGI application (Vercel looks for this name)."""
    body = _index_bytes()
    start_response(
        "200 OK",
        [
            ("Content-Type", "text/html; charset=utf-8"),
            ("Content-Length", str(len(body))),
        ],
    )
    return [body]


application = app
handler = app
