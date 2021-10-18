import asyncio
from hypercorn import Config
from hypercorn.asyncio import serve
from app import app
from dotenv import load_dotenv
import os

dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

import server

if __name__ == "__main__":
    config = Config()
    config.bind = "0.0.0.0:3600"
    asyncio.run(serve(app, config))
