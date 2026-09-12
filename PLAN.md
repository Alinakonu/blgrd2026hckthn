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

## 2. The contract — agree on this BEFORE splitting

This is what lets us work in parallel without blocking. Person A produces this JSON; Person B consumes it. **Person B builds against a hardcoded fixture of this shape immediately**, without waiting for A's real implementation.

```json
{
  "location": { "name": "Novi Sad", "lat": 45.2671, "lon": 19.8335 },
  "baseline": {
    "period": "1985-1994",
    "hot_days_30": 29.4,
    "hot_days_35": 3.5,
    "precip_mm": 599,
    "heavy_rain_days_20": 2.5,
    "max_dry_streak_days": 21
  },
  "recent": {
    "period": "2015-2024",
    "hot_days_30": 38.1,
    "hot_days_35": 6.6,
    "precip_mm": 609,
    "heavy_rain_days_20": 2.6,
    "max_dry_streak_days": 28
  },
  "outlook": {
    "period": "2030-2039",
    "hot_days_30": 44.0,
    "precip_mm": 615,
    "confidence": "single-model illustrative"
  },
  "soil": { "ph": 6.8, "clay_pct": 24.0, "nitrogen_g_kg": 1.9, "source": "SoilGrids" },
  "signals": ["heat_intensifying", "rainfall_stable", "evaporative_stress_rising"]
}
```

**Rule:** if either of us needs to change this shape, say so immediately — it is the only hard dependency between the two tracks.

---

## 3. Parallel work split

Timebox: **~75 minutes of investigation**, then we sync and build. Do not perfect anything in this phase; the output of each task is a yes/no plus a snippet that runs.

### Track A — Data & signal (owns: is this real?)

| Task | Deliverable | Timebox |
| --- | --- | --- |
| A1 | Run the decade comparison for 5–6 Serbian points (Novi Sad, Subotica, Belgrade, Niš, Zrenjanin, Kraljevo). Answer Q1: does heat rise everywhere? | 20 min |
| A2 | Pull Climate API for 2–3 different models at one point. Answer Q2: do they agree on direction? If they disagree wildly, we present **range**, not a number. | 15 min |
| A3 | Hit SoilGrids for those same points, time each call, note failures. Answer Q3. Decide: live call, or pre-cached JSON for the demo pins. | 15 min |
| A4 | Add dry-streak + growing-degree-days to the index calculator | 15 min |
| A5 | Emit the section 2 JSON for all demo pins → commit as `data/pins.json` | 10 min |

**Fallback if an API dies mid-hackathon:** A5's committed `pins.json` becomes the demo's data source. This is our insurance — do it even if everything works.

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
| **Open-Meteo Archive** `archive-api.open-meteo.com/v1/archive` | ✅ verified | ERA5, 1940→, no key, JSON. **Primary.** |
| **Open-Meteo Climate** `climate-api.open-meteo.com/v1/climate` | ✅ verified | to 2050, pick `models=` explicitly |
| Copernicus EFAS / GloFAS (flood) | ⚠️ heavy | Needs account + GRIB/NetCDF parsing. **Skip for hackathon.** |
| EM-DAT (disaster events) | ⚠️ GraphQL + registration | Nice for pitch narrative, not for the pipeline |
| MeteoSerbia1km (Zenodo) | 🟡 offline CSV | Backup only if Open-Meteo dies |
| RHMZ / Digital Climate Atlas of Serbia | 🟡 no clean API | Use as credibility citation in slides |

### Soil

| Candidate | Status | Notes |
| --- | --- | --- |
| **SoilGrids** `rest.isric.org/soilgrids/v2.0/properties/query` | ✅ verified | pH, clay, sand, nitrogen, SOC. ISRIC calls it beta — **cache results.** |
| Kaggle soil sliders (current idea.md plan) | 🟡 fallback | Honest but fake; keep as "manual override" input |

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

After the 75 minutes, we each answer in one line:

- **A:** "Signal holds in N of 6 locations. Soil is live/cached. Projections agree/disagree."
- **B:** "Map click works via X. Crop model is usable/replaced. LLM output is specific/generic. GEV is in/out."

Then we decide together:
1. Map or dropdown?
2. Kaggle model or hand table?
3. Live APIs or committed `pins.json`?
4. GEV or Streamlit only?

**Default if we run out of time:** dropdown + hand table + `pins.json` + Streamlit. That combination has zero external dependencies at demo time and still tells the full story.

---

## 6. Build phase (after sync)

```
[+0:00] Wire A's JSON into B's UI (contract already agreed → should be minutes)
[+0:20] Decade comparison panel: the "rain flat, heat doubled" chart
[+0:40] Crop + action plan panel from LLM
[+1:00] Three scripted demo locations, screenshots taken
[+1:20] Fallback path tested with network off
[+1:30] Pitch script + 60s recording
```

---

## 7. Non-goals

Naming these so neither of us drifts:

- No leaf-disease vision module unless everything else is done.
- No user accounts, no persistence, no field polygon drawing.
- No claim that this is a forecast. We say **"climate model summary, illustrative"** on screen.
- No new model training beyond a RandomForest that fits in seconds.

---

## 8. Checklist

**Track A**
- [ ] A1 multi-location signal check
- [ ] A2 model-spread check
- [ ] A3 SoilGrids reliability + timing
- [ ] A4 dry streak / GDD indices
- [ ] A5 `data/pins.json` committed

**Track B**
- [ ] B1 map click or dropdown working
- [ ] B2 crop recommender sane for Serbia
- [ ] B3 LLM prompt producing specific advice
- [ ] B4 GEV in-or-out decision recorded

**Together**
- [ ] Sync + 4 decisions made
- [ ] End-to-end demo runs
- [ ] Offline fallback verified
- [ ] Pitch recorded
