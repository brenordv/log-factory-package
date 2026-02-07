# -*- coding: utf-8 -*-
from __future__ import annotations

import logging
import os
import tempfile

import pytest


@pytest.fixture(autouse=True)
def _reset_logging():
    """Reset the logging module state between tests.

    Removes all handlers from every logger that was created during the test and
    clears the logger manager's dictionary so that ``getLogger`` returns a fresh
    logger on the next call.
    """
    yield

    manager = logging.Logger.manager
    for logger in list(manager.loggerDict.values()):
        if isinstance(logger, logging.Logger):
            logger.handlers.clear()

    root = logging.getLogger()
    root.handlers.clear()
    manager.loggerDict.clear()


@pytest.fixture()
def tmp_log_file(tmp_path):
    """Return a path string for a temporary log file inside *tmp_path*."""
    return str(tmp_path / "test.log")
