import json
import os

from src.testing.test_framework import AmmeterTestFramework
from src.testing.orchestrator import Orchestrator
from src.testing.accuracy_assessment import AccuracyAssessment
from src.models.ammeter_result import NormalizedAmmeterResult

from src.config.constants import (
    AMMETER,
    SAMPLES,
    ERRORS,
    MEAN,
    MEDIAN,
    STD,
    MIN,
    MAX,
    COUNT,
    TABLE,
    MOST_RELIABLE,
    RANKING
)

ANALYSIS_FILE = "results/analysis_results.json"


def ammeter_to_dict(r: NormalizedAmmeterResult):
    stats = getattr(r, "statistics", None)
    return {
        AMMETER: r.ammeter,
        SAMPLES: r.samples,
        COUNT: r.count,
        ERRORS: r.errors,
        "expected_freq": r.expected_freq,
        "actual_freq": r.actual_freq,
        MEAN: getattr(stats, MEAN, r.mean) if stats else r.mean,
        MEDIAN: getattr(stats, MEDIAN, r.median) if stats else r.median,
        STD: getattr(stats, STD, r.std) if stats else r.std,
        MIN: getattr(stats, MIN, r.min) if stats else r.min,
        MAX: getattr(stats, MAX, r.max) if stats else r.max,
        "test_passed": r.test_passed,
        "failures": r.failures,
        "raw_result": r.raw_result if isinstance(r.raw_result, dict) else str(r.raw_result),
    }


def main():
    framework = AmmeterTestFramework()
    orchestrator = Orchestrator(framework)

    # ---------------------------
    # RUN TESTS
    # ---------------------------
    results = orchestrator.run_full_analysis()

    # ---------------------------
    # ANALYSIS
    # ---------------------------
    analyzer = AccuracyAssessment()
    comparison = analyzer.compare_ammeters(results)

    table_df = comparison[TABLE]

    # ---------------------------
    # SAVE OUTPUT
    # ---------------------------
    os.makedirs("results", exist_ok=True)

    output = {
        "results": [ammeter_to_dict(r) for r in results],

        # FULL TABLE
        "accuracy_table": {
            "columns": list(table_df.columns),
            "index": list(table_df.index),
            "data": table_df.values.tolist()
        },

        "comparison": {
            MOST_RELIABLE: comparison[MOST_RELIABLE],
            RANKING: comparison[RANKING]
        }
    }

    with open(ANALYSIS_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

    # ---------------------------
    # PRINT
    # ---------------------------
    print("\n==================== ACCURACY TABLE ====================")
    print(table_df.to_string(float_format="%.4f"))

    print("\n==================== MOST RELIABLE ====================")
    print(comparison[MOST_RELIABLE])

    print("\n==================== RANKING ====================")
    print(comparison[RANKING])


if __name__ == "__main__":
    main()