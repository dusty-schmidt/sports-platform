"""
Dynamic tournament/sport discovery system for handling sports with changing league IDs.
This addresses sports like tennis, golf, MMA where tournament IDs change daily.
"""

import json
import logging
import os
from typing import Any, Dict, List, Optional, Set
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class DynamicTournamentManager:
    """Manages dynamic discovery of tournament/sport IDs that change daily."""
    
    def __init__(self, cache_file: str = "tournament_cache.json"):
        self.cache_file = cache_file
        self.cache = self._load_cache()
        self.session = None

    def _load_cache(self) -> Dict[str, Any]:
        """Load cached tournament data."""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r') as f:
                    cache = json.load(f)
                    logger.info(f"Loaded tournament cache from {self.cache_file}")
                    return cache
        except Exception as e:
            logger.warning(f"Failed to load tournament cache: {e}")
        return {}

    def _save_cache(self) -> None:
        """Save tournament data to cache."""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(self.cache, f, indent=2, default=str)
            logger.info(f"Saved tournament cache to {self.cache_file}")
        except Exception as e:
            logger.error(f"Failed to save tournament cache: {e}")

    def _is_cache_valid(self, sport: str) -> bool:
        """Check if cache is still valid for a sport."""
        cache_entry = self.cache.get(sport)
        if not cache_entry:
            return False
        
        cached_time = cache_entry.get("timestamp")
        if not cached_time:
            return False
        
        try:
            # Cache is valid for 4 hours
            cached_datetime = datetime.fromisoformat(cached_time)
            return datetime.now() - cached_datetime < timedelta(hours=4)
        except:
            return False

    def discover_tournaments(self, base_url: str, session) -> Dict[str, List[Dict[str, Any]]]:
        """Discover all currently available tournaments/sports."""
        if not self.session:
            self.session = session
        
        # Get manifest data
        try:
            url = f"{base_url}/sites/US-OH-SB/api/sportslayout/v1/manifest?format=json"
            logger.info(f"Discovering tournaments from: {url}")
            
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            tournaments = {}
            
            logger.info(f"Manifest response structure: {data.keys() if isinstance(data, dict) else 'Not a dict'}")
            
            # Check different possible response structures
            sports_data = None
            if isinstance(data, dict):
                # Try different possible keys
                for key in ["sports", "data", "manifest", "content", "categories"]:
                    if key in data:
                        sports_data = data[key]
                        logger.info(f"Found sports data in key: {key}")
                        break
            
            if not sports_data:
                # If no structured data, log the response structure
                logger.warning("No clear sports data structure found in manifest")
                logger.info(f"Available keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                return {}
            
            # Parse sports and their leagues
            for sport_data in sports_data:
                if not isinstance(sport_data, dict):
                    continue
                    
                sport_name = sport_data.get("name", "").lower()
                leagues = sport_data.get("leagues", sport_data.get("categories", []))
                
                # Focus on sports with dynamic tournaments
                dynamic_sports = ["tennis", "golf", "mma", "boxing", "motorsports"]
                
                for league in leagues:
                    if not isinstance(league, dict):
                        continue
                        
                    league_name = league.get("name", "").lower()
                    league_id = str(league.get("id", ""))
                    
                    if any(sport in sport_name for sport in dynamic_sports):
                        if sport_name not in tournaments:
                            tournaments[sport_name] = []
                        
                        tournament_info = {
                            "name": league.get("name", ""),
                            "id": league_id,
                            "url": league.get("url"),
                            "sport_category": sport_name
                        }
                        tournaments[sport_name].append(tournament_info)
                        logger.info(f"Discovered tournament: {league.get('name')} (ID: {league_id}) for {sport_name}")
            
            # Also check for any sports mentioned in the full data
            if not tournaments:
                logger.info("No dynamic sports found, checking all sports for debugging...")
                for sport_data in sports_data:
                    if isinstance(sport_data, dict):
                        sport_name = sport_data.get("name", "")
                        leagues_count = len(sport_data.get("leagues", sport_data.get("categories", [])))
                        logger.info(f"  {sport_name}: {leagues_count} leagues")
            
            return tournaments
            
        except Exception as e:
            logger.error(f"Error discovering tournaments: {e}")
            return {}

    def get_tournament_for_sport(self, sport: str, base_url: str, session) -> Optional[Dict[str, Any]]:
        """Get the best available tournament ID for a given sport."""
        sport = sport.lower()
        
        # Check if we have valid cached data
        if self._is_cache_valid(sport):
            cached_tournaments = self.cache[sport].get("tournaments", [])
            if cached_tournaments:
                tournament = cached_tournaments[0]  # Use the first (most relevant) tournament
                logger.info(f"Using cached tournament for {sport}: {tournament['name']} (ID: {tournament['id']})")
                return tournament
        
        # Discover new tournaments
        tournaments = self.discover_tournaments(base_url, session)
        
        # Update cache
        self.cache[sport] = {
            "tournaments": tournaments.get(sport, []),
            "timestamp": datetime.now().isoformat(),
            "all_sports": tournaments
        }
        self._save_cache()
        
        # Return the best tournament for this sport
        available_tournaments = tournaments.get(sport, [])
        if available_tournaments:
            # Prioritize major tournaments
            major_tournaments = self._prioritize_tournaments(available_tournaments)
            selected = major_tournaments[0] if major_tournaments else available_tournaments[0]
            logger.info(f"Selected tournament for {sport}: {selected['name']} (ID: {selected['id']})")
            return selected
        
        logger.warning(f"No tournaments found for sport: {sport}")
        return None

    def _prioritize_tournaments(self, tournaments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Prioritize tournaments by importance."""
        # Major tournament keywords for each sport
        priorities = {
            "tennis": ["grand slam", "masters", "wta", "atp", "us open", "wimbledon", "australian open", "french open", "rolland garros"],
            "golf": ["major", "pga", "masters", "us open", "british open", "pga championship", "players", "ryder cup", "solheim cup"],
            "mma": ["ufc", "bellator", "one championship", "pfl"],
            "boxing": ["wbc", "wba", "wbo", "ibf", "title"],
            "motorsports": ["formula 1", "nascar", "indycar", "motogp"]
        }
        
        # Sort by priority
        def get_priority(tournament):
            name = tournament["name"].lower()
            for priority_list in priorities.values():
                for keyword in priority_list:
                    if keyword in name:
                        return 0  # High priority
            return 1  # Default priority
        
        return sorted(tournaments, key=get_priority)

    def get_all_cached_sports(self) -> Dict[str, Any]:
        """Get all cached sports data."""
        return self.cache

    def clear_cache(self) -> None:
        """Clear the tournament cache."""
        self.cache = {}
        try:
            if os.path.exists(self.cache_file):
                os.remove(self.cache_file)
            logger.info("Cleared tournament cache")
        except Exception as e:
            logger.error(f"Failed to clear cache: {e}")


# Global tournament manager instance
tournament_manager = DynamicTournamentManager()


def get_dynamic_tournament_id(sport: str, base_url: str, session) -> Optional[str]:
    """Get tournament ID for a sport, discovering it dynamically if needed."""
    tournament = tournament_manager.get_tournament_for_sport(sport, base_url, session)
    return tournament["id"] if tournament else None


def discover_all_sports(base_url: str, session) -> Dict[str, List[Dict[str, Any]]]:
    """Discover all available sports and their tournaments."""
    return tournament_manager.discover_tournaments(base_url, session)


def print_available_sports() -> None:
    """Print all currently available sports from cache."""
    cache = tournament_manager.get_all_cached_sports()
    print("\n=== Available Sports in Cache ===")
    for sport, data in cache.items():
        tournaments = data.get("tournaments", [])
        timestamp = data.get("timestamp", "Unknown")
        print(f"\n{sport.upper()} (cached: {timestamp})")
        for tournament in tournaments:
            print(f"  - {tournament['name']} (ID: {tournament['id']})")
    print("\n" + "="*50)