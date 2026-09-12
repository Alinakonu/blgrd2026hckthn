"""Print the crop assessment and the exact LLM prompt for each pin.

Run: python scripts/preview_advice.py [location-name]
No API key needed — this renders the prompt without calling a model, so Track B
can tune wording before spending tokens.
"""

import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from agrisense import crops as crop_model  # noqa: E402
from agrisense.prompt import build_user_prompt  # noqa: E402

PINS = pathlib.Path(__file__).resolve().parent.parent / "data" / "pins.json"


def main():
    records = json.loads(PINS.read_text(encoding="utf-8"))
    wanted = sys.argv[1].lower() if len(sys.argv) > 1 else None

    print("=== CROP EXPOSURE ACROSS ALL PINS ===\n")
    header = f"{'Location':<12}{'most exposed':<14}{'at risk':<40}{'alternatives'}"
    print(header)
    print("-" * len(header))
    for record in records:
        assessment = crop_model.assess(record)
        at_risk = ", ".join(assessment["crops_at_risk"]) or "none"
        print(
            f"{assessment['location']:<12}"
            f"{assessment['most_exposed'] or '-':<14}"
            f"{at_risk:<40}"
            f"{', '.join(assessment['adaptation_candidates']) or '-'}"
        )

    print("\n=== EXPOSURE SCORE (widening x sensitivity x summer overlap) ===\n")
    names = [r["location"]["name"] for r in records]
    print(f"{'Crop':<12}{'overlap':>9}" + "".join(f"{n:>11}" for n in names))
    print("-" * (21 + 11 * len(names)))
    for key in crop_model.CROPS:
        overlap = crop_model.summer_overlap(crop_model.CROPS[key]["peak_window"])
        cells = []
        for record in records:
            entry = crop_model.assess_crop(record, key)
            cells.append(f"{entry['exposure_score']:>11.2f}" if entry else f"{'n/a':>11}")
        print(f"{crop_model.CROPS[key]['label']:<12}{overlap:>9.2f}" + "".join(cells))

    print("\n=== IRRIGATION GAP BY CROP (mm, summer ETc minus summer rain) ===\n")
    names = [r["location"]["name"] for r in records]
    print(f"{'Crop':<12}" + "".join(f"{n:>13}" for n in names))
    print("-" * (12 + 13 * len(names)))
    for key in crop_model.CROPS:
        cells = []
        for record in records:
            entry = crop_model.assess_crop(record, key)
            cells.append(
                f"{entry['irrigation_gap_recent_mm']:>6} ({entry['gap_widening_mm']:+d})"
                if entry
                else f"{'n/a':>13}"
            )
        print(f"{crop_model.CROPS[key]['label']:<12}" + "".join(cells))

    for record in records:
        if wanted and record["location"]["name"].lower() != wanted:
            continue
        print("\n" + "=" * 70)
        print(f"PROMPT — {record['location']['name']}")
        print("=" * 70)
        print(build_user_prompt(record))
        if wanted:
            break


if __name__ == "__main__":
    main()
