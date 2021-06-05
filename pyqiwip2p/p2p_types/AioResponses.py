from pyqiwip2p.p2p_types.Errors import QiwiError
from httpx._models import Response
import typing
import json
import time
from pyqiwip2p.p2p_types import QiwiCustomer
from pyqiwip2p.p2p_types import QiwiDatetime


class AioBill:
	"""
	Объект для удобной работы со счетом

	**Аргументы**

	:param response: ответ от серверов киви. Можно просто json.
	:type response: Response or ``dict``
	:param qiwi_p2p: объект P2P для работы дополнительных методов
	:type qiwi_p2p: QiwiP2P, optional

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
	:param bill_history: будет сохраняться история объектов Bill при обновлении информации о счете через метод update
	:type bill_history: list
	"""

	def __init__(self, response: typing.Union[Response, dict], qiwi_p2p=None):
		self.r_json = response if type(response) is Response else response
		try:
			self.r_json = self.r_json.json()
		except json.decoder.JSONDecodeError:
			fn = f"QiwiCrash_{int(time.time())}.html"
			with open(fn, "w+") as crash:
				crash.write(self.r_json.text)
			raise ValueError(
				f"Qiwi response is not JSON. This is Qiwi-side bug. Please try again later. Qiwi response page - {fn}")
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
			self.customer: QiwiCustomer = QiwiCustomer(
				json_data=self.r_json["customer"]) if "customer" in self.r_json else None
			self.fields: dict = self.r_json["customFields"] if "customFields" in self.r_json else None
			self.json = self.r_json
		self.__p2p = qiwi_p2p
		self.bill_history = [self]

	async def actual(self):
		"""
		Актуальная информация о счёте, получаемая прямо при вызове.
		Если нет необходимости в постоянном обновлении данных, можно воспользоваться методом Bill.update_info().

		В историю Bill.bill_history будет добавлен актуальный Bill. Зачем? Не знаю, пусть будет. Может кому-то пригодится.

		:return: Объект счета с обновленной информацией
		:rtype: AioBill
		"""
		if self.__p2p:
			actual = await self.__get_actual()
			actual.bill_history = self.bill_history
			actual.bill_history.append(actual)
			self.bill_history.append(actual)
			return actual

	async def __get_actual(self):
		"""
		Возвращает новый экземпляр Bill с актуальной информацией.

		:return: Объект счета с обновленной информацией
		:rtype: AioBill
		"""
		if self.__p2p:
			return await self.__p2p.check(self.bill_id)

	async def update_info(self):
		"""
		Изменяет текущий экземпляр Bill, устанавливая актуальную информацию.

		:return: Объект счета с обновленной информацией
		:rtype: AioBill
		"""
		actual = await self.__get_actual()
		actual.bill_history = self.bill_history
		actual.bill_history.append(actual)
		self.__dict__ = actual.__dict__
		return self
