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
        assert hasattr(r, "ammeter")
        assert hasattr(r, "samples")
        assert hasattr(r, "statistics")
        assert hasattr(r, "test_passed")


# ---------------------------
# ALL DEVICES PRESENT
# ---------------------------
def test_all_devices_present(orchestrator):
    results = orchestrator.run_full_analysis()
    names = [r.ammeter for r in results]
    assert set(names) == set(ALL_AMMETERS)


# ---------------------------
# NORMALIZATION TEST
# ---------------------------
def test_normalization_no_missing_fields(orchestrator):
    results = orchestrator.run_full_analysis()
    for r in results:
        assert r.statistics.mean is not None
        assert r.statistics.min is not None
        assert r.statistics.max is not None
        assert r.count is not None
        assert r.errors is not None


# ---------------------------
# RAW RESULT EXISTS
# ---------------------------
def test_raw_result_exists(orchestrator):
    results = orchestrator.run_full_analysis()
    for r in results:
        assert hasattr(r, "raw_result")


# ---------------------------
# PARTIAL FAILURE TEST
# ---------------------------
def test_partial_failure(monkeypatch, framework):
    def mock_run_test(device):
        return type("FailResult", (), {
            "ammeter": device,
            "samples": [],
            "errors": 1,
            "test_passed": False,
            "count": 0,
            "statistics": type("Stats", (), {"mean": 0, "min": 0, "max": 0})(),
            "raw_result": None
        })()
    monkeypatch.setattr(framework, "run_test", mock_run_test)
    orchestrator = Orchestrator(framework)
    results = orchestrator.run_full_analysis()
    for r in results:
        assert r.ammeter in ALL_AMMETERS
        assert r.samples == []
        assert r.errors >= 0
        assert r.test_passed is False


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
        samples = r.samples
        assert isinstance(samples, list)
        assert r.count == len(samples)


# ---------------------------
# EMPTY RESULTS SAFETY
# ---------------------------
def test_empty_result_handling(monkeypatch, framework):
    def mock_run_test(name):
        return type("EmptyResult", (), {
            "samples": [],
            "statistics": type("Stats", (), {"mean": 0, "min": 0, "max": 0})(),
            "errors": 0,
            "test_passed": True,
            "count": 0,
            "raw_result": None,
            "ammeter": name
        })()
    monkeypatch.setattr(framework, "run_test", mock_run_test)
    orchestrator = Orchestrator(framework)
    results = orchestrator.run_full_analysis()
    for r in results:
        assert r.count == 0