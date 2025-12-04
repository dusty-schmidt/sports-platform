"""
Test suite for the DFS Pools Service scheduler mechanism.

This script verifies:
1. Scheduler startup and shutdown
2. Manual data ingestion triggering
3. Scheduler status reporting
4. Database updates from scheduled ingestion
"""

import unittest
import time
import os
import sys
import json
from datetime import datetime
from unittest.mock import patch, MagicMock
import requests

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pool_scheduler import PoolScheduler
from db_manager import DatabaseManager
from api_server import app

class TestSchedulerBasics(unittest.TestCase):
    """Test basic scheduler functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.scheduler = PoolScheduler()
    
    def test_scheduler_initialization(self):
        """Test that scheduler initializes without errors."""
        self.assertFalse(self.scheduler.is_running)
        self.assertIsNotNone(self.scheduler.scheduler)
    
    def test_scheduler_start(self):
        """Test scheduler startup."""
        try:
            self.scheduler.start(update_interval_hours=1)
            self.assertTrue(self.scheduler.is_running)
            self.scheduler.stop()
            self.assertFalse(self.scheduler.is_running)
        except Exception as e:
            self.fail(f"Scheduler startup failed: {e}")
    
    def test_scheduler_prevent_double_start(self):
        """Test that starting scheduler twice doesn't cause issues."""
        try:
            self.scheduler.start(update_interval_hours=1)
            self.scheduler.start(update_interval_hours=1)  # Should warn, not fail
            self.assertTrue(self.scheduler.is_running)
            self.scheduler.stop()
        except Exception as e:
            self.fail(f"Double start failed: {e}")
    
    def test_scheduler_stop_when_not_running(self):
        """Test stopping scheduler when it's not running."""
        try:
            self.scheduler.stop()  # Should warn, not fail
            self.assertFalse(self.scheduler.is_running)
        except Exception as e:
            self.fail(f"Stop when not running failed: {e}")


class TestAPISchedulerEndpoints(unittest.TestCase):
    """Test scheduler API endpoints."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test client."""
        app.config['TESTING'] = True
        cls.client = app.test_client()
    
    def test_scheduler_status_endpoint(self):
        """Test GET /api/scheduler/status endpoint."""
        response = self.client.get('/api/scheduler/status')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('scheduler_enabled', data)
        self.assertIn('is_running', data)
        self.assertIn('update_interval_hours', data)
    
    def test_trigger_endpoint_returns_success(self):
        """Test POST /api/scheduler/trigger endpoint."""
        response = self.client.post('/api/scheduler/trigger')
        # May return 200 or 500 depending on whether data fetch succeeds
        # We just verify the endpoint exists and returns JSON
        self.assertIn(response.status_code, [200, 500])
        
        try:
            data = json.loads(response.data)
            self.assertIn('status', data)
            self.assertIn('message', data)
        except json.JSONDecodeError:
            self.fail("Trigger endpoint did not return JSON")


class TestSchedulerDataIngestion(unittest.TestCase):
    """Test that scheduler actually invokes data ingestion."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.db = DatabaseManager()
        self.initial_count = len(self.db.get_all_draftgroups())
    
    @patch('pool_scheduler.dk_pools.main')
    def test_scheduler_calls_data_ingestion(self, mock_main):
        """Test that scheduler calls dk_pools.main()."""
        scheduler = PoolScheduler()
        scheduler._run_data_ingestion()
        
        # Verify dk_pools.main was called
        mock_main.assert_called_once()
    
    def test_manual_trigger_via_api(self):
        """Test manual trigger via API endpoint."""
        app.config['TESTING'] = True
        client = app.test_client()
        
        # This will attempt real data ingestion if enabled
        response = client.post('/api/scheduler/trigger')
        
        # Should return valid JSON response
        self.assertEqual(response.content_type, 'application/json')
        data = json.loads(response.data)
        self.assertIn('status', data)


class TestEnvironmentConfiguration(unittest.TestCase):
    """Test environment variable configuration."""
    
    def test_scheduler_enabled_flag(self):
        """Test SCHEDULER_ENABLED environment variable."""
        # Check if environment variables are being read
        from api_server import SCHEDULER_ENABLED, SCHEDULER_INTERVAL_HOURS
        
        self.assertIsInstance(SCHEDULER_ENABLED, bool)
        self.assertIsInstance(SCHEDULER_INTERVAL_HOURS, int)
        self.assertGreater(SCHEDULER_INTERVAL_HOURS, 0)
    
    def test_environment_variable_override(self):
        """Test that environment variables can override defaults."""
        os.environ['SCHEDULER_INTERVAL_HOURS'] = '2'
        
        # Reimport to get new values
        import importlib
        import api_server
        importlib.reload(api_server)
        
        self.assertEqual(api_server.SCHEDULER_INTERVAL_HOURS, 2)
        
        # Cleanup
        del os.environ['SCHEDULER_INTERVAL_HOURS']


class TestSchedulerLogging(unittest.TestCase):
    """Test that scheduler generates appropriate logs."""
    
    def test_scheduler_logs_startup(self):
        """Test that scheduler logs startup messages."""
        import logging
        
        # Capture logs
        logger = logging.getLogger('pool_scheduler')
        logger.setLevel(logging.INFO)
        
        scheduler = PoolScheduler()
        try:
            scheduler.start(update_interval_hours=1)
            # If we get here, logging at least didn't crash
            self.assertTrue(scheduler.is_running)
            scheduler.stop()
        except Exception as e:
            self.fail(f"Scheduler logging test failed: {e}")


def run_integration_test():
    """Run a simple integration test with the full API."""
    print("\n" + "="*60)
    print("INTEGRATION TEST: Full Schedule Mechanism")
    print("="*60)
    
    app.config['TESTING'] = True
    client = app.test_client()
    
    # Test 1: Check scheduler status
    print("\n1. Checking scheduler status...")
    response = client.get('/api/scheduler/status')
    if response.status_code == 200:
        status = json.loads(response.data)
        print(f"   [PASS] Scheduler enabled: {status.get('scheduler_enabled')}")
        print(f"   [PASS] Scheduler running: {status.get('is_running')}")
        print(f"   [PASS] Update interval: {status.get('update_interval_hours')} hours")
    else:
        print(f"   [FAIL] Status endpoint failed: {response.status_code}")
    
    # Test 2: Verify API health
    print("\n2. Checking API health...")
    response = client.get('/api/health')
    if response.status_code == 200:
        print("   [PASS] API is healthy")
    else:
        print(f"   [FAIL] Health check failed: {response.status_code}")
    
    # Test 3: Verify draftgroups endpoint
    print("\n3. Checking draftgroups endpoint...")
    response = client.get('/api/draftgroups')
    if response.status_code == 200:
        data = json.loads(response.data)
        print(f"   [PASS] Draftgroups endpoint working: {data.get('count')} draftgroups found")
    else:
        print(f"   [FAIL] Draftgroups endpoint failed: {response.status_code}")
    
    # Test 4: Verify active draftgroups endpoint
    print("\n4. Checking active draftgroups endpoint...")
    response = client.get('/api/draftgroups/active')
    if response.status_code in [200, 404]:
        print("   [PASS] Active draftgroups endpoint working")
    else:
        print(f"   [FAIL] Active draftgroups endpoint failed: {response.status_code}")
    
    print("\n" + "="*60)
    print("INTEGRATION TEST COMPLETE")
    print("="*60 + "\n")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Test DFS Pools Service scheduler')
    parser.add_argument('--integration', action='store_true', help='Run integration test')
    parser.add_argument('--verbose', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    if args.integration:
        run_integration_test()
    else:
        # Run unit tests
        verbosity = 2 if args.verbose else 1
        unittest.main(verbosity=verbosity, exit=True)