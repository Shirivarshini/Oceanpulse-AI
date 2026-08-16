from pathlib import Path
import csv
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_PIPELINE_DIR = PROJECT_ROOT / "data-pipeline"

if str(DATA_PIPELINE_DIR) not in sys.path:
    sys.path.insert(0, str(DATA_PIPELINE_DIR))

from connectors import resolve_scenario_sources
from ml.fusion_engine.schema import MolecularFeatures, SourceStatus


def resolve_demo_sources(scenario: str) -> dict:
    """
    Resolve the actual source tier for each data category.

    The Data Fallback package owns:
        LIVE -> CACHED -> HISTORICAL -> DEMO
    """
    return resolve_scenario_sources(scenario)


def load_edna_sample(sample_id: str) -> dict:
    """
    Load one DEMO eDNA sample from the Data pipeline CSV.
    """
    path = DATA_PIPELINE_DIR / "edna_sample.csv"

    records = []

    with path.open(newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            if row["sample_id"] == sample_id:
                records.append(row)

    if not records:
        raise ValueError(f"Unknown eDNA sample: {sample_id}")

    return {
        "sample_id": sample_id,
        "records": records,
        "source": records[0]["source"],
    }


def edna_to_molecular_features(
    sample_id: str,
    baseline_richness: int = 0,
) -> MolecularFeatures:
    """
    Convert an eDNA sample into the normalized MolecularFeatures
    consumed by the Fusion Engine.
    """
    sample = load_edna_sample(sample_id)
    records = sample["records"]

    richness = len({row["taxon"] for row in records})

    rare_count = sum(
        row["status"] == "rare"
        for row in records
    )

    invasive_count = sum(
        row["status"] == "invasive"
        for row in records
    )

    confidences = [
        float(row["confidence"])
        for row in records
    ]

    sample_quality = (
        sum(confidences) / len(confidences)
        if confidences
        else 0.0
    )

    return MolecularFeatures(
        species_richness=richness,
        baseline_richness=baseline_richness,
        rare_taxa_detected=rare_count,
        invasive_taxa_detected=invasive_count,
        sample_quality=sample_quality,
        source=SourceStatus(sample["source"]),
    )