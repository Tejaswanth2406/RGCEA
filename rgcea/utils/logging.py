"""
rgcea.utils.logging — Structured logging setup for RGCEA.
"""

from __future__ import annotations

import logging
import sys
from typing import Optional


def configure_logging(
    level: str = "INFO",
    fmt: Optional[str] = None,
    stream=None,
) -> None:
    """
    Configure root logger for RGCEA.

    Parameters
    ----------
    level:
        Log level string ("DEBUG", "INFO", "WARNING", "ERROR").
    fmt:
        Log format string.  Defaults to a human-readable timestamped format.
    stream:
        Output stream.  Defaults to sys.stdout.
    """
    fmt = fmt or "%(asctime)s [%(levelname)-8s] %(name)s: %(message)s"
    handler = logging.StreamHandler(stream or sys.stdout)
    handler.setFormatter(logging.Formatter(fmt, datefmt="%Y-%m-%d %H:%M:%S"))

    root = logging.getLogger("rgcea")
    root.setLevel(getattr(logging, level.upper(), logging.INFO))
    root.handlers.clear()
    root.addHandler(handler)
    root.propagate = False
