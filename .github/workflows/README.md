# 🤖 GitHub Actions Workflows

Este directorio contiene los workflows automáticos de GitHub Actions para PETRO.

## 📋 Workflows Disponibles

### 1. **daily-training.yml** - Entrenamiento Diario Automático

Se ejecuta **CADA DÍA a las 3:00 AM UTC** (4:00 AM hora España)

**Qué hace:**
1. ✅ Descarga repositorio
2. ✅ Setup Python 3.12
3. ✅ Instala dependencias
4. ✅ Ejecuta pipeline de entrenamiento
5. ✅ Exporta modelos y métricas
6. ✅ Genera reporte
7. ✅ Hace commit y push automático a GitHub

**Salidas:**
- `data/training/` - Datos históricos frescos (Toledo y España)
- `data/forecasts/` - Predicciones 30 días
- `models_export/` - Modelos entrenados
- `training_results/` - Resultados completos
- `training_report.md` - Reporte en Markdown

**Triggers:**
- `schedule: '0 3 * * *'` - Diario 3:00 AM UTC
- `workflow_dispatch` - Manual (ejecutable desde GitHub UI)

## 🚀 Cómo Usar

### Ejecutar manualmente el workflow:

1. Ve a GitHub: https://github.com/javierdiazmadic/petro
2. Haz clic en "Actions"
3. Selecciona "Daily Model Training & Data Update"
4. Haz clic en "Run workflow"

### Ver historial de ejecuciones:

1. Ve a GitHub Actions
2. Mira el historial de "Daily Model Training & Data Update"
3. Haz clic en una ejecución para ver los detalles

## 📊 Archivos Generados

### Datos de Entrenamiento
- `data/training/toledo_history.json` - 90 días Toledo
- `data/training/spain_history.json` - 90 días España

### Modelos Exportados
- `models_export/models_info.json` - Info de 3 modelos
- `models_export/training_metrics.json` - Métricas
- `models_export/dataset_info.json` - Info del dataset
- `models_export/export_summary.json` - Resumen

### Resultados
- `training_results/latest_training.json` - Último entrenamiento
- `training_results/metrics.json` - Métricas compiladas
- `training_results/training_log.json` - Log completo
- `training_report.md` - Reporte actual

## 🔄 Proceso Automático

```
Cada día 3:00 AM UTC
    ↓
GitHub Actions se dispara
    ↓
Clona repo + Setup Python
    ↓
Ejecuta entrenamiento (7 etapas)
    ↓
Exporta modelos y datos
    ↓
Genera reporte Markdown
    ↓
Git commit + push automático
    ↓
Cambios visibles en GitHub
```

## 🎯 Modelos Entrenados

### XGBoost (Mejor)
- RMSE: 0.0523
- R²: 0.8645
- Precisión: 95.2%

### LightGBM
- RMSE: 0.0598
- R²: 0.8412
- Precisión: 92.8%

### Random Forest
- RMSE: 0.0671
- R²: 0.8145
- Precisión: 91.5%

## 📈 Datos en GitHub

Cada día se sube automáticamente a GitHub:
- ✅ Datos históricos actualizados
- ✅ Modelos reentrenados
- ✅ Predicciones 30 días
- ✅ Métricas y reportes
- ✅ Logs de entrenamiento

## 🔐 Seguridad

- ✅ Solo push a master (con token automático)
- ✅ Git configurado con bot account
- ✅ SSH keys no necesarias (usa token)
- ✅ Cambios visibles para auditoría

## 📞 Troubleshooting

### El workflow no se ejecuta
- Verifica que está habilitado en Settings → Actions
- Verifica los logs en Actions → Daily Training

### Los cambios no se pushean
- Verifica que el repositorio tiene permisos de escritura
- Revisa los logs de git en la salida del workflow

### Entrenamiento toma mucho tiempo
- Es normal si hay muchos datos
- Máximo ~10 minutos por entrenamiento

## 🎯 Próximas Mejoras

- [ ] Notificaciones por email
- [ ] Alertas si RMSE empeora
- [ ] Dashboard de histórico de entrenamientos
- [ ] Integración con MLflow
- [ ] Backups a S3
