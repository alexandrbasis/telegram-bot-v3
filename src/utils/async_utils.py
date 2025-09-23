"""Async utility helpers."""

from inspect import isawaitable
from typing import Any


async def await_if_needed(result: Any) -> Any:
    """Await the value if it is awaitable; otherwise return it unchanged."""

    if isawaitable(result):
        return await result
    return result
