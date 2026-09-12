# SoilShift

**Field + crop → soil adaptation for the 2030s / 2050s.**

SoilShift blends the team’s [AgriSense](./idea.md) precision-farming copilot idea (soil telemetry + agentic advice) with the **SoilShift** climate-horizon concept: locate a field, choose a crop, see projected heat/drought stress, and get a **ranked soil-adaptation checklist**. Not a weather app — a “what should this soil change before yields crash” advisor.

Hackathon: Grok Bot Serbia / Cursor Serbia · 12 Sep 2026.

## Happy path (demo script, ~60s)

1. Open the app → demo parcel **Near Novi Sad (maize belt)** is preselected.
2. Keep **Use cached demo fixtures** on (pitch-safe).
3. Set horizon to **2050s** → click **Run adaptation plan**.
4. Show overall stress score, heat/drought bars, soil pH/SOC.
5. Walk top 3 checklist items + citations.
6. Optional: open “AgriSense soil telemetry”, set high N + low moisture, re-run — NPK action rises.
7. Point at the **future: LinkedIn agritech company intel** stub (not implemented).

## Quick start

```bash
npm install
cp .env.example .env.local   # USE_FIXTURES=1 recommended
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

### Scripts

| Command | Purpose |
| --- | --- |
| `npm run dev` | Next.js local UI |
| `npm run build` / `npm start` | Production |
| `npm run snapshot` | Daytona-friendly SoilGrids/Open-Meteo fetch (JSON to stdout) |
| `npm run snapshot:fixture` | Same with fixtures only |

```bash
# Live APIs (falls back to fixtures on failure)
npm run snapshot -- --lat 45.2671 --lon 19.8335 --horizon 2050s

# Fixture-only (Daytona / offline)
npm run snapshot:fixture
```

## Environment variables

| Var | Default | Notes |
| --- | --- | --- |
| `USE_FIXTURES` | unset | `1` / `true` forces cached parcels server-side |
| `NEXT_PUBLIC_CONVEX_URL` | — | Optional; see `convex/README.md` |
| `PORT` | `3000` | Used by `next start` / Render |

No API keys required for the MVP happy path (SoilGrids + Open-Meteo are public; fixtures cover demo).

## Live demo

Full team runbook (local, Render, Cursor Try Live notes, 18:00 freeze checklist):

→ **[Live session setup](./docs/live-session-setup.md)**  
(Project copy also at store `docs/live-session-setup.md`.)

Quick path:

```bash
npm install && cp .env.example .env.local && npm run dev
```

Public HTTPS: deploy this branch on Render with `USE_FIXTURES=1` (see below). Redeem Render credits at check-in.

## Deploy on Render

1. Push this branch / merge to a public GitHub repo.
2. [Render](https://render.com) → **New → Web Service** → connect the repo.
3. Settings (or use `render.yaml`):
   - **Branch:** `cursor/soilshift-mvp-scaffold-f4e3` (or `main` after merge)
   - **Build:** `npm install && npm run build`
   - **Start:** `npm start`
   - **Env:** `USE_FIXTURES=1`, `NODE_VERSION=22`
4. After deploy, hit `/api/health` then run the Novi Sad demo.

Live URL: add here once Render credentials are available.

## Architecture

```
Map pin / demo parcel
    → POST /api/analyze
        → SoilGrids + Open-Meteo (or fixtures)
        → stress scores
        → ranked adaptation checklist
    → UI: StressPanel + AdaptationChecklist
```

- **UI:** Next.js App Router + Tailwind + Leaflet map pin
- **Soil:** [ISRIC SoilGrids](https://www.isric.org/explore/soilgrids) REST
- **Climate:** [Open-Meteo](https://open-meteo.com/) archive + climate APIs
- **Fixtures:** `src/data/fixtures/parcels.json` (3 Vojvodina parcels)
- **Agent-friendly:** `scripts/fetch-field-snapshot.mjs` for Daytona sandboxes
- **Convex:** placeholder under `convex/` for saving plans next
- **LinkedIn intel:** stub only — `src/lib/linkedin-stub.ts`, `/api/linkedin-intel`, UI banner

## What came from where

| Source | What we used |
| --- | --- |
| **Repo `idea.md` (AgriSense)** | Soil telemetry (NPK/pH/moisture) as optional inputs; agentic “plain-language mitigation” framing; crop-focused advice loop. Vision/leaf pathology deferred. |
| **SoilShift concept** | Core product: locate field → baseline soil/climate → 2030s/2050s stress → ranked adaptation checklist + citations + disclaimer. |
| **[gods-eye-view](https://github.com/uhrichsam4/gods-eye-view)** | *Patterns only* (not a code fork): lat/lon place-first UX, offline **fixtures** when third-party APIs flake, **retryable load** cooldown idea (`src/lib/retryable.ts`), and explicit **data credits** on every response (`src/lib/credits.ts`). No Cesium/globe/OSINT layers copied. |
| **Sponsor checklist** | Public repo, Render deploy path, Convex hook, Daytona script, fixture-backed demo before 18:00 freeze. |

## API

### `POST /api/analyze`

```json
{
  "lat": 45.2671,
  "lon": 19.8335,
  "crop": "maize",
  "horizon": "2050s",
  "useFixture": true,
  "parcelId": "vojvodina-maize",
  "telemetry": { "n": 90, "moisture": 30, "ph": 7.1 }
}
```

### `GET /api/health`

### `GET /api/linkedin-intel` — stub (`future: LinkedIn agritech company intel`)

## Disclaimer

Decision support only — not a certified agronomic prescription.
