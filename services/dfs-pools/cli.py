#!/usr/bin/env python3
"""
DFS Pools CLI - Interactive tool to browse and export player pool data
Pulls from the pre-populated database and outputs JSON files to data/ directory
"""

import json
import os
import sys
from datetime import datetime

# Fix Unicode encoding on Windows
if sys.platform == 'win32':
    import codecs
    sys.stdout.reconfigure(encoding='utf-8')
from src.db_manager import DatabaseManager
from src.logger import get_logger, setup_logging

setup_logging()
logger = get_logger(__name__)

# Ensure data directory exists
DATA_DIR = "data"
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)
    logger.info(f"Created data directory: {DATA_DIR}")


def clear_screen():
    """Clear terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')


def display_header(title):
    """Display a formatted header"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60 + "\n")


def safe_print(text):
    """Print text with ASCII-safe fallback"""
    try:
        print(text)
    except UnicodeEncodeError:
        # Fallback: remove non-ASCII characters
        print(text.encode('ascii', 'ignore').decode('ascii'))


def select_sport():
    """Display sports with available player pools and let user select one"""
    clear_screen()
    display_header("DFS POOLS - SELECT SPORT")
    
    db = DatabaseManager()
    sports = db.get_available_sports()
    
    if not sports:
        print("[ERROR] No sports with available player pools found.")
        print("        Ensure the scheduler has fetched data.")
        input("\nPress Enter to return to menu...")
        return None
    
    print("Available Sports with Player Pools:\n")
    for idx, sport_info in enumerate(sports, 1):
        sport = sport_info['sport']
        count = sport_info['slate_count']
        print(f"  {idx}. {sport:<15} ({count} slate{'s' if count != 1 else ''})")
    
    print(f"\n  0. Exit")
    
    while True:
        try:
            choice = input("\nSelect sport (enter number): ").strip()
            
            if choice == "0":
                return None
            
            idx = int(choice) - 1
            if 0 <= idx < len(sports):
                return sports[idx]['sport']
            else:
                print("[ERROR] Invalid selection. Please try again.")
        except ValueError:
            print("[ERROR] Please enter a valid number.")


def select_slate(sport):
    """Display available slates for selected sport and let user select one"""
    clear_screen()
    display_header(f"DFS POOLS - SELECT SLATE ({sport})")
    
    db = DatabaseManager()
    slates = db.get_available_slates(sport)
    
    if not slates:
        print(f"[ERROR] No slates with player pools found for {sport}.")
        input("\nPress Enter to return to menu...")
        return None
    
    print(f"Available {sport} Slates with Player Pools:\n")
    for idx, slate in enumerate(slates, 1):
        dg_id = slate['dg_id']
        game_type = slate['game_type']
        start_time_display = slate['start_time_display']
        start_time_timestamp = slate['start_time_timestamp']
        game_count = slate['game_count']
        player_count = slate['player_count']
        
        label = f"{game_type} - {start_time_display} - {game_count} game{'s' if game_count != 1 else ''}"
        print(f"  {idx}. ID: {dg_id:<10} | {label:<40} ({player_count} players)")
    
    print(f"\n  0. Back to Sport Selection")
    
    while True:
        try:
            choice = input("\nSelect slate (enter number): ").strip()
            
            if choice == "0":
                return None
            
            idx = int(choice) - 1
            if 0 <= idx < len(slates):
                return slates[idx]
            else:
                print("[ERROR] Invalid selection. Please try again.")
        except ValueError:
            print("[ERROR] Please enter a valid number.")


def export_player_data(sport, slate):
    """Fetch player data for slate and export to JSON file"""
    db = DatabaseManager()
    dg_id = slate['dg_id']
    
    print(f"\n[WAIT] Fetching player data for slate {dg_id}...")
    
    try:
        # Get player data
        players = db.get_draftables_parsed(dg_id)
        
        if not players:
            print(f"[ERROR] No player data found for slate {dg_id}.")
            input("\nPress Enter to continue...")
            return False
        
        # Prepare output data
        output_data = {
            "metadata": {
                "sport": sport,
                "dg_id": dg_id,
                "game_type": slate['game_type'],
                "start_time_display": slate['start_time_display'],
                "start_time_timestamp": slate['start_time_timestamp'],
                "game_count": slate['game_count'],
                "exported_at": datetime.now().isoformat(),
                "total_players": len(players)
            },
            "players": players
        }
        
        # Generate filename with sport, dg_id, and timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{sport}_{dg_id}_{timestamp}.json"
        filepath = os.path.join(DATA_DIR, filename)
        
        # Write to file
        with open(filepath, 'w') as f:
            json.dump(output_data, f, indent=2)
        
        print(f"\n[OK] Successfully exported {len(players)} players to:")
        print(f"     {filepath}")
        
        # Display summary
        print(f"\nExport Summary:")
        print(f"  Sport: {sport}")
        print(f"  Game Type: {slate['game_type']}")
        print(f"  Start Time: {slate['start_time_display']}")
        print(f"  Start Time (ISO): {slate['start_time_timestamp']}")
        print(f"  Games on Slate: {slate['game_count']}")
        print(f"  Total Players: {len(players)}")
        print(f"  File Size: {os.path.getsize(filepath) / 1024:.1f} KB")
        
        input("\nPress Enter to return to menu...")
        return True
        
    except Exception as e:
        logger.error(f"Error exporting player data: {e}")
        print(f"\n[ERROR] Error exporting data: {e}")
        input("\nPress Enter to return to menu...")
        return False


def main_menu():
    """Display main menu and handle navigation"""
    while True:
        clear_screen()
        display_header("DFS POOLS - PLAYER POOL EXPORTER")
        
        print("This tool allows you to:")
        print("  1. Browse available DFS contests (slates) by sport")
        print("  2. Select a specific slate")
        print("  3. Export the full player pool to JSON")
        print("\n(Data is pulled from the pre-populated database)\n")
        
        print("Options:\n")
        print("  1. Browse and Export Player Pool")
        print("  0. Exit\n")
        
        choice = input("Select option (enter number): ").strip()
        
        if choice == "0":
            print("\n[OK] Goodbye!\n")
            break
        elif choice == "1":
            # Sport selection loop
            while True:
                sport = select_sport()
                if sport is None:
                    break
                
                # Slate selection loop
                while True:
                    slate = select_slate(sport)
                    if slate is None:
                        break
                    
                    # Export
                    clear_screen()
                    display_header(f"EXPORTING DATA - {sport} (Slate {slate['dg_id']})")
                    export_player_data(sport, slate)
        else:
            print("[ERROR] Invalid option. Please try again.")
            input("\nPress Enter to continue...")


if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print("\n\n[INTERRUPTED] Interrupted by user.")
    except Exception as e:
        logger.error(f"CLI error: {e}")
        print(f"\n[ERROR] Error: {e}")
