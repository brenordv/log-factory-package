# Simple log factory
This package is a wrapper for a simple log factory. 


# Usage
Creates a logger that will write to console, with level set to DEBUG.

```python
from simple_log_factory import log_factory

logger = log_factory("my_log1")
```

Creates a logger that will write to console and to file, with level set to DEBUG.
The file log will rotate daily, with timestamp added.

```python
from simple_log_factory import log_factory

logger = log_factory("my_log1", log_file="./my_log_dump.log")
```

Creates a logger that will write to console and to file, with level set to DEBUG.
This log file will be unique.

```python
from simple_log_factory import log_factory

logger = log_factory("my_log1", log_file="./my_log_dump.log", rotate_file_by_day=False)
```

Creates a logger that will write to console, with level set to DEBUG.
This type of logger (console) will be unique. 
(That's a workaround to log entries duplicated when more than one logger is configured to the same output)

```python
from simple_log_factory import log_factory

logger = log_factory("my_log1", unique_handler_types=True)
```


# Notes
This is a very early stage project, just a few functionalities. If you find any bugs, please contact me (or feel free to open an issue on Github).

- [Github Project: https://github.com/brenordv/log-factory-package](https://github.com/brenordv/log-factory-package)
- [PyPi Page: https://pypi.org/project/simple-log-factory](https://pypi.org/project/simple-log-factory)