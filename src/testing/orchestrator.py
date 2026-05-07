from src.models.ammeter_result import NormalizedAmmeterResult
from src.models.statistics_model import Statistics
from src.testing.accuracy_assessment import AccuracyAssessment
from src.utils.logger import AppLogger
import json, os, uuid
from datetime import datetime

class Orchestrator:

    def __init__(self, framework):
        self.framework = framework
        self.analyzer = AccuracyAssessment()
        self.logger = AppLogger("Orchestrator")

    def normalize_result(self, result, device_name):
        try:
            if hasattr(result, "sensor"):
                samples = result.sensor.samples
                count = result.sensor.count
                errors = result.sensor.errors
                stats = result.statistics
                test_passed = result.test_passed
                failures = result.failures
                expected_freq = result.expected_freq
                actual_freq = result.actual_freq
            else:
                # Could be Exception or manual FailResult
                samples = getattr(result, "samples", [])
                count = getattr(result, "count", 0)
                errors = getattr(result, "errors", 1)
                stats = getattr(result, "statistics", Statistics(0,0,0,0,0))
                test_passed = getattr(result, "test_passed", False)
                failures = getattr(result, "failures", [str(result)])
                expected_freq = getattr(result, "expected_freq", 0.0)
                actual_freq = getattr(result, "actual_freq", 0.0)

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
        except Exception as e:
            # Fallback if normalization fails
            stats = Statistics(0,0,0,0,0)
            return NormalizedAmmeterResult(
                ammeter=str(device_name),
                samples=[],
                count=0,
                errors=1,
                expected_freq=0.0,
                actual_freq=0.0,
                mean=0.0,
                median=0.0,
                std=0.0,
                min=0.0,
                max=0.0,
                test_passed=False,
                failures=[str(e)],
                raw_result=None,
                statistics=stats
            )

    def run_full_analysis(self):
        self.logger.info("Starting full analysis pipeline")
        normalized_results = []

        for device in self.framework.devices.keys():
            self.logger.info(f"Running test for {device}")
            try:
                result = self.framework.run_test(device)
            except Exception as e:
                self.logger.error(f"Test failed for {device}: {e}")
                result = e

            normalized = self.normalize_result(result, device)
            normalized_results.append(normalized)

        self.logger.info("Full analysis completed")
        return normalized_results

    def run_and_export(self, path="results/results.json"):
        results = self.run_full_analysis()
        comparison = self.analyzer.compare_ammeters(results)

        output = {
            "run_id": str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat(),
            "results": results,
            "most_reliable": comparison["most_reliable"],
            "ranking": comparison["ranking"],
        }

        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2, default=str)

        return output