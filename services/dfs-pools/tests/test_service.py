"""
DFS Pools Service - Integration Test Suite
Cross-platform testing for Windows and Linux
"""

import requests
import time
import sys
import os

BASE_URL = "http://localhost:5000"

def test_service_health():
    """Test 1: Service is running and healthy"""
    print("\n[TEST 1] Checking service health...")
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=5)
        assert response.status_code == 200, f"Health check failed: {response.status_code}"
        print("  ✓ Service is healthy")
        return True
    except Exception as e:
        print(f"  ✗ FAILED: {e}")
        return False

def test_trigger_ingestion():
    """Test 2: Trigger full data ingestion"""
    print("\n[TEST 2] Triggering data ingestion...")
    print("  This will take 2-5 minutes to fetch all sports from DraftKings...")
    
    try:
        response = requests.post(f"{BASE_URL}/api/scheduler/trigger", timeout=300)
        assert response.status_code == 200, f"Ingestion failed: {response.status_code}"
        print("  ✓ Data ingestion completed")
        return True
    except Exception as e:
        print(f"  ✗ FAILED: {e}")
        return False

def test_sports_fetched():
    """Test 3: Verify sports data was fetched"""
    print("\n[TEST 3] Verifying sports data...")
    try:
        response = requests.get(f"{BASE_URL}/api/sports", timeout=10)
        assert response.status_code == 200, "Sports endpoint failed"
        
        data = response.json()
        sports = data.get('sports', [])
        sport_count = len(sports)
        
        assert sport_count > 0, "No sports found"
        print(f"  ✓ Found {sport_count} sports: {', '.join(sorted(sports)[:5])}{'...' if sport_count > 5 else ''}")
        return True
    except Exception as e:
        print(f"  ✗ FAILED: {e}")
        return False

def test_draftgroups_fetched():
    """Test 4: Verify draftgroups were fetched"""
    print("\n[TEST 4] Verifying draftgroups...")
    try:
        response = requests.get(f"{BASE_URL}/api/draftgroups", timeout=10)
        assert response.status_code == 200, "Draftgroups endpoint failed"
        
        data = response.json()
        count = data.get('count', 0)
        
        assert count > 0, "No draftgroups found"
        print(f"  ✓ Found {count} draftgroups")
        
        # Show breakdown by sport
        draftgroups_by_sport = data.get('draftgroups', [])
        sports_with_dgs = {}
        for dg in draftgroups_by_sport:
            sport = dg['sport']
            sports_with_dgs[sport] = sports_with_dgs.get(sport, 0) + 1
        
        print(f"  ✓ Breakdown by sport:")
        for sport, dg_count in sorted(sports_with_dgs.items())[:10]:
            print(f"      {sport}: {dg_count}")
        
        return True
    except Exception as e:
        print(f"  ✗ FAILED: {e}")
        return False

def test_draftables_fetched(sample_sport='NFL'):
    """Test 5: Verify player pools (draftables) were fetched"""
    print(f"\n[TEST 5] Verifying player pools for {sample_sport}...")
    try:
        # Get draftgroups for sample sport
        response = requests.get(f"{BASE_URL}/api/sports/{sample_sport}/draftgroups", timeout=10)
        if response.status_code != 200:
            print(f"  ⚠ No {sample_sport} draftgroups found (might be off-season)")
            return True  # Not a failure, just off-season
        
        data = response.json()
        draftgroups = data.get('draftgroups', [])
        
        if not draftgroups:
            print(f"  ⚠ No {sample_sport} draftgroups available")
            return True
        
        # Check if first draftgroup has player data
        dg_id = draftgroups[0]['dg_id']
        response = requests.get(f"{BASE_URL}/api/draftgroups/{dg_id}/draftables", timeout=10)
        
        if response.status_code == 404:
            print(f"  ⚠ Player pools not yet fetched (run longer or wait)")
            return True  # Might still be fetching
        
        assert response.status_code == 200, "Draftables endpoint failed"
        
        data = response.json()
        player_count = data.get('draftables_count', 0)
        
        assert player_count > 0, "No players found"
        print(f"  ✓ Found {player_count} players for {sample_sport} draftgroup {dg_id}")
        return True
    except Exception as e:
        print(f"  ✗ FAILED: {e}")
        return False

def test_optimizer_view():
    """Test 6: Verify optimizer view endpoint works"""
    print("\n[TEST 6] Testing optimizer view...")
    try:
        response = requests.get(f"{BASE_URL}/api/draftgroups/active/optimizer", timeout=10)
        
        if response.status_code == 404:
            print("  ⚠ No active draftgroups (might all be started)")
            return True
        
        assert response.status_code == 200, "Active optimizer endpoint failed"
        
        data = response.json()
        active_count = data.get('active_count', 0)
        
        print(f"  ✓ Found {active_count} active draftgroups with player data")
        
        if active_count > 0:
            first_dg = data['draftgroups'][0]
            player_count = len(first_dg.get('players', []))
            print(f"  ✓ Sample: {first_dg['sport']} has {player_count} players")
        
        return True
    except Exception as e:
        print(f"  ✗ FAILED: {e}")
        return False

def run_all_tests():
    """Run complete test suite"""
    print("=" * 70)
    print("DFS POOLS SERVICE - INTEGRATION TESTS")
    print("=" * 70)
    
    results = []
    
    # Test 1: Health
    results.append(test_service_health())
    
    if not results[0]:
        print("\n✗ Service not running! Start with: python app.py")
        return False
    
    # Test 2-6: Functionality
    results.append(test_trigger_ingestion())
    time.sleep(2)  # Let ingestion start
    results.append(test_sports_fetched())
    results.append(test_draftgroups_fetched())
    results.append(test_draftables_fetched())
    results.append(test_optimizer_view())
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    passed = sum(results)
    total = len(results)
    
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("\n✓ ALL TESTS PASSED - Service is working correctly!")
        return True
    else:
        print(f"\n⚠ {total - passed} test(s) had issues - check messages above")
        return False

if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)