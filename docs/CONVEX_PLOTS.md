# Convex plot locker (~30 minutes)

Give Convex a real job in AgriSense: **save the current demo pin as a farmer plot**, then list “My plots” in the Streamlit sidebar.

Without Convex, the same UI writes to `data/saved_plots.local.json` so the demo never blocks.

## What you get

| Piece | Role |
| --- | --- |
| `convex/schema.ts` | `plots` table |
| `convex/plots.ts` | `save` / `list` / `clear` |
| `convex/http.ts` | `GET/POST /plots` for Python |
| `agrisense/plots_store.py` | Streamlit client (Convex or local) |
| Sidebar **Save farmer plot** | Name + Save + list |

## Setup (≈30 min)

### 1. Install + log in (≈5 min)

```bash
cd /path/to/repo
npm install
npx convex dev
```

Browser login → create/link a project. Leave `convex dev` running (it generates `convex/_generated/`).

### 2. Copy the HTTP URL (≈2 min)

In the Convex dashboard (or terminal), copy the **HTTP Actions** URL:

```text
https://<your-deployment>.convex.site
```

### 3. Point Streamlit at it (≈1 min)

```bash
export CONVEX_SITE_URL="https://<your-deployment>.convex.site"
# optional shared secret (also set PLOTS_HTTP_TOKEN in Convex dashboard env)
# export PLOTS_HTTP_TOKEN="hackathon-demo"
streamlit run app.py
```

### 4. Demo click path (≈1 min)

1. Sidebar → pin **Zrenjanin**
2. Plot name: `Milan – maize`
3. **Save plot**
4. Sidebar list shows the row (backend: **convex**)

Pitch line: *“Climate math stays in pins.json; Convex is the plot locker — saved fields survive refresh and can sync to another screen.”*

## Optional: lock the HTTP route

```bash
npx convex env set PLOTS_HTTP_TOKEN 'hackathon-demo'
export PLOTS_HTTP_TOKEN='hackathon-demo'
```

## Offline / no Convex account

Skip steps 1–3. Leave `CONVEX_SITE_URL` unset. Saves go to `data/saved_plots.local.json` (gitignored). Sidebar shows `backend: local`.

## Not in scope (on purpose)

Map drawing, GPS, auth, email outreach — keep this under 30 minutes for main-track / Convex sponsor credit.
