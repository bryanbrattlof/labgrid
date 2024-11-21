
import attr
import re

from ..factory import target_factory
from ..protocol import BootModeProtocol, ConsoleProtocol
from ..step import step
from .common import Driver


@target_factory.reg_driver
@attr.s(eq=False)
class TIVABootModeDriver(Driver, BootModeProtocol):
    """TIVABootModeDriver - Driver using a TIVA-C Microcontroller to control
    a target's bootmode
    """
    bindings = {"console": ConsoleProtocol, }
    dut = attr.ib(default="am62xx-sk", validator=attr.validators.instance_of(str))

    @Driver.check_active
    @step(args=['mode'])
    def set(self, mode: int) -> None:
        """set the raw devstat value for the target"""
        self.console.sendline(f"auto sysboot {mode:04x}")
        self.console.expect("Sysboot set on DUT")
