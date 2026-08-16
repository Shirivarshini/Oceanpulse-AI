"""
Generic data-source fallback resolver.

Implements the fallback chain required by CLAUDE.md's Reliability Rules and
API_CONTRACT.md section 13:

    LIVE -> CACHED -> HISTORICAL -> DEMO

This module only knows about priority and fallback mechanics. It has no
knowledge of oceanographic/fisheries/molecular data itself -- that lives in
connectors.py, which supplies the per-category tiers.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

# Step 1: source priority is defined once, here, and nowhere else.
SOURCE_PRIORITY = ["LIVE", "CACHED", "HISTORICAL", "DEMO"]


class SourceUnavailableError(Exception):
    """Raised by a tier's fetch() when that specific tier cannot supply data."""


class DataUnavailableError(Exception):
    """Raised when every tier in the priority chain is unavailable."""


@dataclass
class ConnectorTier:
    """One rung of the fallback ladder for a given data category."""
    name: str  # must be one of SOURCE_PRIORITY
    fetch: Callable[[], Any]

    def __post_init__(self) -> None:
        if self.name not in SOURCE_PRIORITY:
            raise ValueError(
                f"Unknown source tier '{self.name}', expected one of {SOURCE_PRIORITY}"
            )


@dataclass
class ResolvedSource:
    category: str
    status: str  # LIVE | CACHED | HISTORICAL | DEMO -- always the tier that actually succeeded
    data: Any


def resolve(category: str, tiers: list[ConnectorTier]) -> ResolvedSource:
    """
    Walk the tiers in SOURCE_PRIORITY order.

    Step 2 (detect unavailable source): a tier signals it can't supply data
    by raising SourceUnavailableError.
    Step 3 (select next available source): on that error, move to the next
    tier in priority order.
    Step 4 (attach selected source status): the returned ResolvedSource.status
    is the name of whichever tier's fetch() actually returned data.
    Step 5 (never label unavailable data LIVE): status is only ever set from
    a tier that succeeded, so a failed LIVE fetch can never produce a LIVE
    label -- it simply isn't the tier that ran.
    """
    ordered = sorted(tiers, key=lambda t: SOURCE_PRIORITY.index(t.name))
    attempted: list[tuple[str, str]] = []
    for tier in ordered:
        try:
            data = tier.fetch()
        except SourceUnavailableError as exc:
            attempted.append((tier.name, str(exc)))
            continue
        return ResolvedSource(category=category, status=tier.name, data=data)
    raise DataUnavailableError(
        f"No available source for '{category}'. Attempted: {attempted}"
    )
