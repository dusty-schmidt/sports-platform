from flask import Flask, jsonify, request
from src.db_manager import DatabaseManager
from src.pool_scheduler import pool_scheduler
from src.logger import get_logger, setup_logging
import json
from datetime import datetime
import os

setup_logging()
logger = get_logger(__name__)

app = Flask(__name__)
db = DatabaseManager()

# Get scheduling configuration from environment
SCHEDULER_ENABLED = os.getenv('SCHEDULER_ENABLED', 'True') == 'True'
SCHEDULER_INTERVAL_HOURS = int(os.getenv('SCHEDULER_INTERVAL_HOURS', '4'))

def parse_start_time(start_time_str):
    """Parse common DraftKings start time format (e.g., 'Sun 1:00PM')."""
    try:
        return datetime.strptime(start_time_str, '%a %I:%M%p')
    except:
        return None

def get_draftgroup_status(start_time_str):
    """Determine if a draftgroup is 'upcoming' or 'started' based on start_time."""
    parsed_time = parse_start_time(start_time_str)
    if parsed_time is None:
        return "upcoming"  # Default to upcoming if we can't parse
    
    now = datetime.now()
    return "upcoming" if parsed_time.time() > now.time() else "started"

def extract_optimizer_view(draftables_data):
    """Extract only the fields needed for a lineup optimizer from raw draftables data."""
    if not draftables_data or 'draftables' not in draftables_data:
        return []
    
    optimized = []
    for player in draftables_data.get('draftables', []):
        optimized.append({
            'playerId': player.get('playerId'),
            'displayName': player.get('displayName'),
            'salary': player.get('salary'),
            'teamAbbreviation': player.get('teamAbbreviation'),
            'position': player.get('position'),
            'nbaPlayerMoneyLine': player.get('nbaPlayerMoneyLine'),
            'tier': player.get('tier'),
            'rosterSlotId': player.get('rosterSlotId')
        })
    
    return optimized

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({"status": "healthy"}), 200

@app.route('/api/sports', methods=['GET'])
def get_sports():
    """Get all sports with detailed draftgroups and slate metadata."""
    try:
        draftgroups = db.get_all_draftgroups()
        sports_data = {}
        
        for dg in draftgroups:
            sport = dg['sport']
            if sport not in sports_data:
                sports_data[sport] = {
                    'sport': sport,
                    'classic_slates': [],
                    'showdown_slates': [],
                    'classic_count': 0,
                    'showdown_count': 0
                }
            
            # Build slate info
            slate_info = {
                'dg_id': dg['dg_id'],
                'game_type': dg['game_type'],
                'start_time': dg['start_time'],
                'teams': json.loads(dg['teams']) if dg['teams'] else None
            }
            
            # Count draftables/players for this draftgroup
            draftables = db.get_draftables(dg['dg_id'])
            slate_info['players_count'] = len(draftables.get('draftables', [])) if draftables else 0
            
            # Organize by game type
            if dg['game_type'] == 'Classic':
                sports_data[sport]['classic_slates'].append(slate_info)
                sports_data[sport]['classic_count'] += 1
            elif 'Showdown' in dg['game_type'] or 'Captain' in dg['game_type']:
                sports_data[sport]['showdown_slates'].append(slate_info)
                sports_data[sport]['showdown_count'] += 1
        
        # Sort slates by start time and convert to array format
        sports_list = []
        for sport in sorted(sports_data.keys()):
            sport_obj = sports_data[sport]
            sport_obj['classic_slates'].sort(key=lambda x: x['start_time'])
            sport_obj['showdown_slates'].sort(key=lambda x: x['start_time'])
            sports_list.append(sport_obj)
        
        return jsonify({
            "total_sports": len(sports_list),
            "sports": sports_list
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/draftgroups', methods=['GET'])
def get_draftgroups():
    """Get all draftgroups, optionally filtered by sport."""
    try:
        sport = request.args.get('sport', None)
        draftgroups = db.get_all_draftgroups(sport=sport)
        
        result = []
        for dg in draftgroups:
            dg_dict = dict(dg)
            if dg_dict['teams']:
                dg_dict['teams'] = json.loads(dg_dict['teams'])
            dg_dict['status'] = get_draftgroup_status(dg['start_time'])
            result.append(dg_dict)
        
        return jsonify({
            "count": len(result),
            "draftgroups": result
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/draftgroups/<int:dg_id>', methods=['GET'])
def get_draftgroup(dg_id):
    """Get a specific draftgroup by ID."""
    try:
        draftgroup = db.get_draftgroup(dg_id)
        if not draftgroup:
            return jsonify({"error": "Draftgroup not found"}), 404
        
        dg_dict = dict(draftgroup)
        if dg_dict['teams']:
            dg_dict['teams'] = json.loads(dg_dict['teams'])
        dg_dict['status'] = get_draftgroup_status(draftgroup['start_time'])
        
        return jsonify(dg_dict), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/draftgroups/<int:dg_id>/draftables', methods=['GET'])
def get_draftables(dg_id):
    """Get draftables data for a specific draftgroup."""
    try:
        draftgroup = db.get_draftgroup(dg_id)
        if not draftgroup:
            return jsonify({"error": "Draftgroup not found"}), 404
        
        draftables = db.get_draftables(dg_id)
        if not draftables:
            return jsonify({"error": "Draftables not yet fetched for this draftgroup"}), 404
        
        return jsonify({
            "dg_id": dg_id,
            "sport": draftgroup['sport'],
            "draftables_count": len(draftables.get('draftables', [])),
            "draftables": draftables
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/sports/<sport>/draftgroups', methods=['GET'])
def get_sport_draftgroups(sport):
    """Get all draftgroups for a specific sport."""
    try:
        draftgroups = db.get_all_draftgroups(sport=sport)
        if not draftgroups:
            return jsonify({"error": f"No draftgroups found for sport: {sport}"}), 404
        
        result = []
        for dg in draftgroups:
            dg_dict = dict(dg)
            if dg_dict['teams']:
                dg_dict['teams'] = json.loads(dg_dict['teams'])
            dg_dict['status'] = get_draftgroup_status(dg['start_time'])
            result.append(dg_dict)
        
        return jsonify({
            "sport": sport,
            "count": len(result),
            "draftgroups": result
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/sports/<sport>/draftables', methods=['GET'])
def get_sport_draftables(sport):
    """Get all draftables for a specific sport."""
    try:
        draftables_by_dg = db.get_draftables_by_sport(sport)
        if not draftables_by_dg:
            return jsonify({"error": f"No draftables found for sport: {sport}"}), 404
        
        return jsonify({
            "sport": sport,
            "draftgroup_count": len(draftables_by_dg),
            "draftables_by_draftgroup": draftables_by_dg
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/sports/<sport>/slates', methods=['GET'])
def get_sport_slates(sport):
    """Get all slates (draftgroups) for a specific sport with simplified metadata for UI dropdown."""
    try:
        draftgroups = db.get_all_draftgroups(sport=sport)
        if not draftgroups:
            return jsonify({"error": f"No slates found for sport: {sport}"}), 404
        
        slates = []
        for dg in draftgroups:
            # Parse teams to get team count
            teams = json.loads(dg['teams']) if dg['teams'] else []
            team_count = len(teams)
            game_count = team_count // 2 if team_count > 0 else 0
            
            # Build label: "game_type - start_time - N games"
            label = f"{dg['game_type']} - {dg['start_time']} - {game_count} games"
            
            slate_info = {
                'dg_id': dg['dg_id'],
                'label': label,
                'team_count': team_count
            }
            slates.append(slate_info)
        
        # Sort by start_time (assuming chronological order in label)
        return jsonify({
            "sport": sport,
            "count": len(slates),
            "slates": slates
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/sports/<sport>/slates/<int:dg_id>/players', methods=['GET'])
def get_slate_players(sport, dg_id):
    """Get all players for a specific slate with all roster slot variants preserved."""
    try:
        # Verify draftgroup exists and belongs to this sport
        draftgroup = db.get_draftgroup(dg_id)
        if not draftgroup:
            return jsonify({"error": "Slate not found"}), 404
        
        if draftgroup['sport'] != sport:
            return jsonify({"error": f"Slate {dg_id} does not belong to sport {sport}"}), 404
        
        # Get parsed draftables for this slate
        players = db.get_draftables_parsed(dg_id)
        if not players:
            return jsonify({"error": "Players not yet fetched for this slate"}), 404
        
        return jsonify({
            "dg_id": dg_id,
            "sport": sport,
            "game_type": draftgroup['game_type'],
            "start_time": draftgroup['start_time'],
            "players_count": len(players),
            "players": players
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500



@app.route('/api/draftgroups/<int:dg_id>/draftables/optimizer_view', methods=['GET'])
def get_draftables_optimizer_view(dg_id):
    """Get optimized draftables for lineup optimizer (essential fields only)."""
    try:
        draftgroup = db.get_draftgroup(dg_id)
        if not draftgroup:
            return jsonify({"error": "Draftgroup not found"}), 404
        
        draftables = db.get_draftables(dg_id)
        if not draftables:
            return jsonify({"error": "Draftables not yet fetched for this draftgroup"}), 404
        
        optimized = extract_optimizer_view(draftables)
        
        return jsonify({
            "dg_id": dg_id,
            "sport": draftgroup['sport'],
            "start_time": draftgroup['start_time'],
            "game_type": draftgroup['game_type'],
            "status": get_draftgroup_status(draftgroup['start_time']),
            "players_count": len(optimized),
            "players": optimized
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/draftgroups/active', methods=['GET'])
def get_active_draftgroups():
    """Get currently active draftgroups (games haven't started yet)."""
    try:
        all_draftgroups = db.get_all_draftgroups()
        if not all_draftgroups:
            return jsonify({"error": "No draftgroups found"}), 404
        
        now = datetime.now()
        active_draftgroups = []
        
        for dg in all_draftgroups:
            # Parse start time - format is "Day HH:MMAM/PM" (e.g., "Sun 1:00PM")
            start_time_str = dg['start_time']
            
            # Try to parse the start time
            parsed_time = parse_start_time(start_time_str)
            
            # If parsing failed, consider it as active (safer approach)
            if parsed_time is None:
                is_active = True
            else:
                # Check if game hasn't started yet (parsed time > now)
                # Note: This is a simplified check since we don't have the date
                # In production, you'd want to track the actual date with start_time
                is_active = parsed_time.time() > now.time()
            
            if is_active:
                dg_dict = dict(dg)
                if dg_dict['teams']:
                    dg_dict['teams'] = json.loads(dg_dict['teams'])
                dg_dict['status'] = get_draftgroup_status(dg['start_time'])
                
                # Try to fetch draftables for this draftgroup
                draftables = db.get_draftables(dg['dg_id'])
                if draftables:
                    optimized_players = extract_optimizer_view(draftables)
                    dg_dict['players_count'] = len(optimized_players)
                    dg_dict['sample_players'] = optimized_players[:5]  # First 5 players as sample
                else:
                    dg_dict['players_count'] = 0
                    dg_dict['sample_players'] = []
                
                active_draftgroups.append(dg_dict)
        
        return jsonify({
            "timestamp": now.isoformat(),
            "active_count": len(active_draftgroups),
            "active_draftgroups": active_draftgroups
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/draftgroups/active/optimizer', methods=['GET'])
def get_active_draftgroups_optimizer():
    """Get currently active draftgroups with optimized player data for lineup optimizer."""
    try:
        all_draftgroups = db.get_all_draftgroups()
        if not all_draftgroups:
            return jsonify({"error": "No draftgroups found"}), 404
        
        now = datetime.now()
        active_draftgroups = []
        
        for dg in all_draftgroups:
            start_time_str = dg['start_time']
            parsed_time = parse_start_time(start_time_str)
            
            if parsed_time is None:
                is_active = True
            else:
                is_active = parsed_time.time() > now.time()
            
            if is_active:
                draftables = db.get_draftables(dg['dg_id'])
                if draftables:
                    dg_dict = {
                        'dg_id': dg['dg_id'],
                        'sport': dg['sport'],
                        'start_time': dg['start_time'],
                        'game_type': dg['game_type'],
                        'status': get_draftgroup_status(dg['start_time']),
                        'teams': json.loads(dg['teams']) if dg['teams'] else None,
                        'players': extract_optimizer_view(draftables)
                    }
                    active_draftgroups.append(dg_dict)
        
        return jsonify({
            "timestamp": now.isoformat(),
            "active_count": len(active_draftgroups),
            "draftgroups": active_draftgroups
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/scheduler/status', methods=['GET'])
def scheduler_status():
    """Get scheduler status and configuration."""
    return jsonify({
        "scheduler_enabled": SCHEDULER_ENABLED,
        "is_running": pool_scheduler.is_running,
        "update_interval_hours": SCHEDULER_INTERVAL_HOURS
    }), 200

@app.route('/api/scheduler/trigger', methods=['POST'])
def trigger_data_ingestion():
    """Manually trigger data ingestion."""
    try:
        logger.info("Manual data ingestion triggered via API")
        pool_scheduler._run_data_ingestion()
        return jsonify({
            "status": "success",
            "message": "Data ingestion triggered successfully"
        }), 200
    except Exception as e:
        logger.error(f"Error during manual data ingestion: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.before_request
def startup_scheduler():
    """Start scheduler on first request if enabled."""
    if not hasattr(app, 'scheduler_initialized'):
        if SCHEDULER_ENABLED:
            try:
                pool_scheduler.start(update_interval_hours=SCHEDULER_INTERVAL_HOURS)
                logger.info("Data ingestion scheduler started automatically")
            except Exception as e:
                logger.warning(f"Could not start automatic scheduler: {e}")
        app.scheduler_initialized = True

def shutdown_scheduler():
    """Shutdown scheduler on application exit."""
    if pool_scheduler.is_running:
        pool_scheduler.stop()
        logger.info("Data ingestion scheduler stopped")

if __name__ == '__main__':
    try:
        app.run(debug=False, host='0.0.0.0', port=5000)
    finally:
        shutdown_scheduler()