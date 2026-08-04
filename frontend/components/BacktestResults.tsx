'use client';

import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

interface BacktestData {
  date: string;
  actual_price: number;
  predicted_price: number;
  error: number;
}

interface BacktestMetrics {
  mae: number;
  mape: number;
  rmse: number;
  r_squared: number;
  direction_accuracy: number;
  period_days: number;
}

interface BacktestResultsProps {
  data: BacktestData[];
  metrics: BacktestMetrics;
}

export function BacktestResults({ data, metrics }: BacktestResultsProps) {
  if (!data || data.length === 0) {
    return (
      <div className="bg-white rounded-xl shadow-lg p-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center gap-2">
          <span className="text-2xl">✅</span> Validación del Modelo (Backtesting)
        </h2>
        <p className="text-gray-500 text-center py-12">Sin datos de backtesting disponibles</p>
      </div>
    );
  }

  const interval = Math.max(0, Math.floor(data.length / 15));

  return (
    <div className="bg-white rounded-xl shadow-lg p-10 mb-12">
      <h2 className="text-4xl font-bold text-gray-900 mb-8 flex items-center gap-3">
        <span className="text-4xl">✅</span> Validación del Modelo (Backtesting)
      </h2>

      {/* Metrics Summary */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-10">
        <div className="bg-gradient-to-br from-green-50 to-emerald-50 p-6 rounded-lg border-2 border-green-200">
          <p className="text-sm text-gray-700 font-bold">MAE (€/L)</p>
          <p className="text-4xl font-bold text-green-600 my-2">{metrics?.mae?.toFixed(4) || 'N/A'}</p>
          <p className="text-sm text-gray-600">Error Medio Absoluto</p>
        </div>

        <div className="bg-gradient-to-br from-blue-50 to-cyan-50 p-6 rounded-lg border-2 border-blue-200">
          <p className="text-sm text-gray-700 font-bold">MAPE (%)</p>
          <p className="text-4xl font-bold text-blue-600 my-2">{metrics?.mape?.toFixed(2) || 'N/A'}%</p>
          <p className="text-sm text-gray-600">Error Porcentual Medio</p>
        </div>

        <div className="bg-gradient-to-br from-purple-50 to-indigo-50 p-6 rounded-lg border-2 border-purple-200">
          <p className="text-sm text-gray-700 font-bold">RMSE</p>
          <p className="text-4xl font-bold text-purple-600 my-2">{metrics?.rmse?.toFixed(4) || 'N/A'}</p>
          <p className="text-sm text-gray-600">Raíz Error Cuadrado Medio</p>
        </div>

        <div className="bg-gradient-to-br from-orange-50 to-amber-50 p-6 rounded-lg border-2 border-orange-200">
          <p className="text-sm text-gray-700 font-bold">R² Score</p>
          <p className="text-4xl font-bold text-orange-600 my-2">{metrics?.r_squared?.toFixed(3) || 'N/A'}</p>
          <p className="text-sm text-gray-600">Bondad del Ajuste</p>
        </div>

        <div className="bg-gradient-to-br from-pink-50 to-rose-50 p-6 rounded-lg border-2 border-pink-200">
          <p className="text-sm text-gray-700 font-bold">Precisión Dir.</p>
          <p className="text-4xl font-bold text-pink-600 my-2">{metrics?.direction_accuracy?.toFixed(1) || 'N/A'}%</p>
          <p className="text-sm text-gray-600">Precisión Tendencia</p>
        </div>
      </div>

      {/* Historical Comparison Chart */}
      <div className="bg-gray-50 p-8 rounded-lg mb-10">
        <p className="text-lg text-gray-800 font-bold mb-6">
          📊 Comparativa Detallada: Precios Predichos vs Reales ({metrics?.period_days} días)
        </p>
        <ResponsiveContainer width="100%" height={550}>
          <LineChart
            data={data}
            margin={{ top: 5, right: 30, left: 0, bottom: 5 }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" vertical={false} />
            <XAxis
              dataKey="date"
              stroke="#6b7280"
              tick={{ fontSize: 10 }}
              interval={interval}
              angle={-45}
              textAnchor="end"
              height={80}
            />
            <YAxis
              stroke="#6b7280"
              label={{ value: 'EUR/Litro', angle: -90, position: 'insideLeft', offset: 10 }}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: '#fff',
                border: '2px solid #e5e7eb',
                borderRadius: '8px',
                padding: '12px',
              }}
              formatter={(value: any) => `€${value?.toFixed(3)}/L`}
              labelFormatter={(label: any) => `📅 ${label}`}
              wrapperStyle={{ outline: 'none' }}
            />
            <Legend
              verticalAlign="top"
              height={36}
              wrapperStyle={{ paddingBottom: '20px' }}
            />
            <Line
              type="monotone"
              dataKey="actual_price"
              stroke="#10b981"
              strokeWidth={4}
              name="Precio Real"
              dot={false}
              isAnimationActive={true}
            />
            <Line
              type="monotone"
              dataKey="predicted_price"
              stroke="#f59e0b"
              strokeWidth={4}
              strokeDasharray="5 5"
              name="Precio Predicho"
              dot={false}
              isAnimationActive={true}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Interpretation */}
      <div className="bg-blue-50 border-2 border-blue-300 rounded-lg p-8">
        <h3 className="font-bold text-2xl text-blue-900 mb-4 flex items-center gap-2">
          <span>📌</span> Análisis e Interpretación
        </h3>
        <div className="space-y-3 text-blue-900">
          <p className="text-base">
            <strong>Error Absoluto Medio (MAE):</strong> €{metrics?.mae?.toFixed(4)}/L - El modelo se desvía en promedio esta cantidad del precio real.
          </p>
          <p className="text-base">
            <strong>Error Porcentual Medio (MAPE):</strong> {metrics?.mape?.toFixed(2)}% - Desviación relativa respecto al precio real.
          </p>
          <p className="text-base">
            <strong>Precisión de Dirección:</strong> {metrics?.direction_accuracy?.toFixed(1)}% - El modelo predice correctamente si el precio subirá o bajará.
          </p>
          <p className="text-base">
            <strong>R² Score:</strong> {metrics?.r_squared?.toFixed(3)} - Indica que el modelo explica el {(metrics?.r_squared * 100)?.toFixed(1)}% de la varianza en los precios.
          </p>
        </div>
      </div>
    </div>
  );
}
