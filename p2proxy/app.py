import asyncio
from hypercorn import Config
from hypercorn.asyncio import serve
from starlette.applications import Starlette

from server import router

app = Starlette()

app.mount("", router)

if __name__ == "__main__":
    config = Config()
    config.bind = "0.0.0.0:3600"
    asyncio.run(serve(app, config))
