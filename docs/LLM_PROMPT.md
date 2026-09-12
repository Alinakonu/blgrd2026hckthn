# LLM action plan — data investigation (B3)

Investigated from the data side: what goes into the prompt, what the model is forbidden to produce, and how to check the output is real. Implemented in `agrisense/prompt.py`.

---

## 1. The design rule

**The model explains and prioritises numbers. It never produces them.**

Every figure that reaches the farmer should be traceable to `data/pins.json` or the FAO constants in `crops.py`. This is not a style preference — it is what makes the demo survive a judge asking "where did that number come from." An LLM that invents a yield percentage or a seed variety gives an answer that cannot be defended, and one fabricated figure discredits the measured ones next to it.

So the prompt hands over a complete data block and asks for interpretation, sequencing and timing. Those are things a language model is actually good at, and they are exactly what the raw indices lack.

## 2. What the data block contains

Built by `build_user_prompt(record)`:

| Section | Source | Why it's there |
| --- | --- | --- |
| Location | `record["location"]` | Anchors advice to a real place |
| Baseline + Recent periods | `pins.json` | The measured change, with units and periods on every line |
| Model range | `record["outlook"]` | Always a range across three models, never a point |
| What the comparison shows | `record["signals"]` | Pre-computed findings, so the model isn't left to infer trends from raw numbers |
| Heat accumulation | `crops.thermal_trend()` | The opportunity side: longer-maturity varieties |
| Crop exposure | `crops.assess()` | Per-crop irrigation gap, FAO sensitivity, peak months, hectares planted |
| Soil | `record["soil"]`, ERA5 moisture | Honest `not available` when SoilGrids has no data |

The `signals` list is doing important work. Rather than hoping the model notices that annual rainfall rose while the summer balance fell, `annual_totals_masking_summer_stress` states it. `SIGNAL_TEXT` in `prompt.py` maps each key to a sentence, so the vocabulary stays fixed and the model's framing is reproducible across runs.

## 3. The guardrails

`SYSTEM_PROMPT` carries seven rules. Four exist because of specific ways this demo can fail:

**No invented numbers, yields, prices or variety names.** The most likely hallucination is a plausible commercial hybrid name. "A shorter-maturity hybrid" is useful advice; "NS-640" is a liability.

**Projections are ranges, called model ranges.** The three climate models disagree by up to 13 days at Novi Sad (44.2 to 56.9). Presenting 52 would be false precision, and calling any of it a forecast would be a claim we cannot support.

**Say so when conditions are stable.** Belgrade and Niš show no deterioration. A model that manufactures concern there would undermine the three locations where the signal is real — and the contrast is the strongest part of the pitch.

**Practice, not brands.** Keeps recommendations inside what the data supports.

The requested structure — what changed, what it means, what to do, what to watch — exists so the output maps onto UI panels instead of arriving as prose that has to be read whole.

## 4. Checking the output

Track B's job on this is a scoring pass, not vibes. For each of the three demo locations, check:

- [ ] Every number in the output appears in the data block. Any that doesn't is a hallucination — tighten rule 1.
- [ ] The projection is stated as a range and labelled as a model range.
- [ ] Maize is identified as the priority at Novi Sad and Zrenjanin. If the model leads with wheat, it ignored the exposure scores.
- [ ] Belgrade or Niš produces a "no change indicated" style answer, not invented alarm.
- [ ] Actions carry months or seasons, not "soon."
- [ ] No commercial product or variety names.

A generic answer usually means the data block was too long and the crop table got lost. Cut the per-model breakdown before cutting the crop exposure lines.

## 5. Running it

Render the prompt without spending tokens:

```bash
python scripts/preview_advice.py            # all pins, plus prompts
python scripts/preview_advice.py "Novi Sad" # one location
```

Then wire to any OpenAI-compatible endpoint. `build_messages` returns the standard chat format, so x.ai works with only a base-URL change:

```python
from agrisense.prompt import build_messages
messages = build_messages(record)
# client.chat.completions.create(model="grok-...", messages=messages)
```

`prompt.py` deliberately has no HTTP client and no API key handling — it is pure string building, so it stays testable offline and Track B owns the transport.

## 6. Cost and latency

The rendered block is roughly 700–900 tokens. With a 300-word cap on the answer, a call is about 1,200 tokens round trip — fast enough to run live in the demo, cheap enough to re-run freely while tuning.

Cache the response per location. Re-generating on every Streamlit rerun will make the UI feel broken, since Streamlit re-executes the whole script on each widget interaction.
