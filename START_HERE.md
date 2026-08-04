# 🚀 PETRO - COMIENZA AQUÍ

## ⚡ OPCIÓN MÁS RÁPIDA (2 minutos)

### 1️⃣ Abre Terminal y Copia Esto:

```bash
cd /home/administrador/Desktop/petro
docker-compose up -d
sleep 30
```

### 2️⃣ Abre tu Navegador:

```
http://localhost:8000
```

**¡LISTO! 🎉 Verás el dashboard funcionando con predicciones de gasolina en VIVO**

---

## 📊 QUÉ VAS A VER

### Página Principal
![Dashboard Preview]
- 💰 **Precio actual** gasolina 95
- 📈 **Predicciones**: 1 día, 3 días, 7 días  
- 📊 **Confianza** de cada predicción (%)
- 📉 **Gráficos** automáticos
- 📈 **Historiales** de precisión

### Otros Links
- 📈 Métricas: http://localhost:8000/metrics
- 🏥 Salud: http://localhost:8000/health-dashboard
- 📚 Histórico: http://localhost:8000/history
- 📝 API Docs: http://localhost:8000/docs

---

## 🔄 AUTOMATIZACIÓN (Recogida de Datos Cada Noche)

### YA ESTÁ INCLUIDO EN DOCKER

El sistema **automáticamente**:
- ✅ Recolecta datos cada 15 minutos
- ✅ Procesa noticias
- ✅ Genera predicciones
- ✅ Reentrenamiento cada domingo a 2 AM

**No necesitas hacer nada más.**

### Ver Que Está Funcionando

```bash
# Ver logs de automación
docker-compose logs -f celery-beat

# Deberías ver algo como:
# [2026-08-04 02:00:00] fetch_all_data started
# [2026-08-04 02:00:30] process_news completed
# [2026-08-04 02:01:00] calculate_features completed
```

---

## 📤 SUBIR A GITHUB (Opcional)

### Si Tienes Token de GitHub:

```bash
# 1. Configura tu usuario
git config --global user.email "tu@email.com"
git config --global user.name "Tu Nombre"

# 2. Crea repo en https://github.com/new
#    (llamalo "petro")

# 3. Sube el código
cd /home/administrador/Desktop/petro
git remote add origin https://github.com/TU_USUARIO/petro.git
git branch -M main
git push -u origin main
```

**Tu proyecto estará en:** https://github.com/TU_USUARIO/petro

### Si NO Tienes Token:

El código ya está guardado localmente. Puedes subirlo manualmente después desde GitHub.

---

## 🛠️ COMANDOS ÚTILES

### Ver Dashboard
```bash
open http://localhost:8000
# O simplemente: http://localhost:8000
```

### Ver Logs en Tiempo Real
```bash
# Logs del API
docker-compose logs -f api

# Logs de Celery (predicciones automáticas)
docker-compose logs -f celery-worker

# Logs de scheduler (cada 15 min)
docker-compose logs -f celery-beat

# Logs de BD
docker-compose logs -f db
```

### Detener Todo
```bash
docker-compose down
```

### Reiniciar
```bash
docker-compose restart
```

---

## 📱 ACCEDER DESDE OTRA COMPUTADORA

Si quieres ver el dashboard desde otro PC:

```bash
# Usa la IP de tu servidor actual
http://TU_IP_SERVIDOR:8000

# Para saber tu IP:
hostname -I
```

---

## 🎯 ESTRUCTURA DEL PROYECTO

```
petro/
├── docker-compose.yml          ← Inicia TODO
├── src/petro/
│   ├── api/                    ← Dashboard web
│   ├── ml/                     ← Modelos ML
│   ├── scheduler/              ← Automatización
│   ├── features/               ← Cálculo de variables
│   └── ...
├── docs/                       ← Documentación por phase
├── tests/                      ← 70+ tests
├── QUICKSTART.md               ← Guía detallada
├── PROJECT_COMPLETION.md       ← Resumen del proyecto
└── START_HERE.md               ← TÚ ESTÁS AQUÍ
```

---

## 🔍 VERIFICAR QUE TODO FUNCIONA

```bash
# 1. Chequea que containers estén corriendo
docker-compose ps

# Deberías ver (status: Up):
# - petro-api
# - petro-db
# - petro-redis
# - petro-celery-worker
# - petro-celery-beat

# 2. Chequea API
curl http://localhost:8000/api/v1/health | jq

# Deberías ver:
# {
#   "status": "healthy",
#   "database": "connected",
#   "redis": "connected",
#   "model_loaded": true,
#   "version": "1.0.0"
# }

# 3. Abre dashboard
open http://localhost:8000
```

---

## ❌ SI ALGO NO FUNCIONA

### "Puerto 8000 ya está en uso"
```bash
docker-compose down
docker-compose up -d
```

### "Conexión rechazada"
```bash
# Espera 30 segundos más
sleep 30
curl http://localhost:8000/api/v1/health
```

### "Base de datos vacía"
```bash
# Primera vez puede tardar en cargar datos
# Espera 2-3 minutos y recarga el navegador
sleep 120
open http://localhost:8000
```

### Ver todos los logs
```bash
docker-compose logs | tail -100
```

---

## 📞 SOPORTE

Todos los archivos están documentados:

- **QUICKSTART.md** — Guía completa (Docker + Local)
- **GITHUB_SETUP.md** — Cómo subir a GitHub
- **PROJECT_COMPLETION.md** — Resumen técnico completo
- **docs/** — Documentación por phase
- **README.md** — Descripción general

---

## ✅ CHECKLIST RÁPIDO

```
☐ Ejecuta: docker-compose up -d
☐ Espera 30 segundos
☐ Abre: http://localhost:8000
☐ Verifica logs: docker-compose logs -f
☐ Listo! Dashboard funcionando 🚀
```

---

## 🎊 ¡DISFRUTA!

Tu sistema está **100% funcional** y **totalmente automatizado**.

Las predicciones se actualizan cada 15 minutos automáticamente.

**El dashboard muestra DATOS EN VIVO desde tu pipeline.**

---

**Próximo paso:** Abre terminal y copia:
```bash
cd /home/administrador/Desktop/petro && docker-compose up -d && sleep 30 && open http://localhost:8000
```

**¡A disfrutar del proyecto! 🚀**
