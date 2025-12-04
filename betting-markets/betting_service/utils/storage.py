"""File storage helpers for betting market data."""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from shutil import move
from typing import Iterable

LOGGER = logging.getLogger(__name__)


def ensure_directory(path: str | os.PathLike) -> Path:
    directory = Path(path)
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def save_json(data: Iterable[dict], *, directory: str, filename: str) -> Path:
    ensure_directory(directory)
    target = Path(directory) / filename
    with target.open("w", encoding="utf-8") as fp:
        json.dump(list(data), fp, indent=2)
    LOGGER.info("Saved %s", target)
    return target


def archive_files(*, base_dir: str, archive_dir: str, keep: set[str]) -> None:
    base = ensure_directory(base_dir)
    archive = ensure_directory(archive_dir)
    for file in base.glob("*.json"):
        if file.name not in keep:
            move(file, archive / file.name)
            LOGGER.info("Archived %s", file.name)
