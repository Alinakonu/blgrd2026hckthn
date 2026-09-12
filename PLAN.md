> **Working plan / draft** — living investigation & build plan. Expect updates as we verify APIs and split work.

# AgriSense — Investigation & Build Plan (2 people, parallel)

Working document. Goal: decide fast what is real, split the research so we never block each other, then converge on one demo.

Related: [`idea.md`](idea.md) (concept), [`TECH_PARTNERS.md`](TECH_PARTNERS.md) (sponsor tools).

---

## 0. Track A results — measured, not assumed

Everything below came from running `scripts/build_pins.py` against the live APIs for all six pins. Output is committed at `data/pins.json`.

| Source | Status | Detail |
| --- | --- | --- |
| Open-Meteo Archive | ✅ works | ERA5 daily, 1940→, no key. Also serves ET0 and soil moisture. |
| Open-Meteo Climate | ✅ works | 3 CMIP6 models retrieved to 2050 |
| SoilGrids | ❌ **dead for Europe** | Returns HTTP 200 with `null` values for Serbia *and* the Netherlands. Iowa returns real data, so it's regional, not our bug. 0/6 pins. |
| FAOSTAT QCL | ❌ HTTP 521 | Still down |

> **Correction to an earlier note in this file:** SoilGrids was previously marked verified. That check only read the response's layer *names*, which are present even when every value is null. It is not usable for Serbia right now.

### The real finding: annual rainfall hides the problem

The first hunch — "rain flat, heat up" — only held at Novi Sad, and only for *annual* totals. Annual rainfall actually **rose** at four of six pins. The defensible version uses the growing-season water balance: summer rainfall minus ET0 (reference evapotranspiration, the FAO standard measure of crop water demand). Both come straight from ERA5.

**Summer (Jun–Aug) water balance, mm/year:**

| Location | Rainfall | ET0 demand | Balance | Annual rainfall says |
| --- | --- | --- | --- | --- |
| Novi Sad | 187 → 158 | 428 → 456 | −241 → **−298** | "stable, 599→609" |
| Zrenjanin | 170 → 159 | 430 → 471 | −260 → **−312** | "stable, 564→597" |
| Subotica | 156 → 159 | 434 → 463 | −278 → **−304** | "improving, 547→606" |
| Belgrade | 181 → 209 | 420 → 449 | −239 → −240 | improving, 598→708 |
| Kraljevo | 192 → 206 | 382 → 414 | −190 → −208 | improving, 661→772 |
| Niš | 132 → 164 | 419 → 434 | −287 → **−270** | improving, 521→682 |

**Three things this gives us that a generic climate chart does not:**

1. **ET0 rose at 6 of 6 pins** (+15 to +41 mm per summer). Crop water demand is up everywhere, without exception. That is the universal signal.
2. **The masking effect is real at 3 of 6 pins** — Novi Sad, Zrenjanin, Subotica. Their annual rainfall looks flat or improving while the summer deficit worsens by 26–57 mm. A farmer reading annual totals concludes nothing is wrong.
3. **It is not uniform, and that is the product.** Vojvodina (the northern breadbasket) is deteriorating; Belgrade, Kraljevo and Niš are stable or improving. So the answer genuinely depends on your plot — which is the reason to build the tool at all. "Everything is getting worse" would be both less true and less useful.

Heat rose at 6 of 6 pins regardless: growing degree days up 51–190, days ≥35 °C up at every location (Zrenjanin 2.7 → 8.0).

---

## 1. Open questions

| # | Question | Risk if wrong | Owner | Status |
| --- | --- | --- | --- | --- |
| Q1 | Does the signal hold across Serbia, or is Novi Sad a fluke? | Kills the pitch | A | ✅ Holds at 6/6 for heat and ET0; water deficit worsens at 3/6 |
| Q2 | Is the Climate projection usable, or does model choice swing it? | Forecast panel becomes noise | A | ✅ Direction agrees, magnitude does not — **must show a range** |
| Q3 | Can we get real soil per point? | Back to fake sliders | A | ❌ SoilGrids dead for Europe — replaced with ERA5 soil moisture |
| Q4 | Which map/UI gives click-a-field in the least code? | Burns hours on plumbing | B | open |
| Q5 | Does the Kaggle crop model make sense for Serbian crops? | Recommendations look silly | B | open |
| Q6 | Does the LLM produce real agronomy or generic filler? | Demo feels hollow | B | open |
| Q7 | Is God's Eye View worth forking? | Could eat the whole day | B | open |

**On Q2 — do not print a single projected number.** For 2031–2040 days ≥30 °C the three models disagree substantially: Novi Sad 44–57, Belgrade 42–53, Kraljevo 38–47. Every model agrees the direction is up and every projection exceeds the recent decade, so the honest presentation is "44 to 57 days, models disagree on how far" rather than a fake-precise 52.

---

## 2. The contract — this now exists, don't invent your own

Person A produces this; Person B consumes it. It is **already built and committed** at `data/pins.json` for all six pins, so Track B is unblocked immediately — no waiting, no fixtures.

```python
import json
pins = json.load(open("data/pins.json", encoding="utf-8"))
# or, for an arbitrary point:
from agrisense.climate import build_pin
record = build_pin({"name": "My field", "lat": 45.1, "lon": 19.9})
```

Real record, abbreviated:

```json
{
  "location": { "name": "Novi Sad", "region": "Vojvodina", "lat": 45.2671, "lon": 19.8335 },
  "baseline": {
    "period": "1985-1994",
    "hot_days_30": 29.4, "hot_days_35": 3.5, "peak_temp": 39.6,
    "longest_hot_streak_days": 8.9, "precip_mm": 599,
    "heavy_rain_days_20": 2.5, "max_dry_streak_days": 23.5,
    "growing_degree_days": 1679,
    "summer_rain_mm": 187, "summer_water_demand_mm": 428,
    "summer_water_balance_mm": -241, "summer_soil_moisture": 0.2372
  },
  "recent": { "period": "2015-2024", "...": "same keys" },
  "outlook": {
    "period": "2031-2040",
    "hot_days_30_range": [44.2, 56.9],
    "hot_days_30_median": 51.9,
    "precip_mm_range": [681, 709],
    "confidence": "multi-model range, illustrative not a forecast",
    "per_model": { "MRI_AGCM3_2_S": { "...": "full indices" } }
  },
  "soil": null,
  "signals": [
    "heat_intensifying", "annual_rainfall_stable", "crop_water_demand_rising",
    "summer_water_deficit_worsening", "annual_totals_masking_summer_stress"
  ]
}
```

**Notes for Track B:**

- `soil` is `null` for every Serbian pin — SoilGrids is down for Europe. Use `summer_soil_moisture` (ERA5, always present) or keep manual sliders as an input, not as an output. Don't render an empty soil card.
- `signals` is the list to drive both the UI headline and the LLM prompt. Current vocabulary: `heat_intensifying` / `heat_stable` / `heat_easing`, `annual_rainfall_stable` / `_increasing` / `_declining`, `crop_water_demand_rising`, `summer_water_deficit_worsening` / `_stable` / `_easing`, `annual_totals_masking_summer_stress`, `dry_spells_lengthening`.
- **Timing matters.** A full `build_pin` takes 33–114 s (five API calls, throttled to dodge Open-Meteo's 429s). That is not interactive. Read `data/pins.json` for the demo; only call `build_pin` live for an off-pin location, with a spinner and a warning.

**Rule:** if either of us needs to change this shape, say so immediately — it is the only hard dependency between the tracks.

---

## 3. Parallel work split

Timebox: **~75 minutes of investigation**, then we sync and build. Do not perfect anything in this phase; the output of each task is a yes/no plus a snippet that runs.

### Track A — Data & signal — ✅ done

| Task | Deliverable | Result |
| --- | --- | --- |
| A1 | Decade comparison across 6 Serbian points | Heat and ET0 up at 6/6; deficit worsens at 3/6 |
| A2 | Multi-model projection spread | 3 models agree on direction, spread up to 13 days → report a range |
| A3 | SoilGrids reliability | 0/6, Europe returns nulls → dropped, replaced with ERA5 soil moisture |
| A4 | Index calculator | `agrisense/climate.py` — hot days, GDD, dry streaks, ET0, water balance |
| A5 | Offline fallback | `data/pins.json`, 6 records committed |

Two methodology fixes made along the way, both worth knowing because they changed the numbers:

- **Dry streaks** were being computed over the whole concatenated decade, which reports the single worst drought in ten years as if it were typical (Subotica looked like a 60-day streak). Now it averages each year's longest run — Subotica is 27.4 → 26.1 days, i.e. flat.
- **SoilGrids** looked fine because the response carries layer names even when every value is null. Always check values, not keys.

**Insurance is in place:** `data/pins.json` is committed, so the demo runs with every network call failing.

### Track B — Interface & reasoning (owns: does it land?)

| Task | Deliverable | Timebox |
| --- | --- | --- |
| B1 | Streamlit skeleton + map click returning lat/lon. Answer Q4 (see candidates below). | 20 min |
| B2 | Load Kaggle crop dataset, train RandomForest, sanity-check it on Serbian-ish inputs. Answer Q5: does it say wheat/maize, or mango? | 20 min |
| B3 | Write the LLM prompt against the **fixture JSON**, not real data. Answer Q6. Iterate on prompt until output is specific (names crops, months, actions). | 20 min |
| B4 | Decide GEV: 15 min timeboxed spike — `git clone`, `npm ci`, `npm run dev`. If it doesn't run in 15 min, **drop it** and note why. Answer Q7. | 15 min |

**B2 warning to check for:** the Kaggle crop dataset is India-centric (rice, mango, coconut, jute). If it never recommends wheat/maize/soy, it is wrong for Serbia — fall back to a hand-written suitability table for ~6 local crops. That table is ~20 lines and more defensible in front of Serbian judges anyway.

---

## 4. Candidates per step

Use these instead of searching from scratch. Status reflects what we actually know.

### Climate history & projection

| Candidate | Status | Notes |
| --- | --- | --- |
| **Open-Meteo Archive** `archive-api.open-meteo.com/v1/archive` | ✅ in use | ERA5, 1940→, no key. Also supplies ET0 and soil moisture. **Primary.** |
| **Open-Meteo Climate** `climate-api.open-meteo.com/v1/climate` | ✅ in use | to 2050; pass `models=` explicitly and report the spread |
| Copernicus EFAS / GloFAS (flood) | ⚠️ heavy | Account + GRIB/NetCDF parsing. **Skip.** |
| EM-DAT (disaster events) | ⚠️ GraphQL + registration | Pitch narrative only, not the pipeline |
| MeteoSerbia1km (Zenodo) | 🟡 offline CSV | Unnecessary now that `pins.json` exists |
| RHMZ / Digital Climate Atlas of Serbia | 🟡 no clean API | Credibility citation in slides |

**Rate limit warning:** Open-Meteo returns HTTP 429 on bursts. `agrisense/climate.py` paces requests 6 s apart and backs off on 429; without that, 2 of 6 pins failed.

### Soil

| Candidate | Status | Notes |
| --- | --- | --- |
| **ERA5 soil moisture via Open-Meteo** | ✅ in use | `soil_moisture_0_to_7cm_mean`. Real, free, trended over decades. |
| SoilGrids `rest.isric.org` | ❌ down for Europe | HTTP 200 with null values for Serbia and NL; Iowa works. Retry on the day in case it returns. |
| Manual NPK/pH sliders | 🟡 keep | Now an *input* the farmer supplies, not something we claim to know |

### Crop / yield

| Candidate | Status | Notes |
| --- | --- | --- |
| Kaggle `atharvaingle/crop-recommendation-dataset` | 🟡 unverified fit | See B2 warning — India-centric |
| Hand-built Serbian crop suitability table | ✅ always works | 6 crops × temp/water tolerance. Recommended. |
| FAOSTAT QCL | ❌ 521 error today | Retry once; else drop |
| Eurostat `apro_cpsh1` / DBnomics | 🟡 untested | Backup for yield validation, only if we want a yield chart |

### UI / map

| Candidate | Status | Notes |
| --- | --- | --- |
| **`streamlit-folium`** (`st_folium` → `last_clicked`) | ✅ simplest | Returns `{lat, lng}` directly. **Recommended for B1.** |
| `st.pydeck_chart(on_select="rerun")` | 🟡 more code | Needs layer `id` + object picking; clicking empty map gives nothing |
| Preset dropdown of 6 Serbian cities | ✅ zero risk | **Build this first**, add map after |
| God's Eye View fork | ⚠️ timebox | Cesium+Vite, Node 24+. Great visuals, real cost. B4 decides. |

### LLM

| Candidate | Status | Notes |
| --- | --- | --- |
| x.ai / Grok API | 🟢 sponsor | Use this — sponsor points |
| LangChain | 🟡 optional | Probably unnecessary; a single prompt + JSON is enough |
| CrewAI multi-agent | ❌ | Don't. Not in this timeframe. |

---

## 5. Sync point

**A has reported:** signal holds at 6/6 for heat and crop water demand; the summer water deficit worsens at 3/6, all in Vojvodina; projections need a range not a number; soil comes from ERA5 because SoilGrids is down; `data/pins.json` is committed as the offline path.

**B still to report:** "Map click works via X. Crop model is usable/replaced. LLM output is specific/generic. GEV is in/out."

Decisions left:
1. Map or dropdown?
2. Kaggle model or hand table?
3. GEV or Streamlit only?

Decision 3 from the original list — live APIs or cached — is **settled: cached.** A full point build takes 33–114 s, so live fetching cannot sit in the click path.

**Default if we run out of time:** dropdown + hand table + `pins.json` + Streamlit. Zero external dependencies at demo time, and it still tells the whole story.

---

## 6. Build phase (after sync)

```
[+0:00] Wire data/pins.json into B's UI (already exists → minutes)
[+0:20] Water-balance panel: rainfall vs ET0, the "your rain gauge lies" chart
[+0:40] Crop + action plan panel from LLM, driven by signals[]
[+1:00] Three scripted locations, screenshots taken
[+1:20] Fallback path tested with network off
[+1:30] Pitch script + 60s recording
```

**Demo running order** — the contrast is what sells it:

1. **Novi Sad** — annual rainfall flat, summer deficit 57 mm worse. "Nothing looks wrong, and that's the problem."
2. **Zrenjanin** — worst case, deficit 52 mm worse and days ≥35 °C up from 2.7 to 8.0.
3. **Belgrade or Niš** — the counter-example. Deficit stable, Niš slightly improved. Proves the tool answers per-plot rather than printing doom everywhere.

---

## 7. Non-goals

Naming these so neither of us drifts:

- No leaf-disease vision module unless everything else is done.
- No user accounts, no persistence, no field polygon drawing.
- No claim that this is a forecast. We say **"climate model summary, illustrative"** on screen.
- No new model training beyond a RandomForest that fits in seconds.

---

## 8. Checklist

**Track A** — complete
- [x] A1 multi-location signal check — 6/6 heat, 3/6 deficit worsening
- [x] A2 model-spread check — range required, direction robust
- [x] A3 SoilGrids — down for Europe, replaced with ERA5 soil moisture
- [x] A4 indices — `agrisense/climate.py` incl. ET0 water balance
- [x] A5 `data/pins.json` committed

**Track B**
- [x] B1 map click or dropdown working — Streamlit `streamlit_app.py` dropdown over `data/pins.json` (+ map marker)
- [x] B2 crop recommender sane for Serbia — `agrisense/crops.py` FAO table (Kaggle dropped; see `docs/CROP_MODEL.md`)
- [x] B3 LLM prompt producing specific advice — `agrisense/prompt.py` + offline deterministic plan in UI; live Grok optional via `XAI_API_KEY`
- [x] B4 GEV in-or-out decision recorded — **out** (`docs/GEV_DECISION.md`)

**Together**
- [x] Sync + 4 decisions made — dropdown + FAO table + GEV out + cached pins on click
- [x] End-to-end demo runs — `streamlit run streamlit_app.py`
- [x] Offline fallback verified — pins.json + offline action plan (no API key)
- [ ] Pitch recorded
