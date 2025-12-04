"""Data models for the betting market service."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(slots=True)
class MarketEvent:
    """Represents a single betting market event."""

    book: str
    sport: str
    game: str
    game_start: datetime
    away: str
    home: str
    total: Optional[float]
    over_price: Optional[str]
    under_price: Optional[str]
    away_moneyline: Optional[str]
    home_moneyline: Optional[str]
    away_spread: Optional[float]
    away_spread_price: Optional[str]
    home_spread: Optional[float]
    home_spread_price: Optional[str]
    retrieved_at: datetime


__all__ = ["MarketEvent"]
