# 🌐 Arquitectura Distribuida - PETRO

## 📋 Resumen

Sistema PETRO con arquitectura cliente-servidor:

- **SERVIDOR** (tu PC actual): Entrena modelos + API + GitHub
- **CLIENTES** (otros PCs en red local): Solo frontend que ve gráficos en remoto

Cada noche:
1. Servidor entrena y sube a GitHub
2. Clientes descargan proyecto actualizado
3. Clientes ven gráficos actualizados sin instalar nada

---

## 🏗️ Arquitectura

```
┌─────────────────────────────────────────────────────────────┐
│                    GITHUB (sincronización)                  │
└────────────────────┬────────────────────────────────────────┘
                     ↑↓
    ┌────────────────────────────────────────┐
    │  SERVIDOR LOCAL (Tu PC actual)         │
    ├────────────────────────────────────────┤
    │  🔧 Entrenamiento (GPU)                │
    │  💾 Exporta modelos + datos            │
    │  📤 Sube a GitHub                      │
    │  🌐 API REST (localhost:8000)          │
    └────────┬───────────────────────────────┘
             │ Red local (192.168.x.x)
    ┌────────┴───────────┬──────────────┐
    ↓                    ↓              ↓
┌─────────┐         ┌─────────┐   ┌─────────┐
│ Cliente │         │ Cliente │   │ Cliente │
│ PC #1   │         │ PC #2   │   │ PC #3   │
├─────────┤         ├─────────┤   ├─────────┤
│Frontend │         │Frontend │   │Frontend │
│ + datos │         │ + datos │   │ + datos │
│actuales │         │actuales │   │actuales │
└─────────┘         └─────────┘   └─────────┘
```

---

## 🖥️ SERVIDOR - Setup Inicial

### Paso 1: Instalar y configurar

```bash
# En tu servidor (donde está ahora)
cd /home/administrador/Desktop/petro

# Instalar dependencias
python3 -m venv venv
source venv/bin/activate
pip install -e ".[dev]"

# Instalar frontend también
cd frontend && npm install && cd ..
```

### Paso 2: Levantar servidor

```bash
# Opción A: Docker (recomendado)
docker compose up -d

# Opción B: Local
# Terminal 1: API
python -m uvicorn src.petro.api.main:app --reload --port 8000 --host 0.0.0.0

# Terminal 2: Scheduler
python scripts/local_daily_scheduler.py

# Terminal 3: Frontend
cd frontend && npm run dev  # esto usa localhost:3000 localmente
```

**IMPORTANTE**: API en puerto **8000** disponible para red local

### Paso 3: Verificar API accesible en red

```bash
# En el servidor, obtén tu IP local
hostname -I          # Linux
ipconfig             # Windows
ifconfig | grep inet # macOS

# Verifica que API responde
curl http://localhost:8000/api/v1/health
# Debe retornar: {"status": "ok", ...}
```

---

## 💻 CLIENTE - Setup en otros PCs

### Paso 1: Descargar proyecto desde GitHub

```bash
# En los otros PCs (Windows, macOS, Linux)
git clone https://github.com/javierdiazmadic/petro.git
cd petro
```

### Paso 2: Configurar API del servidor

**Archivo**: `frontend/.env.local`

```env
# API del servidor (CAMBIA 192.168.1.100 por IP de tu servidor)
NEXT_PUBLIC_API_URL=http://192.168.1.100:8000
```

### Paso 3: Instalar y ejecutar frontend

```bash
# Instalar dependencias
cd frontend
npm install

# Ejecutar solo el frontend
npm run dev

# Abre en navegador: http://localhost:3000
```

**¡LISTO!** Verás los gráficos del servidor en remoto

---

## 📅 Automatización Cada Noche

### En el SERVIDOR (3:00 AM UTC)

```bash
# Automáticamente ejecuta:
python scripts/local_daily_scheduler.py

# Esto hace:
# 1. Entrena 3 modelos (XGBoost, LightGBM, RandomForest)
# 2. Exporta .h5 + JSON metadata
# 3. git commit + git push a GitHub
# 4. Descarga y carga modelos
```

### En los CLIENTES (cada mañana)

```bash
# Descargar proyecto actualizado
git pull origin master

# O más fácil: script automático
bash scripts/daily_client_update.sh  # Linux/macOS
PowerShell .\scripts\daily_client_update.ps1  # Windows
```

---

## 🔧 Script para Clientes - Actualización Automática

### Linux/macOS: `scripts/daily_client_update.sh`

```bash
#!/bin/bash

# Actualizar proyecto cada noche
cd ~/petro  # O tu ruta

echo "🔄 Actualizando proyecto..."
git pull origin master

echo "📦 Instalando dependencias si es necesario"
cd frontend
npm install

echo "✅ Proyecto actualizado"
echo "Para ejecutar: npm run dev"
```

### Windows: `scripts/daily_client_update.ps1`

```powershell
# Actualizar proyecto cada noche

$projectPath = "C:\Users\YourUser\petro"  # Cambia tu ruta
Set-Location $projectPath

Write-Host "🔄 Actualizando proyecto..." -ForegroundColor Cyan
git pull origin master

Write-Host "📦 Instalando dependencias..." -ForegroundColor Cyan
Set-Location frontend
npm install

Write-Host "✅ Proyecto actualizado" -ForegroundColor Green
Write-Host "Para ejecutar: npm run dev" -ForegroundColor Yellow
```

---

## 🌐 Configuración por Sistema

### WINDOWS

#### Servidor:
```powershell
# Terminal 1 - API
python -m uvicorn src.petro.api.main:app --reload --port 8000 --host 0.0.0.0

# Terminal 2 - Scheduler
python scripts\local_daily_scheduler.py
```

#### Cliente:
```powershell
# Crear .env.local
echo "NEXT_PUBLIC_API_URL=http://192.168.1.100:8000" > frontend\.env.local

# Ejecutar
cd frontend
npm run dev
```

### LINUX/macOS

#### Servidor:
```bash
# Terminal 1 - API
python -m uvicorn src.petro.api.main:app --reload --port 8000 --host 0.0.0.0

# Terminal 2 - Scheduler
python scripts/local_daily_scheduler.py
```

#### Cliente:
```bash
# Crear .env.local
echo "NEXT_PUBLIC_API_URL=http://192.168.1.100:8000" > frontend/.env.local

# Ejecutar
cd frontend
npm run dev
```

---

## 📊 Flujo Completo Cada Día

### Día 1 - Setup Inicial

```
Servidor:
  $ docker compose up -d
  ✅ API en 0.0.0.0:8000

Cliente 1:
  $ git clone ... petro
  $ echo "NEXT_PUBLIC_API_URL=http://192.168.1.100:8000" > frontend/.env.local
  $ cd frontend && npm run dev
  ✅ Abre http://localhost:3000
  ✅ Ve gráficos del servidor

Cliente 2-N:
  (mismo proceso)
```

### 3:00 AM UTC Cada Noche

```
Servidor automáticamente:
  ✅ Entrena modelos (tu GPU)
  ✅ Exporta .h5 + JSON
  ✅ git push a GitHub

Clientes por la mañana:
  $ bash scripts/daily_client_update.sh
  ✅ Proyecto actualizado
  $ cd frontend && npm run dev
  ✅ Gráficos actualizados

4:00 AM (España):
  └─ Abres cliente: TODO NUEVO sin hacer nada
```

---

## 🔍 Verificación

### Servidor - ¿Está disponible?

```bash
# Desde cliente, verifica que puede conectar
curl http://192.168.1.100:8000/api/v1/health

# Debe retornar:
# {"status": "ok", "version": "1.0.0", ...}
```

### Cliente - ¿Está conectado?

```bash
# Abrir dev tools en navegador (F12)
# Network tab
# Buscar peticiones a: http://192.168.1.100:8000/api/v1/

# Si ves requests exitosas (200): ✅ CONECTADO
```

### Gráficos - ¿Se actualizan?

```bash
# En cliente, consola del navegador:
const response = await fetch('http://192.168.1.100:8000/api/v1/models/info')
const data = await response.json()
console.log(data)

# Debe mostrar info de modelos con timestamp actual
```

---

## 🐛 Troubleshooting

### Error: "Cannot connect to server"

```bash
# 1. Verificar IP correcta
ping 192.168.1.100  # Usa tu IP real

# 2. Verificar API está corriendo
curl http://192.168.1.100:8000/api/v1/health

# 3. Firewall
# Windows: abrir puerto 8000
# Linux: sudo ufw allow 8000
# macOS: System Preferences > Security & Privacy
```

### Error: "API URL not set"

```bash
# Verificar archivo frontend/.env.local
cat frontend/.env.local

# Debe tener:
# NEXT_PUBLIC_API_URL=http://192.168.1.100:8000

# Reiniciar npm dev
npm run dev
```

### Error: "Git pull falla"

```bash
# Asegurar credenciales GitHub
git config --global user.name "Tu Nombre"
git config --global user.email "tu@email.com"

# Hacer pull manual
git pull origin master
```

---

## 📱 Acceso desde móvil (opcional)

```
En el móvil (misma red local):
  1. Abre navegador
  2. Ve a: http://192.168.1.100:3000
  3. Verás dashboard en móvil
  
  (si quieres frontend en móvil):
  1. Clone proyecto en PC con Node
  2. npm run dev
  3. Desde móvil: http://PC-IP:3000
```

---

## 🎯 Resumen

| Componente | Ubicación | Función |
|-----------|-----------|---------|
| Entrenamiento | Servidor GPU | 3:00 AM UTC automático |
| Modelos | `/models_export/` Servidor | Exportados cada noche |
| API REST | Servidor:8000 | Sirve datos a clientes |
| GitHub | Nube | Sincronización cada noche |
| Frontend | Clientes | Ve gráficos en remoto |
| Datos | GitHub | Descargan clientes cada mañana |

---

## ✅ Ventajas de este Setup

✅ **Entrenamiento centralizado** - Solo en servidor con GPU  
✅ **Múltiples clientes** - Todos ven los mismos gráficos  
✅ **Actualización automática** - GitHub cada noche  
✅ **Bajo consumo cliente** - Solo frontend, sin cálculos  
✅ **Sincronización** - Todos ven datos actualizados  
✅ **Escalable** - Agregar N clientes fácilmente  

---

*Última actualización: 2026-08-14*
*Arquitectura distribuida PETRO - Production Ready*
