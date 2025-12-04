"""Service orchestrating multi-book betting market collection."""

from __future__ import annotations

import logging
from dataclasses import asdict
from datetime import datetime
from typing import Iterable, Sequence

from .books import CLIENT_REGISTRY, SportsbookClient
from .config.sports import BookConfig, SportConfig, get_sport_config
from .models import MarketEvent

LOGGER = logging.getLogger(__name__)


class BettingMarketService:
    """Collects betting market data across sports and sportsbooks."""

    def __init__(
        self,
        sport: str,
        *,
        books: Sequence[str] | None = None,
    ) -> None:
        self.sport_config: SportConfig = get_sport_config(sport)
        self.book_configs: dict[str, BookConfig] = self._select_books(books)

    def _select_books(self, books: Sequence[str] | None) -> dict[str, BookConfig]:
        available = {name.lower(): config for name, config in self.sport_config.books.items()}
        if not books:
            return available

        selected: dict[str, BookConfig] = {}
        for book in books:
            key = book.lower()
            if key not in available:
                raise ValueError(f"Book '{book}' unsupported for sport {self.sport_config.name}")
            selected[key] = available[key]
        return selected

    def _build_client(self, name: str, config: BookConfig) -> SportsbookClient:
        try:
            client_cls = CLIENT_REGISTRY[name]
        except KeyError as exc:
            raise ValueError(f"No client registered for '{name}'") from exc

        return client_cls(
            self.sport_config.name,
            team_aliases=self.sport_config.team_aliases,
            timezone=self.sport_config.timezone,
            **config.options,
        )

    def collect(self) -> list[MarketEvent]:
        """Collect events from configured sportsbooks."""

        events: list[MarketEvent] = []
        for name, config in self.book_configs.items():
            client = self._build_client(name, config)
            LOGGER.info("Fetching markets from %s", client.name)
            try:
                events.extend(client.get_events())
            except Exception as exc:  # noqa: BLE001
                LOGGER.exception("Failed to fetch %s: %s", client.name, exc)
        LOGGER.info("Collected %d events", len(events))
        return events


def to_serialisable(event: MarketEvent) -> dict:
    """Convert MarketEvent to JSON serialisable dict."""

    data = asdict(event)
    for key, value in list(data.items()):
        if isinstance(value, datetime):
            data[key] = value.isoformat()
    return data


def serialise_events(events: Iterable[MarketEvent]) -> list[dict]:
    return [to_serialisable(event) for event in events]


__all__ = ["BettingMarketService", "serialise_events", "to_serialisable"]
