#!/usr/bin/env python3
"""
Test script to verify CLI export functionality
"""

import json
import os
import sys
from src.db_manager import DatabaseManager
from src.logger import get_logger, setup_logging
from datetime import datetime

# Fix Unicode encoding on Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

setup_logging()
logger = get_logger(__name__)

DATA_DIR = "data"

def test_export():
    """Test exporting a single slate to JSON"""
    db = DatabaseManager()
    
    # Get first NBA draftgroup
    draftgroups = db.get_all_draftgroups(sport="NBA")
    
    if not draftgroups:
        print("ERROR: No NBA draftgroups found in database")
        return False
    
    draftgroup = draftgroups[0]
    dg_id = draftgroup['dg_id']
    sport = draftgroup['sport']
    
    print(f"\nTesting export for {sport} slate {dg_id}...")
    print(f"  Game Type: {draftgroup['game_type']}")
    print(f"  Start Time: {draftgroup['start_time']}")
    
    # Get player data
    players = db.get_draftables_parsed(dg_id)
    
    if not players:
        print(f"ERROR: No player data found for slate {dg_id}")
        return False
    
    print(f"  Players: {len(players)}")
    
    # Prepare output data
    output_data = {
        "metadata": {
            "sport": sport,
            "dg_id": dg_id,
            "game_type": draftgroup['game_type'],
            "start_time": draftgroup['start_time'],
            "exported_at": datetime.now().isoformat(),
            "total_players": len(players)
        },
        "players": players
    }
    
    # Create data directory if it doesn't exist
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    
    # Generate filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{sport}_{dg_id}_{timestamp}.json"
    filepath = os.path.join(DATA_DIR, filename)
    
    # Write to file
    with open(filepath, 'w') as f:
        json.dump(output_data, f, indent=2)
    
    file_size = os.path.getsize(filepath)
    
    print(f"\n✓ Successfully exported to: {filepath}")
    print(f"  File Size: {file_size / 1024:.1f} KB")
    
    # Verify file was created and has content
    if os.path.exists(filepath) and file_size > 0:
        print("\n✓ Export test PASSED")
        return True
    else:
        print("\n✗ Export test FAILED")
        return False

if __name__ == "__main__":
    try:
        success = test_export()
        sys.exit(0 if success else 1)
    except Exception as e:
        logger.error(f"Test error: {e}")
        print(f"ERROR: {e}")
        sys.exit(1)
