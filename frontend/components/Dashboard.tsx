'use client';

import { useEffect, useState } from 'react';
import { dashboardAPI, predictionAPI, toledoAPI } from '@/lib/api';
import { PriceChart } from './PriceChart';
import { PredictionChart } from './PredictionChart';
import { NewsAnalysis } from './NewsAnalysis';
import { BacktestResults } from './BacktestResults';
import { GasStationsList } from './GasStationsList';
import { RecommendationCard } from './RecommendationCard';
import { ProbabilityCard } from './ProbabilityCard';
import { ToledoAnalysis } from './ToledoAnalysis';
import { FilterButtonsBar } from './FilterButtonsBar';
import { GasStationsTableDynamic } from './GasStationsTableDynamic';
import { ComparisonChart } from './ComparisonChart';
import { StatsCard } from './StatsCard';
import { ToledoGasStationsMap } from './ToledoGasStationsMap';

export function Dashboard() {
  const [stats, setStats] = useState<any>(null);
  const [priceHistory, setPriceHistory] = useState<any>(null);
  const [priceChartData, setPriceChartData] = useState<any[]>([]);
  const [metrics, setMetrics] = useState<any>(null);
  const [health, setHealth] = useState<any>(null);

  // Prediction data
  const [forecast, setForecast] = useState<any>(null);
  const [newsAnalysis, setNewsAnalysis] = useState<any>(null);
  const [backtest, setBacktest] = useState<any>(null);
  const [probabilities, setProbabilities] = useState<any>(null);
  const [recommendation, setRecommendation] = useState<any>(null);

  // Toledo gas stations
  const [gasStations, setGasStations] = useState<any[]>([]);
  const [gasStationsLoading, setGasStationsLoading] = useState(false);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedProvince, setSelectedProvince] = useState<'spain' | 'toledo'>('toledo');
  const [selectedFilter, setSelectedFilter] = useState<'todas' | 'repsol'>('todas');

  const fetchData = async (province: string = 'toledo') => {
    try {
      setError(null);
      console.log('Fetching from API...', process.env.NEXT_PUBLIC_API_URL);

      const [statsRes, priceRes, metricsRes, healthRes, forecastRes, newsRes, backtestRes, probRes, recRes, stationsRes] = await Promise.all([
        dashboardAPI.getStats().catch((e) => { console.error('stats error:', e.message); return { data: null }; }),
        dashboardAPI.getPriceHistory(90, province).catch((e) => { console.error('price history error:', e.message); return { data: null }; }),
        dashboardAPI.getMetrics().catch((e) => { console.error('metrics error:', e.message); return { data: null }; }),
        dashboardAPI.getHealth().catch((e) => { console.error('health error:', e.message); return { data: null }; }),
        predictionAPI.getForecast('gasolina_95', 30).catch((e) => { console.error('forecast error:', e.message); return { data: null }; }),
        predictionAPI.getNewsAnalysis().catch((e) => { console.error('news error:', e.message); return { data: null }; }),
        predictionAPI.getBacktest('gasolina_95', 90).catch((e) => { console.error('backtest error:', e.message); return { data: null }; }),
        predictionAPI.getProbabilities('gasolina_95').catch((e) => { console.error('prob error:', e.message); return { data: null }; }),
        predictionAPI.getRecommendation().catch((e) => { console.error('rec error:', e.message); return { data: null }; }),
        toledoAPI.getCheapest('gasoleoa', 15).catch((e) => { console.error('stations error:', e.message); return { data: null }; }),
      ]);

      console.log('API Response:', { statsRes: statsRes?.data, priceRes: priceRes?.data });

      if (statsRes?.data) setStats(statsRes.data);
      if (metricsRes?.data) setMetrics(metricsRes.data);
      if (healthRes?.data) setHealth(healthRes.data);
      if (forecastRes?.data) setForecast(forecastRes.data);
      if (newsRes?.data) setNewsAnalysis(newsRes.data);
      if (backtestRes?.data) setBacktest(backtestRes.data);
      if (probRes?.data) setProbabilities(probRes.data);
      if (recRes?.data) setRecommendation(recRes.data);
      if (stationsRes?.data) setGasStations(stationsRes.data.stations || []);

      // Procesar histórico de precios DIARIOS
      if (priceRes?.data) {
        setPriceHistory(priceRes.data);

        // Convertir timestamps a formato de fecha (día/mes) - robusto para diferentes formatos
        const chartData = priceRes.data.timestamps?.map((ts: string, idx: number) => {
          let date;
          if (ts.includes('T')) {
            // ISO format: "2026-05-06T14:35:09.868487"
            date = new Date(ts);
          } else {
            // Date format: "2026-06-01"
            date = new Date(ts + 'T00:00:00');
          }

          return {
            date: date.toLocaleDateString('es-ES', { month: 'short', day: 'numeric' }),
            fullDate: ts,
            gasolina_95: parseFloat(priceRes.data.gasolina_95?.[idx]) || 0,
            gasoleoa: parseFloat(priceRes.data.gasoleoa?.[idx]) || 0,
          };
        }) || [];

        setPriceChartData(chartData);
      }

      setLoading(false);
    } catch (err) {
      console.error('Error fetching dashboard data:', err);
      setError('Error al cargar los datos.');
      setLoading(false);
    }
  };

  useEffect(() => {
    let mounted = true;

    const load = async () => {
      if (mounted) {
        setLoading(true);
        await fetchData(selectedProvince);
        setLoading(false);
      }
    };

    load();

    // Actualizar cada 60 segundos (datos diarios, no necesita actualizar más frecuente)
    const interval = setInterval(() => {
      if (mounted) fetchData(selectedProvince);
    }, 60000);

    return () => {
      mounted = false;
      clearInterval(interval);
    };
  }, [selectedProvince]);

  const latestPrice = stats?.latest_price;

  // Indicadores de carga
  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 flex items-center justify-center">
        <div className="text-center">
          <div className="mb-6">
            <div className="w-16 h-16 mx-auto mb-4 rounded-full border-4 border-gray-200 border-t-blue-600 animate-spin"></div>
          </div>
          <h2 className="text-2xl font-bold text-gray-800 mb-2">Cargando PETRO Dashboard</h2>
          <p className="text-gray-600">Conectando con los servidores...</p>
          <div className="mt-6 flex gap-2 justify-center">
            <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce" style={{ animationDelay: '0s' }}></div>
            <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
            <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-12">
          <div className="flex items-center gap-3 mb-3">
            <div className="text-4xl">⚡</div>
            <h1 className="text-5xl font-bold text-white">PETRO</h1>
          </div>
          <p className="text-gray-300 text-lg">Sistema de predicción de precios de combustibles en España</p>
          {error && <p className="text-red-400 mt-2">{error}</p>}
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
          <div className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl p-6 text-white shadow-lg hover:shadow-xl transition-shadow">
            <div className="flex justify-between items-start">
              <div>
                <p className="text-blue-100 text-sm font-medium">Gasolina 95</p>
                <p className="text-4xl font-bold mt-2">€{latestPrice?.gasolina_95?.toFixed(3) || '0.000'}</p>
              </div>
              <div className="text-3xl">⛽</div>
            </div>
          </div>

          <div className="bg-gradient-to-br from-green-500 to-green-600 rounded-xl p-6 text-white shadow-lg hover:shadow-xl transition-shadow">
            <div className="flex justify-between items-start">
              <div>
                <p className="text-green-100 text-sm font-medium">Gasóleo A</p>
                <p className="text-4xl font-bold mt-2">€{latestPrice?.gasoleoa?.toFixed(3) || '0.000'}</p>
              </div>
              <div className="text-3xl">🛢️</div>
            </div>
          </div>

          <div className="bg-gradient-to-br from-purple-500 to-purple-600 rounded-xl p-6 text-white shadow-lg hover:shadow-xl transition-shadow">
            <div className="flex justify-between items-start">
              <div>
                <p className="text-purple-100 text-sm font-medium">Registros</p>
                <p className="text-4xl font-bold mt-2">{stats?.prices_recorded || 0}</p>
              </div>
              <div className="text-3xl">📊</div>
            </div>
          </div>

          <div className={`bg-gradient-to-br rounded-xl p-6 text-white shadow-lg hover:shadow-xl transition-shadow ${
            stats?.status === 'operational'
              ? 'from-emerald-500 to-emerald-600'
              : 'from-red-500 to-red-600'
          }`}>
            <div className="flex justify-between items-start">
              <div>
                <p className="text-opacity-90 text-sm font-medium">Estado Sistema</p>
                <p className="text-2xl font-bold mt-2">{stats?.status === 'operational' ? 'Operativo' : 'Error'}</p>
              </div>
              <div className="text-3xl">{stats?.status === 'operational' ? '✅' : '❌'}</div>
            </div>
          </div>
        </div>

        {/* Price Chart - USANDO COMPONENTE MEJORADO */}
        <div className="bg-white rounded-xl shadow-lg p-8 hover:shadow-xl transition-shadow mb-12">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
              <span className="text-2xl">📈</span> Evolución de Precios - Últimos 90 Días
            </h2>
            <div className="flex gap-2">
              <button
                onClick={() => setSelectedProvince('toledo')}
                className={`px-4 py-2 rounded-lg font-medium transition ${
                  selectedProvince === 'toledo'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                }`}
              >
                Toledo
              </button>
              <button
                onClick={() => setSelectedProvince('spain')}
                className={`px-4 py-2 rounded-lg font-medium transition ${
                  selectedProvince === 'spain'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                }`}
              >
                España
              </button>
            </div>
          </div>
          {priceChartData.length > 0 ? (
            <PriceChart data={priceChartData} stats={priceHistory} />
          ) : (
            <p className="text-gray-500 text-center py-12">Sin datos disponibles</p>
          )}
          {priceHistory?.province && (
            <p className="text-sm text-gray-500 mt-4">
              📊 Mostrando datos de: <strong>{priceHistory.province === 'toledo' ? 'Toledo' : 'España'}</strong>
            </p>
          )}
        </div>

        {/* RECOMENDACIÓN DESTACADA */}
        {recommendation && (
          <div className="mb-12">
            <RecommendationCard
              recommendation={recommendation.recommendation}
              best_period={recommendation.best_period}
              expected_savings_min={recommendation.expected_savings_min}
              expected_savings_max={recommendation.expected_savings_max}
              days_to_wait={recommendation.days_to_wait}
              confidence={recommendation.confidence}
            />
          </div>
        )}

        {/* SECCIÓN DE PREDICCIONES Y ANÁLISIS */}
        <div className="mb-12">
          {/* Predicción 30 días - FULL WIDTH */}
          {forecast && forecast.data ? (
            <div className="bg-white rounded-xl shadow-lg p-10 mb-12">
              <h2 className="text-3xl font-bold text-gray-900 mb-8 flex items-center gap-2">
                <span className="text-4xl">🔮</span> Predicción de Precios - 30 Días
              </h2>
              <div style={{ minHeight: '500px' }}>
                <PredictionChart data={forecast.data} confidence={forecast.confidence * 100} />
              </div>
              <p className="text-center text-gray-600 text-sm mt-6">
                Predicción basada en análisis histórico, tendencias del mercado y noticias relevantes
              </p>
            </div>
          ) : (
            <div className="bg-white rounded-xl shadow-lg p-8">
              <p className="text-gray-500 text-center py-12">Cargando predicción...</p>
            </div>
          )}

          {/* Probabilidades y Stats */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {probabilities && (
              <div>
                <ProbabilityCard
                  probability_up={probabilities.probability_up}
                  probability_down={probabilities.probability_down}
                  probability_stable={probabilities.probability_stable}
                />
              </div>
            )}
          </div>
        </div>

        {/* Análisis de Noticias */}
        {newsAnalysis && (
          <div className="mb-12">
            <NewsAnalysis events={newsAnalysis.events} />
          </div>
        )}

        {/* Backtesting */}
        {backtest && (
          <div className="mb-12">
            <BacktestResults data={backtest.data} metrics={backtest.metrics} />
          </div>
        )}

        {/* Gasolineras más baratas */}
        <div className="mb-12">
          <GasStationsList
            stations={gasStations}
            loading={gasStationsLoading}
            error={null}
            selectedFilter={selectedFilter}
          />
        </div>

        {/* Gas Stations Filter & Dynamic Table */}
        <div className="bg-gradient-to-br from-white to-gray-50 rounded-xl shadow-lg p-8 mb-12">
          <h2 className="text-3xl font-bold text-gray-900 mb-8 flex items-center gap-2">
            <span className="text-3xl">⛽</span> Sistema de Gasolineras de Toledo
          </h2>

          <FilterButtonsBar
            selectedFilter={selectedFilter}
            onFilterChange={setSelectedFilter}
          />

          <div className="my-12">
            <StatsCard
              filter={selectedFilter}
              averages={{
                gasolina_95: selectedFilter === 'todas' ? 1.735 : 1.805,
                gasoleoa: selectedFilter === 'todas' ? 1.861 : 1.938,
              }}
              stationCount={selectedFilter === 'todas' ? 246 : 79}
              toledoAverage={selectedFilter === 'repsol' ? { gasolina_95: 1.735, gasoleoa: 1.861 } : undefined}
            />
          </div>

          <div className="my-12">
            <ComparisonChart
              selectedFilter={selectedFilter}
              apiUrl={process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}
            />
          </div>

          <div className="my-12">
            <GasStationsTableDynamic
              selectedFilter={selectedFilter}
              apiUrl={process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}
            />
          </div>
        </div>

        {/* Metrics & Services */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Model Metrics */}
          <div className="bg-white rounded-xl shadow-lg p-8 hover:shadow-xl transition-shadow">
            <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center gap-2">
              <span className="text-2xl">🤖</span> Métricas del Modelo
            </h2>
            {metrics ? (
              <>
                <div className="bg-gradient-to-r from-blue-50 to-purple-50 p-4 rounded-lg mb-6">
                  <p className="text-sm text-gray-600">Mejor modelo</p>
                  <p className="text-2xl font-bold text-gray-900">{metrics?.best_model?.toUpperCase() || 'N/A'}</p>
                </div>

                <div className="space-y-3 mb-6">
                  {metrics?.metrics && Object.entries(metrics.metrics).map(([key, value]: [string, any]) => (
                    <div key={key} className="flex justify-between items-center p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition">
                      <span className="text-gray-700 font-medium">{key.toUpperCase()}</span>
                      <span className="text-lg font-bold text-blue-600">{typeof value === 'number' ? value.toFixed(4) : value}</span>
                    </div>
                  ))}
                </div>

                <div className="border-t pt-6">
                  <h3 className="font-bold text-gray-900 mb-4">Comparativa de Modelos</h3>
                  <div className="space-y-3">
                    {metrics?.models && Object.entries(metrics.models).map(([name, model]: [string, any]) => (
                      <div key={name} className="bg-gradient-to-r from-gray-50 to-gray-100 p-4 rounded-lg">
                        <p className="font-bold text-gray-900">{name.replace(/_/g, ' ').toUpperCase()}</p>
                        <div className="text-sm text-gray-600 mt-2 grid grid-cols-3 gap-2">
                          <div><span className="font-medium">RMSE:</span> {model.rmse?.toFixed(4)}</div>
                          <div><span className="font-medium">R²:</span> {model.r2?.toFixed(4)}</div>
                          <div><span className="font-medium">MAE:</span> {model.mae?.toFixed(4)}</div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </>
            ) : (
              <p className="text-gray-500">Sin datos disponibles</p>
            )}
          </div>

          {/* Services Status */}
          <div className="bg-white rounded-xl shadow-lg p-8 hover:shadow-xl transition-shadow">
            <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center gap-2">
              <span className="text-2xl">🔧</span> Estado de Servicios
            </h2>
            {health ? (
              <>
                <div className="space-y-3 mb-6">
                  {Object.entries(health).map(([key, value]: [string, any]) => {
                    if (key === 'timestamp') return null;
                    const isHealthy = value === 'connected' || value === 'running' || value === 'healthy';
                    return (
                      <div key={key} className={`flex items-center justify-between p-4 rounded-lg transition ${
                        isHealthy ? 'bg-emerald-50' : 'bg-red-50'
                      }`}>
                        <span className="text-gray-700 capitalize font-medium">{key.replace(/_/g, ' ')}</span>
                        <div className="flex items-center gap-3">
                          <div className={`w-3 h-3 rounded-full ${isHealthy ? 'bg-emerald-500' : 'bg-red-500'}`}></div>
                          <span className={`text-sm font-bold ${isHealthy ? 'text-emerald-600' : 'text-red-600'}`}>
                            {isHealthy ? '✓ OK' : '✗ ERROR'}
                          </span>
                        </div>
                      </div>
                    );
                  })}
                </div>

                <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
                  <p className="text-sm text-blue-800">
                    <strong>Última actualización:</strong><br/>
                    {new Date(health?.timestamp).toLocaleString('es-ES')}
                  </p>
                </div>
              </>
            ) : (
              <p className="text-gray-500">Sin datos disponibles</p>
            )}
          </div>
        </div>

        {/* Mapa de Gasolineras de Toledo */}
        <div className="mb-12">
          <ToledoGasStationsMap showBrands={true} />
        </div>
      </div>
    </div>
  );
}
