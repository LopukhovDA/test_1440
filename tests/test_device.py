"""Проверки прибора."""
import pytest
from loguru import logger
import os
import sys

sys.path.append(os.getcwd())
from pygen.device import Device
from utils.variables import MIN_TEMPERATURE, MAX_TEMPERATURE, MAX_CONSUMPTION, SERIAL_NUMBER


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
    # проверяем приоритетную шину по телеметрии
    active_bus = device.get_tm(device.TmId.active_bus)
    logger.info(f'Active bus: {active_bus}')
    assert ((change_bus == device.ResultCode.ok) and (active_bus == device.ActiveBus.main))


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


def test_serial(device):
    """Проверка установки серийного номера"""

    # запрашиваем серийный номер прибора
    base_serial = device.get_tm(device.TmId.serial)
    logger.info(f'Serial number device: {base_serial}')
    # устанавливаем свой серийный номер прибора
    result = device.set_serial(SERIAL_NUMBER)
    # проверяем серийный номер по телеметрии
    new_serial = device.get_tm(device.TmId.serial)
    assert ((result == device.ResultCode.ok) and (new_serial == SERIAL_NUMBER))
