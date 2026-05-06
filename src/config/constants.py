# ---------------------------
# AMMETER NAMES
# ---------------------------
GREENLEE = "greenlee"
ENTES = "entes"
CIRCUTOR = "circutor"
ALL_AMMETERS = [GREENLEE, ENTES, CIRCUTOR]

# ---------------------------
# RESULT KEYS
# ---------------------------
AMMETER = "ammeter"
DEVICE = "device"
COUNT = "count"
ERRORS = "errors"
SAMPLES = "samples"
EXPECTED_FREQ = "expected_freq"
ACTUAL_FREQ = "actual_freq"
TEST_PASSED = "test_passed"
FAILURES = "failures"
MEAN = "mean"
MEDIAN = "median"
STD = "std"
MIN = "min"
MAX = "max"
ANOMALIES = "anomalies"
RAW_RESULT = "raw_result"

# ---------------------------
# TEST VALUES / ERRORS
# ---------------------------
INVALID_DEVICE = "invalid_device"
SENSOR_FAILURE_MSG = "sensor failure"
SIMULATION_CRASH_MSG = "simulation crash"
MAX_RUNTIME_SECONDS = 10

# ---------------------------
# FRAMEWORK CONFIG KEYS
# ---------------------------
AMMETER_TYPE = "ammeter_type"
MEASUREMENTS_COUNT = "measurements_count"
SAMPLING_FREQUENCY_HZ = "sampling_frequency_hz"
READ_SENSOR_METHOD = "_read_sensor"
INJECT = "inject"

# ---------------------------
# PYTEST KEYS
# --------------------------
TEST_PYTEST_TYPE = "pytest"
TYPE = "type"
FILE = "file"
TEST = "test"
PASSED = "passed"
ERROR = "error"
FRAMEWORK_RESULT = "framework_result"
ACCURACY_SCORE = "accuracy_score"
CV = "cv"
RANGE = "range"
ERROR_RATE = "error_rate"
TABLE = "table"
MOST_RELIABLE = "most_reliable"
RANKING = "ranking"
ANOMALY_COUNT = "anomaly_count"

# ---------------------------
# ERROR MANAGER KEYS
# ---------------------------
ERRORS_LOG = "errors_log"
ERROR_TYPE = "type"
ERROR_MESSAGE = "message"
ERROR_CONTEXT = "context"
ERROR_SEVERITY = "severity"

# ---------------------------
# ORCHESTRATOR KEYS
# ---------------------------
RUN_ID = "run_id"
TIMESTAMP = "timestamp"
METADATA = "metadata"
DEVICES = "devices"
SAMPLING = "sampling"
RESULTS = "results"
DEVICE_NAME = "device_name"
DEVICE_ALIAS = "device"
STATISTICS = "statistics"
STD_DEV = "std_dev"
MIN_VALUE = "min_value"
MAX_VALUE = "max_value"
COEFFICIENT_OF_VARIATION = "coefficient_of_variation"
STABILITY_SCORE = "stability_score"
CONSISTENCY = "consistency"
ANALYSIS_ERROR = "analysis_error"
META = "meta"
DURATION = "duration"
PORT = "port"
STATUS = "status"

# ---------------------------
# SIMULATION KEYS
# ---------------------------
SIMULATION = "simulation"
NUM_SAMPLES = "num_samples"
TIME_STEP_MIN = "time_step_min"
TIME_STEP_MAX = "time_step_max"
VOLTAGE_MIN = "voltage_min"
VOLTAGE_MAX = "voltage_max"

# ---------------------------
# ENTES SIMULATION KEYS
# ---------------------------
MAGNETIC_FIELD_MIN = "magnetic_field_min"
MAGNETIC_FIELD_MAX = "magnetic_field_max"
CALIBRATION_MIN = "calibration_min"
CALIBRATION_MAX = "calibration_max"

# ---------------------------
# GREENLEE SIMULATION KEYS
# ---------------------------
RESISTANCE_MIN = "resistance_min"
RESISTANCE_MAX = "resistance_max"