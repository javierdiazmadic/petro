'use client';

import { useEffect, useState } from 'react';
import { toledoAPI } from '@/lib/api';

interface FilterButtonsBarProps {
  selectedFilter: 'todas' | 'repsol';
  onFilterChange: (filter: 'todas' | 'repsol') => void;
}

export function FilterButtonsBar({ selectedFilter, onFilterChange }: FilterButtonsBarProps) {
  const [cheapestDiesel, setCheapestDiesel] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchCheapestDiesel = async () => {
      if (selectedFilter === 'repsol') {
        setLoading(true);
        try {
          const response = await toledoAPI.getCheapest('gasoleoa', 1, 'repsol');
          if (response?.data?.stations?.[0]) {
            setCheapestDiesel(response.data.stations[0].price);
          }
        } catch (err) {
          console.error('Error fetching cheapest diesel:', err);
        } finally {
          setLoading(false);
        }
      }
    };

    fetchCheapestDiesel();
  }, [selectedFilter]);

  return (
    <div className="mb-8 p-6 bg-gradient-to-r from-blue-50 to-purple-50 rounded-xl border border-blue-200">
      <p className="text-sm font-semibold text-gray-700 mb-4 uppercase tracking-wide">
        Filtro de Gasolineras
      </p>
      <div className="flex gap-3 flex-wrap">
        <button
          onClick={() => onFilterChange('todas')}
          className={`px-6 py-3 rounded-lg font-bold transition-all transform hover:scale-105 ${
            selectedFilter === 'todas'
              ? 'bg-blue-600 text-white shadow-lg ring-2 ring-blue-300'
              : 'bg-white text-gray-700 border-2 border-gray-300 hover:border-blue-400 hover:bg-blue-50'
          }`}
        >
          <span className="flex items-center gap-2">
            <span className="text-lg">🚗</span>
            Todas las Estaciones (246)
          </span>
        </button>

        <button
          onClick={() => onFilterChange('repsol')}
          className={`px-6 py-3 rounded-lg font-bold transition-all transform hover:scale-105 ${
            selectedFilter === 'repsol'
              ? 'bg-red-600 text-white shadow-lg ring-2 ring-red-300'
              : 'bg-white text-gray-700 border-2 border-gray-300 hover:border-red-400 hover:bg-red-50'
          }`}
        >
          <span className="flex items-center gap-2">
            <span className="text-lg">⚠️</span>
            Solo Repsol (79)
          </span>
        </button>
      </div>

      {selectedFilter === 'repsol' && (
        <div className="mt-4 p-4 bg-red-50 border-l-4 border-red-500 rounded">
          <p className="text-sm text-red-800 font-medium">
            📍 Gasolineras Repsol: €0.070/L más caras en Gasolina 95
            <br />
            📍 Gasolineras Repsol: €0.077/L más caras en Gasóleo A
            {loading ? (
              <span className="block mt-2">📦 Cargando diesel más barato...</span>
            ) : cheapestDiesel ? (
              <span className="block mt-2 font-bold text-red-700">
                🛢️ Diésel más barato REPSOL: €{cheapestDiesel.toFixed(3)}/L
              </span>
            ) : null}
          </p>
        </div>
      )}
    </div>
  );
}
