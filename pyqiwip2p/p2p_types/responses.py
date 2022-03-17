import json
import time
import typing

from httpx._models import Response
from response_report import Reporter

from pyqiwip2p.p2p_types import QiwiCustomer
from pyqiwip2p.p2p_types import QiwiDatetime
from pyqiwip2p.p2p_types import QiwiError


class Bill:
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
    :param status_changed: время последнего изменения счёта
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
    :param json: исходный словарь Qiwi на случай,
    если они что-то обновят или у меня что-то не работает
    :type json: ``dict``
    :param alt_url: ссылка с проксированием через сервер
    для установления заголовка referer
    :type alt_url: ``str``
    """

    def __init__(self, response: typing.Union[Response, dict], alt="qp2p.0708.su"):
        self.r_json = response
        if type(self.r_json) is Response:
            try:
                self.r_json = self.r_json.json()
            except json.decoder.JSONDecodeError:
                fn = f"QiwiCrash_{int(time.time())}.txt"
                Reporter(response).save(fn)
                raise ValueError(
                    f"Code: {response.status_code}. "
                    f"Qiwi response is not JSON. This is Qiwi-side bug. "
                    f"Please try again later or check response. "
                    f"Qiwi response saved to {fn}. "
                    f"P.S. The number of requests per minute may have been exceeded. "
                    f"You can wait, change auth_key or cry."
                )
        if "errorCode" in self.r_json:
            fn = f"QiwiCrash_{int(time.time())}.txt"
            Reporter(response).save(fn)
            raise QiwiError(self.r_json)

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
        self.customer: QiwiCustomer = (
            QiwiCustomer(json_data=self.r_json["customer"])
            if "customer" in self.r_json
            else None
        )
        self.fields: dict = (
            self.r_json["customFields"] if "customFields" in self.r_json else None
        )
        self.json: dict = self.r_json
        self.alt_url: str = f"https://{alt}/bill/{self.pay_url[-36:]}"
