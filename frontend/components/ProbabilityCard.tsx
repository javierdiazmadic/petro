'use client';

interface ProbabilityCardProps {
  probability_up: number;
  probability_down: number;
  probability_stable: number;
}

export function ProbabilityCard({
  probability_up,
  probability_down,
  probability_stable,
}: ProbabilityCardProps) {
  return (
    <div className="bg-white rounded-xl shadow-lg p-8">
      <h2 className="text-2xl font-bold text-gray-900 mb-8 flex items-center gap-2">
        <span className="text-2xl">📊</span> Probabilidades de Movimiento
      </h2>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Up - Red */}
        <div className="space-y-4">
          <div className="bg-red-50 p-6 rounded-lg border border-red-200">
            <p className="text-sm text-gray-600 font-medium mb-2">Probabilidad SUBIDA</p>
            <p className="text-4xl font-bold text-red-600 mb-4">{(probability_up * 100).toFixed(1)}%</p>

            {/* Gauge Chart SVG */}
            <div className="flex items-center justify-center mb-4">
              <svg width="120" height="120" viewBox="0 0 120 120" className="transform -rotate-90">
                {/* Background circle */}
                <circle cx="60" cy="60" r="50" fill="none" stroke="#fee2e2" strokeWidth="10" />
                {/* Progress circle */}
                <circle
                  cx="60"
                  cy="60"
                  r="50"
                  fill="none"
                  stroke="#dc2626"
                  strokeWidth="10"
                  strokeDasharray={`${(probability_up / 1) * 314} 314`}
                  strokeLinecap="round"
                />
              </svg>
            </div>

            <p className="text-xs text-gray-600 text-center">
              {probability_up < 0.3
                ? '🟢 Baja probabilidad de subida'
                : probability_up < 0.6
                ? '🟡 Probabilidad media de subida'
                : '🔴 Alta probabilidad de subida'}
            </p>
          </div>
        </div>

        {/* Down - Green */}
        <div className="space-y-4">
          <div className="bg-green-50 p-6 rounded-lg border border-green-200">
            <p className="text-sm text-gray-600 font-medium mb-2">Probabilidad BAJADA</p>
            <p className="text-4xl font-bold text-green-600 mb-4">{(probability_down * 100).toFixed(1)}%</p>

            {/* Gauge Chart SVG */}
            <div className="flex items-center justify-center mb-4">
              <svg width="120" height="120" viewBox="0 0 120 120" className="transform -rotate-90">
                {/* Background circle */}
                <circle cx="60" cy="60" r="50" fill="none" stroke="#dcfce7" strokeWidth="10" />
                {/* Progress circle */}
                <circle
                  cx="60"
                  cy="60"
                  r="50"
                  fill="none"
                  stroke="#16a34a"
                  strokeWidth="10"
                  strokeDasharray={`${(probability_down / 1) * 314} 314`}
                  strokeLinecap="round"
                />
              </svg>
            </div>

            <p className="text-xs text-gray-600 text-center">
              {probability_down < 0.3
                ? '🔴 Baja probabilidad de bajada'
                : probability_down < 0.6
                ? '🟡 Probabilidad media de bajada'
                : '🟢 Alta probabilidad de bajada'}
            </p>
          </div>
        </div>

        {/* Stable - Gray */}
        <div className="space-y-4">
          <div className="bg-gray-50 p-6 rounded-lg border border-gray-200">
            <p className="text-sm text-gray-600 font-medium mb-2">Probabilidad ESTABLE</p>
            <p className="text-4xl font-bold text-gray-600 mb-4">{(probability_stable * 100).toFixed(1)}%</p>

            {/* Gauge Chart SVG */}
            <div className="flex items-center justify-center mb-4">
              <svg width="120" height="120" viewBox="0 0 120 120" className="transform -rotate-90">
                {/* Background circle */}
                <circle cx="60" cy="60" r="50" fill="none" stroke="#f3f4f6" strokeWidth="10" />
                {/* Progress circle */}
                <circle
                  cx="60"
                  cy="60"
                  r="50"
                  fill="none"
                  stroke="#4b5563"
                  strokeWidth="10"
                  strokeDasharray={`${(probability_stable / 1) * 314} 314`}
                  strokeLinecap="round"
                />
              </svg>
            </div>

            <p className="text-xs text-gray-600 text-center">
              {probability_stable < 0.3
                ? '🔴 Baja probabilidad de estabilidad'
                : probability_stable < 0.6
                ? '🟡 Probabilidad media de estabilidad'
                : '🟢 Alta probabilidad de estabilidad'}
            </p>
          </div>
        </div>
      </div>

      {/* Summary */}
      <div className="mt-8 p-4 bg-blue-50 border border-blue-200 rounded-lg">
        <h3 className="font-bold text-blue-900 mb-2">📌 Interpretación</h3>
        <p className="text-sm text-blue-800">
          Basado en el modelo predictivo, hay un {(probability_up * 100).toFixed(1)}% de probabilidad de subida de precios,
          un {(probability_down * 100).toFixed(1)}% de probabilidad de bajada, y un {(probability_stable * 100).toFixed(1)}% de probabilidad de estabilidad
          en los próximos 30 días.
        </p>
      </div>
    </div>
  );
}
