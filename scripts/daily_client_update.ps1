# ═══════════════════════════════════════════════════════════════════════════════
# PETRO - Daily Client Update Script (PowerShell - Windows)
#
# Ejecutar cada mañana para descargar datos actualizados del servidor
# Uso: PowerShell .\scripts\daily_client_update.ps1
# ═══════════════════════════════════════════════════════════════════════════════

Write-Host "╔═══════════════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║                                                                           ║" -ForegroundColor Cyan
Write-Host "║  🔄 PETRO - Actualización diaria de datos (Cliente)                      ║" -ForegroundColor Cyan
Write-Host "║                                                                           ║" -ForegroundColor Cyan
Write-Host "║  Este script descarga los modelos y datos del servidor central            ║" -ForegroundColor Cyan
Write-Host "║  que fueron entrenados durante la noche                                   ║" -ForegroundColor Cyan
Write-Host "║                                                                           ║" -ForegroundColor Cyan
Write-Host "╚═══════════════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════════════════════════" -ForegroundColor Yellow
Write-Host "PASO 1: Obtener ruta del proyecto" -ForegroundColor Yellow
Write-Host "═══════════════════════════════════════════════════════════════════════════════" -ForegroundColor Yellow

# Determinar ruta base (donde está este script)
$scriptPath = $PSScriptRoot
$projectPath = Split-Path -Parent $scriptPath
Write-Host "📁 Directorio del proyecto: $projectPath" -ForegroundColor White
Set-Location $projectPath

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════════════════════════" -ForegroundColor Yellow
Write-Host "PASO 2: Actualizar desde GitHub" -ForegroundColor Yellow
Write-Host "═══════════════════════════════════════════════════════════════════════════════" -ForegroundColor Yellow

Write-Host "🔄 Haciendo git pull origin master..." -ForegroundColor Cyan

try {
    $gitOutput = git pull origin master 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Proyecto actualizado desde GitHub" -ForegroundColor Green
        Write-Host $gitOutput -ForegroundColor Gray
    } else {
        Write-Host "❌ Error en git pull. Verifica tu conexión a GitHub" -ForegroundColor Red
        Write-Host $gitOutput -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "❌ Error ejecutando git: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════════════════════════" -ForegroundColor Yellow
Write-Host "PASO 3: Instalar dependencias de frontend (si es necesario)" -ForegroundColor Yellow
Write-Host "═══════════════════════════════════════════════════════════════════════════════" -ForegroundColor Yellow

Set-Location frontend

$nodeModulesPath = Join-Path $PWD "node_modules"

if (-not (Test-Path $nodeModulesPath)) {
    Write-Host "🔄 Instalando dependencias de npm..." -ForegroundColor Cyan
    npm install
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Dependencias instaladas" -ForegroundColor Green
    } else {
        Write-Host "❌ Error instalando dependencias" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "📦 Actualizando dependencias de npm..." -ForegroundColor Cyan
    npm ci  # Instancia limpia
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Dependencias actualizadas" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Advertencia actualizando dependencias" -ForegroundColor Yellow
    }
}

Set-Location ..

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host "✅ ACTUALIZACIÓN COMPLETADA" -ForegroundColor Green
Write-Host "═══════════════════════════════════════════════════════════════════════════════" -ForegroundColor Green

Write-Host ""
Write-Host "📊 SIGUIENTE PASO:" -ForegroundColor Yellow
Write-Host ""
Write-Host "  Para ejecutar el frontend:" -ForegroundColor White
Write-Host "  PS> cd frontend" -ForegroundColor Green
Write-Host "  PS> npm run dev" -ForegroundColor Green
Write-Host ""
Write-Host "  Luego abre en navegador:" -ForegroundColor White
Write-Host "  👉 http://localhost:3000" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Para conectar a servidor remoto, asegúrate que:" -ForegroundColor White
Write-Host "  - frontend\.env.local tiene: NEXT_PUBLIC_API_URL=http://IP-SERVIDOR:8000" -ForegroundColor Gray
Write-Host ""

Write-Host "═══════════════════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
Write-Host "📅 Lo que pasó esta noche en el servidor:" -ForegroundColor Yellow
Write-Host ""
Write-Host "  3:00 AM UTC:" -ForegroundColor White
Write-Host "  ✅ Entrenó 3 modelos (XGBoost, LightGBM, RandomForest)" -ForegroundColor Green
Write-Host "  ✅ Exportó modelos en .h5 + JSON" -ForegroundColor Green
Write-Host "  ✅ Subió a GitHub" -ForegroundColor Green
Write-Host "  ✅ Descargó y cargó modelos en memoria" -ForegroundColor Green
Write-Host ""
Write-Host "  Resultado: Datos frescos en \models_export\" -ForegroundColor Gray
Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
