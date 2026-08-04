#!/bin/bash
# PETRO - Instalador y Lanzador Automático
# Ejecuta TODO en un comando

set -euo pipefail

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ===== Helper Functions =====

print_header() {
    echo -e "${BLUE}════════════════════════════════════════${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}════════════════════════════════════════${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ $1${NC}"
}

print_step() {
    echo -e "${BLUE}→ $1${NC}"
}

# ===== Main Script =====

main() {
    print_header "PETRO - Instalador Automático v1.0.0"

    # Check prerequisites
    print_step "Verificando prerequisitos..."
    check_docker
    check_docker_compose

    # Setup project
    print_step "Configurando proyecto..."
    setup_project

    # Start services
    print_step "Iniciando servicios..."
    start_services

    # Wait for services
    print_step "Esperando a que los servicios estén listos..."
    wait_for_services

    # Print summary
    print_summary
}

check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker no está instalado"
        echo "Instala Docker desde: https://docs.docker.com/install"
        exit 1
    fi
    print_success "Docker está instalado"
}

check_docker_compose() {
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose no está instalado"
        echo "Instala Docker Compose desde: https://docs.docker.com/compose/install"
        exit 1
    fi
    print_success "Docker Compose está instalado"
}

setup_project() {
    # Check if in project directory
    if [ ! -f "docker-compose.yml" ]; then
        print_error "No se encuentra docker-compose.yml"
        print_info "Asegúrate de estar en el directorio raíz de petro"
        exit 1
    fi

    # Create .env if doesn't exist
    if [ ! -f ".env" ]; then
        print_step "Creando archivo .env..."
        cp .env.example .env
        print_success ".env creado"
    else
        print_info ".env ya existe"
    fi

    # Create logs directory
    mkdir -p logs
    print_success "Directorio de logs listo"
}

start_services() {
    print_step "Iniciando containers..."
    docker-compose up -d
    print_success "Containers iniciados"
}

wait_for_services() {
    print_step "Esperando que API esté lista..."

    local max_attempts=30
    local attempt=0
    local api_url="http://localhost:8000/api/v1/health"

    while [ $attempt -lt $max_attempts ]; do
        if curl -s -f "$api_url" > /dev/null 2>&1; then
            print_success "API está lista!"
            return 0
        fi

        echo -n "."
        sleep 1
        ((attempt++))
    done

    print_error "Timeout esperando API"
    print_info "Los containers pueden estar iniciándose. Intenta abrir http://localhost:8000 en 30 segundos"
    return 1
}

print_summary() {
    echo ""
    print_header "🎉 ¡PETRO ESTÁ LISTO!"
    echo ""
    echo -e "${GREEN}═══════════════════════════════════════${NC}"
    echo -e "${GREEN}Dashboard Web${NC}"
    echo -e "${GREEN}═══════════════════════════════════════${NC}"
    echo ""
    echo -e "  🌐 http://localhost:8000"
    echo -e "     → Predicciones de gasolina en vivo"
    echo ""
    echo -e "${GREEN}═══════════════════════════════════════${NC}"
    echo -e "${GREEN}Otros Endpoints${NC}"
    echo -e "${GREEN}═══════════════════════════════════════${NC}"
    echo ""
    echo -e "  📊 Métricas:      http://localhost:8000/metrics"
    echo -e "  🏥 Salud:         http://localhost:8000/health-dashboard"
    echo -e "  📚 Histórico:     http://localhost:8000/history"
    echo -e "  📝 API Docs:      http://localhost:8000/docs"
    echo -e "  🔴 ReDoc:        http://localhost:8000/redoc"
    echo ""
    echo -e "${GREEN}═══════════════════════════════════════${NC}"
    echo -e "${GREEN}Comandos Útiles${NC}"
    echo -e "${GREEN}═══════════════════════════════════════${NC}"
    echo ""
    echo -e "  Ver logs:         ${YELLOW}docker-compose logs -f${NC}"
    echo -e "  Ver logs API:     ${YELLOW}docker-compose logs -f api${NC}"
    echo -e "  Ver logs Celery:  ${YELLOW}docker-compose logs -f celery-beat${NC}"
    echo -e "  Detener:          ${YELLOW}docker-compose down${NC}"
    echo -e "  Reiniciar:        ${YELLOW}docker-compose restart${NC}"
    echo ""
    echo -e "${GREEN}═══════════════════════════════════════${NC}"
    echo -e "${BLUE}Automación${NC}"
    echo -e "${GREEN}═══════════════════════════════════════${NC}"
    echo ""
    echo -e "  ✅ Recolección cada 15 minutos"
    echo -e "  ✅ Predicciones automáticas"
    echo -e "  ✅ Reentrenamiento cada domingo"
    echo ""
    echo -e "${GREEN}═══════════════════════════════════════${NC}"
    echo ""
    echo -e "${BLUE}Abre tu navegador en:${NC} ${YELLOW}http://localhost:8000${NC}"
    echo ""
    echo -e "${GREEN}¡LISTO! Dashboard funcionando 🚀${NC}"
    echo ""
}

# ===== Execution =====

main "$@"
