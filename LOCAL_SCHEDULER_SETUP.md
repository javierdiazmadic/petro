# 🤖 Configuración del Scheduler Local (Sin GitHub Actions)

Como no tienes puertos abiertos, usaremos un scheduler que se ejecuta **completamente en tu servidor local** y sube los cambios a GitHub.

## 📋 Requisitos

```bash
pip install schedule
```

## 🚀 Instalación

### 1. Instalar Python schedule

```bash
pip install schedule
```

### 2. Linux/Mac - Configurar con CRON

Edita tu crontab:
```bash
crontab -e
```

Añade esta línea para ejecutar diariamente a las 3:00 AM UTC:
```bash
0 3 * * * /usr/bin/python3 scripts/local_daily_scheduler.py >> training_scheduler.log 2>&1
```

**Nota**: Reemplaza `/home/administrador/Desktop/petro` con tu ruta real.

### 3. Windows - Configurar con Task Scheduler

1. Abre **Task Scheduler** (Programador de tareas)
2. Clic derecho en "Task Scheduler Library"
3. Clic en "Create Basic Task"
4. Nombre: "PETRO Daily Training"
5. Trigger: Daily a las 3:00 AM
6. Action:
   - Program: `C:\Python3\python.exe` (tu ruta de Python)
   - Arguments: `C:\path\to\petro\scripts\local_daily_scheduler.py`
   - Start in: `C:\path\to\petro`

## 🎯 Uso

### Opción 1: Ejecutar manualmente (una sola vez)

```bash
cd /path/to/petro
python scripts/daily_training.py
python scripts/export_models.py
python scripts/generate_report.py
git add -A
git commit -m "Manual training run"
git push origin master
```

### Opción 2: Ejecutar scheduler en foreground (para testing)

```bash
cd /path/to/petro
python scripts/local_daily_scheduler.py
```

Presiona Ctrl+C para detener.

### Opción 3: Ejecutar scheduler en background (permanentemente)

Linux/Mac:
```bash
nohup python scripts/local_daily_scheduler.py > training_scheduler.log 2>&1 &
```

Windows PowerShell:
```powershell
Start-Process python -ArgumentList "scripts/local_daily_scheduler.py" -NoNewWindow
```

## 📊 Archivos Generados

Cada día (3:00 AM UTC) se generan y suben automáticamente:

```
✅ data/training/toledo_history.json
✅ data/training/spain_history.json
✅ data/forecasts/forecast_30days.json
✅ models_export/models_info.json
✅ models_export/training_metrics.json
✅ training_results/metrics.json
✅ training_report.md
✅ training_results/report_YYYY-MM-DD.md
```

## 📈 Logs

Los logs se guardan en `training_scheduler.log`:

```bash
# Ver últimas 50 líneas
tail -50 training_scheduler.log

# Monitorear en tiempo real
tail -f training_scheduler.log
```

## ✅ Verificar que funciona

1. **Verificar cron (Linux/Mac)**:
   ```bash
   crontab -l
   ```

2. **Verificar logs**:
   ```bash
   cat training_scheduler.log
   ```

3. **Verificar cambios en GitHub**:
   - Ve a https://github.com/javierdiazmadic/petro
   - Busca commits con "🤖 Auto: Daily training"

## 🔄 Flujo Completo

```
3:00 AM UTC (cada día)
    ↓
Scheduler local detecta la hora
    ↓
Ejecuta daily_training.py
    ├─ Genera datos Toledo + España
    ├─ Entrena 3 modelos ML
    └─ Genera predicciones 30 días
    ↓
Ejecuta export_models.py
    ├─ Exporta info modelos
    ├─ Exporta métricas
    └─ Exporta dataset info
    ↓
Ejecuta generate_report.py
    └─ Genera reporte Markdown
    ↓
Git commit automático
    └─ "🤖 Auto: Daily training & data update..."
    ↓
Git push a GitHub
    └─ Cambios subidos a master
    ↓
✅ COMPLETADO - Archivos disponibles en GitHub
```

## 🐛 Troubleshooting

### Cron no se ejecuta
```bash
# Verificar que cron está activo
sudo service cron status

# Reiniciar cron
sudo service cron restart

# Ver logs de cron
grep CRON /var/log/syslog
```

### Error de Git
```bash
# Verificar configuración Git
git config --global user.name
git config --global user.email

# Si faltan, configurar:
git config --global user.name "PETRO Bot"
git config --global user.email "petro@localhost"
```

### Error de Python
```bash
# Verificar que Python 3 está disponible
python3 --version

# Verificar que schedule está instalado
pip3 list | grep schedule
```

## 📞 Monitoring

Para monitorear el scheduler en una ventana separada:

```bash
# Terminal 1: Ejecutar scheduler
cd /path/to/petro
python scripts/local_daily_scheduler.py

# Terminal 2: Monitorear logs (en otra ventana)
tail -f training_scheduler.log
```

## ⏰ Próxima Ejecución

Mañana a las 3:00 AM UTC se ejecutará automáticamente y subirá los cambios a GitHub.

Verifica en: https://github.com/javierdiazmadic/petro/commits/master

