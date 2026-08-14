import axios from 'axios';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const dashboardAPI = {
  getStats: () => api.get('/api/v1/dashboard/stats'),
  // IMPORTANTE: Ahora retorna 90 días de datos DIARIOS (no por horas)
  // Cada datapoint es el precio del día
  // province: "spain" (default) o "toledo" para precios de Toledo
  // Con cache buster (_t) para asegurar datos frescos
  getPriceHistory: (days = 90, province = 'spain') => {
    const cacheBuster = Date.now();
    return api.get(`/api/v1/dashboard/prices/history?days=${days}&province=${province}&_t=${cacheBuster}`);
  },
  getBrentHistory: (limit = 168) => api.get(`/api/v1/dashboard/brent/history?limit=${limit}`),
  getMetrics: () => api.get('/api/v1/dashboard/metrics'),
  getHealth: () => api.get('/api/v1/dashboard/health'),
};

// Toledo Gas Stations API endpoints
export const toledoAPI = {
  // Get all gas stations in Toledo with current prices
  getGasStations: (maxDistanceKm = 100, fuelType = 'gasoleoa') =>
    api.get(`/api/v1/toledo/gas-stations?max_distance_km=${maxDistanceKm}&fuel_type=${fuelType}`),

  // Get cheapest gas stations (top 15)
  getCheapest: (fuelType = 'gasoleoa', limit = 15, filterType = 'todas') =>
    api.get(`/api/v1/toledo/cheapest?fuel_type=${fuelType}&limit=${limit}&filter_type=${filterType}`),

  // Get detailed analysis by distance/price ratio
  getAnalysis: (fuelType = 'gasoleoa', maxDistanceKm = 100) =>
    api.get(`/api/v1/toledo/analysis?fuel_type=${fuelType}&max_distance_km=${maxDistanceKm}`),

  // Get ALL gas stations (246 total) - all brands in Toledo
  // Con cache buster (_t) para asegurar datos frescos
  getAllStations: (maxDistanceKm = 100) => {
    const cacheBuster = Date.now();
    return api.get(`/api/v1/toledo/all-stations?max_distance_km=${maxDistanceKm}&_t=${cacheBuster}`);
  },

  // Get ONLY Repsol gas stations (79 total)
  getRepsol: (maxDistanceKm = 100) =>
    api.get(`/api/v1/toledo/repsol?max_distance_km=${maxDistanceKm}`),
};

// Prediction API endpoints
export const predictionAPI = {
  // Get 30-day price forecast
  getForecast: (commodity = 'gasolina_95', days = 30) =>
    api.get(`/api/v1/predictions/forecast?commodity=${commodity}&days=${days}`),

  // Get news analysis with impact on prices
  getNewsAnalysis: () => api.get('/api/v1/predictions/news-analysis'),

  // Get backtesting results to validate model
  getBacktest: (commodity = 'gasolina_95', days = 90) =>
    api.get(`/api/v1/predictions/backtest?commodity=${commodity}&days=${days}`),

  // Get movement probabilities (up/down/stable)
  getProbabilities: (commodity = 'gasolina_95') =>
    api.get(`/api/v1/predictions/probabilities?commodity=${commodity}`),

  // Get AI recommendation based on forecasts
  getRecommendation: () => api.get('/api/v1/predictions/recommendation'),
};

// Models API endpoints
export const modelsAPI = {
  // Get information about all trained models
  // Returns: best_model, loaded_models count, metrics for each
  getModelsInfo: () => api.get('/api/v1/models/info'),

  // Get the best performing model (highest R²)
  // Returns: xgboost, lightgbm, or randomforest with metrics
  getBestModel: () => api.get('/api/v1/models/best'),

  // Get detailed info about a specific model
  // modelName: 'xgboost', 'lightgbm', or 'randomforest'
  getModel: (modelName: string) =>
    api.get(`/api/v1/models/${modelName}`),

  // Force reload models from cache
  // Useful after new training or manual updates
  refreshModels: () => api.post('/api/v1/models/refresh'),
};
