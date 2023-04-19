# pylint: disable=arguments-differ
import re

import attr
from typing import List

from ..factory import target_factory
from ..protocol import CommandProtocol, ConsoleProtocol, FileTransferProtocol, PowerProtocol, PowerResetProtocol, SysbootProtocol, PowerMeterProtocol, ConfigurationProtocol, RailData
from .common import Driver
from .commandmixin import CommandMixin
from .consoleexpectmixin import ConsoleExpectMixin


@target_factory.reg_driver
@attr.s(eq=False)
class FakeConsoleDriver(ConsoleExpectMixin, Driver, ConsoleProtocol):
    txdelay = attr.ib(default=0.0, validator=attr.validators.instance_of(float))

    def __attrs_post_init__(self):
        super().__attrs_post_init__()
        self.rxq = []
        self.txq = []

    def _read(self, *_, **__):
        if self.rxq:
            return self.rxq.pop()
        return b''

    def _write(self, data, *_):
        self.txq.append(data)
        mo = re.match(rb'^echo "(\w+)""(\w+)"\n$', data)
        if mo:
            self.rxq.insert(0, b''.join(mo.groups())+b'\n')

    def open(self):
        pass

    def close(self):
        pass


@target_factory.reg_driver
@attr.s(eq=False)
class FakeCommandDriver(CommandMixin, Driver, CommandProtocol):
    
    @Driver.check_active
    def run(self, *args, timeout=None):
        pass

    @Driver.check_active
    def run_check(self, *args):
        pass

    @Driver.check_active
    def get_status(self):
        pass


@target_factory.reg_driver
@attr.s(eq=False)
class FakeFileTransferDriver(Driver, FileTransferProtocol):

    @Driver.check_active
    def get(self, *args):
        pass

    @Driver.check_active
    def put(self, *args):
        pass

@target_factory.reg_driver
@attr.s(eq=False)
class FakePowerDriver(Driver, PowerProtocol):
    bindings={ "console": "ConsoleProtocol" }
    
    def __attrs_post_init__(self):
        super().__attrs_post_init__()
        
    @Driver.check_active
    def on(self, *args):
        pass

    @Driver.check_active
    def off(self, *args):
        pass

    @Driver.check_active
    def cycle(self, *args):
        pass

@target_factory.reg_driver
@attr.s(eq=False)
class FakeResetDriver(Driver, PowerResetProtocol):
    bindings = { "console": "ConsoleProtocol" }
    
    def __attrs_post_init__(self):
        super().__attrs_post_init__()
        
    @Driver.check_active
    def reset(self):
        self.console.sendline(b"fake data from fake reset driver") 

    # @Driver.check_active
    def por(self):
        self.console.sendline(b"fake data from fake reset driver")
    
    @Driver.check_active
    def hold_por(self):
        self.console.sendline(b"fake data from fake reset driver")
    
    @Driver.check_active
    def release_por(self):
        self.console.sendline(b"fake data from fake reset driver")

@target_factory.reg_driver
@attr.s(eq=False)
class FakeSysbootDriver(Driver, SysbootProtocol):
    bindings = { "console": "ConsoleProtocol" }
    
    def __attrs_post_init__(self):
        super().__attrs_post_init__()
    
    @Driver.check_active
    def set_bootmode(self, mode: str):
        self.console.sendline("WOWOWO writing fake bootmode {}".format(mode))


@target_factory.reg_driver
@attr.s(eq=False)
class FakePowerMeterDriver(Driver, PowerMeterProtocol):
    bindings = { "console": "ConsoleProtocol" }
    
    def __attrs_post_init__(self):
        super().__attrs_post_init__()
        
    def measure_power(self, samples: int, delay: int) -> List[RailData]:
        pass
    
    def resolve_conflicts(self, client):
        pass

@target_factory.reg_driver
@attr.s(eq=False)
class FakeConfigDriver(Driver, ConfigurationProtocol):
    bindings = { "console": "ConsoleProtocol" }
    def __attrs_post_init__(self):
        super().__attrs_post_init__()
        
    def set_dut(self, dut: str):
        # self.console.write_line("WOWOWO writing fake dut {}".format(dut))
        pass
