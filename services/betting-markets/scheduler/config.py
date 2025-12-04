"""Scheduler configuration and settings."""

from __future__ import annotations

import os
from typing import Dict, List
from pydantic_settings import BaseSettings
from pydantic import Field


class SchedulerConfig(BaseSettings):
    """Configuration for the betting market data collection scheduler."""
    
    # Collection intervals (in minutes)
    nba_interval: int = Field(default=15, description="NBA data collection interval in minutes")
    nfl_interval: int = Field(default=15, description="NFL data collection interval in minutes")
    mlb_interval: int = Field(default=30, description="MLB data collection interval in minutes")
    nhl_interval: int = Field(default=20, description="NHL data collection interval in minutes")
    soccer_interval: int = Field(default=20, description="Soccer data collection interval in minutes")
    
    # Default collection interval for unspecified sports
    default_interval: int = Field(default=30, description="Default collection interval in minutes")
    
    # Sports to collect automatically
    auto_collect_sports: List[str] = Field(
        default=["nba", "nfl", "mlb", "nhl"],
        description="List of sports to automatically collect data for"
    )
    
    # Default sportsbooks for each sport
    default_sportsbooks: Dict[str, List[str]] = Field(
        default={
            "nba": ["draftkings", "fanduel"],
            "nfl": ["draftkings", "fanduel"],
            "mlb": ["draftkings", "fanduel"],
            "nhl": ["draftkings", "fanduel"],
            "soccer": ["draftkings", "fanduel"]
        },
        description="Default sportsbooks for each sport"
    )
    
    # Job management
    max_concurrent_jobs: int = Field(default=3, description="Maximum number of concurrent collection jobs")
    job_timeout_minutes: int = Field(default=10, description="Job timeout in minutes")
    retry_attempts: int = Field(default=2, description="Number of retry attempts for failed jobs")
    
    # Cleanup settings
    cleanup_interval_hours: int = Field(default=24, description="How often to run cleanup (in hours)")
    days_to_keep_snapshots: int = Field(default=7, description="Number of days to keep old snapshots")
    
    # API endpoints for manual triggers
    enable_manual_triggers: bool = Field(default=True, description="Enable manual trigger endpoints")
    
    class Config:
        env_prefix = "SCHEDULER_"
        case_sensitive = False


# Default configuration instance
config = SchedulerConfig()


# Sports-specific configuration
SPORTS_CONFIG = {
    "nba": {
        "interval_minutes": config.nba_interval,
        "books": config.default_sportsbooks.get("nba", ["draftkings", "fanduel"]),
        "active_hours": [(6, 23)],  # 6 AM to 11 PM
    },
    "nfl": {
        "interval_minutes": config.nfl_interval,
        "books": config.default_sportsbooks.get("nfl", ["draftkings", "fanduel"]),
        "active_hours": [(6, 23)],
    },
    "mlb": {
        "interval_minutes": config.mlb_interval,
        "books": config.default_sportsbooks.get("mlb", ["draftkings", "fanduel"]),
        "active_hours": [(10, 23)],  # 10 AM to 11 PM
    },
    "nhl": {
        "interval_minutes": config.nhl_interval,
        "books": config.default_sportsbooks.get("nhl", ["draftkings", "fanduel"]),
        "active_hours": [(6, 23)],
    },
    "soccer": {
        "interval_minutes": config.soccer_interval,
        "books": config.default_sportsbooks.get("soccer", ["draftkings", "fanduel"]),
        "active_hours": [(6, 23)],
    }
}


def get_sport_config(sport: str) -> Dict:
    """Get configuration for a specific sport."""
    return SPORTS_CONFIG.get(sport, {
        "interval_minutes": config.default_interval,
        "books": config.default_sportsbooks.get(sport, ["draftkings", "fanduel"]),
        "active_hours": [(0, 23)]  # 24/7 by default
    })