"use client";

import dynamic from "next/dynamic";

const FieldMap = dynamic(() => import("./FieldMap"), {
  ssr: false,
  loading: () => (
    <div className="flex h-full items-center justify-center bg-[var(--map-wash)] text-sm text-[var(--muted)]">
      Loading map…
    </div>
  ),
});

export default function FieldMapClient({
  lat,
  lon,
  onPick,
}: {
  lat: number;
  lon: number;
  onPick: (lat: number, lon: number) => void;
}) {
  return <FieldMap lat={lat} lon={lon} onPick={onPick} />;
}
