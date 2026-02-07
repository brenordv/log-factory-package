# Simple Log Factory

A lightweight wrapper around Python's built-in `logging` module that creates
pre-configured loggers with sensible defaults.

**Requires Python 3.9+**

## Installation

```bash
pip install simple_log_factory
```

## Usage

### Basic console logger (DEBUG level)

```python
from simple_log_factory import log_factory

logger = log_factory("my_app")
logger.info("Application started")
```

### Console + rotating file logger

The file log rotates daily at midnight. The time-only format (`%H:%M:%S`) is
used automatically for the file handler since the date is encoded in the
filename.

```python
from simple_log_factory import log_factory

logger = log_factory("my_app", log_file="./app.log")
```

### Console + static file logger

```python
from simple_log_factory import log_factory

logger = log_factory("my_app", log_file="./app.log", rotate_file_by_day=False)
```

### Deduplicate handlers

Prevent duplicate output when multiple loggers write to the same destination:

```python
from simple_log_factory import log_factory

logger = log_factory("my_app", unique_handler_types=True)
```

### LogContext and LogContextGenerators

`LogContextGenerators` creates context-bound loggers that inject extra
key-value pairs into every log call:

```python
from simple_log_factory import LogContextGenerators

gen = LogContextGenerators(log_name="my_app")
ctx = gen.get_logger_for_context(request_id="abc-123", user="alice")

ctx.info("Processing request")   # extra={request_id: "abc-123", user: "alice"}
ctx.error("Something went wrong")
```

The returned `LogContext` object is a frozen dataclass with attributes
`exception`, `error`, `warning`, `info`, and `debug`.

## Links

- [GitHub](https://github.com/brenordv/log-factory-package)
- [PyPI](https://pypi.org/project/simple-log-factory)
