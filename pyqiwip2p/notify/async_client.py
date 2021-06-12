import asyncio
from hypercorn.config import Config
from hypercorn.asyncio import serve
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import Response
from starlette import status
from starlette.routing import Route

import inspect
from typing import Optional
from datetime import date, datetime, time, timedelta
from pyqiwip2p.p2p_types.Responses import Bill
import hmac
import hashlib
import asyncio


class AioQiwiNotify:
	"""
	Штучка, чтобы работать с серверными уведомлениями Qiwi. Запускает сервер для приема уведомлений. А ещё тут есть хендлеры.

	:param auth_key: приватный ключ, на который настроен прием уведомлений.
	:type auth_key: ``str``
	"""

	def __init__(self, auth_key: str, once=False):
		self.auth_key = auth_key
		self.handlers = []
		self.once = once
		routes = [
			Route("/qiwi_notify", endpoint=self.server)
		]

		self.app = Starlette(routes=routes)

	def handler(self, func=None):
		def decorator(handler):
			self.handlers.append({"handler": handler, "filter": func})
			return handler
		return decorator

	def _check_valid(self, bill: Bill, sha256: str):
		invoice_parameters = f"{bill.currency} | {bill.amount} | {bill.bill_id} | {bill.site_id} | {bill.status}"
		if hmac.new(self.auth_key.encode(), invoice_parameters.encode(), hashlib.sha256).hexdigest() == sha256:
			return True
		else:
			return False

	async def _parse(self, response, sha256):
		bill = Bill(response)
		if self._check_valid(bill, sha256):
			loop = asyncio.get_event_loop()
			loop.create_task(self._check(bill))
			return Response(status_code=status.HTTP_200_OK)
		else:
			return Response(status_code=status.HTTP_401_UNAUTHORIZED)

	async def _check(self, bill):
		for handler in self.handlers:
			if handler["filter"](bill):
				if inspect.iscoroutinefunction(handler["handler"]):
					await handler["handler"](bill)
				else:
					handler["handler"](bill)
				if self.once:
					break

	async def server(self, request: Request):
		await self._parse(await request.json(), request.headers["X-Api-Signature-SHA256"])

	def start(self, port: int = 12345, log_level="info"):
		config = Config()
		config.bind = [f"0.0.0.0:{port}"]
		asyncio.run(serve(self.app, config))

	async def a_start(self, port: int = 12345, log_level="info"):
		config = Config()
		config.bind = [f"0.0.0.0:{port}"]
		await serve(self.app, Config())
