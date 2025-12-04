#!/usr/bin/env python3
"""Simple script to test and pretty-print API responses."""

import requests
import json
from pprint import pprint

BASE_URL = "http://localhost:5000"

def test_endpoint(endpoint, title=None):
    """Fetch and pretty-print an API endpoint response."""
    if title:
        print(f"\n{'='*80}")
        print(f"  {title}")
        print(f"{'='*80}\n")
    
    url = f"{BASE_URL}{endpoint}"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        # Pretty print with indentation
        print(json.dumps(data, indent=2))
    except Exception as e:
        print(f"Error fetching {endpoint}: {e}")

if __name__ == "__main__":
    # Test the sports endpoint
    test_endpoint("/api/sports", "GET /api/sports - Sports with Slate Metadata")
    
    print(f"\n{'='*80}")
    print(f"  END OF OUTPUT")
    print(f"{'='*80}\n")
