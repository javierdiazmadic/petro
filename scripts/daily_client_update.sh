#!/bin/bash

# ═══════════════════════════════════════════════════════════════════════════════
# PETRO - Daily Client Update Script (Linux/macOS)
#
# Ejecutar cada mañana para descargar datos actualizados del servidor
# Uso: bash scripts/daily_client_update.sh
# ═══════════════════════════════════════════════════════════════════════════════

set -e

echo "╔═══════════════════════════════════════════════════════════════════════════╗"
echo "║                                                                           ║"
echo "║  🔄 PETRO - Actualización diaria de datos (Cliente)                      ║"
echo "║                                                                           ║"
echo "║  Este script descarga los modelos y datos del servidor central            ║"
echo "║  que fueron entrenados durante la noche                                   ║"
echo "║                                                                           ║"
echo "╚═══════════════════════════════════════════════════════════════════════════╝"

echo ""
echo "═══════════════════════════════════════════════════════════════════════════════"
echo "PASO 1: Obtener ruta del proyecto"
echo "═══════════════════════════════════════════════════════════════════════════════"

# Determinar ruta base (donde está este script)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
echo "📁 Directorio del proyecto: $SCRIPT_DIR"
cd "$SCRIPT_DIR"

echo ""
echo "═══════════════════════════════════════════════════════════════════════════════"
echo "PASO 2: Actualizar desde GitHub"
echo "═══════════════════════════════════════════════════════════════════════════════"

echo "🔄 Haciendo git pull origin master..."

if git pull origin master; then
    echo "✅ Proyecto actualizado desde GitHub"
else
    echo "⚠️  Error en git pull. Verifica tu conexión a GitHub"
    exit 1
fi

echo ""
echo "═══════════════════════════════════════════════════════════════════════════════"
echo "PASO 3: Instalar dependencias de frontend (si es necesario)"
echo "═══════════════════════════════════════════════════════════════════════════════"

cd frontend

if [ ! -d "node_modules" ]; then
    echo "🔄 Instalando dependencias de npm..."
    npm install
    echo "✅ Dependencias instaladas"
else
    echo "📦 Actualizando dependencias de npm..."
    npm ci  # Instancia limpia
    echo "✅ Dependencias actualizadas"
fi

cd ..

echo ""
echo "═══════════════════════════════════════════════════════════════════════════════"
echo "✅ ACTUALIZACIÓN COMPLETADA"
echo "═══════════════════════════════════════════════════════════════════════════════"

echo ""
echo "📊 SIGUIENTE PASO:"
echo ""
echo "  Para ejecutar el frontend:"
echo "  $ cd frontend"
echo "  $ npm run dev"
echo ""
echo "  Luego abre en navegador:"
echo "  👉 http://localhost:3000"
echo ""
echo "  Para conectar a servidor remoto, asegúrate que:"
echo "  - frontend/.env.local tiene: NEXT_PUBLIC_API_URL=http://IP-SERVIDOR:8000"
echo ""

echo "═══════════════════════════════════════════════════════════════════════════════"
echo ""
echo "📅 Lo que pasó esta noche en el servidor:"
echo ""
echo "  3:00 AM UTC:"
echo "  ✅ Entrenó 3 modelos (XGBoost, LightGBM, RandomForest)"
echo "  ✅ Exportó modelos en .h5 + JSON"
echo "  ✅ Subió a GitHub"
echo "  ✅ Descargó y cargó modelos en memoria"
echo ""
echo "  Resultado: Datos frescos en /models_export/"
echo ""
echo "═══════════════════════════════════════════════════════════════════════════════"
