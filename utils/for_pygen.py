"""Utils for pygen."""
import json
import socket
from dataclasses import dataclass
from math import isclose

from _pytest.python_api import ApproxBase


class Caller:
    def __init__(self, ip_address):
        self.ip = ip_address
        self.port = 9090
        self.socket = socket.socket()
        self.socket.settimeout(3)  # 0 for non-blocking mode
        self.connect()

    def send(self, command: str):
        if not command.endswith(r'\n'):
            command += '\n'
        self.socket.send(command.encode())

    def receive(self, buffer_size=2048):
        received = self.socket.recv(buffer_size).decode()
        if received and not received.endswith('\n'):
            return received + self.receive()
        else:
            return received.replace('\n', '')

    def send_and_receive(self, command: str, buffer_size=1024):
        self.send(command)
        return self.receive(buffer_size)

    def connect(self):
        self.socket.connect((self.ip, self.port))

    def _disconnect(self):
        """Be careful with closing socket if there is something to receive in channel"""
        self.socket.close()

    def __del__(self):
        self.send('closing')
        self.socket.close()


class Command:
    """Descriptor for sending command to device with passing args or kwargs."""

    def __init__(self, arg_type, cmd_id: int, return_type):
        self.arg_type = arg_type  # Don't check explicitly
        self.cmd_id = cmd_id
        self.return_type = return_type

    def __get__(self, instance: Caller, instance_type=None):
        def _caller(*args, **kwargs):
            # str_command = f'{self.cmd_id}:: {args};{kwargs}'
            str_command = json.dumps(dict(cmd_id=self.cmd_id, args=args, kwargs=kwargs))
            result = json.loads(instance.send_and_receive(str_command))
            result = ReturnMessage(**result)
            return result.in_instance_class(instance)

        return _caller


@dataclass
class ReturnMessage:
    type: str
    data: int | str | dict

    def in_instance_class(self, instance: Caller):
        """convert type to Inctance.Class"""
        if self.type in {'int', 'str', 'float', 'list'}:
            return eval(self.type)(self.data)

        return_type = getattr(instance, self.type, None)

        try:
            if isinstance(self.data, (int, str)):
                return return_type(self.data)
            elif isinstance(self.data, dict):
                return return_type(**self.data)
        except Exception as e:
            return self


class AttrDict(dict):
    """
    Словарь с возможностью аттрибутного обращения
    вместо d["key"] = 10 можно использовать
    d.key=10
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for key, value in self.items():
            if isinstance(value, dict):
                self[key] = AttrDict(value)

    def __getattr__(self, item):
        value = self.get(item, AttributeError)
        if value is AttributeError:
            raise value
        else:
            return value  # Чтобы не было "self.__dict__ = self" и дублирующих аттрибутов в виде строки

    def __setattr__(self, key, value):
        """Tries to write in __dict__ by default"""
        self[key] = value

    def __eq__(self, other):
        if isinstance(other, dict):
            return super().__eq__(other)
        elif isinstance(other, ApproxBase):
            return other == self  # ApproxBase знает, что делать
        elif hasattr(other, '__dict__'):
            return self == other.__dict__
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def copy(self):
        return AttrDict(super().copy())

    def as_dict(self):
        new_dict = dict()
        for key, value in self.items():
            new_dict[key] = value.as_dict() if isinstance(value, AttrDict) else value
        return new_dict

    def almost_equal(self, other_obj, *, rel_tol=1e-07, abs_tol=0.0):
        """
        Use if float inside objects.
        math.isclose inside
        """
        if isinstance(other_obj, dict):
            if self.keys() != other_obj.keys():
                return False
            result = True

            for key, value in self.items():
                if isinstance(value, (float, int)) and isinstance(other_obj[key], (float, int)):
                    result = result and isclose(value, other_obj[key], rel_tol=rel_tol, abs_tol=abs_tol)
                elif isinstance(value, AttrDict):
                    result = result and value.almost_equal(other_obj[key], rel_tol=rel_tol, abs_tol=abs_tol)
                else:
                    result *= value == other_obj[key]
            return result
        elif hasattr(other_obj, '__dict__'):
            return self.almost_equal(other_obj.__dict__)
        else:
            raise TypeError(f'You can not compare {type(other_obj)} with AttrDict')

