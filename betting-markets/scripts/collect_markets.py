"""Command-line entrypoint for betting market data collection."""

from __future__ import annotations

import argparse
import logging
from datetime import datetime

from betting_service.service import BettingMarketService, serialise_events
from betting_service.utils.storage import archive_files, save_json

DEFAULT_OUTPUT_DIR = "data"
DEFAULT_ARCHIVE_DIR = "data/previous"

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
LOGGER = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Collect betting market data from sportsbooks")
    parser.add_argument("sport", nargs="?", default="nba", help="Sport key to collect markets for (default: nba)")
    parser.add_argument(
        "--books",
        nargs="*",
        default=None,
        help="Optional list of sportsbook names to query (default: all for sport)",
    )
    parser.add_argument(
        "--output-dir",
        default=DEFAULT_OUTPUT_DIR,
        help=f"Directory to store output files (default: {DEFAULT_OUTPUT_DIR})",
    )
    parser.add_argument(
        "--archive-dir",
        default=DEFAULT_ARCHIVE_DIR,
        help=f"Directory to archive previous JSON files (default: {DEFAULT_ARCHIVE_DIR})",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    service = BettingMarketService(args.sport, books=args.books)
    events = service.collect()

    serialised = serialise_events(events)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{args.sport.lower()}_{timestamp}.json"
    target = save_json(serialised, directory=args.output_dir, filename=filename)

    archive_files(base_dir=args.output_dir, archive_dir=args.archive_dir, keep={target.name})


if __name__ == "__main__":  # pragma: no cover
    main()
