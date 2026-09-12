### Project Concept: AgriSense — Climate-Adaptive Land Copilot

**One-liner:** Help a landowner (farmer or agri-corporation) understand what their plot has endured, what extremes are becoming more likely, and what to grow / prepare / schedule next — with Serbia as the demo geography.

**Concept Summary:**
AgriSense is a decision copilot for agricultural land under climate stress. The user picks (or draws) a field, reviews a local history of weather extremes (heatwaves, heavy rain / flood risk, drought), sees a simple 5–10 year outlook for temperature and moisture stress, and gets actionable recommendations: crop suitability, seed/variety direction, fertilizer and soil prep, and a revised seasonal work schedule.

This is **not** a full climate science platform. For the hackathon it is a **proof of concept**: real open weather/climate data + lightweight rules or tabular ML + an LLM that explains the plan in plain language. Optional 3D globe UX can reuse [God's Eye View](https://github.com/bilawalsidhu/gods-eye-view) as a spatial shell.

---

### Problem (user story)

> I own land in Serbia. Summers are getting hotter; some years bring heavy rain and waterlogging; other years drought. I need to know:
>
> 1. What extreme weather has already hit this area?
> 2. What is likely to get worse over the next 5–10 years (heat, rain extremes, soil moisture stress)?
> 3. Should I switch crops, order more heat-/flood-/drought-tolerant seeds, change fertilizer / soil prep, or reschedule field work?

**Primary users:** individual farmers, agronomists, small/medium agri-businesses planning multi-year land use.

**Demo locale:** Serbia (e.g. Vojvodina arable belt, Belgrade region, or a named municipality) — recent heat summers and flood/heavy-rain years make a convincing narrative for judges.

---

### Core Product Pillars

| Pillar | What the user sees | POC approach (keep it simple) |
| --- | --- | --- |
| **1. Extreme-weather memory** | Timeline of heat spikes, drought stretches, heavy-rain days for the plot | Open-Meteo Historical Weather API → compute annual indices (hot days >30°C, consecutive dry days, max daily precip, wet-day totals) |
| **2. Near-future climate stress** | “By ~2030–2035, expect more X / less Y” for this location | Open-Meteo Climate API (multi-model daily series to ~2050) → compare baseline decade vs next decade on the same indices |
| **3. Soil & crop fitness** | What grows well under current vs projected conditions; fertilizer hints | Crop Recommendation + Fertilizer datasets (tabular ML) fed with soil sliders *and* climate-adjusted temp/humidity/rainfall features |
| **4. Action plan** | Seeds / crop switch, soil prep, season calendar changes | LLM (x.ai Grok or similar) synthesizes pillars 1–3 into a short agronomist-style plan |
| **5. Spatial context (optional wow)** | Photorealistic globe, zoom to plot, overlay risk layers | Fork / embed God's Eye View Cesium globe + custom agri layers |

Optional stretch (only if time): leaf-disease photo check via Hugging Face PlantVillage models — useful for “today’s field health,” secondary to the climate story.

---

### Why Serbia works as the hackathon example

- Documented agricultural sensitivity to **heatwaves / drought** and **heavy precipitation / flooding**.
- Easy storytelling: “hot summer years vs flood years → what should a Vojvodina wheat/maize/soy grower prepare for?”
- Open global APIs cover Serbia coordinates with no special license negotiation.
- Local flavor for Belgrade judges: RHMZ agro bulletins, Digital Climate Atlas of Serbia (reference / narrative), MeteoSerbia1km research dataset (optional offline CSV if needed).

**Pitch disclaimer:** POC projections are illustrative climate-model summaries, not official forecasts or insurance advice.

---

### Recommended Architecture (hackathon-realistic)

```
[User: pick Serbia plot / lat-lon]
        │
        ▼
┌───────────────────┐     ┌────────────────────────────┐
│ Open-Meteo        │     │ Soil inputs (sliders)      │
│ Historical +      │     │ N,P,K,pH, moisture         │
│ Climate APIs      │     └─────────────┬──────────────┘
└─────────┬─────────┘                   │
          │ extremes + outlook          │
          ▼                             ▼
┌───────────────────┐     ┌────────────────────────────┐
│ Extreme-index     │     │ Crop / fertilizer ML       │
│ calculator        │     │ (RandomForest / lookup)    │
│ (Python, ~50 LOC) │     └─────────────┬──────────────┘
└─────────┬─────────┘                   │
          └──────────────┬──────────────┘
                         ▼
              ┌─────────────────────┐
              │ LLM synthesis       │
              │ (x.ai / LangChain)  │
              └──────────┬──────────┘
                         ▼
              Streamlit / Gradio UI
              OR God's Eye View panel on globe
```

**Backend / state (optional):** Convex for saved plots and live demo state.  
**Host:** Render for a public demo URL.  
**Research agents:** Exa + Firecrawl to pull Serbia flood/heat news or RHMZ summaries into the LLM context.  
**Design:** Wonder for UI polish if needed.  
**Media:** Fal.ai only if you want generated “future field” visuals for the pitch — not required for core POC.

---

### Integration: [God's Eye View](https://github.com/bilawalsidhu/gods-eye-view)

**What it is:** Open-source browser spatial intelligence app — CesiumJS + Vite + vanilla JS, photorealistic 3D globe, modular live data layers, optional voice agent. Starts **keyless** (Esri imagery); Google Maps / Cesium ion unlock better 3D.

**Why it fits AgriSense:** Land decisions are spatial. A globe zoomed to a Serbian field, with heat/flood risk overlays and a side panel for “what to grow,” looks far more demoable than charts alone.

**What to reuse (do not rebuild):**

| GEV piece | AgriSense use |
| --- | --- |
| Cesium globe + map stack | Show the user’s plot in context |
| Layer module pattern `src/data/<layer>.js` | Add `agriClimate.js`, `floodHeatIndex.js` |
| Click-to-track + metadata card | Click field → show extremes + crop plan |
| Voice tools (optional) | “Show drought risk for Novi Sad” |
| FIRMS / environmental layers (existing) | Bonus fire / environmental context |

**How to integrate without drowning in the codebase:**

1. **Fast path (recommended for ≤1 day):** Keep AgriSense as a **Streamlit/Gradio app**. Use GEV only as inspiration / pitch visual, or iframe a local GEV instance pointed at Serbia coordinates via share-link params if available.
2. **Medium path (best wow):** Fork GEV → disable irrelevant layers (flights, AIS, CCTV) → add 1–2 agri layers that fetch Open-Meteo for the clicked lat/lon → open a HUD panel that calls your Python/FastAPI crop+LLM service.
3. **Hard path (avoid in hackathon):** Full multi-agent CrewAI + custom Cesium from scratch. Not worth it.

**GEV setup (from upstream README):**

```bash
git clone https://github.com/bilawalsidhu/gods-eye-view.git
cd gods-eye-view
# Node 24.14+ or 26.x
npm ci
npm run doctor
npm run dev
# → http://localhost:4173
```

**Custom layer sketch (conceptual):** implement `init / enable / disable / update / destroy` in `src/data/agriClimate.js`, fetch Open-Meteo for viewport center or click point, color-code entities by heat/flood index, register attribution in `DATA_SOURCES.md` / credits. Follow upstream CONTRIBUTING.md layer interface.

**Keys (only if you want photorealism):** Cesium ion (often free for eligible personal/non-commercial) and/or Google Maps; keep secrets in `.env` / POWER UP panel — do not commit keys.

---

### Data & Models Inventory

#### A. Climate / extremes (primary for the new story)

| Source | Role | Notes |
| --- | --- | --- |
| **Open-Meteo Historical** (`archive-api.open-meteo.com`) | Past heat, rain, soil moisture proxies | Free, no key, ERA5/ERA5-Land; daily max/min temp, precip, etc. |
| **Open-Meteo Climate API** | 1950–2050 multi-model outlook | Perfect for “next decade vs baseline” POC |
| **Open-Meteo Forecast** | Short-term schedule tweaks | Optional “this week’s field ops” |
| Digital Climate Atlas of Serbia / RHMZ | Narrative + credibility in pitch | May not be a clean REST API — use Exa/Firecrawl or cite screenshots |
| MeteoSerbia1km (Zenodo) | Offline Serbia grid 2000–2019 | Only if you want a canned CSV demo without live API |

**POC extreme indices (easy to code):**

- Hot days: count of days with `temperature_2m_max >= 30` (or 35)
- Heatwave proxy: longest streak of hot days
- Drought proxy: max consecutive days with `precipitation_sum < 1 mm`
- Flood / heavy-rain proxy: annual max `precipitation_sum`, or days > 40 mm
- Soil stress proxy: rising summer mean temp + falling precip (or ET0 if available)

#### B. Crop / soil (keep from earlier plan)

| Dataset | Source | Hackathon use |
| --- | --- | --- |
| Crop Recommendation | Kaggle `atharvaingle/crop-recommendation-dataset` | Random Forest in under 1 min; feed climate-adjusted features |
| Fertilizer Prediction | Kaggle `godeep48/fertilizer-prediction` | Lookup / light classifier |
| PlantVillage + HF ViT/MobileNet | HF hubs | Optional disease photo module |

#### C. Pre-trained / frameworks

- Vision: `nateraw/vit-base-patch16-224-plant-village` or MobileNet plant-disease pipeline
- Agents: `google-genai` / LangChain / x.ai API (hackathon partner)
- UI: Streamlit or Gradio first; GEV second
- Orchestration: skip CrewAI unless multi-agent is a judging criterion

---

### Proof-of-Concept Algorithm (explicitly simple)

Goal: **credible demo in hours**, not a research paper.

1. **Input:** lat/lon in Serbia (preset pins: Novi Sad, Subotica, Niš, …) + optional soil NPK/pH/moisture sliders.
2. **History pull:** Open-Meteo archive daily series for last ~20–40 years.
3. **Score history:** compute yearly extreme indices; chart “heat years” vs “wet years.”
4. **Outlook pull:** Open-Meteo Climate API for same point; compare mean indices for e.g. 1995–2014 vs 2025–2040 (or 2030s decade).
5. **Map to agronomy features:** derive effective `temperature`, `humidity`, `rainfall` for the crop model from outlook (rules of thumb are fine).
6. **Crop model:** Random Forest → top-3 crops under *current* vs *projected* climate; flag “switch recommended” if ranking changes.
7. **LLM plan:** prompt with JSON of indices + crops → output:
   - risks to expect
   - keep / switch crop
   - seed trait guidance (heat-, drought-, or flood-tolerant — qualitative, not a seed SKU DB)
   - soil / fertilizer notes
   - calendar shifts (earlier sowing, drainage, irrigation windows)
8. **UI:** one page — map or pin picker, charts, recommendation card, “Ask Grok” explanation.

**Out of scope for POC:** true soil physics, insurance pricing, satellite NDVI pipelines, training foundation models, multi-country coverage.

---

### Hackathon Execution Plan (lean)

Prefer a **half-day core** + optional GEV polish rather than the old 3-hour leaf-disease-only plan.

```
[0:00–0:45] Setup
 ├── Streamlit app skeleton + Serbia preset coordinates
 ├── Smoke-test Open-Meteo Historical + Climate for one lat/lon
 └── (Optional) Clone God's Eye View; confirm npm run dev

[0:45–2:00] Climate memory + outlook
 ├── Extreme-index functions + simple charts (Plotly/Altair)
 ├── Decade comparison card (past vs projected)
 └── Wire soil sliders → Random Forest crop recommender

[2:00–3:00] LLM action plan + polish
 ├── Prompt template: extremes + outlook + crop ranks → plan
 ├── 3 demo scenarios (heat-prone north / wet year narrative / crop switch)
 └── Pitch script + 60s screen recording

[Stretch] GEV fork
 ├── Hide non-agri layers
 ├── Click Serbia → call backend for indices
 └── Show recommendation HUD
```

---

### Demo Scenarios (Serbia)

1. **Heat summer stress (Vojvodina):** rising hot-day counts → maize/soy heat risk → suggest drought-/heat-tolerant variety direction + irrigation schedule shift.
2. **Heavy-rain / flood memory:** spikes in max daily precip → drainage, delayed tillage, avoid waterlogging-sensitive crops in low parcels.
3. **Crop switch signal:** current top crop ≠ projected top crop → “prepare seed orders and rotation for the next 2–3 seasons.”

---

### Hackathon Tech Partners Map (`TECH_PARTNERS.md`)

| Partner | Use in AgriSense |
| --- | --- |
| **x.ai** | LLM agronomist voice / synthesis |
| **Firecrawl** | Pull clean text from RHMZ / news pages about Serbian floods & heat |
| **Exa** | Find relevant climate/agri sources for the agent |
| **Convex** | Save plots, share demo state |
| **Render** | Public demo URL |
| **Wonder** | Fast React+Tailwind UI if not staying on Streamlit |
| **Daytona** | Isolated runs for agent/code experiments |
| **Fal.ai** | Optional pitch visuals |
| **Grok Bot / Cursor** | Build speed |
| **Wispr Flow** | Dictate while building |

---

### Success Criteria for Judging

- [ ] User can select a Serbian location and see **past extremes** in under 10 seconds.
- [ ] User sees a **clear 5–10 year stress narrative** (more heat / more intense rain / drier summers — whatever the data shows for that point).
- [ ] System proposes **concrete land actions** (crop/seed direction, soil prep, calendar).
- [ ] Story is coherent: memory → outlook → decision.
- [ ] (Bonus) Globe / God's Eye View makes the land feel real.

---

### Legacy notes (still useful, deprioritized)

Earlier MVP ideas remain valid as modules:

1. **Soil & Telemetry Analysis** — NPK/pH/humidity → crop suitability + fertilizer.
2. **Vision Pathology** — leaf disease classification from uploads.
3. **Agentic Synthesis** — LLM merges tabular + vision (+ now climate extremes).

For Belgrade 2026, **lead with climate-adaptive land planning**; treat leaf disease as a secondary “today’s crop health” add-on if time remains.
