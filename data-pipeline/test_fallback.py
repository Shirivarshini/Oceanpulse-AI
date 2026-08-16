from source_resolver import (
    ConnectorTier,
    DataUnavailableError,
    SourceUnavailableError,
    resolve,
)
import connectors


def _ok(value):
    return lambda: value


def _fail(msg="unavailable"):
    def _raise():
        raise SourceUnavailableError(msg)
    return _raise


def test_live_is_selected_when_available():
    result = resolve("ocean", [
        ConnectorTier("LIVE", _ok("live-data")),
        ConnectorTier("CACHED", _ok("cached-data")),
        ConnectorTier("HISTORICAL", _ok("historical-data")),
        ConnectorTier("DEMO", _ok("demo-data")),
    ])
    assert result.status == "LIVE"
    assert result.data == "live-data"


def test_live_to_cached():
    result = resolve("ocean", [
        ConnectorTier("LIVE", _fail("live down")),
        ConnectorTier("CACHED", _ok("cached-data")),
        ConnectorTier("HISTORICAL", _ok("historical-data")),
        ConnectorTier("DEMO", _ok("demo-data")),
    ])
    assert result.status == "CACHED"
    assert result.data == "cached-data"


def test_cached_to_historical():
    result = resolve("fisheries", [
        ConnectorTier("LIVE", _fail("live down")),
        ConnectorTier("CACHED", _fail("cache miss")),
        ConnectorTier("HISTORICAL", _ok("historical-data")),
        ConnectorTier("DEMO", _ok("demo-data")),
    ])
    assert result.status == "HISTORICAL"
    assert result.data == "historical-data"


def test_historical_to_demo():
    result = resolve("molecular", [
        ConnectorTier("LIVE", _fail()),
        ConnectorTier("CACHED", _fail()),
        ConnectorTier("HISTORICAL", _fail()),
        ConnectorTier("DEMO", _ok("demo-data")),
    ])
    assert result.status == "DEMO"
    assert result.data == "demo-data"


def test_unavailable_live_can_never_be_labelled_live():
    result = resolve("ocean", [
        ConnectorTier("LIVE", _fail("live unavailable")),
        ConnectorTier("DEMO", _ok("demo-data")),
    ])
    assert result.status == "DEMO"
    assert result.status != "LIVE"


def test_all_tiers_unavailable_raises():
    try:
        resolve("ocean", [
            ConnectorTier("LIVE", _fail()),
            ConnectorTier("CACHED", _fail()),
            ConnectorTier("HISTORICAL", _fail()),
            ConnectorTier("DEMO", _fail()),
        ])
    except DataUnavailableError:
        return
    raise AssertionError("Expected DataUnavailableError")


def test_connector_resolves_all_categories_to_demo_when_external_sources_disabled():
    connectors.disable_external_sources()
    try:
        for scenario in connectors.SCENARIO_FILES:
            result = connectors.resolve_scenario_sources(scenario)
            assert set(result["sources"]) == set(connectors.CATEGORIES)
            assert all(status == "DEMO" for status in result["sources"].values())
            assert all(result["data"][category] for category in connectors.CATEGORIES)
    finally:
        connectors.enable_external_sources()


def test_status_is_the_tier_that_actually_supplied_data():
    result = resolve("ocean", [
        ConnectorTier("LIVE", _fail()),
        ConnectorTier("CACHED", _ok([{"value": 1}])),
        ConnectorTier("HISTORICAL", _ok([{"value": 2}])),
        ConnectorTier("DEMO", _ok([{"value": 3}])),
    ])
    assert result.status == "CACHED"
    assert result.data == [{"value": 1}]
