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

import altair as alt
import pandas as pd
import requests
import streamlit as st

from agrisense import crops as crop_model
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
  background: #ffffff !important;
  border: 1px solid var(--rule);
  border-radius: 20px;
  padding: 0.65rem 0.7rem 0.45rem;
  box-shadow:
    0 1px 0 rgba(255, 255, 255, 0.75) inset,
    0 12px 32px rgba(27, 45, 36, 0.06);
  overflow: hidden !important;
  max-width: 100%;
}

/* Keep Vega SVG inside the white panel — no green wash / no right-column eclipse */
[data-testid="stVegaLiteChart"] > div,
[data-testid="stArrowVegaLiteChart"] > div,
[data-testid="stVegaLiteChart"] canvas,
[data-testid="stArrowVegaLiteChart"] canvas,
[data-testid="stVegaLiteChart"] svg,
[data-testid="stArrowVegaLiteChart"] svg,
[data-testid="stVegaLiteChart"] .vega-embed,
[data-testid="stArrowVegaLiteChart"] .vega-embed {
  max-width: 100% !important;
  background: #ffffff !important;
}

[data-testid="stHorizontalBlock"] {
  gap: 1.35rem !important;
  align-items: start !important;
}

[data-testid="stHorizontalBlock"] > div {
  min-width: 0 !important; /* allow charts to shrink instead of overflowing */
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

/* Buttons — primary label always white on sage */
.stButton > button,
.stButton > button[kind="primary"],
.stButton > button[data-testid="baseButton-primary"] {
  background: var(--accent) !important;
  color: #ffffff !important;
  border: none !important;
  border-radius: 999px !important;
  font-family: "Figtree", sans-serif !important;
  font-weight: 600 !important;
  letter-spacing: -0.01em;
  padding: 0.55rem 1.25rem !important;
  box-shadow: 0 8px 20px var(--accent-glow);
  transition: transform 0.18s ease, background 0.18s ease;
}

.stButton > button p,
.stButton > button span,
.stButton > button[kind="primary"] p,
.stButton > button[kind="primary"] span,
.stButton > button[data-testid="baseButton-primary"] p,
.stButton > button[data-testid="baseButton-primary"] span {
  color: #ffffff !important;
}

.stButton > button:hover {
  background: #264d39 !important;
  color: #ffffff !important;
  transform: translateY(-1px);
}

.stButton > button[kind="secondary"],
.stButton > button[data-testid="baseButton-secondary"] {
  background: rgba(255, 255, 255, 0.7) !important;
  color: var(--ink) !important;
  border: 1px solid var(--rule-strong) !important;
  box-shadow: none !important;
}

.stButton > button[kind="secondary"] p,
.stButton > button[kind="secondary"] span {
  color: var(--ink) !important;
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

/* Sidebar — stronger field-day wash */
[data-testid="stSidebar"] {
  background: linear-gradient(
    185deg,
    rgba(244, 247, 244, 0.98) 0%,
    rgba(255, 252, 248, 0.94) 55%,
    rgba(232, 240, 234, 0.96) 100%
  ) !important;
  border-right: 1px solid var(--rule) !important;
}

[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h2,
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h3 {
  font-family: "Fraunces", Georgia, serif !important;
  color: var(--ink) !important;
}

[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stCheckbox label,
[data-testid="stSidebar"] label {
  color: var(--ink-soft) !important;
  font-weight: 500 !important;
}

.sidebar-brand {
  margin: 0.25rem 0 1rem;
  padding: 0.85rem 1rem;
  border-radius: 16px;
  background: linear-gradient(
    145deg,
    rgba(47, 95, 70, 0.12) 0%,
    rgba(255, 252, 248, 0.85) 100%
  );
  border: 1px solid var(--rule);
  box-shadow: 0 8px 20px rgba(27, 45, 36, 0.05);
}
.sidebar-brand .eyebrow {
  font-size: 0.68rem;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: var(--muted);
  margin-bottom: 0.2rem;
}
.sidebar-brand .title {
  font-family: "Fraunces", Georgia, serif;
  font-size: 1.35rem;
  color: var(--ink);
  letter-spacing: -0.03em;
  line-height: 1.1;
}
.sidebar-brand .sub {
  margin-top: 0.35rem;
  font-size: 0.82rem;
  color: var(--ink-soft);
  line-height: 1.4;
}

.pitch-card {
  margin: 0.6rem 0 0.9rem;
  padding: 0.7rem 0.85rem;
  border-radius: 14px;
  background: rgba(255, 252, 248, 0.75);
  border: 1px solid var(--rule);
  font-size: 0.86rem;
  color: var(--ink-soft);
  line-height: 1.55;
}
.pitch-card strong { color: var(--accent); }

.outlook-card {
  margin: 0.35rem 0 0.85rem;
  padding: 1rem 1.05rem 0.95rem;
  border-radius: 18px;
  background: linear-gradient(
    160deg,
    rgba(255, 252, 248, 0.95) 0%,
    rgba(232, 240, 234, 0.75) 100%
  );
  border: 1px solid var(--rule);
  box-shadow:
    0 1px 0 rgba(255, 255, 255, 0.8) inset,
    0 12px 28px rgba(27, 45, 36, 0.06);
}
.outlook-card .eyebrow {
  font-size: 0.68rem;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: var(--muted);
  margin-bottom: 0.35rem;
}
.outlook-card .period {
  font-family: "Fraunces", Georgia, serif;
  font-size: 1.35rem;
  color: var(--ink);
  letter-spacing: -0.03em;
  margin-bottom: 0.75rem;
}
.outlook-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.75rem;
}
.outlook-metric {
  padding: 0.65rem 0.7rem;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.65);
  border: 1px solid var(--rule);
}
.outlook-metric .label {
  font-size: 0.68rem;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--muted);
  margin-bottom: 0.25rem;
}
.outlook-metric .value {
  font-family: "Fraunces", Georgia, serif;
  font-size: 1.2rem;
  color: var(--ink);
  line-height: 1.15;
}
.outlook-metric .sub {
  margin-top: 0.25rem;
  font-size: 0.78rem;
  color: var(--ink-soft);
}
.outlook-range {
  margin-top: 0.45rem;
  height: 8px;
  border-radius: 999px;
  background: rgba(47, 95, 70, 0.12);
  overflow: hidden;
  position: relative;
}
.outlook-range > span {
  display: block;
  height: 100%;
  border-radius: 999px;
}
.outlook-note {
  margin-top: 0.75rem;
  font-size: 0.8rem;
  color: var(--muted);
  line-height: 1.45;
}
.status-pill {
  display: inline-block;
  margin-top: 0.4rem;
  padding: 0.18rem 0.55rem;
  border-radius: 999px;
  border: 1px solid;
  font-size: 0.72rem;
  font-weight: 600;
  letter-spacing: 0.02em;
}
.outlook-range > i {
  position: absolute;
  top: -3px;
  width: 2px;
  height: 14px;
  background: var(--ink);
  opacity: 0.55;
  border-radius: 2px;
  transform: translateX(-1px);
}
.legend-row {
  display: flex;
  flex-wrap: wrap;
  gap: 0.65rem 1rem;
  margin: 0.15rem 0 0.55rem;
  font-size: 0.78rem;
  color: var(--muted);
}
.legend-row span::before {
  content: "";
  display: inline-block;
  width: 0.65rem;
  height: 0.65rem;
  border-radius: 999px;
  margin-right: 0.35rem;
  vertical-align: middle;
}
.legend-good::before { background: #2f5f46; }
.legend-avg::before { background: #c4a35a; }
.legend-bad::before { background: #a84840; }
.legend-base::before { background: #8fa898; }
</style>
"""


def apply_field_day_theme() -> None:
    """Inject SoilShift-inspired cozy field-day CSS. Presentation only."""
    st.markdown(FIELD_DAY_CSS, unsafe_allow_html=True)


@st.cache_data
def load_pins() -> list[dict]:
    return json.loads(PINS_PATH.read_text(encoding="utf-8"))


def pin_by_name(pins: list[dict], name: str) -> dict:
    for pin in pins:
        if pin["location"]["name"] == name:
            return pin
    raise KeyError(name)


def delta(a: float, b: float) -> float:
    return round(b - a, 1)


# Traffic-light palette (theme-aligned): green good · gold average · red bad · sage baseline
COLOR_GOOD = "#2f5f46"
COLOR_AVG = "#c4a35a"
COLOR_BAD = "#a84840"
COLOR_BASE = "#8fa898"


def _gaussian_status(
    recent: float,
    baseline: float,
    *,
    higher_is_better: bool,
    sigma_frac: float = 0.15,
) -> str:
    """Traffic-light vs baseline using a normal-PDF style average band.

    Treat relative change as z = (recent − baseline) / σ with
    σ ≈ sigma_frac · |baseline| (floored). The average (gold) band is the
    high-density bulk of φ(z) — the derivative of the normal CDF — i.e.
    |z| < 1. Tails beyond 1σ read as better/worse.
    """
    sigma = max(abs(baseline) * sigma_frac, 1.0)
    z = (recent - baseline) / sigma
    if abs(z) < 1.0:
        return "Near baseline"
    improved = z > 0 if higher_is_better else z < 0
    return "Better than baseline" if improved else "Worse than baseline"


def _status_higher_worse(recent: float, baseline: float, tol_frac: float = 0.15) -> str:
    """Increase is worse — wide Near band (~1σ of a normal PDF)."""
    # tol_frac kept for call-site compat; maps onto gaussian sigma_frac.
    return _gaussian_status(
        recent, baseline, higher_is_better=False, sigma_frac=tol_frac
    )


def _status_higher_better(recent: float, baseline: float, tol_frac: float = 0.15) -> str:
    """Increase is better — wide Near band (~1σ of a normal PDF)."""
    return _gaussian_status(
        recent, baseline, higher_is_better=True, sigma_frac=tol_frac
    )


def _status_color(status: str) -> str:
    if status.startswith("Better"):
        return COLOR_GOOD
    if status.startswith("Worse"):
        return COLOR_BAD
    return COLOR_AVG


def score_legend_html() -> str:
    return (
        '<div class="legend-row">'
        '<span class="legend-good">Better than baseline</span>'
        '<span class="legend-avg">Near baseline (≈1σ)</span>'
        '<span class="legend-bad">Worse than baseline</span>'
        '<span class="legend-base">Baseline</span>'
        "</div>"
    )


def _status_scale() -> alt.Scale:
    return alt.Scale(
        domain=[
            "Baseline",
            "Better than baseline",
            "Near baseline",
            "Worse than baseline",
        ],
        range=[COLOR_BASE, COLOR_GOOD, COLOR_AVG, COLOR_BAD],
    )


def _paired_bar_chart(
    rows: list[dict],
    *,
    value_title: str,
    metric_order: list[str],
    height: int,
    pair_gap: float = 0.34,
    bar_size: int = 22,
) -> alt.Chart:
    """Baseline/Recent pairs tucked close on a clipped white panel."""
    index = {m: i for i, m in enumerate(metric_order)}
    # Half-gap between baseline & recent centers (<< 0.5 keeps the pair tight)
    half = pair_gap / 2
    for row in rows:
        i = index[row["metric"]]
        dx = -half if row["period"] == "Baseline" else half
        row["x"] = i + dx

    df = pd.DataFrame(rows)
    label_expr = "[" + ", ".join(repr(m) for m in metric_order) + "][datum.value]"
    return (
        alt.Chart(df)
        .mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4, size=bar_size)
        .encode(
            x=alt.X(
                "x:Q",
                title=None,
                scale=alt.Scale(domain=[-0.55, len(metric_order) - 0.45]),
                axis=alt.Axis(
                    values=list(range(len(metric_order))),
                    labelExpr=label_expr,
                    labelAngle=0,
                    labelFontSize=12,
                    ticks=False,
                    domain=True,
                    grid=False,
                ),
            ),
            y=alt.Y("value:Q", title=value_title),
            color=alt.Color("status:N", scale=_status_scale(), legend=None),
            tooltip=[
                alt.Tooltip("metric:N", title="Metric"),
                alt.Tooltip("period:N", title="Period"),
                alt.Tooltip("value:Q", title=value_title, format=".1f"),
                alt.Tooltip("status:N", title="vs baseline"),
            ],
        )
        .properties(
            height=height,
            padding={"left": 6, "right": 10, "top": 10, "bottom": 4},
        )
        .configure_axis(
            labelColor="#3e5349",
            titleColor="#6a7c72",
            gridColor="rgba(27, 45, 36, 0.08)",
            domainColor="rgba(27, 45, 36, 0.15)",
        )
        .configure(background="white")
        .configure_view(strokeWidth=0, fill="white")
    )


def water_balance_chart(record: dict) -> alt.Chart:
    """Grouped bars: sage baseline; recent colored vs that pin's baseline."""
    base = record["baseline"]
    recent = record["recent"]
    metrics = [
        (
            "Summer rain",
            base["summer_rain_mm"],
            recent["summer_rain_mm"],
            _status_higher_better(recent["summer_rain_mm"], base["summer_rain_mm"]),
        ),
        (
            "Crop demand (ET0)",
            base["summer_water_demand_mm"],
            recent["summer_water_demand_mm"],
            _status_higher_worse(
                recent["summer_water_demand_mm"], base["summer_water_demand_mm"]
            ),
        ),
        (
            "Summer balance",
            base["summer_water_balance_mm"],
            recent["summer_water_balance_mm"],
            _status_higher_better(
                recent["summer_water_balance_mm"], base["summer_water_balance_mm"]
            ),
        ),
    ]
    rows = []
    for label, b_val, r_val, status in metrics:
        rows.append(
            {
                "metric": label,
                "period": "Baseline",
                "value": b_val,
                "status": "Baseline",
            }
        )
        rows.append(
            {
                "metric": label,
                "period": "Recent",
                "value": r_val,
                "status": status,
            }
        )
    return _paired_bar_chart(
        rows,
        value_title="mm",
        metric_order=["Summer rain", "Crop demand (ET0)", "Summer balance"],
        height=260,
        pair_gap=0.22,
        bar_size=22,
    )


def heat_chart(record: dict) -> alt.Chart:
    base = record["baseline"]
    recent = record["recent"]
    metrics = [
        (
            "Days ≥30°C",
            base["hot_days_30"],
            recent["hot_days_30"],
            _status_higher_worse(recent["hot_days_30"], base["hot_days_30"]),
        ),
        (
            "Days ≥35°C",
            base["hot_days_35"],
            recent["hot_days_35"],
            _status_higher_worse(recent["hot_days_35"], base["hot_days_35"]),
        ),
    ]
    rows = []
    for label, b_val, r_val, status in metrics:
        rows.append(
            {
                "metric": label,
                "period": "Baseline",
                "value": b_val,
                "status": "Baseline",
            }
        )
        rows.append(
            {
                "metric": label,
                "period": "Recent",
                "value": r_val,
                "status": status,
            }
        )
    return _paired_bar_chart(
        rows,
        value_title="days / year",
        metric_order=["Days ≥30°C", "Days ≥35°C"],
        height=230,
        pair_gap=0.22,
        bar_size=26,
    )


def crop_exposure_chart(assessment: dict) -> alt.Chart:
    """Horizontal exposure scores — green / gold / red by band."""
    band_label = {
        "high": "High (stressed)",
        "moderate": "Moderate (watch)",
        "stable": "Stable",
        "improving": "Improving",
        "low": "Low",
    }
    rows = []
    for entry in assessment["crops"]:
        band = entry["exposure_band"]
        rows.append(
            {
                "crop": entry["label"],
                "score": entry["exposure_score"],
                "band": band_label.get(band, band),
            }
        )
    df = pd.DataFrame(rows).sort_values("score", ascending=True)
    n = max(len(df), 1)
    # Extra vertical room so every crop label is visible + a little gap between bars
    row_px = 52
    return (
        alt.Chart(df)
        .mark_bar(cornerRadiusEnd=6, size=18)
        .encode(
            x=alt.X("score:Q", title="Exposure score"),
            y=alt.Y(
                "crop:N",
                sort=list(df["crop"]),
                title=None,
                scale=alt.Scale(paddingInner=0.28, paddingOuter=0.1),
                axis=alt.Axis(labelFontSize=13, labelLimit=180, labelPadding=8),
            ),
            color=alt.Color(
                "band:N",
                scale=alt.Scale(
                    domain=[
                        "High (stressed)",
                        "Moderate (watch)",
                        "Stable",
                        "Improving",
                        "Low",
                    ],
                    range=[
                        COLOR_BAD,
                        COLOR_AVG,
                        COLOR_GOOD,
                        COLOR_GOOD,
                        COLOR_GOOD,
                    ],
                ),
                legend=alt.Legend(title=None, orient="bottom", direction="horizontal"),
            ),
            tooltip=[
                alt.Tooltip("crop:N", title="Crop"),
                alt.Tooltip("score:Q", title="Score", format=".2f"),
                alt.Tooltip("band:N", title="Band"),
            ],
        )
        .properties(
            height=max(300, row_px * n + 48),
            padding={"left": 4, "right": 10, "top": 8, "bottom": 4},
        )
        .configure_axis(
            labelColor="#3e5349",
            titleColor="#6a7c72",
            gridColor="rgba(27, 45, 36, 0.08)",
            domainColor="rgba(27, 45, 36, 0.15)",
        )
        .configure(background="white")
        .configure_view(strokeWidth=0, fill="white")
        .configure_legend(
            labelColor="#3e5349",
            titleColor="#6a7c72",
            symbolType="circle",
        )
    )


def outlook_card_html(record: dict) -> str:
    """Formatted outlook panel with range bars vs recent climate."""
    outlook = record.get("outlook") or {}
    if not outlook:
        return ""
    recent = record["recent"]
    lo, hi = outlook["hot_days_30_range"]
    med = outlook.get("hot_days_30_median", (lo + hi) / 2)
    rain_lo, rain_hi = outlook["precip_mm_range"]
    rain_med = outlook.get("precip_mm_median", (rain_lo + rain_hi) / 2)
    recent_hot = recent["hot_days_30"]
    recent_rain = recent["precip_mm"]

    heat_status = _status_higher_worse(med, recent_hot, tol_frac=0.08)
    heat_color = _status_color(heat_status)
    rain_mid = rain_med
    rain_status = _status_higher_better(rain_mid, recent_rain, tol_frac=0.08)
    rain_color = _status_color(rain_status)

    heat_scale = max(hi, recent_hot, 60)
    rain_scale = max(rain_hi, recent_rain, 800)
    heat_width = max(8, min(100, (hi - lo) / heat_scale * 100))
    heat_left = max(0, min(92, lo / heat_scale * 100))
    rain_width = max(8, min(100, (rain_hi - rain_lo) / rain_scale * 100))
    rain_left = max(0, min(92, rain_lo / rain_scale * 100))
    heat_marker = max(0, min(98, recent_hot / heat_scale * 100))
    rain_marker = max(0, min(98, recent_rain / rain_scale * 100))

    models = ", ".join(outlook.get("models", [])[:3]) or "multi-model"
    note = outlook.get("confidence", "multi-model range, illustrative not a forecast")
    n_models = len(outlook.get("models") or [])

    return f"""
<div class="outlook-card">
  <div class="eyebrow">Outlook · model range</div>
  <div class="period">{outlook.get("period", "—")}</div>
  <div class="outlook-grid">
    <div class="outlook-metric">
      <div class="label">Days ≥30°C</div>
      <div class="value" style="color:{heat_color}">{lo:.0f} – {hi:.0f}</div>
      <div class="sub">median <strong>{med:.0f}</strong> · recent {recent_hot:.0f}</div>
      <div class="status-pill" style="background:{heat_color}22;color:{heat_color};border-color:{heat_color}55">{heat_status}</div>
      <div class="outlook-range">
        <span style="width:{heat_width}%; margin-left:{heat_left}%; background:{heat_color};"></span>
        <i style="left:{heat_marker}%;" title="Recent"></i>
      </div>
    </div>
    <div class="outlook-metric">
      <div class="label">Annual rain (mm)</div>
      <div class="value" style="color:{rain_color}">{rain_lo:.0f} – {rain_hi:.0f}</div>
      <div class="sub">median <strong>{rain_med:.0f}</strong> · recent {recent_rain:.0f}</div>
      <div class="status-pill" style="background:{rain_color}22;color:{rain_color};border-color:{rain_color}55">{rain_status}</div>
      <div class="outlook-range">
        <span style="width:{rain_width}%; margin-left:{rain_left}%; background:{rain_color};"></span>
        <i style="left:{rain_marker}%;" title="Recent"></i>
      </div>
    </div>
  </div>
  <div class="outlook-note">{note}. {n_models} models ({models}). Marker = recent climate.</div>
</div>
"""


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


def resolve_xai_key() -> str | None:
    """Sidebar paste wins for the session; else env XAI_API_KEY / GROK_API_KEY."""
    keyed = (st.session_state.get("xai_api_key") or "").strip()
    if keyed:
        return keyed
    return os.environ.get("XAI_API_KEY") or os.environ.get("GROK_API_KEY") or None


def call_grok(messages: list[dict]) -> str:
    api_key = resolve_xai_key()
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

    pins = load_pins()
    names_present = {p["location"]["name"] for p in pins}
    ordered = [n for n in DEMO_ORDER if n in names_present]
    ordered += sorted(names_present - set(ordered))

    st.title("AgriSense")
    st.caption(
        "Serbia field check — measured climate shift, crop exposure, action plan. "
        "Climate model summary is illustrative, not an official forecast."
    )

    with st.sidebar:
        st.markdown(
            """
            <div class="sidebar-brand">
              <div class="eyebrow">SoilShift × AgriSense</div>
              <div class="title">Field day</div>
              <div class="sub">Sage mist briefing · cached Serbia pins · offline-first</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        name = st.selectbox(
            "Demo pin",
            ordered,
            index=0,
            help="Cached pins from data/pins.json — no live API on click.",
        )
        st.markdown(
            """
            <div class="pitch-card">
              <strong>Pitch path</strong><br/>
              1. <strong>Novi Sad</strong> — rain gauge looks fine<br/>
              2. <strong>Zrenjanin</strong> — worst summer deficit<br/>
              3. <strong>Belgrade / Nis</strong> — stable counter-example
            </div>
            """,
            unsafe_allow_html=True,
        )
        pasted = st.text_input(
            "xAI API key",
            value=st.session_state.get("xai_api_key", ""),
            type="password",
            help="Paste a key from https://console.x.ai — stored only in this browser session. "
            "Or export XAI_API_KEY before `streamlit run`.",
            placeholder="xai-…",
        )
        if pasted.strip():
            st.session_state["xai_api_key"] = pasted.strip()
        elif "xai_api_key" in st.session_state and not pasted:
            # cleared by user
            st.session_state.pop("xai_api_key", None)

        has_key = bool(resolve_xai_key())
        use_llm = st.toggle(
            "Call Grok for advice",
            value=has_key,
            help="Needs an xAI key (sidebar or XAI_API_KEY). Off = deterministic offline plan.",
        )
        show_prompt = st.toggle("Show LLM prompt (debug)", value=False)
        st.divider()
        st.caption(
            f"Offline store: `{PINS_PATH.relative_to(ROOT)}` · {len(pins)} pins"
        )

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
        delta_color="inverse",
    )
    m4.metric(
        "Days ≥30°C",
        f"{recent['hot_days_30']}",
        f"{delta(base['hot_days_30'], recent['hot_days_30']):+.1f}",
        delta_color="inverse",
    )

    left, right = st.columns((1.25, 1), gap="large")

    with left:
        st.markdown("#### Your rain gauge can lie")
        st.caption(
            "Annual totals may look stable while June–August rainfall minus ET0 worsens. "
            "Recent colored vs this pin’s baseline — gold = within ~1σ (average span)."
        )
        st.markdown(score_legend_html(), unsafe_allow_html=True)
        st.altair_chart(water_balance_chart(record), use_container_width=True)

        st.markdown("#### Heat")
        st.caption("More hot days than baseline reads as worse (red); near stays gold.")
        st.altair_chart(heat_chart(record), use_container_width=True)

    with right:
        st.markdown("#### Signals")
        for sig in record.get("signals", []):
            st.markdown(f"- {SIGNAL_TEXT.get(sig, sig)}")

        if record.get("outlook"):
            st.markdown("#### Outlook")
            st.markdown(outlook_card_html(record), unsafe_allow_html=True)

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

    st.altair_chart(crop_exposure_chart(assessment), use_container_width=True)
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
