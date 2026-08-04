'use client';

import { useState, useEffect } from 'react';
import dynamic from 'next/dynamic';
import { toledoAPI } from '@/lib/api';

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
}

// Dynamically import Leaflet to avoid SSR issues
const MapComponent = dynamic(() => import('./MapComponent'), {
  loading: () => <div className="h-96 flex items-center justify-center bg-gray-100">Cargando mapa...</div>,
  ssr: false,
});

export function ToledoInteractiveMap() {
  const [stations, setStations] = useState<GasStation[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

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

  return (
    <div className="bg-white rounded-xl shadow-lg p-8 mb-12">
      <h2 className="text-3xl font-bold text-gray-900 mb-6 flex items-center gap-2">
        <span className="text-4xl">🗺️</span> Mapa Interactivo - Gasolineras Toledo
      </h2>

      {loading ? (
        <div className="h-96 flex items-center justify-center bg-gray-100 rounded-lg">
          <p className="text-gray-500">Cargando mapa y gasolineras...</p>
        </div>
      ) : error ? (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-600">
          {error}
        </div>
      ) : (
        <>
          <MapComponent stations={stations} />
          <div className="mt-6 p-4 bg-blue-50 rounded-lg border border-blue-200 text-sm text-gray-600">
            <p>
              <strong>Total de gasolineras en Toledo:</strong> {stations?.length || 0} |
              <strong> Haz clic en los marcadores</strong> para ver precios actualizados
            </p>
          </div>
        </>
      )}
    </div>
  );
}
