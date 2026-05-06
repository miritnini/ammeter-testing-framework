import logging
from src.utils.logger import AppLogger

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

    # ---------------------------
    # MAIN HANDLER
    # ---------------------------
    def handle(self, result: dict, error: Exception, context: str):

        error_entry = {
            ERROR_TYPE: type(error).__name__,
            ERROR_MESSAGE: str(error),
            ERROR_CONTEXT: context
        }

        if isinstance(error, ValueError):
            severity = "critical"
        elif isinstance(error, TimeoutError):
            severity = "retry"
        else:
            severity = "non_critical"

        error_entry[ERROR_SEVERITY] = severity
        if ERRORS_LOG not in result:
            result[ERRORS_LOG] = []

        result[ERRORS_LOG].append(error_entry)

        # logging
        if severity == "critical":
            self.logger.error(f"[{context}] {error_entry}")
        else:
            self.logger.warning(f"[{context}] {error_entry}")
        return severity