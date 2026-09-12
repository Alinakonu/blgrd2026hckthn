"""Crop exposure scoring for Serbia's main arable crops.

Answers one question: given the measured shift in growing-season water balance,
which of the crops actually planted in this region are most exposed, and what
are the options?

Method: FAO-56 crop water requirement, ETc = Kc * ETo. The ETo term is the
et0_fao_evapotranspiration already in every pins.json record, so a crop's
summer water demand is derived from measured data rather than a lookup.

Constants are sourced, not invented:
  - Kc mid-season, seasonal water need, drought sensitivity: FAO Irrigation
    Water Management Training Manual 3, Tables 12 and 14
    (fao.org/4/S2022E/s2022e07.htm).
  - Sowing areas: Republic Statistical Office of Serbia, 2026 release
    (publikacije.stat.gov.rs/G2026/HtmlE/G20261171.html).

Deliberately NOT modelled: absolute crop-fit from growing degree days. See
docs/CROP_MODEL.md for why that comparison is invalid here.
"""

# sensitivity_rank maps FAO's drought sensitivity bands to a 1-5 scale so the
# crops can be ordered. 1 = withstands shortage well, 5 = must not be stressed.
SENSITIVITY_RANK = {
    "low": 1,
    "low-medium": 2,
    "medium": 3,
    "medium-high": 4,
    "high": 5,
}

# peak_window is the month range when the crop is in its moisture-sensitive
# mid-season stage. Crops whose peak falls inside Jun-Aug take the full force of
# a worsening summer deficit; winter wheat is harvested before it arrives.
CROPS = {
    "maize": {
        "label": "Maize",
        "label_sr": "Kukuruz",
        "kc_mid": 1.20,
        "water_need_mm": (500, 800),
        "drought_sensitivity": "medium-high",
        "peak_window": (6, 8),
        "sown_ha_serbia": 938209,
        "sown_ha_vojvodina": 500759,
        "note": "Serbia's largest crop by area and the most drought-sensitive of the majors.",
    },
    "wheat": {
        "label": "Wheat",
        "label_sr": "Pšenica",
        "kc_mid": 1.15,
        "water_need_mm": (450, 650),
        "drought_sensitivity": "low-medium",
        "peak_window": (4, 6),
        "sown_ha_serbia": 626282,
        "sown_ha_vojvodina": 305412,
        "note": "Winter-sown and harvested in early July, so it largely escapes peak summer deficit.",
    },
    "sunflower": {
        "label": "Sunflower",
        "label_sr": "Suncokret",
        "kc_mid": 1.15,
        "water_need_mm": (600, 1000),
        "drought_sensitivity": "low-medium",
        "peak_window": (6, 8),
        "sown_ha_serbia": 250816,
        "sown_ha_vojvodina": 220139,
        "note": "High total demand but deep roots; tolerates shortage better than maize.",
    },
    "soybean": {
        "label": "Soybean",
        "label_sr": "Soja",
        "kc_mid": 1.10,
        "water_need_mm": (450, 700),
        "drought_sensitivity": "low-medium",
        "peak_window": (7, 8),
        "sown_ha_serbia": 193731,
        "sown_ha_vojvodina": 172117,
        "note": "Pod fill in Jul-Aug lands squarely in the worsening window.",
    },
    "sugar_beet": {
        "label": "Sugar beet",
        "label_sr": "Šećerna repa",
        "kc_mid": 1.15,
        "water_need_mm": (550, 750),
        "drought_sensitivity": "low-medium",
        "peak_window": (6, 9),
        "sown_ha_serbia": 32432,
        "sown_ha_vojvodina": 31539,
        "note": "Long season keeps it exposed into September.",
    },
    "sorghum": {
        "label": "Sorghum",
        "label_sr": "Sirak",
        "kc_mid": 1.10,
        "water_need_mm": (450, 650),
        "drought_sensitivity": "low",
        "peak_window": (6, 8),
        "sown_ha_serbia": 0,
        "sown_ha_vojvodina": 0,
        "note": "Not currently grown at scale in Serbia. Included as the adaptation candidate: "
        "lowest FAO drought sensitivity of the warm-season grains.",
    },
}


def _mid(bounds):
    return sum(bounds) / 2


def irrigation_gap(period, crop):
    """Millimetres of water the crop needs beyond summer rainfall.

    ETc = Kc * ETo over Jun-Aug, minus rainfall over the same window. Positive
    means rain alone does not meet demand, which is the normal case for summer
    crops in Serbia -- what matters is how the gap is changing, not that it
    exists.
    """
    eto = period.get("summer_water_demand_mm")
    rain = period.get("summer_rain_mm")
    if eto is None or rain is None:
        return None
    return round(crop["kc_mid"] * eto - rain)


def summer_overlap(peak_window):
    """Fraction of a crop's moisture-sensitive window that falls in Jun-Aug.

    This is what separates the crops. Every crop at a given location sees the
    same ET0, and the FAO Kc values span only 1.10-1.20, so demand alone ranks
    them almost identically. What actually differs is timing: winter wheat fills
    grain in May and is off the field by early July, so a worsening July-August
    deficit barely touches it, while soybean sets pods straight into it.
    """
    start, end = peak_window
    months = set(range(start, end + 1))
    return len(months & {6, 7, 8}) / len(months)


def assess_crop(record, key):
    """Compare a crop's water gap between the baseline and recent decades."""
    crop = CROPS[key]
    baseline, recent = record["baseline"], record["recent"]

    gap_before = irrigation_gap(baseline, crop)
    gap_after = irrigation_gap(recent, crop)
    if gap_before is None or gap_after is None:
        return None

    widening = gap_after - gap_before
    sensitivity = SENSITIVITY_RANK[crop["drought_sensitivity"]]
    overlap = summer_overlap(crop["peak_window"])

    # Exposure = how much more water is needed, weighted by how badly the crop
    # handles shortage and by how much of its sensitive window sits in the
    # months that are deteriorating. Scaled so a 50 mm widening on a fully
    # exposed medium-high sensitivity crop lands around 2.0.
    exposure = round(widening / 50 * sensitivity / 2 * overlap, 2)

    return {
        "crop": key,
        "label": crop["label"],
        "label_sr": crop["label_sr"],
        "water_need_mm": list(crop["water_need_mm"]),
        "drought_sensitivity": crop["drought_sensitivity"],
        "irrigation_gap_baseline_mm": gap_before,
        "irrigation_gap_recent_mm": gap_after,
        "gap_widening_mm": widening,
        "summer_overlap": round(overlap, 2),
        "exposure_score": exposure,
        "exposure_band": _band(exposure),
        "peak_demand_months": list(crop["peak_window"]),
        "sown_ha_vojvodina": crop["sown_ha_vojvodina"],
        "note": crop["note"],
    }


def _band(score):
    if score >= 1.5:
        return "high"
    if score >= 0.5:
        return "moderate"
    if score > -0.5:
        return "stable"
    return "improving"


def thermal_trend(record):
    """Change in accumulated heat, used only as a relative signal.

    Rising GDD means longer-maturity varieties become viable, which is an
    opportunity that partly offsets the water risk. The absolute value is NOT
    compared against published maturity requirements -- see docs/CROP_MODEL.md.
    """
    before = record["baseline"].get("growing_degree_days")
    after = record["recent"].get("growing_degree_days")
    if before is None or after is None:
        return None

    change = after - before
    return {
        "gdd_baseline": before,
        "gdd_recent": after,
        "gdd_change": change,
        "percent_change": round(change / before * 100, 1) if before else None,
        "interpretation": (
            "longer-maturity varieties now viable"
            if change >= 100
            else "thermal window broadly unchanged"
        ),
    }


def assess(record):
    """Full crop assessment for one location record from data/pins.json."""
    results = [r for r in (assess_crop(record, key) for key in CROPS) if r]
    results.sort(key=lambda r: r["exposure_score"], reverse=True)

    grown = [r for r in results if r["sown_ha_vojvodina"] > 0]
    at_risk = [r for r in grown if r["exposure_band"] in ("high", "moderate")]

    # Only offer a swap when something is actually under pressure and the
    # alternative is meaningfully less exposed than what is at risk.
    alternatives = [
        r
        for r in results
        if r["sown_ha_vojvodina"] == 0
        and at_risk
        and r["exposure_score"] < min(g["exposure_score"] for g in at_risk)
    ]

    return {
        "location": record["location"]["name"],
        "crops": results,
        # Naming a "most exposed" crop where nothing is deteriorating would
        # imply a problem the data does not show.
        "most_exposed": at_risk[0]["crop"] if at_risk else None,
        "crops_at_risk": [r["crop"] for r in at_risk],
        "adaptation_candidates": [r["crop"] for r in alternatives],
        "verdict": "action_needed" if at_risk else "no_change_indicated",
        "thermal": thermal_trend(record),
    }
