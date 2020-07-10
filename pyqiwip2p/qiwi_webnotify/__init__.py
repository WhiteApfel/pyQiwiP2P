import cherrypy
import json
import hmac
import hashlib
from pyqiwip2p.qiwi_types.Responses import Bill


class QiwiNotify:
	"""
	Штучка, чтобы работать с серверными уведомлениями Qiwi. Запускает сервер для приема уведомлений. А ещё тут есть хендлеры.
	"""
	def __init__(self, auth_key: str, port: int = 8099):
		self.port = port
		self.auth_key = auth_key
		self.handlers = []

	def handler(self, func=None):
		def decorator(handler):
			self.handlers.append({"handler": handler, "filter": func})
			return handler
		return decorator

	def check_valid(self, bill: Bill, sha256):
		invoice_parameters = f"{bill.currency} | {bill.amount} | {bill.bill_id} | {bill.site_id} | {bill.status}"
		if hmac.new(self.auth_key, invoice_parameters, hashlib.sha256).hexdigest() ==  sha256:
			return True
		else:
			return False

	def parse(self, response, sha256):
		bill = Bill(response)
		if self.check_valid(bill, sha256):
			self.check(bill)
		else:
			raise cherrypy.HTTPError(403)

	def check(self, bill):
		for handler in self.handlers:
			if handler["filter"](bill):
				handler["handler"](bill)

	def start(qiwi):
		class WebhookServer(object):
			def check_headers(self, headers):
				if "content-type" in headers and headers["content-type"] == "application/json" and \
						"X-Api-Signature-SHA25" in headers:
					return True
				return False

			@cherrypy.expose
			def qiwi_notify(self):
				if self.check_headers(cherrypy.request.headers):
					json_string = cherrypy.request.body.read().decode("utf-8")
					qiwi.parse(json.loads(json_string), cherrypy.request.headers["X-Api-Signature-SHA25"])
					return ''
				else:
					raise cherrypy.HTTPError(403)

		cherrypy.config.update({'server.socket_port': qiwi.port})
		cherrypy.quickstart(WebhookServer())
