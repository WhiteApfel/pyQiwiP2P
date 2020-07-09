Как пользоваться
================

::

 from pyqiwip2p import QiwiP2P
 from pyqiwip2p.qiwi_types import QiwiCustomer, QiwiDatetime

 QIWI_PRIV_KEY = "abCdef...xYz"

 p2p = QiwiP2P(QIWI_PRIV_KEY)

 # Выставим счет на сумму 228 рублей который будет работать 45 минут
 new_bill = p2p.bill(bill_id=212332030, amount=228, lifetime=45)

 print(new_bill.bill_id, new_bill.pay_url)

 # Проверим статус выставленного счета
 print(p2p.check(bill_id=new_bill.bill_id).status)

 # Потеряли ссылку на оплату счета? Не проблема!
 print(p2p.check(bill_id=245532).pay_url)

 # Клиент отменил заказ? Тогда и счет надо закрыть
 p2p.reject(bill_id=new_bill.bill_id)