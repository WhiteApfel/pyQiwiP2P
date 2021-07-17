import typing
import time
import random
import requests

from pyqiwip2p.p2p_types import Bill
from pyqiwip2p.p2p_types import QiwiError
from pyqiwip2p.p2p_types import QiwiCustomer
from pyqiwip2p.p2p_types import QiwiDatetime



class QiwiP2P:
	"""
	Основной инструмент-клиент для взаимодействия с API QiwiP2P

	**Аргументы и атрибуты**

	:param auth_key: приватный ключ авторизации со страницы https://qiwi.com/p2p-admin/transfers/api. Нужен для работы с вашим аккаунтом.
	:type auth_key: ``str``
	:param default_amount: значение суммы счета по умолчанию для новых счетов.
	:type default_amount: ``int`` or ``float``, optional
	:param currency: валюта для счетов в формате *Alpha-3 ISO 4217*. Пока что API умеет работать только с *RUB*
	:type currency: ``str``, optional
	"""

	def __init__(self, auth_key: str, default_amount: int = 100, currency: str = "RUB"):
		self.auth_key = auth_key
		self.default_amount = default_amount
		if currency in ["RUB", "KZT"]:
			self.currency = currency
		else:
			raise ValueError('Currency must be "RUB" or "KZT"')

	def bill(self,
			 bill_id: typing.Union[str, int] = None,
			 amount: typing.Union[int, float] = None,
			 currency: str = None,
			 expiration: typing.Union[str, int, QiwiDatetime] = None,
			 lifetime: int = 30,
			 customer: typing.Union[QiwiCustomer, dict] = None, comment: str = "via pyQiwiP2P made by WhiteApfel",
			 fields: dict = None):
		"""
		Метод для выставления счета.

		:param bill_id: идентификатор заказа/счета в вашей системе. Если параметр не укзаан, генерируется строка, основанная на времени.
		:type bill_id: ``str`` or ``int``, optional
		:param amount: сумма заказа в рублях. Округляется до двух знаков после запятой. Если не указано, используется значение по умолчанию
		:type amount: ``int`` or ``float``, optional
		:param currency: валюта платежа. ``RUB`` - рубли,  ``KZT`` - тенге
		:type currency: ``str`` or None, optional
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
		bill_id = bill_id if bill_id else f"WhiteApfel-PyQiwiP2P-{str(int(time.time() * 100))[4:]}-{int(random.random() * 1000)}"
		amount = amount if amount else self.default_amount
		expiration = QiwiDatetime(moment=expiration).qiwi if expiration else QiwiDatetime(lifetime=lifetime).qiwi
		amount = str(round(float(amount), 2)) if len(str(float(amount)).split(".")[1]) > 1 else str(
			round(float(amount), 2)) + "0"
		if currency:
			if not (currency in ["RUB", "KZT"]):
				raise ValueError('Currency must be "RUB" or "KZT"')
		else:
			currency = self.currency
		qiwi_request_headers = {
			"Accept": "application/json",
			"Content-Type": "application/json",
			"Authorization": f"Bearer {self.auth_key}"
		}
		qiwi_request_data = {
			"amount": {
				"currency": currency,
				"value": amount
			},
			"comment": comment,
			"expirationDateTime": expiration,
			"customer": customer.dict if type(customer) is QiwiCustomer else QiwiCustomer(
				json_data=customer).dict if customer else {},
			"customFields": fields if fields else {}
		}

		qiwi_raw_response = requests.put(f"https://api.qiwi.com/partner/bill/v1/bills/{bill_id}",
										  json=qiwi_request_data, headers=qiwi_request_headers)
		qiwi_response = Bill(qiwi_raw_response, self)
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

		qiwi_raw_response = requests.get(f"https://api.qiwi.com/partner/bill/v1/bills/{bill_id}",
										  headers=qiwi_request_headers)
		qiwi_response = Bill(qiwi_raw_response, self)
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
		qiwi_raw_response = requests.post(f"https://api.qiwi.com/partner/bill/v1/bills/{bill_id}/reject",
										   headers=qiwi_request_headers)
		qiwi_response = Bill(qiwi_raw_response, self)
		return qiwi_response
