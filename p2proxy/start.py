import asyncio
from hypercorn import Config
from hypercorn.asyncio import serve
from app import app

# from models import Referer
# import api

import server

# from dotenv import load_dotenv
# import os
#
# dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
# if os.path.exists(dotenv_path):
#     load_dotenv(dotenv_path)


if __name__ == "__main__":
    # Referer.create_table(True)
    config = Config()
    config.bind = "0.0.0.0:3600"
    asyncio.run(serve(app, config))
