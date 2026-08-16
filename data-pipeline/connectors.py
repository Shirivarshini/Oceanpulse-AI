"""
Per-category connectors for ocean, fisheries, and molecular data.

LIVE/CACHED/HISTORICAL are placeholders: per implementation_plan.md, live
Argo/Copernicus/GBIF/OBIS/AIS integration (Phase 6) and caching (Phase 6/9)
are not built yet, so those tiers correctly report themselves as
unavailable. DEMO always succeeds, reading the Task 1 datasets in this same
directory -- this is what keeps the app demoable per CLAUDE.md's
Reliability Rules ("app must remain demoable if external dependencies fail").

As Phase 6/9 are implemented, _fetch_live/_fetch_cached/_fetch_historical
get replaced with real calls; resolve() and the fallback order do not change.
"""

from __future__ import annotations

import json
from pathlib import Path

from source_resolver import ConnectorTier, ResolvedSource, SourceUnavailableError, resolve

DATA_PIPELINE_DIR = Path(__file__).parent
SCENARIO_FILES = {
    "healthy_reef": DATA_PIPELINE_DIR / "healthy_reef.json",
    "declining_fishery": DATA_PIPELINE_DIR / "declining_fishery.json",
    "coral_bleaching": DATA_PIPELINE_DIR / "coral_bleaching.json",
}
CATEGORIES = ["ocean", "fisheries", "molecular"]

# Global toggle so tests/demo runs can explicitly simulate "external sources
# down" (used by the Hour-12 final verification), separate from the
# not-yet-implemented state each tier is already in.
_EXTERNAL_SOURCES_DISABLED = False


def disable_external_sources() -> None:
    global _EXTERNAL_SOURCES_DISABLED
    _EXTERNAL_SOURCES_DISABLED = True


def enable_external_sources() -> None:
    global _EXTERNAL_SOURCES_DISABLED
    _EXTERNAL_SOURCES_DISABLED = False


def _load_scenario(scenario: str) -> dict:
    path = SCENARIO_FILES.get(scenario)
    if path is None or not path.exists():
        raise SourceUnavailableError(f"Unknown demo scenario '{scenario}'")
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _demo_records(scenario: str, category: str) -> list[dict]:
    dataset = _load_scenario(scenario)
    return [r for r in dataset["records"] if r["category"] == category]


def _fetch_live(category: str):
    if _EXTERNAL_SOURCES_DISABLED:
        raise SourceUnavailableError(f"LIVE {category} source disabled for testing")
    raise SourceUnavailableError(f"LIVE {category} connector not yet implemented (Phase 6)")


def _fetch_cached(category: str):
    if _EXTERNAL_SOURCES_DISABLED:
        raise SourceUnavailableError(f"CACHED {category} source disabled for testing")
    raise SourceUnavailableError(f"CACHED {category} store not yet implemented (Phase 6)")


def _fetch_historical(category: str):
    if _EXTERNAL_SOURCES_DISABLED:
        raise SourceUnavailableError(f"HISTORICAL {category} source disabled for testing")
    raise SourceUnavailableError(f"HISTORICAL {category} dataset not yet configured (Phase 6)")


def _fetch_demo(scenario: str, category: str):
    records = _demo_records(scenario, category)
    if not records:
        raise SourceUnavailableError(f"No DEMO records for '{category}' in scenario '{scenario}'")
    return records


def build_tiers(scenario: str, category: str) -> list[ConnectorTier]:
    return [
        ConnectorTier("LIVE", lambda: _fetch_live(category)),
        ConnectorTier("CACHED", lambda: _fetch_cached(category)),
        ConnectorTier("HISTORICAL", lambda: _fetch_historical(category)),
        ConnectorTier("DEMO", lambda: _fetch_demo(scenario, category)),
    ]


def resolve_scenario_sources(scenario: str) -> dict:
    """Resolve ocean/fisheries/molecular sources for one demo scenario."""
    resolved: dict[str, ResolvedSource] = {
        category: resolve(category, build_tiers(scenario, category))
        for category in CATEGORIES
    }
    return {
        "scenario": scenario,
        "sources": {c: r.status for c, r in resolved.items()},
        "data": {c: r.data for c, r in resolved.items()},
    }
