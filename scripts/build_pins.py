"""Build data/pins.json and print the Track A findings table.

Run: python scripts/build_pins.py
The committed JSON is the demo's offline fallback if an API is down on the day.
"""

import json
import pathlib
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from agrisense.climate import PINS, build_pin, fetch_soil  # noqa: E402

OUTPUT = pathlib.Path(__file__).resolve().parent.parent / "data" / "pins.json"


def main():
    records = []
    soil_results = []

    for pin in PINS:
        started = time.time()
        print(f"  fetching {pin['name']}...", flush=True)
        try:
            record = build_pin(pin, include_soil=False)
        except RuntimeError as exc:
            print(f"    FAILED: {exc}")
            continue

        soil_started = time.time()
        soil = fetch_soil(pin["lat"], pin["lon"])
        soil_results.append((pin["name"], time.time() - soil_started, soil))
        record["soil"] = {**soil, "depth": "0-5cm", "source": "SoilGrids"} if soil else None

        records.append(record)
        print(f"    done in {time.time() - started:.1f}s")

    print("\n=== A1: HEAT, 1985-1994 vs 2015-2024 (per year) ===")
    print(f"{'Location':<12}{'days >=30C':>18}{'days >=35C':>16}{'GDD':>16}")
    print("-" * 62)
    for record in records:
        base, recent = record["baseline"], record["recent"]
        print(
            f"{record['location']['name']:<12}"
            f"{base['hot_days_30']:>8.1f} -> {recent['hot_days_30']:<8.1f}"
            f"{base['hot_days_35']:>7.1f} -> {recent['hot_days_35']:<7.1f}"
            f"{base['growing_degree_days']:>7} -> {recent['growing_degree_days']:<7}"
        )

    print("\n=== A4: SUMMER WATER BALANCE (Jun-Aug, mm/year) ===")
    print(f"{'Location':<12}{'rainfall':>16}{'ET0 demand':>18}{'balance':>18}{'change':>10}")
    print("-" * 74)
    for record in records:
        base, recent = record["baseline"], record["recent"]
        if base["summer_water_balance_mm"] is None:
            continue
        delta = recent["summer_water_balance_mm"] - base["summer_water_balance_mm"]
        print(
            f"{record['location']['name']:<12}"
            f"{base['summer_rain_mm']:>7} -> {recent['summer_rain_mm']:<8}"
            f"{base['summer_water_demand_mm']:>8} -> {recent['summer_water_demand_mm']:<9}"
            f"{base['summer_water_balance_mm']:>8} -> {recent['summer_water_balance_mm']:<9}"
            f"{delta:>+9}"
        )

    print("\n=== A1: ANNUAL RAINFALL (mm/year) — the misleading number ===")
    for record in records:
        base, recent = record["baseline"], record["recent"]
        print(
            f"  {record['location']['name']:<12} {base['precip_mm']} -> {recent['precip_mm']}"
            f"   dry streak {base['max_dry_streak_days']} -> {recent['max_dry_streak_days']} days"
        )

    print("\n=== A1: SIGNALS ===")
    for record in records:
        print(f"  {record['location']['name']:<12} {', '.join(record['signals'])}")

    print("\n=== A2: MODEL SPREAD, days >=30C in 2031-2040 ===")
    for record in records:
        outlook = record.get("outlook")
        name = record["location"]["name"]
        if not outlook:
            print(f"  {name:<12} no projection returned")
            continue
        low, high = outlook["hot_days_30_range"]
        per_model = ", ".join(
            f"{key.split('_')[0]}={value['hot_days_30']:.0f}"
            for key, value in outlook["per_model"].items()
        )
        print(
            f"  {name:<12} recent={record['recent']['hot_days_30']:<6.1f}"
            f"projected {low:.0f}-{high:.0f}   [{per_model}]"
        )

    print("\n=== A3: SOILGRIDS ===")
    for name, elapsed, soil in soil_results:
        status = "ok" if soil else "no data returned"
        print(f"  {name:<12} {elapsed:>6.1f}s  {status}")

    # Never let a rate-limited run replace good committed data with a short or
    # empty file. Open-Meteo starts returning 429s well before all pins finish.
    if OUTPUT.exists():
        existing = json.loads(OUTPUT.read_text(encoding="utf-8"))
        if len(records) < len(existing):
            print(
                f"\nRefusing to write: got {len(records)} records but "
                f"data/{OUTPUT.name} already holds {len(existing)}. "
                "Existing file left untouched — retry when the rate limit clears."
            )
            return

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(records, indent=2), encoding="utf-8")
    print(f"\nWrote {len(records)} records to data/{OUTPUT.name}")


if __name__ == "__main__":
    main()
