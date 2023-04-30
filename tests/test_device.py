"""Проверки прибора."""
import pytest
from loguru import logger
import os
import sys
from time import sleep

sys.path.append(os.getcwd())
from pygen.device import Device
from utils.variables import MIN_TEMPERATURE, MAX_TEMPERATURE, MAX_CONSUMPTION, SERIAL_NUMBER, START_TIME, TIME_DELAY, \
    DELTA_TIME


@pytest.fixture()
def device() -> Device:
    device_ = Device(0x12)

    yield device_


def test_version(device):
    version = device.get_tm(device.TmId.version)
    logger.info(f'Actual version: {version}')
    assert version.minor > 0


def test_bus_main(device):
    """Проверка установки приоритетной шины - главная"""

    # Устанавливаем приоритетную шину - главная
    change_bus = device.set_active_bus(device.ActiveBus.main)
    logger.info('Send command set active bus main')
    logger.info(f'Result of set active bus: {change_bus}')
    logger.info(f'Type: {type(change_bus)}')
    # проверяем приоритетную шину по телеметрии
    active_bus = device.get_tm(device.TmId.active_bus)
    logger.info(f'Active bus: {active_bus}')
    assert ((change_bus == device.ResultCode.ok) and (active_bus == device.ActiveBus.main) and isinstance(
        change_bus, device.ResultCode))


def test_bus_reserve(device):
    """Проверка установки приоритетной шины - резервная"""

    # Устанавливаем приоритетную шину - резервная
    change_bus = device.set_active_bus(device.ActiveBus.reserve)
    logger.info('Send command set active bus reserve')
    logger.info(f'Result of set active bus: {change_bus}')
    # проверяем приоритетную шину по телеметрии
    active_bus = device.get_tm(device.TmId.active_bus)
    logger.info(f'Active bus: {active_bus}')
    assert ((change_bus == device.ResultCode.ok) and (active_bus == device.ActiveBus.reserve))


def test_time(device):
    """Проверка установки текущего времени"""
    # запрашиваем текущее время
    time = device.get_tm(device.TmId.current_time)
    logger.info(f'Current time: {time}')
    # устанавливаем нужное время
    result = device.set_time(START_TIME)
    # ждем определенное время
    sleep(TIME_DELAY)
    # запрашиваем текущее время
    new_time = device.get_tm(device.TmId.current_time)
    logger.info(f'New current time: {new_time}')
    # проверяем что время установилось с учетом задержки времени и зазора на выдачу команды и запроса ТМ
    assert ((result == device.ResultCode.ok) and (
            (START_TIME + TIME_DELAY + DELTA_TIME) > new_time >= (START_TIME + TIME_DELAY)))


def test_reboot(device):
    """Проверка перезагрузки прибора"""
    # запрашиваем кол-во перезапусков в ТМ
    reset_count = device.get_tm(device.TmId.operating_time).reboot_count
    logger.info(f'Reboot count: {reset_count}')
    # перезагружаем прибор
    result = device.reset()
    # снова запрашиваем кол-во перезапусков в ТМ
    new_reset_count = device.get_tm(device.TmId.operating_time).reboot_count
    logger.info(f'Reboot count: {new_reset_count}')
    # проверяем что кол-во перезапусков увеличилось на 1
    assert ((result == device.ResultCode.ok) and (new_reset_count == reset_count + 1))


def test_temperature(device):
    """Проверка температуры прибора на соответствие рабочему диапазону"""
    # запрашиваем температуру прибора
    current_temperature = device.get_tm(device.TmId.temperature)
    logger.info(f'Сurrent temperature: {current_temperature}')
    """сравниваем значение температуры на соответствие рабочему диапазону
    в случае непрохождения теста СРОЧНО предпринять меры!"""
    assert MIN_TEMPERATURE < current_temperature < MAX_TEMPERATURE


def test_consumption(device):
    """Проверка мощности потребления прибора"""
    # запрашиваем мощность потребления прибора
    current_consumption = device.get_tm(device.TmId.consumption)
    logger.info(f'Сurrent consumption: {current_consumption}')
    # сравниваем значение мощности потребления на соответствие документации
    assert current_consumption <= MAX_CONSUMPTION
    """Результат проверки положительный, однако, имитатор выдает 'Device' object has no attribute 'consumption',
    значение current_consumption равно 5 это ResultCode.NotImplemented, означающий что ТМ-параметр
    мощности потребления не реализован, ниже есть проверка типов получаемых данных"""


def test_operation_time(device):
    """Проверка операционного времени прибора"""
    # перезагрузим прибор
    device.reset()
    # запросим в ТМ операционное время
    oper_time = device.get_tm(device.TmId.operating_time)
    logger.info(f'Operating time: {oper_time.operating_time}')
    logger.info(f'Total time: {oper_time.total_time}')
    """ проверим что время с последнего включения меньше зазора времени на выдачу команды
    (обнулилось при перезагрузке прибора) и что общее время работы прибора больше времени
    с последнего включения (перезагрузки)"""
    assert ((oper_time.operating_time < DELTA_TIME) and (oper_time.operating_time < oper_time.total_time))


def test_serial(device):
    # Проверка установки серийного номера
    # запрашиваем серийный номер прибора
    base_serial = device.get_tm(device.TmId.serial)
    logger.info(f'Serial number device: {base_serial}')
    # устанавливаем свой серийный номер прибора
    result = device.set_serial(SERIAL_NUMBER)
    # проверяем серийный номер по телеметрии
    new_serial = device.get_tm(device.TmId.serial)
    logger.info(f'New serial number device: {new_serial}')
    assert ((result == device.ResultCode.ok) and (new_serial == SERIAL_NUMBER))

    """При повторной установке серийного номера вызывает ошибку 'доступ запрещен' (PermissionDenied), получается
    что установить серийный номер можно только после его отключения и включения (перезагрузка не помогает)"""


"""Серия проверок на типы получаемых данных"""


def test_type_active_bus(device):
    active_bus = device.get_tm(device.TmId.active_bus)
    logger.info(f'Type active_bus {type(active_bus)}')
    assert isinstance(active_bus, device.ActiveBus) and not isinstance(active_bus, device.ResultCode)


def test_type_temperature(device):
    temperature = device.get_tm(device.TmId.temperature)
    logger.info(f'Type temperature {type(temperature)}')
    assert isinstance(temperature, int | float) and not isinstance(temperature, device.ResultCode)


def test_type_version(device):
    version = device.get_tm(device.TmId.version)
    logger.info(f'Type version {type(version)}')
    assert isinstance(version, device.Version) and not isinstance(version, device.ResultCode)


def test_type_serial(device):
    serial = device.get_tm(device.TmId.serial)
    logger.info(f'Type serial {type(serial)}')
    assert isinstance(serial, str) and not isinstance(serial, device.ResultCode)


def test_type_current_time(device):
    current_time = device.get_tm(device.TmId.current_time)
    logger.info(f'Type current_time {type(current_time)}')
    assert isinstance(current_time, int | float) and not isinstance(current_time, device.ResultCode)


def test_type_operating_time(device):
    operating_time = device.get_tm(device.TmId.operating_time)
    logger.info(f'Type operating_time {type(operating_time)}')
    assert isinstance(operating_time, device.OperatingTimeInfo) and not isinstance(operating_time, device.ResultCode)


def test_type_consumption(device):
    consumption = device.get_tm(device.TmId.consumption)
    logger.info(f'Type consumption {type(consumption)}')
    assert isinstance(consumption, int | float) and not isinstance(consumption, device.ResultCode)
    """Результат проверки отрицательный, ТМ-параметр потребления не реализован"""
