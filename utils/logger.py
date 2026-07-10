"""Run-scoped file logging for the whole suite.

Every test run gets ONE timestamped log file under results/logs, and
every module grabs its own named logger pointed at it. Console output
is handled separately by pytest live logging (see log_cli in pytest.ini),
so this module only worries about the file.
"""

import logging
import os
from datetime import datetime
from pathlib import Path

# Cache the path AND the handler so the whole run shares one log file
# and one open file handle. Building a new FileHandler per logger works,
# but it leaves a pile of open handles all pointed at the same file.
_LOG_FILE_PATH = None
_FILE_HANDLER = None

# Overridable per run, e.g. LOG_LEVEL=DEBUG pytest ...
_LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()


def _shared_file_handler() -> logging.FileHandler:
    global _LOG_FILE_PATH, _FILE_HANDLER

    if _FILE_HANDLER is not None:
        return _FILE_HANDLER

    # Resolve project paths safely
    project_root = Path(__file__).resolve().parents[1]
    log_dir = project_root / "results" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    # ONE timestamped log file per test run
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    _LOG_FILE_PATH = log_dir / f"test_run_{timestamp}.log"

    _FILE_HANDLER = logging.FileHandler(_LOG_FILE_PATH, mode="a", encoding="utf-8")
    _FILE_HANDLER.setFormatter(
        logging.Formatter("%(asctime)s | %(name)s | %(levelname)s | %(message)s")
    )
    return _FILE_HANDLER


def get_logger(name: str) -> logging.Logger:
    """Hand back a named logger wired to the shared run log file."""
    logger = logging.getLogger(name)

    # Return it as-is so handlers never stack up.
    if logger.handlers:
        return logger

    logger.setLevel(_LOG_LEVEL)
    logger.addHandler(_shared_file_handler())

    # Propagation stays ON deliberately. It lets pytest's live logging
    # and caplog see these records without any extra wiring.
    return logger
