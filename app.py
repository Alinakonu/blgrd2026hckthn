"""
AgriSense — Path A Streamlit UI (Track B)

Offline-first: reads data/pins.json. Optional live Grok advice when
XAI_API_KEY / GROK_API_KEY is set; otherwise a deterministic plan from the
crop assessment so the demo still works with the network off.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import pandas as pd
import requests
import streamlit as st

from agrisense import crops as crop_model
from agrisense import store
from agrisense.prompt import SIGNAL_TEXT, build_messages, build_user_prompt

ROOT = Path(__file__).resolve().parent
PINS_PATH = ROOT / "data" / "pins.json"

# Pitch order from PLAN.md: masking story → worst case → counter-example
DEMO_ORDER = [
    "Novi Sad",
    "Zrenjanin",
    "Subotica",
    "Belgrade",
    "Kraljevo",
    "Nis",
]

st.set_page_config(
    page_title="AgriSense — Serbia climate field check",
    page_icon="🌾",
    layout="wide",
)

# Visual theme only — mirrors the SoilShift field-day look, dialed a bit cozier.
# Does not change data, charts, or control flow.
FIELD_DAY_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Figtree:wght@400;500;600;700&family=Fraunces:opsz,wght@9..144,500;9..144,600;9..144,700&display=swap');

:root {
  --bg: #e6ede7;
  --panel: #f4f7f4;
  --panel-strong: #fffcf8;
  --ink: #1b2d24;
  --ink-soft: #3e5349;
  --muted: #6a7c72;
  --accent: #2f5f46;
  --accent-ink: #f3faf5;
  --accent-soft: #c8dccf;
  --accent-glow: rgba(47, 95, 70, 0.18);
  --rule: rgba(27, 45, 36, 0.11);
  --rule-strong: rgba(27, 45, 36, 0.2);
  --warn: #a56b28;
  --danger: #a84840;
  --warm-mist: rgba(255, 250, 242, 0.55);
}

html, body, [data-testid="stAppViewContainer"],
[data-testid="stAppViewContainer"] > .main,
.stApp {
  background: transparent !important;
  color: var(--ink) !important;
  font-family: "Figtree", "Segoe UI", sans-serif !important;
}

/* Soft morning field wash — linen mist, no neon */
[data-testid="stAppViewContainer"]::before {
  content: "";
  position: fixed;
  inset: 0;
  z-index: -2;
  pointer-events: none;
  background:
    radial-gradient(1000px 560px at 8% 0%, rgba(180, 210, 190, 0.92), transparent 58%),
    radial-gradient(820px 480px at 92% 8%, rgba(232, 220, 200, 0.45), transparent 55%),
    radial-gradient(900px 520px at 50% 100%, rgba(168, 196, 176, 0.5), transparent 60%),
    linear-gradient(180deg, #eef3ef 0%, #e6ede7 45%, #dce6de 100%);
}

[data-testid="stAppViewContainer"]::after {
  content: "";
  position: fixed;
  inset: 0;
  z-index: -1;
  pointer-events: none;
  opacity: 0.22;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.45'/%3E%3C/svg%3E");
  mix-blend-mode: multiply;
}

[data-testid="stHeader"] {
  background: rgba(242, 246, 243, 0.72) !important;
  backdrop-filter: blur(10px);
  border-bottom: 1px solid var(--rule);
}

[data-testid="stSidebar"] {
  background: linear-gradient(
    180deg,
    rgba(244, 247, 244, 0.96) 0%,
    rgba(255, 252, 248, 0.9) 100%
  ) !important;
  border-right: 1px solid var(--rule);
}

[data-testid="stSidebar"] > div:first-child {
  background: transparent !important;
}

[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
  font-family: "Fraunces", Georgia, serif !important;
  color: var(--ink) !important;
  letter-spacing: -0.02em;
}

.main .block-container {
  padding-top: 1.75rem;
  padding-bottom: 3rem;
  max-width: 1180px;
}

h1, h2, h3, h4, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4 {
  font-family: "Fraunces", Georgia, serif !important;
  color: var(--ink) !important;
  letter-spacing: -0.03em;
  font-weight: 600 !important;
}

h1 {
  font-size: clamp(2.4rem, 5vw, 3.4rem) !important;
  line-height: 0.95 !important;
  margin-bottom: 0.35rem !important;
}

.stCaption, [data-testid="stCaption"], small {
  color: var(--muted) !important;
  font-family: "Figtree", sans-serif !important;
}

p, li, label, .stMarkdown, .stText {
  color: var(--ink-soft) !important;
  line-height: 1.55;
}

/* Soft field cards around metric blocks */
div[data-testid="stMetric"] {
  background: linear-gradient(
    165deg,
    rgba(255, 252, 248, 0.92) 0%,
    rgba(255, 255, 255, 0.72) 100%
  );
  border: 1px solid var(--rule);
  border-radius: 20px;
  padding: 1rem 1.05rem 0.85rem;
  box-shadow:
    0 1px 0 rgba(255, 255, 255, 0.8) inset,
    0 12px 30px rgba(27, 45, 36, 0.07);
}

div[data-testid="stMetric"] label {
  color: var(--muted) !important;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  font-size: 0.7rem !important;
}

div[data-testid="stMetric"] [data-testid="stMetricValue"] {
  font-family: "Fraunces", Georgia, serif !important;
  color: var(--ink) !important;
  font-weight: 600;
}

div[data-testid="stMetric"] [data-testid="stMetricDelta"] svg {
  display: none;
}

/* Charts / map / tables sit on soft panels */
[data-testid="stVerticalBlockBorderWrapper"],
div[data-testid="stDataFrame"],
div[data-testid="stDeckGlJsonChart"],
div[data-testid="stArrowVegaLiteChart"],
iframe[title="streamlit_keplergl.st_keplergl"] {
  border-radius: 18px !important;
}

[data-testid="stVegaLiteChart"],
[data-testid="stArrowVegaLiteChart"],
div[data-testid="stPlotlyChart"],
div[data-testid="stMap"] {
  background: linear-gradient(
    180deg,
    rgba(255, 252, 248, 0.88) 0%,
    rgba(255, 255, 255, 0.7) 100%
  );
  border: 1px solid var(--rule);
  border-radius: 20px;
  padding: 0.75rem;
  box-shadow:
    0 1px 0 rgba(255, 255, 255, 0.75) inset,
    0 12px 32px rgba(27, 45, 36, 0.06);
}

div[data-testid="stDataFrame"] {
  background: linear-gradient(
    180deg,
    rgba(255, 252, 248, 0.9) 0%,
    rgba(255, 255, 255, 0.78) 100%
  );
  border: 1px solid var(--rule);
  border-radius: 20px;
  padding: 0.45rem;
  box-shadow:
    0 1px 0 rgba(255, 255, 255, 0.75) inset,
    0 12px 32px rgba(27, 45, 36, 0.05);
}

/* Alerts — soft, not loud */
div[data-testid="stAlert"] {
  border-radius: 16px !important;
  border: 1px solid var(--rule) !important;
  box-shadow: 0 8px 22px rgba(27, 45, 36, 0.05);
  background: var(--warm-mist) !important;
}

/* Buttons */
.stButton > button {
  background: var(--accent) !important;
  color: var(--accent-ink) !important;
  border: none !important;
  border-radius: 999px !important;
  font-family: "Figtree", sans-serif !important;
  font-weight: 600 !important;
  letter-spacing: -0.01em;
  padding: 0.55rem 1.25rem !important;
  box-shadow: 0 8px 20px var(--accent-glow);
  transition: transform 0.18s ease, background 0.18s ease;
}

.stButton > button:hover {
  background: #264d39 !important;
  transform: translateY(-1px);
}

.stButton > button[kind="secondary"] {
  background: rgba(255, 255, 255, 0.7) !important;
  color: var(--ink) !important;
  border: 1px solid var(--rule-strong) !important;
  box-shadow: none !important;
}

/* Inputs / selects */
.stSelectbox div[data-baseweb="select"] > div,
.stTextInput input,
.stNumberInput input {
  background: rgba(255, 255, 255, 0.78) !important;
  border-radius: 12px !important;
  border-color: var(--rule-strong) !important;
  color: var(--ink) !important;
}

/* Toggles & dividers */
hr {
  border-color: var(--rule) !important;
}

[data-testid="stExpander"] {
  background: rgba(255, 255, 255, 0.55);
  border: 1px solid var(--rule);
  border-radius: 16px;
}

/* Code blocks in debug expander */
.stCode {
  border-radius: 14px !important;
}

/* Soften default link color */
a { color: var(--accent) !important; }

/* Sidebar pitch list breathing room */
[data-testid="stSidebar"] .stMarkdown p {
  line-height: 1.65;
}
</style>
"""


def apply_field_day_theme() -> None:
    """Inject SoilShift-inspired cozy field-day CSS. Presentation only."""
    st.markdown(FIELD_DAY_CSS, unsafe_allow_html=True)


@st.cache_data
def load_pins() -> tuple[list[dict], str]:
    """Field records from Convex, falling back to the committed JSON."""
    return store.load_pins()


def pin_by_name(pins: list[dict], name: str) -> dict:
    for pin in pins:
        if pin["location"]["name"] == name:
            return pin
    raise KeyError(name)


def delta(a: float, b: float) -> float:
    return round(b - a, 1)


def headline_for(record: dict, assessment: dict) -> str:
    signals = set(record.get("signals", []))
    if "annual_totals_masking_summer_stress" in signals:
        return (
            "Annual rainfall looks fine — the summer water deficit is getting worse. "
            "That is the problem."
        )
    if assessment["verdict"] == "action_needed":
        crop = assessment["most_exposed"] or "crops"
        label = crop_model.CROPS.get(crop, {}).get("label", crop)
        return f"Action indicated — {label} is the most exposed crop at this plot."
    return "No material crop-exposure change indicated at this plot."


def water_balance_frame(record: dict) -> pd.DataFrame:
    rows = []
    for label, period in (
        ("Baseline", record["baseline"]),
        ("Recent", record["recent"]),
    ):
        rows.append(
            {
                "period": f"{label} ({period['period']})",
                "Summer rain (mm)": period["summer_rain_mm"],
                "Crop water demand ET0 (mm)": period["summer_water_demand_mm"],
                "Summer balance (mm)": period["summer_water_balance_mm"],
            }
        )
    return pd.DataFrame(rows).set_index("period")


def heat_frame(record: dict) -> pd.DataFrame:
    rows = []
    for label, period in (
        ("Baseline", record["baseline"]),
        ("Recent", record["recent"]),
    ):
        rows.append(
            {
                "period": f"{label} ({period['period']})",
                "Days ≥30°C": period["hot_days_30"],
                "Days ≥35°C": period["hot_days_35"],
            }
        )
    return pd.DataFrame(rows).set_index("period")


def crop_table(assessment: dict) -> pd.DataFrame:
    rows = []
    for entry in assessment["crops"]:
        rows.append(
            {
                "Crop": entry["label"],
                "Exposure": entry["exposure_band"],
                "Score": entry["exposure_score"],
                "Gap baseline (mm)": entry["irrigation_gap_baseline_mm"],
                "Gap recent (mm)": entry["irrigation_gap_recent_mm"],
                "Widening (mm)": entry["gap_widening_mm"],
                "Summer overlap": entry["summer_overlap"],
                "FAO sensitivity": entry["drought_sensitivity"],
                "Vojvodina ha": entry["sown_ha_vojvodina"],
            }
        )
    return pd.DataFrame(rows)


def offline_action_plan(record: dict, assessment: dict) -> str:
    """Deterministic plan when no API key — still specific, still from measured numbers."""
    loc = record["location"]["name"]
    base, recent = record["baseline"], record["recent"]
    bal_d = delta(base["summer_water_balance_mm"], recent["summer_water_balance_mm"])
    rain_d = delta(base["precip_mm"], recent["precip_mm"])
    hot_d = delta(base["hot_days_30"], recent["hot_days_30"])
    demand_d = delta(
        base["summer_water_demand_mm"], recent["summer_water_demand_mm"]
    )

    lines = [
        "WHAT CHANGED",
        (
            f"At {loc}, summer water balance moved from "
            f"{base['summer_water_balance_mm']} mm ({base['period']}) to "
            f"{recent['summer_water_balance_mm']} mm ({recent['period']}) "
            f"({bal_d:+.0f} mm). Annual rainfall changed by {rain_d:+.0f} mm "
            f"({base['precip_mm']} → {recent['precip_mm']} mm) while summer ET0 "
            f"rose {demand_d:+.0f} mm and days ≥30°C rose {hot_d:+.1f}."
        ),
        "",
        "WHAT IT MEANS FOR YOUR CROPS",
    ]

    if assessment["verdict"] != "action_needed":
        lines.append(
            "Crop exposure scores stay in the stable/improving band. "
            "Do not force a crop switch from this climate signal alone."
        )
    else:
        exposed = [
            e
            for e in assessment["crops"]
            if e["crop"] in assessment["crops_at_risk"]
        ]
        bits = [
            (
                f"{e['label']} exposure {e['exposure_band']} "
                f"(irrigation gap {e['irrigation_gap_baseline_mm']} → "
                f"{e['irrigation_gap_recent_mm']} mm, {e['gap_widening_mm']:+d} mm)"
            )
            for e in exposed[:4]
        ]
        lines.append("; ".join(bits) + ".")
        if assessment["adaptation_candidates"]:
            alts = ", ".join(
                crop_model.CROPS[k]["label"]
                for k in assessment["adaptation_candidates"]
            )
            lines.append(f"Lower-exposure alternatives to consider: {alts}.")

    lines.extend(["", "WHAT TO DO"])
    if assessment["verdict"] == "action_needed":
        lines.extend(
            [
                "1. Before next sowing (Feb–Apr): prioritise water-efficient or "
                "shorter-maturity options for the most exposed summer crop — "
                "do not pick a brand from this tool.",
                "2. In spring: plan irrigation or mulching for the crop whose peak "
                "months overlap Jun–Aug most (see exposure table).",
                "3. This winter: treat annual rainfall totals as misleading if the "
                "masking signal is present — track summer rain minus ET0 instead.",
                "4. If adapting rotation: trial a lower-sensitivity summer crop on a "
                "strip before a full switch.",
            ]
        )
    else:
        lines.extend(
            [
                "1. Keep current rotation; re-check this plot after the next hot summer.",
                "2. Still log summer rainfall and irrigation hours — stability can reverse.",
                "3. Use the model range below as context, not as a forecast.",
            ]
        )

    outlook = record.get("outlook") or {}
    if outlook:
        lo, hi = outlook["hot_days_30_range"]
        lines.extend(
            [
                "",
                "WHAT TO WATCH",
                (
                    f"Model range for {outlook['period']}: {lo}–{hi} days ≥30°C/year "
                    f"across {len(outlook.get('models', []))} models "
                    f"({outlook.get('confidence', 'illustrative range')}). "
                    "Also watch June–August rainfall versus ET0 each season."
                ),
            ]
        )
    else:
        lines.extend(
            [
                "",
                "WHAT TO WATCH",
                "June–August rainfall versus ET0, and days ≥35°C each summer.",
            ]
        )

    lines.append(
        "\n_Source: offline plan built from data/pins.json + agrisense.crops "
        "(no LLM). Figures are measured or FAO-derived._"
    )
    return "\n".join(lines)


def call_grok(messages: list[dict]) -> str:
    api_key = os.environ.get("XAI_API_KEY") or os.environ.get("GROK_API_KEY")
    if not api_key:
        raise RuntimeError("No XAI_API_KEY / GROK_API_KEY set")

    model = os.environ.get("XAI_MODEL", "grok-2-latest")
    url = os.environ.get("XAI_API_URL", "https://api.x.ai/v1/chat/completions")
    resp = requests.post(
        url,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": model,
            "messages": messages,
            "temperature": 0.2,
            "max_tokens": 700,
        },
        timeout=60,
    )
    resp.raise_for_status()
    data = resp.json()
    return data["choices"][0]["message"]["content"].strip()


def main() -> None:
    apply_field_day_theme()

    pins, pin_source = load_pins()
    names_present = {p["location"]["name"] for p in pins}
    ordered = [n for n in DEMO_ORDER if n in names_present]
    ordered += sorted(names_present - set(ordered))

    st.title("AgriSense")
    st.caption(
        "Serbia field check — measured climate shift, crop exposure, action plan. "
        "Climate model summary is illustrative, not an official forecast."
    )

    with st.sidebar:
        st.header("Field")
        name = st.selectbox(
            "Demo pin",
            ordered,
            index=0,
            help="Cached pins from data/pins.json — no live API on click.",
        )
        st.markdown("**Pitch path**")
        st.markdown(
            "1. **Novi Sad** — rain gauge looks fine\n"
            "2. **Zrenjanin** — worst summer deficit\n"
            "3. **Belgrade / Nis** — stable counter-example"
        )
        use_llm = st.toggle(
            "Call Grok for advice",
            value=bool(
                os.environ.get("XAI_API_KEY") or os.environ.get("GROK_API_KEY")
            ),
            help="Needs XAI_API_KEY. Off = deterministic offline plan.",
        )
        show_prompt = st.toggle("Show LLM prompt (debug)", value=False)
        st.divider()

        if pin_source == "convex":
            st.caption(f"Store: **Convex** · {len(pins)} pins")
        else:
            st.caption(
                f"Store: local `{PINS_PATH.relative_to(ROOT)}` · {len(pins)} pins"
            )

        feed = store.recent_advisories(limit=5)
        if feed:
            st.markdown("**Recent plans (live)**")
            for item in feed:
                st.caption(f"· {item['location']} — {item['mode']}")

    record = pin_by_name(pins, name)
    assessment = crop_model.assess(record)
    loc = record["location"]
    base, recent = record["baseline"], record["recent"]

    st.subheader(f"{loc['name']} · {loc.get('region', 'Serbia')}")
    st.write(headline_for(record, assessment))

    m1, m2, m3, m4 = st.columns(4)
    m1.metric(
        "Summer balance",
        f"{recent['summer_water_balance_mm']} mm",
        f"{delta(base['summer_water_balance_mm'], recent['summer_water_balance_mm']):+.0f} mm vs baseline",
    )
    m2.metric(
        "Annual rain",
        f"{recent['precip_mm']} mm",
        f"{delta(base['precip_mm'], recent['precip_mm']):+.0f} mm",
    )
    m3.metric(
        "Summer ET0",
        f"{recent['summer_water_demand_mm']} mm",
        f"{delta(base['summer_water_demand_mm'], recent['summer_water_demand_mm']):+.0f} mm",
    )
    m4.metric(
        "Days ≥30°C",
        f"{recent['hot_days_30']}",
        f"{delta(base['hot_days_30'], recent['hot_days_30']):+.1f}",
    )

    left, right = st.columns((1.35, 1))

    with left:
        st.markdown("#### Your rain gauge can lie")
        st.caption(
            "Annual totals may look stable while June–August rainfall minus ET0 worsens."
        )
        st.bar_chart(water_balance_frame(record), height=280)

        st.markdown("#### Heat")
        st.bar_chart(heat_frame(record), height=220)

    with right:
        st.markdown("#### Signals")
        for sig in record.get("signals", []):
            st.markdown(f"- {SIGNAL_TEXT.get(sig, sig)}")

        outlook = record.get("outlook") or {}
        if outlook:
            lo, hi = outlook["hot_days_30_range"]
            st.markdown("#### Outlook (model range)")
            st.info(
                f"**{outlook['period']}** days ≥30°C: **{lo} – {hi}** "
                f"(median {outlook.get('hot_days_30_median', '—')}). "
                f"Rain {outlook['precip_mm_range'][0]}–{outlook['precip_mm_range'][1]} mm. "
                f"_{outlook.get('confidence', '')}_"
            )

        st.markdown("#### Map")
        st.map(
            pd.DataFrame([{"lat": loc["lat"], "lon": loc["lon"]}]),
            zoom=7,
            height=220,
        )

    st.markdown("#### Crop exposure (FAO-56)")
    if assessment["verdict"] != "action_needed":
        st.success(
            "No change indicated — no crop is in the high/moderate exposure band."
        )
    else:
        labels = ", ".join(
            crop_model.CROPS[c]["label"] for c in assessment["crops_at_risk"]
        )
        most = assessment["most_exposed"]
        st.warning(
            f"Action needed — at risk: **{labels}**. "
            f"Most exposed: **{crop_model.CROPS[most]['label']}**."
        )
        if assessment["adaptation_candidates"]:
            alts = ", ".join(
                crop_model.CROPS[c]["label"]
                for c in assessment["adaptation_candidates"]
            )
            st.caption(f"Adaptation candidates: {alts}")

    st.dataframe(crop_table(assessment), use_container_width=True, hide_index=True)

    thermal = assessment.get("thermal") or {}
    if thermal:
        st.caption(
            f"Heat accumulation: GDD {thermal.get('gdd_baseline')} → "
            f"{thermal.get('gdd_recent')} ({thermal.get('percent_change')}%). "
            f"{thermal.get('interpretation')}."
        )

    st.markdown("#### Action plan")
    cache_key = f"plan::{loc['name']}::{'llm' if use_llm else 'offline'}"
    if st.button("Generate plan", type="primary") or cache_key in st.session_state:
        if cache_key not in st.session_state:
            if use_llm:
                try:
                    with st.spinner("Asking Grok…"):
                        st.session_state[cache_key] = {
                            "mode": "llm",
                            "text": call_grok(build_messages(record, assessment)),
                        }
                except Exception as exc:  # noqa: BLE001 — show fallback in UI
                    st.session_state[cache_key] = {
                        "mode": "offline_fallback",
                        "text": offline_action_plan(record, assessment),
                        "error": str(exc),
                    }
            else:
                st.session_state[cache_key] = {
                    "mode": "offline",
                    "text": offline_action_plan(record, assessment),
                }

            # Best effort — a Convex failure must not hide the plan.
            store.log_advisory(
                record,
                assessment,
                st.session_state[cache_key]["mode"],
                st.session_state[cache_key]["text"],
            )

        payload = st.session_state[cache_key]
        if payload.get("error"):
            st.caption(
                f"LLM unavailable ({payload['error']}) — showing offline plan."
            )
        elif payload["mode"] == "llm":
            st.caption("Generated with Grok from the measured data block.")
        else:
            st.caption(
                "Offline plan — figures only from pins.json + FAO crop table."
            )
        st.markdown(payload["text"])

    if show_prompt:
        with st.expander("LLM user prompt"):
            st.code(build_user_prompt(record, assessment), language="markdown")

    st.divider()
    st.caption(
        "Data: Open-Meteo ERA5 archive + CMIP6 climate API via agrisense.climate · "
        "Crops: FAO Irrigation Manual 3 · SoilGrids unavailable for Europe — "
        "summer soil moisture from ERA5 when present · "
        "God's Eye View: out of scope for this build (see docs/GEV_DECISION.md)."
    )


if __name__ == "__main__":
    main()
