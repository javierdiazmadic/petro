# 🚀 PETRO - Configuración del Servidor Local

Bienvenido. Este documento es tu **GUÍA COMPLETA** para ejecutar PETRO en tu servidor local (125GB RAM, 42GB VRAM, GPU potente).

---

## 📋 REQUISITOS PREVIOS

✅ **Sistema**: Linux con 125GB RAM y GPU  
✅ **Python**: 3.12+  
✅ **Git**: Configurado con credenciales GitHub  
✅ **Docker**: Docker Desktop o Docker Engine  
✅ **Docker Compose**: V2+  

---

## 🎯 OPCIÓN 1: EJECUCIÓN RÁPIDA (TODO EN DOCKER - RECOMENDADO)

### Paso 1: Levantar Docker Compose

```bash
cd /home/administrador/Desktop/petro
docker compose up -d
```

**Esto inicia 12 servicios:**
- ✅ PostgreSQL 16 + TimescaleDB
- ✅ Redis (cache)
- ✅ FastAPI (API)
- ✅ Celery Beat (scheduler 3 AM UTC)
- ✅ Celery Worker (ejecutor)
- ✅ Next.js Frontend
- ✅ MLflow (tracking)
- ✅ Y más...

### Paso 2: Verificar que todo está UP

```bash
docker compose ps

# Debe mostrar 12 servicios con status "Up"
```

### Paso 3: Acceder al Dashboard

Abre en el navegador:
```
http://localhost:3000
```

✅ Verás:
- 📊 Gráficos de precios (Toledo + España, 90 días)
- 🗺️ Mapa interactivo de gasolineras
- 📰 Noticias del mercado
- 🤖 Predicciones 30 días
- 💡 Recomendaciones

### Paso 4: La automatización está LISTA

El scheduler **ya está configurado** en Docker Compose:
- ⏰ Se ejecuta automáticamente a las **3:00 AM UTC** cada día
- 🔄 Reentrenamiento automático de modelos
- 📤 Actualiza todo a GitHub automáticamente

**¡NADA QUE HACER - TODO ES AUTOMÁTICO!**

---

## 🎯 OPCIÓN 2: EJECUCIÓN LOCAL (Python puro - SIN Docker)

### Paso 1: Crear Virtual Environment

```bash
cd /home/administrador/Desktop/petro
python3.12 -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

### Paso 2: Instalar dependencias

```bash
pip install --upgrade pip
pip install -e ".[dev]"
# Esto instala todo, incluyendo 'schedule'
```

### Paso 3: Configurar base de datos (PostgreSQL local)

```bash
# Si no tienes PostgreSQL, instálalo:
# Ubuntu/Debian:
sudo apt-get install postgresql postgresql-contrib

# Crear base de datos PETRO
sudo sudo -u postgres psql << EOF
CREATE USER petro WITH PASSWORD 'petro_password';
CREATE DATABASE petro_dev OWNER petro;
GRANT ALL PRIVILEGES ON DATABASE petro_dev TO petro;
EOF
```

### Paso 4: Configurar Redis local

```bash
# Ubuntu/Debian:
sudo apt-get install redis-server

# Iniciar Redis:
sudo systemctl start redis-server
```

### Paso 5: Ejecutar la automatización LOCAL

```bash
cd /home/administrador/Desktop/petro

# Opción A: Ejecutar scheduler en foreground (para testing)
python scripts/local_daily_scheduler.py

# Opción B: Ejecutar scheduler en background (permanente)
nohup python scripts/local_daily_scheduler.py > training_scheduler.log 2>&1 &

# Opción C: Configurar con CRON (se ejecuta cada día a las 3 AM)
crontab -e
# Agregar esta línea:
# 0 3 * * * /path/to/venv/bin/python /home/administrador/Desktop/petro/scripts/local_daily_scheduler.py >> /home/administrador/Desktop/petro/training_scheduler.log 2>&1
```

### Paso 6: Monitorear logs

```bash
# Ver últimas 50 líneas en tiempo real
tail -f training_scheduler.log

# O ver solo eventos importantes
grep -i "error\|success\|completed" training_scheduler.log
```

---

## ✅ VERIFICAR QUE FUNCIONA

### 1. Verificar que Docker está UP (si usas Docker)

```bash
# Ver logs del scheduler de Celery Beat
docker compose logs petro-beat --tail 20

# Debe mostrar algo como:
# petro-beat  | beat: Starting Beat v5.3.0
# petro-beat  | beat: Scheduler: celery.beat.PersistentScheduler
```

### 2. Verificar que API está respondiendo

```bash
curl http://localhost:8000/api/v1/dashboard/stats | jq .

# Respuesta esperada:
# {
#   "timestamp": "2026-08-14T...",
#   "total_stations": 227,
#   "last_price_update": "2026-08-14T..."
# }
```

### 3. Verificar que Frontend está UP

```bash
# En el navegador:
http://localhost:3000

# Debe cargar el dashboard con gráficos y mapa
```

### 4. Verificar datos frescos

```bash
# Verificar que los gráficos tienen datos de HOY
curl "http://localhost:8000/api/v1/dashboard/prices/history?days=3&province=toledo" | jq '.period.end_date'

# Debe devolver fecha de hoy (2026-08-14 o posterior)
```

---

## 📊 LO QUE VAS A VER CADA DÍA

### Automáticamente a las 3:00 AM UTC:

1. **📊 Gráficos actualizados**
   - Últimos 90 días de Toledo
   - Últimos 90 días de España
   - Con datos de HOY

2. **🗺️ Mapa actualizado**
   - 227 gasolineras con precios frescos
   - Coordenadas exactas
   - Clickeables

3. **📰 Noticias del mercado**
   - 8+ noticias recientes
   - Análisis de impacto
   - Clasificadas por categoría

4. **🤖 Modelos reentrenados**
   - 3 modelos ML nuevos (XGBoost, LightGBM, RandomForest)
   - 30 días de predicciones
   - Guardado en GitHub

5. **📤 GitHub actualizado**
   - Nuevo commit: "🤖 Auto: Daily training & data update..."
   - Archivos JSON exportados
   - Reporte Markdown

---

## 🔧 COMANDOS ÚTILES

### Docker Compose

```bash
# Ver status de todos los servicios
docker compose ps

# Ver logs de un servicio específico
docker compose logs petro-api --tail 50
docker compose logs petro-worker --tail 50

# Reiniciar todo
docker compose restart

# Detener todo
docker compose down

# Levantar de nuevo
docker compose up -d
```

### Git / GitHub

```bash
# Ver últimos commits con timestamps
git log --oneline --decorate | head -20

# Ver commits automáticos del scheduler
git log --oneline | grep "Auto: Daily"

# Ver cambios no commiteados
git status

# Ver diferencia de archivos
git diff
```

### Base de datos

```bash
# Conectarse a PostgreSQL (si estás en Docker)
docker compose exec db psql -U petro -d petro_dev

# Ver últimos 5 precios
SELECT * FROM price ORDER BY timestamp DESC LIMIT 5;

# Ver gasolineras de Toledo
SELECT * FROM gas_station WHERE province = 'toledo' LIMIT 10;

# Salir
\q
```

---

## 🐛 TROUBLESHOOTING

### Problema: Docker no inicia
```bash
# Verificar que Docker está corriendo
docker ps

# Si no, iniciar Docker
systemctl start docker

# Ver logs del error
docker compose logs
```

### Problema: API retorna 500
```bash
# Verificar logs de FastAPI
docker compose logs petro-api --tail 50

# Reiniciar API
docker compose restart petro-api
```

### Problema: Base de datos vacía
```bash
# Reiniciar con datos limpios
docker compose down -v
docker compose up -d

# Esperar 30 segundos para que se inicialice
sleep 30

# Verificar logs de inicialización
docker compose logs petro-db | grep "CREATE TABLE"
```

### Problema: Scheduler no se ejecuta
```bash
# Verificar logs de beat
docker compose logs petro-beat | tail -50

# Si no está ejecutándose, reiniciar beat
docker compose restart petro-beat

# O ver logs de worker
docker compose logs petro-worker | tail -50
```

---

## 📞 SOPORTE RÁPIDO

| Problema | Solución |
|----------|----------|
| **¿Cómo verifico que el scheduler se ejecutó?** | Ver logs: `tail -50 training_scheduler.log` o `docker compose logs petro-beat` |
| **¿Dónde están los datos generados?** | En GitHub: `https://github.com/javierdiazmadic/petro/tree/master/data` |
| **¿Cómo fuerzo una ejecución manual?** | `python scripts/daily_training.py` |
| **¿Cuánto tarda cada ciclo?** | 5-10 minutos (7 etapas) |
| **¿Qué hora se ejecuta?** | 3:00 AM UTC (4:00 AM España) |
| **¿Dónde puedo ver las predicciones?** | En el dashboard: `http://localhost:3000` → "Predicciones" |

---

## 🎯 PRÓXIMOS PASOS

### HOY:
1. ✅ Docker Compose levantado
2. ✅ Dashboard abierto en navegador
3. ✅ Verificar que todo carga correctamente

### MAÑANA (3:00 AM UTC):
1. ✅ Scheduler se ejecuta automáticamente
2. ✅ Nuevos datos en GitHub
3. ✅ Modelos reentrenados
4. ✅ Dashboard con datos frescos

### MANTENIMIENTO:
- ✅ Revisar logs cada mañana: `tail -10 training_scheduler.log`
- ✅ Monitorear recursos: `docker stats`
- ✅ Backup semanal de BD: `docker compose exec db pg_dump -U petro petro_dev > backup.sql`

---

## 🎉 ¡LISTO!

Tu sistema PETRO está **100% automatizado** y funcionando.

Mañana a las 3:00 AM UTC se ejecutará automáticamente y subirá los cambios a GitHub.

No requiere intervención manual - todo es automático.

**Verifica los cambios en:** https://github.com/javierdiazmadic/petro/commits/master

---

*Última actualización: 2026-08-14*  
*Hecho por: Claude Code*
