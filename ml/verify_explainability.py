#!/usr/bin/env python3
"""
OceanPulse AI — Task 3 final verification script.

Per the Task 3 card:
    "Final verification: Member 3 runs all three demo scenarios and
    verifies non-empty factors and timeline arrays by Hour 9."

Usage:
    cd ml
    python verify_explainability.py

Prints the factor count and timeline length for each of the three
required demo scenarios so the result can be posted directly. Exits 0
if all three have non-empty factors and timeline arrays, exits 1
otherwise.
"""

import sys

from fusion_engine.fusion import FusionEngine
from fusion_engine.demo_scenarios import SCENARIOS


def main():
    engine = FusionEngine()
    all_pass = True

    for name, fusion_input in SCENARIOS.items():
        result = engine.analyze(fusion_input)
        factors_ok = len(result.factors) >= 1
        timeline_ok = len(result.timeline) >= 1
        scenario_pass = factors_ok and timeline_ok
        all_pass = all_pass and scenario_pass

        status = "OK" if scenario_pass else "FAIL"
        print(f"[{status}] {name}: index={result.index} level={result.level} "
              f"factors={len(result.factors)} timeline_events={len(result.timeline)}")

        for factor in result.factors:
            print(f"    factor: {factor['name']} ({factor['category']}, "
                  f"impact={factor['impact']}, severity={factor['severity']})")
        for point in result.timeline:
            print(f"    timeline: {point['timestamp']} -> "
                  f"index={point['index']} ({point['event']})")

    print()
    if all_pass:
        print("All three demo scenarios have non-empty factors and "
              "timeline arrays.")
        sys.exit(0)
    else:
        print("One or more demo scenarios have empty factors or "
              "timeline arrays.")
        sys.exit(1)


if __name__ == "__main__":
    main()
