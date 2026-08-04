'use client';

import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ComposedChart, Bar } from 'recharts';

interface PriceChartProps {
  data: any;
  stats?: any;
}

export function PriceChart({ data, stats }: PriceChartProps) {
  if (!data || data.length === 0) {
    return <p className="text-gray-500 text-center py-12">Sin datos disponibles</p>;
  }

  // Calculate interval intelligently based on data length
  const interval = Math.max(0, Math.floor(data.length / 20));

  return (
    <div className="space-y-6">
      {/* Estadísticas resumidas */}
      {stats && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
            <p className="text-sm text-gray-600">Mínimo Gasolina 95</p>
            <p className="text-2xl font-bold text-blue-600">€{stats.gasolina_95_stats?.min || 'N/A'}</p>
          </div>
          <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
            <p className="text-sm text-gray-600">Máximo Gasolina 95</p>
            <p className="text-2xl font-bold text-blue-600">€{stats.gasolina_95_stats?.max || 'N/A'}</p>
          </div>
          <div className="bg-green-50 p-4 rounded-lg border border-green-200">
            <p className="text-sm text-gray-600">Mínimo Gasóleo A</p>
            <p className="text-2xl font-bold text-green-600">€{stats.gasoleoa_stats?.min || 'N/A'}</p>
          </div>
          <div className="bg-green-50 p-4 rounded-lg border border-green-200">
            <p className="text-sm text-gray-600">Máximo Gasóleo A</p>
            <p className="text-2xl font-bold text-green-600">€{stats.gasoleoa_stats?.max || 'N/A'}</p>
          </div>
        </div>
      )}

      {/* Gráfico principal */}
      <div className="bg-white p-6 rounded-lg">
        <p className="text-sm text-gray-600 mb-4">
          📊 Histórico de {data.length} días - Precios reales actualizados DIARIAMENTE (1 dato por día)
        </p>
        <ResponsiveContainer width="100%" height={400}>
          <LineChart
            data={data}
            margin={{ top: 5, right: 30, left: 0, bottom: 5 }}
          >
            <defs>
              <linearGradient id="colorGasolina" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.8} />
                <stop offset="95%" stopColor="#3b82f6" stopOpacity={0.1} />
              </linearGradient>
              <linearGradient id="colorGasoleoa" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#10b981" stopOpacity={0.8} />
                <stop offset="95%" stopColor="#10b981" stopOpacity={0.1} />
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
              labelFormatter={(label: any) => `📅 Día: ${label}`}
              wrapperStyle={{ outline: 'none' }}
            />
            <Legend
              verticalAlign="top"
              height={36}
              wrapperStyle={{ paddingBottom: '20px' }}
            />
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
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Información adicional */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-blue-50 p-4 rounded-lg">
            <h3 className="font-bold text-blue-900 mb-3">Gasolina 95 - Últimos 90 días</h3>
            <div className="space-y-2 text-sm">
              <p>Promedio: <span className="font-bold">€{stats.gasolina_95_stats?.avg || 'N/A'}/L</span></p>
              <p>Cambio: <span className="font-bold">{stats.gasolina_95_stats?.change_percent || 'N/A'}% ({stats.gasolina_95_stats?.change || 'N/A'}€)</span></p>
              <p>Precio actual: <span className="font-bold">€{stats.gasolina_95_stats?.current || 'N/A'}/L</span></p>
            </div>
          </div>
          <div className="bg-green-50 p-4 rounded-lg">
            <h3 className="font-bold text-green-900 mb-3">Gasóleo A - Últimos 90 días</h3>
            <div className="space-y-2 text-sm">
              <p>Promedio: <span className="font-bold">€{stats.gasoleoa_stats?.avg || 'N/A'}/L</span></p>
              <p>Cambio: <span className="font-bold">{stats.gasoleoa_stats?.change_percent || 'N/A'}% ({stats.gasoleoa_stats?.change || 'N/A'}€)</span></p>
              <p>Precio actual: <span className="font-bold">€{stats.gasoleoa_stats?.current || 'N/A'}/L</span></p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
