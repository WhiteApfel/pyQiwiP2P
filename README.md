# pyQiwiP2P

### Предисловие
Штучка для удобной работы с кивишной апишкой платежей

Есть типа [документация](https://pyqiwip2p.readthedocs.io/ru/latest/), но в ней есть и косячки, поэтому, 
если найдёте таковой, обязательно сообщите мне. Буду искренне рад. Правда. Спасибо.

---

### Что есть?
Есть сам класс QiwiP2P, который обладает тремя инструментами:
для выставления, проверки и закрытия платежа (счёта). 


Пример использования:

```python
from pyqiwip2p import QiwiP2P
from pyqiwip2p.types import QiwiCustomer, QiwiDatetime

QIWI_PRIV_KEY = "abCdef...xYz"


p2p = QiwiP2P(auth_key=QIWI_PRIV_KEY)

# Выставим счет на сумму 228 рублей который будет работать 45 минут
new_bill = p2p.bill(bill_id=212332030, amount=228, lifetime=45)

print(new_bill.bill_id, new_bill.pay_url)

# Проверим статус выставленного счета
print(p2p.check(bill_id=new_bill.bill_id).status)

# Потеряли ссылку на оплату счета? Не проблема!
print(p2p.check(bill_id=245532).pay_url)

# Клиент отменил заказ? Тогда и счет надо закрыть
p2p.reject(bill_id=new_bill.bill_id)


# Если планируете выставлять счета с одинаковой суммой,
# можно воспользоваться параметром default_amount
p2p = QiwiP2P(auth_key=QIWI_PRIV_KEY, default_amount=148)

# Теперь, если не указывать в методе p2p.bill() значение суммы заказа,
# будет применяться указанная базовая сумма
new_bill = p2p.bill(bill_id=6627358)

# А ещё можно не указывать bill_id, тогда значение сгенерируется автоматически.
# Его можно будет посмотреть в объекте ответа Bill
# В комбинации со стандартным значением суммы будет вот так
new_bill = p2p.bill()
print(new_bill.bill_id, new_bill.pay_url)
```

### И всё?
Нет, не всё. Ещё можно настроить кивишные уведомления на свой сервер, 
для этого придется немного пострадать, но лишь немного.

**Внимание!** Для работы будет необходим проксирующий сервер (например, Nginx) с доверенным SSL-сертификатом. 
Да. Подробнее про требования к проксирующему серверу в [документации Qiwi](https://developer.qiwi.com/ru/p2p-payments/?shell#notification "Почитай, это полезно")

А эта шайтан-машина нужна для захендлирования функций на события. Она не готова самостоятельно контактировать с внешним миром. Пожалей её.

Запросы сервер по умолчанию принимает на 8099 порту, его можно изменить, и только на `/qiwi_notify` - изменить нельзя.

```python
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
```
### Настройка проксирующего Nginx
Для порта 12345 (как в примере выше) будет:
```
server {
    listen 443;
    server_name qiwinotify.domain.com;
    ssl_certificate      cert.crt;
    ssl_certificate_key  pkey.key;
    location /superSecretQiwiURI {
        proxy_pass http://0.0.0.0:12345/qiwi_notify;
    }
}
```
В таком случае при генерации ключей API на https://qiwi.com/p2p-admin/transfers/api
нужно будет указать `https://qiwinotify.domain.com/superSecretQiwiURI` в качестве URL для уведомлений

**P.S. за неприходящие от Qiwi запросы ответсвенность не несу, как и за приходящие, кстати, тоже.
Если запроса от Qiwi не было, то пишите им в поддержку [@qiwi_api_help_bot](https://t.me/qiwi_api_help_bot)**
