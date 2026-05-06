import os
import pandas as pd
import pytest

from src.config.constants import (
    TEST_PYTEST_TYPE,
    TYPE,
    FILE,
    TEST,
    PASSED,
    ERROR,
    FRAMEWORK_RESULT,
)

ALL_RESULTS = []
RESULT_FILE = os.path.join( os.path.dirname(__file__), "..", "results.json")

def safe(obj):
    if isinstance(obj, pd.DataFrame):
        return obj.to_dict(orient="records")
    return obj

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    if report.when == "call":
        framework_result = getattr(item, "result", None)
        ALL_RESULTS.append({
            TYPE: TEST_PYTEST_TYPE,
            FILE: item.location[0],
            TEST: item.name,
            PASSED: report.passed,
            ERROR: str(report.longrepr) if report.failed else None,
            FRAMEWORK_RESULT: safe(framework_result)
        })