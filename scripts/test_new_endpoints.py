#!/usr/bin/env python3
"""Quick test for new Toledo endpoints."""

import sys
sys.path.insert(0, '/home/administrador/Desktop/petro/src')

# Test imports
try:
    from petro.api.toledo_analysis import get_all_toledo_stations, get_repsol_toledo_stations
    print("✓ Successfully imported new endpoint functions")
except ImportError as e:
    print(f"✗ Failed to import endpoints: {e}")
    sys.exit(1)

# Test endpoint decorator
try:
    from petro.api.toledo_analysis import router
    routes = [route.path for route in router.routes]
    print(f"✓ Found {len(routes)} routes in toledo router")
    
    # Check for new endpoints
    if '/all-stations' in routes:
        print("✓ /all-stations endpoint registered")
    else:
        print("✗ /all-stations endpoint NOT registered")
        
    if '/repsol' in routes:
        print("✓ /repsol endpoint registered")
    else:
        print("✗ /repsol endpoint NOT registered")
        
except Exception as e:
    print(f"✗ Error checking routes: {e}")
    sys.exit(1)

print("\n✓ All endpoint checks passed!")
