import logging
import logging.config as config
import logging
import logging.config as config


def apply_default_logging(
    log_level: str = "INFO",
    log_file: str = None,
    use_json: bool = False
):
    
    """
    Applies a default logging configuration.

    Parameters:
    - log_level: Global log level (default: INFO)
    - log_file: If provided, logs will also be saved to this file
    - use_json: If True, use JSON formatter for logs
    """

    base_formatter = {
        "format": "%(levelname)s [%(asctime)s] %(name)s - %(message)s",
        "datefmt": "%Y-%m-%d %H:%M:%S"
    }

    json_formatter = {
        "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
        "datefmt": "%Y-%m-%d %H:%M:%S",
        "format": "%(levelname)s %(asctime)s %(name)s %(message)s"
    }

    handlers = {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "json" if use_json else "default",
        }
    }

    if log_file:
        handlers["file"] = {
            "class": "logging.FileHandler",
            "filename": log_file,
            "formatter": "json" if use_json else "default",
        }

    LOGGING_CONFIG = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": base_formatter,
            "json": json_formatter
        },
        "handlers": handlers,
        "loggers": {
            "alatpay": {
                "handlers": list(handlers.keys()),
                "level": log_level.upper(),
                "propagate": False
            },
            "stripe": {
                "handlers": list(handlers.keys()),
                "level": log_level.upper(),
                "propagate": False
            }
        }
    }

    config.dictConfig(LOGGING_CONFIG)

def get_logger(name: str = "payment") -> logging.Logger:
    """
    Returns a logger with a NullHandler if no handlers are attached.
    """
    logger = logging.getLogger(name)
    
    if not logger.hasHandlers():
        logger.addHandler(logging.NullHandler())
    
    return logger
