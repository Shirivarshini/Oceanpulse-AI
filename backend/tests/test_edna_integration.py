from backend.app.data_adapter import edna_to_molecular_features


def test_edna_sample_converts_to_molecular_features():
    features = edna_to_molecular_features(
        "sample-003",
        baseline_richness=20,
    )

    assert features.species_richness == 3
    assert features.rare_taxa_detected == 1
    assert features.invasive_taxa_detected == 1
    assert 0.0 <= features.sample_quality <= 1.0
    assert features.source.value == "DEMO"


def test_edna_sample_001_has_no_rare_or_invasive_taxa():
    features = edna_to_molecular_features(
        "sample-001",
        baseline_richness=20,
    )

    assert features.species_richness == 3
    assert features.rare_taxa_detected == 0
    assert features.invasive_taxa_detected == 0
    assert features.source.value == "DEMO"


def test_unknown_edna_sample_is_rejected():
    try:
        edna_to_molecular_features("does-not-exist")
        assert False
    except ValueError:
        assert True