#!/usr/bin/env python3
"""
OceanPulse AI — Task 4 final verification script.

Per the Task 4 card:
    "Final verification: Member 3 runs each scenario five times and
    records the 15 outputs by Hour 11."

Usage:
    cd ml
    python verify_demo_scenarios.py

Runs each of the three demo scenarios five times (15 runs total),
prints every output, and checks each run's index/level against the
project contract. Exits 0 if all 15 runs match, exits 1 otherwise.
"""

import sys

from fusion_engine.fusion import FusionEngine
from fusion_engine.demo_scenarios import get_scenario

RUNS_PER_SCENARIO = 5

# (scenario name, expected index, expected level) — per project contract.
SCENARIOS_EXPECTED = [
    ("healthy_reef", 22, "STABLE"),
    ("declining_fishery", 55, "WATCH"),
    ("coral_bleaching", 88, "CRITICAL"),
]


def main():
    engine = FusionEngine()
    all_match = True
    run_number = 0

    for name, expected_index, expected_level in SCENARIOS_EXPECTED:
        print(f"{name} (expecting {expected_index}/{expected_level}):")
        for i in range(1, RUNS_PER_SCENARIO + 1):
            run_number += 1
            result = engine.analyze(get_scenario(name))
            match = (result.index == expected_index
                     and result.level == expected_level)
            all_match = all_match and match
            status = "OK" if match else "MISMATCH"
            print(f"  run {i}/{RUNS_PER_SCENARIO} (#{run_number} overall): "
                  f"index={result.index} level={result.level} [{status}]")
        print()

    print(f"Total runs recorded: {run_number}")
    if all_match:
        print("All 15 outputs match the required index and level for "
              "their scenario.")
        sys.exit(0)
    else:
        print("One or more runs did not match the required index/level.")
        sys.exit(1)


if __name__ == "__main__":
    main()
