from __future__ import annotations

import logging
from importlib.metadata import version


class TestPackageInit:
    def test_import_log_factory_function(self):
        from simple_log_factory import log_factory

        assert callable(log_factory)

    def test_import_log_context(self):
        from simple_log_factory import LogContext

        assert LogContext is not None

    def test_import_log_context_generators(self):
        from simple_log_factory import LogContextGenerators

        assert LogContextGenerators is not None

    def test_all_attribute(self):
        import simple_log_factory

        assert hasattr(simple_log_factory, "__all__")
        assert "log_factory" in simple_log_factory.__all__
        assert "LogContext" in simple_log_factory.__all__
        assert "LogContextGenerators" in simple_log_factory.__all__

    def test_version_matches_installed_distribution(self) -> None:
        import simple_log_factory

        assert simple_log_factory.__version__ == version("simple_log_factory")

    def test_log_factory_is_callable_and_works(self):
        from simple_log_factory import log_factory

        logger = log_factory("init_test")
        assert isinstance(logger, logging.Logger)
