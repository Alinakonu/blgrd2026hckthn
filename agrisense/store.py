"""Data access with a Convex backend and a local-file fallback.

Convex holds the field records and the advisory history. Every function here
degrades to the committed data/pins.json when Convex is unset, unreachable, or
the client library is missing, because the demo must survive a dead network.

Nothing in this module raises on a Convex failure. Read paths fall back, write
paths are best-effort and report success as a boolean.
"""

from __future__ import annotations

import json
import os
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
PINS_PATH = ROOT / "data" / "pins.json"

_client = None
_client_error: str | None = None
_env_loaded = False


def _load_env_files() -> None:
    """Read CONVEX_URL out of .env.local, the file `npx convex dev` writes.

    Streamlit is started by hand rather than through the Convex CLI, so nothing
    else puts these values in the environment. Real environment variables win,
    which keeps deployment overrides working.
    """
    global _env_loaded
    if _env_loaded:
        return
    _env_loaded = True

    for name in (".env.local", ".env"):
        path = ROOT / name
        if not path.exists():
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            os.environ.setdefault(key.strip(), value.strip().strip("'\""))


def convex_url() -> str | None:
    _load_env_files()
    return os.environ.get("CONVEX_URL") or os.environ.get("NEXT_PUBLIC_CONVEX_URL")


def _defined(fields: dict) -> dict:
    """Drop None values.

    Convex reads a missing key as `undefined`, which `v.optional` accepts, but
    an explicit None arrives as `null` and fails validation.
    """
    return {k: v for k, v in fields.items() if v is not None}


def client():
    """Lazily build a ConvexClient, or None if unavailable.

    Cached including the failure case so a missing package or an unreachable
    deployment costs one attempt rather than one per Streamlit rerun.
    """
    global _client, _client_error
    if _client is not None or _client_error is not None:
        return _client

    url = convex_url()
    if not url:
        _client_error = "CONVEX_URL not set"
        return None

    try:
        from convex import ConvexClient

        _client = ConvexClient(url)
    except ImportError:
        _client_error = "convex package not installed (pip install convex)"
    except Exception as exc:  # noqa: BLE001 - any client failure means fall back
        _client_error = str(exc)
    return _client


def status() -> dict:
    """Human-readable backend state for the UI footer."""
    active = client()
    return {
        "connected": active is not None,
        "url": convex_url(),
        "detail": _client_error or "connected",
    }


def load_local_pins() -> list[dict]:
    return json.loads(PINS_PATH.read_text(encoding="utf-8"))


def load_pins() -> tuple[list[dict], str]:
    """Field records plus the source they came from ("convex" or "local")."""
    active = client()
    if active is not None:
        try:
            records = active.query("pins:list", {})
            if records:
                return records, "convex"
        except Exception:  # noqa: BLE001 - fall back rather than break the app
            pass
    return load_local_pins(), "local"


def push_pins(records: list[dict]) -> int:
    """Upload field records to Convex. Returns how many were written."""
    active = client()
    if active is None:
        raise RuntimeError(f"Convex unavailable: {_client_error}")

    written = 0
    for record in records:
        location = record["location"]
        active.mutation(
            "pins:upsert",
            _defined(
                {
                    "name": location["name"],
                    "region": location.get("region"),
                    "lat": location["lat"],
                    "lon": location["lon"],
                    "record": record,
                }
            ),
        )
        written += 1
    return written


def log_advisory(record: dict, assessment: dict, mode: str, text: str) -> bool:
    """Store a generated action plan. Best effort — never breaks plan display."""
    active = client()
    if active is None:
        return False

    try:
        active.mutation(
            "advisories:add",
            _defined(
                {
                    "location": record["location"]["name"],
                    "mode": mode,
                    "verdict": assessment.get("verdict"),
                    # None where no crop is deteriorating — a real result, not
                    # missing data, so it is simply omitted.
                    "mostExposed": assessment.get("most_exposed"),
                    "signals": record.get("signals", []),
                    "summerBalanceMm": record["recent"].get(
                        "summer_water_balance_mm"
                    ),
                    "text": text,
                }
            ),
        )
        return True
    except Exception:  # noqa: BLE001
        return False


def recent_advisories(limit: int = 8) -> list[dict]:
    """Latest plans across all fields. Empty list when Convex is unavailable."""
    active = client()
    if active is None:
        return []
    try:
        return active.query("advisories:recent", {"limit": limit})
    except Exception:  # noqa: BLE001
        return []
