# -*- coding: utf-8 -*-
"""log_factory.py - Simple wrapper around Python's logging module.

Creates pre-configured logging objects with sensible defaults for console
and/or file output, optional daily rotation, and handler deduplication.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from logging.handlers import TimedRotatingFileHandler
from typing import Callable, List, Optional, Sequence, Union


def _get_handlers(
    to_console: bool,
    log_file: Optional[str],
    rotate_file_by_day: bool,
) -> List[logging.Handler]:
    """Build a list of logging handlers based on the requested outputs.

    Args:
        to_console: If ``True``, include a :class:`~logging.StreamHandler`.
        log_file: Path for a file handler. ``None`` means no file output.
        rotate_file_by_day: If ``True`` **and** *log_file* is set, use a
            :class:`~logging.handlers.TimedRotatingFileHandler` that rotates
            at midnight.

    Returns:
        A list of freshly created handler instances.
    """
    handlers: List[logging.Handler] = []

    if to_console:
        handlers.append(logging.StreamHandler())

    if log_file:
        if rotate_file_by_day:
            handlers.append(TimedRotatingFileHandler(log_file, when="midnight"))
        else:
            handlers.append(logging.FileHandler(log_file))

    return handlers


def _check_unique_handler_types(
    logger: logging.Logger,
    unique_handler_types: bool,
) -> logging.Logger:
    """Remove duplicate handler sets inherited from a parent logger.

    When *unique_handler_types* is ``True`` and the logger's handler list is
    identical to its parent's, the logger's handlers are cleared so that
    messages are not emitted twice.

    Args:
        logger: The logger to inspect.
        unique_handler_types: Whether deduplication is active.

    Returns:
        The (possibly modified) logger.
    """
    if (
        unique_handler_types
        and logger.parent is not None
        and logger.handlers == logger.parent.handlers
    ):
        logger.handlers = []

    return logger


def _attach_handlers(
    logger: logging.Logger,
    handlers: Sequence[logging.Handler],
    log_level: Union[int, str],
    formatter: logging.Formatter,
    unique_handler_types: bool,
) -> logging.Logger:
    """Attach *handlers* to *logger*, optionally skipping duplicate types.

    Args:
        logger: Target logger.
        handlers: Handlers to attach.
        log_level: Level applied to each handler.
        formatter: Formatter applied to each handler.
        unique_handler_types: If ``True``, a handler whose type already
            exists on the logger (or its parent) is skipped.

    Returns:
        The logger with newly attached handlers.
    """
    # Bug 4 fix: copy the handler list instead of aliasing it.
    handler_list: List[logging.Handler] = list(logger.handlers)

    # Bug 2/3 fix: guard against logger.parent being None.
    if logger.parent is not None:
        handler_list.extend(logger.parent.handlers)

    handler_types = [type(h) for h in handler_list]

    for handler in handlers:
        if unique_handler_types and (type(handler) in handler_types):
            continue

        handler.setFormatter(formatter)
        handler.setLevel(log_level)
        logger.addHandler(handler)

    return logger


def log_factory(
    log_name: str,
    log_file: Optional[str] = None,
    rotate_file_by_day: bool = True,
    log_level: Union[int, str] = logging.DEBUG,
    to_console: bool = True,
    custom_handlers: Optional[Union[logging.Handler, List[logging.Handler]]] = None,
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    log_time_format: Optional[str] = None,
    unique_handler_types: bool = False,
) -> logging.Logger:
    """Create a pre-configured: class:`~logging.Logger`.

    Args:
        log_name: Name of the logger (typically ``__name__`` of the caller).
        log_file: Optional file path for file-based logging.
        rotate_file_by_day: Rotate the log file daily at midnight.
            Only takes effect when *log_file* is set.
        log_level: Logging level (default ``DEBUG``). Accepts an ``int`` or
            a case-insensitive level name such as ``"INFO"``.
        to_console: Emit log records to *stderr* via a
            :class:`~logging.StreamHandler`.
        custom_handlers: One or more additional handlers to attach.
        log_format: :func:`logging.Formatter` format string.
        log_time_format: Optional *datefmt* passed to the formatter.
        unique_handler_types: When ``True``, only one handler of each type
            will be attached (useful to prevent duplicate output).

    Returns:
        A fully configured: class:`~logging.Logger` instance.

    Raises:
        ValueError: If *log_name* is not a non-empty string.

    Example::

        from simple_log_factory import log_factory

        logger = log_factory(__name__)
        logger.info("Hello, world!")
    """
    # log_name validation
    if not isinstance(log_name, str) or not log_name.strip():
        raise ValueError("log_name must be a non-empty string.")

    if rotate_file_by_day and log_file:
        formatter = logging.Formatter(log_format, "%H:%M:%S")
    elif log_time_format:
        formatter = logging.Formatter(log_format, log_time_format)
    else:
        formatter = logging.Formatter(log_format)

    handlers = _get_handlers(
        to_console=to_console,
        log_file=log_file,
        rotate_file_by_day=rotate_file_by_day,
    )

    if custom_handlers:
        if isinstance(custom_handlers, list):
            handlers.extend(custom_handlers)
        else:
            handlers.append(custom_handlers)

    logger = logging.getLogger(log_name)

    log_level = log_level.strip().upper() if isinstance(log_level, str) else log_level
    logger.setLevel(log_level)

    logger = _attach_handlers(
        logger=logger,
        handlers=handlers,
        formatter=formatter,
        log_level=log_level,
        unique_handler_types=unique_handler_types,
    )

    return _check_unique_handler_types(logger=logger, unique_handler_types=unique_handler_types)


@dataclass(frozen=True)
class LogContext:
    """Immutable container of pre-bound logging callables for a single context.

    Each attribute is a callable that accepts a message string and logs it at
    the corresponding level, automatically injecting any extra context passed
    when the instance was created via
    :meth:`LogContextGenerators.get_logger_for_context`.

    Attributes:
        exception: Logs at ``EXCEPTION`` level.
        error: Logs at ``ERROR`` level.
        warning: Logs at ``WARNING`` level.
        info: Logs at ``INFO`` level.
        debug: Logs at ``DEBUG`` level.
    """

    exception: Callable[[str], None]
    error: Callable[[str], None]
    warning: Callable[[str], None]
    info: Callable[[str], None]
    debug: Callable[[str], None]


class LogContextGenerators:
    """Factory that produces :class:`LogContext` instances bound to a single logger.

    All keyword arguments are forwarded to :func:`log_factory`.

    Example::

        gen = LogContextGenerators(log_name="my_app")
        ctx = gen.get_logger_for_context(request_id="abc-123")
        ctx.info("Processing request")
    """

    def __init__(self, **kwargs: object):
        self.logger: logging.Logger = log_factory(**kwargs)

    def get_logger_for_context(self, **kwargs: object) -> LogContext:
        """Return a :class:`LogContext` with *kwargs* injected as ``extra``.

        Args:
            **kwargs: Arbitrary key-value pairs passed as the ``extra``
                dict on every log call.

        Returns:
            A frozen :class:`LogContext` whose methods include the given
            extra context.
        """
        return LogContext(
            exception=lambda msg: self.logger.exception(msg, extra=kwargs),
            error=lambda msg: self.logger.error(msg, extra=kwargs),
            warning=lambda msg: self.logger.warning(msg, extra=kwargs),
            info=lambda msg: self.logger.info(msg, extra=kwargs),
            debug=lambda msg: self.logger.debug(msg, extra=kwargs),
        )
