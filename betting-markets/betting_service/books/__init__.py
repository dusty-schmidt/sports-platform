"""Sportsbook client registry."""

from __future__ import annotations

from typing import Type

from .base import SportsbookClient
from .draftkings import DraftKingsClient
from .fanduel import FanDuelClient

CLIENT_REGISTRY: dict[str, Type[SportsbookClient]] = {
    "draftkings": DraftKingsClient,
    "fanduel": FanDuelClient,
}

__all__ = ["CLIENT_REGISTRY", "SportsbookClient", "DraftKingsClient", "FanDuelClient"]
