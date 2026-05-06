import json
import os

from src.utils.logger import AppLogger
from src.testing.accuracy_assessment import AccuracyAssessment
import uuid
from datetime import datetime

from src.config.constants import (
    DEVICE_ALIAS,
    STATISTICS,
    SAMPLES,
    COUNT,
    ERRORS,
    EXPECTED_FREQ,
    ACTUAL_FREQ,
    MEAN,
    MEDIAN,
    STD,
    MIN,
    MAX,
    TEST_PASSED,
    FAILURES,
    RAW_RESULT,
    TABLE,
    MOST_RELIABLE,
    RANKING,
    AMMETER,
)


class Orchestrator:

    def __init__(self, framework):
        self.framework = framework
        self.analyzer = AccuracyAssessment()
        self.logger = AppLogger("Orchestrator")

    # ---------------------------
    # RUN FULL ANALYSIS
    # ---------------------------
    def run_full_analysis(self):

        self.logger.info("Starting full analysis pipeline")
        normalized_results = []

        for device in self.framework.devices.keys():
            self.logger.info(f"Running test for {device}")
            try:
                result = self.framework.run_test(device)
            except Exception as e:
                self.logger.error(f"Test failed for {device}: {e}")
                result = {
                    AMMETER: device,
                    SAMPLES: [],
                    COUNT: 0,
                    ERRORS: 1,
                    EXPECTED_FREQ: 0,
                    ACTUAL_FREQ: 0,
                    MEAN: 0,
                    MEDIAN: 0,
                    STD: 0,
                    MIN: 0,
                    MAX: 0,
                    TEST_PASSED: False,
                    FAILURES: [str(e)],
                    RAW_RESULT: None
                }

            stats = result.get(STATISTICS, {})
            name = result.get(AMMETER) or result.get(DEVICE_ALIAS)
            if not name:
                self.logger.warning("Missing ammeter name -> using fallback device key")
                name = device

            normalized = {
                AMMETER: name,
                SAMPLES: result.get(SAMPLES, []),
                COUNT: result.get(COUNT, 0),
                ERRORS: result.get(ERRORS, 0),
                EXPECTED_FREQ: result.get(EXPECTED_FREQ, 0),
                ACTUAL_FREQ: result.get(ACTUAL_FREQ, 0),
                MEAN: stats.get(MEAN, result.get(MEAN, 0)),
                MEDIAN: stats.get(MEDIAN, result.get(MEDIAN, 0)),
                STD: stats.get(STD, result.get(STD, 0)),
                MIN: stats.get(MIN, result.get(MIN, 0)),
                MAX: stats.get(MAX, result.get(MAX, 0)),
                TEST_PASSED: result.get(TEST_PASSED, False),
                FAILURES: result.get(FAILURES, []),
                RAW_RESULT: result
            }
            normalized_results.append(normalized)

        # ---------------------------
        # RETURN CLEAN DATA FIRST
        # ---------------------------
        self.logger.info("Full analysis completed")
        return normalized_results

    # ---------------------------
    # ANALYSIS
    # ---------------------------
    def run_analysis(self, framework_results):

        comparison = self.analyzer.compare_ammeters(framework_results)
        return {
            "results": comparison[TABLE].to_dict(orient="records"),
            "most_reliable": comparison[MOST_RELIABLE],
            "ranking": comparison[RANKING],
        }

    # ---------------------------
    # EXPORT
    # ---------------------------
    def run_and_export(self, path="results/results.json"):

        results = self.run_full_analysis()
        comparison = self.analyzer.compare_ammeters(results)

        output = {
            "run_id": str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat(),
            "results": results,
            "most_reliable": comparison[MOST_RELIABLE],
            "ranking": comparison[RANKING],
        }

        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2, default=str)

        return output
