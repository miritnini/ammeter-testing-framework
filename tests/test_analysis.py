import json
import pytest
from src.testing.test_framework import AmmeterTestFramework
from src.testing.orchestrator import Orchestrator

from src.config.constants import (
    ALL_AMMETERS,
    AMMETER,
    SAMPLES,
    MEAN,
    TEST_PASSED,
    COUNT,
    ERRORS,
    MIN,
    MAX
)

# ---------------------------
# FIXTURE
# ---------------------------
@pytest.fixture(scope="module")
def framework():
    return AmmeterTestFramework()


@pytest.fixture(scope="module")
def orchestrator(framework):
    return Orchestrator(framework)


# ---------------------------
# STRUCTURE TEST
# ---------------------------
def test_run_analysis_structure(orchestrator):
    results = orchestrator.run_full_analysis()
    assert isinstance(results, list)
    assert len(results) == len(ALL_AMMETERS)
    for r in results:
        assert AMMETER in r
        assert SAMPLES in r
        assert MEAN in r
        assert TEST_PASSED in r


# ---------------------------
# ALL DEVICES PRESENT
# ---------------------------
def test_all_devices_present(orchestrator):
    results = orchestrator.run_full_analysis()
    names = [r[AMMETER] for r in results]
    assert set(names) == set(ALL_AMMETERS)


# ---------------------------
# NORMALIZATION TEST
# ---------------------------
def test_normalization_no_missing_fields(orchestrator):
    results = orchestrator.run_full_analysis()
    for r in results:
        assert r[MEAN] is not None
        assert r[MIN] is not None
        assert r[MAX] is not None
        assert COUNT in r
        assert ERRORS in r


# ---------------------------
# RAW RESULT EXISTS
# ---------------------------
def test_raw_result_exists(orchestrator):
    results = orchestrator.run_full_analysis()
    for r in results:
        assert "raw_result" in r


# ---------------------------
# PARTIAL FAILURE TEST
# ---------------------------
def test_partial_failure(monkeypatch, framework):
    def mock_run_test(device):
        raise Exception("failure")
    monkeypatch.setattr(framework, "run_test", mock_run_test)
    orchestrator = Orchestrator(framework)
    results = orchestrator.run_full_analysis()
    for r in results:
        assert r[AMMETER] in ALL_AMMETERS
        assert r[SAMPLES] == []
        assert r[ERRORS] >= 0
        assert r[TEST_PASSED] is False


# ---------------------------
# EXPORT TEST
# ---------------------------
def test_run_and_export(tmp_path, orchestrator):
    file_path = tmp_path / "results.json"
    results = orchestrator.run_and_export(file_path)
    assert file_path.exists()
    with open(file_path) as f:
        data = json.load(f)
    assert "results" in data
    assert isinstance(data["results"], list)
    assert len(data["results"]) == len(orchestrator.framework.devices)


# ---------------------------
# EXPORT CONSISTENCY
# ---------------------------
def test_export_matches_run(orchestrator, tmp_path):
    file_path = tmp_path / "results.json"
    results1 = orchestrator.run_full_analysis()
    results2 = orchestrator.run_and_export(file_path)
    assert len(results1) == len(results2["results"])


# ---------------------------
# DATA INTEGRITY TEST
# ---------------------------
def test_samples_consistency(orchestrator):
    results = orchestrator.run_full_analysis()
    for r in results:
        samples = r[SAMPLES]
        assert isinstance(samples, list)
        assert r[COUNT] == len(samples)


# ---------------------------
# EMPTY RESULTS SAFETY
# ---------------------------
def test_empty_result_handling(monkeypatch, framework):
    def mock_run_test(name):
        return {
            SAMPLES: [],
            MEAN: 0,
            MIN: 0,
            MAX: 0,
            ERRORS: 0,
            TEST_PASSED: True
        }
    monkeypatch.setattr(framework, "run_test", mock_run_test)
    orchestrator = Orchestrator(framework)
    results = orchestrator.run_full_analysis()
    for r in results:
        assert r[COUNT] == 0