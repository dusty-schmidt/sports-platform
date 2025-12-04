"""Base classes and helpers for sportsbook integrations."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterable
import string

from ..models import MarketEvent


class SportsbookClient(ABC):
    """Abstract base client to fetch and transform betting market data."""

    def __init__(self, sport: str, *, team_aliases: dict[str, str], timezone: str) -> None:
        self.sport = sport.lower()
        self.team_aliases = {normalize_name(k): v for k, v in team_aliases.items()}
        self.timezone = timezone

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the display name of the sportsbook."""

    @abstractmethod
    def fetch(self) -> dict:
        """Fetch raw data from the sportsbook API."""

    @abstractmethod
    def transform(self, payload: dict) -> Iterable[MarketEvent]:
        """Transform a payload into a sequence of MarketEvent objects."""

    def get_events(self) -> list[MarketEvent]:
        """Fetch and transform data in a single step."""

        payload = self.fetch()
        return list(self.transform(payload))

    def alias_team(self, name: str) -> str:
        """Normalise and alias a team name if a mapping exists."""

        norm = normalize_name(name)
        return self.team_aliases.get(norm, name)


_TRANSLATOR = str.maketrans('', '', string.punctuation)


def normalize_name(value: str) -> str:
    return value.lower().translate(_TRANSLATOR).strip()


__all__ = ["SportsbookClient", "normalize_name"]
