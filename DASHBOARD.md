# PETRO Dashboard - Frontend React/Next.js

## Acceso al Dashboard

El dashboard está disponible en **http://localhost:3000** una vez que se inicie el servidor Next.js.

## Instalación y ejecución

### Opción 1: Desarrollo local

```bash
cd frontend
npm install
npm run dev
```

Accede a **http://localhost:3000**

### Opción 2: Docker (próximamente)

El dashboard se ejecutará en un contenedor separado accesible en **http://localhost:3000**

## Características

✅ **Estadísticas en tiempo real**
- Precio actual de Gasolina 95
- Precio actual de Gasóleo A
- Total de registros en la BD
- Estado del sistema

✅ **Gráficos interactivos**
- Evolución de precios (última semana)
- Precio del Brent (última semana)
- Zoom y paneo en los gráficos

✅ **Métricas del modelo**
- Rendimiento del mejor modelo (XGBoost)
- Comparativa RMSE, R², MAE entre modelos
- Detalles de cada modelo (XGBoost, LightGBM, RandomForest)

✅ **Estado de servicios**
- Database (PostgreSQL + TimescaleDB)
- Redis
- Celery Worker
- Celery Beat
- Indicadores visuales de estado (verde/rojo)

✅ **Actualización automática**
- Los datos se actualizan cada 15 segundos
- Sin necesidad de recargar la página

## Estructura del proyecto

```
frontend/
├── app/
│   └── page.tsx              # Página principal
├── components/
│   ├── Dashboard.tsx         # Dashboard principal con gráficos
│   └── StatCard.tsx          # Componente de tarjeta de estadísticas
├── lib/
│   └── api.ts                # Cliente Axios para la API
├── .env.local                # Configuración local
└── package.json              # Dependencias
```

## Dependencias principales

- **Next.js 14+**: Framework React
- **React 18+**: Librería UI
- **Recharts**: Gráficos interactivos
- **Axios**: Cliente HTTP
- **Tailwind CSS**: Estilos (ya incluido en Next.js)

## API endpoints utilizados

- `GET /api/v1/dashboard/stats` - Estadísticas generales
- `GET /api/v1/dashboard/prices/history` - Historial de precios
- `GET /api/v1/dashboard/brent/history` - Historial de Brent
- `GET /api/v1/dashboard/metrics` - Métricas del modelo
- `GET /api/v1/dashboard/health` - Estado de servicios

## Variables de entorno

```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Cambiar según donde esté desplegada la API de PETRO.

## Problemas comunes

### "Cannot connect to API"
- Verificar que la API FastAPI esté corriendo en http://localhost:8000
- Verificar CORS: la API debe permitir peticiones desde http://localhost:3000

### Gráficos vacíos
- Asegurar que hay datos en la BD (ejecutar la recolección de datos)
- Verificar que los endpoints de API devuelven datos

### Errores de módulos
```bash
# Reinstalar dependencias
rm -rf node_modules package-lock.json
npm install
```

## Próximas mejoras

- [ ] Agregar predicciones futuras en los gráficos
- [ ] Panel de configuración de modelos
- [ ] Exportar reportes en PDF
- [ ] Alertas cuando los precios suban/bajen
- [ ] Análisis detallado por región
- [ ] Integración con WebSockets para actualización en tiempo real
