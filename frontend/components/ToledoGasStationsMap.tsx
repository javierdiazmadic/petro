'use client';

import { useState, useEffect } from 'react';
import { toledoAPI } from '@/lib/api';

interface GasStation {
  id?: string | number;
  name?: string;
  nombre?: string;
  brand?: string;
  location?: {
    latitude: number;
    longitude: number;
  };
  coordinates?: {
    lat: number;
    lng: number;
  };
  prices?: {
    gasolina_95?: number;
    gasolina_98?: number;
    gasoleoa?: number;
  };
  price_gasolina_95?: number;
  price_gasolina_98?: number;
  price_gasoleoa?: number;
  timestamp?: string;
}

interface ToledoGasStationsMapProps {
  showBrands?: boolean;
}

export function ToledoGasStationsMap({ showBrands = true }: ToledoGasStationsMapProps) {
  const [stations, setStations] = useState<GasStation[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedStation, setSelectedStation] = useState<GasStation | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Toledo city coordinates (center)
  const TOLEDO_CENTER = { lat: 39.8562, lng: -4.0274 };

  useEffect(() => {
    const fetchStations = async () => {
      try {
        setLoading(true);
        const res = await toledoAPI.getAllStations(100);
        if (res?.data?.stations) {
          setStations(res.data.stations);
        }
        setError(null);
      } catch (err) {
        console.error('Error fetching stations:', err);
        setError('Error al cargar gasolineras');
      } finally {
        setLoading(false);
      }
    };

    fetchStations();
  }, []);

  const getBrandLogo = (brand?: string) => {
    if (!brand) return '⛽'; // Generic icon for no brand

    const brandLower = brand.toLowerCase();

    // Brand logos/emojis
    const brandIcons: Record<string, string> = {
      'repsol': '🔴',
      'repsolya': '🔴',
      'cepsa': '🟦',
      'carrefour': '🟥',
      'leclerc': '🟧',
      'bp': '🟩',
      'shell': '🟪',
      'esso': '🟨',
      'alcampo': '🟧',
      'eroski': '🟦',
      'dia': '🟥',
      'galp': '🟩',
    };

    for (const [key, icon] of Object.entries(brandIcons)) {
      if (brandLower.includes(key)) {
        return icon;
      }
    }

    return '⛽'; // Default generic icon
  };

  const getStationName = (station: GasStation) => {
    return station.name || station.nombre || 'Gasolinera';
  };

  const getCoordinates = (station: GasStation) => {
    if (station.coordinates) {
      return station.coordinates;
    }
    if (station.location) {
      return { lat: station.location.latitude, lng: station.location.longitude };
    }
    // Default to Toledo center if no coordinates
    return TOLEDO_CENTER;
  };

  return (
    <div className="bg-white rounded-xl shadow-lg p-8 mb-12">
      <h2 className="text-3xl font-bold text-gray-900 mb-6 flex items-center gap-2">
        <span className="text-4xl">🗺️</span> Mapa de Gasolineras - Toledo
      </h2>

      {loading ? (
        <div className="text-center py-12">
          <p className="text-gray-500">Cargando mapa...</p>
        </div>
      ) : error ? (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-600">
          {error}
        </div>
      ) : (
        <>
          {/* Interactive Map Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-4 gap-4 mb-8">
            {stations && stations.length > 0 ? (
              stations.map((station, idx) => (
                <button
                  key={idx}
                  onClick={() => setSelectedStation(station)}
                  className={`p-4 rounded-lg border-2 transition text-left ${
                    selectedStation === station
                      ? 'border-blue-600 bg-blue-50'
                      : 'border-gray-200 bg-white hover:border-gray-300'
                  }`}
                >
                  <div className="flex items-center gap-2 mb-2">
                    <span className="text-2xl">{getBrandLogo(station.brand)}</span>
                    <span className="font-bold text-sm">{getStationName(station).substring(0, 20)}</span>
                  </div>
                  <div className="text-xs text-gray-600 mb-2">
                    {station.coordinates?.lat.toFixed(4) || 'N/A'}, {station.coordinates?.lng.toFixed(4) || 'N/A'}
                  </div>
                  <div className="space-y-1 text-xs">
                    {station.price_gasolina_95 && (
                      <div className="text-blue-600 font-bold">
                        G95: €{station.price_gasolina_95.toFixed(3)}/L
                      </div>
                    )}
                    {station.price_gasoleoa && (
                      <div className="text-green-600 font-bold">
                        Gasóleo: €{station.price_gasoleoa.toFixed(3)}/L
                      </div>
                    )}
                  </div>
                </button>
              ))
            ) : (
              <p className="col-span-4 text-gray-500 text-center py-8">No hay gasolineras disponibles</p>
            )}
          </div>

          {/* Selected Station Details */}
          {selectedStation && (
            <div className="bg-gradient-to-r from-blue-50 to-green-50 rounded-lg p-6 border-2 border-blue-300">
              <div className="flex items-start justify-between mb-4">
                <div>
                  <h3 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
                    <span className="text-4xl">{getBrandLogo(selectedStation.brand)}</span>
                    {getStationName(selectedStation)}
                  </h3>
                  <p className="text-sm text-gray-600 mt-1">
                    Marca: {selectedStation.brand || 'Marca Blanca'}
                  </p>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                <div className="bg-white rounded-lg p-4 border border-blue-200">
                  <p className="text-sm text-gray-600 font-medium">Gasolina 95</p>
                  <p className="text-3xl font-bold text-blue-600 mt-2">
                    €{selectedStation.price_gasolina_95?.toFixed(3) || 'N/A'}/L
                  </p>
                </div>

                {selectedStation.price_gasolina_98 && (
                  <div className="bg-white rounded-lg p-4 border border-purple-200">
                    <p className="text-sm text-gray-600 font-medium">Gasolina 98</p>
                    <p className="text-3xl font-bold text-purple-600 mt-2">
                      €{selectedStation.price_gasolina_98.toFixed(3)}/L
                    </p>
                  </div>
                )}

                <div className="bg-white rounded-lg p-4 border border-green-200">
                  <p className="text-sm text-gray-600 font-medium">Gasóleo A</p>
                  <p className="text-3xl font-bold text-green-600 mt-2">
                    €{selectedStation.price_gasoleoa?.toFixed(3) || 'N/A'}/L
                  </p>
                </div>
              </div>

              <div className="bg-white rounded-lg p-4 border border-gray-200 text-sm">
                <p className="text-gray-600 mb-2">
                  <strong>Última actualización:</strong>{' '}
                  {selectedStation.timestamp
                    ? new Date(selectedStation.timestamp).toLocaleString('es-ES')
                    : 'No disponible'}
                </p>
                <p className="text-gray-600">
                  <strong>Coordenadas:</strong> {getCoordinates(selectedStation).lat.toFixed(6)}, {getCoordinates(selectedStation).lng.toFixed(6)}
                </p>
              </div>
            </div>
          )}

          <div className="mt-6 p-4 bg-blue-50 rounded-lg border border-blue-200 text-sm text-gray-600">
            <p>
              <strong>Total de gasolineras:</strong> {stations?.length || 0} |
              <strong> Selecciona una gasolinera</strong> en la cuadrícula de arriba para ver sus precios actualizados
            </p>
          </div>
        </>
      )}
    </div>
  );
}
