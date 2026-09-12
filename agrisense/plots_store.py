"""
Tiny plot locker used by the Streamlit sidebar.

- If CONVEX_SITE_URL is set → POST/GET https://<deployment>.convex.site/plots
- Else → local JSON file (demo still works offline / without Convex login)

Setup: see docs/CONVEX_PLOTS.md (~30 minutes).
"""

from __future__ import annotations

import json
import os
import time
import uuid
from pathlib import Path
from typing import Any

import requests

ROOT = Path(__file__).resolve().parents[1]
LOCAL_PATH = ROOT / "data" / "saved_plots.local.json"


def convex_site_url() -> str | None:
    url = (os.environ.get("CONVEX_SITE_URL") or "").strip().rstrip("/")
    return url or None


def backend_label() -> str:
    return "convex" if convex_site_url() else "local"


def _headers() -> dict[str, str]:
    headers = {"Content-Type": "application/json"}
    token = (os.environ.get("PLOTS_HTTP_TOKEN") or "").strip()
    if token:
        headers["x-plots-token"] = token
    return headers


def _load_local() -> list[dict[str, Any]]:
    if not LOCAL_PATH.exists():
        return []
    try:
        data = json.loads(LOCAL_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []
    return data if isinstance(data, list) else []


def _save_local(rows: list[dict[str, Any]]) -> None:
    LOCAL_PATH.parent.mkdir(parents=True, exist_ok=True)
    LOCAL_PATH.write_text(json.dumps(rows, indent=2), encoding="utf-8")


def save_plot(payload: dict[str, Any]) -> dict[str, Any]:
    """Persist one farmer plot. Returns the saved row (best-effort)."""
    site = convex_site_url()
    if site:
        resp = requests.post(
            f"{site}/plots",
            headers=_headers(),
            json=payload,
            timeout=20,
        )
        resp.raise_for_status()
        data = resp.json()
        return {"backend": "convex", **payload, "id": data.get("id")}

    rows = _load_local()
    row = {
        "_id": str(uuid.uuid4()),
        **payload,
        "savedAt": int(time.time() * 1000),
        "backend": "local",
    }
    rows.insert(0, row)
    _save_local(rows[:50])
    return row


def list_plots() -> list[dict[str, Any]]:
    site = convex_site_url()
    if site:
        resp = requests.get(f"{site}/plots", headers=_headers(), timeout=20)
        resp.raise_for_status()
        data = resp.json()
        plots = data.get("plots") if isinstance(data, dict) else data
        return list(plots or [])

    return _load_local()
