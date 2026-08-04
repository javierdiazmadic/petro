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
    <div className="bg-white rounded-xl shadow-lg p-8">
      <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center gap-2">
        <span className="text-2xl">✅</span> Validación del Modelo (Backtesting)
      </h2>

      {/* Metrics Summary */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-8">
        <div className="bg-gradient-to-br from-green-50 to-emerald-50 p-4 rounded-lg border border-green-200">
          <p className="text-xs text-gray-600 font-medium">MAE (€/L)</p>
          <p className="text-2xl font-bold text-green-600">{metrics?.mae?.toFixed(4) || 'N/A'}</p>
          <p className="text-xs text-gray-500 mt-1">Error Medio</p>
        </div>

        <div className="bg-gradient-to-br from-blue-50 to-cyan-50 p-4 rounded-lg border border-blue-200">
          <p className="text-xs text-gray-600 font-medium">MAPE (%)</p>
          <p className="text-2xl font-bold text-blue-600">{metrics?.mape?.toFixed(2) || 'N/A'}%</p>
          <p className="text-xs text-gray-500 mt-1">Error Porcentual</p>
        </div>

        <div className="bg-gradient-to-br from-purple-50 to-indigo-50 p-4 rounded-lg border border-purple-200">
          <p className="text-xs text-gray-600 font-medium">RMSE</p>
          <p className="text-2xl font-bold text-purple-600">{metrics?.rmse?.toFixed(4) || 'N/A'}</p>
          <p className="text-xs text-gray-500 mt-1">Raíz del Error</p>
        </div>

        <div className="bg-gradient-to-br from-orange-50 to-amber-50 p-4 rounded-lg border border-orange-200">
          <p className="text-xs text-gray-600 font-medium">R² Score</p>
          <p className="text-2xl font-bold text-orange-600">{metrics?.r_squared?.toFixed(3) || 'N/A'}</p>
          <p className="text-xs text-gray-500 mt-1">Bondad del Ajuste</p>
        </div>

        <div className="bg-gradient-to-br from-pink-50 to-rose-50 p-4 rounded-lg border border-pink-200">
          <p className="text-xs text-gray-600 font-medium">Precisión Dirección</p>
          <p className="text-2xl font-bold text-pink-600">{metrics?.direction_accuracy?.toFixed(1) || 'N/A'}%</p>
          <p className="text-xs text-gray-500 mt-1">↑↓ Tendencia</p>
        </div>
      </div>

      {/* Historical Comparison Chart */}
      <div className="bg-gray-50 p-6 rounded-lg mb-8">
        <p className="text-sm text-gray-600 mb-4">
          📊 Comparativa: Precios Predichos vs Reales ({metrics?.period_days} días)
        </p>
        <ResponsiveContainer width="100%" height={350}>
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
              strokeWidth={3}
              name="Precio Real"
              dot={false}
            />
            <Line
              type="monotone"
              dataKey="predicted_price"
              stroke="#f59e0b"
              strokeWidth={2}
              strokeDasharray="5 5"
              name="Precio Predicho"
              dot={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Interpretation */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h3 className="font-bold text-blue-900 mb-2">📌 Interpretación</h3>
        <p className="text-sm text-blue-800">
          El modelo tiene un MAE de €{metrics?.mae?.toFixed(4)}/L (error medio absoluto) y un MAPE del {metrics?.mape?.toFixed(2)}% en el período analizado.
          La precisión de dirección del {metrics?.direction_accuracy?.toFixed(1)}% indica que el modelo predice correctamente si el precio subirá o bajará en {metrics?.direction_accuracy?.toFixed(1)}% de los casos.
        </p>
      </div>
    </div>
  );
}
