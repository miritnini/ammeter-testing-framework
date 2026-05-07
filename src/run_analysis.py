import json
import os
from src.testing.test_framework import AmmeterTestFramework
from src.testing.orchestrator import Orchestrator
from src.testing.accuracy_assessment import AccuracyAssessment


ANALYSIS_FILE = "results/analysis_results.json"

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
    table_df = comparison["table"]

    # ---------------------------
    # SAVE OUTPUT
    # ---------------------------
    os.makedirs("results", exist_ok=True)

    output = {
        "results": results,

        # FULL TABLE (keeps structure)
        "accuracy_table": {
            "columns": list(table_df.columns),
            "index": list(table_df.index),
            "data": table_df.values.tolist()
        },

        "comparison": {
            "most_reliable": comparison["most_reliable"],
            "ranking": comparison["ranking"]
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
    print(comparison["most_reliable"])

    print("\n==================== RANKING ====================")
    print(comparison["ranking"])


if __name__ == "__main__":
    main()