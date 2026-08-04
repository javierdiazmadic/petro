#!/usr/bin/env python3
"""Test the Toledo API endpoints.

This script tests the new /all-stations and /repsol endpoints.
"""

import asyncio
import sys
import json
from datetime import datetime

# Add src to path
sys.path.insert(0, '/home/administrador/Desktop/petro/src')

from fastapi.testclient import TestClient
from petro.api.main import create_app

logger_simple = print  # Simple print-based logger for tests


def test_all_stations_endpoint():
    """Test GET /api/v1/toledo/all-stations endpoint."""
    print("\n" + "="*70)
    print(" Testing GET /api/v1/toledo/all-stations")
    print("="*70 + "\n")

    try:
        app = create_app()
        client = TestClient(app)

        logger_simple("Making request to /api/v1/toledo/all-stations...")
        response = client.get("/api/v1/toledo/all-stations?max_distance_km=150")

        logger_simple(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()

            logger_simple(f"✓ Endpoint returned successfully")
            logger_simple(f"\nResponse structure:")
            logger_simple(f"  - filter: {data.get('filter')}")
            logger_simple(f"  - total_stations: {data.get('total_stations')}")

            if 'statistics' in data:
                stats = data['statistics']
                logger_simple(f"\n  - Statistics:")
                for fuel, stat in stats.items():
                    logger_simple(f"    {fuel}:")
                    logger_simple(f"      min: €{stat.get('min')}")
                    logger_simple(f"      max: €{stat.get('max')}")
                    logger_simple(f"      media: €{stat.get('media')}")
                    logger_simple(f"      estaciones: {stat.get('estaciones')}")

            # Check sample station
            stations = data.get('gas_stations', [])
            if stations:
                logger_simple(f"\n  - Sample station:")
                sample = stations[0]
                logger_simple(f"    nombre: {sample.get('nombre')}")
                logger_simple(f"    municipio: {sample.get('municipio')}")
                logger_simple(f"    distancia_km: {sample.get('distancia_km')}")
                logger_simple(f"    precios:")
                logger_simple(f"      gasolina_95: €{sample.get('precios', {}).get('gasolina_95')}")
                logger_simple(f"      gasoleoa: €{sample.get('precios', {}).get('gasoleoa')}")

            return True

        else:
            logger_simple(f"✗ Error: {response.status_code}")
            logger_simple(f"Response: {response.text[:200]}")
            return False

    except Exception as e:
        logger_simple(f"✗ Exception: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_repsol_endpoint():
    """Test GET /api/v1/toledo/repsol endpoint."""
    print("\n" + "="*70)
    print(" Testing GET /api/v1/toledo/repsol")
    print("="*70 + "\n")

    try:
        app = create_app()
        client = TestClient(app)

        logger_simple("Making request to /api/v1/toledo/repsol...")
        response = client.get("/api/v1/toledo/repsol?max_distance_km=150")

        logger_simple(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()

            logger_simple(f"✓ Endpoint returned successfully")
            logger_simple(f"\nResponse structure:")
            logger_simple(f"  - filter: {data.get('filter')}")
            logger_simple(f"  - total_stations: {data.get('total_stations')}")

            if 'statistics' in data:
                stats = data['statistics']
                logger_simple(f"\n  - Statistics (Repsol):")
                for fuel, stat in stats.items():
                    logger_simple(f"    {fuel}:")
                    logger_simple(f"      min: €{stat.get('min')}")
                    logger_simple(f"      max: €{stat.get('max')}")
                    logger_simple(f"      media: €{stat.get('media')}")
                    logger_simple(f"      estaciones: {stat.get('estaciones')}")

            if 'comparacion_toledo' in data:
                comp = data['comparacion_toledo']
                logger_simple(f"\n  - Comparison with Toledo Average:")
                for fuel, c in comp.items():
                    logger_simple(f"    {fuel}:")
                    logger_simple(f"      repsol_media: €{c.get('repsol_media')}")
                    logger_simple(f"      toledo_media: €{c.get('toledo_media')}")
                    logger_simple(f"      diferencia: €{c.get('diferencia')}")
                    logger_simple(f"      porcentaje: {c.get('porcentaje')}%")

            # Check sample station
            stations = data.get('gas_stations', [])
            if stations:
                logger_simple(f"\n  - Sample station:")
                sample = stations[0]
                logger_simple(f"    nombre: {sample.get('nombre')}")
                logger_simple(f"    municipio: {sample.get('municipio')}")
                logger_simple(f"    distancia_km: {sample.get('distancia_km')}")
                logger_simple(f"    precios:")
                logger_simple(f"      gasolina_95: €{sample.get('precios', {}).get('gasolina_95')}")
                logger_simple(f"      gasoleoa: €{sample.get('precios', {}).get('gasoleoa')}")

            return True

        else:
            logger_simple(f"✗ Error: {response.status_code}")
            logger_simple(f"Response: {response.text[:200]}")
            return False

    except Exception as e:
        logger_simple(f"✗ Exception: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all endpoint tests."""
    print("\n" + "="*70)
    print(" TOLEDO API ENDPOINTS TEST")
    print("="*70)

    tests = [
        ("GET /api/v1/toledo/all-stations", test_all_stations_endpoint),
        ("GET /api/v1/toledo/repsol", test_repsol_endpoint),
    ]

    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            logger_simple(f"Unexpected error in {test_name}: {e}")
            results[test_name] = False

    # Summary
    print("\n" + "="*70)
    print(" TEST SUMMARY")
    print("="*70 + "\n")

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        logger_simple(f"{status}: {test_name}")

    logger_simple(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        logger_simple("\n✓ All tests passed!")
        return 0
    else:
        logger_simple(f"\n✗ {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
