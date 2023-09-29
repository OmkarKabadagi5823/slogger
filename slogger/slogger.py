from contextvars import ContextVar
import functools
import inspect
import logging

from slogger.handlers import *

__all__ = ["builtin_logger", "instrument", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL", "FATAL"]


DEBUG = logging.DEBUG
INFO = logging.INFO
WARNING = logging.WARNING
ERROR = logging.ERROR
CRITICAL = logging.CRITICAL
FATAL = logging.FATAL
    

class _SLogger():
    SPAN_CONTEXT = ContextVar("SPAN_CONTEXT", default=None)

    def __init__(
        self,
        logger_name: str,
        level=logging.DEBUG
    ):
        self._logger = logging.getLogger(logger_name)

        self._logger.setLevel(level)

    def __log(self, level, msg, *args, **kwargs):
        current_span = self.SPAN_CONTEXT.get()
        if current_span:
            kwargs = {**current_span.context, **kwargs}

        kwargs = {"extra": kwargs}

        if self._logger.isEnabledFor(level):
            caller = self._logger.findCaller(stack_info=True, stacklevel=3)
            record = self._logger.makeRecord(
                self._logger.name, level, caller[0], caller[1], msg, args, None, caller[2], sinfo=caller[3], **kwargs
            )
            self._logger.handle(record)

    def span(self, name, **context):
        parent_span = self.SPAN_CONTEXT.get()
        if parent_span:
            context = {**parent_span.context, **context}

        context["_Span.__name__"] = name
        span = _Span(self, name, **context)

        return span

    def debug(self, msg, *args, **kwargs):
        self.__log(logging.DEBUG, msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        self.__log(logging.INFO, msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        self.__log(logging.WARNING, msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        self.__log(logging.ERROR, msg, *args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        self.__log(logging.CRITICAL, msg, *args, **kwargs)

    def fatal(self, msg, *args, **kwargs):
        self.__log(logging.FATAL, msg, *args, **kwargs)

    def add_handler(self, handler):
        self._logger.addHandler(handler)


class _Span():
    def __init__(self, logger: _SLogger, name: str, **context):
        self._logger = logger
        self._name = name
        self._parent = None
        self._context = context
        self._closed = False

    def __enter__(self):
        self._parent = _SLogger.SPAN_CONTEXT.set(self)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if not self._closed:
            self.close()

    async def __aenter__(self):
        self._parent = _SLogger.SPAN_CONTEXT.set(self)
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        if not self._closed:
            self.close()

    def __del__(self):
        if not self._closed:
            self.close()

    def close(self):
        _SLogger.SPAN_CONTEXT.reset(self._parent)

        self._closed = True

    @property
    def name(self):
        return self._name

    @property
    def context(self):
        return self._context


builtin_logger = _SLogger("builtin_logger")
builtin_logger.add_handler(get_console_handler(logging.INFO))
builtin_logger.add_handler(get_structured_file_handler("app.log", logging.DEBUG))


def instrument(name=None, capture=[], **context):
    def decorator(func):
        is_async_fn = inspect.iscoroutinefunction(func)
    
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()
            selected_args = {k: v for k, v in bound_args.arguments.items() if k in capture}

            with builtin_logger.span(name or func.__name__, **selected_args, **context):
                return func(*args, **kwargs)

        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()
            selected_args = {k: v for k, v in bound_args.arguments.items() if k in capture}

            async with builtin_logger.span(name or func.__name__, **selected_args, **context):
                return await func(*args, **kwargs)

        return async_wrapper if is_async_fn else sync_wrapper

    return decorator
