"""Unit tests for sportsbook clients and service."""

from __future__ import annotations

from datetime import datetime

import pytest

from betting_service.books.draftkings import DraftKingsClient
from betting_service.books.fanduel import FanDuelClient
from betting_service.service import BettingMarketService, serialise_events
from betting_service.models import MarketEvent


def build_dk_client() -> DraftKingsClient:
    return DraftKingsClient(
        "NBA",
        league_id="TEST",
        team_aliases={"team a": "TA", "team b": "TB"},
        timezone="America/New_York",
    )


def build_fd_client() -> FanDuelClient:
    return FanDuelClient(
        "NBA",
        custom_page_id="nba",
        team_aliases={"team a": "TA", "team b": "TB"},
        timezone="America/New_York",
    )


def test_draftkings_transform_builds_market_event():
    client = build_dk_client()
    payload = {
        "events": [
            {
                "id": 1,
                "name": "Team A @ Team B",
                "startEventDate": "2025-01-01T00:00:00Z",
                "participants": [
                    {"venueRole": "AWAY", "name": "Team A"},
                    {"venueRole": "HOME", "name": "Team B"},
                ],
            }
        ],
        "markets": [
            {"id": "1_1", "eventId": 1},
            {"id": "2_1", "eventId": 1},
            {"id": "3_1", "eventId": 1},
        ],
        "selections": [
            {"marketId": "1_1", "label": "Team A", "displayOdds": {"american": "+110"}},
            {"marketId": "1_1", "label": "Team B", "displayOdds": {"american": "-130"}},
            {
                "marketId": "2_1",
                "label": "Team A",
                "points": -3.5,
                "displayOdds": {"american": "+100"},
            },
            {
                "marketId": "2_1",
                "label": "Team B",
                "points": 3.5,
                "displayOdds": {"american": "-110"},
            },
            {
                "marketId": "3_1",
                "outcomeType": "over",
                "points": 220.5,
                "displayOdds": {"american": "-105"},
            },
            {
                "marketId": "3_1",
                "outcomeType": "under",
                "points": 220.5,
                "displayOdds": {"american": "-115"},
            },
        ],
    }

    events = list(client.transform(payload))
    assert len(events) == 1
    event = events[0]
    assert event.away == "TA"
    assert event.home == "TB"
    assert event.away_moneyline == "+110"
    assert event.home_spread == pytest.approx(3.5)
    assert event.total == pytest.approx(220.5)


def test_fanduel_transform_builds_market_event():
    client = build_fd_client()
    payload = {
        "1": {
            "eventId": "1",
            "marketTime": "2025-01-01T00:00:00Z",
            "marketType": "MONEY_LINE",
            "runners": [
                {
                    "runnerName": "Team A",
                    "result": {"type": "AWAY"},
                    "winRunnerOdds": {"americanDisplayOdds": {"americanOdds": "+120"}},
                },
                {
                    "runnerName": "Team B",
                    "result": {"type": "HOME"},
                    "winRunnerOdds": {"americanDisplayOdds": {"americanOdds": "-140"}},
                },
            ],
        },
        "2": {
            "eventId": "1",
            "marketTime": "2025-01-01T00:00:00Z",
            "marketType": "MATCH_HANDICAP_(2-WAY)",
            "runners": [
                {
                    "runnerName": "Team A",
                    "result": {"type": "AWAY"},
                    "handicap": -4.5,
                    "winRunnerOdds": {"americanDisplayOdds": {"americanOdds": "+100"}},
                },
                {
                    "runnerName": "Team B",
                    "result": {"type": "HOME"},
                    "handicap": 4.5,
                    "winRunnerOdds": {"americanDisplayOdds": {"americanOdds": "-110"}},
                },
            ],
        },
        "3": {
            "eventId": "1",
            "marketTime": "2025-01-01T00:00:00Z",
            "marketType": "TOTAL_POINTS_(OVER/UNDER)",
            "runners": [
                {
                    "runnerName": "Over",
                    "handicap": 215.5,
                    "winRunnerOdds": {"americanDisplayOdds": {"americanOdds": "-105"}},
                },
                {
                    "runnerName": "Under",
                    "handicap": 215.5,
                    "winRunnerOdds": {"americanDisplayOdds": {"americanOdds": "-115"}},
                },
            ],
        },
    }

    events = list(client.transform(payload))
    assert len(events) == 1
    event = events[0]
    assert event.away == "TA"
    assert event.home == "TB"
    assert event.total == pytest.approx(215.5)
    assert event.away_moneyline == "+120"
    assert event.home_spread_price == "-110"


def test_serialise_events_converts_datetimes():
    event = MarketEvent(
        book="Test",
        sport="nba",
        game="Team A @ Team B",
        game_start=datetime(2025, 1, 1, 12, 0, 0),
        away="TA",
        home="TB",
        total=210.5,
        over_price="-110",
        under_price="-110",
        away_moneyline="+150",
        home_moneyline="-170",
        away_spread=-3.5,
        away_spread_price="-105",
        home_spread=3.5,
        home_spread_price="-115",
        retrieved_at=datetime(2025, 1, 1, 10, 0, 0),
    )

    serialised = serialise_events([event])
    assert serialised[0]["game_start"].startswith("2025-01-01")
    assert serialised[0]["retrieved_at"].startswith("2025-01-01")


def test_service_collect_uses_config(monkeypatch):
    service = BettingMarketService("nba", books=["draftkings"])

    class DummyClient:
        name = "DraftKings"

        def get_events(self):
            return [
                MarketEvent(
                    book="DraftKings",
                    sport="nba",
                    game="Team A @ Team B",
                    game_start=datetime(2025, 1, 1, 12, 0, 0),
                    away="TA",
                    home="TB",
                    total=None,
                    over_price=None,
                    under_price=None,
                    away_moneyline=None,
                    home_moneyline=None,
                    away_spread=None,
                    away_spread_price=None,
                    home_spread=None,
                    home_spread_price=None,
                    retrieved_at=datetime(2025, 1, 1, 9, 0, 0),
                )
            ]

    monkeypatch.setattr(service, "_build_client", lambda name, config: DummyClient())
    events = service.collect()
    assert len(events) == 1
    assert events[0].book == "DraftKings"
