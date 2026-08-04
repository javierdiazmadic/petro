'use client';

interface RecommendationCardProps {
  recommendation: string;
  best_period: string;
  expected_savings_min: number;
  expected_savings_max: number;
  days_to_wait: number;
  confidence: number;
}

export function RecommendationCard({
  recommendation,
  best_period,
  expected_savings_min,
  expected_savings_max,
  days_to_wait,
  confidence,
}: RecommendationCardProps) {
  const getRecommendationColor = (rec: string) => {
    if (rec.toLowerCase().includes('compra ahora')) {
      return 'bg-orange-50 border-orange-200';
    }
    if (rec.toLowerCase().includes('espera')) {
      return 'bg-green-50 border-green-200';
    }
    return 'bg-blue-50 border-blue-200';
  };

  const getHeaderColor = (rec: string) => {
    if (rec.toLowerCase().includes('compra ahora')) {
      return 'bg-orange-100 text-orange-900';
    }
    if (rec.toLowerCase().includes('espera')) {
      return 'bg-green-100 text-green-900';
    }
    return 'bg-blue-100 text-blue-900';
  };

  const getAccentColor = (rec: string) => {
    if (rec.toLowerCase().includes('compra ahora')) {
      return 'bg-orange-500';
    }
    if (rec.toLowerCase().includes('espera')) {
      return 'bg-green-500';
    }
    return 'bg-blue-500';
  };

  const getRecommendationEmoji = (rec: string) => {
    if (rec.toLowerCase().includes('compra ahora')) {
      return '⚡';
    }
    if (rec.toLowerCase().includes('espera')) {
      return '⏳';
    }
    return '📊';
  };

  return (
    <div className={`rounded-xl shadow-lg border-2 p-10 mb-12 ${getRecommendationColor(recommendation)}`}>
      {/* Header */}
      <div className={`${getHeaderColor(recommendation)} rounded-lg p-6 mb-8 border-l-4 ${getAccentColor(recommendation)}`}>
        <h2 className="text-4xl font-bold mb-2 flex items-center gap-3">
          <span className="text-5xl">{getRecommendationEmoji(recommendation)}</span> Recomendación de Compra
        </h2>
        <p className="text-2xl font-bold mt-4">{recommendation}</p>
      </div>

      {/* Confidence Bar */}
      <div className="mb-8 p-6 bg-white rounded-lg border border-gray-200">
        <div className="flex items-center gap-4 mb-3">
          <p className="text-gray-700 font-bold">Nivel de Confianza del Análisis</p>
          <p className="text-3xl font-bold text-gray-900">{(confidence * 100).toFixed(0)}%</p>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-4">
          <div
            className={`${getAccentColor(recommendation)} h-4 rounded-full transition-all`}
            style={{ width: `${confidence * 100}%` }}
          />
        </div>
      </div>

      {/* Key Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-white rounded-lg p-6 border-2 border-gray-200 shadow-sm">
          <p className="text-gray-600 text-sm font-bold uppercase mb-2">📅 Período Óptimo</p>
          <p className="text-3xl font-bold text-gray-900">{best_period}</p>
        </div>

        <div className="bg-white rounded-lg p-6 border-2 border-gray-200 shadow-sm">
          <p className="text-gray-600 text-sm font-bold uppercase mb-2">⏱️ Días de Espera</p>
          <p className="text-3xl font-bold text-gray-900">{days_to_wait} <span className="text-lg">días</span></p>
        </div>

        <div className="bg-white rounded-lg p-6 border-2 border-gray-200 shadow-sm">
          <p className="text-gray-600 text-sm font-bold uppercase mb-2">💰 Ahorro por Litro</p>
          <p className="text-2xl font-bold text-gray-900">€{expected_savings_min.toFixed(3)} → €{expected_savings_max.toFixed(3)}</p>
        </div>
      </div>

      {/* Detailed Analysis */}
      <div className="bg-white rounded-lg p-6 border-2 border-gray-200">
        <p className="text-gray-900 text-lg font-bold mb-6 flex items-center gap-2">
          <span>📋</span> Análisis Detallado
        </p>
        <ul className="space-y-4">
          <li className="flex items-start gap-3 pb-4 border-b border-gray-200">
            <span className="text-2xl mt-1">🎯</span>
            <div>
              <p className="font-bold text-gray-900">Ahorro Estimado</p>
              <p className="text-gray-700">€{expected_savings_min.toFixed(3)}/L a €{expected_savings_max.toFixed(3)}/L en próximas compras</p>
            </div>
          </li>
          <li className="flex items-start gap-3 pb-4 border-b border-gray-200">
            <span className="text-2xl mt-1">📈</span>
            <div>
              <p className="font-bold text-gray-900">Tendencia del Mercado</p>
              <p className="text-gray-700">Precios bajando en los próximos <strong>{days_to_wait} días</strong></p>
            </div>
          </li>
          <li className="flex items-start gap-3 pb-4 border-b border-gray-200">
            <span className="text-2xl mt-1">📍</span>
            <div>
              <p className="font-bold text-gray-900">Mejor Momento para Comprar</p>
              <p className="text-gray-700">{best_period}</p>
            </div>
          </li>
          <li className="flex items-start gap-3">
            <span className="text-2xl mt-1">✅</span>
            <div>
              <p className="font-bold text-gray-900">Modelo Predictivo</p>
              <p className="text-gray-700">Análisis basado en IA con <strong>{(confidence * 100).toFixed(0)}% de confianza</strong></p>
            </div>
          </li>
        </ul>
      </div>
    </div>
  );
}
