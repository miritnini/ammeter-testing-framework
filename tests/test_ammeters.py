import time
import pytest
from src.testing.test_framework import AmmeterTestFramework
from src.testing.accuracy_assessment import AccuracyAssessment
import matplotlib.pyplot as plt


from src.config.constants import (
    ALL_AMMETERS,
    GREENLEE,
    ENTES,
    CIRCUTOR,
    INVALID_DEVICE,
    SENSOR_FAILURE_MSG,
    SIMULATION_CRASH_MSG,
    MAX_RUNTIME_SECONDS,
    COUNT,
    SAMPLES,
    MEAN,
    ERRORS,
    FAILURES,
    TEST_PASSED,
    EXPECTED_FREQ,
    ACTUAL_FREQ,
    INJECT,
    AMMETER_TYPE,
    ANOMALIES,
    SAMPLING_FREQUENCY_HZ,
    MEASUREMENTS_COUNT,
    READ_SENSOR_METHOD,
)

# ---------------------------
# FIXTURE
# ---------------------------
@pytest.fixture(scope="module")
def framework():
    return AmmeterTestFramework()


# ---------------------------
# BASIC TEST
# ---------------------------
@pytest.mark.parametrize(AMMETER_TYPE, ALL_AMMETERS)
def test_ammeter_basic_pass(framework, ammeter_type):
    result = framework.run_test(ammeter_type)
    assert result is not None
    assert result[COUNT] >= 0
    assert result[ERRORS] >= 0
    assert SAMPLES in result
    assert isinstance(result[SAMPLES], list)


# ---------------------------
# VALIDATION TEST (TCS)
# ---------------------------
@pytest.mark.parametrize(AMMETER_TYPE, ALL_AMMETERS)
def test_ammeter_validation_pass(framework, ammeter_type, request):
    result = framework.run_test(ammeter_type)
    request.node.result = result
    assert result[TEST_PASSED] is True, f"Failures: {result[FAILURES]}"


# ---------------------------
# SAMPLING FREQUENCY TEST
# ---------------------------
@pytest.mark.parametrize(AMMETER_TYPE, ALL_AMMETERS)
def test_sampling_frequency(framework, ammeter_type, request):
    result = framework.run_test(ammeter_type)
    request.node.result = result
    expected = result[EXPECTED_FREQ]
    actual = result[ACTUAL_FREQ]
    assert abs(actual - expected) < 0.5


# ---------------------------
# NEGATIVE VALUES TEST
# ---------------------------
@pytest.mark.parametrize(AMMETER_TYPE, ALL_AMMETERS)
def test_no_negative_values(framework, ammeter_type, request):
    result = framework.run_test(ammeter_type)
    request.node.result = result
    negatives = [v for v in result[SAMPLES] if v < 0]
    assert len(negatives) == 0


# ---------------------------
# INVALID AMMETER TEST
# ---------------------------
def test_invalid_ammeter():
    framework = AmmeterTestFramework()
    with pytest.raises(ValueError):
        framework.run_test(INVALID_DEVICE)


# ---------------------------
# ACCURACY TEST
# ---------------------------
def test_accuracy(framework, request):
    greenlee = framework.run_test(GREENLEE)
    entes = framework.run_test(ENTES)
    circutor = framework.run_test(CIRCUTOR)
    analyzer = AccuracyAssessment()
    comparison = analyzer.compare_ammeters([greenlee, entes, circutor])
    request.node.result = {"accuracy_comparison": comparison}
    df = comparison["table"]
    analyzer.plot_comparison(df)
    print("Most reliable:", comparison["most_reliable"])
    print(df)


# ---------------------------
# EMPTY SAMPLES TEST
# ---------------------------
def test_empty_samples(monkeypatch, framework):
    def mock_read_sensor(port):
        raise Exception(SENSOR_FAILURE_MSG)
    monkeypatch.setattr(framework, READ_SENSOR_METHOD, mock_read_sensor)
    result = framework.run_test(GREENLEE)
    assert result[COUNT] == 0
    assert result[ERRORS] > 0
    assert TEST_PASSED in result


# ---------------------------
# ERROR SIMULATOR TEST
# ---------------------------
def test_simulator_failure(monkeypatch, framework):
    def mock_inject(value):
        raise Exception(SIMULATION_CRASH_MSG)
    monkeypatch.setattr(framework.simulator, INJECT, mock_inject)
    result = framework.run_test(ENTES)
    assert SAMPLES in result


# ---------------------------
# EXTREME VALUES TEST
# ---------------------------
def test_extreme_values(monkeypatch, framework):
    values = [1, 2, 3, 1000000, -999999]
    def mock_read_sensor(port):
        return values.pop(0) if values else 1
    monkeypatch.setattr(framework, READ_SENSOR_METHOD, mock_read_sensor)
    result = framework.run_test(CIRCUTOR)
    assert result[COUNT] > 0
    assert isinstance(result[MEAN], float)


# ---------------------------
# SAMPLING FREQUENCY = 0 TEST
# ---------------------------
def test_zero_frequency():
    framework = AmmeterTestFramework()
    framework.sampling[SAMPLING_FREQUENCY_HZ] = 0
    with pytest.raises(ZeroDivisionError):
        framework.run_test(GREENLEE)


# ---------------------------
# COUNT = 0 TEST
# ---------------------------
def test_zero_measurements(framework):
    framework.sampling[MEASUREMENTS_COUNT] = 0
    result = framework.run_test(GREENLEE)
    assert result[COUNT] == 0
    assert result[SAMPLES] == []


# ---------------------------
# PERFORMANCE SANITY TEST
# ---------------------------
def test_runtime_limit(framework):
    start = time.time()
    framework.run_test(ENTES)
    duration = time.time() - start
    assert duration < MAX_RUNTIME_SECONDS


# ---------------------------
# CONSISTENCY (REPEATABILITY) TEST
# ---------------------------
def test_repeatability(framework):
    r1 = framework.run_test(GREENLEE)
    r2 = framework.run_test(GREENLEE)
    assert r1[COUNT] == r2[COUNT]


# ---------------------------
# ANOMALY DETECTION TEST
# ---------------------------
def test_anomalies_exist(framework):
    result = framework.run_test(CIRCUTOR)
    if ANOMALIES in result:
        assert isinstance(result[ANOMALIES], list)