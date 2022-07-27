import asyncio

from hypercorn import Config
from hypercorn.asyncio import serve
from server import routes
from starlette.applications import Starlette

app = Starlette(routes=routes)

if __name__ == "__main__":
    config = Config()
    config.bind = "0.0.0.0:3600"
    asyncio.run(serve(app, config))
