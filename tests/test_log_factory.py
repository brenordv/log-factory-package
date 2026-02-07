# -*- coding: utf-8 -*-
from __future__ import annotations

import logging
from logging.handlers import TimedRotatingFileHandler

import pytest

from simple_log_factory.log_factory import (
    LogContext,
    LogContextGenerators,
    _attach_handlers,
    _check_unique_handler_types,
    _get_handlers,
    log_factory,
)


# ---- _get_handlers ---------------------------------------------------------


class TestGetHandlers:
    def test_console_only(self):
        handlers = _get_handlers(to_console=True, log_file=None, rotate_file_by_day=False)
        assert len(handlers) == 1
        assert isinstance(handlers[0], logging.StreamHandler)

    def test_file_only(self, tmp_log_file):
        handlers = _get_handlers(to_console=False, log_file=tmp_log_file, rotate_file_by_day=False)
        assert len(handlers) == 1
        assert isinstance(handlers[0], logging.FileHandler)

    def test_rotating_file(self, tmp_log_file):
        handlers = _get_handlers(to_console=False, log_file=tmp_log_file, rotate_file_by_day=True)
        assert len(handlers) == 1
        assert isinstance(handlers[0], TimedRotatingFileHandler)

    def test_console_and_file(self, tmp_log_file):
        handlers = _get_handlers(to_console=True, log_file=tmp_log_file, rotate_file_by_day=False)
        assert len(handlers) == 2
        assert isinstance(handlers[0], logging.StreamHandler)
        assert isinstance(handlers[1], logging.FileHandler)

    def test_no_handlers(self):
        handlers = _get_handlers(to_console=False, log_file=None, rotate_file_by_day=False)
        assert handlers == []


# ---- log_factory (main function) -------------------------------------------


class TestLogFactory:
    def test_returns_logger(self):
        logger = log_factory("test_basic")
        assert isinstance(logger, logging.Logger)
        assert logger.name == "test_basic"

    def test_default_level_is_debug(self):
        logger = log_factory("test_debug_level")
        assert logger.level == logging.DEBUG

    def test_custom_level_int(self):
        logger = log_factory("test_info_level", log_level=logging.INFO)
        assert logger.level == logging.INFO

    def test_custom_level_string(self):
        logger = log_factory("test_level_str", log_level="warning")
        assert logger.level == logging.WARNING

    def test_file_handler(self, tmp_log_file):
        logger = log_factory("test_file", log_file=tmp_log_file, to_console=False)
        handler_types = [type(h) for h in logger.handlers]
        assert TimedRotatingFileHandler in handler_types

    def test_custom_handler_single(self):
        custom = logging.StreamHandler()
        logger = log_factory("test_custom_single", to_console=False, custom_handlers=custom)
        assert custom in logger.handlers

    def test_custom_handler_list(self):
        h1 = logging.StreamHandler()
        h2 = logging.StreamHandler()
        logger = log_factory("test_custom_list", to_console=False, custom_handlers=[h1, h2])
        assert h1 in logger.handlers
        assert h2 in logger.handlers

    def test_unique_handler_types(self):
        logger = log_factory("test_unique", to_console=True, unique_handler_types=True)
        stream_handler_count = sum(1 for h in logger.handlers if isinstance(h, logging.StreamHandler))
        assert stream_handler_count <= 1

    def test_custom_format(self):
        fmt = "%(message)s"
        logger = log_factory("test_fmt", log_format=fmt)
        for h in logger.handlers:
            assert h.formatter._fmt == fmt

    def test_custom_time_format(self):
        logger = log_factory("test_time_fmt", rotate_file_by_day=False, log_time_format="%Y")
        for h in logger.handlers:
            assert h.formatter.datefmt == "%Y"


# ---- Bug regression tests --------------------------------------------------


class TestBugRegressions:
    def test_bug1_console_only_keeps_date(self):
        """Bug 1: Console-only logger should NOT use time-only format."""
        logger = log_factory("bug1_test", rotate_file_by_day=True, log_file=None)
        for handler in logger.handlers:
            # datefmt should be None (the default) when no log_file is set.
            assert handler.formatter.datefmt is None

    def test_bug1_rotating_file_uses_time_only(self, tmp_log_file):
        """Bug 1: With a rotating file, time-only format IS correct."""
        logger = log_factory("bug1_file", log_file=tmp_log_file, rotate_file_by_day=True)
        for handler in logger.handlers:
            assert handler.formatter.datefmt == "%H:%M:%S"

    def test_bug2_root_logger_parent_none(self):
        """Bug 2: _check_unique_handler_types must not crash when parent is None."""
        root = logging.getLogger()
        # root.parent is None
        result = _check_unique_handler_types(root, unique_handler_types=True)
        assert result is root

    def test_bug3_attach_handlers_parent_none(self):
        """Bug 3: _attach_handlers must not crash when parent is None."""
        root = logging.getLogger()
        handler = logging.StreamHandler()
        fmt = logging.Formatter("%(message)s")
        result = _attach_handlers(root, [handler], logging.DEBUG, fmt, unique_handler_types=False)
        assert handler in result.handlers

    def test_bug4_handler_list_not_mutated(self):
        """Bug 4: Calling _attach_handlers should not mutate logger.handlers via aliasing."""
        logger = logging.getLogger("bug4_test")
        original_handler = logging.StreamHandler()
        logger.addHandler(original_handler)
        original_count = len(logger.handlers)

        new_handler = logging.StreamHandler()
        fmt = logging.Formatter("%(message)s")
        _attach_handlers(logger, [new_handler], logging.DEBUG, fmt, unique_handler_types=False)

        # The new handler should have been added via addHandler, not via extend.
        # The key check: there should be exactly original_count + 1 handlers.
        assert len(logger.handlers) == original_count + 1

    def test_bug5_import_is_callable(self):
        """Bug 5: Importing log_factory from the package should give a function."""
        from simple_log_factory import log_factory as lf

        assert callable(lf)
        logger = lf("bug5_test")
        assert isinstance(logger, logging.Logger)

    def test_bug6_old_dunder_names_removed(self):
        """Bug 6: Old dunder-style private names no longer exist."""
        import simple_log_factory.log_factory as mod

        assert not hasattr(mod, "_get_handlers_")
        assert not hasattr(mod, "_check_unique_handler_types_")
        assert not hasattr(mod, "_attach_handlers_")


# ---- log_name validation ---------------------------------------------------


class TestLogNameValidation:
    def test_empty_string_raises(self):
        with pytest.raises(ValueError, match="non-empty string"):
            log_factory("")

    def test_whitespace_only_raises(self):
        with pytest.raises(ValueError, match="non-empty string"):
            log_factory("   ")

    def test_none_raises(self):
        with pytest.raises(ValueError, match="non-empty string"):
            log_factory(None)  # type: ignore[arg-type]

    def test_non_string_raises(self):
        with pytest.raises(ValueError, match="non-empty string"):
            log_factory(123)  # type: ignore[arg-type]
