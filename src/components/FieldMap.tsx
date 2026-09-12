"use client";

import { MapContainer, TileLayer, Marker, useMapEvents, useMap } from "react-leaflet";
import L from "leaflet";
import { useEffect } from "react";
import "leaflet/dist/leaflet.css";

const pinIcon = L.divIcon({
  className: "soilshift-pin",
  html: `<span style="
      display:block;width:16px;height:16px;border-radius:999px;
      background:#2f5f46;border:2px solid #f3faf5;
      box-shadow:0 0 0 5px rgba(47,95,70,.2),0 6px 14px rgba(27,45,36,.25);
    "></span>`,
  iconSize: [16, 16],
  iconAnchor: [8, 8],
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
        url="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png"
      />
      <Marker position={[lat, lon]} icon={pinIcon} />
      <ClickHandler onPick={onPick} />
      <Recenter lat={lat} lon={lon} />
    </MapContainer>
  );
}
