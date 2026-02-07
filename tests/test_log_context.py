# -*- coding: utf-8 -*-
from __future__ import annotations

import dataclasses
import logging

import pytest

from simple_log_factory.log_factory import LogContext, LogContextGenerators


class TestLogContext:
    def test_is_frozen_dataclass(self):
        assert dataclasses.is_dataclass(LogContext)
        ctx = LogContext(
            exception=lambda m: None,
            error=lambda m: None,
            warning=lambda m: None,
            info=lambda m: None,
            debug=lambda m: None,
        )
        with pytest.raises(dataclasses.FrozenInstanceError):
            ctx.info = lambda m: None  # type: ignore[misc]

    def test_fields(self):
        fields = {f.name for f in dataclasses.fields(LogContext)}
        assert fields == {"exception", "error", "warning", "info", "debug"}

    def test_equality(self):
        fn = lambda m: None  # noqa: E731
        a = LogContext(exception=fn, error=fn, warning=fn, info=fn, debug=fn)
        b = LogContext(exception=fn, error=fn, warning=fn, info=fn, debug=fn)
        assert a == b

    def test_repr(self):
        fn = lambda m: None  # noqa: E731
        ctx = LogContext(exception=fn, error=fn, warning=fn, info=fn, debug=fn)
        assert "LogContext" in repr(ctx)


class TestLogContextGenerators:
    def test_creates_logger(self):
        gen = LogContextGenerators(log_name="ctx_gen_test")
        assert isinstance(gen.logger, logging.Logger)

    def test_get_logger_for_context_returns_log_context(self):
        gen = LogContextGenerators(log_name="ctx_gen_test2")
        ctx = gen.get_logger_for_context(request_id="abc")
        assert isinstance(ctx, LogContext)
        assert callable(ctx.info)

    def test_context_logs_message(self, capfd):
        gen = LogContextGenerators(log_name="ctx_gen_log")
        ctx = gen.get_logger_for_context()
        ctx.info("hello from context")
        captured = capfd.readouterr()
        # The message should appear in stderr (StreamHandler default)
        assert "hello from context" in captured.err
