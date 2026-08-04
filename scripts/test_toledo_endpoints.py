#!/usr/bin/env python3
"""Test script for Toledo dynamic endpoints."""

import asyncio
import sys
import json
from datetime import datetime

# Add src to path
sys.path.insert(0, '/home/administrador/Desktop/petro/src')

from petro.core import get_logger
from petro.infrastructure.connectors.minetur_carburantes import MineturCarburantesConnector

logger = get_logger(__name__)


def print_section(title: str):
    """Print a formatted section header."""
    print(f"\n{'='*70}")
    print(f" {title}")
    print(f"{'='*70}\n")


def test_ministerio_connection():
    """Test connection to Ministerio API."""
    print_section("Testing Ministerio de Energía Connection")

    try:
        logger.info("Fetching Toledo stations from Ministerio...")
        data = MineturCarburantesConnector.fetch_toledo_stations()

        if not data:
            logger.error("No data returned")
            return False

        logger.info("✓ Successfully connected to Ministerio API")
        logger.info(f"✓ Total stations in Toledo: {data.get('total_estaciones', 0)}")

        # Check statistics
        stats = data.get('estadisticas', {})
        logger.info(f"\nPrice Statistics:")
        logger.info(f"  Gasolina 95:")
        logger.info(f"    Min: €{stats.get('gasolina_95', {}).get('min', 'N/A')}")
        logger.info(f"    Max: €{stats.get('gasolina_95', {}).get('max', 'N/A')}")
        logger.info(f"    Avg: €{stats.get('gasolina_95', {}).get('media', 'N/A')}")
        logger.info(f"  Gasóleo A:")
        logger.info(f"    Min: €{stats.get('gasoleoa', {}).get('min', 'N/A')}")
        logger.info(f"    Max: €{stats.get('gasoleoa', {}).get('max', 'N/A')}")
        logger.info(f"    Avg: €{stats.get('gasoleoa', {}).get('media', 'N/A')}")

        # Sample stations
        stations = data.get('estaciones', [])[:3]
        logger.info(f"\nSample stations (first 3):")
        for s in stations:
            logger.info(f"  - {s.get('nombre', 'Unknown')} ({s.get('municipio', '')})")
            logger.info(f"    95: €{s['precios'].get('gasolina_95', 'N/A')} | Diesel: €{s['precios'].get('gasoleoa', 'N/A')}")

        return True

    except Exception as e:
        logger.error(f"✗ Error connecting to Ministerio: {e}", exc_info=True)
        return False


def test_repsol_filtering():
    """Test Repsol filtering."""
    print_section("Testing Repsol Brand Filtering")

    try:
        logger.info("Fetching Toledo stations and filtering Repsol...")
        data = MineturCarburantesConnector.fetch_toledo_stations()

        if not data:
            logger.error("No data returned")
            return False

        # Filter Repsol
        all_stations = data.get('estaciones', [])
        repsol_stations = [
            s for s in all_stations
            if 'REPSOL' in s.get('nombre', '').upper()
        ]

        logger.info(f"✓ Total stations: {len(all_stations)}")
        logger.info(f"✓ Repsol stations: {len(repsol_stations)}")

        if repsol_stations:
            # Calculate Repsol averages
            prices_95 = [
                s['precios'].get('gasolina_95')
                for s in repsol_stations
                if s['precios'].get('gasolina_95') is not None
            ]
            prices_diesel = [
                s['precios'].get('gasoleoa')
                for s in repsol_stations
                if s['precios'].get('gasoleoa') is not None
            ]

            avg_95 = sum(prices_95) / len(prices_95) if prices_95 else 0
            avg_diesel = sum(prices_diesel) / len(prices_diesel) if prices_diesel else 0

            logger.info(f"\nRepsol Average Prices:")
            logger.info(f"  Gasolina 95: €{avg_95:.3f}")
            logger.info(f"  Gasóleo A: €{avg_diesel:.3f}")

            # Sample Repsol stations
            logger.info(f"\nSample Repsol stations (first 3):")
            for s in repsol_stations[:3]:
                logger.info(f"  - {s.get('nombre', 'Unknown')}")
                logger.info(f"    95: €{s['precios'].get('gasolina_95', 'N/A')} | Diesel: €{s['precios'].get('gasoleoa', 'N/A')}")

            return True

        else:
            logger.warning("⚠ No Repsol stations found - check data format")
            return False

    except Exception as e:
        logger.error(f"✗ Error filtering Repsol: {e}", exc_info=True)
        return False


def test_distance_calculation():
    """Test distance calculations."""
    print_section("Testing Distance Calculations")

    try:
        from petro.api.toledo_analysis import calculate_distance

        # Test Los Yébenes (center)
        center_lat = 39.86
        center_lon = -3.96

        # Test points
        test_points = [
            ("Los Yébenes (center)", 39.86, -3.96, 0),
            ("Toledo", 39.8627, -3.9447, 3.7),  # ~3.7 km
            ("Puertollano", 38.6975, -4.1186, 130),  # ~130 km
        ]

        logger.info("Testing distance calculations from Los Yébenes (39.86, -3.96):")

        all_passed = True
        for name, lat, lon, expected_km in test_points:
            distance = calculate_distance(center_lat, center_lon, lat, lon)
            logger.info(f"  {name}: {distance:.1f} km (expected ~{expected_km} km)")

            # Basic validation
            if name == "Los Yébenes (center)" and distance > 1:
                logger.warning(f"    ⚠ Distance should be ~0 km for center")
                all_passed = False
            elif name == "Toledo" and not (1 < distance < 10):
                logger.warning(f"    ⚠ Distance seems off")
                all_passed = False
            else:
                logger.info(f"    ✓ OK")

        return all_passed

    except Exception as e:
        logger.error(f"✗ Error testing distance: {e}", exc_info=True)
        return False


def test_statistics_calculation():
    """Test statistics calculations."""
    print_section("Testing Statistics Calculations")

    try:
        data = MineturCarburantesConnector.fetch_toledo_stations()

        if not data:
            logger.error("No data returned")
            return False

        stats = data.get('estadisticas', {})

        logger.info("Statistics validation:")

        # Check each fuel type
        for fuel in ['gasolina_95', 'gasoleoa']:
            fuel_stats = stats.get(fuel, {})
            min_price = fuel_stats.get('min')
            max_price = fuel_stats.get('max')
            avg_price = fuel_stats.get('media')

            logger.info(f"\n{fuel.upper()}:")
            logger.info(f"  Min: €{min_price:.3f}")
            logger.info(f"  Max: €{max_price:.3f}")
            logger.info(f"  Avg: €{avg_price:.3f}")

            # Validation
            if min_price and max_price and avg_price:
                if min_price <= avg_price <= max_price:
                    logger.info(f"  ✓ Valid (min ≤ avg ≤ max)")
                else:
                    logger.warning(f"  ✗ Invalid range")
                    return False
            else:
                logger.warning(f"  ✗ Missing data")
                return False

        return True

    except Exception as e:
        logger.error(f"✗ Error testing statistics: {e}", exc_info=True)
        return False


def test_caching():
    """Test caching mechanism."""
    print_section("Testing Cache Mechanism (1 hour)")

    try:
        from petro.api.toledo_analysis import get_cached_data, cache_data

        logger.info("Testing cache store and retrieve...")

        test_key = "test_toledo_cache"
        test_data = {
            "test": "data",
            "timestamp": datetime.now().isoformat()
        }

        # Store
        cache_data(test_key, test_data)
        logger.info("✓ Data cached")

        # Retrieve
        cached = get_cached_data(test_key)
        if cached and cached["test"] == "data":
            logger.info("✓ Data retrieved from cache")
            return True
        else:
            logger.error("✗ Could not retrieve cached data")
            return False

    except Exception as e:
        logger.error(f"✗ Error testing cache: {e}", exc_info=True)
        return False


def main():
    """Run all tests."""
    print_section("TOLEDO DYNAMIC ENDPOINTS TEST SUITE")
    logger.info(f"Test started at: {datetime.now().isoformat()}")

    tests = [
        ("Ministerio Connection", test_ministerio_connection),
        ("Repsol Filtering", test_repsol_filtering),
        ("Distance Calculation", test_distance_calculation),
        ("Statistics Calculation", test_statistics_calculation),
        ("Caching Mechanism", test_caching),
    ]

    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            logger.error(f"Unexpected error in {test_name}: {e}")
            results[test_name] = False

    # Summary
    print_section("TEST SUMMARY")
    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for test_name, passed_flag in results.items():
        status = "✓ PASS" if passed_flag else "✗ FAIL"
        logger.info(f"{status}: {test_name}")

    logger.info(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        logger.info("\n✓ All tests passed!")
        return 0
    else:
        logger.warning(f"\n✗ {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
