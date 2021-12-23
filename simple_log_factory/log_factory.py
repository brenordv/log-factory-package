# -*- coding: utf-8 -*-

"""log_factory.py - Simple wrapper to make things easier when using the default Python logging package.
This script will create a logging object with a set of default objects. The current configuration is the most common
in my usage and that motivated the creation of this script.

"""

import logging
from logging.handlers import TimedRotatingFileHandler


def _get_handlers_(to_console, log_file, rotate_file_by_day):
    """
    Creates a list with the handlers that will be used with the log object.
    :param to_console: should log to console
    :param log_file: should log to file
    :param rotate_file_by_day: if logging to file, should rotate log_file by day
    :return: list of handlers.
    """
    # List of handlers that will be added to the log.
    handlers = []

    if to_console:
        # Adding console logging handler...
        handlers.append(logging.StreamHandler())

    if log_file:
        if rotate_file_by_day:
            # Adding handler for a file log that resets at midnight.
            handlers.append(TimedRotatingFileHandler(log_file, when="midnight"))
        else:
            # Adding common file log.
            handlers.append(logging.FileHandler(log_file))

    return handlers


def _check_unique_handler_types_(logger, unique_handler_types):
    """
    Checks for duplicated handler types between logger and it's parent.
    :param logger: logger object
    :param unique_handler_types: if the handler types should be unique
    :return: logger object
    """
    if unique_handler_types and logger.handlers == logger.parent.handlers:
        logger.handlers = list()

    return logger


def _attach_handlers_(logger, handlers, log_level, formatter, unique_handler_types):
    """
    Attaches each handler to the log object provided.
    :param logger: logging object
    :param handlers: list of handlers to attach
    :param log_level: log level for each handler
    :param formatter: format that will be used by the handler
    :param unique_handler_types: if true, will only add one handler of each type.
    :return: logging object with handlers.
    """
    # Adding handlers to the object.
    handler_list = logger.handlers
    handler_list.extend(logger.parent.handlers)
    handler_types = [type(h) for h in handler_list]
    for handler in handlers:
        # If logger object is set to use only one handler of each type and already have a handler of that type,
        # will skip adding it.
        if unique_handler_types and (type(handler) in handler_types):
            continue

        # but first, let's configure each handler.
        handler.setFormatter(formatter)
        handler.setLevel(log_level)

        # Adding the handler to the logging object.
        logger.addHandler(handler)

    return logger


def log_factory(log_name, log_file=None, rotate_file_by_day=True, log_level=logging.DEBUG, to_console=True,
                custom_handlers=None, log_format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                log_time_format=None, unique_handler_types=False):
    """
    Simple log factory using default Python logging package.
        :param log_time_format: Custom format for time section of the log.
        :param log_name: Name of the logger. (Should be the variable __main__ from the caller)
        :param log_file: If informed, will save log to that log.
        :param rotate_file_by_day: If true, will rotate the log file by day. (at midnight)
        :param log_level: Level of the log. (Default: 10 - DEBUG)
        :param to_console: If should show log on console.
        :param custom_handlers: will add any custom logging handlers informed here.
        :param log_format: Format of the log messages.
        :param unique_handler_types: if true, will only add one handler of each type.
        :returns: Logging object with the corresponding configurations.
    """
    # Defining formatter.
    if rotate_file_by_day:
        # If we're going to rotate our log files by day, we don't need to clutter-up each line with the current date.
        formatter = logging.Formatter(log_format, "%H:%M:%S")
    elif log_time_format:
        formatter = logging.Formatter(log_format, log_time_format)
    else:
        formatter = logging.Formatter(log_format)

    # Getting handlers
    handlers = _get_handlers_(to_console=to_console, log_file=log_file, rotate_file_by_day=rotate_file_by_day)

    # Adding custom handlers, if any...
    if custom_handlers:
        if isinstance(custom_handlers, list):
            handlers.extend(custom_handlers)
        else:
            handlers.append(custom_handlers)

    # Creating the log object.
    logger = logging.getLogger(log_name)

    # Setting log level to the root logger. If we don't do this, it will only log warnings+..
    log_level = log_level.strip().upper() if isinstance(log_level, str) else log_level
    logger.setLevel(log_level)

    # Returning the logging object ready to use.
    logger = _attach_handlers_(logger=logger, handlers=handlers, formatter=formatter, log_level=log_level,
                               unique_handler_types=unique_handler_types)

    # Double check for unique handler types and return the logger.
    return _check_unique_handler_types_(logger=logger, unique_handler_types=unique_handler_types)


class LogContext:
    def __init__(self, exception, error, warning, info, debug):
        self.exception = exception
        self.error = error
        self.warning = warning
        self.info = info
        self.debug = debug


class LogContextGenerators:
    def __init__(self, **kwargs):
        self.logger = log_factory(**kwargs)

    def get_logger_for_context(self, **kwargs) -> LogContext:
        return LogContext(exception=lambda msg: self.logger.exception(msg, extra=kwargs),
                          error=lambda msg: self.logger.error(msg, extra=kwargs),
                          warning=lambda msg: self.logger.warning(msg, extra=kwargs),
                          info=lambda msg: self.logger.info(msg, extra=kwargs),
                          debug=lambda msg: self.logger.debug(msg, extra=kwargs))
