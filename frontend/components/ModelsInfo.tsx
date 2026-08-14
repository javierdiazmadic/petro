'use client';

import { useEffect, useState } from 'react';
import { modelsAPI } from '@/lib/api';
import { TrendingUp, RefreshCw, AlertCircle } from 'lucide-react';

interface ModelMetrics {
  r2: number;
  rmse: number;
  mae: number;
  accuracy: string;
}

interface Model {
  name: string;
  framework: string;
  metrics: ModelMetrics;
  training_date: string;
  input_features: number;
  available: boolean;
}

interface ModelsData {
  timestamp: string;
  best_model: string;
  total_models: number;
  loaded_models: number;
  models: Record<string, Model>;
}

export const ModelsInfo = () => {
  const [modelsData, setModelsData] = useState<ModelsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchModelsInfo = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await modelsAPI.getModelsInfo();
      setModelsData(response.data);
    } catch (err) {
      setError('Error cargando información de modelos');
      console.error('Error fetching models info:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = async () => {
    try {
      setRefreshing(true);
      await modelsAPI.refreshModels();
      await fetchModelsInfo();
    } catch (err) {
      setError('Error al recargar modelos');
      console.error('Error refreshing models:', err);
    } finally {
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchModelsInfo();
  }, []);

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-start gap-3">
        <AlertCircle className="text-red-500 mt-1 flex-shrink-0" size={20} />
        <div className="flex-1">
          <p className="text-red-700 font-semibold">Error</p>
          <p className="text-red-600 text-sm">{error}</p>
        </div>
      </div>
    );
  }

  if (loading || !modelsData) {
    return (
      <div className="bg-gray-50 rounded-lg p-8 text-center">
        <div className="inline-block">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
        </div>
        <p className="text-gray-600 mt-4">Cargando información de modelos...</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <TrendingUp className="text-blue-600" size={24} />
          <div>
            <h3 className="text-lg font-semibold text-gray-900">Modelos Entrenados</h3>
            <p className="text-sm text-gray-500">
              {modelsData.loaded_models}/{modelsData.total_models} modelos cargados
            </p>
          </div>
        </div>
        <button
          onClick={handleRefresh}
          disabled={refreshing}
          className="flex items-center gap-2 px-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
        >
          <RefreshCw size={16} className={refreshing ? 'animate-spin' : ''} />
          {refreshing ? 'Recargando...' : 'Recargar'}
        </button>
      </div>

      {/* Best Model Highlight */}
      {modelsData.best_model && modelsData.models[modelsData.best_model] && (
        <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-center gap-2 mb-2">
            <span className="bg-blue-100 text-blue-700 px-3 py-1 rounded-full text-sm font-semibold">
              🏆 Mejor Modelo
            </span>
          </div>
          <h4 className="font-semibold text-gray-900 mb-2">
            {modelsData.models[modelsData.best_model].name}
          </h4>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            <div>
              <p className="text-sm text-gray-600">R²</p>
              <p className="text-lg font-bold text-blue-600">
                {modelsData.models[modelsData.best_model].metrics.r2.toFixed(4)}
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-600">RMSE</p>
              <p className="text-lg font-bold text-green-600">
                {modelsData.models[modelsData.best_model].metrics.rmse.toFixed(4)}
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-600">MAE</p>
              <p className="text-lg font-bold text-purple-600">
                {modelsData.models[modelsData.best_model].metrics.mae.toFixed(4)}
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Accuracy</p>
              <p className="text-lg font-bold text-orange-600">
                {modelsData.models[modelsData.best_model].metrics.accuracy}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* All Models Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {Object.entries(modelsData.models).map(([modelKey, model]) => (
          <div
            key={modelKey}
            className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-lg transition-shadow"
          >
            <div className="flex items-start justify-between mb-3">
              <div>
                <h4 className="font-semibold text-gray-900">{model.name}</h4>
                <p className="text-xs text-gray-500 capitalize">{model.framework}</p>
              </div>
              {model.available ? (
                <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                  ✓ Cargado
                </span>
              ) : (
                <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                  ✗ Error
                </span>
              )}
            </div>

            {model.available ? (
              <>
                <div className="space-y-2 mb-3">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">R²:</span>
                    <span className="font-semibold text-blue-600">
                      {model.metrics.r2.toFixed(4)}
                    </span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">RMSE:</span>
                    <span className="font-semibold text-green-600">
                      {model.metrics.rmse.toFixed(4)}
                    </span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">MAE:</span>
                    <span className="font-semibold text-purple-600">
                      {model.metrics.mae.toFixed(4)}
                    </span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Accuracy:</span>
                    <span className="font-semibold text-orange-600">
                      {model.metrics.accuracy}
                    </span>
                  </div>
                </div>

                <div className="pt-3 border-t border-gray-200">
                  <p className="text-xs text-gray-500">
                    Entrenado: {new Date(model.training_date).toLocaleDateString('es-ES')}
                  </p>
                  <p className="text-xs text-gray-500">
                    Features: {model.input_features} variables
                  </p>
                </div>
              </>
            ) : (
              <p className="text-sm text-gray-600 py-4">Error al cargar modelo</p>
            )}
          </div>
        ))}
      </div>

      {/* Metadata */}
      <div className="bg-gray-50 rounded-lg p-3 text-xs text-gray-600">
        <p>Última carga: {new Date(modelsData.timestamp).toLocaleString('es-ES')}</p>
      </div>
    </div>
  );
};
