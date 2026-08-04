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
      return 'from-orange-500 to-red-600';
    }
    if (rec.toLowerCase().includes('espera')) {
      return 'from-emerald-500 to-green-600';
    }
    return 'from-blue-500 to-cyan-600';
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
    <div className={`bg-gradient-to-br ${getRecommendationColor(recommendation)} rounded-2xl shadow-2xl p-10 text-white mb-12`}>
      <h2 className="text-4xl font-bold mb-8 flex items-center gap-3">
        <span className="text-5xl">{getRecommendationEmoji(recommendation)}</span> Recomendación de Compra
      </h2>

      {/* Main Recommendation Box */}
      <div className="bg-white bg-opacity-15 backdrop-blur-md rounded-xl p-8 mb-8 border-2 border-white border-opacity-30">
        <p className="text-4xl font-bold mb-4">{recommendation}</p>
        <div className="flex items-center gap-4">
          <div className="flex-1">
            <p className="text-white text-opacity-80 text-lg">Nivel de Confianza</p>
            <div className="w-full bg-white bg-opacity-20 rounded-full h-3 mt-2">
              <div
                className="bg-white h-3 rounded-full transition-all"
                style={{ width: `${confidence * 100}%` }}
              />
            </div>
          </div>
          <p className="text-3xl font-bold">{(confidence * 100).toFixed(0)}%</p>
        </div>
      </div>

      {/* Key Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-white bg-opacity-10 rounded-xl p-6 border border-white border-opacity-25 hover:bg-opacity-15 transition">
          <p className="text-white text-opacity-70 text-sm font-bold uppercase mb-2">📅 Período Óptimo</p>
          <p className="text-3xl font-bold">{best_period}</p>
        </div>

        <div className="bg-white bg-opacity-10 rounded-xl p-6 border border-white border-opacity-25 hover:bg-opacity-15 transition">
          <p className="text-white text-opacity-70 text-sm font-bold uppercase mb-2">⏱️ Días de Espera</p>
          <p className="text-3xl font-bold">{days_to_wait} <span className="text-lg">días</span></p>
        </div>

        <div className="bg-white bg-opacity-10 rounded-xl p-6 border border-white border-opacity-25 hover:bg-opacity-15 transition">
          <p className="text-white text-opacity-70 text-sm font-bold uppercase mb-2">💰 Ahorro por Litro</p>
          <p className="text-3xl font-bold">€{expected_savings_min.toFixed(3)} → €{expected_savings_max.toFixed(3)}</p>
        </div>
      </div>

      {/* Detailed Analysis */}
      <div className="bg-white bg-opacity-10 rounded-xl p-6 border border-white border-opacity-25">
        <p className="text-white text-opacity-90 text-lg font-bold mb-4">📋 Análisis Detallado</p>
        <ul className="space-y-3">
          <li className="flex items-start gap-3">
            <span className="text-2xl mt-1">🎯</span>
            <span className="text-base">Ahorro estimado: <strong>€{expected_savings_min.toFixed(3)}/L a €{expected_savings_max.toFixed(3)}/L</strong> en próximas compras</span>
          </li>
          <li className="flex items-start gap-3">
            <span className="text-2xl mt-1">📈</span>
            <span className="text-base">Tendencia: Precios bajando en los próximos <strong>{days_to_wait} días</strong></span>
          </li>
          <li className="flex items-start gap-3">
            <span className="text-2xl mt-1">📍</span>
            <span className="text-base">Mejor momento: <strong>{best_period}</strong></span>
          </li>
          <li className="flex items-start gap-3">
            <span className="text-2xl mt-1">✅</span>
            <span className="text-base">Basado en modelo predictivo con <strong>{(confidence * 100).toFixed(0)}% confianza</strong></span>
          </li>
        </ul>
      </div>
    </div>
  );
}
