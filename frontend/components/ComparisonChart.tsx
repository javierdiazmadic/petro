'use client';

import { useEffect, useState } from 'react';

interface ComparisonChartProps {
  selectedFilter: 'todas' | 'repsol';
  apiUrl: string;
}

export function ComparisonChart({ selectedFilter, apiUrl }: ComparisonChartProps) {
  const [todasData, setTodasData] = useState<any>(null);
  const [repsolData, setRepsolData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [todasRes, repsolRes] = await Promise.all([
          fetch(`${apiUrl}/api/v1/toledo/all-stations?max_distance_km=100`),
          fetch(`${apiUrl}/api/v1/toledo/repsol?max_distance_km=100`),
        ]);

        const todasJSON = await todasRes.json();
        const repsolJSON = await repsolRes.json();

        setTodasData(todasJSON);
        setRepsolData(repsolJSON);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [apiUrl]);

  if (loading || !todasData || !repsolData) {
    return (
      <div className="bg-white rounded-xl shadow-lg p-8">
        <h3 className="text-xl font-bold text-gray-900 mb-6">
          📊 Comparación de Precios
        </h3>
        <div className="text-center py-12">
          <div className="inline-block">
            <div className="w-8 h-8 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin"></div>
          </div>
          <p className="mt-4 text-gray-500">Cargando gráfico...</p>
        </div>
      </div>
    );
  }

  const todasGas95 = todasData.fuel_types?.gasolina_95?.media || 1.735;
  const todasDiesel = todasData.fuel_types?.gasoleoa?.media || 1.861;

  const repsolGas95 = repsolData.comparison?.gasolina_95?.repsol_avg || 1.805;
  const repsolDiesel = repsolData.comparison?.gasoleoa?.repsol_avg || 1.938;

  const maxPrice = Math.max(todasGas95, repsolGas95, todasDiesel, repsolDiesel) + 0.1;

  const barWidth = (price: number) => (price / maxPrice) * 100;

  return (
    <div className="bg-white rounded-xl shadow-lg p-8">
      <h3 className="text-xl font-bold text-gray-900 mb-8">
        📊 Comparación: Todas vs Repsol
      </h3>

      <div className="space-y-8">
        {/* Gasolina 95 */}
        <div>
          <h4 className="font-bold text-gray-900 mb-4">⛽ Gasolina 95</h4>
          <div className="space-y-3">
            {/* Todas */}
            <div>
              <div className="flex justify-between mb-2">
                <span className="text-sm font-medium text-gray-700">
                  Todas las estaciones
                </span>
                <span className="text-sm font-bold text-blue-600">
                  €{todasGas95.toFixed(3)}
                </span>
              </div>
              <div className="relative h-8 bg-gray-100 rounded-lg overflow-hidden">
                <div
                  className="h-full bg-gradient-to-r from-blue-400 to-blue-600 transition-all duration-500 flex items-center justify-end pr-2"
                  style={{ width: `${barWidth(todasGas95)}%` }}
                >
                  {barWidth(todasGas95) > 30 && (
                    <span className="text-xs font-bold text-white">
                      {todasGas95.toFixed(3)}
                    </span>
                  )}
                </div>
              </div>
            </div>

            {/* Repsol */}
            <div>
              <div className="flex justify-between mb-2">
                <span className="text-sm font-medium text-gray-700">
                  Repsol Toledo
                </span>
                <span className="text-sm font-bold text-red-600">
                  €{repsolGas95.toFixed(3)}
                  <span className="text-xs text-red-500 ml-1">
                    (+€{(repsolGas95 - todasGas95).toFixed(3)})
                  </span>
                </span>
              </div>
              <div className="relative h-8 bg-gray-100 rounded-lg overflow-hidden">
                <div
                  className="h-full bg-gradient-to-r from-red-400 to-red-600 transition-all duration-500 flex items-center justify-end pr-2"
                  style={{ width: `${barWidth(repsolGas95)}%` }}
                >
                  {barWidth(repsolGas95) > 30 && (
                    <span className="text-xs font-bold text-white">
                      {repsolGas95.toFixed(3)}
                    </span>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Gasóleo A */}
        <div>
          <h4 className="font-bold text-gray-900 mb-4">🛢️ Gasóleo A</h4>
          <div className="space-y-3">
            {/* Todas */}
            <div>
              <div className="flex justify-between mb-2">
                <span className="text-sm font-medium text-gray-700">
                  Todas las estaciones
                </span>
                <span className="text-sm font-bold text-green-600">
                  €{todasDiesel.toFixed(3)}
                </span>
              </div>
              <div className="relative h-8 bg-gray-100 rounded-lg overflow-hidden">
                <div
                  className="h-full bg-gradient-to-r from-green-400 to-green-600 transition-all duration-500 flex items-center justify-end pr-2"
                  style={{ width: `${barWidth(todasDiesel)}%` }}
                >
                  {barWidth(todasDiesel) > 30 && (
                    <span className="text-xs font-bold text-white">
                      {todasDiesel.toFixed(3)}
                    </span>
                  )}
                </div>
              </div>
            </div>

            {/* Repsol */}
            <div>
              <div className="flex justify-between mb-2">
                <span className="text-sm font-medium text-gray-700">
                  Repsol Toledo
                </span>
                <span className="text-sm font-bold text-red-600">
                  €{repsolDiesel.toFixed(3)}
                  <span className="text-xs text-red-500 ml-1">
                    (+€{(repsolDiesel - todasDiesel).toFixed(3)})
                  </span>
                </span>
              </div>
              <div className="relative h-8 bg-gray-100 rounded-lg overflow-hidden">
                <div
                  className="h-full bg-gradient-to-r from-orange-400 to-orange-600 transition-all duration-500 flex items-center justify-end pr-2"
                  style={{ width: `${barWidth(repsolDiesel)}%` }}
                >
                  {barWidth(repsolDiesel) > 30 && (
                    <span className="text-xs font-bold text-white">
                      {repsolDiesel.toFixed(3)}
                    </span>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="mt-8 grid grid-cols-2 gap-4">
        <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
          <p className="text-xs text-blue-600 font-bold mb-1">MEDIA TOLEDO</p>
          <p className="text-lg font-bold text-blue-900">
            €{((todasGas95 + todasDiesel) / 2).toFixed(3)}
          </p>
        </div>
        <div className="p-4 bg-red-50 rounded-lg border border-red-200">
          <p className="text-xs text-red-600 font-bold mb-1">MEDIA REPSOL</p>
          <p className="text-lg font-bold text-red-900">
            €{((repsolGas95 + repsolDiesel) / 2).toFixed(3)}
          </p>
        </div>
      </div>
    </div>
  );
}
