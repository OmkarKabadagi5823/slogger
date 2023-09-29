import logging
import logging.handlers

from slogger.formators import ColoredFormatter, JSONFormatter


def get_console_handler(level=logging.INFO):
    console_handler = logging.StreamHandler()
    console_formatter = ColoredFormatter()
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(level)

    return console_handler


def get_structured_file_handler(filename, level=logging.INFO):
    structured_file_handler = logging.handlers.TimedRotatingFileHandler(
        filename=filename,
        when="midnight", interval=1,
        backupCount=7,
        encoding="utf-8",
        utc=True
    )
    file_formatter = JSONFormatter()
    structured_file_handler.setFormatter(file_formatter)
    structured_file_handler.setLevel(level)

    return structured_file_handler


def get_batched_structured_file_handler(filename, level=logging.INFO):
    structured_file_handler = get_structured_file_handler(filename, level=level)
    batched_file_handler = logging.handlers.MemoryHandler(capacity=10, flushLevel=logging.ERROR, target=structured_file_handler)
    return batched_file_handler
