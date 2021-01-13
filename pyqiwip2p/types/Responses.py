from pyqiwip2p.types.Errors import QiwiError
from requests import Response
import typing
import json
from pyqiwip2p.types import QiwiCustomer
from pyqiwip2p.types import QiwiDatetime


class Bill:
	"""
	Объект для удобной работы со счетом

	**Аргументы**

	:param response: ответ от серверов киви. Можно просто json.
	:type response: Response or ``dict``

	**Атрибуты**

	:param site_id: идентификатор вашего сайта в системе Qiwi
	:type site_id: ``str``
	:param bill_id: идентификатор счета
	:type bill_id: ``str``
	:param amount: сумма счета
	:type amount: ``float``
	:param currency: валюта счета
	:type currency: ``str``
	:param status: статус счета
	:type status: ``str``
	:param status_changed: время последнего изменения счата
	:type status_changed: QiwiDatetime
	:param creation: время создания счета
	:type creation: QiwiDatetime
	:param expiration: время закрытия счета
	:type expiration: QiwiDatetime
	:param pay_url: URL-адрес для оплаты
	:type pay_url: ``str``
	:param comment: комментарий
	:type comment: ``str``, optional
	:param customer: информация о клиенте
	:type customer: QiwiCustomer
	:param fields: кастомные поля Qiwi
	:type fields: ``dict``
	:param json: исходный словарь Qiwi на случай, если они что-то обновят или у меня что-то не работает
	:type json: ``dict``
	"""
	def __init__(self, response: typing.Union[Response, dict]):
		self.r_json = response if type(response) is Response else response
		try:
			self.r_json = self.r_json.json()
		except json.decoder.JSONDecodeError as e:
			raise ValueError("Qiwi response is not JSON. This is Qiwi-side bug. Please try again later.")
		if "errorCode" in self.r_json:
			raise QiwiError(self.r_json)
		else:
			self.site_id: int = self.r_json["siteId"]
			self.bill_id: int = self.r_json["billId"]
			self.amount: float = self.r_json["amount"]["value"]
			self.currency: str = self.r_json["amount"]["currency"]
			self.status: str = self.r_json["status"]["value"]
			self.status_changed: str = self.r_json["status"]["changedDateTime"]
			self.creation: str = self.r_json["creationDateTime"]
			self.expiration: str = self.r_json["expirationDateTime"]
			self.pay_url: str = self.r_json["payUrl"]
			self.comment: str = self.r_json["comment"] if "comment" in self.r_json else None
			self.customer: QiwiCustomer = QiwiCustomer(json_data=self.r_json["customer"]) if "customer" in self.r_json else None
			self.fields: dict = self.r_json["customFields"] if "customFields" in self.r_json else None
			self.json = self.r_json
