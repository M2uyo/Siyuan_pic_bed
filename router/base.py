import asyncio
import functools
import signal

from fastapi import APIRouter

import define
from model.api_model import APIResponse

router = APIRouter()


@router.post("/")
async def root():
    return APIResponse(data={"message": define.IMsg.HELLO_WORLD, "result": True})


@router.get("/exit")
async def say_goodbye():
    asyncio.get_event_loop().call_later(1, functools.partial(signal.raise_signal, signal.SIGINT))
    return APIResponse(data={"message": "Goodbye"})
