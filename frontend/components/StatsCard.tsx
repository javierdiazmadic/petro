'use client';

interface StatsCardProps {
  filter: 'todas' | 'repsol';
  averages: {
    gasolina_95: number;
    gasoleoa: number;
  };
  stationCount: number;
  toledoAverage?: {
    gasolina_95: number;
    gasoleoa: number;
  };
}

export function StatsCard({ filter, averages, stationCount, toledoAverage }: StatsCardProps) {
  const isRepsol = filter === 'repsol';

  const gasolinaDiff = toledoAverage
    ? (averages.gasolina_95 - toledoAverage.gasolina_95).toFixed(3)
    : '0.000';

  const gasoleoDiff = toledoAverage
    ? (averages.gasoleoa - toledoAverage.gasoleoa).toFixed(3)
    : '0.000';

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 animate-fade-in">
      {/* Gasolina 95 */}
      <div className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl p-6 text-white shadow-lg hover:shadow-xl transition-all">
        <div className="flex justify-between items-start">
          <div>
            <p className="text-blue-100 text-sm font-medium">Gasolina 95</p>
            <p className="text-3xl font-bold mt-2">€{averages.gasolina_95.toFixed(3)}</p>
            {isRepsol && toledoAverage && (
              <p className={`text-sm mt-2 ${parseFloat(gasolinaDiff) > 0 ? 'text-red-200' : 'text-green-200'}`}>
                {parseFloat(gasolinaDiff) > 0 ? '📈' : '📉'} {gasolinaDiff}€ vs Toledo
              </p>
            )}
          </div>
          <div className="text-3xl">⛽</div>
        </div>
      </div>

      {/* Gasóleo A */}
      <div className="bg-gradient-to-br from-green-500 to-green-600 rounded-xl p-6 text-white shadow-lg hover:shadow-xl transition-all">
        <div className="flex justify-between items-start">
          <div>
            <p className="text-green-100 text-sm font-medium">Gasóleo A</p>
            <p className="text-3xl font-bold mt-2">€{averages.gasoleoa.toFixed(3)}</p>
            {isRepsol && toledoAverage && (
              <p className={`text-sm mt-2 ${parseFloat(gasoleoDiff) > 0 ? 'text-red-200' : 'text-green-200'}`}>
                {parseFloat(gasoleoDiff) > 0 ? '📈' : '📉'} {gasoleoDiff}€ vs Toledo
              </p>
            )}
          </div>
          <div className="text-3xl">🛢️</div>
        </div>
      </div>

      {/* Total de Estaciones */}
      <div className="bg-gradient-to-br from-purple-500 to-purple-600 rounded-xl p-6 text-white shadow-lg hover:shadow-xl transition-all">
        <div className="flex justify-between items-start">
          <div>
            <p className="text-purple-100 text-sm font-medium">Total Estaciones</p>
            <p className="text-3xl font-bold mt-2">{stationCount}</p>
            <p className="text-sm mt-2 text-purple-200">
              {filter === 'todas' ? '🏢 Todas las marcas' : '⭐ Solo Repsol'}
            </p>
          </div>
          <div className="text-3xl">{filter === 'todas' ? '🏢' : '⭐'}</div>
        </div>
      </div>

      {/* Filtro Actual */}
      <div className={`bg-gradient-to-br rounded-xl p-6 text-white shadow-lg hover:shadow-xl transition-all ${
        isRepsol
          ? 'from-yellow-500 to-yellow-600'
          : 'from-indigo-500 to-indigo-600'
      }`}>
        <div className="flex justify-between items-start">
          <div>
            <p className="text-opacity-90 text-sm font-medium">Filtro Activo</p>
            <p className="text-2xl font-bold mt-2">
              {isRepsol ? 'REPSOL' : 'TODAS'}
            </p>
            <p className="text-sm mt-2 text-opacity-75">
              {isRepsol
                ? '79 gasolineras'
                : '246 gasolineras'
              }
            </p>
          </div>
          <div className="text-3xl">{isRepsol ? '⭐' : '🏢'}</div>
        </div>
      </div>
    </div>
  );
}
