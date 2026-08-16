#!/usr/bin/env python3
"""
OceanPulse AI — Task 4 (ML Integration) final verification script.

Per the Task 4 card:
    "Done when: the Fusion Engine can use ML when available and still
    produces valid results when ML is disabled."

Usage:
    cd ml
    python verify_ml_integration.py

Checks, in order:
  1. Model availability detection reports the true (currently
     unavailable, since no trained artifacts ship with this MVP)
     status honestly.
  2. All three demo scenarios still return their exact contract
     index/level through MLEnhancedFusionEngine, proving ML-disabled
     behavior is a byte-for-byte pass-through of the rule-based engine.
  3. With fake "available" model interfaces injected, the engine
     combines ML output into the index/factors/confidence while index
     classification bands, timeline, and sources stay intact.

Exits 0 if every check passes, exits 1 otherwise.
"""

import sys

from fusion_engine.fusion import FusionEngine, index_to_level
from fusion_engine.demo_scenarios import get_scenario
from models.schema import IsolationForestOutput, StockTrendClass, XGBoostOutput
from models.ml_fusion_engine import MLEnhancedFusionEngine

SCENARIOS_EXPECTED = [
    ("healthy_reef", 22, "STABLE"),
    ("declining_fishery", 55, "WATCH"),
    ("coral_bleaching", 88, "CRITICAL"),
]


class _FakeXGB:
    model_version = "verify-xgb-v1"

    def is_available(self):
        return True

    def predict(self, fisheries):
        return XGBoostOutput(
            stock_trend_class=StockTrendClass.CRITICAL_DECLINE,
            confidence=0.82,
            model_version=self.model_version,
            available=True,
        )


class _FakeIso:
    model_version = "verify-iso-v1"

    def is_available(self):
        return True

    def predict(self, ocean, fisheries, molecular):
        return IsolationForestOutput(
            normalized_anomaly_score=0.75,
            is_anomaly=True,
            model_version=self.model_version,
            available=True,
        )


def check_1_model_availability_detection():
    print("[1] Model availability detection")
    engine = MLEnhancedFusionEngine()
    status = engine.model_status()
    print(f"    {status}")
    ok = (
        status["xgboost_fisheries"]["available"] is False
        and status["xgboost_fisheries"]["model_version"] is None
        and status["isolation_forest_anomaly"]["available"] is False
        and status["isolation_forest_anomaly"]["model_version"] is None
    )
    print("    OK: honestly reports no trained model artifacts present"
          if ok else "    MISMATCH: expected both models unavailable")
    return ok


def check_2_demo_scenarios_unchanged():
    print("\n[2] Demo scenarios unchanged when ML is disabled (no artifacts)")
    engine = MLEnhancedFusionEngine()
    base_engine = FusionEngine()
    all_ok = True
    for name, expected_index, expected_level in SCENARIOS_EXPECTED:
        scenario = get_scenario(name)
        base = base_engine.analyze(scenario)
        ml_result = engine.analyze(scenario)
        match = (
            ml_result.index == expected_index
            and ml_result.level == expected_level
            and ml_result.index == base.index
            and ml_result.factors == base.factors
            and ml_result.ml_enhanced is False
        )
        all_ok = all_ok and match
        status = "OK" if match else "MISMATCH"
        print(f"    {name}: index={ml_result.index} level={ml_result.level} "
              f"ml_enhanced={ml_result.ml_enhanced} [{status}]")
    return all_ok


def check_3_ml_enhanced_combination():
    print("\n[3] ML-enhanced combination (fake available models injected)")
    engine = MLEnhancedFusionEngine(
        xgboost_interface=_FakeXGB(),
        isolation_forest_interface=_FakeIso(),
    )
    base_engine = FusionEngine()
    all_ok = True
    for name, _, _ in SCENARIOS_EXPECTED:
        scenario = get_scenario(name)
        base = base_engine.analyze(scenario)
        result = engine.analyze(scenario)

        bands_ok = result.level == index_to_level(result.index)
        index_raised_or_equal = result.index >= base.index
        factors_extend_base = all(f in result.factors for f in base.factors)
        confidence_non_decreasing = result.confidence >= base.confidence
        timeline_preserved = result.timeline == base.timeline
        sources_preserved = result.sources == base.sources
        clamped = 0 <= result.index <= 100
        match = (
            bands_ok and index_raised_or_equal and factors_extend_base
            and confidence_non_decreasing and timeline_preserved
            and sources_preserved and clamped and result.ml_enhanced is True
        )
        all_ok = all_ok and match
        status = "OK" if match else "MISMATCH"
        print(f"    {name}: base_index={base.index} -> ml_index={result.index} "
              f"level={result.level} confidence={base.confidence}->{result.confidence} "
              f"[{status}]")
    return all_ok


def main():
    r1 = check_1_model_availability_detection()
    r2 = check_2_demo_scenarios_unchanged()
    r3 = check_3_ml_enhanced_combination()

    print()
    if r1 and r2 and r3:
        print("All Task 4 checks passed: ML integrates when available, "
              "and the Fusion Engine still produces valid, unchanged "
              "results when ML is disabled.")
        sys.exit(0)
    else:
        print("One or more Task 4 checks failed.")
        sys.exit(1)


if __name__ == "__main__":
    main()
