from pyqiwip2p.types import QiwiDatetime

class QiwiError(Exception):
	"""
	Штучка для удобной работы с ошибками от Qiwi

	**Аргументы**

	:param response_json: json-словарь ответа на запрос
	:type response_json: ``dict``

	**Атрибуты**

	:param service_name: название сервсиса
	:type service_name: ``str``
	:param error_code: код ошибки
	:type error_code: ``str``
	:param description: описание ошибки
	:type description: ``str``
	:param user_message: сообщение
	:type description: ``str``
	:param datetime: момент времени
	:type datetime: QiwiDatetime
	:param trace_id: идентификатор ошибки
	:type trace_id: ``str``
	:param cause: поясление
	:type cause: ``str``, optional
	"""
	def __init__(self, response_json: dict):
		self.service_name = response_json["serviceName"]
		self.error_code = response_json["errorCode"]
		self.description = response_json["description"]
		self.user_message = response_json["userMessage"]
		self.datetime = QiwiDatetime(response_json["dateTime"])
		self.trace_id = response_json["traceId"]
		self.cause = response_json["cause"] if "cause" in response_json else None
		if self.cause:
			message = f"{self.error_code} - {self.description}. {self.cause}"
		else:
			message = f"{self.error_code} - {self.description}."
		super().__init__(message)

	def __str__(self):
		return f"{self.error_code} - {self.description}"
