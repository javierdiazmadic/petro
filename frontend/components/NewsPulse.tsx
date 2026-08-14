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

interface NewsPulseProps {
  events: NewsEvent[];
}

export function NewsPulse({ events }: NewsPulseProps) {
  const getCategoryIcon = (category: string) => {
    const icons: Record<string, string> = {
      'OPEC': '⛽',
      'Refinería': '🏭',
      'Geopolítica': '🌍',
      'Divisas': '💱',
      'Demanda': '📊',
      'Subvenciones': '💰',
      'Impuestos': '📋',
      'Energías Renovables': '♻️',
      'Transporte': '🚗',
      'default': '📰'
    };
    return icons[category] || icons['default'];
  };

  const getSentimentEmoji = (sentiment: string) => {
    switch (sentiment) {
      case 'positive': return '😊';
      case 'negative': return '😟';
      default: return '😐';
    }
  };

  const getImpactBg = (impact: number) => {
    if (impact > 0.05) return 'bg-red-100 border-red-300';
    if (impact > 0) return 'bg-orange-100 border-orange-300';
    if (impact < -0.05) return 'bg-green-100 border-green-300';
    if (impact < 0) return 'bg-lime-100 border-lime-300';
    return 'bg-gray-100 border-gray-300';
  };

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    const today = new Date();
    const yesterday = new Date(today);
    yesterday.setDate(yesterday.getDate() - 1);

    if (date.toDateString() === today.toDateString()) {
      return `Hoy ${date.toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' })}`;
    } else if (date.toDateString() === yesterday.toDateString()) {
      return `Ayer ${date.toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' })}`;
    }
    return date.toLocaleDateString('es-ES') + ' ' + date.toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' });
  };

  if (!events || events.length === 0) {
    return (
      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl shadow-lg p-8 border-2 border-blue-200">
        <h2 className="text-3xl font-bold text-gray-900 mb-4 flex items-center gap-3">
          <span className="text-4xl animate-pulse">📰</span>
          <span>Noticias del Mercado</span>
        </h2>
        <p className="text-gray-500 text-center py-12 text-lg">📡 Sin noticias relevantes en este momento</p>
      </div>
    );
  }

  const sortedEvents = [...events].sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime());
  const maxImpact = Math.max(...sortedEvents.map(e => Math.abs(e.impact_price_eur)));

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-indigo-600 rounded-xl shadow-lg p-6 text-white">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-3xl font-bold flex items-center gap-3 mb-2">
              <span className="text-4xl animate-pulse">📰</span>
              Noticias del Mercado de Carburantes
            </h2>
            <p className="text-blue-100">Últimas noticias sobre combustibles, subvenciones e impuestos</p>
          </div>
          <div className="text-right">
            <p className="text-3xl font-bold">{events.length}</p>
            <p className="text-blue-100">noticias activas</p>
          </div>
        </div>
      </div>

      {/* News Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {sortedEvents.map((event, idx) => (
          <div
            key={event.id || idx}
            className={`rounded-lg p-5 border-2 transition-all hover:shadow-lg ${getImpactBg(event.impact_price_eur)}`}
          >
            {/* Header */}
            <div className="flex items-start justify-between mb-3">
              <div className="flex items-start gap-3 flex-1">
                <span className="text-3xl">{getCategoryIcon(event.category)}</span>
                <div className="flex-1">
                  <h3 className="font-bold text-gray-900 text-sm md:text-base leading-snug">{event.title}</h3>
                  <p className="text-xs text-gray-500 mt-1">{event.category}</p>
                </div>
              </div>
              <span className="text-2xl ml-2">{getSentimentEmoji(event.sentiment)}</span>
            </div>

            {/* Description */}
            <p className="text-sm text-gray-700 mb-3 line-clamp-2">{event.description}</p>

            {/* Impact & Source */}
            <div className="flex items-center justify-between flex-wrap gap-2">
              <div className="flex items-center gap-2">
                <span className="text-xs font-bold px-2 py-1 rounded bg-white bg-opacity-60">
                  {event.source || 'Reuters'}
                </span>
                {event.confidence && (
                  <span className="text-xs text-gray-600">
                    Confianza: {Math.round(event.confidence * 100)}%
                  </span>
                )}
              </div>

              {/* Impact Bar */}
              <div className="flex items-center gap-2">
                <span className="text-xs font-bold">
                  {event.impact_price_eur >= 0 ? '📈 +' : '📉 '}{Math.abs(event.impact_price_eur).toFixed(3)}€/L
                </span>
                <div className="w-24 h-2 bg-white bg-opacity-50 rounded-full overflow-hidden">
                  <div
                    className={`h-full ${event.impact_price_eur > 0 ? 'bg-red-500' : 'bg-green-500'}`}
                    style={{
                      width: `${(Math.abs(event.impact_price_eur) / (maxImpact || 0.1)) * 100}%`
                    }}
                  />
                </div>
              </div>
            </div>

            {/* Timestamp */}
            <p className="text-xs text-gray-500 mt-3 pt-3 border-t border-gray-300 border-opacity-50">
              🕐 {formatDate(event.date)}
            </p>
          </div>
        ))}
      </div>

      {/* Summary Stats */}
      <div className="bg-white rounded-lg p-4 border border-gray-200">
        <div className="grid grid-cols-3 md:grid-cols-5 gap-4 text-center">
          <div>
            <p className="text-xs text-gray-500">Total Noticias</p>
            <p className="text-lg md:text-2xl font-bold text-gray-900">{events.length}</p>
          </div>
          <div>
            <p className="text-xs text-gray-500">Impacto Positivo</p>
            <p className="text-lg md:text-2xl font-bold text-green-600">
              {events.filter(e => e.impact_price_eur < 0).length}
            </p>
          </div>
          <div>
            <p className="text-xs text-gray-500">Impacto Negativo</p>
            <p className="text-lg md:text-2xl font-bold text-red-600">
              {events.filter(e => e.impact_price_eur > 0).length}
            </p>
          </div>
          <div>
            <p className="text-xs text-gray-500">Neutral</p>
            <p className="text-lg md:text-2xl font-bold text-gray-600">
              {events.filter(e => e.impact_price_eur === 0).length}
            </p>
          </div>
          <div>
            <p className="text-xs text-gray-500">Impacto Total</p>
            <p className={`text-lg md:text-2xl font-bold ${
              events.reduce((sum, e) => sum + e.impact_price_eur, 0) < 0 ? 'text-green-600' : 'text-red-600'
            }`}>
              {(events.reduce((sum, e) => sum + e.impact_price_eur, 0)).toFixed(3)}€/L
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
