from __future__ import annotations

import json
import logging
from pathlib import Path


def configure_logging(data_dir: str) -> logging.Logger:
    logs_dir = Path(data_dir) / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    log_file = logs_dir / "jobpipeline.log"
    logger = logging.getLogger("jobpipeline")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    handler = logging.FileHandler(log_file, encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(handler)
    return logger


def log_event(logger: logging.Logger, event: dict) -> None:
    logger.info(json.dumps(event, ensure_ascii=False))
