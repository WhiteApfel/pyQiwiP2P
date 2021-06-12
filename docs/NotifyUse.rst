Как пользоваться уведомлениями
==============================

Qiwi может отправлять на наш сервис запросы-уведомления об изменениях статусов счетов, чтобы мы могли
осуществлять какие-то действия на таковые события, например, обновлять статус заказа в базе данных или
высылать клиенту чек об оплате в случае самозанятости.

Как составлять хендлер?

Асинхронный сервер
------------------

Рекомендуется использовать его, ибо он стабильнее, при этом поддерживает синхронные захендленные функции

::

  from pyqiwip2p import QiwiP2P, AioQiwiP2P
  from pyqiwip2p.p2p_types import Bill
  from pyqiwip2p.notify import AioQiwiNotify
  import asyncio

  QIWI_PRIV_KEY = "abCdef...xYz"

  qiwi_notify = AioQiwiNotify(QIWI_PRIV_KEY)
  p2p = AioQiwiP2P(auth_key=QIWI_PRIV_KEY)


  @qiwi_notify.handler(lambda bill: bill.status == "EXPIRED")
  async def on_expired(bill: Bill):
    new_bill = await p2p.bill(amount=bill.amount, comment=bill.comment)
    print(new_bill.pay_url)


  # Добавим хэндлер, который будет печатать billID для всех счетов
  @qiwi_notify.handler(lambda bill: True)
  def on_all(bill: Bill):
    print(bill.status)


  async def main():
    p = asyncio.get_event_loop()
    server = p.create_task(qiwi_notify.a_start(port=12345))
    await server


  loop = asyncio.get_event_loop()
  loop.run_until_complete(main())


Синхронный сервер
-----------------
Проверен временем, но лучше перейти на асинхронный

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

Уточним, что проксироваться должно на ``/qiwi_notify`` сервера,
так как только этот URI обрабатывается и синхронным, и асинхронным сервером.

Пример настройки Nginx для перенаправления запросов к серверу ниже.

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