from __future__ import annotations

import logging
import logging.config
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any, cast

LOG_LEVELS = {
    "error": logging.ERROR,
    "warn": logging.WARN,
    "warning": logging.WARN,
    "info": logging.INFO,
    "debug": logging.DEBUG,
    "trace": 5,
}


def _is_ci() -> bool:
    return os.environ.get("CI", "").lower() in {"1", "true", "yes"}


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        import json as _json

        event_time = self.formatTime(
            record,
            datefmt="%Y-%m-%dT%H:%M:%S",
        )
        event: dict[str, Any] = {
            "time": event_time,
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        std = {
            "name",
            "msg",
            "args",
            "levelname",
            "levelno",
            "pathname",
            "filename",
            "module",
            "exc_info",
            "exc_text",
            "stack_info",
            "lineno",
            "funcName",
            "created",
            "msecs",
            "relativeCreated",
            "thread",
            "threadName",
            "processName",
            "process",
        }
        for key, val in record.__dict__.items():
            if key not in std and not key.startswith("_"):
                event[key] = val
        redacted = _apply_redaction(event)
        return _json.dumps(cast(dict[str, Any], redacted), separators=(",", ":"))


def _apply_redaction(obj: object) -> object:
    import re as _re

    def redact_val(value: object) -> object:
        if isinstance(value, str):
            return _re.sub(
                r"(?i)(password|token|secret|authorization|apikey)",
                "REDACTED",
                value,
            )
        if isinstance(value, dict):
            return {k: redact_val(v) for k, v in value.items()}
        if isinstance(value, list):
            return [redact_val(v) for v in value]
        return value

    return redact_val(obj)


def setup_logging(level: str | None) -> None:
    # Add TRACE level
    if not hasattr(logging, "TRACE"):
        logging.TRACE = 5  # type: ignore[attr-defined]
        logging.addLevelName(5, "TRACE")

    # Centralized config file support
    cfg_path = os.environ.get("NOISECUTTER_LOGGING_CONFIG")
    if cfg_path and Path(cfg_path).exists():
        logging.config.fileConfig(cfg_path)
        return

    chosen = level or ("error" if _is_ci() else "info")
    numeric = LOG_LEVELS.get(chosen.lower(), logging.INFO)
    logging.basicConfig(
        format="%(asctime)s | %(levelname)s | %(message)s",
        level=numeric,
    )

    # Optional rotating file handler via env var
    log_file = os.environ.get("NOISECUTTER_LOG_FILE")
    if log_file:
        handler = RotatingFileHandler(
            log_file,
            maxBytes=int(os.environ.get("NOISECUTTER_LOG_MAX_BYTES", "1048576")),
            backupCount=int(os.environ.get("NOISECUTTER_LOG_BACKUPS", "3")),
        )
        handler.setLevel(numeric)
        fmt = logging.Formatter("%(asctime)s | %(name)s | %(levelname)s | %(message)s")
        handler.setFormatter(fmt)
        logging.getLogger().addHandler(handler)

    # Optional JSON logs for structured logging
    json_env = os.environ.get("NOISECUTTER_LOG_JSON", "").lower()
    json_flags = {"1", "true", "yes", "json"}
    if json_env in json_flags:
        json_fmt = JsonFormatter()
        root_logger = logging.getLogger()
        for stream_handler in list(root_logger.handlers):
            if isinstance(stream_handler, logging.StreamHandler):
                stream_handler.setFormatter(json_fmt)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
