import requests
import os
import sys
import json
import time
import re
from requests.adapters import HTTPAdapter
from src.db_manager import DatabaseManager

DEBUG_MODE = os.getenv("DEBUG_MODE", "False") == "True"

db = DatabaseManager()

SPORTS_ENDPOINT = "https://api.draftkings.com/sites/US-DK/sports/v1/sports?format=json"
CONTESTS_ENDPOINT = "https://www.draftkings.com/lobby/getcontests?sport={sport}"
DRAFTABLES_ENDPOINT = "https://api.draftkings.com/draftgroups/v1/draftgroups/{draftgroup_id}/draftables"

def get_session():
    """Create a session with retry mechanism for handling transient errors."""
    session = requests.Session()
    adapter = HTTPAdapter(max_retries=3)
    session.mount("https://", adapter)
    return session

session = get_session()

def debug_log(message):
    if DEBUG_MODE:
        print(f"[DEBUG] {message}")

def fetch_sports():
    """Fetch all sports with their regionAbbreviatedSportName."""
    try:
        response = session.get(SPORTS_ENDPOINT, timeout=10)
        response.raise_for_status()
        sports_data = response.json()
        return [sport['regionAbbreviatedSportName'] for sport in sports_data.get('sports', [])]
    except requests.RequestException as e:
        print(f"Error fetching sports: {e}")
        return []

def extract_teams_from_contest_name(contest_name):
    """Extract team abbreviations from contest name."""
    match = re.search(r'\((\w+)\s*@\s*(\w+)\)', contest_name)
    if match:
        return {"team1": match.group(1), "team2": match.group(2)}
    return None

def is_valid_game_type(game_type, sport):
    """Check if the game type should be included based on sport-specific rules."""
    valid_types = ["Classic", "Showdown Captain Mode"]
    if sport == "TEN":
        valid_types.append("Single Game")
    return game_type in valid_types

def fetch_and_store_draftgroup_metadata(sport, raw_data):
    """Fetch draftgroup metadata from raw response and store in database."""
    draftgroups_added = 0
    for contest in raw_data.get('Contests', []):
        dg_id = contest.get('dg')
        game_type = contest.get('gameType', 'Unknown')
        
        if dg_id is not None and is_valid_game_type(game_type, sport):
            start_time = contest.get('sdstring', '')
            contest_name = contest.get('n', '')
            teams = None
            
            if "Showdown" in game_type or "Captain" in game_type:
                teams = extract_teams_from_contest_name(contest_name)
            
            try:
                db.add_or_update_draftgroup(dg_id, sport, start_time, game_type, teams)
                draftgroups_added += 1
            except Exception as e:
                print(f"Error storing draftgroup {dg_id}: {e}")
    
    return draftgroups_added

def fetch_and_store_draftables(draftgroup_id, sport):
    """Fetch draftables for a specific draftgroup ID and store in database."""
    draftables_endpoint = f"https://api.draftkings.com/draftgroups/v1/draftgroups/{draftgroup_id}/draftables?format=json"
    
    try:
        response = session.get(draftables_endpoint, timeout=10)
        response.raise_for_status()
        draftables_data = response.json()
        
        db.add_draftables(draftgroup_id, sport, draftables_data)
        debug_log(f"Draftables for DraftGroupId {draftgroup_id} stored in database.")
        print(f"Draftables stored: {draftgroup_id}")
        
        time.sleep(0.5)
        return True
    except requests.RequestException as e:
        print(f"Error fetching draftables for DraftGroupId {draftgroup_id}: {e}")
        return False

def main():
    """Main function orchestrating the two-step data ingestion process."""
    print("Step 1: Fetching sports...")
    sports = fetch_sports()
    if not sports:
        print("No sports data available.")
        sys.exit(1)
    
    print(f"Found {len(sports)} sports.")
    
    print("\nStep 2: Fetching and storing draftgroup metadata...")
    total_draftgroups_added = 0
    for sport in sorted(sports):
        url = CONTESTS_ENDPOINT.format(sport=sport)
        try:
            response = session.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            draftgroups_added = fetch_and_store_draftgroup_metadata(sport, data)
            total_draftgroups_added += draftgroups_added
            print(f"{sport}: Added/Updated {draftgroups_added} draftgroups")
        except requests.RequestException as e:
            print(f"Error fetching contest data for {sport}: {e}")
    
    print(f"\nTotal draftgroups added/updated: {total_draftgroups_added}")
    
    print("\nStep 3: Fetching and storing draftables for new draftgroups...")
    new_draftgroups = db.get_new_draftgroups()
    print(f"Found {len(new_draftgroups)} new draftgroups without draftables.")
    
    total_draftables_fetched = 0
    for dg in new_draftgroups:
        if fetch_and_store_draftables(dg['dg_id'], dg['sport']):
            total_draftables_fetched += 1
    
    print(f"\nCompleted! Fetched draftables for {total_draftables_fetched} draftgroups.")
    print("Data is now stored in the database and ready to be accessed via API.")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error running script: {e}")
        import traceback
        traceback.print_exc()