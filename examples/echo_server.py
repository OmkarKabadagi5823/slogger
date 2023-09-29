import asyncio
from fastapi import FastAPI, HTTPException
import uvicorn

from slogger import builtin_logger, instrument


echo_service = FastAPI()


async def toggle_case(char: str) -> str:
    await asyncio.sleep(2)

    if char.islower():
        return char.upper()
    elif char.isupper():
        return char.lower()
    else:
        return char


@echo_service.get("/echo/{char}")
@instrument(name="echo", capture=["char"], route="/:id")
async def echo(char: str):
    if not char.isalpha() or len(char) != 1:
        builtin_logger.error("Received invalid character", char=char)
        raise HTTPException(status_code=422, detail="Value must be a single alphabet character")

    builtin_logger.info(f"echo input [{char}]")

    await asyncio.sleep(2)

    builtin_logger.info(f"echo output [{char}]")

    return {"char": char}


@echo_service.get("/toggle/{char}")
@instrument(name="toggle", capture=["char"], route="/:id")
async def toggle(char: str):
    if not char.isalpha() or len(char) != 1:
        builtin_logger.error("Received invalid character", char=char)
        raise HTTPException(status_code=422, detail="Value must be a single alphabet character")

    builtin_logger.info(f"toggle input [{char}]")

    toggle_char = await toggle_case(char)

    builtin_logger.info(f"toggle output [{toggle_char}]")

    return {"char": toggle_char}


if __name__ == "__main__":
    uvicorn.run(
        echo_service,
        host="127.0.0.1",
        port=8081
    )
