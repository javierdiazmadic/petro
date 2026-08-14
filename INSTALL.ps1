# ═══════════════════════════════════════════════════════════════════════════════
# PETRO - INSTALLATION SCRIPT (PowerShell - Windows)
# Instalación completa en tu servidor local
# ═══════════════════════════════════════════════════════════════════════════════

Write-Host "╔═══════════════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║                                                                           ║" -ForegroundColor Cyan
Write-Host "║  🚀 PETRO - INSTALACIÓN COMPLETA (Windows)                              ║" -ForegroundColor Cyan
Write-Host "║                                                                           ║" -ForegroundColor Cyan
Write-Host "║  ✅ TODO se ejecuta en TU servidor (sin equipos externos)                ║" -ForegroundColor Cyan
Write-Host "║  ✅ Entrenamiento local                                                   ║" -ForegroundColor Cyan
Write-Host "║  ✅ Modelos guardados localmente                                          ║" -ForegroundColor Cyan
Write-Host "║  ✅ Dashboard en tiempo real                                              ║" -ForegroundColor Cyan
Write-Host "║                                                                           ║" -ForegroundColor Cyan
Write-Host "╚═══════════════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════════════════════════" -ForegroundColor Yellow
Write-Host "PASO 1: Verificar requisitos" -ForegroundColor Yellow
Write-Host "═══════════════════════════════════════════════════════════════════════════════" -ForegroundColor Yellow

# Verificar Python
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python encontrado: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python no está instalado" -ForegroundColor Red
    Write-Host "   Descarga desde: https://www.python.org/downloads/" -ForegroundColor Yellow
    exit 1
}

# Verificar Git
try {
    $gitVersion = git --version
    Write-Host "✅ Git encontrado: $gitVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Git no está instalado" -ForegroundColor Red
    Write-Host "   Descarga desde: https://git-scm.com/" -ForegroundColor Yellow
    exit 1
}

# Verificar Docker (opcional)
try {
    $dockerVersion = docker --version
    Write-Host "✅ Docker encontrado: $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Docker no está instalado (opcional pero recomendado)" -ForegroundColor Yellow
    Write-Host "   Descarga desde: https://www.docker.com/products/docker-desktop" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════════════════════════" -ForegroundColor Yellow
Write-Host "PASO 2: Descargar código desde GitHub" -ForegroundColor Yellow
Write-Host "═══════════════════════════════════════════════════════════════════════════════" -ForegroundColor Yellow

Write-Host "🔄 Clonando repositorio..." -ForegroundColor Cyan

if (-not (Test-Path "petro")) {
    git clone https://github.com/javierdiazmadic/petro.git
    Set-Location petro
} else {
    Write-Host "📁 Directorio 'petro' ya existe" -ForegroundColor Yellow
    Set-Location petro
    git pull origin master
}

Write-Host "✅ Código descargado" -ForegroundColor Green

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════════════════════════" -ForegroundColor Yellow
Write-Host "PASO 3: Instalar dependencias Python" -ForegroundColor Yellow
Write-Host "═══════════════════════════════════════════════════════════════════════════════" -ForegroundColor Yellow

Write-Host "🔄 Creando virtual environment..." -ForegroundColor Cyan
python -m venv venv

Write-Host "🔄 Activando virtual environment..." -ForegroundColor Cyan
& ".\venv\Scripts\Activate.ps1"

Write-Host "🔄 Instalando dependencias..." -ForegroundColor Cyan
python -m pip install --upgrade pip
pip install -e ".[dev]"

Write-Host "✅ Dependencias instaladas" -ForegroundColor Green

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════════════════════════" -ForegroundColor Yellow
Write-Host "PASO 4: Instalar frontend (Node.js)" -ForegroundColor Yellow
Write-Host "═══════════════════════════════════════════════════════════════════════════════" -ForegroundColor Yellow

try {
    $nodeVersion = node --version
    Write-Host "✅ Node.js encontrado: $nodeVersion" -ForegroundColor Green
    Set-Location frontend
    npm install
    Set-Location ..
    Write-Host "✅ Frontend dependencies instaladas" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Node.js no encontrado" -ForegroundColor Yellow
    Write-Host "   Para usar el frontend, instalar Node.js:" -ForegroundColor Yellow
    Write-Host "   https://nodejs.org/" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════════════════════════" -ForegroundColor Yellow
Write-Host "PASO 5: Opción A - DOCKER (RECOMENDADO)" -ForegroundColor Yellow
Write-Host "═══════════════════════════════════════════════════════════════════════════════" -ForegroundColor Yellow

try {
    $docker = docker --version
    Write-Host ""
    Write-Host "🐳 Con Docker Compose (TODO automático):" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  1. Asegúrate que Docker está corriendo" -ForegroundColor White
    Write-Host "  2. Ejecuta:" -ForegroundColor White
    Write-Host "     PS> docker compose up -d" -ForegroundColor Green
    Write-Host ""
    Write-Host "  3. Espera 30 segundos para que todo inicie" -ForegroundColor White
    Write-Host ""
    Write-Host "  4. Abre en navegador:" -ForegroundColor White
    Write-Host "     👉 http://localhost:3000" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  5. Dashboard estará COMPLETAMENTE FUNCIONAL:" -ForegroundColor White
    Write-Host "     ✅ Gráficos de precios" -ForegroundColor Green
    Write-Host "     ✅ Mapa interactivo" -ForegroundColor Green
    Write-Host "     ✅ Noticias" -ForegroundColor Green
    Write-Host "     ✅ Predicciones" -ForegroundColor Green
    Write-Host "     ✅ Información de modelos" -ForegroundColor Green
    Write-Host ""
    Write-Host "  ⏰ Cada noche a las 3:00 AM UTC:" -ForegroundColor Yellow
    Write-Host "     └─ Entrena automáticamente" -ForegroundColor White
    Write-Host "     └─ Descarga y carga modelos" -ForegroundColor White
    Write-Host "     └─ Todo actualizado mañana" -ForegroundColor White
    Write-Host ""
} catch {
    Write-Host "❌ Docker no está disponible" -ForegroundColor Red
}

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════════════════════════" -ForegroundColor Yellow
Write-Host "PASO 5: Opción B - LOCAL (Python puro)" -ForegroundColor Yellow
Write-Host "═══════════════════════════════════════════════════════════════════════════════" -ForegroundColor Yellow

Write-Host ""
Write-Host "🐍 Sin Docker (más manual pero funciona):" -ForegroundColor Cyan
Write-Host ""
Write-Host "  1. Asegúrate que virtual env está activado:" -ForegroundColor White
Write-Host "     PS> .\venv\Scripts\Activate.ps1" -ForegroundColor Green
Write-Host ""
Write-Host "  2. Ejecuta el scheduler:" -ForegroundColor White
Write-Host "     PS> python scripts\local_daily_scheduler.py" -ForegroundColor Green
Write-Host ""
Write-Host "  3. En OTRA terminal, inicia la API:" -ForegroundColor White
Write-Host "     PS> .\venv\Scripts\Activate.ps1" -ForegroundColor Green
Write-Host "     PS> python -m uvicorn src.petro.api.main:app --reload --port 8000" -ForegroundColor Green
Write-Host ""
Write-Host "  4. En OTRA terminal, ve al frontend:" -ForegroundColor White
Write-Host "     PS> cd frontend && npm run dev" -ForegroundColor Green
Write-Host ""
Write-Host "  5. Abre en navegador:" -ForegroundColor White
Write-Host "     👉 http://localhost:3000" -ForegroundColor Cyan
Write-Host ""

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════════════════════════" -ForegroundColor Yellow
Write-Host "⏰ ENTRENAMIENTO AUTOMÁTICO" -ForegroundColor Yellow
Write-Host "═══════════════════════════════════════════════════════════════════════════════" -ForegroundColor Yellow

Write-Host ""
Write-Host "📅 3:00 AM UTC cada noche:" -ForegroundColor Cyan
Write-Host ""
Write-Host "   1. ⚙️  Entrena 3 modelos (tu GPU lo hace)" -ForegroundColor White
Write-Host "      └─ XGBoost, LightGBM, RandomForest" -ForegroundColor Gray
Write-Host "      └─ Usa últimos 90 días de datos" -ForegroundColor Gray
Write-Host ""
Write-Host "   2. 💾 Exporta .h5 + JSON metadata" -ForegroundColor White
Write-Host "      └─ Archivos en: models_export/" -ForegroundColor Gray
Write-Host ""
Write-Host "   3. 📤 Sube a GitHub" -ForegroundColor White
Write-Host "      └─ https://github.com/javierdiazmadic/petro" -ForegroundColor Gray
Write-Host ""
Write-Host "   4. ↻ Automáticamente descarga y carga" -ForegroundColor White
Write-Host "      └─ ModelsRegistry en memoria" -ForegroundColor Gray
Write-Host ""
Write-Host "   5. ✅ Dashboard obtiene datos frescos" -ForegroundColor White
Write-Host ""
Write-Host "🎯 RESULTADO: Mañana a las 4:00 AM (España)" -ForegroundColor Yellow
Write-Host "   └─ Abre http://localhost:3000" -ForegroundColor White
Write-Host "   └─ TODO está actualizado sin hacer nada" -ForegroundColor White
Write-Host ""

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════════════════════════" -ForegroundColor Yellow
Write-Host "🧪 VER EN TIEMPO REAL (Opcional)" -ForegroundColor Yellow
Write-Host "═══════════════════════════════════════════════════════════════════════════════" -ForegroundColor Yellow

Write-Host ""
Write-Host "Para VER el entrenamiento AHORA (sin esperar a las 3 AM):" -ForegroundColor Cyan
Write-Host ""
Write-Host "  # Ejecutar manualmente el script de entrenamiento" -ForegroundColor White
Write-Host "  PS> python scripts\daily_training.py" -ForegroundColor Green
Write-Host ""
Write-Host "  # O ejecutar el pipeline completo" -ForegroundColor White
Write-Host "  PS> python scripts\daily_training.py; python scripts\export_models_h5.py; python scripts\download_and_load_models.py" -ForegroundColor Green
Write-Host ""
Write-Host "  # O esperar a las 3:00 AM UTC y ver los logs" -ForegroundColor White
Write-Host "  PS> Get-Content -Path training_scheduler.log -Tail 50 -Wait" -ForegroundColor Green
Write-Host ""

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════════════════════════" -ForegroundColor Yellow
Write-Host "📊 LO QUE VERÁS EN EL DASHBOARD" -ForegroundColor Yellow
Write-Host "═══════════════════════════════════════════════════════════════════════════════" -ForegroundColor Yellow

Write-Host ""
Write-Host "  📈 Gráficos de precios (90 días)" -ForegroundColor White
Write-Host "     └─ Toledo + España" -ForegroundColor Gray
Write-Host "     └─ Actualizados diariamente" -ForegroundColor Gray
Write-Host ""
Write-Host "  🗺️ Mapa interactivo" -ForegroundColor White
Write-Host "     └─ 227 gasolineras de Toledo" -ForegroundColor Gray
Write-Host "     └─ Con precios frescos" -ForegroundColor Gray
Write-Host "     └─ Clickeable" -ForegroundColor Gray
Write-Host ""
Write-Host "  📰 Noticias del mercado" -ForegroundColor White
Write-Host "     └─ OPEC, subvenciones, etc" -ForegroundColor Gray
Write-Host "     └─ Análisis de impacto" -ForegroundColor Gray
Write-Host ""
Write-Host "  🤖 Información de modelos" -ForegroundColor White
Write-Host "     └─ Mejor modelo destacado" -ForegroundColor Gray
Write-Host "     └─ Métricas: R², RMSE, MAE" -ForegroundColor Gray
Write-Host "     └─ Botón refresh manual" -ForegroundColor Gray
Write-Host ""
Write-Host "  🔮 Predicciones 30 días" -ForegroundColor White
Write-Host "     └─ Basadas en modelos ML" -ForegroundColor Gray
Write-Host "     └─ Con análisis de impacto" -ForegroundColor Gray
Write-Host ""

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════════════════════════" -ForegroundColor Yellow
Write-Host "🎯 IMPORTANTE - ACLARACIÓN" -ForegroundColor Yellow
Write-Host "═══════════════════════════════════════════════════════════════════════════════" -ForegroundColor Yellow

Write-Host ""
Write-Host "✅ TODO se ejecuta en TU SERVIDOR" -ForegroundColor Green
Write-Host ""
Write-Host "  • Entrenamiento: SE EJECUTA EN TU GPU/CPU" -ForegroundColor White
Write-Host "  • Modelos: SE GUARDAN EN TU MÁQUINA" -ForegroundColor White
Write-Host "  • GitHub: Solo se usa para SINCRONIZACIÓN" -ForegroundColor White
Write-Host "  • Dashboard: SE SIRVE DESDE TU SERVIDOR" -ForegroundColor White
Write-Host ""
Write-Host "  NO NECESITAS equipos externos" -ForegroundColor Yellow
Write-Host "  NO NECESITAS cloud computing" -ForegroundColor Yellow
Write-Host "  TODO es LOCAL" -ForegroundColor Yellow
Write-Host ""

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host "✅ INSTALACIÓN LISTA" -ForegroundColor Green
Write-Host "═══════════════════════════════════════════════════════════════════════════════" -ForegroundColor Green

Write-Host ""
Write-Host "Próximos pasos:" -ForegroundColor Yellow
Write-Host ""
try {
    $docker = docker --version
    Write-Host "  PS> docker compose up -d" -ForegroundColor Green
    Write-Host "  PS> start http://localhost:3000" -ForegroundColor Green
} catch {
    Write-Host "  PS> .\venv\Scripts\Activate.ps1" -ForegroundColor Green
    Write-Host "  PS> python scripts\local_daily_scheduler.py" -ForegroundColor Green
}
Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
