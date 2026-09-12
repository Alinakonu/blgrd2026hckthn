#!/usr/bin/env python3
"""Build the compressed AgriSense demo deck (16:9).

Original sparse field-day slides, plus a climate opener and a farmer
through-line: every slide is his problem, then how the app answers it.

  pip install python-pptx
  python scripts/build_demo_pptx.py
"""

from __future__ import annotations

from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "AgriSense-demo.pptx"
OUT_DOCS = ROOT / "docs" / "AgriSense-demo.pptx"

BG = RGBColor(0xE6, 0xED, 0xE7)
INK = RGBColor(0x1B, 0x2D, 0x24)
INK_SOFT = RGBColor(0x3E, 0x53, 0x49)
MUTED = RGBColor(0x6A, 0x7C, 0x72)
ACCENT = RGBColor(0x2F, 0x5F, 0x46)
DANGER = RGBColor(0xA8, 0x48, 0x40)
PANEL = RGBColor(0xFF, 0xFC, 0xF8)
PANEL_DANGER = RGBColor(0xFF, 0xF6, 0xF2)
PANEL_GOOD = RGBColor(0xEC, 0xF6, 0xEF)
RULE = RGBColor(0xC9, 0xD3, 0xCC)
SERIF = "Georgia"
SANS = "Calibri"

SLIDE_W = Inches(13.333)
SLIDE_H = Inches(7.5)
TOTAL = 9


def set_run(run, text, size, color, font=SERIF, bold=False, italic=False):
    run.text = text
    run.font.size = Pt(size)
    run.font.color.rgb = color
    run.font.name = font
    run.font.bold = bold
    run.font.italic = italic


def textbox(slide, left, top, width, height):
    box = slide.shapes.add_textbox(left, top, width, height)
    tf = box.text_frame
    tf.word_wrap = True
    tf.clear()
    return box, tf


def para(
    tf,
    text,
    size,
    color,
    font=SERIF,
    bold=False,
    italic=False,
    align=PP_ALIGN.LEFT,
    space_before=0,
    space_after=0,
    first=False,
):
    p = tf.paragraphs[0] if first else tf.add_paragraph()
    if first:
        p = tf.paragraphs[0]
        p.clear()
    p.alignment = align
    p.space_before = Pt(space_before)
    p.space_after = Pt(space_after)
    run = p.add_run()
    set_run(run, text, size, color, font, bold, italic)
    return p


def mixed(tf, parts, align=PP_ALIGN.LEFT, space_before=0, space_after=0, first=False):
    p = tf.paragraphs[0] if first else tf.add_paragraph()
    if first:
        p = tf.paragraphs[0]
        p.clear()
    p.alignment = align
    p.space_before = Pt(space_before)
    p.space_after = Pt(space_after)
    for text, size, color, font, bold in parts:
        run = p.add_run()
        set_run(run, text, size, color, font, bold)
    return p


def card(slide, left, top, width, height, fill=PANEL):
    sh = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    sh.fill.solid()
    sh.fill.fore_color.rgb = fill
    sh.line.color.rgb = RULE
    sh.line.width = Pt(1)
    try:
        sh.adjustments[0] = 0.16
    except Exception:
        pass
    return sh


def oval(slide, left, top, width, height, fill):
    sh = slide.shapes.add_shape(MSO_SHAPE.OVAL, left, top, width, height)
    sh.fill.solid()
    sh.fill.fore_color.rgb = fill
    sh.line.fill.background()
    return sh


def set_bg(slide):
    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = BG
    oval(slide, Inches(-1.8), Inches(-2.2), Inches(7.2), Inches(4.8), RGBColor(0xC5, 0xD8, 0xCC))
    oval(slide, Inches(8.6), Inches(-2.0), Inches(6.4), Inches(4.4), RGBColor(0xE8, 0xDC, 0xC8))
    oval(slide, Inches(3.2), Inches(5.4), Inches(8.0), Inches(4.2), RGBColor(0xB8, 0xCC, 0xBE))


def notes(slide, text):
    slide.notes_slide.notes_text_frame.text = text


def blank(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_bg(slide)
    return slide


def footer(slide, n):
    box, tf = textbox(slide, Inches(0.7), Inches(7.18), Inches(10.5), Inches(0.24))
    para(
        tf,
        "AgriSense  ·  Milan’s field  ·  not an official forecast",
        10,
        MUTED,
        SANS,
        first=True,
    )
    box, tf = textbox(slide, Inches(11.5), Inches(7.18), Inches(1.1), Inches(0.24))
    para(tf, f"{n} / {TOTAL}", 10, MUTED, SANS, align=PP_ALIGN.RIGHT, first=True)


def problem_line(slide, text):
    """Farmer's problem — top of every slide."""
    box, tf = textbox(slide, Inches(0.85), Inches(0.28), Inches(11.6), Inches(0.42))
    para(tf, "HIS PROBLEM  ·  " + text, 13, MUTED, SANS, True, first=True)


def solution_line(slide, text):
    """How AgriSense answers — bottom of every slide."""
    box, tf = textbox(slide, Inches(0.85), Inches(6.55), Inches(11.6), Inches(0.52))
    para(tf, "AGRISENSE  ·  " + text, 15, ACCENT, SANS, True, first=True)


def eyebrow(slide, left, top, width, text, align=PP_ALIGN.LEFT):
    box, tf = textbox(slide, left, top, width, Inches(0.32))
    para(tf, text.upper(), 12, MUTED, SANS, True, align=align, first=True)


def build():
    prs = Presentation()
    prs.slide_width = SLIDE_W
    prs.slide_height = SLIDE_H

    # ------------------------------------------------------------------ 1. Title
    s = blank(prs)
    footer(s, 1)
    problem_line(s, "Milan farms maize and wheat outside Novi Sad. He must order seed in February — before he knows if the year was actually dry.")
    eyebrow(s, Inches(0.85), Inches(1.85), Inches(11.6), "Serbia  ·  one farmer  ·  one plot", PP_ALIGN.CENTER)
    box, tf = textbox(s, Inches(0.7), Inches(2.25), Inches(11.9), Inches(1.5))
    para(tf, "AgriSense", 76, INK, SERIF, True, align=PP_ALIGN.CENTER, first=True)
    box, tf = textbox(s, Inches(1.2), Inches(3.9), Inches(10.9), Inches(1.3))
    para(
        tf,
        "The climate is changing. His rain gauge still looks fine.",
        24,
        INK_SOFT,
        SERIF,
        italic=True,
        align=PP_ALIGN.CENTER,
        first=True,
        space_after=8,
    )
    para(
        tf,
        "A land copilot for the field he actually plants.",
        20,
        INK_SOFT,
        SANS,
        align=PP_ALIGN.CENTER,
    )
    solution_line(s, "We do not brief him on the planet. We show what already happened on his plot — and what to do next.")
    notes(
        s,
        "Meet Milan: Vojvodina, maize and wheat, seed order in February. "
        "AgriSense is his plot copilot, not a climate TED talk.",
    )

    # ------------------------------------------------------------------ 2. Climate problem
    s = blank(prs)
    footer(s, 2)
    problem_line(s, "Headlines say Serbia is getting hotter and wilder. His seed catalogue is still last year’s. The country is not a field.")
    eyebrow(s, Inches(0.85), Inches(0.85), Inches(11.6), "The climate he already feels")
    box, tf = textbox(s, Inches(0.85), Inches(1.2), Inches(11.6), Inches(1.35))
    para(tf, "Hotter summers. Some years drown. Some years burn.", 32, INK, SERIF, True, first=True, space_after=8)
    para(tf, "That is the climate story. It does not tell him what to plant.", 20, INK_SOFT, SANS)

    items = [
        ("HOTTER", "Heatwaves he can feel. He cannot count them."),
        ("WETTER / DRIER", "Flood years and drought years in the same decade."),
        ("NOT HIS PLOT", "A national headline averages his uncle in Banat with his cousin in Niš."),
    ]
    for i, (lab, hint) in enumerate(items):
        x = Inches(0.85) + i * Inches(4.05)
        card(s, x, Inches(2.85), Inches(3.85), Inches(3.15), PANEL)
        box, tf = textbox(s, x + Inches(0.3), Inches(3.1), Inches(3.25), Inches(2.7))
        para(tf, lab, 14, MUTED, SANS, True, first=True, space_after=10)
        para(tf, hint, 20, INK, SERIF, True)
    solution_line(s, "Climate is the backdrop. The app answers the plot: months, this crop, this seed order.")
    notes(
        s,
        "General climate problem first. Then: a newspaper is not a planting decision. "
        "AgriSense exists because the country average hides the field.",
    )

    # ------------------------------------------------------------------ 3. Three questions
    s = blank(prs)
    footer(s, 3)
    problem_line(s, "He already knows summers feel worse. He does not know whether HIS field got harder to farm — or only the news did.")
    eyebrow(s, Inches(1.5), Inches(0.9), Inches(10.3), "What he actually needs")
    qs = [
        ("01", "What already hit this field?"),
        ("02", "Is my summer drying — even if the year looks wet?"),
        ("03", "Keep maize, change practice, or leave it?"),
    ]
    y = 1.45
    for n, q in qs:
        box, tf = textbox(s, Inches(1.5), Inches(y), Inches(1.1), Inches(0.7))
        para(tf, n, 20, ACCENT, SERIF, True, first=True)
        box, tf = textbox(s, Inches(2.7), Inches(y - 0.06), Inches(9.2), Inches(0.85))
        para(tf, q, 28, INK, SERIF, True, first=True)
        y += 1.15
    solution_line(s, "Those three questions are the product. Pick a pin. See history, summer water, crop plan.")
    notes(s, "His three questions. The rest of the deck answers them in order, as the live app would.")

    # ------------------------------------------------------------------ 4. Novi Sad rain lie
    s = blank(prs)
    footer(s, 4)
    problem_line(s, "Milan’s year-end rain is 609 mm — almost the same as his father’s 599. He nearly orders the same maize, on the same calendar.")
    eyebrow(s, Inches(1.15), Inches(0.82), Inches(11), "Novi Sad  ·  the year he thinks was fine")
    left, top, w, h, gap = Inches(1.15), Inches(1.25), Inches(5.15), Inches(4.55), Inches(0.4)
    card(s, left, top, w, h, PANEL)
    box, tf = textbox(s, left + Inches(0.4), top + Inches(0.4), w - Inches(0.7), Inches(3.8))
    para(tf, "WHAT HE SEES  ·  ANNUAL RAIN", 12, MUTED, SANS, True, first=True)
    mixed(
        tf,
        [
            ("599 ", 44, INK, SERIF, True),
            ("→ ", 32, MUTED, SERIF, False),
            ("609", 44, INK, SERIF, True),
        ],
        space_before=14,
        space_after=12,
    )
    para(tf, "Looks fine. Seed order unchanged.", 18, INK_SOFT, SANS)

    card(s, left + w + gap, top, w, h, PANEL_DANGER)
    box, tf = textbox(s, left + w + gap + Inches(0.4), top + Inches(0.4), w - Inches(0.7), Inches(3.8))
    para(tf, "WHAT THE APP SHOWS  ·  JUNE–AUGUST", 12, MUTED, SANS, True, first=True)
    mixed(
        tf,
        [
            ("−241 ", 44, DANGER, SERIF, True),
            ("→ ", 32, MUTED, SERIF, False),
            ("−298", 44, DANGER, SERIF, True),
        ],
        space_before=14,
        space_after=12,
    )
    para(tf, "−57 mm of extra thirst. Hidden in a “stable” year.", 18, INK_SOFT, SANS)
    solution_line(s, "Split the year. Summer rain 187→158 mm, crop demand 428→456. The rain gauge was lying to him.")
    notes(
        s,
        "This is the hook. He almost does nothing. Then point at summer water. "
        "Fifty-seven millimetres more stress, inside a stable year.",
    )

    # ------------------------------------------------------------------ 5. Maize vs wheat
    s = blank(prs)
    footer(s, 5)
    problem_line(s, "Same field, two crops. He would treat maize and wheat as one climate. They do not drink in the same months.")
    eyebrow(s, Inches(1.15), Inches(0.82), Inches(11), "Novi Sad  ·  same climate, different thirst")
    card(s, left, top, w, h, PANEL_DANGER)
    box, tf = textbox(s, left + Inches(0.4), top + Inches(0.4), w - Inches(0.7), Inches(3.9))
    para(tf, "MAIZE  ·  HIS MAIN CROP", 12, MUTED, SANS, True, first=True)
    para(tf, "2.48", 52, DANGER, SERIF, True, space_before=8, space_after=8)
    para(tf, "Drinks June–August — the window that dried. 501k ha in Vojvodina.", 18, INK_SOFT, SANS, space_after=12)
    card(s, left + Inches(0.4), top + Inches(3.55), Inches(2.4), Inches(0.42), RGBColor(0xF8, 0xE8, 0xE6))
    box, tf = textbox(s, left + Inches(0.4), top + Inches(3.56), Inches(2.4), Inches(0.4))
    para(tf, "highest exposure", 12, DANGER, SANS, True, align=PP_ALIGN.CENTER, first=True)

    card(s, left + w + gap, top, w, h, PANEL)
    box, tf = textbox(s, left + w + gap + Inches(0.4), top + Inches(0.4), w - Inches(0.7), Inches(3.9))
    para(tf, "WHEAT  ·  OFF THE FIELD FIRST", 12, MUTED, SANS, True, first=True)
    para(tf, "stable", 52, INK, SERIF, True, space_before=8, space_after=8)
    para(tf, "Grain fill in May. Harvested before the bad July–August.", 18, INK_SOFT, SANS, space_after=12)
    card(s, left + w + gap + Inches(0.4), top + Inches(3.55), Inches(1.1), Inches(0.42), RGBColor(0xE4, 0xF0, 0xE8))
    box, tf = textbox(s, left + w + gap + Inches(0.4), top + Inches(3.56), Inches(1.1), Inches(0.4))
    para(tf, "0.41", 12, ACCENT, SANS, True, align=PP_ALIGN.CENTER, first=True)
    solution_line(s, "The app scores his real crops with FAO water math — not a generic “plant something else.” Maize is the decision. Wheat can wait.")
    notes(s, "Same climate, different crop. Irrigation gap maize 327→389. Wheat escapes the window. That is why we dropped the mango model.")

    # ------------------------------------------------------------------ 6. Zrenjanin
    s = blank(prs)
    footer(s, 6)
    problem_line(s, "His uncle in Banat says the fields scorched. Milan cannot tell if that is weather talk — or a reason to change seed.")
    eyebrow(s, Inches(0.85), Inches(1.15), Inches(11.6), "Zrenjanin  ·  days ≥ 35°C", PP_ALIGN.CENTER)
    box, tf = textbox(s, Inches(0.5), Inches(1.7), Inches(12.3), Inches(2.4))
    mixed(
        tf,
        [
            ("2.7  ", 88, MUTED, SERIF, True),
            ("→  ", 64, MUTED, SERIF, False),
            ("8.0", 88, DANGER, SERIF, True),
        ],
        PP_ALIGN.CENTER,
        first=True,
    )
    box, tf = textbox(s, Inches(0.85), Inches(4.25), Inches(11.6), Inches(1.7))
    para(tf, "Nearly triple. Summer deficit −260 → −312 mm. Worst pin in the set.", 22, INK_SOFT, SANS, align=PP_ALIGN.CENTER, first=True, space_after=8)
    para(tf, "Outlook 46–55 days above 30°C in the 2030s — a range, not a date.", 16, MUTED, SANS, align=PP_ALIGN.CENTER)
    solution_line(s, "The app names the urgent field so he does not average Banat with the rest of Serbia. Heat plus thirst, before the next sowing.")
    notes(s, "Uncle in Zrenjanin. 2.7 to 8.0. Then: we still do not timestamp a 2034 storm. Range, not a forecast.")

    # ------------------------------------------------------------------ 7. Niš
    s = blank(prs)
    footer(s, 7)
    problem_line(s, "His cousin near Niš says nothing changed. If a tool shouts crisis on every map, Milan will not trust it with his seed money.")
    eyebrow(s, Inches(1.15), Inches(0.82), Inches(11), "Niš  ·  the cousin who is fine")
    box, tf = textbox(s, Inches(1.15), Inches(1.15), Inches(11), Inches(1.35))
    para(tf, "No change indicated.", 40, INK, SERIF, True, first=True)
    cw, ch = Inches(5.15), Inches(2.7)
    cy = Inches(2.65)
    card(s, left, cy, cw, ch, PANEL_GOOD)
    box, tf = textbox(s, left + Inches(0.4), cy + Inches(0.35), cw - Inches(0.7), Inches(2.1))
    para(tf, "ANNUAL RAIN", 12, MUTED, SANS, True, first=True)
    mixed(
        tf,
        [
            ("521 ", 40, ACCENT, SERIF, True),
            ("→ ", 28, MUTED, SERIF, False),
            ("682", 40, ACCENT, SERIF, True),
        ],
        space_before=8,
    )
    card(s, left + cw + gap, cy, cw, ch, PANEL_GOOD)
    box, tf = textbox(s, left + cw + gap + Inches(0.4), cy + Inches(0.35), cw - Inches(0.7), Inches(2.1))
    para(tf, "SUMMER WATER", 12, MUTED, SANS, True, first=True)
    mixed(
        tf,
        [
            ("−287 ", 40, ACCENT, SERIF, True),
            ("→ ", 28, MUTED, SERIF, False),
            ("−270", 40, ACCENT, SERIF, True),
        ],
        space_before=8,
    )
    solution_line(s, "The app says spend nothing here. Trust is the feature: it is quiet where the data is quiet.")
    notes(s, "Cousin in Niš. If we skip this slide the pitch is generic alarm. Keep the rotation. Do not spend.")

    # ------------------------------------------------------------------ 8. How the app works
    s = blank(prs)
    footer(s, 8)
    problem_line(s, "He will not download ERA5, FAO tables, or three climate models. He will not read a research paper before February.")
    eyebrow(s, Inches(1.0), Inches(0.85), Inches(11.3), "What he opens instead")
    items = [
        ("MEMORY", "His weather, already counted", "Open ERA5 via one API. Hot days, summer rain, crop demand. The history he could not see on a gauge."),
        ("EXPOSURE", "His crops, not mango", "FAO water math on maize, wheat, sunflower, soybean. The app names which plant drinks in the bad months."),
        ("PLAN", "A report he can read", "Grok writes four parts — what changed, what it means, what to do, what to watch — from measured numbers only. No invented seed brands."),
    ]
    cw = Inches(3.65)
    gap3 = Inches(0.28)
    x0 = Inches(1.0)
    top7 = Inches(1.28)
    h7 = Inches(4.85)
    for i, (lab, title, hint) in enumerate(items):
        x = x0 + i * (cw + gap3)
        card(s, x, top7, cw, h7, PANEL)
        box, tf = textbox(s, x + Inches(0.28), top7 + Inches(0.32), cw - Inches(0.5), Inches(4.35))
        para(tf, lab, 12, MUTED, SANS, True, first=True, space_after=10)
        para(tf, title, 22, INK, SERIF, True, space_after=12)
        para(tf, hint, 15, INK_SOFT, SANS)
    solution_line(s, "One screen: pick the field, see the months, generate the plan. Open data in. Human report out.")
    notes(
        s,
        "He does not fetch APIs. We do. Memory, exposure, plan. LLM explains numbers it did not invent.",
    )

    # ------------------------------------------------------------------ 9. Close
    s = blank(prs)
    footer(s, 9)
    problem_line(s, "February is coming. He still has to lock a seed order for one plot — not for Serbia.")
    eyebrow(s, Inches(0.85), Inches(0.85), Inches(11.6), "Measured  ·  not a forecast", PP_ALIGN.CENTER)
    box, tf = textbox(s, Inches(0.85), Inches(1.2), Inches(11.6), Inches(1.2))
    para(tf, "A decision for Milan’s field.", 40, INK, SERIF, True, align=PP_ALIGN.CENTER, first=True)
    pins = [
        ("Subotica", "MASK", True),
        ("Novi Sad", "HIS PLOT", True),
        ("Zrenjanin", "UNCLE", True),
        ("Belgrade", "FLAT", False),
        ("Kraljevo", "STABLE", False),
        ("Niš", "COUSIN", False),
    ]
    pw, ph, pg = Inches(1.75), Inches(2.05), Inches(0.18)
    total = 6 * pw + 5 * pg
    x = (SLIDE_W - total) / 2
    py = Inches(2.7)
    for name, tag, hot in pins:
        fill = PANEL_DANGER if hot else PANEL
        card(s, x, py, pw, ph, fill)
        oval(
            s,
            x + (pw - Inches(0.16)) / 2,
            py + Inches(0.28),
            Inches(0.16),
            Inches(0.16),
            DANGER if hot else ACCENT,
        )
        box, tf = textbox(s, x + Inches(0.06), py + Inches(0.55), pw - Inches(0.12), Inches(1.3))
        para(tf, name, 13, INK, SANS, True, align=PP_ALIGN.CENTER, first=True, space_after=4)
        para(tf, tag, 11, MUTED, SANS, True, align=PP_ALIGN.CENTER)
        x += pw + pg
    box, tf = textbox(s, Inches(0.85), Inches(4.95), Inches(11.6), Inches(1.35))
    para(
        tf,
        "The rain gauge hid a worse summer on his plot. Banat is urgent. Niš is not.",
        18,
        INK_SOFT,
        SANS,
        align=PP_ALIGN.CENTER,
        first=True,
        space_after=6,
    )
    para(
        tf,
        "Better weather models will sharpen next week and next summer. Today, open data plus a plan he can read.",
        16,
        MUTED,
        SANS,
        align=PP_ALIGN.CENTER,
    )
    solution_line(s, "AgriSense: his history, his crops, his report. Not a forecast. A seed-order decision.")
    notes(
        s,
        "Close on Milan’s February. Novi Sad is his plot, Zrenjanin the uncle, Niš the cousin. "
        "Offer the three clicks in the live app.",
    )

    prs.save(OUT)
    OUT_DOCS.parent.mkdir(parents=True, exist_ok=True)
    prs.save(OUT_DOCS)
    print(f"Wrote {OUT}")
    print(f"Wrote {OUT_DOCS}")


if __name__ == "__main__":
    build()
