# pyQiwiP2P

[![CodeFactor](https://www.codefactor.io/repository/github/whiteapfel/pyqiwip2p/badge)](https://www.codefactor.io/repository/github/whiteapfel/pyqiwip2p)

## Поддержка прекращена

Есть более качественный инструмент, полностью покрывающий функции pyQiwiP2P: [glQiwiApi](https://github.com/GLEF1X/glQiwiApi)

Возможно, здесь когда-нибудь будет гайд по миграции на него, но всё в руках сообщества

### О библиотеке

Штучка для удобной работы с кивишной апишкой платежей

Есть типа [документация](https://pyqiwip2p.readthedocs.io/ru/latest/), но в ней есть и косячки, поэтому, 
если найдёте таковой, обязательно сообщите мне. Буду искренне рад. Правда. Спасибо.

### Миграция с первой версии:

 1. Свойство ``Bill.actual`` было удалено из-за PEP8
 2. ``QiwiNotify`` по умолчанию выполняет только функцию по первому подошедшему хендлеру

### ⚠️ Важное уведомление [2023.04.05]

Выпуск ключей для приёма P2P платежей через сайт официально закрыт, 
но метод, заявленный в [документации QIWI](https://github.com/QIWI-API/qiwi-wallet-personal-docs/blob/94cf6b68a12dea916d99144b4f7a12ab810753d5/_payment_ru.html.md#выпуск-токена-p2p-p2p-token), 
продолжает работать, хоть и с несколько изменённой авторизацией. 

Инструкция:

1. Переходим на https://qiwi.com/p2p-admin
2. Авторизуемся в свой Qiwi аккаунт
3. Открываем консоль браузера. [Как?](https://duckduckgo.com/?q=Как+открыть+консоль+браузера)
4. Вставляем код из первого блока и нажимаем enter
5. Вставляем код из второго блока и нажимаем enter
6. Если прошло успешно:
   * появится строка "Private Key: <KEY>"
   * копируем ключ, и используем по назначению
7. Если что-то пошло не так:
   * смириться, что накосячили
   * меня не тревожить
   * мне в личку не писать
   * кусаюсь и кидаю в чс

```javascript
function createKeys(name, notification_url) {
    let p2pApiData = JSON.parse(localStorage.getItem("p2p-admin-checkout-oauth-token-head"))
    let token = btoa(p2pApiData["client_id"] + ":" + p2pApiData["access_token"]).replaceAll("=", "")

    let body = {
        keysPairName: name
    }

    if (notification_url) {
        body.serverNotificationsUrl = notification_url
    }

    fetch('https://edge.qiwi.com/widgets-api/api/p2p/protected/keys/create', {
        method: 'POST',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': "TokenHeadV2 " + token
        },
        body: JSON.stringify(body),
        credentials: 'include',
    })
    .then(response => {
        console.log(response.status);
        return response.json();
    })
    .then(data => {
        console.log(data);
        console.log("Private Key: "+ data.result.secretKey)
    })
    .catch(error => console.error(error));
}
```
```javascript
createKeys("Tokens by WhiteApfel")
// or
createKeys("Tokens by WhiteApfel", "https://qiwi.example.com/any")
```

### ⚠️ Важное уведомление [2021.06.13]

С июня Qiwi начала блокировать кошельки, если пользователь открыл
страницу оплаты "напрямую", тем самым не передав заголовок referer.

**Это случается при открытии ссылки:**

 * из мессенджера
 * из смс
 * из письма
 * из адресной строки
 * из браузера с повышенным режимом приватности или расширениями для приватного просмотра

Для обхода всех проблем, кроме последней (она не решается), к объекту
``Bill`` был добавлен атрибут ``Bill.alt_url``, который предоставляет ссылку
для перенаправления на страницу оплаты через специальную
страницу-прокладу, добавляющую этот самый referer.

Страница предоставлена мною, но её можно поднять на своём сервере
с помощью docker-контейнера.

 * Исходники: [Github](https://github.com/WhiteApfel/pyQiwiP2P/tree/master/p2proxy)
 * Образ контейнера: ``ghcr.io/whiteapfel/pyqiwip2p:p2proxy``
 * Запуск: ``docker run -p 3600:3600 -e QP2P_DOMAIN='example.com' -d ghcr.io/whiteapfel/pyqiwip2p:p2proxy``
 * Свой домен в клиенте: ``p2p = AioQiwiP2P(PrivKey, alt="example.com")``


---
## А как пользоваться

### Что есть?
Есть сам класс QiwiP2P, который обладает тремя инструментами:
для выставления, проверки и закрытия платежа (счёта). 


Пример использования:

```python
from pyqiwip2p import QiwiP2P
from pyqiwip2p.p2p_types import QiwiCustomer, QiwiDatetime, PaymentMethods

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

# Чтобы запретить приём платежей через какой-то метод оплаты, например, карты,
# необходимо передать paySourcesFilter в fields. Туда же можно передать themeCode

fields = {
    "paySourcesFilter": "qw,card",
    "themeCode": "MalchikGay",
}
p2p.bill(fields=fields)

# Либо же воспользоваться удобными полями

p2p.bill(pay_sources=[PaymentMethods.qiwi, PaymentMethods.card])
p2p.bill(pay_sources=[PaymentMethods.qiwi], theme_code="MalchikGay")
```

### А асинхронно могёте?
Могём. Причём примерно так же.

```python
from pyqiwip2p import AioQiwiP2P
from pyqiwip2p.p2p_types import QiwiCustomer, QiwiDatetime, PaymentMethods

QIWI_PRIV_KEY = "abCdef...xYz"

p2p = AioQiwiP2P(auth_key=QIWI_PRIV_KEY)

# Если планируете выставлять счета с одинаковой суммой,
# можно воспользоваться параметром default_amount
p2p = AioQiwiP2P(auth_key=QIWI_PRIV_KEY, default_amount=148)

async def main():
    async with p2p:
        # Выставим счет на сумму 228 рублей который будет работать 45 минут
        new_bill = await p2p.bill(bill_id=212332030, amount=228, lifetime=45)
        
        print(new_bill.bill_id, new_bill.pay_url)
        
        # Проверим статус выставленного счета
        print((await p2p.check(bill_id=new_bill.bill_id)).status)
        
        # Потеряли ссылку на оплату счета? Не проблема!
        print((await p2p.check(bill_id=245532)).pay_url)
        
        # Клиент отменил заказ? Тогда и счет надо закрыть
        await p2p.reject(bill_id=new_bill.bill_id)
        
        # Если не указывать в методе p2p.bill() значение суммы заказа,
        # будет применяться указанная базовая сумма, которую вы установили
        new_bill = await p2p.bill(bill_id=6627358)
        
        # А ещё можно не указывать bill_id, тогда значение сгенерируется автоматически.
        # Его можно будет посмотреть в объекте ответа Bill
        # В комбинации со стандартным значением суммы будет вот так
        new_bill = await p2p.bill()
        print(new_bill.bill_id, new_bill.pay_url)
        
        # Чтобы запретить приём платежей через какой-то метод оплаты, например, карты,
        # необходимо передать paySourcesFilter в fields. Туда же можно передать themeCode
        
        fields = {
            "paySourcesFilter": "qw,card",
            "themeCode": "MalchikGay",
        }
        await p2p.bill(fields=fields)
        
        # Либо же воспользоваться удобными полями
        
        await p2p.bill(pay_sources=[PaymentMethods.qiwi, PaymentMethods.card])
        await p2p.bill(pay_sources=[PaymentMethods.qiwi], theme_code="MalchikGay")

p2p.run(main())
# Аналог
# asyncio.run(main())
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
from pyqiwip2p.p2p_types import Bill

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

### И асинхронный сервер, наверное, у вас есть?
Да есть. Причём хендлить функции можно и асинхронные, и синхронные.

```python
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


@qiwi_notify.handler(lambda bill: True)
def on_all(bill: Bill):
	print(bill.status)


async def main():
	p = asyncio.get_event_loop()
	server = p.create_task(qiwi_notify.a_start(port=12345))
	await server


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
```

### Настройка проксирующего Nginx
Для порта 12345 (как в примерах выше) будет:
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

**P.S. за неприходящие от Qiwi запросы ответственность не несу, как и за приходящие, кстати, тоже.
Если запроса от Qiwi не было, то пишите им в поддержку [@qiwi_api_help_bot](https://t.me/qiwi_api_help_bot)**
