'use client';

import { useEffect, useState } from 'react';

interface ToledoStation {
  name: string;
  distance_km: number;
  operator?: string;
  brand?: string;
  prices?: {
    gasolina_95: number;
    gasolina_98: number;
    gasoleoa: number;
  };
  distance_price_ratio?: {
    gasolina_95: number;
    gasolina_98: number;
    gasoleoa: number;
  };
}

interface ToledoAnalysisProps {
  apiUrl: string;
}

const FUEL_TYPES = {
  gasolina_95: { label: '⛽ Gasolina 95', color: 'blue' },
  gasolina_98: { label: '⛽ Gasolina 98', color: 'purple' },
  gasoleoa: { label: '🛢️ Gasóleo A', color: 'green' },
};

export function ToledoAnalysis({ apiUrl }: ToledoAnalysisProps) {
  const [stations, setStations] = useState<any>(null);
  const [analysis, setAnalysis] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'analysis' | 'stations'>('analysis');
  const [selectedFuelType, setSelectedFuelType] = useState<'gasolina_95' | 'gasolina_98' | 'gasoleoa'>('gasoleoa');

  useEffect(() => {
    const fetchToledoData = async () => {
      try {
        setLoading(true);
        setError(null);

        // Fetch gas stations
        const stationsRes = await fetch(
          `${apiUrl}/api/v1/toledo/gas-stations?max_distance_km=50`
        );
        const stationsData = await stationsRes.json();
        setStations(stationsData);

        // Fetch analysis for selected fuel type
        const analysisRes = await fetch(
          `${apiUrl}/api/v1/toledo/analysis?fuel_type=${selectedFuelType}&max_distance_km=50`
        );
        const analysisData = await analysisRes.json();
        setAnalysis(analysisData);
      } catch (err) {
        setError('Error al cargar datos de Toledo');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchToledoData();
  }, [selectedFuelType, apiUrl]);

  if (loading) {
    return (
      <div className="bg-white rounded-xl shadow-lg p-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Análisis de Gasolineras - Toledo</h2>
        <div className="text-center py-8">
          <p className="text-gray-500">Cargando datos de gasolineras...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 rounded-xl shadow-lg p-8 border border-red-200">
        <h2 className="text-2xl font-bold text-red-900 mb-4">Análisis de Gasolineras - Toledo</h2>
        <p className="text-red-600">{error}</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl shadow-lg p-8">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-4 flex items-center gap-2">
          <span className="text-2xl">📍</span> Análisis de Gasolineras en Toledo
        </h2>
        <p className="text-gray-600">
          Centro de referencia: Los Yébenes (39.86°N, 3.96°O)
        </p>
      </div>

      {/* Fuel Type Selector */}
      <div className="mb-6 p-4 bg-gray-50 rounded-lg">
        <label className="block text-sm font-bold text-gray-700 mb-3">Selecciona tipo de combustible:</label>
        <div className="flex gap-3 flex-wrap">
          {Object.entries(FUEL_TYPES).map(([key, { label }]) => (
            <button
              key={key}
              onClick={() => setSelectedFuelType(key as any)}
              className={`px-4 py-2 rounded-lg font-medium transition ${
                selectedFuelType === key
                  ? 'bg-blue-600 text-white'
                  : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-100'
              }`}
            >
              {label}
            </button>
          ))}
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-4 mb-6 border-b border-gray-200">
        <button
          onClick={() => setActiveTab('analysis')}
          className={`px-4 py-2 font-medium transition ${
            activeTab === 'analysis'
              ? 'text-green-600 border-b-2 border-green-600'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          🏆 Ranking por Mejor Relación Distancia/Precio
        </button>
        <button
          onClick={() => setActiveTab('stations')}
          className={`px-4 py-2 font-medium transition ${
            activeTab === 'stations'
              ? 'text-blue-600 border-b-2 border-blue-600'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          📍 Todas las Gasolineras
        </button>
      </div>

      {/* Analysis Tab - RANKING */}
      {activeTab === 'analysis' && analysis && (
        <div className="space-y-4">
          <div className="bg-gray-50 p-4 rounded-lg mb-4">
            <h3 className="font-bold text-gray-900 mb-2">Filtrado por: {analysis.fuel_name}</h3>
            <p className="text-sm text-gray-600">
              Precio base: €{analysis.base_price}/L | Ordenado por mejor relación distancia/precio (lo más bajo = mejor opción)
            </p>
          </div>

          {analysis.stations && analysis.stations.length > 0 ? (
            <div className="max-h-96 overflow-y-auto space-y-3">
              {analysis.stations.map((station: any, idx: number) => (
                <div
                  key={idx}
                  className={`border rounded-lg p-4 transition ${
                    idx === 0
                      ? 'border-green-500 bg-green-50'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <div className="flex justify-between items-start mb-2">
                    <div>
                      <h4 className="font-bold text-gray-900">
                        {idx === 0 && '🥇 '}
                        {idx === 1 && '🥈 '}
                        {idx === 2 && '🥉 '}
                        {station.name}
                      </h4>
                      <p className="text-sm text-gray-600">{station.operator}</p>
                    </div>
                    <div className="text-right">
                      <p className="text-2xl font-bold text-gray-900">€{station.price.toFixed(3)}/L</p>
                      <p className="text-sm text-gray-500">
                        {station.price_vs_reference > 0 ? '+' : ''}
                        €{station.price_vs_reference.toFixed(3)} vs base
                      </p>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-3 text-sm">
                    <div className="bg-white p-2 rounded border border-gray-200">
                      <p className="text-gray-600">Distancia</p>
                      <p className="font-bold">{station.distance_km} km</p>
                    </div>
                    <div className="bg-white p-2 rounded border border-gray-200">
                      <p className="text-gray-600">Ratio dist/precio</p>
                      <p className="font-bold">{station.distance_price_ratio.toFixed(3)}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-500 text-center py-8">
              No hay gasolineras disponibles para este combustible
            </p>
          )}
        </div>
      )}

      {/* Stations Tab - ALL STATIONS WITH PRICES */}
      {activeTab === 'stations' && stations && (
        <div className="space-y-4">
          <div className="bg-gray-50 p-4 rounded-lg mb-4">
            <h3 className="font-bold text-gray-900">Todas las gasolineras con precios completos</h3>
            <p className="text-sm text-gray-600">
              {stations.total_stations} estaciones encontradas
            </p>
          </div>

          {stations.stations && stations.stations.length > 0 ? (
            <div className="max-h-96 overflow-y-auto space-y-3">
              {stations.stations.map((station: ToledoStation, idx: number) => (
                <div key={idx} className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition">
                  <div className="flex justify-between items-start mb-3">
                    <div>
                      <h4 className="font-bold text-gray-900">{station.name}</h4>
                      <p className="text-sm text-gray-600">{station.operator} • {station.brand}</p>
                    </div>
                    <span className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full font-bold text-sm">
                      {station.distance_km} km
                    </span>
                  </div>

                  {station.prices && (
                    <div className="grid grid-cols-3 gap-2">
                      <div className="bg-blue-50 p-2 rounded border border-blue-200">
                        <p className="text-xs text-gray-600">Gasolina 95</p>
                        <p className="font-bold text-sm">€{station.prices.gasolina_95.toFixed(3)}</p>
                        <p className="text-xs text-gray-500">
                          Ratio: {(station.distance_km / station.prices.gasolina_95).toFixed(3)}
                        </p>
                      </div>
                      <div className="bg-purple-50 p-2 rounded border border-purple-200">
                        <p className="text-xs text-gray-600">Gasolina 98</p>
                        <p className="font-bold text-sm">€{station.prices.gasolina_98.toFixed(3)}</p>
                        <p className="text-xs text-gray-500">
                          Ratio: {(station.distance_km / station.prices.gasolina_98).toFixed(3)}
                        </p>
                      </div>
                      <div className="bg-green-50 p-2 rounded border border-green-200">
                        <p className="text-xs text-gray-600">Gasóleo A</p>
                        <p className="font-bold text-sm">€{station.prices.gasoleoa.toFixed(3)}</p>
                        <p className="text-xs text-gray-500">
                          Ratio: {(station.distance_km / station.prices.gasoleoa).toFixed(3)}
                        </p>
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-500 text-center py-8">
              No hay gasolineras disponibles
            </p>
          )}
        </div>
      )}

      {/* Data Source */}
      <div className="mt-6 pt-6 border-t border-gray-200">
        <p className="text-xs text-gray-500">
          📊 Fuente: OpenStreetMap + Precios Realistas | Centro: Los Yébenes (39.86°N, 3.96°O)
        </p>
      </div>
    </div>
  );
}
