from typing import Any, Iterable
import asyncio

async def _maybe_await(obj):
    if hasattr(obj, "__await__"):
        return await obj
    return obj

async def scalars_first(result) -> Any:
    """Return first value from result.scalars(), awaiting intermediate awaitables if necessary."""
    scalars = result.scalars()
    scalars = await _maybe_await(scalars)
    val = scalars.first()
    return await _maybe_await(val)

async def scalars_all(result) -> list[Any]:
    """Return list from result.scalars().all(), awaiting intermediate awaitables if necessary."""
    scalars = result.scalars()
    scalars = await _maybe_await(scalars)
    val = scalars.all()
    return await _maybe_await(val)

async def scalar_value(result) -> Any:
    """Return scalar() from result, awaiting if it's awaitable."""
    val = result.scalar()
    val = await _maybe_await(val)
    return val

async def result_first(result) -> Any:
    """Return result.first(), awaiting if the returned value is awaitable."""
    val = result.first()
    return await _maybe_await(val)
