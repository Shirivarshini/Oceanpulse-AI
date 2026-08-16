#!/usr/bin/env python3
"""
OceanPulse AI — Task 1 final verification script.

Per the Task 1 card:
    "Final verification: Member 3 runs the engine twice with identical
    input and compares the outputs, then posts matching results by
    Hour 5."

Usage:
    cd ml
    python verify_determinism.py

Exits 0 and prints "MATCH" if both runs produce identical output for
every demo scenario plus one arbitrary custom input. Exits 1 and prints
"MISMATCH" with a diff if not.
"""

import json
import sys
from dataclasses import asdict

from fusion_engine.fusion import FusionEngine
from fusion_engine.schema import (
    FusionInput, OceanFeatures, FisheriesFeatures, MolecularFeatures,
    SourceStatus,
)
from fusion_engine.demo_scenarios import SCENARIOS


def _result_to_dict(result):
    return {
        "index": result.index,
        "level": result.level,
        "confidence": result.confidence,
        "factors": result.factors,
        "timeline": result.timeline,
        "sources": result.sources,
    }


def _custom_input():
    return FusionInput(
        region_id="gulf-of-mannar",
        ocean=OceanFeatures(sst_anomaly_c=1.2, chlorophyll_a_anomaly_pct=45,
                             source=SourceStatus.DEMO),
        fisheries=FisheriesFeatures(cpue_trend_pct=-22, vessel_density_index=0.4,
                                     source=SourceStatus.DEMO),
        molecular=MolecularFeatures(species_richness=70, baseline_richness=90,
                                     rare_taxa_detected=1, invasive_taxa_detected=0,
                                     sample_quality=0.85, source=SourceStatus.DEMO),
    )


def main():
    inputs = dict(SCENARIOS)
    inputs["custom_arbitrary_input"] = _custom_input()

    all_match = True
    for name, fusion_input in inputs.items():
        engine_run_1 = FusionEngine()
        engine_run_2 = FusionEngine()

        result_1 = _result_to_dict(engine_run_1.analyze(fusion_input))
        result_2 = _result_to_dict(engine_run_2.analyze(fusion_input))

        match = result_1 == result_2
        all_match = all_match and match

        status = "MATCH" if match else "MISMATCH"
        print(f"[{status}] {name}: index={result_1['index']} "
              f"level={result_1['level']} confidence={result_1['confidence']}")

        if not match:
            print("  run 1:", json.dumps(result_1, indent=2))
            print("  run 2:", json.dumps(result_2, indent=2))

    print()
    if all_match:
        print("MATCH — same input produces the same index on repeated "
              "executions across all scenarios.")
        sys.exit(0)
    else:
        print("MISMATCH — see diff above. Engine is not deterministic.")
        sys.exit(1)


if __name__ == "__main__":
    main()
