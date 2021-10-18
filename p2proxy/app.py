import asyncio
import os

from dotenv import load_dotenv
from hypercorn import Config
from hypercorn.asyncio import serve
from starlette.applications import Starlette

dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

from server import router

app = Starlette()

dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

app.mount("", router)

if __name__ == "__main__":
    config = Config()
    config.bind = "0.0.0.0:3600"
    asyncio.run(serve(app, config))
