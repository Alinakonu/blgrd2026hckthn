# Data limits and failure modes

What is broken, what is rate-limited, and what to do when it bites during the build. Read this before debugging a data problem.

---

## Open-Meteo rate limiting

The free tier has no key and no signup, which is why we use it, but it enforces burst and hourly limits and returns **HTTP 429** when you cross them.

`agrisense/climate.py` paces every request 6 seconds apart and backs off 15, 30 then 45 seconds on a 429. Without that, 2 of 6 pins failed outright.

Even with pacing, a full six-pin rebuild makes 30 calls (2 history + 3 projection per pin) and takes roughly 5 minutes. **Running it twice in quick succession exhausts the hourly allowance**, after which every call 429s for a while. That happened once already during Track A; the fix is simply to wait.

**Consequences for the build:**

- Read `data/pins.json`. Do not call the API in the click path.
- If you need a fresh rebuild, budget 5 minutes and do not retry on failure.
- `build_pins.py` refuses to overwrite `pins.json` with fewer records than it already holds, so a rate-limited run cannot destroy good data. That guard exists because a run where all six pins failed would otherwise have written an empty array.

## `pins.json` is one schema version behind

`climate.py` computes three fields that the committed `pins.json` does not contain, because the rebuild that would have added them hit the rate limit:

- `season_rain_mm` — April–September rainfall
- `season_water_demand_mm` — April–September ET0
- `growing_degree_days_base0` — GDD for cool-season crops (wheat, barley)

**Nothing currently depends on them.** `crops.py` deliberately uses the June–August ET0 and rainfall that are already present, via the FAO-56 `ETc = Kc × ETo` method. The missing fields would refine the model, not enable it.

To add them, run `python scripts/build_pins.py` when the rate limit has cleared and commit the result.

## SoilGrids is down for Europe

ISRIC's REST API returns **HTTP 200 with every value `null`** for Serbian coordinates. It is not our request that is wrong: the same query shape returns real data for Iowa (`clay: 291`, `phh2o: 65`) and nulls for both Serbia and the Netherlands. ISRIC's own site carries a "service temporarily paused" notice.

The trap is that the response still lists layer names, so a check that only inspects keys will report success. **Always check values.**

`fetch_soil()` returns `None` rather than a partially-filled dict, and `soil` is `null` for all six pins. Track B should render "not available" rather than an empty soil card.

Soil moisture comes from ERA5 instead (`summer_soil_moisture`), which is present for every pin and is arguably more relevant to the water-stress story than static pH would be.

## FAOSTAT is down

`fenixservices.fao.org/faostat/api/v1/en/data/QCL` returns **HTTP 521**. It would have supplied Serbian crop yield history for validating the climate-to-yield link.

Nothing depends on it. If a yield chart is wanted later, Eurostat `apro_cpsh1` via DBnomics is the untested backup.

## Two methodology traps already hit

Both produced plausible-looking wrong numbers, so they are worth knowing about.

**Streak metrics over a multi-year window.** Computing the longest dry streak across a concatenated decade returns the single worst drought in ten years and presents it as typical — Subotica appeared to have a 60-day dry streak. `compute_indices` now averages each year's longest run; Subotica is 27.4 → 26.1 days, essentially flat.

**Growing degree days compared to published requirements.** Our GDD uses base 10 °C capped at 30 °C over April–September. Published maturity figures use crop-specific bases and different season windows, so comparing them implies maize cannot grow in Serbia — against 938,209 planted hectares. GDD is used as a relative signal only. See `docs/CROP_MODEL.md` section 4.

## Quick health check

```bash
python scripts/preview_advice.py     # exercises pins.json, crops.py and prompt.py offline
python scripts/build_pins.py         # hits the network; ~5 min; safe to fail
```

If `preview_advice.py` works, everything the demo needs is functioning regardless of network state.
