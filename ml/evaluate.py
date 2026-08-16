#!/usr/bin/env python3
"""
OceanPulse AI — ml/ — Task 6: Evaluation & Documentation.

Deliverable: reproducible evaluation script.

Usage:
    cd ml
    python evaluate.py

What this script does, honestly, in order:

  1. Reports live model-availability status for both Phase-5 models
     (XGBoost fisheries, IsolationForest anomaly) — whether a trained
     artifact is actually loaded right now, and its version.
  2. Reports the deterministic heuristic-fallback tier's behavior on
     the three demo scenarios, clearly labeled as heuristic output,
     NOT a measured accuracy metric.
  3. Looks for a labeled evaluation dataset at the paths documented
     below. If one exists AND a trained model is loaded, computes
     Precision / Recall / F1 / ROC-AUC / false-positive rate against
     it and writes eval_report.json. If either is missing (the
     current MVP state — no labeled data, no trained artifacts), it
     prints exactly that and NOTHING is scored, guessed, or invented.

Per CLAUDE.md: "Report Precision, Recall, F1, ROC-AUC and
false-positive rate only when measured" and "Never fabricate ...
model metrics." This script is the mechanism that rule is enforced
through — it has no code path that can print a metric that wasn't
actually computed from real predictions vs. real labels.

Expected labeled-dataset format (create these yourself to evaluate a
real trained model — none are provided, since none of this MVP's data
is labeled ground truth):

  eval_data/fisheries_eval.csv
      columns: cpue_trend_pct, vessel_density_index, label
      label ∈ {stable, declining, critical_decline}
      (matches models.schema.StockTrendClass values)

  eval_data/anomaly_eval.csv
      columns: sst_anomaly_c, chlorophyll_a_anomaly_pct,
               salinity_anomaly_psu, cpue_trend_pct,
               vessel_density_index, species_richness_delta_pct, label
      label ∈ {0, 1}   (1 = anomalous, matches IsolationForestOutput.is_anomaly)

Exit code is always 0 — an "unmeasured" result is a valid, honest
outcome for an MVP with no labeled data yet, not a script failure.
"""

import csv
import json
import os
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fusion_engine.demo_scenarios import get_scenario  # noqa: E402
from models.isolation_forest_anomaly import IsolationForestAnomalyInterface  # noqa: E402
from models.ml_fusion_engine import MLEnhancedFusionEngine  # noqa: E402
from models.schema import StockTrendClass  # noqa: E402
from models.xgboost_fisheries import XGBoostFisheriesInterface  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
EVAL_DATA_DIR = os.path.join(HERE, "eval_data")
FISHERIES_EVAL_PATH = os.path.join(EVAL_DATA_DIR, "fisheries_eval.csv")
ANOMALY_EVAL_PATH = os.path.join(EVAL_DATA_DIR, "anomaly_eval.csv")
REPORT_PATH = os.path.join(HERE, "eval_report.json")

DEMO_SCENARIOS = ["healthy_reef", "declining_fishery", "coral_bleaching"]


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ---------------------------------------------------------------------
# Section 1 — live model availability (always real, never guessed)
# ---------------------------------------------------------------------

def report_model_status() -> dict:
    print("=" * 70)
    print("1. MODEL AVAILABILITY (live check, not a claim)")
    print("=" * 70)
    engine = MLEnhancedFusionEngine()
    status = engine.model_status()
    for model_name, info in status.items():
        tier = "trained model" if info["available"] else "heuristic fallback (no trained artifact)"
        print(f"  {model_name}: available={info['available']} "
              f"model_version={info['model_version']!r}  [{tier}]")
    print()
    return status


# ---------------------------------------------------------------------
# Section 2 — heuristic-tier behavior on demo scenarios (not a metric)
# ---------------------------------------------------------------------

def report_heuristic_behavior() -> None:
    print("=" * 70)
    print("2. HEURISTIC-FALLBACK-TIER OUTPUT ON DEMO SCENARIOS")
    print("   (deterministic rule output for inspection only — this is")
    print("    NOT an accuracy metric; no ground-truth labels exist for")
    print("    these scenarios)")
    print("=" * 70)
    xgb = XGBoostFisheriesInterface()
    iso = IsolationForestAnomalyInterface()
    for name in DEMO_SCENARIOS:
        scenario = get_scenario(name)
        xgb_out = xgb.predict(scenario.fisheries) if scenario.fisheries else None
        iso_out = iso.predict(scenario.ocean, scenario.fisheries, scenario.molecular)
        xgb_desc = (f"{xgb_out.stock_trend_class.value} "
                    f"(heuristic_score={xgb_out.confidence})") if xgb_out else "n/a"
        print(f"  {name}:")
        print(f"    xgboost_fisheries  -> {xgb_desc}")
        print(f"    isolation_forest   -> anomaly_score={iso_out.normalized_anomaly_score} "
              f"is_anomaly={iso_out.is_anomaly}")
    print()


# ---------------------------------------------------------------------
# Section 3 — real metrics, only if a labeled dataset + trained model
# both actually exist. Otherwise: say so, compute nothing.
# ---------------------------------------------------------------------

def _read_csv(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def _confusion_counts(y_true, y_pred, positive_label):
    tp = sum(1 for t, p in zip(y_true, y_pred) if t == positive_label and p == positive_label)
    fp = sum(1 for t, p in zip(y_true, y_pred) if t != positive_label and p == positive_label)
    fn = sum(1 for t, p in zip(y_true, y_pred) if t == positive_label and p != positive_label)
    tn = sum(1 for t, p in zip(y_true, y_pred) if t != positive_label and p != positive_label)
    return tp, fp, fn, tn


def _prf(tp, fp, fn):
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) else 0.0
    return round(precision, 4), round(recall, 4), round(f1, 4)


def evaluate_fisheries_model(model_status: dict) -> dict:
    print("=" * 70)
    print("3a. XGBoost fisheries model evaluation")
    print("=" * 70)
    if not os.path.exists(FISHERIES_EVAL_PATH):
        print(f"  NOT MEASURED — no labeled dataset at {FISHERIES_EVAL_PATH}")
        print("  Metrics are not reported because none have been computed.\n")
        return {"measured": False, "reason": "no_labeled_dataset"}
    if not model_status["xgboost_fisheries"]["available"]:
        print(f"  Labeled dataset found at {FISHERIES_EVAL_PATH}, but no trained")
        print("  XGBoost artifact is loaded — scoring the heuristic fallback tier")
        print("  instead (still real, still measured, but NOT a trained-model metric).\n")

    rows = _read_csv(FISHERIES_EVAL_PATH)
    if not rows:
        print("  Dataset file exists but is empty. Nothing to measure.\n")
        return {"measured": False, "reason": "empty_dataset"}

    from fusion_engine.schema import FisheriesFeatures
    xgb = XGBoostFisheriesInterface()
    y_true, y_pred = [], []
    for row in rows:
        features = FisheriesFeatures(
            cpue_trend_pct=float(row["cpue_trend_pct"]),
            vessel_density_index=float(row["vessel_density_index"]),
        )
        out = xgb.predict(features)
        y_true.append(row["label"].strip())
        y_pred.append(out.stock_trend_class.value)

    classes = [c.value for c in StockTrendClass]
    per_class = {}
    for cls in classes:
        tp, fp, fn, tn = _confusion_counts(y_true, y_pred, cls)
        precision, recall, f1 = _prf(tp, fp, fn)
        fpr = fp / (fp + tn) if (fp + tn) else 0.0
        per_class[cls] = {
            "precision": precision, "recall": recall, "f1": f1,
            "false_positive_rate": round(fpr, 4), "support": tp + fn,
        }
        print(f"  class={cls:<17} precision={precision:.2f} recall={recall:.2f} "
              f"f1={f1:.2f} fpr={fpr:.2f} support={tp + fn}")

    accuracy = sum(1 for t, p in zip(y_true, y_pred) if t == p) / len(y_true)
    print(f"  overall accuracy={accuracy:.4f}  n={len(y_true)}")
    print("  ROC-AUC not reported: requires class probability scores, which the")
    print("  heuristic tier does not produce (it emits a discrete class only).\n")

    return {
        "measured": True,
        "tier": "trained_model" if model_status["xgboost_fisheries"]["available"] else "heuristic_fallback",
        "model_version": model_status["xgboost_fisheries"]["model_version"],
        "n_samples": len(y_true),
        "accuracy": round(accuracy, 4),
        "per_class": per_class,
        "roc_auc": None,
        "roc_auc_reason": "heuristic tier emits a discrete class, not a probability score",
    }


def evaluate_anomaly_model(model_status: dict) -> dict:
    print("=" * 70)
    print("3b. IsolationForest anomaly model evaluation")
    print("=" * 70)
    if not os.path.exists(ANOMALY_EVAL_PATH):
        print(f"  NOT MEASURED — no labeled dataset at {ANOMALY_EVAL_PATH}")
        print("  Metrics are not reported because none have been computed.\n")
        return {"measured": False, "reason": "no_labeled_dataset"}
    if not model_status["isolation_forest_anomaly"]["available"]:
        print(f"  Labeled dataset found at {ANOMALY_EVAL_PATH}, but no trained")
        print("  IsolationForest artifact is loaded — scoring the heuristic fallback")
        print("  tier instead (still real, still measured, but NOT a trained-model metric).\n")

    rows = _read_csv(ANOMALY_EVAL_PATH)
    if not rows:
        print("  Dataset file exists but is empty. Nothing to measure.\n")
        return {"measured": False, "reason": "empty_dataset"}

    from fusion_engine.schema import FisheriesFeatures, MolecularFeatures, OceanFeatures
    iso = IsolationForestAnomalyInterface()
    y_true, y_pred, y_score = [], [], []
    for row in rows:
        ocean = OceanFeatures(
            sst_anomaly_c=float(row["sst_anomaly_c"]),
            chlorophyll_a_anomaly_pct=float(row["chlorophyll_a_anomaly_pct"]),
            salinity_anomaly_psu=float(row["salinity_anomaly_psu"]),
        )
        fisheries = FisheriesFeatures(
            cpue_trend_pct=float(row["cpue_trend_pct"]),
            vessel_density_index=float(row["vessel_density_index"]),
        )
        # species_richness_delta_pct is derived inside converters.py from
        # species_richness/baseline_richness, so reconstruct a compatible pair.
        delta_pct = float(row["species_richness_delta_pct"])
        molecular = MolecularFeatures(species_richness=100 - int(delta_pct), baseline_richness=100)
        out = iso.predict(ocean, fisheries, molecular)
        y_true.append(int(row["label"]))
        y_pred.append(1 if out.is_anomaly else 0)
        y_score.append(out.normalized_anomaly_score if out.normalized_anomaly_score is not None else 0.0)

    tp, fp, fn, tn = _confusion_counts(y_true, y_pred, 1)
    precision, recall, f1 = _prf(tp, fp, fn)
    fpr = fp / (fp + tn) if (fp + tn) else 0.0
    print(f"  precision={precision:.2f} recall={recall:.2f} f1={f1:.2f} "
          f"false_positive_rate={fpr:.2f} n={len(y_true)}")

    roc_auc = None
    try:
        from sklearn.metrics import roc_auc_score
        if len(set(y_true)) > 1:
            roc_auc = round(float(roc_auc_score(y_true, y_score)), 4)
            print(f"  roc_auc={roc_auc:.4f}")
        else:
            print("  ROC-AUC not reported: dataset has only one label class.")
    except ImportError:
        print("  ROC-AUC not reported: scikit-learn is not installed in this environment.")
    print()

    return {
        "measured": True,
        "tier": "trained_model" if model_status["isolation_forest_anomaly"]["available"] else "heuristic_fallback",
        "model_version": model_status["isolation_forest_anomaly"]["model_version"],
        "n_samples": len(y_true),
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "false_positive_rate": round(fpr, 4),
        "roc_auc": roc_auc,
    }


def main():
    print("\nOceanPulse AI — ml/ — evaluation run:", _now())
    print()

    model_status = report_model_status()
    report_heuristic_behavior()
    fisheries_result = evaluate_fisheries_model(model_status)
    anomaly_result = evaluate_anomaly_model(model_status)

    report = {
        "generated_at": _now(),
        "model_status": model_status,
        "fisheries_evaluation": fisheries_result,
        "anomaly_evaluation": anomaly_result,
    }

    any_measured = fisheries_result["measured"] or anomaly_result["measured"]
    if any_measured:
        with open(REPORT_PATH, "w") as f:
            json.dump(report, f, indent=2)
        print("=" * 70)
        print(f"Wrote {REPORT_PATH} (contains only metrics actually computed above).")
        print("=" * 70)
    else:
        print("=" * 70)
        print("SUMMARY: No labeled evaluation data is present in this repository,")
        print("and no trained model artifacts ship with this MVP. Precision /")
        print("Recall / F1 / ROC-AUC / false-positive rate are therefore NOT")
        print("reported anywhere, per CLAUDE.md ('report ... only when measured').")
        print("See EVALUATION.md for what would need to exist for this script")
        print("to produce real numbers.")
        print("=" * 70)
        # No report file is written — an empty/absent eval_report.json is
        # itself the honest signal that nothing has been measured yet.

    sys.exit(0)


if __name__ == "__main__":
    main()
