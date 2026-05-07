from src.utils.logger import AppLogger
from src.models.error_models import ErrorEntry

from src.config.constants import (
    ERRORS_LOG,
    ERROR_TYPE,
    ERROR_MESSAGE,
    ERROR_CONTEXT,
    ERROR_SEVERITY,
)


class ErrorManager:
    """
    Central error handling system for Ammeter framework.
    """

    def __init__(self):
        self.logger = AppLogger("ErrorManager")

    def handle(self, result, error: Exception, context: str):

        error_entry = ErrorEntry(
            error_type=type(error).__name__,
            message=str(error),
            context=context,
            severity=self._resolve_severity(error)
        )
        if isinstance(result, dict):
            if ERRORS_LOG not in result:
                result[ERRORS_LOG] = []

            result[ERRORS_LOG].append({
                ERROR_TYPE: error_entry.error_type,
                ERROR_MESSAGE: error_entry.message,
                ERROR_CONTEXT: error_entry.context,
                ERROR_SEVERITY: error_entry.severity
            })

        # NEW models-based system (future)
        else:
            if not hasattr(result, "failures"):
                result.failures = []

            result.failures.append(
                f"{error_entry.context}: {error_entry.message}"
            )

        if error_entry.severity == "critical":
            self.logger.error(f"[{context}] {error_entry}")
        else:
            self.logger.warning(f"[{context}] {error_entry}")

        return error_entry.severity

    def _resolve_severity(self, error: Exception) -> str:
        if isinstance(error, ValueError):
            return "critical"
        elif isinstance(error, TimeoutError):
            return "retry"
        return "non_critical"