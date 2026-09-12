# Crop recommender — data investigation (B2)

Investigated from the data side. Conclusion first, then why.

**Verdict: drop the Kaggle crop-recommendation dataset. Use a small FAO-constant model instead.** It is implemented in `agrisense/crops.py` and runs against the existing `data/pins.json` with no extra downloads, no training, and no Kaggle credentials.

---

## 1. Why the Kaggle dataset fails here

`atharvaingle/crop-recommendation-dataset` is the obvious choice and it is the wrong one for this project, for three reasons that have nothing to do with model quality:

**It answers a different question.** Its 22 labels are rice, maize, chickpea, kidney beans, pigeon peas, moth beans, mung bean, black gram, lentil, pomegranate, banana, mango, grapes, watermelon, muskmelon, apple, orange, papaya, coconut, cotton, jute, coffee. That is an Indian cropping system. Of Serbia's five major arable crops — maize, wheat, sunflower, soybean, sugar beet — only maize appears at all. A model that cannot name wheat cannot advise a Vojvodina farmer, and recommending mango near Subotica in front of Serbian judges ends the demo.

**Its inputs are not the ones we measured.** It keys on N, P, K, pH and rainfall. We have no real soil chemistry — SoilGrids returns nulls across Europe — so N, P, K and pH would all be slider guesses. The model would then be reacting mostly to numbers the user invented, which makes the output untraceable.

**It is static where our signal is a trend.** It maps one snapshot of conditions to one crop label. Our entire finding is a *change* between two decades. A classifier trained on absolute values has no way to express "your maize is getting 62 mm thirstier than it was."

Kaggle access also needs an API token, which is avoidable setup on a clock.

## 2. What replaces it

A scoring model over Serbia's actual crops, using published constants and our measured ET0.

**Crop water demand** uses the FAO-56 method, `ETc = Kc × ETo`. The `ETo` term is `et0_fao_evapotranspiration`, already in every `pins.json` record, so demand is derived from measured data rather than looked up. `Kc` mid-season values come from FAO Irrigation Water Management Training Manual 3, Table 12.

**Irrigation gap** is `ETc − summer rainfall` over June–August. Positive is normal for summer crops in Serbia; what matters is how it moves between decades.

**Drought sensitivity** is FAO Table 14, mapped to a 1–5 rank. Maize is `medium-high`; wheat, sunflower, soybean and sugar beet are `low-medium`; sorghum is `low`.

**Sowing areas** are from the Republic Statistical Office of Serbia, 2026 release, so the model weights crops by what is actually planted: maize 500,759 ha in Vojvodina, sunflower 220,139, soybean 172,117, sugar beet 31,539.

### The timing weight is what makes it work

The first version scored every crop almost identically — +62, +61, +61, +61, +60 mm. That is unavoidable with Kc alone: every crop at one location sees the same ET0, and the FAO Kc values span only 1.10 to 1.20, so demand cannot separate them by more than a few percent.

The real differentiator is *when* a crop is vulnerable. Winter wheat fills grain in May and is off the field by early July, so a worsening July–August deficit barely reaches it. Soybean sets pods directly into it. So exposure is weighted by the fraction of the crop's moisture-sensitive window falling in June–August:

```
exposure = (gap widening / 50) × (drought sensitivity / 2) × (summer overlap)
```

Wheat's overlap is 0.33, maize's is 1.00. That single factor moved wheat from "at risk" to "stable" at every pin, which matches how Serbian farmers actually treat the two crops.

## 3. What it produces

Exposure scores, higher is worse:

| Crop | Summer overlap | Novi Sad | Zrenjanin | Subotica | Kraljevo | Belgrade | Niš |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Maize | 1.00 | **2.48** | **2.40** | 1.28 | 1.00 | 0.28 | −0.56 |
| Sunflower | 1.00 | 1.22 | 1.18 | 0.60 | 0.46 | 0.10 | −0.30 |
| Soybean | 1.00 | 1.20 | 1.12 | 0.58 | 0.42 | 0.08 | −0.32 |
| Sugar beet | 0.75 | 0.92 | 0.89 | 0.45 | 0.35 | 0.08 | −0.22 |
| Sorghum | 1.00 | 0.60 | 0.56 | 0.29 | 0.21 | 0.04 | −0.16 |
| Wheat | 0.33 | 0.41 | 0.39 | 0.20 | 0.15 | 0.03 | −0.10 |

Three things a judge can check:

1. **Maize is both Serbia's largest crop and its most exposed one.** 500,759 ha in Vojvodina, FAO drought sensitivity `medium-high`, peak demand squarely in the months that are deteriorating. Its irrigation gap at Novi Sad widened from 327 to 389 mm.
2. **The adaptation case is quantified, not asserted.** Sorghum scores 0.60 against maize's 2.48 at Novi Sad — roughly a fourfold reduction in exposure, traceable to one FAO sensitivity band and the same measured ET0.
3. **Two locations return "no change indicated."** Belgrade and Niš produce no at-risk crops and no alternatives. A model that flagged every location would be less believable, not more.

## 4. Known limitation: growing degree days are relative only

`pins.json` carries `growing_degree_days` on the maize convention: base 10 °C, capped at 30 °C, accumulated April–September. Serbian pins land at 1,494–1,864.

**Do not compare that to published maturity requirements.** US extension figures put maize at 2,400–2,900 GDD, which would imply maize cannot be grown in Serbia — against 938,209 hectares of it. The gap comes from different accumulation windows and base temperatures; European maturity groups use their own convention. Wheat and barley use base 0, sunflower base 6–8, so a single base-10 figure cannot serve them all.

The model therefore uses GDD only as a **relative** signal. A rise of 168 at Novi Sad (+10.0%) supports "longer-maturity varieties are now viable," which is a real and useful recommendation, without claiming any absolute crop fit.

`climate.py` now also computes `growing_degree_days_base0` for cool-season crops, but the committed `pins.json` predates it — see the rate-limit note in `docs/DATA_LIMITS.md`.

## 5. Handoff to Track B

```python
from agrisense import crops
assessment = crops.assess(record)     # record = one entry from data/pins.json
assessment["verdict"]                  # "action_needed" | "no_change_indicated"
assessment["most_exposed"]             # crop key, or None when nothing is deteriorating
assessment["crops_at_risk"]            # ordered worst first
assessment["adaptation_candidates"]    # only populated when something is at risk
assessment["crops"]                    # full per-crop detail for a table
```

Inspect everything with `python scripts/preview_advice.py`.

Two UI cautions. `most_exposed` is `None` at Belgrade and Niš by design — render "no change indicated" rather than an empty crop card. And `exposure_score` goes negative where conditions improved; if you colour-scale it, make sure negative reads as good.
