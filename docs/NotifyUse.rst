Как пользоваться уведомлениями
==============================

::

 from pyqiwip2p.notify import QiwiNotify
 from pyqiwip2p.types import Bill

 QIWI_PRIV_KEY = "abCdef...xYz"

 qiwi_notify = QiwiNotify(QIWI_PRIV_KEY)

 #
 # Хэндлер принимает в себя аргументом функцию,
 # в которую передаст объект счёта - Bill
 #

 # Добавим хэндлер, который будет печатать billID для всех счетов
 @qiwi_notify.handler(lambda bill: True)
 def print_bill(bill: Bill):
      print(bill.bill_id)

 # Создадим хэндлер, который будет печатать сумму оплаченных счетов
 @qiwi_notify.handler(lambda bill: bill.status == "PAID")
 def print_bill(bill: Bill):
      print(bill.amount)

 # Теперь запустим сервер на 12345'ом порту
 qiwi_notify.start(port=12345)

------

Уточним, что проксироваться должно на ``/qiwi_notify`` нашего сервера,
так как только этот URI обрабатывается.

Пример настройки Nginx для перенаправления запросов к нашему серверу.

В таком случае нужно при генерации ключей API на https://qiwi.com/p2p-admin/transfers/api
нужно будет указать ``https://qiwinotify.domain.com/superSecretQiwiURI``

::

 server {
     listen 443;
     server_name qiwinotify.domain.com;
     ssl_certificate      cert.crt;
     ssl_certificate_key  pkey.key;
     location /superSecretQiwiURI {
         proxy_pass http://0.0.0.0:12345/qiwi_notify;
     }
 }