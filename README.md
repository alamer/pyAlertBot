Бот для Telegram, оповещающий о событиях

Компоненты
=====

pyAlertBot состоит из следующих модулей:
* Avito: поиск объявлений на [Авито](https://avito.ru) по заданным параметрам и отправка сообщений в Telegram при появлении новых или изменении цены
* Youla: поиск объявлений в [Юла](https://youla.ru) по заданным параметрам и отправка сообщений в Telegram при появлении новых или изменении цены

Установка
=====

* Установить зависимости из [requirements.txt](requirements.txt)
``pip -r install requirements.txt``
* Настроить модули в файле [config.json](examples/config.json)
* ``python3 app.py``