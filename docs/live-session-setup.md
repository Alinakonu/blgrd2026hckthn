# SoilShift — live session setup

How the team gets a **live** demo for the Grok Bot Serbia Hackathon (freeze target **18:00**, official submit **19:00**).

## Option A — Local (fastest for rehearsal)

```bash
git checkout cursor/soilshift-mvp-scaffold-f4e3
npm install
cp .env.example .env.local   # keep USE_FIXTURES=1 for pitch safety
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

**Happy path (~60s):** Near Novi Sad parcel → maize → **2050s** → fixtures on → **Run adaptation plan** → show stress score + top 3 checklist items.

## Option B — Render (public HTTPS URL — required for submit)

1. At check-in, redeem **Render** promo credits (Stack → Billing → promo).
2. [Render Dashboard](https://dashboard.render.com) → **New → Web Service**.
3. Connect GitHub repo `Alinakonu/blgrd2026hckthn`.
4. Settings:
   - **Branch:** `cursor/soilshift-mvp-scaffold-f4e3` (or `main` after merge)
   - **Runtime:** Node
   - **Build command:** `npm install && npm run build`
   - **Start command:** `npm start`
   - Or use Blueprint: `render.yaml` in repo root
5. Environment variables:

| Key | Value |
| --- | --- |
| `USE_FIXTURES` | `1` |
| `NODE_VERSION` | `22` |

6. Deploy → wait for green → open the `*.onrender.com` URL.
7. Smoke: `/api/health` then run the Novi Sad happy path once on the live URL.
8. Paste the live URL into the hackathon submit form + README.

**If Render is slow or credits missing:** keep Option A ready for the video; get HTTPS up before 18:00 if at all possible (judges want a non-localhost URL).

## Option C — Cursor Cloud / “Try Live”

If this agent run exposes a **Try Live / desktop** link in the Cursor Agents UI, you can show the running environment there for mentors. That is **not** a substitute for the public Render URL on the submit form — treat it as a backup walkthrough surface only.

## Daytona (optional prize track)

```bash
# Inside a Daytona sandbox (or locally)
npm run snapshot:fixture
# or live APIs with auto-fallback:
npm run snapshot -- --lat 45.2671 --lon 19.8335 --horizon 2050s
```

Shows SoilGrids/Open-Meteo (or fixtures) as JSON — good for “we used Daytona for the climate/soil fetch” story.

## Pre-demo checklist (lock by 18:00)

- [ ] Public GitHub repo URL ready
- [ ] Live demo URL (Render) opens on phone + laptop
- [ ] Fixtures path works without Wi‑Fi flake (`USE_FIXTURES=1`)
- [ ] 3-minute video recorded (Loom/YouTube): pin → 2050s → top 3 actions
- [ ] Submit form draft filled (title, description, repo, demo URL, video URL)
- [ ] One teammate owns the live click-through; another owns the form submit at 19:00
- [ ] Disclaimer visible (“decision support, not certified agronomy”)
- [ ] LinkedIn intel stub pointed at verbally as “next hook,” not claimed as shipped

## Env vars (quick reference)

| Var | Purpose |
| --- | --- |
| `USE_FIXTURES` | `1` forces cached Vojvodina parcels (demo-safe) |
| `NEXT_PUBLIC_CONVEX_URL` | Optional later — see `convex/README.md` |
| `PORT` | Set by Render automatically |

No API keys required for the MVP happy path.
