# SLogger
## Description
`slogger` is a structured logging library for python built on top of the python's built-in `logging` library

## Features
* Structured logging into json
* Contextual logging using `span`
* Automatic contextual logging using `instrument` decorator
* `instrument` decorator also supports async functions

## Getting Started
### Installation
```bash
git clone https://github.com/OmkarKabadagi5823/slogger.git
cd slogger
python -m build
cd dist
pip install slogger-<version>-py3-none-any.whl
```

### Usage
```python
# Import builtin_logger to do normal logging
from slogger.slogger import builtin_logger, instrument

# Use the `instrument` decorator to configure automatic contextual logging for a function
@instrument(capture=["message"])
def print_message(message):
    builtin_logger.info(message)

def main():
    builtin_logger.info("hello world", context1=1, context2=2)

    # Use `span` to create a context for logging
    with builtin_logger.span("myspan", context="user1"):
        builtin_logger.info("hello world from span")

```

You can also look at the examples under the `examples` directory.

> **Note**: For the `echo_server` example, you will need to install `fastapi` and `uvicorn`
