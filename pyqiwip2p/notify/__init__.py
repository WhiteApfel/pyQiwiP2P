import hashlib
import hmac
import json
import threading

import cherrypy

from pyqiwip2p.notify.async_client import AioQiwiNotify
from pyqiwip2p.p2p_types import Bill


class QiwiNotify:
    """
    Штучка, чтобы работать с серверными уведомлениями Qiwi. Запускает сервер для приема уведомлений. А ещё тут есть хендлеры.

    :param auth_key: приватный ключ, на который настроен прием уведомлений.
    :type auth_key: ``str``
    """

    def __init__(self, auth_key: str, once=True):
        self.auth_key = auth_key
        self.handlers = []
        self.once = once

    def handler(self, func=None):
        def decorator(handler):
            self.handlers.append({"handler": handler, "filter": func})
            return handler

        return decorator

    def _check_valid(self, bill: Bill, sha256: str):
        invoice_parameters = f"{bill.currency} | {bill.amount} | {bill.bill_id} | {bill.site_id} | {bill.status}"
        return (
            hmac.new(
                self.auth_key.encode(), invoice_parameters.encode(), hashlib.sha256
            ).hexdigest()
            == sha256
        )

    def _parse(self, response, sha256):
        bill = Bill(response)
        if self._check_valid(bill, sha256):
            self._check(bill)
        else:
            raise cherrypy.HTTPError(403)

    def _check(self, bill):
        for handler in self.handlers:
            if handler["filter"](bill):
                handler["handler"](bill)
            if self.once:
                break

    def start(qiwi, port: int = 8099):
        """
        Функция для запуска веб-сервера, который будет обрабатывать входящие запросы и запускать захендленные функции.
        Внимание, предполагается проксирование, так как Qiwi отправляет запросы на
        443 порт серверов с шифрованием доверенным сертификатом (SSL). Подниманиемый сервер не защищен никаким
        сертификатом и вообще ничего не может сделать для Qiwi. Рекомендую настроить Nginx.

        :param port: номер порта, на котором запустится сервер.
        :type port: ``int``
        """

        class WebhookServer(object):
            def check_headers(self, headers):
                if (
                    "content-type" in headers
                    and headers["content-type"] == "application/json"
                    and "X-Api-Signature-SHA256" in headers
                ):
                    return True
                return False

            @cherrypy.expose
            def qiwi_notify(self):
                if self.check_headers(cherrypy.request.headers):
                    json_string = cherrypy.request.body.read().decode("utf-8")
                    qiwi._parse(
                        json.loads(json_string),
                        cherrypy.request.headers["X-Api-Signature-SHA256"],
                    )
                    return ""
                raise cherrypy.HTTPError(403)

        cherrypy.config.update({"server.socket_port": port})
        t = threading.Thread(
            target=lambda ws: cherrypy.quickstart(ws()), args=(WebhookServer,)
        )
        t.start()
