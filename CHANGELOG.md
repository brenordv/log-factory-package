# 1.0.0 (2026-02-07)

- **Bug fixes** — Console-only loggers no longer silently drop dates from timestamps; `None`-parent guards prevent `AttributeError` on root loggers; reference no longer mutates handler list.
- **`__init__.py` fix** — `from simple_log_factory import log_factory` now correctly imports the function (not the module).
- **Type hints** — Full PEP 484 annotations and a `py.typed` marker (PEP 561).
- **`LogContext` is a frozen dataclass** — Immutable and comes with auto-generated `__repr__` and `__eq__`.
- **`log_name` validation** — `ValueError` raised for empty or non-string names.
- **Modern packaging** — `pyproject.toml` is the single source of truth; `setup.py` kept as a thin shim.
- **Test suite** — pytest-based tests with >80% coverage.
- **Python 3.9+** — Dropped support for Python 3.6–3.8.