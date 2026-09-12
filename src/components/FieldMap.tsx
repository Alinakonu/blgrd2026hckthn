"use client";

import { MapContainer, TileLayer, Marker, useMapEvents, useMap } from "react-leaflet";
import L from "leaflet";
import { useEffect } from "react";
import "leaflet/dist/leaflet.css";

const pinIcon = L.divIcon({
  className: "soilshift-pin",
  html: `<span style="
      display:block;width:18px;height:18px;border-radius:999px;
      background:#d6ff4b;border:2px solid #0a1008;
      box-shadow:0 0 0 6px rgba(214,255,75,.25),0 8px 20px rgba(0,0,0,.45);
    "></span>`,
  iconSize: [18, 18],
  iconAnchor: [9, 9],
});

function ClickHandler({ onPick }: { onPick: (lat: number, lon: number) => void }) {
  useMapEvents({
    click(e) {
      onPick(e.latlng.lat, e.latlng.lng);
    },
  });
  return null;
}

function Recenter({ lat, lon }: { lat: number; lon: number }) {
  const map = useMap();
  useEffect(() => {
    map.setView([lat, lon], map.getZoom(), { animate: true });
  }, [lat, lon, map]);
  return null;
}

export default function FieldMap({
  lat,
  lon,
  onPick,
}: {
  lat: number;
  lon: number;
  onPick: (lat: number, lon: number) => void;
}) {
  return (
    <MapContainer
      center={[lat, lon]}
      zoom={8}
      className="h-full w-full"
      scrollWheelZoom
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> · CARTO'
        url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
      />
      <Marker position={[lat, lon]} icon={pinIcon} />
      <ClickHandler onPick={onPick} />
      <Recenter lat={lat} lon={lon} />
    </MapContainer>
  );
}
