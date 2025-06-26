
import attr
import inspect

from .common import Driver
from ..factory import target_factory
from ..step import step
from .exception import ExecutionError
from ..util.helper import processwrapper

@target_factory.reg_driver
@attr.s(eq=False)
class USBSDSwapDriver(Driver):
    """The USBSDSwap driver controlles the connected SDSwap device
    (https://github.com/Mr-Bossman/SD_Swap/tree/master)
    """
    bindings = {
        "mux": {"USBSDSwapDevice", "NetworkUSBSDSwapDevice"},
    }

    def __attrs_post_init__(self):
        super().__attrs_post_init__()

        bin = "sdswap"
        if self.target.env:
            bin = self.target.env.config.get_tool("sdswap")
        assert bin is not None

        # remove an starting zeros. eg: 001 == 1
        bus = int(self.mux.busnum)
        assert bus is not None

        # remove an starting zeros. eg: 001 == 1
        dev = int(self.mux.devnum)
        assert dev is not None

        self.cmd = [ bin , '-b', str(bus), '-d', str(dev) ]

    @Driver.check_active
    @step(title="sdswap_set", args=["mode"])
    def set_mode(self, mode):
        if not mode.lower() in ["dut", "host"]:
            raise ExecutionError(f"SDSwap mode {mode} is not supported")

        if mode.lower() == "dut":
            mode = "target"

        if mode == self.get_mode():
            return

        return processwrapper.check_output(
                self.mux.command_prefix + self.cmd + [
                    f"--{mode}"
                    ],
                )

    @Driver.check_active
    @step(title="sdmux_get")
    def get_mode(self):
        res = processwrapper.check_output(
                self.mux.command_prefix + self.cmd + [
                    '--show',
                    ],
                ).decode("utf-8")
        return res.split(":")[1].strip()
