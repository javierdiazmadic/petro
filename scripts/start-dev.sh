#!/bin/bash

# PETRO - Quick Start Script for Development

set -e

echo "🚀 PETRO - Starting Development Environment"
echo "==========================================="
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check requirements
echo -e "${BLUE}📋 Checking requirements...${NC}"

if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed"
    exit 1
fi

echo -e "${GREEN}✓ Docker and Docker Compose found${NC}"
echo ""

# Build images
echo -e "${BLUE}🔨 Building Docker images...${NC}"
docker-compose build --no-cache 2>&1 | grep -E "(^Building|^Successfully)"

echo ""
echo -e "${BLUE}🚀 Starting services...${NC}"
docker-compose up -d

echo ""
echo -e "${YELLOW}⏳ Waiting for services to be healthy...${NC}"
sleep 10

# Check health
echo ""
echo -e "${BLUE}🏥 Health checks:${NC}"

API_HEALTH=$(curl -s http://localhost:8000/api/v1/health || echo "FAILED")
if [ "$API_HEALTH" != "FAILED" ]; then
    echo -e "${GREEN}✓ API${NC}: http://localhost:8000"
else
    echo -e "${YELLOW}⚠ API is starting... wait a few more seconds${NC}"
fi

if curl -s http://localhost:5000 > /dev/null 2>&1; then
    echo -e "${GREEN}✓ MLflow${NC}: http://localhost:5000"
fi

if curl -s http://localhost:9090/-/healthy > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Prometheus${NC}: http://localhost:9090"
fi

if curl -s http://localhost:3000/api/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Grafana${NC}: http://localhost:3000 (admin/admin)"
fi

if curl -s http://localhost:5601/api/status > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Kibana${NC}: http://localhost:5601"
fi

if curl -s http://localhost:9200/ > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Elasticsearch${NC}: http://localhost:9200"
fi

echo ""
echo -e "${GREEN}✅ Development environment is ready!${NC}"
echo ""
echo "📚 Next steps:"
echo "  1. View logs: make docker-logs"
echo "  2. Access API: http://localhost:8000/docs"
echo "  3. View Grafana: http://localhost:3000 (admin/admin)"
echo "  4. View MLflow: http://localhost:5000"
echo ""
echo "🛑 To stop: make docker-down"
