'use client';

import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, AreaChart, Area, ComposedChart, Bar } from 'recharts';

interface PredictionData {
  date: string;
  gasolina_95: number;
  gasoleoa: number;
  gasolina_95_upper?: number;
  gasolina_95_lower?: number;
  gasoleoa_upper?: number;
  gasoleoa_lower?: number;
}

interface PredictionChartProps {
  data: PredictionData[];
  confidence?: number;
}

export function PredictionChart({ data, confidence = 85 }: PredictionChartProps) {
  if (!data || data.length === 0) {
    return <p className="text-gray-500 text-center py-12">Sin datos de predicción disponibles</p>;
  }

  const interval = Math.max(0, Math.floor(data.length / 15));

  return (
    <div className="space-y-6">
      {/* Confidence Indicator */}
      <div className="bg-gradient-to-r from-blue-50 to-cyan-50 p-4 rounded-lg border border-blue-200 flex items-center gap-4">
        <div className="flex-1">
          <p className="text-sm text-gray-600 font-medium">Nivel de Confianza del Modelo</p>
          <p className="text-2xl font-bold text-blue-600">{confidence}%</p>
        </div>
        <div className="flex-shrink-0">
          <div className="relative w-20 h-20">
            <svg className="transform -rotate-90" viewBox="0 0 100 100">
              <circle cx="50" cy="50" r="45" fill="none" stroke="#e5e7eb" strokeWidth="8" />
              <circle
                cx="50"
                cy="50"
                r="45"
                fill="none"
                stroke="#3b82f6"
                strokeWidth="8"
                strokeDasharray={`${(confidence / 100) * 282.7} 282.7`}
                strokeLinecap="round"
              />
            </svg>
            <div className="absolute inset-0 flex items-center justify-center">
              <span className="text-sm font-bold text-gray-700">{confidence}%</span>
            </div>
          </div>
        </div>
      </div>

      {/* Main Chart */}
      <div className="bg-white p-6 rounded-lg">
        <p className="text-sm text-gray-600 mb-4">
          📊 Predicción para los próximos 30 días con intervalo de confianza
        </p>
        <ResponsiveContainer width="100%" height={400}>
          <ComposedChart
            data={data}
            margin={{ top: 5, right: 30, left: 0, bottom: 5 }}
          >
            <defs>
              <linearGradient id="colorGasolina" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
                <stop offset="95%" stopColor="#3b82f6" stopOpacity={0.01} />
              </linearGradient>
              <linearGradient id="colorGasoleoa" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#10b981" stopOpacity={0.3} />
                <stop offset="95%" stopColor="#10b981" stopOpacity={0.01} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" vertical={false} />
            <XAxis
              dataKey="date"
              stroke="#6b7280"
              tick={{ fontSize: 11 }}
              interval={interval}
              angle={-45}
              textAnchor="end"
              height={80}
            />
            <YAxis
              stroke="#6b7280"
              domain={['dataMin - 0.1', 'dataMax + 0.1']}
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

            {/* Confidence bands */}
            {data[0]?.gasolina_95_upper && (
              <Area
                type="monotone"
                dataKey="gasolina_95_upper"
                fill="#3b82f6"
                stroke="none"
                fillOpacity={0.1}
                name="Intervalo Gasolina 95"
              />
            )}
            {data[0]?.gasoleoa_upper && (
              <Area
                type="monotone"
                dataKey="gasoleoa_upper"
                fill="#10b981"
                stroke="none"
                fillOpacity={0.1}
                name="Intervalo Gasóleo A"
              />
            )}

            {/* Main lines */}
            <Line
              type="monotone"
              dataKey="gasolina_95"
              stroke="#3b82f6"
              strokeWidth={3}
              name="⛽ Gasolina 95"
              dot={false}
              isAnimationActive={false}
            />
            <Line
              type="monotone"
              dataKey="gasoleoa"
              stroke="#10b981"
              strokeWidth={3}
              name="🛢️ Gasóleo A"
              dot={false}
              isAnimationActive={false}
            />
          </ComposedChart>
        </ResponsiveContainer>
      </div>

      {/* Interpretation */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
          <h3 className="font-bold text-blue-900 mb-2">Gasolina 95</h3>
          <p className="text-sm text-blue-800">
            Tendencia de los próximos 30 días con banda de confianza del ±{(100 - confidence)}%
          </p>
        </div>
        <div className="bg-green-50 p-4 rounded-lg border border-green-200">
          <h3 className="font-bold text-green-900 mb-2">Gasóleo A</h3>
          <p className="text-sm text-green-800">
            Tendencia de los próximos 30 días con banda de confianza del ±{(100 - confidence)}%
          </p>
        </div>
      </div>
    </div>
  );
}
