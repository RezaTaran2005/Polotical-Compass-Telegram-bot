from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from config import QUESTIONS_FILE

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Question:

    id: int
    text: str
    axis: str       # "x" (economic) | "y" (social)
    units: int      # weight of the question
    direction: int  # +1 or -1


# Module-level cache so questions are parsed only once.
_questions_cache: Optional[list[Question]] = None


def load_questions() -> list[Question]:
    global _questions_cache

    if _questions_cache is not None:
        return _questions_cache

    path = Path(QUESTIONS_FILE)
    if not path.exists():
        raise FileNotFoundError(f"Questions file not found: {path}")

    with path.open(encoding="utf-8") as fh:
        raw: list[dict] = json.load(fh)

    validated: list[Question] = []
    for item in raw:
        _validate_question(item)
        validated.append(
            Question(
                id=item["id"],
                text=item["text"],
                axis=item["axis"],
                units=int(item["units"]),
                direction=int(item["direction"]),
            )
        )

    _questions_cache = validated
    logger.info("Loaded %d questions from %s", len(validated), path)
    return validated


def _validate_question(item: dict) -> None:
    required_keys = {"id", "text", "axis", "units", "direction"}
    missing = required_keys - item.keys()
    if missing:
        raise ValueError(f"Question {item.get('id', '?')} is missing keys: {missing}")

    if item["axis"] not in ("x", "y"):
        raise ValueError(
            f"Question {item['id']}: axis must be 'x' or 'y', got '{item['axis']}'"
        )

    if int(item["direction"]) not in (1, -1):
        raise ValueError(
            f"Question {item['id']}: direction must be 1 or -1, got '{item['direction']}'"
        )

    if int(item["units"]) <= 0:
        raise ValueError(
            f"Question {item['id']}: units must be a positive integer, got '{item['units']}'"
        )
