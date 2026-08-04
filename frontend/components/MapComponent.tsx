'use client';

import { useEffect, useRef, useState } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

interface GasStation {
  id?: string;
  nombre?: string;
  name?: string;
  brand?: string;
  latitud?: number;
  longitud?: number;
  latitude?: number;
  longitude?: number;
  precio_gasolina_95?: number;
  price_gasolina_95?: number;
  precio_gasoleoa?: number;
  price_gasoleoa?: number;
  timestamp?: string;
  municipio?: string;
  precios?: {
    gasolina_95?: number;
    gasoleoa?: number;
  };
}

interface MapComponentProps {
  stations: GasStation[];
}

export default function MapComponent({ stations }: MapComponentProps) {
  const mapRef = useRef<L.Map | null>(null);
  const [selectedStation, setSelectedStation] = useState<GasStation | null>(null);

  // Toledo coordinates
  const TOLEDO_CENTER = { lat: 39.8562, lng: -4.0274 };

  useEffect(() => {
    if (!mapRef.current) {
      // Initialize map
      mapRef.current = L.map('map').setView([TOLEDO_CENTER.lat, TOLEDO_CENTER.lng], 10);

      // Add OpenStreetMap tiles
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap contributors',
        maxZoom: 19,
      }).addTo(mapRef.current);

      // Add center marker
      L.marker([TOLEDO_CENTER.lat, TOLEDO_CENTER.lng], {
        icon: L.icon({
          iconUrl: 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMzIiIGhlaWdodD0iMzIiIHZpZXdCb3g9IjAgMCAzMiAzMiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48Y2lyY2xlIGN4PSIxNiIgY3k9IjE2IiByPSIxNSIgZmlsbD0iIzMzMzMmIiBzdHJva2U9IndoaXRlIiBzdHJva2Utd2lkdGg9IjIiLz48L3N2Zz4=',
          iconSize: [32, 32],
          iconAnchor: [16, 16],
        }),
      }).addTo(mapRef.current).bindPopup('Centro de Toledo', { autoClose: false });
    }

    // Clear existing markers (except center)
    if (mapRef.current) {
      mapRef.current.eachLayer((layer: any) => {
        if (layer instanceof L.Marker && !(layer.getLatLng().lat === TOLEDO_CENTER.lat && layer.getLatLng().lng === TOLEDO_CENTER.lng)) {
          mapRef.current?.removeLayer(layer);
        }
      });

      // Add gas station markers
      stations.forEach((station) => {
        const lat = station.latitud || station.latitude;
        const lng = station.longitud || station.longitude;

        if (lat && lng) {
          const price95 = station.price_gasolina_95 || station.precio_gasolina_95 || station.precios?.gasolina_95 || 'N/A';
          const priceGasoleoa = station.price_gasoleoa || station.precio_gasoleoa || station.precios?.gasoleoa || 'N/A';

          const stationName = station.nombre || station.name || 'Gasolinera';

          const marker = L.marker([lat, lng], {
            icon: L.icon({
              iconUrl: 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMzIiIGhlaWdodD0iNDgiIHZpZXdCb3g9IjAgMCAzMiA0OCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cGF0aCBkPSJNMTYgMEMxMi4xMjUgMCA4LjYyODI4IDEuNTc5MjggNi4xMzUwMSA0LjA3MjU1QzMuNjQxNzMgNi41NjU4MiAyIDEwLjA2MjUgMiAxNEM0IDE4IDAgMjAwIDI0IDEwMDAgMjQgMjAwIDI4IDE4IDI4IDE0QzI4IDEwLjA2MjUgMjYuMzU4MyA2LjU2NTgyIDIzLjg2NSA0LjA3MjU1QzIxLjM3MTcgMS41NzkyOCAxNy44NzUgMCAxNiAwWiIgZmlsbD0iIzMzODhGRiIgc3Ryb2tlPSJ3aGl0ZSIgc3Ryb2tlLXdpZHRoPSIyIi8+PHRleHQgeD0iMTYiIHk9IjE2IiBmb250LXNpemU9IjEyIiBmaWxsPSJ3aGl0ZSIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZHk9Ii4zZW0iPuKasCDimrDimaA8L3RleHQ+PC9zdmc+',
              iconSize: [32, 48],
              iconAnchor: [16, 48],
              popupAnchor: [0, -48],
            }),
          }).addTo(mapRef.current!);

          const popupContent = `
            <div class="p-3 min-w-48">
              <h3 class="font-bold text-lg mb-2">${stationName}</h3>
              <p class="text-sm text-gray-600 mb-3">${station.municipio || 'Toledo'}</p>
              <div class="space-y-2">
                <div class="bg-blue-50 p-2 rounded">
                  <p class="text-sm">Gasolina 95</p>
                  <p class="text-lg font-bold text-blue-600">€${typeof price95 === 'number' ? price95.toFixed(3) : price95}/L</p>
                </div>
                <div class="bg-green-50 p-2 rounded">
                  <p class="text-sm">Gasóleo A</p>
                  <p class="text-lg font-bold text-green-600">€${typeof priceGasoleoa === 'number' ? priceGasoleoa.toFixed(3) : priceGasoleoa}/L</p>
                </div>
              </div>
              <p class="text-xs text-gray-500 mt-3">
                Actualizado: ${station.timestamp ? new Date(station.timestamp).toLocaleString('es-ES') : 'N/A'}
              </p>
            </div>
          `;

          marker.bindPopup(popupContent);

          marker.on('click', () => {
            setSelectedStation(station);
          });
        }
      });
    }
  }, [stations]);

  return (
    <>
      <div id="map" className="h-96 rounded-lg border border-gray-200 mb-4" />
      {selectedStation && (
        <div className="bg-gradient-to-r from-blue-50 to-green-50 rounded-lg p-4 border-2 border-blue-300">
          <h3 className="text-lg font-bold text-gray-900">
            {selectedStation.nombre || selectedStation.name || 'Gasolinera'}
          </h3>
          <p className="text-sm text-gray-600">{selectedStation.municipio || 'Toledo'}</p>
          <div className="grid grid-cols-2 gap-2 mt-3">
            <div className="bg-white p-2 rounded border border-blue-200">
              <p className="text-xs text-gray-600">Gasolina 95</p>
              <p className="text-lg font-bold text-blue-600">
                €{(selectedStation.price_gasolina_95 || selectedStation.precio_gasolina_95 || selectedStation.precios?.gasolina_95 || 0).toFixed(3)}/L
              </p>
            </div>
            <div className="bg-white p-2 rounded border border-green-200">
              <p className="text-xs text-gray-600">Gasóleo A</p>
              <p className="text-lg font-bold text-green-600">
                €{(selectedStation.price_gasoleoa || selectedStation.precio_gasoleoa || selectedStation.precios?.gasoleoa || 0).toFixed(3)}/L
              </p>
            </div>
          </div>
          <p className="text-xs text-gray-500 mt-2">
            Actualizado: {selectedStation.timestamp ? new Date(selectedStation.timestamp).toLocaleString('es-ES') : 'N/A'}
          </p>
        </div>
      )}
    </>
  );
}
