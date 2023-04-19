import attr
import logging
import re
from dataclasses import dataclass
from labgrid.protocol import RailData, TAIProtocol, SysbootProtocol, PowerMeterProtocol, PowerResetProtocol, ConfigurationProtocol, PowerProtocol, ConsoleProtocol, SysbootRepository
from typing import Dict, List
from .common import Driver
from ..step import step
from ..factory import target_factory


@target_factory.reg_driver
@attr.s(eq=False)
class TAIDriver(Driver, TAIProtocol):
    """
    TODO: Does this driver actually NEED to be active? Or just the underlying ones?
    TODO: Same question for the @step decorators - here or the actual impl?
    """
    bindings = {
        "power_meter_handle": PowerMeterProtocol,
        "por_handle": PowerResetProtocol,
        "power_handle": PowerProtocol,
        "sysboot_handle": SysbootProtocol,
        "config_handle": ConfigurationProtocol
    }
    prompt = attr.ib(default="=>", validator=attr.validators.instance_of(str))
    
    def __attrs_post_init__(self):
        super().__attrs_post_init__()
    
    def _deactivate_all(self):
        """Disable all bound drivers on target (except self) - put into bound state"""
        for k,cls in self.bindings.items():
            driver = self.target.get_driver(cls)
            if self.__class__==driver.__class__:
                continue
            self.target.deactivate(driver)
    
    def _activate_on_target(self, driver: str):
        """Deactivate all others, then activate target"""
        self._deactivate_all()
        driver = self.target.get_driver(driver)
        self.target.activate(driver)
     
    @step(args=["dut"])
    def set_dut(self, dut: str):
        self._activate_on_target("ConfigurationProtocol")
        self.config_handle.set_dut(dut)

    @step(args=["code"])
    def set_bootmode(self, code: str):
        self._activate_on_target("SysbootProtocol")
        self.sysboot_handle.set_bootmode(code)

    @step()
    def por(self):
        self._activate_on_target("PowerResetProtocol")
        self.por_handle.por()

    @step()
    def hold_por(self):
        self._activate_on_target("PowerResetProtocol")
        self.por_handle.hold_por()
    
    @step()
    def release_por(self):
        self._activate_on_target("PowerResetProtocol")
        self.por_handle.release_por()
    
    @step()
    def power_on(self):
        self._activate_on_target("PowerProtocol")
        self.power_handle.on()
    
    @step()
    def power_off(self):
        self._activate_on_target("PowerProtocol")
        self.power_handle.off()
    
    @step()
    def reset(self):
        self._activate_on_target("PowerResetProtocol")
        self.por_handle.reset()

    @step(args=["samples", "delay"])
    def measure_power(self, samples: int, delay: int) -> List[RailData]:
        self._activate_on_target("PowerMeterProtocol")
        self.power_meter_handle.measure_power(samples, delay)


class InMemorySysbootRepostory(SysbootRepository):

    def __attrs_post_init__(self):
        super().__attrs_post_init__()
        self.data: Dict[str, List(str, str)] = self.__init_data()
        self.logger = logging.getLogger(f"{self}:")

    def get_sysboot_code_by_dut_type_and_mode(self, dut_type: str, mode: str) -> str:
        """
        Returns the target sysboot code for given platform and target mode - else None
        i.e. am62xx-sk, mmc => 0243
        """
        if dut_type in self.data:
            dut_map = self.data[dut_type]
            if mode in dut_map:
                return dut_map[mode]
        raise KeyError

    def save(self, dut_type, mode, code):    
        self.data[dut_type] = (mode, code)

    def __init_data(self):
        data = {}
        data['am62xx-sk'] = {
            ('mmc', '0243')
        }
        return data

@target_factory.reg_driver
@attr.s(eq=False)
class TIVAPowerDriver(PowerProtocol):
    bindings = {"console": ConsoleProtocol, }

@target_factory.reg_driver
@attr.s(eq=False)
class TIVAPorDriver(PowerResetProtocol):
    bindings = {"console": ConsoleProtocol, }

@target_factory.reg_driver
@attr.s(eq=False)
class TIVASysbootDriver(SysbootProtocol):
    
    bindings = { "console": ConsoleProtocol, "repository": SysbootRepository }
    dut_type = attr.ib(validator=attr.validators.instance_of(str))
    def __attrs_post_init__(self):
        super().__attrs_post_init__()
        self.logger = logging.getLogger(f"{self}:")

    def set_bootmode(self, mode: str):
        """
        Responsible for setting the target bootmode on the device
        """
        code = self.repository.get_sysboot_code_by_dut_type_and_mode(self.dut_type, mode)
        assert(code != None)
        self.logger.info("Using code: {} for target bootmode: {}".format(code, mode))
        self.console.write_line("auto sysboot {}\r\n".format(code))
        

class TIVAConfigDriver(ConfigurationProtocol):
    bindings = {"console": ConsoleProtocol, }

class TIVAPowerMeterDriver(PowerMeterProtocol):
    bindings = {"console": ConsoleProtocol, }

    def measure_power(self, samples: int, delay: int) -> List[RailData]:
        raise NotImplementedError

def extract_rail_data(input_string: str) -> List[RailData]:
    """
    Factory method which will extract the power measurement data into a collection of RailData domain objects
    If we start using different data formats (like JSON or CSV) and want to support those then this should be 
    updated to use a factory-style approach
    """
    pattern = r'\|\s*(\d+)\s*\|\s*(\w+)\s*\|\s*([\d.]+)\s*\|\s*([\d.]+)\s*\|\s*([\d.]+)\s*\|\s*([\d.]+)\s*\|'
    regex = re.compile(pattern) 
    matches = regex.findall(input_string) 
    rail_data_list = [] 
    for match in matches: 
        rail_data = RailData(int(match[0]), match[1], float(match[2]), float(match[3]), float(match[4]), float(match[5])) 
        rail_data_list.append(rail_data)
    return rail_data_list

    

