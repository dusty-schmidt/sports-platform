import sqlite3
import json
from contextlib import contextmanager

DB_PATH = "dfs_pools.db"

class DatabaseManager:
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        self.init_db()
    
    @contextmanager
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def init_db(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS draftgroups (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    dg_id INTEGER UNIQUE NOT NULL,
                    sport TEXT NOT NULL,
                    start_time TEXT,
                    game_type TEXT,
                    teams TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS draftables (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    dg_id INTEGER NOT NULL,
                    sport TEXT NOT NULL,
                    raw_data TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (dg_id) REFERENCES draftgroups(dg_id)
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sports_inventory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sport TEXT NOT NULL,
                    dg_id INTEGER NOT NULL,
                    game_type TEXT NOT NULL,
                    start_time_display TEXT NOT NULL,
                    start_time_timestamp TEXT NOT NULL,
                    game_count INTEGER NOT NULL,
                    player_count INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(sport, dg_id),
                    FOREIGN KEY (dg_id) REFERENCES draftgroups(dg_id)
                )
            ''')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_dg_id ON draftgroups(dg_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_sport ON draftgroups(sport)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_draftables_dg_id ON draftables(dg_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_draftables_sport ON draftables(sport)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_inventory_sport ON sports_inventory(sport)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_inventory_dg_id ON sports_inventory(dg_id)')
    
    def add_or_update_draftgroup(self, dg_id, sport, start_time, game_type, teams=None):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            teams_json = json.dumps(teams) if teams else None
            cursor.execute('''
                INSERT INTO draftgroups (dg_id, sport, start_time, game_type, teams)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(dg_id) DO UPDATE SET
                    start_time=excluded.start_time,
                    game_type=excluded.game_type,
                    teams=excluded.teams,
                    updated_at=CURRENT_TIMESTAMP
            ''', (dg_id, sport, start_time, game_type, teams_json))
    
    def draftgroup_exists(self, dg_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT 1 FROM draftgroups WHERE dg_id = ?', (dg_id,))
            return cursor.fetchone() is not None
    
    def add_draftables(self, dg_id, sport, raw_data):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            raw_data_json = json.dumps(raw_data)
            cursor.execute('DELETE FROM draftables WHERE dg_id = ?', (dg_id,))
            cursor.execute('''
                INSERT INTO draftables (dg_id, sport, raw_data)
                VALUES (?, ?, ?)
            ''', (dg_id, sport, raw_data_json))
    
    def get_draftgroup(self, dg_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM draftgroups WHERE dg_id = ?', (dg_id,))
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None
    
    def get_all_draftgroups(self, sport=None):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if sport:
                cursor.execute('SELECT * FROM draftgroups WHERE sport = ? ORDER BY created_at DESC', (sport,))
            else:
                cursor.execute('SELECT * FROM draftgroups ORDER BY sport, created_at DESC')
            return [dict(row) for row in cursor.fetchall()]
    
    def get_draftables(self, dg_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT raw_data FROM draftables WHERE dg_id = ?', (dg_id,))
            row = cursor.fetchone()
            if row:
                return json.loads(row['raw_data'])
            return None
    
    def get_draftables_by_sport(self, sport):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT dg_id, raw_data FROM draftables WHERE sport = ? ORDER BY created_at DESC', (sport,))
            return {row['dg_id']: json.loads(row['raw_data']) for row in cursor.fetchall()}
    
    def get_draftables_parsed(self, dg_id, fields=None):
        """
        Get draftables for a specific draftgroup with parsed player fields.
        
        Args:
            dg_id: Draftgroup ID
            fields: List of specific fields to extract from each player.
                   If None, returns all fields from draftables array.
        
        Returns:
            List of parsed player objects with requested fields
        """
        draftables_data = self.get_draftables(dg_id)
        if not draftables_data or 'draftables' not in draftables_data:
            return []
        
        players = []
        for player in draftables_data.get('draftables', []):
            if fields:
                # Extract only requested fields
                parsed_player = {field: player.get(field) for field in fields}
            else:
                # Return all fields
                parsed_player = player
            players.append(parsed_player)
        
        return players
    
    def update_sports_inventory(self):
        """
        Update the sports_inventory table with all available sports and slates that have player data.
        Calculates game count from unique competition IDs and parses actual start times from player data.
        Called after draftables are fetched.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get all draftgroups with corresponding draftables
            cursor.execute('''
                SELECT dg.dg_id, dg.sport, dg.game_type, dg.start_time, da.raw_data
                FROM draftgroups dg
                INNER JOIN draftables da ON dg.dg_id = da.dg_id
                ORDER BY dg.sport, dg.created_at DESC
            ''')
            
            rows = cursor.fetchall()
            
            for row in rows:
                dg_id = row['dg_id']
                sport = row['sport']
                game_type = row['game_type']
                start_time_display = row['start_time']
                
                # Parse raw_data to get competition IDs, player count, and actual start time
                try:
                    raw_data = json.loads(row['raw_data'])
                    draftables_list = raw_data.get('draftables', [])
                    
                    if not draftables_list:
                        continue
                    
                    # Get unique competition IDs to determine game count
                    competition_ids = set()
                    start_time_timestamp = None
                    
                    for player in draftables_list:
                        # Extract competition ID
                        if 'competition' in player and 'competitionId' in player['competition']:
                            competition_ids.add(player['competition']['competitionId'])
                        
                        # Extract actual start time from first player's competition data
                        if not start_time_timestamp and 'competition' in player and 'startTime' in player['competition']:
                            start_time_timestamp = player['competition']['startTime']
                    
                    game_count = len(competition_ids)
                    player_count = len(draftables_list)
                    
                    # Use extracted timestamp or fallback to display format
                    if not start_time_timestamp:
                        start_time_timestamp = start_time_display
                    
                    # Insert or update in sports_inventory
                    cursor.execute('''
                        INSERT INTO sports_inventory (sport, dg_id, game_type, start_time_display, start_time_timestamp, game_count, player_count, created_at, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                        ON CONFLICT(sport, dg_id) DO UPDATE SET
                            game_type=excluded.game_type,
                            start_time_display=excluded.start_time_display,
                            start_time_timestamp=excluded.start_time_timestamp,
                            game_count=excluded.game_count,
                            player_count=excluded.player_count,
                            updated_at=CURRENT_TIMESTAMP
                    ''', (sport, dg_id, game_type, start_time_display, start_time_timestamp, game_count, player_count))
                
                except (json.JSONDecodeError, KeyError, TypeError) as e:
                    # Skip entries with malformed data
                    continue
    
    def get_available_sports(self):
        """
        Get all sports with available player pools from sports_inventory.
        Returns list of dicts with sport and metadata about available slates.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT sport, COUNT(*) as slate_count
                FROM sports_inventory
                GROUP BY sport
                ORDER BY sport
            ''')
            return [dict(row) for row in cursor.fetchall()]
    
    def get_available_slates(self, sport):
        """
        Get all available slates for a sport from sports_inventory.
        Only returns slates that have player data.
        
        Returns list of dicts with: sport, dg_id, game_type, start_time_display, start_time_timestamp, game_count, player_count
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT sport, dg_id, game_type, start_time_display, start_time_timestamp, game_count, player_count
                FROM sports_inventory
                WHERE sport = ?
                ORDER BY start_time_timestamp DESC
            ''', (sport,))
            return [dict(row) for row in cursor.fetchall()]
    
    def get_new_draftgroups(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT dg.* FROM draftgroups dg
                LEFT JOIN draftables da ON dg.dg_id = da.dg_id
                WHERE da.dg_id IS NULL
            ''')
            return [dict(row) for row in cursor.fetchall()]