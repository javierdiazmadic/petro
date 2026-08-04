# 🚀 QUICKSTART - Cómo Ver el Dashboard de PETRO

## Opción 1: Docker (Recomendado - Más Fácil)

### Paso 1: Prerequisitos
```bash
# Instala Docker y Docker Compose
sudo apt-get install docker.io docker-compose

# Inicia Docker
sudo systemctl start docker
```

### Paso 2: Clonar y Configurar
```bash
# Clonar repositorio
git clone https://github.com/tu-usuario/petro.git
cd petro

# Crear archivo .env
cp .env.example .env

# Editar .env (opcional, defaults funcionan)
nano .env
```

### Paso 3: Iniciar Servicios
```bash
# Inicia todos los servicios
docker-compose up -d

# Espera 30 segundos para que inicie todo
sleep 30

# Verifica que todo está corriendo
docker-compose ps
```

**Deberías ver:**
```
CONTAINER ID   STATUS              NAMES
...            Up 25 seconds        petro-api
...            Up 28 seconds        petro-db
...            Up 26 seconds        petro-redis
...            Up 22 seconds        petro-celery-worker
...            Up 20 seconds        petro-celery-beat
```

### Paso 4: Acceder al Dashboard
```
🌐 Dashboard Web:  http://localhost:8000
📊 Predicciones:   http://localhost:8000/
📈 Métricas:       http://localhost:8000/metrics
🏥 Salud:          http://localhost:8000/health-dashboard
📝 API Docs:       http://localhost:8000/docs
🔴 RedOc:          http://localhost:8000/redoc
```

---

## Opción 2: Desarrollo Local (Más Control)

### Paso 1: Setup
```bash
# Crear virtual environment
python3.12 -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install -e ".[dev]"
```

### Paso 2: Iniciar Servicios Necesarios
```bash
# Terminal 1: Database + Redis (Docker)
docker-compose up -d db redis

# Terminal 2: FastAPI
make api-dev

# Terminal 3: Celery Worker
make celery-worker

# Terminal 4: Celery Beat
make celery-beat

# Terminal 5 (Opcional): Flower (monitoring)
celery -A petro.scheduler.app flower --port=5555
```

### Paso 3: Acceder
```
🌐 Dashboard:      http://localhost:8000
📝 API Docs:       http://localhost:8000/docs
🌼 Flower (Tasks): http://localhost:5555
```

---

## ¿Qué Puedes Ver en el Dashboard?

### 📊 Página Principal (`/`)
- **Precio Actual**: Último precio gasolina 95 (actualizado hace 5 min)
- **Predicciones**: 1 día, 3 días, 7 días
- **Gráficos**: 
  - Tendencia de precios (últimos 30 días)
  - Confianza de predicción (pie charts)
- **Tabla**: Comparación de predicciones multi-horizonte

### 📈 Métricas (`/metrics`)
- **Mejor Modelo**: Muestra cuál es (XGBoost, LightGBM, RF)
- **Comparación**: Tabla de RMSE, MAE, R², MAPE
- **Gráficos**: Barras comparando modelos

### 🏥 Salud (`/health-dashboard`)
- **Estado General**: Healthy / Degraded / Unhealthy
- **Componentes**: DB, Redis, Modelo ML
- **Pipeline Celery**: Estado de cada tarea (fetch, NLP, features, inference)
- **Uptime**: Gráfico de disponibilidad 24h

### 📚 Histórico (`/history`)
- **Predicciones Pasadas**: Últimas N predicciones
- **Errores**: MAE, RMSE, MAPE
- **Distribución**: Histograma de errores

---

## 🔄 Automatizar Recogida de Datos Cada Noche

### Opción A: Systemd (Recomendado en Linux)

#### 1. Crear script de actualización
```bash
sudo nano /usr/local/bin/petro-nightly.sh
```

Contenido:
```bash
#!/bin/bash
set -e

# Variables
PETRO_DIR="/home/administrador/Desktop/petro"
LOGFILE="/var/log/petro-nightly.log"

# Log
echo "[$(date)] Starting nightly PETRO pipeline..." >> $LOGFILE

# Cambiar directorio
cd $PETRO_DIR

# Ejecutar pipeline (trigger endpoint)
curl -X POST http://localhost:8000/scheduler/trigger-pipeline \
     -H "Authorization: Bearer $PETRO_API_TOKEN" \
     2>&1 >> $LOGFILE

# Ejecutar reentrenamiento (opcional, solo si es día específico)
if [ $(date +%A) = "Sunday" ]; then
    echo "[$(date)] Running weekly retraining..." >> $LOGFILE
    curl -X POST http://localhost:8000/scheduler/trigger-training \
         -H "Authorization: Bearer $PETRO_API_TOKEN" \
         2>&1 >> $LOGFILE
fi

echo "[$(date)] Nightly pipeline completed" >> $LOGFILE
```

#### 2. Dar permisos
```bash
sudo chmod +x /usr/local/bin/petro-nightly.sh
```

#### 3. Crear servicio systemd
```bash
sudo nano /etc/systemd/system/petro-nightly.service
```

Contenido:
```ini
[Unit]
Description=PETRO Nightly Data Collection
After=network.target

[Service]
Type=oneshot
User=administrador
ExecStart=/usr/local/bin/petro-nightly.sh
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

#### 4. Crear timer (scheduler)
```bash
sudo nano /etc/systemd/system/petro-nightly.timer
```

Contenido:
```ini
[Unit]
Description=PETRO Nightly Pipeline Timer
Requires=petro-nightly.service

[Timer]
# Ejecutar a las 2:00 AM (cuando menos tráfico)
OnCalendar=*-*-* 02:00:00
Persistent=true

[Install]
WantedBy=timers.target
```

#### 5. Habilitar y iniciar
```bash
# Recargar systemd
sudo systemctl daemon-reload

# Habilitar timer
sudo systemctl enable petro-nightly.timer

# Iniciar timer
sudo systemctl start petro-nightly.timer

# Verificar status
sudo systemctl status petro-nightly.timer
systemctl list-timers --all

# Ver logs
sudo journalctl -u petro-nightly.service -f
```

---

### Opción B: Cron Job (Más Simple)

#### 1. Editar crontab
```bash
crontab -e
```

#### 2. Agregar línea al final
```bash
# Ejecutar pipeline cada noche a las 2 AM
0 2 * * * /usr/local/bin/petro-nightly.sh

# Ejecutar reentrenamiento cada domingo a las 3 AM
0 3 * * 0 curl -X POST http://localhost:8000/scheduler/trigger-training
```

#### 3. Verificar cron está activo
```bash
sudo systemctl status cron
crontab -l  # Ver jobs programados
```

---

### Opción C: Docker (Si Usas Containers)

Celery Beat ya está **automatizado dentro de Docker**:

```bash
# Ver el container ejecutándose
docker-compose logs celery-beat

# El scheduler ya ejecuta cada 15 minutos automáticamente
# Daily retraining configurado para 2 AM UTC
```

No necesitas hacer nada más - **ya está funcionando automáticamente**.

---

## ✅ Verificar que Todo Funciona

### 1. Accede al Dashboard
```
http://localhost:8000
```

### 2. Revisa las Predicciones
- Deberías ver: Precio actual + predicciones para 1d, 3d, 7d
- Confianza de cada predicción
- Gráficos de tendencia

### 3. Verifica Pipeline Automático
```bash
# Ver logs de Celery
docker-compose logs -f celery-worker

# O en desarrollo
tail -f logs/celery.log
```

Deberías ver mensajes como:
```
[2026-08-04 02:00:00,000: INFO/MainProcess] Received task: petro.scheduler.tasks.fetch_all_data
[2026-08-04 02:00:28,123: INFO/MainProcess] Task completed successfully
```

### 4. Revisa Métricas
```bash
# Ver métricas Prometheus
curl http://localhost:8000/metrics/prometheus

# Ver health check
curl http://localhost:8000/api/v1/health | jq
```

---

## 🐛 Troubleshooting

### Dashboard no carga
```bash
# Verificar que API está corriendo
curl http://localhost:8000/api/v1/health

# Ver logs del API
docker-compose logs -f api
# o
tail -f logs/api.log
```

### Predicciones vacías
```bash
# Verificar que Celery completó pipeline
docker-compose logs celery-beat

# Verificar base de datos
docker-compose logs db
```

### Datos no se actualizan
```bash
# Ver cron logs
sudo journalctl -u petro-nightly.service

# O manualmente disparar pipeline
curl -X POST http://localhost:8000/scheduler/trigger-pipeline
```

---

## 📊 Datos de Ejemplo

El sistema viene con:
- ✅ Datos simulados (Brent, WTI, EUR/USD)
- ✅ Noticias RSS de muestra
- ✅ Modelos pre-entrenados
- ✅ Predicciones iniciales

Después de 24 horas verás:
- 📈 Gráficos con datos históricos
- 📊 Metrics de precisión
- 🏥 Health checks real
- 🔄 Pipeline ejecutándose automáticamente

---

## 🚀 Próximos Pasos

1. **Conectar datos reales**:
   - Reemplazar simuladores con APIs reales (Geoportal, etc.)
   - Configurar RSS feeds de noticias reales

2. **Personalizar predicciones**:
   - Ajustar thresholds de confianza
   - Entrenar con tus datos específicos

3. **Deployment a producción**:
   - Usar Cloud GCP (ver `infra/cloud/main.tf`)
   - O desplegar en tu servidor

---

**¡Tu dashboard está listo! Accede a http://localhost:8000 y ve cómo funciona la predicción de precios de gasolina en tiempo real.**
