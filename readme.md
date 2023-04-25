# Тестовое задание
В этом задании Вам предстоит показать свои умения:
* в анализе онлайн документации
* чтения кода
* написания тестов

## Что нужно сделать?
Необходимо протестировать функционал прибора.

## Что понадобится?
* Pycharm
* Python 3 (рекомендуется 3.10)
* poetry

## Что уже есть?
* API прибора. Это тот самый функционал, который нужно протестировать.
В условиях данного задания это единственная документация на прибор. Он находится в `pygen/device.py`
* Имитатор прибора. Он будет отвечать на запросы. Он находится в `utils/device.exe`
* Первая написанная проверка в качестве примера `tests/test_device.py`

## На что мы обратим внимание:
* Покрытие проверками. Вы должны быть уверены, что сможете уловить ошибку.
* Читаемость кода. Написанный единожды код будут многократно читать разные люди.


# Начало работы
Можете установить зависимости любым удобным способом: через `poetry` или просто через `requirements.txt`


## requirements.txt
Достаточно команды 
```shell
pip install -r requirements.txt
```

## Poetry
В проекте используется менеджер зависимостей poetry. Подробнее [здесь](https://python-poetry.org/).
Если Вы ничего не слышали про Poetry - ничего страшного.
Вы можете все же настроить окружение по инструкции ниже или просто перейти к пункту `requirements.txt`
Достаточно установить poetry в системный Python
```shell
pip install poetry==1.2
```
После чего настроить работу с окружением в PyCharm.
[Set up poetry environment in PyCharm](https://www.jetbrains.com/help/pycharm/poetry.html#poetry-env).
После проделанных действий нужно установить необходимые пакеты
```shell
poetry install
```
И выбрать интерпретатор (`python.exe`) из только что созданного виртуального окружения


# Дополнительная информация
* Выполнение команды возвращает статусный код (`ResultCode`)
* Тип аргумента для команды указан в `arg_type`. Если `None` то аргумент не нужен

# Полезные ссылки
* [pytest doc](https://docs.pytest.org/en/7.1.x/contents.html)
  * [how to use fixtures](https://docs.pytest.org/en/7.1.x/how-to/fixtures.html#how-to-use-fixtures)
  * [parametrization](https://docs.pytest.org/en/7.1.x/how-to/parametrize.html)
  * [expected exception](https://docs.pytest.org/en/7.1.x/getting-started.html#assert-that-a-certain-exception-is-raised)
* [poetry doc](https://python-poetry.org/docs/)
* [pytest in pycharm](https://www.jetbrains.com/help/pycharm/pytest.html)