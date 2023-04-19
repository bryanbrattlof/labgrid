

import abc
import math
# import statistics as stats
from dataclasses import dataclass
from typing import List

"""
Represents data measured from INA rails
"""
@dataclass 
class RailData:
    """
        Why do we not print out the shunt resistance ? :/
    """
    index: int
    rail_name: str
    shunt_voltage: float
    rail_voltage: float
    current: float
    power: float

"""
    TI Test automation interface
        - Facade
"""
class TAIProtocol(abc.ABC):

    @abc.abstractmethod
    def measure_power(self, delay: int, samples: int) -> List[RailData]:
        raise NotImplementedError

    @abc.abstractmethod
    def release_por(self):
        raise NotImplementedError

    @abc.abstractmethod
    def hold_por(self):
        raise NotImplementedError

    @abc.abstractmethod
    def por(self):
        raise NotImplementedError    
    
    @abc.abstractmethod
    def set_bootmode(self, mode: str):
        raise NotImplementedError

    @abc.abstractmethod
    def power_off(self):
        raise NotImplementedError

    @abc.abstractmethod
    def power_on(self):
        raise NotImplementedError

    @abc.abstractmethod
    def reset(self):
        raise NotImplementedError

    # @abc.abstractmethod
    # def enter_dfu(self):
    #     raise NotImplementedError
    
    # @abc.abstractmethod
    # def scan_i2c(self):
    #     raise NotImplementedError
    
    # @abc.abstractmethod
    # def probe_i2c(self):
    #     raise NotImplementedError

    # @abc.abstractmethod
    # def version(self):
    #     raise NotImplementedError


class PowerResetProtocol(abc.ABC):
        
    @abc.abstractmethod
    def reset(self):
        # TODO: there already is a reset protocol so we should consider that instead of defining here
        raise NotImplementedError 

    @abc.abstractmethod
    def por(self):
        raise NotImplementedError
    
    @abc.abstractmethod
    def hold_por(self):
        raise NotImplementedError
    
    @abc.abstractmethod
    def release_por(self):
        raise NotImplementedError

class SysbootRepository(abc.ABC):
    
    @abc.abstractmethod
    def get_sysboot_code_by_dut_type_and_mode(self, dut_type: str, mode: str) -> str:
        """
        Returns the target sysboot code for given platform and target mode
        i.e. am62xx-sk, mmc => 0243
        """
        raise NotImplementedError

class SysbootProtocol(abc.ABC):
    
    @abc.abstractmethod
    def set_bootmode(self, mode: str):
        """
        Responsible for setting the target bootmode on the device
        """
        raise NotImplementedError

class PowerMeterProtocol(abc.ABC):
    
    @abc.abstractmethod
    def measure_power(self, samples: int, delay: int) -> List[RailData]:
        raise NotImplementedError


class ConfigurationProtocol(abc.ABC):
    
    @abc.abstractmethod
    def set_dut(self, dut: str):
        raise NotImplementedError
