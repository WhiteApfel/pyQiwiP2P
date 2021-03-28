Как пользоваться
================

::

 from pyqiwip2p import QiwiP2P
 from pyqiwip2p.types import QiwiCustomer, QiwiDatetime

 QIWI_PRIV_KEY = "abCdef...xYz"


 p2p = QiwiP2P(auth_key=QIWI_PRIV_KEY)

 # Выставим счет на сумму 228 рублей который будет работать 45 минут
 new_bill = p2p.bill(bill_id=212332030, amount=228, lifetime=45)

 print(new_bill.bill_id, new_bill.pay_url)

 # Проверим статус выставленного счета
 print(p2p.check(bill_id=new_bill.bill_id).status)

 # Или через сам объект класса Bill
 # Внимание! При кажом обращении к Bill.actual происходит получение
 # данных от Qiwi.
 print(bill.actual.status)

 # Если необходимо просто обновить и дальше работать с актуальным
 # объектом, то достаточно воспользоваться методом Bill.update_info()
 bill.update_info()
 print(bill.bill_id, bill.status, bill.status_changed)

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