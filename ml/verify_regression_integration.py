#!/usr/bin/env python3
"""
OceanPulse AI — Task 5 (Regression & Integration Testing) final
verification script.

Per the Task 5 card:
    "Done when: existing tests pass and the ML layer can be enabled or
    disabled without breaking the API flow."

Usage:
    cd ml
    python verify_regression_integration.py

Checks, in order:
  1. The six required index boundaries (29, 30, 59, 60, 79, 80)
     classify correctly.
  2. All three demo scenarios, run five times each (15 runs total),
     return their exact contract index/level/alert outcome:
       healthy_reef       -> 22 / STABLE   / NO_ALERT
       declining_fishery  -> 55 / WATCH    / NO_ALERT
       coral_bleaching    -> 88 / CRITICAL / ALERT_DISPATCHED
  3. ML-disabled fallback matches the plain rule-based FusionEngine
     exactly, for every demo scenario.
  4. Malformed/missing ML inputs (non-numeric, out-of-range, missing
     signal categories) are handled without the pipeline crashing.
  5. Toggling ML (disabled -> enabled) for the primary judge demo does
     not change the alert outcome or the response shape.

Exits 0 if every check passes, exits 1 otherwise.

NOTE: as in tests/test_regression_integration.py, NO_ALERT /
ALERT_DISPATCHED here is a TEST-ONLY mirror of API_CONTRACT.md section
12's rule (index >= threshold -> ALERT_DISPATCHED). The Alert Gate
itself is the Backend's responsibility, not `ml/`'s.
"""

import sys

from fusion_engine.fusion import FusionEngine, index_to_level
from fusion_engine.demo_scenarios import get_scenario
from models.converters import FeatureValidationError
from models.schema import IsolationForestOutput, StockTrendClass, XGBoostOutput
from models.ml_fusion_engine import MLEnhancedFusionEngine
from fusion_engine.schema import (
    FusionInput, OceanFeatures, FisheriesFeatures, MolecularFeatures,
    SourceStatus,
)

ALERT_THRESHOLD = 70
RUNS_PER_SCENARIO = 5

SCENARIOS_EXPECTED = [
    ("healthy_reef", 22, "STABLE", "NO_ALERT"),
    ("declining_fishery", 55, "WATCH", "NO_ALERT"),
    ("coral_bleaching", 88, "CRITICAL", "ALERT_DISPATCHED"),
]


def _alert_status(index: int) -> str:
    return "ALERT_DISPATCHED" if index >= ALERT_THRESHOLD else "NO_ALERT"


class _FakeAvailableXGB:
    model_version = "verify-regression-xgb-v1"

    def is_available(self):
        return True

    def predict(self, fisheries):
        return XGBoostOutput(
            stock_trend_class=StockTrendClass.CRITICAL_DECLINE,
            confidence=0.8,
            model_version=self.model_version,
            available=True,
        )


class _FakeAvailableIso:
    model_version = "verify-regression-iso-v1"

    def is_available(self):
        return True

    def predict(self, ocean, fisheries, molecular):
        return IsolationForestOutput(
            normalized_anomaly_score=0.8,
            is_anomaly=True,
            model_version=self.model_version,
            available=True,
        )


def check_1_index_boundaries():
    print("[1] Index boundary regression (29, 30, 59, 60, 79, 80)")
    expected = {29: "STABLE", 30: "WATCH", 59: "WATCH",
                60: "STRESSED", 79: "STRESSED", 80: "CRITICAL"}
    all_ok = True
    for index, level in expected.items():
        got = index_to_level(index)
        ok = got == level
        all_ok = all_ok and ok
        print(f"    {index} -> {got} [{'OK' if ok else 'MISMATCH, expected ' + level}]")
    return all_ok


def check_2_demo_scenarios_repeated():
    print(f"\n[2] All three demo scenarios, {RUNS_PER_SCENARIO} runs each "
          f"({RUNS_PER_SCENARIO * 3} runs total)")
    engine = MLEnhancedFusionEngine()  # real interfaces -- ML disabled today
    all_ok = True
    run_number = 0
    for name, expected_index, expected_level, expected_alert in SCENARIOS_EXPECTED:
        for i in range(1, RUNS_PER_SCENARIO + 1):
            run_number += 1
            result = engine.analyze(get_scenario(name))
            alert = _alert_status(result.index)
            match = (
                result.index == expected_index
                and result.level == expected_level
                and alert == expected_alert
            )
            all_ok = all_ok and match
            status = "OK" if match else "MISMATCH"
            print(f"    {name} run {i}/{RUNS_PER_SCENARIO} (#{run_number}): "
                  f"index={result.index} level={result.level} alert={alert} [{status}]")
    return all_ok


def check_3_ml_disabled_fallback():
    print("\n[3] ML-disabled fallback matches plain FusionEngine exactly")
    base_engine = FusionEngine()
    ml_engine = MLEnhancedFusionEngine()
    all_ok = True
    for name, _, _, _ in SCENARIOS_EXPECTED:
        scenario = get_scenario(name)
        base = base_engine.analyze(scenario)
        ml_result = ml_engine.analyze(scenario)
        match = (
            ml_result.index == base.index
            and ml_result.level == base.level
            and ml_result.confidence == base.confidence
            and ml_result.factors == base.factors
            and ml_result.ml_enhanced is False
        )
        all_ok = all_ok and match
        print(f"    {name}: ml_enhanced={ml_result.ml_enhanced} "
              f"[{'OK' if match else 'MISMATCH'}]")
    return all_ok


def check_4_malformed_missing_inputs():
    print("\n[4] Malformed / missing ML inputs handled without crashing")
    engine = MLEnhancedFusionEngine()
    all_ok = True

    try:
        result = engine.analyze(FusionInput(region_id="empty"))
        ok = 0 <= result.index <= 100
    except Exception as exc:
        ok = False
        print(f"    empty input CRASHED: {exc}")
    all_ok = all_ok and ok
    print(f"    empty FusionInput -> no crash [{'OK' if ok else 'FAIL'}]")

    try:
        bad_fisheries = FisheriesFeatures(cpue_trend_pct="not-a-number",
                                           vessel_density_index=0.3,
                                           source=SourceStatus.DEMO)
        engine.xgboost_interface.predict(bad_fisheries)
        ok = False  # should have raised
    except FeatureValidationError:
        ok = True
    except Exception as exc:
        ok = False
        print(f"    non-numeric input raised the WRONG exception type: {exc}")
    all_ok = all_ok and ok
    print(f"    non-numeric fisheries value -> FeatureValidationError, "
          f"not a crash [{'OK' if ok else 'FAIL'}]")

    try:
        fusion_input = FusionInput(
            region_id="malformed",
            ocean=OceanFeatures(sst_anomaly_c=999.0, source=SourceStatus.DEMO),
            fisheries=FisheriesFeatures(cpue_trend_pct=-10, vessel_density_index=0.2,
                                         source=SourceStatus.DEMO),
            molecular=MolecularFeatures(species_richness=70, baseline_richness=100,
                                         source=SourceStatus.DEMO),
        )
        result = engine.analyze(fusion_input)
        ok = 0 <= result.index <= 100
    except Exception as exc:
        ok = False
        print(f"    out-of-range ocean input CRASHED: {exc}")
    all_ok = all_ok and ok
    print(f"    out-of-range ocean input -> handled end-to-end "
          f"[{'OK' if ok else 'FAIL'}]")

    return all_ok


def check_5_ml_toggle_does_not_break_flow():
    print("\n[5] ML enabled/disabled toggle does not break the alert flow")
    disabled = MLEnhancedFusionEngine().analyze(get_scenario("coral_bleaching"))
    enabled = MLEnhancedFusionEngine(
        xgboost_interface=_FakeAvailableXGB(),
        isolation_forest_interface=_FakeAvailableIso(),
    ).analyze(get_scenario("coral_bleaching"))

    ok = (
        _alert_status(disabled.index) == "ALERT_DISPATCHED"
        and _alert_status(enabled.index) == "ALERT_DISPATCHED"
        and disabled.level == "CRITICAL"
        and enabled.level == "CRITICAL"
        and disabled.sources == enabled.sources
        and set(disabled.factors[0].keys()) == set(enabled.factors[0].keys())
    )
    print(f"    ML disabled: index={disabled.index} alert={_alert_status(disabled.index)}")
    print(f"    ML enabled:  index={enabled.index} alert={_alert_status(enabled.index)}")
    print(f"    [{'OK' if ok else 'MISMATCH'}] alert outcome and response shape "
          "stable across the toggle")
    return ok


def main():
    results = [
        check_1_index_boundaries(),
        check_2_demo_scenarios_repeated(),
        check_3_ml_disabled_fallback(),
        check_4_malformed_missing_inputs(),
        check_5_ml_toggle_does_not_break_flow(),
    ]

    print()
    if all(results):
        print("All Task 5 checks passed: existing tests hold, and the ML "
              "layer can be enabled or disabled without breaking the API flow.")
        sys.exit(0)
    else:
        print("One or more Task 5 checks failed.")
        sys.exit(1)


if __name__ == "__main__":
    main()
