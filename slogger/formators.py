import json
import logging
from logging import LogRecord


class ColoredFormatter(logging.Formatter):
    COLORS = {
        "DEBUG": "\033[1;36m",  # Bold Cyan
        "INFO": "\033[1;32m",   # Bold Green
        "WARNING": "\033[1;33m",  # Bold Yellow
        "ERROR": "\033[1;31m",  # Bold Red
        "CRITICAL": "\033[1;31m",  # Bold Red
    }
    RESET = "\033[0m"
    WHITE = "\033[1;37m"  # Bold White

    def format(self, record):
        color = self.COLORS.get(record.levelname, self.RESET)
        level_name = f"{color}{record.levelname}{self.RESET}"
        message = f"{self.WHITE}{record.getMessage()}{self.RESET}"
        return f"[{level_name}]  {message}"


class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_object = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "message": record.getMessage(),
            "line": record.lineno,
            "func": record.funcName,
            "file": record.filename
        }

        all_attributes = record.__dict__.copy() 
        standard_attrs = [
            "args", "asctime", "created", "exc_info", "exc_text", "filename", 
            "funcName", "levelname", "levelno", "lineno", "message", 
            "module", "msecs", "msg", "name", "pathname", "process", 
            "processName", "relativeCreated", "stack_info", "thread", 
            "threadName"
        ]
        for attr in standard_attrs:
            all_attributes.pop(attr, None)

        log_object.update(all_attributes)

        return json.dumps(log_object)
