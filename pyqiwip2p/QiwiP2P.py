import typing

import requests

from pyqiwip2p.qiwi_types import Bill
from pyqiwip2p.qiwi_types import QiwiError
from pyqiwip2p.qiwi_types import QiwiCustomer
from pyqiwip2p.qiwi_types import QiwiDatetime


class QiwiP2P:
	"""
	Основной инструмент-клиент для взаимодействия с API QiwiP2P

	**Аргументы и аттрибуты**

	:param auth_key: приватный ключ авторизации со страницы https://qiwi.com/p2p-admin/transfers/api. Нужен для работы с вашим аккаунтом.
	:type auth_key: ``str``
	:param currency: валюта для счетов в формате *Alpha-3 ISO 4217*. Пока что API умеет работать только с *RUB*
	:type currency: ``str``, optional
	"""
	def __init__(self, auth_key: str, currency: str = "RUB"):
		self.auth_key = auth_key
		self.currency = currency

	def bill(self, bill_id: typing.Union[str, int], amount: typing.Union[int, float],
				expiration: typing.Union[str, int, QiwiDatetime] = None,
				lifetime: int = 30,
				customer: typing.Union[QiwiCustomer, dict] = None, comment: str = "via pyQiwiP2P made by WhiteApfel",
				fields: dict = None):
		"""
		Метод для выставления счета.

		:param bill_id: идентификатор заказа/счета в вашей системе
		:type bill_id: ``str`` or ``int``
		:param amount: сумма заказа в рублях. Округляется до двух знаков после запятой.
		:type amount: ``int`` or ``float``
		:param expiration: когда счет будет закрыт. Принимает: Timestamp, Datetime или строку формата YYYY-MM-DDThh:mm:ss+hh:mm.
		:type expiration: ``int``, ``datetime`` or ``str``, optional
		:param lifetime: время жизни счета в минутах. Если параметр ``expiration`` не указан, то будет автоматически сгенерируется дата для закрытия через ``lifetime`` минут.
		:type lifetime: ``int``, optional, default=30
		:param customer: объект QiwiCustomer или ``dict`` с полями phone, email и customer
		:type customer: ``QiwiCustomer`` or ``dict``, optional
		:param comment: комментарий к платежу. До 255 символов
		:type comment: ``str``, optional
		:param fields: словарь кастомных полей QIWI. Я ничего про них не понял, извините.
		:type fields: ``dict``, optional
		:raise QiwiError: объект ответа Qiwi, если запрос не увенчался успехом
		:return: Объект счета при успешном выполнении
		:rtype: Bill
		"""
		expiration = QiwiDatetime(expiration).qiwi if expiration else QiwiDatetime(lifetime).qiwi
		amount = str(round(float(amount), 2)) if len(str(float(amount)).split(".")[1]) > 1 else str(round(float(amount), 2))+"0"
		qiwi_request_headers = {
			"Accept": "application/json",
			"Content-Type": "application/json",
			"Authorization": f"Bearer {self.auth_key}"
		}
		qiwi_request_data = {
			"amount": {
				"currency": self.currency,
				"value": amount
			},
			"comment": comment,
			"expirationDateTime": expiration,
			"customer": customer.dict if type(customer) is QiwiCustomer else QiwiCustomer(json_data=customer).dict if customer else {},
			"customFields": fields if fields else {}
		}
		print(qiwi_request_headers)
		print(qiwi_request_data)
		qiwi_response = Bill(requests.put(f"https://api.qiwi.com/partner/bill/v1/bills/{bill_id}",
					json=qiwi_request_data, headers=qiwi_request_headers))
		return qiwi_response

	def check(self, bill_id: typing.Union[str, int]):
		"""
		Проверяет статус выставленного счета.

		:param bill_id: идентификатор заказа/счета в вашей системе
		:type bill_id: ``str`` or ``int``
		:return: Объект счета при успешном выполнении
		:rtype: Bill
		"""
		qiwi_request_headers = {
			"Content-Type": "application/json",
			"Authorization": f"Bearer {self.auth_key}"
		}
		qiwi_response = Bill(requests.get(f"https://api.qiwi.com/partner/bill/v1/bills/{bill_id}",
					headers=qiwi_request_headers))
		return qiwi_response

	def reject(self, bill_id: typing.Union[str, int]):
		"""
		Закрывает счет на оплату.

		:param bill_id: идентификатор заказа/счета в вашей системе
		:type bill_id: ``str`` or ``int``
		:return: Объект счета при успешном выполнении
		:rtype: Bill
		"""
		qiwi_request_headers = {
			"Content-Type": "application/json",
			"Authorization": f"Bearer {self.auth_key}"
		}
		qiwi_response = Bill(requests.post(f"https://api.qiwi.com/partner/bill/v1/bills/{bill_id}/reject",
					headers=qiwi_request_headers))
		return qiwi_response
