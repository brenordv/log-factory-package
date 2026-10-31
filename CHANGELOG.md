# 2.0.0

- **Python 3.11+**: dropped support for Python 3.9 and 3.10.
- **Fixed**: an explicit `log_time_format` is now honored when `log_file` is set with daily rotation. Before, the
  time-only `%H:%M:%S` format always won. The time-only format is still the default when no `log_time_format` is given.
- **Fixed**: records logged through `LogContext` callables now report the caller's function, file and line number
  instead of a lambda inside `log_factory.py`.
- **Tooling**: dev dependencies moved to a `dev` dependency group (`uv sync`); black and isort replaced by
  `ruff format` and ruff's import sorting; dependencies and build requirements updated to their latest releases.

# 1.0.0

- **Bug fixes** — Console-only loggers no longer silently drop dates from timestamps; `None`-parent guards prevent `AttributeError` on root loggers; reference no longer mutates handler list.
- **`__init__.py` fix** — `from simple_log_factory import log_factory` now correctly imports the function (not the module).
- **Type hints** — Full PEP 484 annotations and a `py.typed` marker (PEP 561).
- **`LogContext` is a frozen dataclass** — Immutable and comes with auto-generated `__repr__` and `__eq__`.
- **`log_name` validation** — `ValueError` raised for empty or non-string names.
- **Modern packaging** — `pyproject.toml` is the single source of truth; `setup.py` kept as a thin shim.
- **Test suite** — pytest-based tests with >80% coverage.
- **Python 3.9+** — Dropped support for Python 3.6–3.8.
