"""Conector para API oficial del Ministerio de Energía - Precios de Carburantes.

Accede a datos reales de precios de combustibles de estaciones de servicio españolas.
Fuente: https://datos.gob.es/es/catalogo/e05068001-precio-de-carburantes-en-las-gasolineras-espanolas
API: https://sedeaplicaciones.minetur.gob.es/ServiciosRESTCarburantes/PreciosCarburantes/EstacionesTerrestres/
"""

import json
import logging
from typing import Dict, List, Optional
from datetime import datetime
import httpx
import ssl

logger = logging.getLogger(__name__)

# URL de la API oficial del Ministerio
MINETUR_API_URL = "https://sedeaplicaciones.minetur.gob.es/ServiciosRESTCarburantes/PreciosCarburantes/EstacionesTerrestres/"

# Caché en memoria para evitar llamadas excesivas
_cache = None
_cache_timestamp = None
CACHE_DURATION_MINUTES = 60  # Cachear durante 1 hora
TIMEOUT_SECONDS = 30.0


class MineturCarburantesConnector:
    """Conector para obtener precios reales de combustibles del Ministerio de Energía."""

    @staticmethod
    def _parse_price(price_str: str) -> Optional[float]:
        """Convertir string de precio a float.

        Args:
            price_str: String con precio (ej: "1,579")

        Returns:
            Float del precio o None si no es válido
        """
        if not price_str or price_str.strip() == '':
            return None
        try:
            return float(price_str.replace(',', '.'))
        except (ValueError, AttributeError):
            return None

    @staticmethod
    def fetch_toledo_stations() -> Dict:
        """Obtener estaciones de servicio reales de Toledo.

        Returns:
            Diccionario con datos de estaciones de Toledo
        """
        global _cache, _cache_timestamp

        # Usar caché si está disponible
        if _cache and _cache_timestamp:
            age_minutes = (datetime.now() - _cache_timestamp).total_seconds() / 60
            if age_minutes < CACHE_DURATION_MINUTES:
                logger.info(f"Usando caché de datos (antigüedad: {age_minutes:.1f} min)")
                return _cache

        try:
            logger.info(f"Obteniendo datos del Ministerio de Energía...")

            # Descargar datos de la API con reintentos
            max_retries = 3
            last_error = None
            data = None

            # Estrategia de reintentos: primero con SSL, luego sin SSL
            for attempt in range(max_retries):
                try:
                    # Intentar con verificación SSL estricta primero
                    logger.info(f"Intento {attempt + 1}/{max_retries} (con SSL)...")
                    with httpx.Client(
                        timeout=TIMEOUT_SECONDS,
                        verify=True,
                        limits=httpx.Limits(max_connections=5, max_keepalive_connections=2)
                    ) as client:
                        response = client.get(
                            MINETUR_API_URL,
                            headers={
                                "Accept": "application/json",
                                "User-Agent": "PETRO/1.0",
                                "Connection": "close"
                            }
                        )
                        response.raise_for_status()
                        data = response.json()
                        logger.info(f"Datos obtenidos exitosamente (intento {attempt + 1} con SSL)")
                        break

                except (httpx.ConnectError, httpx.TimeoutException, httpx.ReadError) as e:
                    last_error = e
                    logger.warning(f"Intento {attempt + 1} falló (SSL): {str(e)[:100]}")

                except httpx.HTTPStatusError as e:
                    last_error = e
                    logger.warning(f"HTTP Error {attempt + 1}: {e.response.status_code}")

                except Exception as e:
                    last_error = e
                    logger.warning(f"Intento {attempt + 1} falló: {str(e)[:100]}")

            # Si falló con SSL, intentar sin verificación SSL
            if not data and last_error:
                logger.warning("Intentando sin verificación SSL...")
                try:
                    with httpx.Client(
                        timeout=TIMEOUT_SECONDS,
                        verify=False,
                        limits=httpx.Limits(max_connections=5, max_keepalive_connections=2)
                    ) as client:
                        response = client.get(
                            MINETUR_API_URL,
                            headers={
                                "Accept": "application/json",
                                "User-Agent": "PETRO/1.0",
                                "Connection": "close"
                            }
                        )
                        response.raise_for_status()
                        data = response.json()
                        logger.info("Datos obtenidos sin verificación SSL")

                except Exception as e2:
                    logger.error(f"Error sin SSL: {str(e2)[:100]}")
                    last_error = e2

            if not data:
                # Si se agotaron todos los intentos
                if last_error:
                    raise last_error
                raise Exception("No se pudieron obtener datos del Ministerio")

            # Filtrar solo estaciones de Toledo
            toledo_stations = [
                station for station in data.get('ListaEESSPrecio', [])
                if station.get('Provincia', '').upper() == 'TOLEDO'
            ]

            logger.info(f"Encontradas {len(toledo_stations)} estaciones en Toledo")

            # Procesar y limpiar datos
            processed_stations = []
            for station in toledo_stations:
                processed = {
                    'id': station.get('IDEESS', ''),
                    'nombre': station.get('Rótulo', 'N/A'),
                    'direccion': station.get('Dirección', ''),
                    'municipio': station.get('Municipio', ''),
                    'provincia': 'Toledo',
                    'latitud': MineturCarburantesConnector._parse_float(
                        station.get('Latitud', '0')
                    ),
                    'longitud': MineturCarburantesConnector._parse_float(
                        station.get('Longitud (WGS84)', '0')
                    ),
                    'horario': station.get('Horario', ''),
                    'precios': {
                        'gasolina_95': MineturCarburantesConnector._parse_price(
                            station.get('Precio Gasolina 95 E5', '')
                        ),
                        'gasolina_98': MineturCarburantesConnector._parse_price(
                            station.get('Precio Gasolina 98 E5', '')
                        ),
                        'gasoleoa': MineturCarburantesConnector._parse_price(
                            station.get('Precio Gasoleo A', '')
                        ),
                        'gasoleob': MineturCarburantesConnector._parse_price(
                            station.get('Precio Gasoleo B', '')
                        ),
                    },
                }
                processed_stations.append(processed)

            # Calcular estadísticas
            stats = MineturCarburantesConnector._calculate_stats(processed_stations)

            result = {
                'fecha_actualizacion': data.get('Fecha', ''),
                'provincia': 'Toledo',
                'total_estaciones': len(processed_stations),
                'estaciones': processed_stations,
                'estadisticas': stats,
                'fuente': 'Ministerio de Energía (datos.gob.es)',
            }

            # Guardar en caché
            _cache = result
            _cache_timestamp = datetime.now()

            return result

        except httpx.HTTPError as e:
            logger.error(f"Error conectando con API del Ministerio: {e}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Error decodificando respuesta JSON: {e}")
            raise
        except Exception as e:
            logger.error(f"Error inesperado en Minetur: {e}", exc_info=True)
            raise

    @staticmethod
    def _parse_float(value: str) -> float:
        """Convertir string a float reemplazando coma por punto.

        Args:
            value: String con número (ej: "39,211417")

        Returns:
            Float del número
        """
        try:
            return float(value.replace(',', '.'))
        except (ValueError, AttributeError):
            return 0.0

    @staticmethod
    def _calculate_stats(stations: List[Dict]) -> Dict:
        """Calcular estadísticas de precios.

        Args:
            stations: Lista de estaciones procesadas

        Returns:
            Diccionario con estadísticas por tipo de combustible
        """
        stats = {}

        for fuel in ['gasolina_95', 'gasolina_98', 'gasoleoa', 'gasoleob']:
            prices = [
                s['precios'][fuel] for s in stations
                if s['precios'][fuel] is not None
            ]

            if prices:
                stats[fuel] = {
                    'min': round(min(prices), 3),
                    'max': round(max(prices), 3),
                    'media': round(sum(prices) / len(prices), 3),
                    'estaciones_con_precio': len(prices),
                    'total_estaciones': len(stations),
                }
            else:
                stats[fuel] = {
                    'min': None,
                    'max': None,
                    'media': None,
                    'estaciones_con_precio': 0,
                    'total_estaciones': len(stations),
                }

        return stats

    @staticmethod
    def get_toledo_daily_prices() -> Dict[str, float]:
        """Obtener precios promedio diarios de Toledo.

        Returns:
            Diccionario con precios promedio por tipo de combustible
        """
        data = MineturCarburantesConnector.fetch_toledo_stations()
        stats = data['estadisticas']

        return {
            'gasolina_95': stats['gasolina_95']['media'],
            'gasolina_98': stats['gasolina_98']['media'],
            'gasoleoa': stats['gasoleoa']['media'],
            'gasoleob': stats['gasoleob']['media'],
            'timestamp': datetime.now().isoformat(),
            'provincia': 'Toledo',
            'fuente': 'Ministerio de Energía',
        }
