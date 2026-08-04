'use client';

interface NewsEvent {
  id: string;
  title: string;
  date: string;
  category: string;
  impact_price_eur: number;
  sentiment: 'positive' | 'negative' | 'neutral';
  description: string;
  source?: string;
  confidence?: number;
}

interface NewsAnalysisProps {
  events: NewsEvent[];
}

export function NewsAnalysis({ events }: NewsAnalysisProps) {
  if (!events || events.length === 0) {
    return (
      <div className="bg-white rounded-xl shadow-lg p-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center gap-2">
          <span className="text-2xl">📰</span> Análisis de Noticias
        </h2>
        <p className="text-gray-500 text-center py-12">Sin noticias relevantes disponibles</p>
      </div>
    );
  }

  const sortedEvents = [...events].sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime());

  const getTrendColor = (impact: number) => {
    if (impact > 0) return 'text-red-600';
    if (impact < 0) return 'text-green-600';
    return 'text-gray-600';
  };

  const getTrendIcon = (impact: number) => {
    if (impact > 0) return '📈';
    if (impact < 0) return '📉';
    return '➡️';
  };

  const getSentimentColor = (sentiment: string) => {
    switch (sentiment) {
      case 'positive':
        return 'bg-green-100 text-green-800';
      case 'negative':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getSentimentLabel = (sentiment: string) => {
    switch (sentiment) {
      case 'positive':
        return 'Positivo';
      case 'negative':
        return 'Negativo';
      default:
        return 'Neutral';
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-lg p-8">
      <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center gap-2">
        <span className="text-2xl">📰</span> Análisis de Noticias (Top 8)
      </h2>

      <div className="space-y-4">
        {sortedEvents.slice(0, 8).map((event, idx) => (
          <div
            key={event.id || idx}
            className={`border rounded-lg p-4 hover:shadow-md transition ${
              event.impact_price_eur > 0
                ? 'border-red-200 bg-red-50'
                : event.impact_price_eur < 0
                ? 'border-green-200 bg-green-50'
                : 'border-gray-200 hover:bg-gray-50'
            }`}
          >
            <div className="flex justify-between items-start gap-4 mb-3">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-lg font-bold text-gray-900">{event.title}</span>
                  <span className={`px-2 py-1 rounded-full text-xs font-bold ${getSentimentColor(event.sentiment)}`}>
                    {getSentimentLabel(event.sentiment)}
                  </span>
                </div>
                <p className="text-sm text-gray-600">{event.description}</p>
              </div>

              <div className="flex-shrink-0 text-right">
                <p className="text-3xl font-bold mb-1">
                  <span className={getTrendColor(event.impact_price_eur)}>
                    {getTrendIcon(event.impact_price_eur)}
                  </span>
                </p>
                <p className={`text-lg font-bold ${getTrendColor(event.impact_price_eur)}`}>
                  {event.impact_price_eur > 0 ? '+' : ''}{event.impact_price_eur.toFixed(3)}€
                </p>
                <p className="text-xs text-gray-500">por litro</p>
              </div>
            </div>

            <div className="flex items-center justify-between text-xs text-gray-600">
              <div className="flex items-center gap-3">
                <span className="bg-white px-2 py-1 rounded border border-gray-200">
                  {event.category}
                </span>
                <span>📅 {new Date(event.date).toLocaleDateString('es-ES')}</span>
              </div>
              {event.confidence && (
                <span className="text-gray-500">
                  Confianza: {(event.confidence * 100).toFixed(0)}%
                </span>
              )}
            </div>
          </div>
        ))}
      </div>

      {events.length > 8 && (
        <div className="mt-6 text-center">
          <p className="text-sm text-gray-600">
            Mostrando 8 de {events.length} eventos | Total impacto agregado: €{(events.reduce((sum, e) => sum + (e.impact_price_eur || 0), 0)).toFixed(3)}
          </p>
        </div>
      )}
    </div>
  );
}
