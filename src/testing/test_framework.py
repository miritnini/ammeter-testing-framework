from typing import Dict, Any, List
import time
import numpy as np
from src.utils.logger import AppLogger
from src.utils.config import load_config
from src.testing.error_simulator import ErrorSimulator
from src.testing.error_manager import ErrorManager
from src.utils.Utils import generate_random_float

from src.config.constants import (
    MEASUREMENTS_COUNT,
    SAMPLING_FREQUENCY_HZ,
    INVALID_DEVICE,
    COUNT,
    ERRORS,
    PORT,
    MEAN,
    MEDIAN,
    STD,
    MIN,
    MAX,
    FAILURES,
    TEST_PASSED,
    EXPECTED_FREQ,
    ACTUAL_FREQ,
    SIMULATION,
    STATISTICS,
    META,
    DURATION,
    AMMETER,
    SAMPLES
)


class AmmeterTestFramework:

    def __init__(self, config_path: str = "config/config.yaml"):
        self.config = load_config(config_path)
        self.devices = self.config["ammeters"]
        self.sampling = self.config["testing"]["sampling"]
        self.sim_config = self.config.get(SIMULATION, {})
        self.simulator = ErrorSimulator(self.sim_config)
        self.error_manager = ErrorManager()

    # ---------------------------
    # RUN TEST
    # ---------------------------
    def run_test(self, ammeter_name: str) -> Dict[str, Any]:

        logger = AppLogger(ammeter_name)
        logger.info(f"Starting test for ammeter: {ammeter_name}")

        if ammeter_name not in self.devices:
            logger.error(f"Invalid device: {ammeter_name}")
            raise ValueError(f"{INVALID_DEVICE}: {ammeter_name}")
        device = self.devices[ammeter_name]
        port = device[PORT]
        logger.debug(f"Device config loaded | port={port}")

        samples: List[float] = []
        timestamps: List[float] = []
        errors = 0
        failures: List[str] = []
        count = self.sampling[MEASUREMENTS_COUNT]
        freq = self.sampling[SAMPLING_FREQUENCY_HZ]
        if freq == 0:
            logger.error("Sampling frequency is 0 → aborting test")
            raise ZeroDivisionError("sampling_frequency_hz cannot be 0")
        interval = 1.0 / freq
        next_tick = time.time()
        logger.info(f"Test config | count={count}, freq={freq}, interval={interval}")

        # ---------------------------
        # SAMPLING LOOP
        # ---------------------------
        for i in range(count):

            while time.time() < next_tick:
                time.sleep(0.001)
            try:
                value = self._read_sensor(port)
                if self.sim_config.get("enabled", False):
                    value = self.simulator.inject(value)
                samples.append(value)
                timestamps.append(time.time())
            except Exception as e:
                severity = self.error_manager.handle({}, e, ammeter_name)
                errors += 1
                logger.error(f"Error at sample {i}: {e} | severity={severity}")
                if severity == "critical":
                    failures.append(str(e))
                    logger.error("Critical failure → stopping test early")
                    break

            next_tick += interval

        # ---------------------------
        # FREQUENCY
        # ---------------------------
        if len(timestamps) > 1:
            duration = timestamps[-1] - timestamps[0]
            actual_freq = (len(timestamps) - 1) / duration if duration > 0 else 0
        else:
            duration = 0
            actual_freq = 0

        # ---------------------------
        # STATISTICS
        # ---------------------------
        arr = np.array(samples) if samples else np.array([])
        mean = float(np.mean(arr)) if len(arr) else 0
        median = float(np.median(arr)) if len(arr) else 0
        std = float(np.std(arr, ddof=1)) if len(arr) > 1 else 0
        min_v = float(np.min(arr)) if len(arr) else 0
        max_v = float(np.max(arr)) if len(arr) else 0
        logger.info( f"Stats | mean={mean:.2f}, std={std:.2f}, min={min_v:.2f}, max={max_v:.2f}" )

        # ---------------------------
        # RESULT DICT
        # ---------------------------
        return {
            AMMETER: ammeter_name,
            COUNT: len(samples),
            ERRORS: errors,
            SAMPLES: samples,
            MEAN: mean,
            MEDIAN: median,
            STD: std,
            MIN: min_v,
            MAX: max_v,
            EXPECTED_FREQ: freq,
            ACTUAL_FREQ: actual_freq,
            TEST_PASSED: len(failures) == 0,
            FAILURES: failures,
            PORT: port,

            # ---------------------------
            # STRUCTURED DATA
            # ---------------------------
            STATISTICS: {
                MEAN: mean,
                MEDIAN: median,
                STD: std,
                MIN: min_v,
                MAX: max_v,
            },

            META: {
                COUNT: len(samples),
                DURATION: duration,
                EXPECTED_FREQ: freq,
                ACTUAL_FREQ: actual_freq
            }
        }

    # ---------------------------
    # SENSOR MOCK
    # ---------------------------
    def _read_sensor(self, port: int) -> float:
        return generate_random_float(0.01, 120)

    # ---------------------------
    # MULTI RUN
    # ---------------------------
    def run_all(self) -> List[Dict[str, Any]]:
        return [self.run_test(name) for name in self.devices.keys()]