"""Central loguru configuration.

Importing this module configures the global `loguru.logger` once.
API keys must never be logged — use user email for identity instead.
"""
import sys
from pathlib import Path

from loguru import logger

_CONFIGURED = False

LOG_DIR = Path("logs")
LOG_FORMAT = (
    "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
    "<level>{message}</level>"
)


def configure_logging() -> None:
    """Configure loguru sinks. Idempotent."""
    global _CONFIGURED
    if _CONFIGURED:
        return

    logger.remove()

    # Console sink
    logger.add(
        sys.stderr,
        level="INFO",
        format=LOG_FORMAT,
        colorize=True,
        backtrace=True,
        diagnose=False,  # diagnose=True leaks variable values; keep off
    )

    # File sink with rotation
    LOG_DIR.mkdir(exist_ok=True)
    logger.add(
        LOG_DIR / "app.log",
        level="INFO",
        format=LOG_FORMAT,
        rotation="10 MB",
        retention="14 days",
        compression="zip",
        enqueue=True,
        backtrace=True,
        diagnose=False,
    )

    # Separate error log for quick triage
    logger.add(
        LOG_DIR / "error.log",
        level="ERROR",
        format=LOG_FORMAT,
        rotation="10 MB",
        retention="30 days",
        compression="zip",
        enqueue=True,
        backtrace=True,
        diagnose=False,
    )

    _CONFIGURED = True


def mask_api_key(key: str | None) -> str:
    """Render api_key as `****last4` for rare legitimate cases."""
    if not key:
        return "<none>"
    if len(key) <= 4:
        return "****"
    return f"****{key[-4:]}"
