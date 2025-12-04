-- Database Schema for Multi-Sport Stats Collection (SQLite Compatible)

-- 1. Sports Table
CREATE TABLE sports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 2. Leagues Table
CREATE TABLE leagues (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sport_id INTEGER REFERENCES sports(id),
    name TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(sport_id, name)
);

-- 3. Players Table (The "Master" Record)
-- ID Strategy: Manual assignment based on sport range (e.g., Tennis = 100000+)
CREATE TABLE players (
    id INTEGER PRIMARY KEY, -- No AUTOINCREMENT, we will assign IDs manually for structure
    league_id INTEGER REFERENCES leagues(id),
    canonical_name TEXT NOT NULL,
    slug TEXT,
    
    -- Common fields
    birth_date TEXT, -- SQLite stores dates as TEXT (ISO8601 strings)
    country_code TEXT,
    
    -- Flexible metadata (Stored as JSON string)
    metadata TEXT DEFAULT '{}',
    
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(league_id, canonical_name)
);

-- 4. Player Aliases Table
CREATE TABLE player_aliases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    player_id INTEGER REFERENCES players(id) ON DELETE CASCADE,
    alias_name TEXT NOT NULL,
    source TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(player_id, alias_name)
);

-- 5. Player Stats Table
CREATE TABLE player_stats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    player_id INTEGER REFERENCES players(id),
    
    season TEXT,
    category TEXT,
    source_url TEXT,
    
    -- JSON payload stored as TEXT
    data TEXT NOT NULL,
    
    collected_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
