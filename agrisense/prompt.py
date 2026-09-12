"""Turn a location record into an LLM prompt for the agronomy action plan.

The design rule throughout: the model explains and prioritises numbers that
were measured. It never produces them. Every figure in the output should be
traceable to data/pins.json or the FAO constants in crops.py, so a judge asking
"where did that come from" always has an answer.
"""

import json

from agrisense import crops as crop_model

SIGNAL_TEXT = {
    "heat_intensifying": "extreme-heat days have increased materially",
    "heat_stable": "extreme-heat days are broadly unchanged",
    "heat_easing": "extreme-heat days have decreased",
    "annual_rainfall_stable": "annual rainfall totals are broadly unchanged",
    "annual_rainfall_increasing": "annual rainfall totals have increased",
    "annual_rainfall_declining": "annual rainfall totals have decreased",
    "crop_water_demand_rising": "reference evapotranspiration has risen, so crops now need more water for the same yield",
    "summer_water_deficit_worsening": "the summer rainfall-minus-demand balance has deteriorated",
    "summer_water_deficit_stable": "the summer rainfall-minus-demand balance is broadly unchanged",
    "summer_water_deficit_easing": "the summer rainfall-minus-demand balance has improved",
    "annual_totals_masking_summer_stress": (
        "annual rainfall looks fine while the growing season has dried out, so "
        "yearly totals would mislead this farmer"
    ),
    "dry_spells_lengthening": "the typical longest dry spell each year has lengthened",
}

SYSTEM_PROMPT = """You are an agronomist advising a farmer in Serbia on adapting \
a specific plot to measured climate change.

Rules you must follow:
1. Use only the figures given in the data block. Never invent a number, a yield \
figure, a price, a product name, or a seed variety name.
2. When you cite a number, state its units and period.
3. The projection is a spread across climate models. Always present it as a \
range and call it a model range, never a forecast or a prediction.
4. If the data shows conditions are stable or improving, say so plainly. Do not \
manufacture alarm.
5. Recommend agronomic practice, not brands. "A shorter-maturity hybrid" is \
allowed; a specific commercial hybrid name is not.
6. Be concrete about timing. Reference the months given in the data.
7. Write for a working farmer: plain language, no climate jargon, under 300 words.

Structure your answer as:
WHAT CHANGED - two sentences on the measured shift.
WHAT IT MEANS FOR YOUR CROPS - which crops are most exposed and why.
WHAT TO DO - three to five specific actions, each with a rough timeframe.
WHAT TO WATCH - one or two indicators worth tracking."""


def _fmt_signals(signals):
    return "\n".join(f"- {SIGNAL_TEXT.get(s, s)}" for s in signals)


def _fmt_period(label, period):
    return (
        f"{label} ({period['period']}):\n"
        f"  days at or above 30C per year: {period['hot_days_30']}\n"
        f"  days at or above 35C per year: {period['hot_days_35']}\n"
        f"  annual rainfall: {period['precip_mm']} mm\n"
        f"  summer (Jun-Aug) rainfall: {period['summer_rain_mm']} mm\n"
        f"  summer crop water demand (ET0): {period['summer_water_demand_mm']} mm\n"
        f"  summer water balance: {period['summer_water_balance_mm']} mm\n"
        f"  typical longest dry spell: {period['max_dry_streak_days']} days\n"
        f"  growing degree days (Apr-Sep, base 10C): {period['growing_degree_days']}"
    )


def _fmt_outlook(outlook):
    if not outlook:
        return "Projection: unavailable."
    low, high = outlook["hot_days_30_range"]
    models = ", ".join(outlook["models"])
    return (
        f"Model range for {outlook['period']} ({len(outlook['models'])} climate models: {models}):\n"
        f"  days at or above 30C per year: {low} to {high}\n"
        f"  annual rainfall: {outlook['precip_mm_range'][0]} to {outlook['precip_mm_range'][1]} mm\n"
        f"  NOTE: {outlook['confidence']}"
    )


def _fmt_crops(assessment):
    lines = []
    for entry in assessment["crops"]:
        if entry["sown_ha_vojvodina"] == 0:
            continue
        lines.append(
            f"  {entry['label']} ({entry['sown_ha_vojvodina']:,} ha in Vojvodina): "
            f"irrigation gap {entry['irrigation_gap_baseline_mm']} -> "
            f"{entry['irrigation_gap_recent_mm']} mm "
            f"({entry['gap_widening_mm']:+d} mm), FAO drought sensitivity "
            f"{entry['drought_sensitivity']}, peak demand months "
            f"{entry['peak_demand_months'][0]}-{entry['peak_demand_months'][1]}, "
            f"exposure {entry['exposure_band']}"
        )

    candidates = assessment["adaptation_candidates"]
    if candidates:
        for key in candidates:
            crop = crop_model.CROPS[key]
            lines.append(
                f"  ALTERNATIVE {crop['label']}: FAO drought sensitivity "
                f"{crop['drought_sensitivity']}, seasonal need "
                f"{crop['water_need_mm'][0]}-{crop['water_need_mm'][1]} mm. {crop['note']}"
            )
    return "\n".join(lines)


def build_user_prompt(record, assessment=None):
    """Render one location record as the data block the model reasons over."""
    assessment = assessment or crop_model.assess(record)
    location = record["location"]
    thermal = assessment.get("thermal") or {}

    return f"""LOCATION: {location['name']}, {location.get('region', 'Serbia')} \
({location['lat']}, {location['lon']})

MEASURED CLIMATE (ERA5 reanalysis, per year):
{_fmt_period('Baseline', record['baseline'])}

{_fmt_period('Recent', record['recent'])}

{_fmt_outlook(record.get('outlook'))}

WHAT THE COMPARISON SHOWS:
{_fmt_signals(record['signals'])}

HEAT ACCUMULATION:
  growing degree days {thermal.get('gdd_baseline')} -> {thermal.get('gdd_recent')} \
({thermal.get('percent_change')}%)
  {thermal.get('interpretation')}

CROP EXPOSURE (FAO-56 method, ETc = Kc x ET0 for Jun-Aug, minus summer rainfall):
{_fmt_crops(assessment)}

SOIL: {"not available for this location" if not record.get("soil") else json.dumps(record["soil"])}
Topsoil moisture (ERA5, summer mean): \
{record['baseline'].get('summer_soil_moisture')} -> {record['recent'].get('summer_soil_moisture')} m3/m3

Write the advice now."""


def build_messages(record, assessment=None):
    """Chat-format messages ready for any OpenAI-compatible API, including x.ai."""
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": build_user_prompt(record, assessment)},
    ]
