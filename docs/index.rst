.. PyQiwiP2P documentation master file, created by
   sphinx-quickstart on Wed Jul  8 14:22:14 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Документация PyQiwiP2P приветствует тебя!
=========================================

Удобная обёрточка для `API Qiwi P2P`_ на Python.

.. _`API Qiwi P2P`: https://developer.qiwi.com/ru/p2p-payments/#API

Важное уведомление
------------------

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

* Исходники: `Github <https://github.com/WhiteApfel/pyQiwiP2P/tree/master/p2proxy>`_
* Образ контейнера: ``ghcr.io/whiteapfel/pyqiwip2p:p2proxy``
* Запуск: ``docker run -p 3600:3600 -d ghcr.io/whiteapfel/pyqiwip2p:p2proxy``
* Свой домен в клиенте: ``p2p = AioQiwiP2P(PrivKey, alt="example.com")``


Зависимости
-----------

.. literalinclude:: ../requirements.txt

Установка
---------

Через pip:

::

 python3 -m pip install --update pyqiwip2p

Из исходников:

::

 git clone https://github.com/WhiteApfel/pyQiwiP2P
 cd pyQiwiP2P
 python setup.py install

.. toctree::
   :maxdepth: 4

   Use
   Client
   Types
   Notify
