import asyncio
import functools
import logging
import signal

import uvicorn
from fastapi import FastAPI

from pools import AioSession
from route import config, siyuan, cloud
from tools.net import is_port_in_use

import define
import setting
from model.api_model import APIResponse

app = FastAPI()
server = uvicorn.Server(
    uvicorn.Config(
        app,
        host=setting.HOST,
        port=setting.PORT,
        log_level="info")
)
app.include_router(config.router)
app.include_router(siyuan.router, prefix="/siyuan")
app.include_router(cloud.router, prefix="/cloud")


@app.post("/")
async def root():
    return APIResponse(data={"message": define.IMsg.HELLO_WORLD, "result": True})


@app.get("/exit")
async def say_goodbye():
    asyncio.get_event_loop().call_later(1, functools.partial(signal.raise_signal, signal.SIGINT))
    return APIResponse(data={"message": "Goodbye"})


async def main():
    if is_port_in_use(setting.PORT):
        logging.error("port occupied")
        return

    session = AioSession()

    try:
        await server.serve()
    except KeyboardInterrupt:
        logging.error("plugin-upload-cloud-background-server-exit")
    finally:
        await session.close()


if __name__ == "__main__":
    asyncio.run(main())
