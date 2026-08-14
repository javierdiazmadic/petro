#!/bin/bash

# ═══════════════════════════════════════════════════════════════════════════════
# PETRO - INSTALLATION SCRIPT
# Instalación completa en tu servidor local
# ═══════════════════════════════════════════════════════════════════════════════

set -e

echo "╔═══════════════════════════════════════════════════════════════════════════╗"
echo "║                                                                           ║"
echo "║  🚀 PETRO - INSTALACIÓN COMPLETA                                         ║"
echo "║                                                                           ║"
echo "║  ✅ TODO se ejecuta en TU servidor (sin equipos externos)                ║"
echo "║  ✅ Entrenamiento local                                                   ║"
echo "║  ✅ Modelos guardados localmente                                          ║"
echo "║  ✅ Dashboard en tiempo real                                              ║"
echo "║                                                                           ║"
echo "╚═══════════════════════════════════════════════════════════════════════════╝"

echo ""
echo "═══════════════════════════════════════════════════════════════════════════════"
echo "PASO 1: Verificar requisitos"
echo "═══════════════════════════════════════════════════════════════════════════════"

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 no está instalado"
    echo "   Ubuntu: sudo apt-get install python3"
    echo "   macOS: brew install python3"
    echo "   Windows: https://www.python.org/downloads/"
    exit 1
fi
echo "✅ Python 3 encontrado: $(python3 --version)"

# Verificar Docker
if ! command -v docker &> /dev/null; then
    echo "⚠️  Docker no está instalado (opcional pero recomendado)"
    echo "   https://www.docker.com/products/docker-desktop"
else
    echo "✅ Docker encontrado: $(docker --version)"
fi

# Verificar Git
if ! command -v git &> /dev/null; then
    echo "❌ Git no está instalado"
    echo "   Ubuntu: sudo apt-get install git"
    echo "   macOS: brew install git"
    echo "   Windows: https://git-scm.com/"
    exit 1
fi
echo "✅ Git encontrado: $(git --version)"

echo ""
echo "═══════════════════════════════════════════════════════════════════════════════"
echo "PASO 2: Descargar código desde GitHub"
echo "═══════════════════════════════════════════════════════════════════════════════"

echo "🔄 Clonando repositorio..."
if [ ! -d "petro" ]; then
    git clone https://github.com/javierdiazmadic/petro.git
    cd petro
else
    echo "📁 Directorio 'petro' ya existe"
    cd petro
    git pull origin master
fi

echo "✅ Código descargado"

echo ""
echo "═══════════════════════════════════════════════════════════════════════════════"
echo "PASO 3: Instalar dependencias Python"
echo "═══════════════════════════════════════════════════════════════════════════════"

echo "🔄 Creando virtual environment..."
python3 -m venv venv

echo "🔄 Activando virtual environment..."
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
    # Windows
    source venv/Scripts/activate
else
    # Linux/macOS
    source venv/bin/activate
fi

echo "🔄 Instalando dependencias..."
pip install --upgrade pip
pip install -e ".[dev]"

echo "✅ Dependencias instaladas"

echo ""
echo "═══════════════════════════════════════════════════════════════════════════════"
echo "PASO 4: Instalar frontend"
echo "═══════════════════════════════════════════════════════════════════════════════"

if command -v node &> /dev/null; then
    echo "✅ Node.js encontrado: $(node --version)"
    cd frontend
    npm install
    cd ..
    echo "✅ Frontend dependencies instaladas"
else
    echo "⚠️  Node.js no encontrado"
    echo "   Para usar el frontend, instalar Node.js:"
    echo "   https://nodejs.org/"
fi

echo ""
echo "═══════════════════════════════════════════════════════════════════════════════"
echo "PASO 5: Opción A - DOCKER (RECOMENDADO)"
echo "═══════════════════════════════════════════════════════════════════════════════"

if command -v docker &> /dev/null; then
    echo ""
    echo "🐳 Con Docker Compose (TODO automático):"
    echo ""
    echo "  1. Asegúrate que Docker está corriendo"
    echo "  2. Ejecuta:"
    echo "     $ docker compose up -d"
    echo ""
    echo "  3. Espera 30 segundos para que todo inicie"
    echo ""
    echo "  4. Abre en navegador:"
    echo "     👉 http://localhost:3000"
    echo ""
    echo "  5. Dashboard estará COMPLETAMENTE FUNCIONAL:"
    echo "     ✅ Gráficos de precios"
    echo "     ✅ Mapa interactivo"
    echo "     ✅ Noticias"
    echo "     ✅ Predicciones"
    echo "     ✅ Información de modelos"
    echo ""
    echo "  ⏰ Cada noche a las 3:00 AM UTC:"
    echo "     └─ Entrena automáticamente"
    echo "     └─ Descarga y carga modelos"
    echo "     └─ Todo actualizado mañana"
    echo ""
else
    echo "❌ Docker no está disponible en PASO 5"
fi

echo ""
echo "═══════════════════════════════════════════════════════════════════════════════"
echo "PASO 5: Opción B - LOCAL (Python puro)"
echo "═══════════════════════════════════════════════════════════════════════════════"

echo ""
echo "🐍 Sin Docker (más manual pero funciona):"
echo ""
echo "  1. Asegúrate que virtual env está activado:"
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
    echo "     $ source venv/Scripts/activate  # Windows"
else
    echo "     $ source venv/bin/activate      # Linux/macOS"
fi
echo ""
echo "  2. Inicia PostgreSQL local (si lo tienes)"
echo "     $ sudo systemctl start postgresql"
echo ""
echo "  3. Inicia Redis local (si lo tienes)"
echo "     $ redis-server"
echo ""
echo "  4. Ejecuta el scheduler:"
echo "     $ python scripts/local_daily_scheduler.py"
echo ""
echo "  5. En OTRA terminal, inicia la API:"
echo "     $ python -m uvicorn src.petro.api.main:app --reload --port 8000"
echo ""
echo "  6. En OTRA terminal, ve al frontend:"
echo "     $ cd frontend && npm run dev"
echo ""
echo "  7. Abre en navegador:"
echo "     👉 http://localhost:3000"
echo ""

echo ""
echo "═══════════════════════════════════════════════════════════════════════════════"
echo "⏰ ENTRENAMIENTO AUTOMÁTICO"
echo "═══════════════════════════════════════════════════════════════════════════════"

echo ""
echo "📅 3:00 AM UTC cada noche:"
echo ""
echo "   1. ⚙️  Entrena 3 modelos (tu GPU lo hace)"
echo "      └─ XGBoost, LightGBM, RandomForest"
echo "      └─ Usa últimos 90 días de datos"
echo ""
echo "   2. 💾 Exporta .h5 + JSON metadata"
echo "      └─ Archivos en: models_export/"
echo ""
echo "   3. 📤 Sube a GitHub"
echo "      └─ https://github.com/javierdiazmadic/petro"
echo ""
echo "   4. ↻ Automáticamente descarga y carga"
echo "      └─ ModelsRegistry en memoria"
echo ""
echo "   5. ✅ Dashboard obtiene datos frescos"
echo ""
echo "🎯 RESULTADO: Mañana a las 4:00 AM (España)"
echo "   └─ Abre http://localhost:3000"
echo "   └─ TODO está actualizado sin hacer nada"
echo ""

echo ""
echo "═══════════════════════════════════════════════════════════════════════════════"
echo "🧪 VER EN TIEMPO REAL (Opcional)"
echo "═══════════════════════════════════════════════════════════════════════════════"

echo ""
echo "Para VER el entrenamiento AHORA (sin esperar a las 3 AM):"
echo ""
echo "  # Ejecutar manualmente el script de entrenamiento"
echo "  $ python scripts/daily_training.py"
echo ""
echo "  # O ejecutar el pipeline completo"
echo "  $ python scripts/daily_training.py && \\"
echo "    python scripts/export_models_h5.py && \\"
echo "    python scripts/download_and_load_models.py"
echo ""
echo "  # O ir a 3:00 AM UTC y ver los logs"
echo "  $ tail -f training_scheduler.log"
echo ""

echo ""
echo "═══════════════════════════════════════════════════════════════════════════════"
echo "📊 LO QUE VERÁS EN EL DASHBOARD"
echo "═══════════════════════════════════════════════════════════════════════════════"

echo ""
echo "  📈 Gráficos de precios (90 días)"
echo "     └─ Toledo + España"
echo "     └─ Actualizados diariamente"
echo ""
echo "  🗺️ Mapa interactivo"
echo "     └─ 227 gasolineras de Toledo"
echo "     └─ Con precios frescos"
echo "     └─ Clickeable"
echo ""
echo "  📰 Noticias del mercado"
echo "     └─ OPEC, subvenciones, etc"
echo "     └─ Análisis de impacto"
echo ""
echo "  🤖 Información de modelos"
echo "     └─ Mejor modelo destacado"
echo "     └─ Métricas: R², RMSE, MAE"
echo "     └─ Botón refresh manual"
echo ""
echo "  🔮 Predicciones 30 días"
echo "     └─ Basadas en modelos ML"
echo "     └─ Con análisis de impacto"
echo ""

echo ""
echo "═══════════════════════════════════════════════════════════════════════════════"
echo "🎯 IMPORTANTE - ACLARACIÓN"
echo "═══════════════════════════════════════════════════════════════════════════════"

echo ""
echo "✅ TODO se ejecuta en TU SERVIDOR"
echo ""
echo "  • Entrenamiento: SE EJECUTA EN TU GPU/CPU"
echo "  • Modelos: SE GUARDAN EN TU MÁQUINA"
echo "  • GitHub: Solo se usa para SINCRONIZACIÓN"
echo "  • Dashboard: SE SIRVE DESDE TU SERVIDOR"
echo ""
echo "  NO NECESITAS equipos externos"
echo "  NO NECESITAS cloud computing"
echo "  TODO es LOCAL"
echo ""

echo ""
echo "═══════════════════════════════════════════════════════════════════════════════"
echo "✅ INSTALACIÓN LISTA"
echo "═══════════════════════════════════════════════════════════════════════════════"

echo ""
echo "Próximos pasos:"
echo ""
if command -v docker &> /dev/null; then
    echo "  $ docker compose up -d"
    echo "  $ open http://localhost:3000"
else
    echo "  $ source venv/bin/activate"
    echo "  $ python scripts/local_daily_scheduler.py"
fi
echo ""
echo "═══════════════════════════════════════════════════════════════════════════════"
echo ""
