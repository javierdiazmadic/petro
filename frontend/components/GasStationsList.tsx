'use client';

import { useState } from 'react';

interface GasStation {
  id?: string | number;
  name?: string;
  nombre?: string;
  municipio: string;
  brand?: string;
  distance_km: number;
  price?: number;
  prices?: {
    gasolina_95?: number;
    gasolina_98?: number;
    gasoleoa?: number;
  };
}

interface GasStationsListProps {
  stations: GasStation[];
  loading?: boolean;
  error?: string | null;
  selectedFilter?: 'todas' | 'repsol';
}

export function GasStationsList({ stations, loading = false, error = null, selectedFilter = 'todas' }: GasStationsListProps) {
  const [selectedFuel, setSelectedFuel] = useState<'gasolina_95' | 'gasolina_98' | 'gasoleoa'>('gasoleoa');
  const [sortBy, setSortBy] = useState<'price' | 'distance'>('price');

  if (loading) {
    return (
      <div className="bg-white rounded-xl shadow-lg p-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center gap-2">
          <span className="text-2xl">⛽</span> Gasolineras Más Baratas (Toledo)
        </h2>
        <div className="text-center py-12">
          <p className="text-gray-500">Cargando gasolineras...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 rounded-xl shadow-lg p-8 border border-red-200">
        <h2 className="text-2xl font-bold text-red-900 mb-4 flex items-center gap-2">
          <span className="text-2xl">⛽</span> Gasolineras Más Baratas (Toledo)
        </h2>
        <p className="text-red-600">{error}</p>
      </div>
    );
  }

  if (!stations || stations.length === 0) {
    return (
      <div className="bg-white rounded-xl shadow-lg p-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center gap-2">
          <span className="text-2xl">⛽</span> Gasolineras Más Baratas (Toledo)
        </h2>
        <p className="text-gray-500 text-center py-12">Sin gasolineras disponibles</p>
      </div>
    );
  }

  // Sort by selected fuel price or distance
  const sortedStations = [...stations].sort((a, b) => {
    if (sortBy === 'distance') {
      const distA = a.distance_km ?? 0;
      const distB = b.distance_km ?? 0;
      return distA - distB;
    } else {
      const priceA = a.prices?.[selectedFuel] ?? a.price ?? 0;
      const priceB = b.prices?.[selectedFuel] ?? b.price ?? 0;
      return priceA - priceB;
    }
  });

  // Get min and max prices for color coding
  const prices = sortedStations.map(s => s.prices?.[selectedFuel] ?? s.price ?? 0);
  const minPrice = Math.min(...prices);
  const maxPrice = Math.max(...prices);
  const priceRange = maxPrice - minPrice;

  const getPriceColor = (price: number) => {
    if (price <= minPrice + priceRange * 0.2) {
      return 'bg-green-100 text-green-800 border-green-300';
    }
    if (price >= maxPrice - priceRange * 0.2) {
      return 'bg-red-100 text-red-800 border-red-300';
    }
    return 'bg-yellow-100 text-yellow-800 border-yellow-300';
  };

  const getFuelLabel = (fuel: string) => {
    switch (fuel) {
      case 'gasolina_95':
        return '⛽ Gasolina 95';
      case 'gasolina_98':
        return '⛽ Gasolina 98';
      case 'gasoleoa':
        return '🛢️ Gasóleo A';
      default:
        return fuel;
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-lg p-8">
      <h2 className="text-3xl font-bold text-gray-900 mb-8 flex items-center gap-2">
        <span className="text-3xl">⛽</span>
        {selectedFilter === 'todas' ? 'Gasolineras Más Baratas - Todas las Estaciones' : 'Gasolineras Más Baratas - Solo Repsol'}
      </h2>

      {/* Fuel Type Selector */}
      <div className="mb-8 p-6 bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg border border-blue-200">
        <label className="block text-sm font-bold text-gray-700 mb-4 uppercase">📍 Tipo de Combustible</label>
        <div className="flex gap-3 flex-wrap">
          {['gasolina_95', 'gasolina_98', 'gasoleoa'].map((fuel) => (
            <button
              key={fuel}
              onClick={() => setSelectedFuel(fuel as any)}
              className={`px-5 py-2 rounded-lg font-bold transition-all ${
                selectedFuel === fuel
                  ? 'bg-blue-600 text-white shadow-md'
                  : 'bg-white text-gray-700 border-2 border-gray-300 hover:border-blue-400 hover:bg-blue-50'
              }`}
            >
              {getFuelLabel(fuel)}
            </button>
          ))}
        </div>
      </div>

      {/* Sort Buttons */}
      <div className="mb-8 flex gap-4">
        <button
          onClick={() => setSortBy('price')}
          className={`px-6 py-3 rounded-lg font-bold transition-all flex items-center gap-2 ${
            sortBy === 'price'
              ? 'bg-green-600 text-white shadow-lg'
              : 'bg-gray-100 text-gray-700 border border-gray-300 hover:bg-gray-200'
          }`}
        >
          <span>💰</span> Más Baratos
        </button>
        <button
          onClick={() => setSortBy('distance')}
          className={`px-6 py-3 rounded-lg font-bold transition-all flex items-center gap-2 ${
            sortBy === 'distance'
              ? 'bg-orange-600 text-white shadow-lg'
              : 'bg-gray-100 text-gray-700 border border-gray-300 hover:bg-gray-200'
          }`}
        >
          <span>📍</span> Más Cercanos
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-4 mb-6">
        <div className="bg-green-50 p-4 rounded-lg border border-green-200">
          <p className="text-xs text-gray-600 font-medium">Más Barato</p>
          <p className="text-2xl font-bold text-green-600">€{minPrice.toFixed(3)}</p>
        </div>
        <div className="bg-yellow-50 p-4 rounded-lg border border-yellow-200">
          <p className="text-xs text-gray-600 font-medium">Promedio</p>
          <p className="text-2xl font-bold text-yellow-600">
            €{(prices.reduce((a, b) => a + b, 0) / prices.length).toFixed(3)}
          </p>
        </div>
        <div className="bg-red-50 p-4 rounded-lg border border-red-200">
          <p className="text-xs text-gray-600 font-medium">Más Caro</p>
          <p className="text-2xl font-bold text-red-600">€{maxPrice.toFixed(3)}</p>
        </div>
      </div>

      {/* Stations Table */}
      <div className="overflow-x-auto">
        <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b-2 border-gray-400 bg-gray-100">
              <th className="text-center py-4 px-4 text-xs font-bold text-gray-800 uppercase">Posición</th>
              <th className="text-left py-4 px-4 text-xs font-bold text-gray-800 uppercase">Nombre Gasolinera</th>
              <th className="text-left py-4 px-4 text-xs font-bold text-gray-800 uppercase">Municipio</th>
              <th className="text-center py-4 px-4 text-xs font-bold text-gray-800 uppercase">Marca</th>
              <th className="text-center py-4 px-4 text-xs font-bold text-gray-800 uppercase">Precio Actual</th>
              <th className="text-center py-4 px-4 text-xs font-bold text-gray-800 uppercase">Distancia desde Centro</th>
            </tr>
          </thead>
          <tbody>
            {sortedStations.slice(0, 15).map((station, idx) => {
              const stationName = station.name ?? station.nombre ?? 'Unknown';
              const stationPrice = station.prices?.[selectedFuel] ?? station.price ?? 0;
              return (
                <tr key={station.id || idx} className="border-b border-gray-200 hover:bg-gray-50 transition">
                  <td className="py-3 px-4">
                    <span className="text-sm font-bold">
                      {idx === 0 && '🥇'}
                      {idx === 1 && '🥈'}
                      {idx === 2 && '🥉'}
                      {idx > 2 && `${idx + 1}.`}
                    </span>
                  </td>
                  <td className="py-3 px-4">
                    <div>
                      <p className="font-bold text-gray-900">{stationName}</p>
                    </div>
                  </td>
                  <td className="py-3 px-4">
                    <p className="text-sm text-gray-600">{station.municipio}</p>
                  </td>
                  <td className="py-3 px-4">
                    <span className="bg-gray-100 text-gray-800 px-2 py-1 rounded text-xs font-bold">
                      {station.brand ?? 'UNKNOWN'}
                    </span>
                  </td>
                  <td className="py-3 px-4 text-center">
                    <span className={`px-3 py-1 rounded-full text-sm font-bold border ${getPriceColor(stationPrice)}`}>
                      €{stationPrice.toFixed(3)}
                    </span>
                  </td>
                  <td className="py-3 px-4 text-center">
                    <span className="text-sm font-bold text-gray-700">{station.distance_km.toFixed(1)} km</span>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {stations.length > 15 && (
        <div className="mt-4 text-center">
          <p className="text-sm text-gray-600">
            Mostrando 15 de {stations.length} gasolineras más cercanas
          </p>
        </div>
      )}

      {/* Legend */}
      <div className="mt-6 pt-6 border-t border-gray-200">
        <p className="text-xs text-gray-600">
          🟢 Verde = Más barato | 🟡 Amarillo = Precio medio | 🔴 Rojo = Más caro | 📍 Centro: Los Yébenes (39.86°N, 3.96°O)
        </p>
      </div>
    </div>
  );
}
