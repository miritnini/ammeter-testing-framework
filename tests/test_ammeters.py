
import time
import pytest
from src.testing.test_framework import AmmeterTestFramework
from src.testing.accuracy_assessment import AccuracyAssessment
from src.models.ammeter_result import NormalizedAmmeterResult
from src.models.statistics_model import Statistics


from src.config.constants import (
    ALL_AMMETERS,
    GREENLEE,
    ENTES,
    CIRCUTOR,
    INVALID_DEVICE,
    SENSOR_FAILURE_MSG,
    SIMULATION_CRASH_MSG,
    MAX_RUNTIME_SECONDS,
    AMMETER_TYPE,
    ANOMALIES,
    SAMPLING_FREQUENCY_HZ,
    MEASUREMENTS_COUNT,
    READ_SENSOR_METHOD,
    INJECT,
)

# =========================================================
# HELPER FUNCTION: Normalize result for testing
# =========================================================
def normalize_result_for_test(result, device_name):
    try:
        samples = result.sensor.samples
        count = result.sensor.count
        errors = result.sensor.errors
        stats = result.statistics
        test_passed = result.test_passed
        failures = result.failures
        expected_freq = result.expected_freq
        actual_freq = result.actual_freq
    except AttributeError:
        # fallback for exceptions or incomplete results
        samples = []
        count = 0
        errors = 1
        stats = Statistics(0, 0, 0, 0, 0)
        test_passed = False
        failures = [str(result)]
        expected_freq = 0
        actual_freq = 0

    return NormalizedAmmeterResult(
        ammeter=getattr(result, "ammeter", device_name),
        samples=samples,
        count=count,
        errors=errors,
        expected_freq=expected_freq,
        actual_freq=actual_freq,
        mean=stats.mean,
        median=stats.median,
        std=stats.std,
        min=stats.min,
        max=stats.max,
        test_passed=test_passed,
        failures=failures,
        raw_result=result,
        statistics=stats
    )

# =========================================================
# FIXTURE
# =========================================================
@pytest.fixture(scope="module")
def framework():
    return AmmeterTestFramework()


# =========================================================
# BASIC TEST
# =========================================================
@pytest.mark.parametrize(AMMETER_TYPE, ALL_AMMETERS)
def test_ammeter_basic_pass(framework, ammeter_type):
    result = framework.run_test(ammeter_type)
    norm_result = normalize_result_for_test(result, ammeter_type)
    assert norm_result.count >= 0
    assert norm_result.errors >= 0
    assert isinstance(norm_result.samples, list)


# =========================================================
# VALIDATION TEST
# =========================================================
@pytest.mark.parametrize(AMMETER_TYPE, ALL_AMMETERS)
def test_ammeter_validation_pass(framework, ammeter_type, request):
    result = framework.run_test(ammeter_type)
    norm_result = normalize_result_for_test(result, ammeter_type)
    request.node.result = norm_result
    assert norm_result.test_passed is True, f"Failures: {norm_result.failures}"


# =========================================================
# SAMPLING FREQUENCY TEST
# =========================================================
@pytest.mark.parametrize(AMMETER_TYPE, ALL_AMMETERS)
def test_sampling_frequency(framework, ammeter_type, request):
    result = framework.run_test(ammeter_type)
    norm_result = normalize_result_for_test(result, ammeter_type)
    request.node.result = norm_result
    assert abs(norm_result.actual_freq - norm_result.expected_freq) < 0.5


# =========================================================
# NEGATIVE VALUES TEST
# =========================================================
@pytest.mark.parametrize(AMMETER_TYPE, ALL_AMMETERS)
def test_no_negative_values(framework, ammeter_type, request):
    result = framework.run_test(ammeter_type)
    norm_result = normalize_result_for_test(result, ammeter_type)
    negatives = [v for v in norm_result.samples if v < 0]
    assert len(negatives) == 0


# =========================================================
# INVALID AMMETER TEST
# =========================================================
def test_invalid_ammeter():
    framework = AmmeterTestFramework()
    with pytest.raises(ValueError):
        framework.run_test(INVALID_DEVICE)


# =========================================================
# ACCURACY TEST
# =========================================================
def test_accuracy(framework, request):
    results = [framework.run_test(a) for a in [GREENLEE, ENTES, CIRCUTOR]]
    normalized_results = [normalize_result_for_test(r, r.ammeter) for r in results]
    analyzer = AccuracyAssessment()
    comparison = analyzer.compare_ammeters(normalized_results)
    request.node.result = {"accuracy_comparison": comparison}
    df = comparison["table"]
    analyzer.plot_comparison(df)
    print("Most reliable:", comparison["most_reliable"])
    print(df)


# =========================================================
# EMPTY SAMPLES TEST
# =========================================================
def test_empty_samples(monkeypatch, framework):
    def mock_read_sensor(port):
        raise Exception(SENSOR_FAILURE_MSG)
    monkeypatch.setattr(framework, READ_SENSOR_METHOD, mock_read_sensor)
    result = framework.run_test(GREENLEE)
    norm_result = normalize_result_for_test(result, GREENLEE)
    assert norm_result.count == 0
    assert norm_result.errors > 0
    assert hasattr(norm_result, "test_passed")


# =========================================================
# ERROR SIMULATOR TEST
# =========================================================
def test_simulator_failure(monkeypatch, framework):
    def mock_inject(value):
        raise Exception(SIMULATION_CRASH_MSG)
    monkeypatch.setattr(framework.simulator, INJECT, mock_inject)
    result = framework.run_test(ENTES)
    norm_result = normalize_result_for_test(result, ENTES)
    assert hasattr(norm_result, "samples")


# =========================================================
# EXTREME VALUES TEST
# =========================================================
def test_extreme_values(monkeypatch, framework):
    values = [1, 2, 3, 1000000, -999999]
    def mock_read_sensor(port):
        return values.pop(0) if values else 1
    monkeypatch.setattr(framework, READ_SENSOR_METHOD, mock_read_sensor)
    result = framework.run_test(CIRCUTOR)
    norm_result = normalize_result_for_test(result, CIRCUTOR)
    assert norm_result.count > 0
    assert isinstance(norm_result.statistics.mean, float)


# =========================================================
# SAMPLING FREQUENCY = 0 TEST
# =========================================================
def test_zero_frequency():
    framework = AmmeterTestFramework()
    framework.sampling[SAMPLING_FREQUENCY_HZ] = 0
    with pytest.raises(ZeroDivisionError):
        framework.run_test(GREENLEE)


# =========================================================
# COUNT = 0 TEST
# =========================================================
def test_zero_measurements(framework):
    framework.sampling[MEASUREMENTS_COUNT] = 0
    result = framework.run_test(GREENLEE)
    norm_result = normalize_result_for_test(result, GREENLEE)
    assert norm_result.count == 0
    assert norm_result.samples == []


# =========================================================
# PERFORMANCE SANITY TEST
# =========================================================
def test_runtime_limit(framework):
    start = time.time()
    result = framework.run_test(ENTES)
    norm_result = normalize_result_for_test(result, ENTES)
    duration = time.time() - start
    assert duration < MAX_RUNTIME_SECONDS


# =========================================================
# CONSISTENCY (REPEATABILITY) TEST
# =========================================================
def test_repeatability(framework):
    r1 = normalize_result_for_test(framework.run_test(GREENLEE), GREENLEE)
    r2 = normalize_result_for_test(framework.run_test(GREENLEE), GREENLEE)
    assert r1.count == r2.count


# =========================================================
# ANOMALY DETECTION TEST
# =========================================================
def test_anomalies_exist(framework):
    result = framework.run_test(CIRCUTOR)
    norm_result = normalize_result_for_test(result, CIRCUTOR)
    if hasattr(norm_result, ANOMALIES):
        anomalies = getattr(norm_result, ANOMALIES)
        assert isinstance(anomalies, list)