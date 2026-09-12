import type { CropId, DemoParcel } from "./types";

/** Serbia / Vojvodina demo parcels for a reliable happy path. */
export const DEMO_PARCELS: DemoParcel[] = [
  {
    id: "vojvodina-maize",
    name: "Near Novi Sad (maize belt)",
    region: "Vojvodina, Serbia",
    lat: 45.2671,
    lon: 19.8335,
    defaultCrop: "maize",
    notes: "Typical chernozem plains — primary demo pin.",
  },
  {
    id: "banat-wheat",
    name: "Banat wheat field",
    region: "Vojvodina, Serbia",
    lat: 45.381,
    lon: 20.39,
    defaultCrop: "wheat",
    notes: "Slightly drier Banat conditions.",
  },
  {
    id: "srem-sunflower",
    name: "Srem sunflower strip",
    region: "Vojvodina, Serbia",
    lat: 44.978,
    lon: 19.612,
    defaultCrop: "sunflower",
    notes: "Western Srem — good for sunflower demo.",
  },
];

export const CROPS: { id: CropId; label: string; hint: string }[] = [
  { id: "maize", label: "Maize", hint: "Heat + mid-season drought sensitive" },
  { id: "wheat", label: "Winter wheat", hint: "Spring heat + waterlogging risk" },
  {
    id: "sunflower",
    label: "Sunflower",
    hint: "Deep-rooted; still needs early moisture",
  },
];

export function findParcel(id?: string): DemoParcel | undefined {
  if (!id) return undefined;
  return DEMO_PARCELS.find((p) => p.id === id);
}

export function nearestParcel(lat: number, lon: number): DemoParcel {
  let best = DEMO_PARCELS[0];
  let bestD = Number.POSITIVE_INFINITY;
  for (const p of DEMO_PARCELS) {
    const d = (p.lat - lat) ** 2 + (p.lon - lon) ** 2;
    if (d < bestD) {
      bestD = d;
      best = p;
    }
  }
  return best;
}
