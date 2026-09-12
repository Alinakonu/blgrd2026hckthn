# AgriSense

**Serbia climate field check** — pick a plot, see the measured summer water-balance shift (the rain gauge can lie), see which crops are exposed, get an action plan.

Hackathon demo for Belgrade. Track A climate pipeline is done; this repo now also ships the **Path A Track B UI** (Streamlit).

## Happy path (~60s)

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

1. Open the app → pin **Novi Sad**.
2. Show: annual rain flat/up, summer balance worse → “your rain gauge can lie”.
3. Crop table: maize most exposed; sorghum as adaptation candidate.
4. Click **Generate plan** (offline plan works without an API key).
5. Switch to **Zrenjanin** (worst case), then **Belgrade** or **Nis** (stable counter-example).

Optional live LLM (Grok via xAI):

```bash
# terminal (recommended for demos)
export XAI_API_KEY="xai-..."   # from https://console.x.ai
streamlit run app.py
```

Or paste the key in the sidebar field **xAI API key** (session-only, not written to disk), then toggle **Call Grok for advice**.

## What is in the box

| Path | Role |
| --- | --- |
| `data/pins.json` | Offline climate pins (6 Serbian locations) |
| `agrisense/climate.py` | ERA5 + CMIP6 fetch / indices (Track A) |
| `agrisense/crops.py` | FAO-56 crop exposure for Serbia majors |
| `agrisense/prompt.py` | LLM prompt builder (numbers in → advice out) |
| `app.py` | Streamlit UI (dropdown → charts → crops → plan) |
| `scripts/build_pins.py` | Rebuild pins (slow, rate-limited — do not put on click path) |
| `scripts/preview_advice.py` | Print assessments + prompts offline |
| `docs/` | Crop model, LLM prompt, data limits, GEV decision (**out**) |

## Design rules (do not break in the demo)

- Read **`data/pins.json` on click**. Live `build_pin` is 30–100s+ and hits Open-Meteo 429s.
- Outlook is always a **model range**, never a single projected number.
- SoilGrids is dead for Europe — do not render an empty soil card; ERA5 summer moisture only.
- Grok must not invent yields, prices, or variety names (`docs/LLM_PROMPT.md`).
- God's Eye View is **out of scope** (`docs/GEV_DECISION.md`).

## Environment

| Variable | Required | Notes |
| --- | --- | --- |
| `XAI_API_KEY` / `GROK_API_KEY` | No | Enables live Grok plan (or paste in the sidebar) |
| `XAI_MODEL` | No | Default `grok-2-latest` |
| `XAI_API_URL` | No | Default `https://api.x.ai/v1/chat/completions` |

No keys needed for the offline happy path.

## Pitch script

1. **Novi Sad** — annual rain looks fine; summer deficit ~57 mm worse.
2. **Zrenjanin** — heat + deficit worst case.
3. **Belgrade / Nis** — no crop-exposure action band → proves per-plot honesty.

## Related docs

- [`PLAN.md`](./PLAN.md) — investigation + build plan
- [`idea.md`](./idea.md) — product concept
- [`TECH_PARTNERS.md`](./TECH_PARTNERS.md) — sponsor tools
- [`docs/CROP_MODEL.md`](./docs/CROP_MODEL.md) — why FAO table, not Kaggle
- [`docs/LLM_PROMPT.md`](./docs/LLM_PROMPT.md) — Grok prompt rules
- [`docs/GEV_DECISION.md`](./docs/GEV_DECISION.md) — God's Eye View out of scope
- [`docs/DATA_LIMITS.md`](./docs/DATA_LIMITS.md) — rate limits / SoilGrids / schema lag
