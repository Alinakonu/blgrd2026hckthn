# AgriSense — 5-minute hackathon demo

Spoken English script, screen plan, and data cheat sheet. All figures come from `data/pins.json` (ERA5 via [Open-Meteo](https://open-meteo.com/en/docs/historical-weather-api), 1985–1994 vs 2015–2024) and the FAO crop table in `agrisense/crops.py`. If a judge asks “where did that number come from,” the answer is always one of those two files — with [source links in §10](#10-open-data-sources-and-linked-pipeline).

**Also in this file:** [open data + live URLs](#10-open-data-sources-and-linked-pipeline) · [how to evaluate a serious version](#11-how-to-evaluate-this-for-something-more-serious) · [heavier models vs disaster prediction](#12-heavier-models-climate-change-vs-weather-disasters).

**Timing:** ~750 spoken words plus clicks. Practise once with a timer. If you overrun, cut the Kraljevo aside and the architecture sentence — never cut the Novi Sad / Zrenjanin / Niš contrast.

---

## 1. Problem definition

A Serbian landowner (farmer or agri-business) can already see that summers feel hotter. What they cannot see, from a rain gauge or an annual climate chart, is whether **this specific plot** is getting harder to farm — and what to change before the next seed order.

Three questions they actually need answered:

1. What extreme weather has already hit this field?
2. Is the growing season getting drier even when the year looks wetter?
3. Should I keep maize, change variety, shift irrigation, or leave the rotation alone?

**The trap we found in the data:** annual rainfall at four of six Serbian pins **rose**. At Novi Sad it looks almost unchanged (599 → 609 mm). A farmer reading yearly totals concludes nothing is wrong. Meanwhile June–August rainfall fell, crop water demand (FAO ET0) rose everywhere, and the summer water deficit in Vojvodina worsened by 26–57 mm.

That is the product: not “climate is getting worse,” which is both too coarse and, in the south, not even true. It is a **plot-level copilot** that compares two decades, scores the crops actually planted in Serbia, and turns the numbers into a seasonal action plan.

**One-liner:** AgriSense shows a landowner what their field has endured, whether the growing season is drying out, and what to grow or change next — for this plot, not for the country.

**Disclaimer to say once, out loud:** these are measured climate indices and a multi-model range, not an official forecast and not insurance advice.

---

## 2. Five-minute rundown

| Clock | Section | On screen | You do |
| --- | --- | --- | --- |
| 0:00–0:40 | Hook + problem | Title / map of six pins | Speak, no clicking |
| 0:40–1:20 | The finding | Novi Sad: annual rain vs summer water balance | Point at the two numbers |
| 1:20–2:20 | Demo 1 — Novi Sad | Water-balance chart + maize exposure | Click Novi Sad |
| 2:20–3:10 | Demo 2 — Zrenjanin | Heat + worst deficit | Click Zrenjanin |
| 3:10–3:50 | Demo 3 — Niš | “No change indicated” | Click Niš |
| 3:50–4:25 | How it works | Crop table + Grok plan | Show one advice card |
| 4:25–5:00 | Close | Six-pin map again | Ask + disclaimer |

If the UI is not ready, use this file’s tables as slides. The argument does not need a live map.

---

## 3. Spoken script (~5 minutes)

Read this as written. Bracketed lines are stage directions, not speech.

### 0:00–0:40 — Hook

Imagine you farm around Novi Sad. Your rain gauge says the year was fine. Annual rainfall is basically the same as it was thirty years ago: six hundred millimetres then, six hundred and nine now. So you keep ordering the same maize seed, on the same calendar.

That number is lying to you.

We built AgriSense: a climate-adaptive land copilot. You pick a plot in Serbia. We show what that plot has actually been through, whether the *growing season* is drying out, and what to do next — crop, irrigation, calendar — in plain language.

### 0:40–1:20 — The finding

[Stay on Novi Sad. Point at annual rainfall, then at the summer panel.]

The trick is the growing-season water balance: June to August rainfall minus ET0, the FAO measure of how much water a crop demands. Rainfall over the whole year can rise because of wet springs and autumns, while summer — when maize, sunflower and soybean actually need the water — gets worse.

At Novi Sad, summer rain fell from 187 to 158 millimetres. Demand rose from 428 to 456. The deficit went from minus 241 to **minus 298**. Fifty-seven millimetres more stress, hidden inside a “stable” year.

We measured this at six points across Serbia. Crop water demand rose at **all six**. Extreme heat rose at all six. The summer deficit only worsened in the north — Vojvodina, the breadbasket. Belgrade and Niš are stable or slightly better. So the answer depends on your field. That is why a national headline is useless, and a plot tool is not.

### 1:20–2:20 — Demo: Novi Sad (the mask)

[Click Novi Sad. Show rainfall-versus-ET0 chart, then the crop table.]

This is the default demo. Annual rain: 599 to 609 millimetres — looks fine. Days at or above 35 °C: 3.5 to 6.6. Growing degree days up 10 percent, so longer-maturity varieties are now viable — that is the opportunity sitting next to the risk.

Maize is Serbia’s largest crop: about 939 thousand hectares nationally, 501 thousand in Vojvodina. It is also the most exposed. Its peak demand is June to August, exactly the window that deteriorated. The irrigation gap — crop demand minus summer rain — widened from 327 to 389 millimetres. Exposure score 2.48, the worst in the set.

Winter wheat? Largely stable. It fills grain in May and is off the field by early July, so a worse July–August barely reaches it. Same climate, different crop, different decision. That is the point of scoring crops with FAO coefficients instead of a generic “plant something else” model.

[If the Grok card is on screen:] The action plan is written by Grok from these numbers. It is not allowed to invent yields, prices, or seed brand names. If a figure appears, it came from the data.

### 2:20–3:10 — Demo: Zrenjanin (the worst case)

[Click Zrenjanin.]

Banat is the hard case. Days at or above 35 °C went from **2.7 to 8.0** — almost a tripling. Hot days over 30 °C: 28 to 41. Summer deficit: minus 260 to **minus 312**. Maize irrigation gap 346 to 406 millimetres.

If you only have time for one emotional number, use this: eight days a year at 35 degrees, where there used to be three. That is not a vibe. That is ERA5, same method, two decades.

Outlook for the 2030s is a **range across three climate models**, not a single forecast: 46 to 55 days above 30 °C. They agree on direction. They disagree on how far. We print the spread on purpose. False precision would be easier to pitch and wrong.

### 3:10–3:50 — Demo: Niš (the counter-example)

[Click Niš. If anyone looks sceptical, this is the slide that earns trust.]

If the tool shouted “crisis” on every pin, you should not believe it. Niš is why we do not.

Annual rainfall **rose** from 521 to 682 millimetres. Summer rain rose too. The summer deficit **eased** from minus 287 to minus 270. Maize exposure is negative — conditions improved. The verdict is **no change indicated**. Keep the rotation; do not spend money adapting to a problem this plot does not have.

Belgrade is the same story on water: deficit flat at minus 239 / minus 240, even though it got hotter. Heat is up; thirst is not. Different advice, fifty kilometres from Zrenjanin.

### 3:50–4:25 — What you are looking at

Under the hood, three pieces, all local to the plot, all from [open data](#10-open-data-sources-and-linked-pipeline):

1. **Memory** — [Open-Meteo Historical](https://open-meteo.com/en/docs/historical-weather-api) serving [ERA5](https://cds.climate.copernicus.eu/datasets/reanalysis-era5-single-levels) daily data, reduced to farmer indices: hot days, dry spells, summer rain, ET0, soil moisture.
2. **Exposure** — [FAO-56](https://www.fao.org/4/x0490e/x0490e00.htm) crop water requirement (`ETc = Kc × ET0`) on Serbia’s real crops: maize, wheat, sunflower, soybean, sugar beet, with coefficients from [FAO Training Manual 3](https://www.fao.org/4/s2022e/s2022e07.htm) and area from the [Statistical Office of Serbia](https://publikacije.stat.gov.rs/G2026/HtmlE/G20261171.html). We dropped the usual Kaggle crop model because it recommends mango and has no wheat.
3. **Plan** — Grok explains and sequences the measured numbers. It does not generate them.

Soil chemistry from SoilGrids is down for Europe right now, so we do not fake NPK. We show ERA5 summer soil moisture instead, and we say “not available” when we do not have a layer. The demo also runs offline from a committed JSON file, because a live rebuild takes up to two minutes per point.

### 4:25–5:00 — Close

So the pitch is not “AI for farms.” It is: **your annual rain gauge can hide a worse summer, and the right response is different in Novi Sad, Zrenjanin, and Niš.**

AgriSense makes that visible in one screen, names the crop that is actually at risk — maize, on half a million hectares in Vojvodina — and turns it into this season’s work: irrigation windows, variety direction, what not to panic about.

We are not issuing forecasts. We are translating two decades of reanalysis, plus a model range for the 2030s, into a decision a landowner can act on.

Happy to take questions — including “show me Belgrade” if you want a fourth pin.

---

## 4. The three demo examples (what to show, what to say)

Run them in this order. The contrast is the product.

### Example A — Novi Sad: “Nothing looks wrong”

| | 1985–1994 | 2015–2024 | Line to say |
| --- | --- | --- | --- |
| Annual rainfall | 599 mm | 609 mm | “Stable. The rain gauge is calm.” |
| Summer rain (Jun–Aug) | 187 mm | 158 mm | “The growing season lost 29 mm.” |
| Summer ET0 (demand) | 428 mm | 456 mm | “Crops asked for 28 mm more.” |
| Summer water balance | −241 mm | **−298 mm** | “Fifty-seven millimetres worse.” |
| Days ≥30 °C | 29.4 | 38.1 | |
| Days ≥35 °C | 3.5 | 6.6 | |
| GDD (Apr–Sep, base 10 °C) | 1679 | 1847 (+10%) | “Longer-maturity varieties now viable.” |
| Maize irrigation gap | 327 mm | 389 mm (+62) | “Highest exposure: 2.48.” |
| Wheat | | exposure 0.41, stable | “Harvested before the bad window.” |
| 2031–2040 days ≥30 °C | | **44–57** (3 models) | “Range, not a forecast.” |

**Signals on screen:** heat intensifying · annual rainfall stable · crop water demand rising · summer deficit worsening · **annual totals masking summer stress**.

**Advice shape (what Grok should say):** maize is the priority; wheat is not; time irrigation to June–August; consider shorter-maturity *or* heat-tolerant maize practice (no brand names); sorghum is the low-sensitivity adaptation candidate, not a command to replant the farm.

### Example B — Zrenjanin: worst heat + worst thirst

| | 1985–1994 | 2015–2024 | Line to say |
| --- | --- | --- | --- |
| Days ≥35 °C | **2.7** | **8.0** | “Nearly triple.” |
| Days ≥30 °C | 28.1 | 40.5 | |
| Annual rainfall | 564 mm | 597 mm | “Looks slightly wetter.” |
| Summer water balance | −260 mm | **−312 mm** | “Worst deficit in the set.” |
| Summer ET0 | 430 mm | 471 mm | “Biggest demand jump: +41 mm.” |
| Maize irrigation gap | 346 mm | 406 mm (+60) | Exposure **2.40**, high |
| 2031–2040 days ≥30 °C | | 46–55 | |

Use this pin if a judge asks “what is the most urgent field?” Do not skip Niš afterwards — otherwise it sounds like a doom dashboard.

### Example C — Niš: the trust slide

| | 1985–1994 | 2015–2024 | Line to say |
| --- | --- | --- | --- |
| Annual rainfall | 521 mm | **682 mm** | “Clearly wetter.” |
| Summer rain | 132 mm | 164 mm | |
| Summer water balance | −287 mm | **−270 mm** | “Slightly *better*.” |
| Days ≥30 °C | 35.3 | 40.1 | “Heat is not the story here.” |
| Maize gap | 371 mm | 357 mm (−14) | Exposure **−0.56**, improving |
| Verdict | | **no change indicated** | “Do not spend on a problem you do not have.” |

**Backup fourth pin — Belgrade:** summer balance −239 → −240 (flat). Heat up (26.7 → 36.0 days ≥30 °C; 2.5 → 5.1 days ≥35 °C). Annual rain 598 → 708. Crop table all **stable**. Use if someone in the room is from Belgrade.

**Do not lead with Subotica** unless asked. Annual rain *rose* 547 → 606 while the summer deficit still worsened (−278 → −304). Good supporting evidence for “totals mask stress,” but weaker theatre than Novi Sad.

---

## 5. Data-point cheat sheet (memorise the bold ones)

### Universal signals (6 / 6 pins)

- **ET0 (crop water demand) rose everywhere** in summer: +15 to **+41 mm** (Niš smallest, Zrenjanin largest).
- **Heat rose everywhere.** Growing degree days up 51–190. Days ≥35 °C up at every pin.
- We do **not** claim dry spells are lengthening. After fixing a methodology bug, Subotica is 27.4 → 26.1 days — flat. Do not quote the old “60-day drought.”

### The mask (3 / 6 pins — all Vojvodina / north)

| Location | Annual rain | Summer balance | Mask? |
| --- | --- | --- | --- |
| **Novi Sad** | 599 → 609 “stable” | −241 → **−298** | Yes, −57 mm |
| **Zrenjanin** | 564 → 597 “stable” | −260 → **−312** | Yes, −52 mm |
| **Subotica** | 547 → 606 “improving” | −278 → **−304** | Yes, −26 mm |
| Belgrade | 598 → 708 | −239 → −240 | No |
| Kraljevo | 661 → 772 | −190 → −208 | No (within stable band) |
| **Niš** | 521 → 682 | −287 → **−270** | No — improved |

### Crop economics (why maize, why not mango)

From the Republic Statistical Office of Serbia, 2026 release:

| Crop | Serbia ha | Vojvodina ha | FAO drought sensitivity | Summer overlap | Novi Sad exposure |
| --- | --- | --- | --- | --- | --- |
| Maize | 938,209 | 500,759 | medium-high | 1.00 | **2.48** |
| Wheat | 626,282 | 305,412 | low-medium | 0.33 | 0.41 (stable) |
| Sunflower | 250,816 | 220,139 | low-medium | 1.00 | 1.22 |
| Soybean | 193,731 | 172,117 | low-medium | 1.00 | 1.20 |
| Sugar beet | 32,432 | 31,539 | low-medium | 0.75 | 0.92 |
| Sorghum | ~0 | ~0 | **low** | 1.00 | 0.60 (candidate) |

One sentence if asked why wheat is “fine”: *wheat’s moisture-sensitive window is April–June; only a third of it sits in the deteriorating summer, so the same millimetres barely score.*

### Outlook — always a range

Three CMIP6 models via Open-Meteo Climate: MRI-AGCM3-2-S, EC-Earth3P-HR, MPI-ESM1-2-XR. Period **2031–2040**.

| Location | Days ≥30 °C, model range |
| --- | --- |
| Novi Sad | **44.2 – 56.9** |
| Zrenjanin | 45.6 – 55.2 |
| Belgrade | 42.1 – 52.7 |
| Kraljevo | 37.7 – 46.6 |
| Niš | 49.6 – 56.5 |

Never say “52 days.” Say “the models put it between 44 and 57.”

### Sources, if asked

Full table and clickable pipeline: [§10](#10-open-data-sources-and-linked-pipeline). One-line version:

- History: [Open-Meteo Archive](https://open-meteo.com/en/docs/historical-weather-api) → [ERA5](https://cds.climate.copernicus.eu/datasets/reanalysis-era5-single-levels).
- Outlook: [Open-Meteo Climate API](https://open-meteo.com/en/docs/climate-api) (three [CMIP6](https://wcrp-cmip.org/cmip-phase-6-cmip6/) models), labelled *illustrative, not a forecast*.
- Crop water: [FAO-56](https://www.fao.org/4/x0490e/x0490e00.htm) method + [Training Manual 3, Tables 12 and 14](https://www.fao.org/4/s2022e/s2022e07.htm).
- Area: [RZS G20261171](https://publikacije.stat.gov.rs/G2026/HtmlE/G20261171.html) (23 May 2026).
- Soil: [SoilGrids REST](https://rest.isric.org/soilgrids/v2.0/properties/query) is [paused](https://docs.isric.org/globaldata/soilgrids/); we use ERA5 moisture instead.
- Yields: [FAOSTAT](https://www.fao.org/faostat/) was down (HTTP 521). We do not show a yield chart we cannot back.

---

## 6. Screen / slide plan (7 beats)

Keep slides sparse. Prefer the live app; these are the beats if you need a deck.

1. **Title** — AgriSense. Climate-adaptive land copilot. Serbia, plot by plot.
2. **The farmer’s question** — three bullets from section 1. Photo or map of Vojvodina fields, not a globe.
3. **The lie of annual rain** — Novi Sad 599 → 609 vs summer −241 → −298. This is the only slide that must be beautiful.
4. **Live: Novi Sad** — chart + maize vs wheat.
5. **Live: Zrenjanin** — 2.7 → 8.0 days ≥35 °C.
6. **Live: Niš** — no change indicated.
7. **Close** — six pins, north deteriorating / south stable; Grok writes the plan from measured numbers.

Do not open with a 3D globe. The finding is a time series. A globe cannot show rainfall versus ET0.

---

## 7. Likely questions (short answers)

**Is this a forecast?** No. History is ERA5 reanalysis. The 2030s panel is a three-model range, on-screen as illustrative.

**Why should I trust the crop list?** We use Serbia’s planted area and FAO coefficients. A popular Kaggle dataset would have recommended mango. We threw it out.

**Why only six points?** Proof of concept, and a full live rebuild is 33–114 seconds per point because of API rate limits. The method is `build_pin(lat, lon)` for any field; the demo reads cached pins so it never stalls on stage.

**Can I click an arbitrary field?** Technically yes, with a spinner. For the five-minute slot, use the three scripted pins. Offer a fourth if there is time.

**What about soil tests?** SoilGrids is returning nulls for Europe. We show that honestly and use ERA5 soil moisture. Farmer NPK sliders are inputs, not claimed measurements.

**Does Grok hallucinate?** The prompt forbids invented numbers and variety names. Every figure in the card should appear in `pins.json` or `crops.py`. If you see a hybrid name like “NS-640,” that is a bug, not a feature.

**Sorghum — are you telling Serbian farmers to rip out maize?** No. It is the FAO low-sensitivity comparison so exposure is interpretable. The practical advice is irrigation timing, heat-tolerant *practice*, and not treating wheat as the same risk.

**Did you train a model?** No new climate model. Indices from reanalysis; a small FAO scoring function; an LLM that only explains.

**Can you predict next year’s flood or a 2035 heatwave to the day?** No. Climate ensembles change *how often* extremes occur; they do not timestamp disasters. Weather models (days) and seasonal models (months) are a different stack — see [§12](#12-heavier-models-climate-change-vs-weather-disasters).

---

## 8. Rehearsal notes

- **Memorise five numbers:** Novi Sad 599→609 vs −241→−298; Zrenjanin 2.7→8.0; maize 501k ha; Niš “no change”; outlook 44–57 days.
- **Speak slower on the water-balance sentence.** That is the insight. Pause after “the rain gauge is lying.”
- **Click Niš even if time is tight.** Without the counter-example the pitch sounds like generic climate alarm.
- **If the app dies:** open `python scripts/preview_advice.py "Novi Sad"` on a terminal, then this file’s tables. The story still stands.
- **Sponsor credit, one clause only:** built with Grok / x.ai for the agronomist write-up, Open-Meteo for climate. Do not tour every partner logo.
- **Words to avoid:** prediction, guaranteed yield, insurance, “the model says plant sorghum,” any commercial hybrid name.

### 60-second emergency cut

If the slot collapses to one minute:

> Annual rainfall at Novi Sad looks unchanged. The growing-season water deficit is 57 millimetres worse. That is the difference between a calm rain gauge and a thirstier maize crop on 500 thousand hectares in Vojvodina. We show that per plot — Zrenjanin is the urgent case, Niš is not — and Grok turns the measured numbers into this season’s work. Not a forecast. A decision.

---

## 9. Team roles on stage (suggested)

| Role | Owns |
| --- | --- |
| Speaker | This script. Stands slightly aside so the screen is readable. |
| Driver | Clicks Novi Sad → Zrenjanin → Niš. Does not ad-lib. Preloads all three so the first click is instant. |
| Backup | `pins.json` + this file on a second laptop, network off. |

Practise the three clicks the night before with the network unplugged. If that run works, the demo works.

---

## 10. Open data sources and linked pipeline

Every step below is something a judge can open in a browser. Code lives in `agrisense/climate.py`, `agrisense/crops.py`, and `agrisense/prompt.py`. Cached output is `data/pins.json`.

### Pipeline with links

```
1. Pick a plot (lat/lon)
        │
        ▼
2. Historical climate ──────────────────────────────────────────────┐
   Open-Meteo Historical API                                        │
   https://open-meteo.com/en/docs/historical-weather-api            │
   Endpoint: https://archive-api.open-meteo.com/v1/archive          │
   Underlying: ECMWF ERA5 (Copernicus CDS)                          │
   https://cds.climate.copernicus.eu/datasets/reanalysis-era5-single-levels
        │                                                           │
        ▼                                                           │
3. Compute farmer indices  (hot days, ET0, summer water balance)    │
   ET0 definition: FAO-56 Penman–Monteith                           │
   https://www.fao.org/4/x0490e/x0490e00.htm                        │
        │                                                           │
        ├───────────────────────────────────────────────────────────┘
        ▼
4. Climate outlook (2031–2040), three models, as a range
   Open-Meteo Climate API
   https://open-meteo.com/en/docs/climate-api
   Endpoint: https://climate-api.open-meteo.com/v1/climate
   Models (CMIP6 HighResMIP, downscaled & bias-corrected to ERA5):
     MRI-AGCM3-2-S   https://open-meteo.com/en/docs/climate-api
     EC-Earth3P-HR   https://ec-earth.org/
     MPI-ESM1-2-XR   https://mpimet.mpg.de/en/science/models
   CMIP6 overview: https://wcrp-cmip.org/cmip-phase-6-cmip6/
        │
        ▼
5. Crop exposure  ETc = Kc × ET0  −  summer rain
   Method: FAO-56  https://www.fao.org/4/x0490e/x0490e00.htm
   Kc, seasonal need, drought sensitivity:
   FAO Irrigation Water Management Training Manual 3, Ch. 3
   https://www.fao.org/4/s2022e/s2022e07.htm   (Tables 12 and 14)
   Irrigation need formula: https://www.fao.org/4/s2022e/s2022e08.htm
        │
        ▼
6. Weight by what Serbia actually plants
   Statistical Office of the Republic of Serbia, release G20261171
   (sown area as of 23 May 2026)
   https://publikacije.stat.gov.rs/G2026/HtmlE/G20261171.html
        │
        ▼
7. Action plan (explains numbers, does not invent them)
   Prompt: agrisense/prompt.py  →  x.ai / Grok
   https://docs.x.ai/
```

**Tried and not in the demo (honest gaps):**

| Source | Why we wanted it | What happened | Link |
| --- | --- | --- | --- |
| SoilGrids 2.0 | Clay, pH, SOC per point | REST returns HTTP 200 with `null` for Serbia (and NL); Iowa works. ISRIC has paused the API. | [Docs](https://docs.isric.org/globaldata/soilgrids/) · [REST](https://rest.isric.org/soilgrids/v2.0/properties/query) |
| FAOSTAT QCL | Serbian yield history | HTTP 521 from the API | [FAOSTAT](https://www.fao.org/faostat/) · [API](https://fenixservices.fao.org/faostat/api/v1/en/data/QCL) |
| Digital Climate Atlas of Serbia | Local credibility with judges | No clean REST for our pipeline; cite in the pitch | [Atlas](https://atlas-klime.eko.gov.rs/) · [about](https://atlas-klime.eko.gov.rs/lat/about) |
| RHMZ | Official station / agro bulletins | Same — narrative, not wired | [hidmet.gov.rs](https://www.hidmet.gov.rs/) |
| MeteoSerbia1km | 1 km daily grid 2000–2019 | Offline CSV/GeoTIFF; skipped once `pins.json` existed | [Zenodo](https://zenodo.org/records/4058167) · [paper](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8087659/) |

Licence note: Open-Meteo data is [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Credit Open-Meteo **and** the underlying models (ERA5 / Copernicus, CMIP6 centres). FAO manuals and RZS tables are cited, not copied wholesale.

### Live check URLs (Novi Sad, 45.2671, 19.8335)

Paste these if a judge wants to see the raw feed. They are the same calls `climate.py` makes.

- **Recent decade (ERA5 daily):**  
  [archive-api … 2015–2024](https://archive-api.open-meteo.com/v1/archive?latitude=45.2671&longitude=19.8335&start_date=2015-01-01&end_date=2024-12-31&daily=temperature_2m_max,precipitation_sum,et0_fao_evapotranspiration_sum,soil_moisture_0_to_7cm_mean&timezone=Europe%2FBelgrade)
- **One climate model, 2030s:**  
  [climate-api … MRI_AGCM3_2_S 2031–2040](https://climate-api.open-meteo.com/v1/climate?latitude=45.2671&longitude=19.8335&start_date=2031-01-01&end_date=2040-12-31&models=MRI_AGCM3_2_S&daily=temperature_2m_max,precipitation_sum,et0_fao_evapotranspiration_sum)
- **FAO crop-need chapter (maize 500–800 mm, medium-high drought sensitivity):**  
  [fao.org/4/s2022e/s2022e07.htm](https://www.fao.org/4/s2022e/s2022e07.htm)
- **RZS maize 500,759 ha in Vojvodina:**  
  [G20261171](https://publikacije.stat.gov.rs/G2026/HtmlE/G20261171.html)

### What each source is allowed to claim

| Layer | Source | We may say | We may not say |
| --- | --- | --- | --- |
| 1985–1994 vs 2015–2024 | ERA5 via Open-Meteo | “Measured / reanalysis indices at this point” | “Official RHMZ observation” (ERA5 is a model–observation blend at ~25 km) |
| 2031–2040 | 3 CMIP6 models | “Model range, illustrative” | “Forecast”, a single day count, a named disaster |
| Crop thirst | FAO Kc × our ET0 | “Irrigation gap widened by N mm” | “Yield will fall X%” |
| Area | RZS 2026 | “Maize is the largest sown crop” | “This farmer plants N hectares” |
| Advice text | Grok | “Interpretation of the block above” | Invented hybrids, prices, yields |

### Local / national sources to add if this becomes a real product

These are the credibility upgrades for a Serbian deployment. Not used in the POC.

| Dataset | Role | Link |
| --- | --- | --- |
| Digital Climate Atlas of Serbia | Official CORDEX + Copernicus + RHMZ maps for adaptation planning | [atlas-klime.eko.gov.rs](https://atlas-klime.eko.gov.rs/) |
| RHMZ | Station observations, agro bulletins, warnings | [hidmet.gov.rs](https://www.hidmet.gov.rs/) |
| MeteoSerbia1km | 1 km daily T/precip 2000–2019, better than ERA5 locally | [doi:10.5281/zenodo.4058167](https://doi.org/10.5281/zenodo.4058167) |
| EURO-CORDEX | Regional climate at ~12 km over Europe | [euro-cordex.net](https://www.euro-cordex.net/) |
| Copernicus AgERA5 | ERA5 on a 0.1° grid with FAO-56 ET0 already computed | [CDS AgERA5](https://cds.climate.copernicus.eu/datasets/sis-agrometeorological-indicators) |
| Eurostat `apro_cpsh1` | Harmonised crop statistics if FAOSTAT stays down | [Eurostat](https://ec.europa.eu/eurostat/databrowser/view/apro_cpsh1/) |
| DBnomics | Convenience API over Eurostat / others | [db.nomics.world](https://db.nomics.world/) |
| EFAS / GloFAS | Operational flood outlook for Europe / globe | [efas.eu](https://www.efas.eu/) · [globalfloods.eu](https://www.globalfloods.eu/) |
| EM-DAT | Historical disaster catalogue (narrative + validation, not a live feed) | [emdat.be](https://www.emdat.be/) |
| Copernicus Emergency | Flood/fire maps after events | [emergency.copernicus.eu](https://emergency.copernicus.eu/) |

---

## 11. How to evaluate this for something more serious

The hackathon proves **a signal exists and is plot-specific**. A serious product has to prove **skill, calibration, and that a farmer would change a decision**. Do not start by training a bigger model. Start by measuring whether the current indices are right.

### What “good” means (in order)

1. **The history is close to the truth** at Serbian stations, not just internally consistent.
2. **The water-balance change lines up with yields** in the same districts.
3. **The outlook is calibrated** (ranges cover outcomes as often as they claim).
4. **The crop ranking matches agronomists**, not Kaggle labels.
5. **The LLM never adds a number** that is not in the data block.
6. **A user changes a real action** (seed order, irrigation week, insurance) — not just nods at a chart.

### Evaluation plan

| Gate | Method | Pass / fail | Data |
| --- | --- | --- | --- |
| **E1. Station check** | Compare our ERA5 indices (Tmax≥30/35, precip, ET0) to RHMZ stations at/near the six pins, 2015–2024. Report bias and MAE. | Hot-day counts within ~15%; summer rain bias stated, not hidden | [RHMZ](https://www.hidmet.gov.rs/), optionally [E-OBS](https://www.ecad.eu/download/ensembles/download.php), [MeteoSerbia1km](https://zenodo.org/records/4058167) |
| **E2. Spatial density** | Rebuild the same indices on a 10–25 km grid over Serbia (or all municipalities), not six cities. Map “masking” vs “stable”. | North/south split still holds; no one district flips the story | Same Open-Meteo / AgERA5 calls, batched offline |
| **E3. Yield link** | Correlate decade change in summer water balance with maize (and wheat) yield anomalies from RZS municipal / regional series. | Sign is right for maize in Vojvodina; wheat weaker — matches our overlap story | [RZS plant production](https://www.stat.gov.rs/sr-latn/oblasti/poljoprivreda-sumarstvo-i-ribarstvo/biljna-proizvodnja), [FAOSTAT](https://www.fao.org/faostat/) when up, [Eurostat apro_cpsh1](https://ec.europa.eu/eurostat/databrowser/view/apro_cpsh1/) |
| **E4. Outlook honesty** | Treat 2005–2014 as a fake “future,” score 1995–2004 → 2005–2014 with the same three models vs ERA5. Reliability of the range. | Direction of heat is right more often than a persistence baseline; width of the range is not theatre | Open-Meteo Climate 1950–2050 |
| **E5. Crop model** | Blind review: 3–5 Serbian agronomists rank exposure at the six pins from the table, without seeing our scores. | Maize worst in Novi Sad/Zrenjanin; Niš “no change”; wheat not flagged as high | Our `crops.assess()` vs expert form |
| **E6. LLM faithfulness** | 30 generated plans. Every numeral must appear in `pins.json` or `crops.py`. Flag variety names, yields, prices. | 100% traceable numbers; 0 brand names | `scripts/preview_advice.py` + a live Grok run |
| **E7. Decision test** | 8–12 farmers or advisors: given Novi Sad vs Niš cards, which field gets extra irrigation budget / different hybrid *practice*? | They treat the two pins differently. If both get the same answer, the product failed | Interview + the three demo cards |
| **E8. Operational** | Offline demo, rate-limit, time-to-first-number, “not available” for soil | Network-off path works; no silent nulls | `data/pins.json`, [DATA_LIMITS.md](docs/DATA_LIMITS.md) |

**Minimum serious bar before calling this a tool rather than a demo:** E1, E3, E6, E7. E2 and E4 are what a ministry or insurer will ask next. E5 is cheap and should happen in week one of a follow-on.

### What we would measure that the POC does not

- **Yield, not just millimetres.** Water balance is a stress proxy. Farmers buy tonnes. Until E3 is done, do not put a yield % on screen.
- **Irrigation actually applied.** A widening gap on rainfed maize is a different decision from the same gap on a pivot field. Needs a water-use or LPIS-like layer.
- **Field, not city.** ERA5 is ~25 km. A parcel on a south slope is not Novi Sad airport. Next step is AgERA5 or MeteoSerbia1km plus a real field polygon.
- **Cost of being wrong.** False “action needed” wastes seed money. False “no change” at Zrenjanin loses a harvest. Track those two errors separately.

### What not to do in the name of “more serious”

- Do not train a neural net on six pins.
- Do not let the LLM become the climate model.
- Do not replace the FAO table with the India-centric Kaggle classifier.
- Do not hide SoilGrids nulls behind slider defaults and call it soil intelligence.
- Do not publish a single 2035 number. The three-model spread is already the honest part of the pitch.

A short written protocol (E1–E8 above, with dates and owners) is more convincing to a follow-on jury or a ministry than a new architecture diagram.

---

## 12. Heavier models: climate change vs weather disasters

This is the usual trap: *“if we use a bigger prediction model we will know future disasters more precisely, so farmers can manage risk.”* Those are three different jobs. Mixing them produces confident nonsense.

| Horizon | Question a farmer actually asks | Right tool family | Wrong tool |
| --- | --- | --- | --- |
| **0–15 days** | Do I harvest before the storm? Irrigate this week? | Numerical weather prediction + AI weather models | CMIP6, our 2030s range |
| **1–6 months** | Will this summer be a drought year? Buy irrigation diesel / insurance now? | Seasonal ensembles (e.g. SEAS5) | GraphCast-to-2050, a fine-tuned LLM |
| **10–30 years** | Should I invest in a well, switch maturity group, change rotation? | Climate ensembles (CMIP6, EURO-CORDEX), **ranges and return periods** | A model that names the date of a 2034 hailstorm |

You can get **more precise risk** (probabilities, return periods, insured layers). You cannot get **more precise disaster timestamps** at climate scales. The atmosphere is chaotic; emission pathways are unknown; models disagree — that is why our POC already prints 44–57 days, not 52.

### A. Do not replace this POC with a giant climate net

What we have is a diagnostic: *this plot’s summer water budget moved by N mm.* That is the right object for a 5-minute demo and still the right object for a land-use decision.

Heavier **climate** modelling that is worth it:

1. **More members, not a fancier single run.** Use the full Open-Meteo set (seven HighResMIP models) and, for Serbia, [EURO-CORDEX](https://www.euro-cordex.net/) plus the [Digital Climate Atlas](https://atlas-klime.eko.gov.rs/). Report percentiles (10 / 50 / 90), not a mean.
2. **Scenarios.** CMIP6 is not one future. At least SSP2-4.5 and SSP5-8.5. Farmers investing in irrigation need to see that the answer depends on the pathway.
3. **Bias correction against Serbian stations** (quantile mapping onto RHMZ / MeteoSerbia1km), then recompute *our same indices*. Skill is “does the corrected ensemble beat raw Open-Meteo on E4,” not “we switched to a transformer.”
4. **Extremes as frequencies.** Count of 3-day heatwaves, 20 mm rain days, 20-year return of summer ET0. [ETCCDI climate indices](https://etccdi.pacificclimate.org/list_27_indices.shtml) are the standard language. This is still not a disaster forecast.

What is **not** worth it for climate-scale farm advice: training GraphCast / Pangu / FourCastNet / a custom LSTM on ERA5 and asking it for 2040. Those models are weather emulators (days), not climate simulators (decades). ECMWF already operationalised this class as [AIFS](https://www.ecmwf.int/en/forecasts/datasets/aifs-machine-learning-data) out to **15 days**, and stopped plotting some third-party ML weather models once AIFS was in production.

### B. Weather disasters: a second product, stacked under the copilot

For **risk management this season**, add a now-to-seasonal layer next to the decade card. Same UI, different physics, different disclaimer.

| Layer | What the farmer gets | Open / operational source | Precision you can honestly sell |
| --- | --- | --- | --- |
| Medium-range weather | 1–15 day heat, rain, wind | [Open-Meteo Forecast](https://open-meteo.com/en/docs) (includes ECMWF among others); [ECMWF IFS](https://www.ecmwf.int/en/forecasts); [AIFS](https://www.ecmwf.int/en/forecasts/datasets/aifs-machine-learning-data); [GraphCast](https://deepmind.google/discover/blog/graphcast-ai-model-for-faster-and-more-accurate-global-weather-forecasting/) as research | Ensemble probabilities (“40% chance of >20 mm in 48 h”), not a single deterministic storm track as fate |
| Flood | River / surface-water outlook | [EFAS](https://www.efas.eu/) (Europe), [GloFAS](https://www.globalfloods.eu/) | Catchment-scale; not “your 4 ha will flood at 16:00” |
| Seasonal | Next summer drier/wetter than normal | [C3S seasonal](https://climate.copernicus.eu/seasonal-forecasts) / [SEAS5](https://www.ecmwf.int/en/forecasts/documentation-and-support/long-range) | Weak but real skill at 1–3 months for some variables; always show the ensemble |
| Process crop model | Yield under that weather | [FAO AquaCrop](https://www.fao.org/aquacrop/), [WOFOST](https://www.wur.nl/en/research-results/research-institutes/environmental-research/facilities-tools/software-models-and-databases/wofost.htm), [DSSAT](https://dssat.net/) | Scenario yields with uncertainty; needs local calibration (phenology, soil, sowing date) |

**The architecture that actually helps risk management:**

```
Decade card (what we have)     Seasonal card (SEAS5 → AquaCrop)     15-day card (IFS/AIFS)
        │                                │                                  │
        └──────────── plot-level risk cockpit ──────────────────────────────┘
                         │
           parametric trigger (mm deficit, hot-day count)
                         │
              insurance / irrigation / harvest decision
```

Coupling seasonal ensembles to a crop model is a known pattern (SEAS5 + WOFOST has published skill at 1–3 month lead for some systems). That is the “heavier model” worth building. It still will not tell you the date of a 2032 hailstorm.

### C. How to evaluate the heavier stack (so it does not become theatre)

| Claim | Test | Kill criterion |
| --- | --- | --- |
| “AI weather is more precise” | CRPS / Brier skill vs ECMWF IFS on Serbian stations, 1–7 day, last 2 years, for Tmax and 24 h precip | If it does not beat a cheap Open-Meteo ensemble on those two variables, do not put it on the farmer screen |
| “We predict droughts” | Seasonal: probability of below-normal JJA rain vs what happened, 1993–present hindcast | Reliability diagram; if 70% drought calls verify 40% of the time, show 40% |
| “We predict floods” | EFAS/GloFAS hit rate vs Copernicus EMS / EM-DAT flood records on the Danube/Tisa/Sava | Misses on known Serbian flood years = do not sell flood warnings |
| “Yield at risk” | AquaCrop/WOFOST vs RZS municipal maize yield, leave-one-year-out | RMSE must beat “last year’s yield” and “district mean” |
| “Better than AgriSense POC” | Does the new model change the Novi Sad vs Niš contrast, or only add decimal places? | If Niš and Novi Sad still need different actions, keep the simple index as the headline |

### D. What we would actually build next (priority order)

1. **Validate the POC** — gates E1, E3, E6, E7 in §11. Weeks, not a new model.
2. **Grid Serbia** — AgERA5 or MeteoSerbia1km, municipality map of the summer-mask signal.
3. **Seasonal risk card** — C3S/SEAS5 ensemble → same ET0 / rain indices we already compute → “this summer vs the 2015–2024 baseline,” with probabilities.
4. **15-day ops card** — Open-Meteo forecast or AIFS for harvest / spray / irrigate windows. This is where ML weather models earn their keep.
5. **One process crop model** — AquaCrop first (FAO, same family as our Kc). Calibrate on Vojvodina maize. Only then talk yield %.
6. **Parametric risk** — publish the trigger (e.g. June–August water balance below the 20th percentile of 1985–2024). Insurers and cooperatives can use that without us pricing a policy.
7. **CORDEX / Atlas overlay** — replace our three-model 2030s range with a Serbia-official ensemble from the Digital Climate Atlas, still as a range.

**Bottom line for the pitch, if asked:** we are not going to “solve climate prediction.” We will keep the decade diagnostic that already works, then add a seasonal probability and a 15-day ensemble so a farmer can manage **this year** and **this week**, not a fictional timestamp in 2035. Precision means calibrated probabilities on the right time scale — not a heavier model pointed at the wrong question.
