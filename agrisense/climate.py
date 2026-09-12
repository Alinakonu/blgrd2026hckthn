"""Climate and soil data for a point, reduced to the indices a farmer cares about.

Stdlib only, no API keys. Track B can import this directly.

The headline metric is the growing-season water balance: rainfall minus ET0
(reference evapotranspiration, the FAO standard for crop water demand). Annual
rainfall totals hide the problem because they average the wet half of the year
into the dry half.
"""

import json
import time
import urllib.error
import urllib.parse
import urllib.request

ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"
CLIMATE_URL = "https://climate-api.open-meteo.com/v1/climate"
SOILGRIDS_URL = "https://rest.isric.org/soilgrids/v2.0/properties/query"

TIMEZONE = "Europe/Belgrade"

# Open-Meteo's free tier rate-limits bursts; pace requests to stay under it.
REQUEST_SPACING_SECONDS = 6.0
_last_request_at = 0.0

# Demo locations across Serbia's main agricultural regions.
PINS = [
    {"name": "Novi Sad", "lat": 45.2671, "lon": 19.8335, "region": "Vojvodina"},
    {"name": "Subotica", "lat": 46.1006, "lon": 19.6651, "region": "North Backa"},
    {"name": "Zrenjanin", "lat": 45.3836, "lon": 20.3819, "region": "Banat"},
    {"name": "Belgrade", "lat": 44.7866, "lon": 20.4489, "region": "Central"},
    {"name": "Kraljevo", "lat": 43.7258, "lon": 20.6892, "region": "Sumadija"},
    {"name": "Nis", "lat": 43.3209, "lon": 21.8958, "region": "South"},
]

BASELINE = ("1985-01-01", "1994-12-31")
RECENT = ("2015-01-01", "2024-12-31")
OUTLOOK = ("2031-01-01", "2040-12-31")

GROWING_SEASON = (4, 9)  # April-September
SUMMER = (6, 8)  # peak water stress

# CMIP6 downscaled models offered by Open-Meteo. Several are queried so the
# spread between them can be reported instead of a single false-precision number.
CLIMATE_MODELS = ["MRI_AGCM3_2_S", "EC_Earth3P_HR", "MPI_ESM1_2_XR"]

DAILY_VARIABLES = [
    "temperature_2m_max",
    "temperature_2m_min",
    "precipitation_sum",
    "et0_fao_evapotranspiration_sum",
    "soil_moisture_0_to_7cm_mean",
]


def _throttle():
    global _last_request_at
    wait = REQUEST_SPACING_SECONDS - (time.time() - _last_request_at)
    if wait > 0:
        time.sleep(wait)
    _last_request_at = time.time()


def _get_json(url, params, timeout=90, retries=3):
    query = urllib.parse.urlencode(params, doseq=True)
    last_error = None
    for attempt in range(retries + 1):
        _throttle()
        try:
            with urllib.request.urlopen(f"{url}?{query}", timeout=timeout) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            last_error = exc
            # Back off hard on rate limiting, fail fast on anything else.
            if exc.code != 429:
                raise RuntimeError(f"{url} returned HTTP {exc.code}") from exc
            time.sleep(15 * (attempt + 1))
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            last_error = exc
            time.sleep(3 * (attempt + 1))
    raise RuntimeError(f"{url} failed after {retries + 1} attempts: {last_error}")


def fetch_history(lat, lon, start, end):
    """Daily observations from ERA5 reanalysis."""
    return _get_json(
        ARCHIVE_URL,
        {
            "latitude": lat,
            "longitude": lon,
            "start_date": start,
            "end_date": end,
            "daily": ",".join(DAILY_VARIABLES),
            "timezone": TIMEZONE,
        },
    )["daily"]


def fetch_projection(lat, lon, start, end, model):
    """Daily values from one downscaled climate model."""
    return _get_json(
        CLIMATE_URL,
        {
            "latitude": lat,
            "longitude": lon,
            "start_date": start,
            "end_date": end,
            "models": model,
            "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,et0_fao_evapotranspiration_sum",
        },
    )["daily"]


def fetch_soil(lat, lon):
    """Topsoil properties from SoilGrids.

    Returns None when unavailable. As of this writing ISRIC has the service
    degraded: European points return HTTP 200 with null values, so always be
    prepared for None rather than treating a successful response as data.
    """
    try:
        payload = _get_json(
            SOILGRIDS_URL,
            {
                "lon": lon,
                "lat": lat,
                "property": ["phh2o", "clay", "sand", "nitrogen", "soc"],
                "depth": "0-5cm",
                "value": "mean",
            },
            timeout=60,
            retries=1,
        )
    except RuntimeError:
        return None

    soil = {}
    for layer in payload.get("properties", {}).get("layers", []):
        depths = layer.get("depths") or []
        if not depths:
            continue
        raw = depths[0].get("values", {}).get("mean")
        if raw is None:
            continue
        factor = layer.get("unit_measure", {}).get("d_factor", 1) or 1
        soil[layer["name"]] = round(raw / factor, 2)
    return soil or None


def _by_year(dates, *series):
    """Group parallel daily series into {year: [(v1, v2, ...), ...]}."""
    grouped = {}
    for row in zip(dates, *series):
        grouped.setdefault(row[0][:4], []).append(row[1:])
    return grouped


def _longest_streak(values, predicate):
    longest = current = 0
    for value in values:
        if value is not None and predicate(value):
            current += 1
            longest = max(longest, current)
        else:
            current = 0
    return longest


def _mean(values):
    clean = [v for v in values if v is not None]
    return sum(clean) / len(clean) if clean else None


def _in_months(date, window):
    return window[0] <= int(date[5:7]) <= window[1]


def compute_indices(daily):
    """Reduce a daily series to per-year agronomic indices.

    Averages are per year, and streak metrics average each year's longest run
    rather than taking the single longest run in the whole period, which would
    report one freak event as if it were typical.
    """
    dates = daily["time"]
    tmax = daily["temperature_2m_max"]
    tmin = daily["temperature_2m_min"]
    precip = daily["precipitation_sum"]
    et0 = daily.get("et0_fao_evapotranspiration_sum") or [None] * len(dates)
    moisture = daily.get("soil_moisture_0_to_7cm_mean") or [None] * len(dates)

    per_year = _by_year(dates, tmax, tmin, precip, et0, moisture)
    years = len(per_year) or 1

    hot_30 = hot_35 = 0
    heavy_rain = 0
    precip_total = 0.0
    gdd_total = 0.0
    hot_streaks = []
    dry_streaks = []
    summer_precip = []
    summer_et0 = []
    summer_moisture = []
    peak = None

    for _year, rows in per_year.items():
        year_tmax = [r[0] for r in rows]
        year_precip = [r[2] for r in rows]

        hot_30 += sum(1 for t in year_tmax if t is not None and t >= 30)
        hot_35 += sum(1 for t in year_tmax if t is not None and t >= 35)
        heavy_rain += sum(1 for p in year_precip if p is not None and p >= 20)
        precip_total += sum(p for p in year_precip if p is not None)
        hot_streaks.append(_longest_streak(year_tmax, lambda t: t >= 30))
        dry_streaks.append(_longest_streak(year_precip, lambda p: p < 1.0))

        year_max = [t for t in year_tmax if t is not None]
        if year_max:
            peak = max(year_max) if peak is None else max(peak, max(year_max))

    for date, high, low, rain, demand, wet in zip(dates, tmax, tmin, precip, et0, moisture):
        if _in_months(date, GROWING_SEASON) and high is not None and low is not None:
            # Maize convention: base 10 degrees C, upper cap 30 degrees C.
            mean_temp = (min(high, 30.0) + max(low, 10.0)) / 2
            gdd_total += max(0.0, mean_temp - 10.0)
        if _in_months(date, SUMMER):
            if rain is not None:
                summer_precip.append(rain)
            if demand is not None:
                summer_et0.append(demand)
            if wet is not None:
                summer_moisture.append(wet)

    summer_rain_mm = round(sum(summer_precip) / years) if summer_precip else None
    summer_demand_mm = round(sum(summer_et0) / years) if summer_et0 else None
    moisture_mean = _mean(summer_moisture)

    return {
        "hot_days_30": round(hot_30 / years, 1),
        "hot_days_35": round(hot_35 / years, 1),
        "peak_temp": round(peak, 1) if peak is not None else None,
        "longest_hot_streak_days": round(sum(hot_streaks) / years, 1),
        "precip_mm": round(precip_total / years),
        "heavy_rain_days_20": round(heavy_rain / years, 1),
        "max_dry_streak_days": round(sum(dry_streaks) / years, 1),
        "growing_degree_days": round(gdd_total / years),
        "summer_rain_mm": summer_rain_mm,
        "summer_water_demand_mm": summer_demand_mm,
        "summer_water_balance_mm": (
            summer_rain_mm - summer_demand_mm
            if summer_rain_mm is not None and summer_demand_mm is not None
            else None
        ),
        "summer_soil_moisture": round(moisture_mean, 4) if moisture_mean else None,
    }


def derive_signals(baseline, recent):
    """Plain-language findings from the shift between two periods."""
    signals = []

    if recent["hot_days_30"] - baseline["hot_days_30"] >= 5:
        signals.append("heat_intensifying")
    elif recent["hot_days_30"] - baseline["hot_days_30"] <= -5:
        signals.append("heat_easing")
    else:
        signals.append("heat_stable")

    annual_change = _pct_change(baseline["precip_mm"], recent["precip_mm"])
    if annual_change is not None:
        if abs(annual_change) < 10:
            signals.append("annual_rainfall_stable")
        elif annual_change > 0:
            signals.append("annual_rainfall_increasing")
        else:
            signals.append("annual_rainfall_declining")

    if baseline["summer_water_demand_mm"] and recent["summer_water_demand_mm"]:
        if recent["summer_water_demand_mm"] > baseline["summer_water_demand_mm"] + 10:
            signals.append("crop_water_demand_rising")

    base_balance = baseline["summer_water_balance_mm"]
    recent_balance = recent["summer_water_balance_mm"]
    if base_balance is not None and recent_balance is not None:
        # Both are negative; more negative means a bigger irrigation gap.
        if recent_balance < base_balance - 20:
            signals.append("summer_water_deficit_worsening")
        elif recent_balance > base_balance + 20:
            signals.append("summer_water_deficit_easing")
        else:
            signals.append("summer_water_deficit_stable")

    # The case worth flagging loudest: the annual rain gauge looks fine while
    # the growing season quietly dries out.
    if (
        "summer_water_deficit_worsening" in signals
        and annual_change is not None
        and annual_change > -10
    ):
        signals.append("annual_totals_masking_summer_stress")

    if recent["max_dry_streak_days"] > baseline["max_dry_streak_days"] + 3:
        signals.append("dry_spells_lengthening")

    return signals


def _pct_change(before, after):
    if not before:
        return None
    return (after - before) / before * 100


def build_pin(pin, models=CLIMATE_MODELS, include_soil=True):
    """Assemble the full record for one location, matching the PLAN.md contract."""
    baseline = compute_indices(fetch_history(pin["lat"], pin["lon"], *BASELINE))
    recent = compute_indices(fetch_history(pin["lat"], pin["lon"], *RECENT))

    projections = {}
    for model in models:
        try:
            daily = fetch_projection(pin["lat"], pin["lon"], *OUTLOOK, model=model)
            projections[model] = compute_indices(daily)
        except (RuntimeError, KeyError):
            continue

    outlook = None
    if projections:
        hot = sorted(p["hot_days_30"] for p in projections.values())
        precip = sorted(p["precip_mm"] for p in projections.values())
        outlook = {
            "period": "2031-2040",
            "models": list(projections),
            "hot_days_30_range": [hot[0], hot[-1]],
            "hot_days_30_median": hot[len(hot) // 2],
            "precip_mm_range": [precip[0], precip[-1]],
            "confidence": "multi-model range, illustrative not a forecast",
            "per_model": projections,
        }

    record = {
        "location": {
            "name": pin["name"],
            "region": pin.get("region"),
            "lat": pin["lat"],
            "lon": pin["lon"],
        },
        "baseline": {"period": "1985-1994", **baseline},
        "recent": {"period": "2015-2024", **recent},
        "outlook": outlook,
        "signals": derive_signals(baseline, recent),
    }

    if include_soil:
        soil = fetch_soil(pin["lat"], pin["lon"])
        record["soil"] = (
            {**soil, "depth": "0-5cm", "source": "SoilGrids"} if soil else None
        )

    return record
