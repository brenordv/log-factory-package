# Contributing to Simple Log Factory

Thank you for your interest in contributing! This guide will help you get started.

## Prerequisites

- Python 3.9 or newer
- Git

## Setting Up the Development Environment

1. **Fork and clone the repository**

   ```bash
   git clone https://github.com/<your-username>/log-factory-package.git
   cd log-factory-package
   ```

2. **Create a virtual environment**

   ```bash
   python -m venv .venv

   # Linux / macOS
   source .venv/bin/activate

   # Windows
   .venv\Scripts\activate
   ```

3. **Install the package in editable mode with dev dependencies**

   ```bash
   pip install -e ".[dev]"
   ```

## Code Style

All style settings live in `pyproject.toml`. The key points:

| Tool      | Purpose         | Config highlights                                |
|-----------|-----------------|--------------------------------------------------|
| **Black** | Code formatting | `line-length = 120`, `target-version = ["py39"]` |
| **isort** | Import sorting  | `profile = "black"`, `line_length = 120`         |
| **Ruff**  | Linting         | `select = ["E", "F", "W", "I", "N", "UP"]`       |
| **mypy**  | Type checking   | `disallow_untyped_defs = true`                   |

### Naming Conventions

- `snake_case` for functions, variables, and modules
- `PascalCase` for classes
- `UPPER_CASE` for constants

### Type Hints

All public **and** private functions must have full type annotations. The codebase uses 
`from __future__ import annotations` for modern syntax. At times this can be annoying, I know. But it helps improve the 
experience with IDEs.

### Docstrings

Use **Google-style** docstrings for all public APIs:

```python
def my_function(name: str, count: int = 1) -> str:
    """Short summary of what the function does.

    Args:
        name: Description of the parameter.
        count: Description with default noted.

    Returns:
        Description of the return value.

    Raises:
        ValueError: When something is wrong.
    """
```

## Running Quality Checks

```bash
# Format code
black .

# Sort imports
isort .

# Lint
ruff check .

# Type check
mypy simple_log_factory/

# Run tests with coverage
pytest --cov=simple_log_factory --cov-report=term-missing
```

All of the above must pass cleanly before a pull request can be merged.

## Testing

Tests live in the `tests/` directory and use **pytest**. When writing tests:

- Follow the **Arrange-Act-Assert** pattern.
- Aim for **>80% coverage** on any code you add or change.
- Add regression tests for every bug fix.
- Use fixtures from `tests/conftest.py` (e.g., `tmp_log_file` for file handler
  tests). The `_reset_logging` fixture runs automatically and cleans up
  loggers between tests.

```bash
# Run the full suite
pytest -v

# Run a specific test file
pytest tests/test_log_factory.py

# Run a single test
pytest tests/test_log_factory.py::TestLogFactory::test_returns_logger
```

## Making Changes

1. **Create a feature branch** from `master`:

   ```bash
   git checkout -b feat/my-feature
   ```

2. **Make your changes.** Keep commits focused and atomic.

3. **Run all quality checks** (formatting, linting, type checking, tests).

4. **Update the CHANGELOG.md** with a brief description of your change under
   an `Unreleased` heading at the top of the file.

5. **Open a pull request** against `master`. The CI pipeline will
   automatically run the test suite across Python 3.9 - 3.14.

## Pull Request Guidelines

- Keep PRs small and focused on a single concern.
- Include tests for new functionality or bug fixes.
- Make sure CI passes before requesting review.
- Update documentation (docstrings, README) if behaviour changes.

## Project Structure

```
log-factory-package/
├── simple_log_factory/
│   ├── __init__.py          # Public API exports & __version__
│   ├── log_factory.py       # Core implementation
│   └── py.typed             # PEP 561 marker
├── tests/
│   ├── conftest.py          # Shared fixtures
│   ├── test_init.py         # Package import tests
│   ├── test_log_context.py  # LogContext / LogContextGenerators tests
│   └── test_log_factory.py  # Core function & bug regression tests
├── pyproject.toml           # Single source of truth for packaging & tools
├── setup.py                 # Thin shim for backward compatibility
├── CHANGELOG.md
├── LICENSE.md
└── readme.md
```

## License

By contributing you agree that your contributions will be licensed under the
[MIT License](LICENSE.md).
