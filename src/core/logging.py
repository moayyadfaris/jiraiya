import logging
import structlog
import sys
from asgi_correlation_id import correlation_id

def configure_logging(log_level: str = "INFO"):
    """
    Configure structlog and standard logging.
    """
    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.format_exc_info,
        structlog.processors.TimeStamper(fmt="iso"),
        _add_correlation_id,
    ]

    structlog.configure(
        processors=shared_processors + [
            structlog.processors.JSONRenderer(),
        ],
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Configure standard library logging to use structlog
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=log_level.upper(),
    )

def _add_correlation_id(logger, method_name, event_dict):
    """Add request correlation ID to log event."""
    request_id = correlation_id.get()
    if request_id:
        event_dict["correlation_id"] = request_id
    return event_dict
