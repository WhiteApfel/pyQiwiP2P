from __future__ import annotations
import json
import random
import time
import typing
from base64 import b64decode
from ipaddress import IPv4Network, IPv4Address

import httpx
from loguru import logger

from pyqiwip2p.p2p_types import PaymentMethods
from pyqiwip2p.p2p_types import Bill
from pyqiwip2p.p2p_types import QiwiCustomer
from pyqiwip2p.p2p_types import QiwiDatetime

logger.disable("pyqiwip2p")


class QiwiP2P:
    """
    Основной инструмент-клиент для взаимодействия с API QiwiP2P

    **Аргументы и атрибуты**

    :param auth_key: приватный ключ авторизации со страницы https://qiwi.com/p2p-admin/transfers/api. Нужен для работы с вашим аккаунтом.
    :type auth_key: ``str``
    :param default_amount: значение суммы счета по умолчанию для новых счетов.
    :type default_amount: ``int`` or ``float``, optional
    :param currency: валюта для счетов в формате *Alpha-3 ISO 4217*. Пока что API умеет работать только с *RUB* и *KZT*
    :type currency: ``str``, optional
    :param alt: альтернативный домен для проксирующей ссылки. По-умолчанию ``qp2p.0708.su``
    :type alt: ``str``, optional
    """

    def __init__(
        self,
        auth_key: str,
        default_amount: int = 100,
        currency: str = "RUB",
        alt: str = "qp2p.0708.su",
    ):
        self.validate_privkey(auth_key)
        self.auth_key = auth_key
        self.default_amount = default_amount
        self.is_async = False
        self._client: httpx.Client = None
        self.alt = alt
        if currency not in ["RUB", "KZT"]:
            raise ValueError('Currency must be "RUB" or "KZT"')
        self.currency = currency

    @property
    def client(self):
        if not self._client:
            self._client = httpx.Client()
        return self._client

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        return self.client.close()

    @staticmethod
    def is_qiwi_ip(ip: str, qiwi_ips=None, *args, **kwargs):
        """
        Вы просили, мы сделали. Теперь проверить IP можнно одной простой функцией.
        Причём не обязательно инициализировать объект, так как это статичный метод.

        :param ip: ip адрес, с которого пришёл запрос
        :type ip: ``str``
        :param qiwi_ips: список разрешённых подсетей
        :type qiwi_ips: ``list`` or ``tuple``, optional
        :return: Принадлежность IP адресам Qiwi
        :rtype: ``bool``
        """
        if qiwi_ips is None:
            qiwi_ips = [
                "79.142.16.0/20",
                "195.189.100.0/22",
                "91.232.230.0/23",
                "91.213.51.0/24",
            ]
        ip = IPv4Address(ip)
        is_qiwi = any(ip in IPv4Network(net) for net in qiwi_ips)
        logger.log(
            "debug" if is_qiwi else "warning",
            f"is_qiwi_ip: {ip} {'not ' if not is_qiwi else ''} in {qiwi_ips}",
        )
        return is_qiwi

    def validate_privkey(self, privkey):
        key_decoded = b64decode(privkey).decode()
        try:
            key_decoded = json.loads(key_decoded)
            if "version" in key_decoded and "data" in key_decoded:
                key_data = key_decoded["data"]
                if (
                    "payin_merchant_site_uid" in key_data
                    and "user_id" in key_data
                    and "secret" in key_data
                ):
                    if key_decoded["version"] == "P2P":
                        return True
        except json.decoder.JSONDecodeError:
            ...
        raise ValueError("Invalid token")

    def bill(
        self,
        bill_id: typing.Union[str, int] = None,
        amount: typing.Union[int, float] = None,
        currency: str = None,
        expiration: typing.Union[str, int, QiwiDatetime] = None,
        lifetime: int = 30,
        customer: typing.Union[QiwiCustomer, dict] = None,
        comment: str = "via pyQiwiP2P (WhiteApfel)",
        pay_sources: list[str] = None,
        theme_code: str = None,
        fields: dict = None,
    ) -> Bill:
        """
        Метод для выставления счета.

        :param bill_id: идентификатор заказа/счета в вашей системе. Если параметр не укзаан, генерируется строка, основанная на времени.
        :type bill_id: ``str`` or ``int``, optional
        :param amount: сумма заказа в рублях. Округляется до двух знаков после запятой. Если не указано, используется значение по умолчанию
        :type amount: ``int`` or ``float``, optional
        :param currency: валюта платежа. ``RUB`` - рубли,  ``KZT`` - тенге
        :type currency: ``str`` or None, optional
        :param expiration: когда счет будет закрыт. Принимает: Timestamp, Datetime или строку формата ``YYYY-MM-DDThh:mm:ss+hh:mm``.
        :type expiration: ``int``, ``datetime`` or ``str``, optional
        :param lifetime: время жизни счета в минутах. Если параметр ``expiration`` не указан, то будет автоматически сгенерируется дата для закрытия через ``lifetime`` минут.
        :type lifetime: ``int``, optional, default=30
        :param customer: объект QiwiCustomer или ``dict`` с полями phone, email и customer
        :type customer: ``QiwiCustomer`` or ``dict``, optional
        :param comment: комментарий к платежу. До 255 символов
        :type comment: ``str``, optional
        :param pay_sources: лист методов оплаты, которые хотим разрешить. Методы есть в классе PaymentMethods
        :type pay_sources: ``list[str]``, optional
        :param theme_code: код темы оформления, можно получить на сайте киви
        :type theme_code: ``str``, optional
        :param fields: словарь кастомных полей QIWI. Я ничего про них не понял, извините. Параметры pay_sources и theme_code перезаписывают соответствующие поля в fields
        :type fields: ``dict``, optional
        :raise QiwiError: объект ответа Qiwi, если запрос не увенчался успехом
        :return: Объект счета при успешном выполнении
        :rtype: Bill
        """
        logger.info(
            f"bill args: bill_id: {bill_id}, amount: {amount}, currency: {currency}, "
            f"expiration: {expiration}, "
            f"lifetime: {lifetime}, customer: {customer}, fields: {fields}"
        )
        fields = fields or {}
        bill_id = (
            bill_id
            or f"WhiteApfel-PyQiwiP2P-{str(int(time.time() * 100))[4:]}-"
            f"{int(random.random() * 1000)}"
        )

        amount = amount or self.default_amount
        amount_round = str(round(float(amount), 2))
        amount = (
            amount_round
            if len(str(float(amount)).split(".")[1]) > 1
            else str(round(float(amount), 2)) + "0"
        )

        expiration = (
            QiwiDatetime(moment=expiration).qiwi
            if expiration
            else QiwiDatetime(lifetime=lifetime).qiwi
        )

        if currency and currency not in ["RUB", "KZT"]:
            raise ValueError(f'Currency must be "RUB" or "KZT", not "{currency}"')
        currency = self.currency

        if pay_sources is not None:
            allowed_sources = [
                PaymentMethods.qiwi,
                PaymentMethods.card,
                PaymentMethods.mobile,
            ]
            if isinstance(pay_sources, list) and all(i in allowed_sources for i in pay_sources):
                fields['paySourcesFilter'] = ",".join(pay_sources)
            else:
                logger.warning("pay_sources must be list of str from PaymentMethods ('qw', 'card', 'mobile')")

        if theme_code is not None:
            fields['themeCode'] = theme_code

        qiwi_request_headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.auth_key}",
        }

        qiwi_request_data = {
            "amount": {"currency": currency, "value": amount},
            "comment": comment,
            "expirationDateTime": expiration,
            "customer": customer.dict
            if type(customer) is QiwiCustomer
            else QiwiCustomer(json_data=customer).dict
            if customer
            else {},
            "customFields": fields,
        }
        logger.info(
            f"bill request: bill_id: {bill_id}, amount: {amount}, "
            f"currency: {currency}, expiration: "
            f"{expiration}, lifetime: {lifetime}, "
            f"customer: {customer}, fields: {fields}"
        )
        qiwi_raw_response = self.client.put(
            f"https://api.qiwi.com/partner/bill/v1/bills/{bill_id}",
            json=qiwi_request_data,
            headers=qiwi_request_headers,
        )
        qiwi_response = Bill(qiwi_raw_response, self.alt)
        logger.info(f"bill created: pay_url: {qiwi_response.pay_url}")
        return qiwi_response

    def check(self, bill_id: typing.Union[str, int, Bill]) -> Bill:
        """
        Проверяет статус выставленного счета.

        :param bill_id: идентификатор заказа/счета в вашей системе
        :type bill_id: ``str`` or ``int``
        :return: Объект счета при успешном выполнении
        :rtype: Bill
        """
        logger.info(f"check bill: bill_id: {bill_id}")
        if type(bill_id) is Bill:
            bill_id = bill_id.bill_id
        qiwi_request_headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.auth_key}",
        }

        qiwi_raw_response = self.client.get(
            f"https://api.qiwi.com/partner/bill/v1/bills/{bill_id}",
            headers=qiwi_request_headers,
        )
        qiwi_response = Bill(qiwi_raw_response, self.alt)
        logger.info(f"checked bill: bill_id: {bill_id}, status: {qiwi_response.status}")
        return qiwi_response

    def reject(self, bill_id: typing.Union[str, int, Bill]) -> Bill:
        """
        Закрывает счет на оплату.

        :param bill_id: идентификатор заказа/счета в вашей системе
        :type bill_id: ``str`` or ``int``
        :return: Объект счета при успешном выполнении
        :rtype: Bill
        """
        logger.info(f"reject bill: bill_id: {bill_id}")
        if type(bill_id) is Bill:
            bill_id = bill_id.bill_id
        qiwi_request_headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.auth_key}",
        }
        qiwi_raw_response = self.client.post(
            f"https://api.qiwi.com/partner/bill/v1/bills/{bill_id}/reject",
            headers=qiwi_request_headers,
        )
        qiwi_response = Bill(qiwi_raw_response, self.alt)
        logger.info(
            f"rejected bill: bill_id: {bill_id}, status: {qiwi_response.status}"
        )
        return qiwi_response
