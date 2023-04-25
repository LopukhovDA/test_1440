from dataclasses import dataclass
from enum import IntEnum

from loguru import logger

from utils.for_pygen import Command, AttrDict, Caller


class Device(Caller):
    def __init__(self, device_id: int):
        super().__init__('localhost')
        self.device_id = device_id

    class CmdId(IntEnum):
        set_active_bus = 0x6315111b
        set_serial = 0x18feb9c5c
        set_time = 0x1dc4734ff
        get_tm = 0x151db77ae
        reset = 0xe2db1244

    class TmId(IntEnum):
        active_bus = 0x129a6bf7
        temperature = 0x7cc02234
        consumption = 0x19a87e6d
        version = 0x251d1696c
        serial = 0x2457c7116
        current_time = 0x6b13fac9
        operating_time = 0x216067f17

    class ActiveBus(IntEnum):
        main = 0
        reserve = 1

    @dataclass
    class OperatingTimeInfo:
        reboot_count: int
        """Количество перезапусков"""
        operating_time: float
        """Время работы с последнего включения"""
        total_time: float
        """Общее время работы"""

    @dataclass
    class Version:
        major: int
        minor: int
        patch: int
        build: int

    class ResultCode(IntEnum):
        ok = 0
        ParamTooMany = 1
        NotEnoughData = 2
        BadArg = 3
        TmUnknown = 4
        NotImplemented = 5
        UnknownError = 6
        PermissionDenied = 7

    set_active_bus = Command(arg_type=ActiveBus, cmd_id=CmdId.set_active_bus, return_type=ResultCode)
    """Установка приоритетной шины обмена"""
    
    set_serial = Command(arg_type=str, cmd_id=CmdId.set_serial, return_type=ResultCode)
    """Установка серийного номера"""
    
    get_tm = Command(arg_type=TmId, cmd_id=CmdId.get_tm, return_type=AttrDict)
    """Запрос ТМ сообщения"""

    set_time = Command(arg_type=int | float, cmd_id=CmdId.set_time, return_type=ResultCode)
    """Установка времени"""

    reset = Command(arg_type=None, cmd_id=CmdId.reset, return_type=ResultCode)


if __name__ == '__main__':
    # Run FakeDevice.exe first
    my_device = Device(0x12)

    init_base = my_device.get_tm(my_device.TmId.active_bus)
    logger.info(f'{init_base = }')
    result = my_device.set_active_bus(my_device.ActiveBus.reserve)
    logger.info(f'Changing bus {result = }')
    logger.info(f'actual_base = {my_device.get_tm(my_device.TmId.active_bus)}')
