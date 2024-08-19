import asyncio

import uvicorn
from fastapi import FastAPI

from router import root_router

app = FastAPI()
app.include_router(root_router)


async def main():
    import logging
    from pools import AioSession
    import setting
    from tools.net import is_port_in_use

    if is_port_in_use(setting.PORT):
        logging.error("port occupied")
        return

    session = AioSession()

    try:
        await uvicorn.Server(
            uvicorn.Config(
                app,
                host=setting.HOST,
                port=setting.PORT,
                log_level="info")
        ).serve()
    except KeyboardInterrupt:
        logging.error("plugin-upload-cloud-background-server-exit")
    finally:
        await session.close()


if __name__ == "__main__":
    asyncio.run(main())
