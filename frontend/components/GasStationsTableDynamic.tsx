'use client';

import { useEffect, useState } from 'react';

interface Station {
  id?: string;
  nombre?: string;
  name?: string;
  municipio?: string;
  city?: string;
  direction?: string;
  address?: string;
  latitud?: number;
  longitud?: number;
  distancia_km?: number;
  distance_km?: number;
  precios?: {
    gasolina_95?: number;
    gasolina_98?: number;
    gasoleoa?: number;
    gasoleob?: number;
  };
  prices?: {
    gasolina_95?: number;
    gasolina_98?: number;
    gasoleoa?: number;
    gasoleob?: number;
  };
  comparacion_media?: {
    gasolina_95_vs_media?: number;
    gasoleoa_vs_media?: number;
  };
}

interface GasStationsTableDynamicProps {
  selectedFilter: 'todas' | 'repsol';
  apiUrl: string;
}

export function GasStationsTableDynamic({
  selectedFilter,
  apiUrl,
}: GasStationsTableDynamicProps) {
  const [stations, setStations] = useState<Station[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [sortBy, setSortBy] = useState<'price' | 'distance'>('price');

  useEffect(() => {
    const fetchStations = async () => {
      try {
        setLoading(true);
        setError(null);

        const url = selectedFilter === 'todas'
          ? `${apiUrl}/api/v1/toledo/all-stations?max_distance_km=150`
          : `${apiUrl}/api/v1/toledo/repsol?max_distance_km=150`;

        console.log('Fetching from:', url);
        const response = await fetch(url);

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`);
        }

        const data = await response.json();
        console.log('Response data:', data);

        const gasStations = data.gas_stations || [];
        setStations(gasStations);

        if (gasStations.length === 0) {
          setError('No se encontraron gasolineras');
        }
      } catch (err) {
        const errorMsg = err instanceof Error ? err.message : 'Error desconocido';
        setError(`Error al cargar gasolineras: ${errorMsg}`);
        console.error('Fetch error:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchStations();
  }, [selectedFilter, apiUrl]);

  if (loading) {
    return (
      <div className="bg-white rounded-xl shadow-lg p-8">
        <div className="text-center py-12">
          <div className="inline-block">
            <div className="w-8 h-8 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin"></div>
          </div>
          <p className="mt-4 text-gray-500">Cargando gasolineras...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-xl shadow-lg p-8">
        <p className="text-red-600 font-medium">{error}</p>
        <p className="text-sm text-gray-600 mt-2">Intentando conectar a: {apiUrl}</p>
      </div>
    );
  }

  const sortedStations = [...stations].sort((a, b) => {
    const aPrice = a.precios?.gasolina_95 || a.prices?.gasolina_95 || 0;
    const bPrice = b.precios?.gasolina_95 || b.prices?.gasolina_95 || 0;
    const aDistance = a.distancia_km || a.distance_km || 0;
    const bDistance = b.distancia_km || b.distance_km || 0;

    if (sortBy === 'price') {
      return aPrice - bPrice;
    } else {
      return aDistance - bDistance;
    }
  });

  return (
    <div className="bg-white rounded-xl shadow-lg p-8">
      <div className="flex justify-between items-center mb-6">
        <h3 className="text-xl font-bold text-gray-900">
          {selectedFilter === 'todas'
            ? `🚗 Todas las Gasolineras (${stations.length})`
            : `⚠️ Gasolineras Repsol (${stations.length})`}
        </h3>
        <div className="flex gap-2">
          <button
            onClick={() => setSortBy('price')}
            className={`px-4 py-2 rounded-lg font-medium transition ${
              sortBy === 'price'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            💰 Precio
          </button>
          <button
            onClick={() => setSortBy('distance')}
            className={`px-4 py-2 rounded-lg font-medium transition ${
              sortBy === 'distance'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            📍 Distancia
          </button>
        </div>
      </div>

      {stations.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          No hay datos para mostrar
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="px-4 py-3 text-left font-bold text-gray-700">#</th>
                <th className="px-4 py-3 text-left font-bold text-gray-700">Nombre</th>
                <th className="px-4 py-3 text-left font-bold text-gray-700">Municipio</th>
                <th className="px-4 py-3 text-center font-bold text-gray-700">Gasolina 95</th>
                <th className="px-4 py-3 text-center font-bold text-gray-700">Gasóleo A</th>
                <th className="px-4 py-3 text-center font-bold text-gray-700">Distancia</th>
                <th className="px-4 py-3 text-center font-bold text-gray-700">Comparativa</th>
              </tr>
            </thead>
            <tbody>
              {sortedStations.slice(0, 50).map((station, idx) => {
                const gas95 = station.precios?.gasolina_95 ?? station.prices?.gasolina_95 ?? 0;
                const gasA = station.precios?.gasoleoa ?? station.prices?.gasoleoa ?? 0;
                const distance = station.distancia_km ?? station.distance_km ?? 0;
                const nombre = station.nombre ?? station.name ?? 'Sin nombre';
                const municipio = station.municipio ?? station.city ?? 'N/A';
                const comparacion = station.comparacion_media?.gasolina_95_vs_media ?? 0;

                return (
                  <tr
                    key={idx}
                    className="border-b border-gray-100 hover:bg-blue-50 transition"
                  >
                    <td className="px-4 py-3 text-gray-600 font-bold">{idx + 1}</td>
                    <td className="px-4 py-3 font-medium text-gray-900 text-sm">{nombre}</td>
                    <td className="px-4 py-3 text-gray-600 text-sm">{municipio}</td>
                    <td className="px-4 py-3 text-center">
                      <span className={`font-bold ${gas95 < 1.78 ? 'text-green-600' : 'text-red-600'}`}>
                        €{gas95.toFixed(3)}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-center">
                      <span className={`font-bold ${gasA < 1.91 ? 'text-green-600' : 'text-red-600'}`}>
                        €{gasA.toFixed(3)}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-center text-gray-600 text-sm">
                      {distance.toFixed(1)} km
                    </td>
                    <td className="px-4 py-3 text-center text-sm">
                      <span className={`font-bold ${comparacion < 0 ? 'text-green-600' : 'text-red-600'}`}>
                        {comparacion > 0 ? '+' : ''}{comparacion.toFixed(3)}€
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      {stations.length > 0 && (
        <div className="mt-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
          <p className="text-sm text-blue-800">
            <strong>Total de gasolineras mostradas:</strong> {Math.min(sortedStations.length, 50)}{sortedStations.length > 50 ? ` de ${sortedStations.length}` : ''}
            {selectedFilter === 'todas' && (
              <>
                <br />
                <strong>Precio promedio Gasolina 95:</strong> €
                {(
                  sortedStations.reduce((sum, s) => {
                    const price = s.precios?.gasolina_95 ?? s.prices?.gasolina_95 ?? 0;
                    return sum + price;
                  }, 0) / Math.max(sortedStations.length, 1)
                ).toFixed(3)}
                <br />
                <strong>Precio promedio Gasóleo A:</strong> €
                {(
                  sortedStations.reduce((sum, s) => {
                    const price = s.precios?.gasoleoa ?? s.prices?.gasoleoa ?? 0;
                    return sum + price;
                  }, 0) / Math.max(sortedStations.length, 1)
                ).toFixed(3)}
              </>
            )}
          </p>
        </div>
      )}
    </div>
  );
}
