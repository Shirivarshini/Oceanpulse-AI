#!/usr/bin/env python3
"""
OceanPulse AI — Task 2 final verification script.

Per the Task 2 card:
    "Final verification: Member 3 runs six boundary tests and posts the
    six returned levels by Hour 7."

Usage:
    cd ml
    python verify_boundaries.py

Prints the level returned for each of the six required boundary
indices (29, 30, 59, 60, 79, 80) so the result can be posted directly.
Exits 0 if all six match the specified levels, exits 1 otherwise.
"""

import sys

from fusion_engine.fusion import index_to_level

# (index, expected level) — per Task 2 steps 1-4 / success criteria.
BOUNDARIES = [
    (29, "STABLE"),
    (30, "WATCH"),
    (59, "WATCH"),
    (60, "STRESSED"),
    (79, "STRESSED"),
    (80, "CRITICAL"),
]


def main():
    all_match = True
    print("Index -> Level")
    for index, expected in BOUNDARIES:
        actual = index_to_level(index)
        match = actual == expected
        all_match = all_match and match
        status = "OK" if match else "MISMATCH"
        print(f"  {index:>3} -> {actual:<9} [{status}]"
              + ("" if match else f" (expected {expected})"))

    print()
    if all_match:
        print("All six boundary tests returned the specified levels.")
        sys.exit(0)
    else:
        print("One or more boundary tests did not match the specified levels.")
        sys.exit(1)


if __name__ == "__main__":
    main()
