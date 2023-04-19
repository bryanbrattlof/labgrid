import pytest
import warnings

from labgrid import Environment
from labgrid.exceptions import NoConfigFoundError, InvalidConfigError
from labgrid.protocol import ConsoleProtocol
from labgrid.resource import RawSerialPort


class TestEnvironment:
    def test_noconfig_instance(self):
        with pytest.raises(NoConfigFoundError):
            e = Environment()

    def test_instance(self, tmpdir):
        p = tmpdir.join("config.yaml")
        p.write(
            """
        targets:
          test1:
            drivers: {}
          test2:
            role: foo
            resources: {}
        """
        )
        e = Environment(str(p))
        assert (isinstance(e, Environment))

    def test_get_target(self, tmpdir):
        p = tmpdir.join("config.yaml")
        p.write(
            """
        targets:
          test1:
            drivers: {}
          test2:
            role: foo
            resources: {}
        """
        )
        e = Environment(str(p))
        assert (e.get_target("test1"))
        assert (e.get_target("test2"))

    def test_instance_invalid_yaml(self, tmpdir):
        p = tmpdir.join("config.yaml")
        p.write(
            """
        I a(m) no yaml:
          - keks
          cookie
        """
        )
        with pytest.raises(InvalidConfigError):
            e = Environment(str(p))

    def test_env_imports_yaml(self, tmpdir):
        import sys
        i = tmpdir.join("myimport.py")
        i.write(
"""
class Test:
    pass
"""
        )
        p = tmpdir.join("config.yaml")
        p.write(
    f"""
targets:
  main:
    drivers: {{}}
imports:
  - {str(i)}
"""
        )
        e = Environment(str(p))
        assert (isinstance(e, Environment))
        assert "myimport" in sys.modules
        import myimport
        t = myimport.Test()
        assert (isinstance(t, myimport.Test))

    def test_create_named_resources(self, tmpdir):
        p = tmpdir.join("config.yaml")
        p.write(
            """
        targets:
          test1:
            resources:
            - AndroidUSBFastboot:
                name: "fastboot"
                match: {}
            - RawSerialPort:
                port: "/dev/ttyUSB0"
                speed: 115200
        """
        )
        e = Environment(str(p))
        t = e.get_target("test1")

    def test_create_named_drivers(self, tmpdir):
        p = tmpdir.join("config.yaml")
        p.write(
            """
        targets:
          test1:
            resources:
            - AndroidUSBFastboot:
                name: "fastboot"
                match: {}
            - RawSerialPort:
                name: "serial_a"
                port: "/dev/ttyUSB0"
                speed: 115200
            - cls: RawSerialPort
              name: "serial_b"
              port: "/dev/ttyUSB0"
              speed: 115200
            drivers:
            - FakeConsoleDriver:
                name: "serial_a"
            - FakeConsoleDriver:
                name: "serial_b"
        """
        )
        e = Environment(str(p))
        t = e.get_target("test1")

    def test_create_multi_drivers(self, tmpdir):
        p = tmpdir.join("config.yaml")
        p.write(
            """
        targets:
          test1:
            resources:
            - RawSerialPort:
                name: "serial_a"
                port: "/dev/ttyUSB0"
                speed: 115200
            - RawSerialPort:
                name: "serial_b"
                port: "/dev/ttyUSB0"
                speed: 115200
            drivers:
            - SerialDriver:
                name: "serial_a"
                bindings:
                  port: "serial_a"
            - SerialDriver:
                name: "serial_b"
                bindings:
                  port: "serial_b"
        """
        )
        e = Environment(str(p))
        t = e.get_target("test1")
        r_a = t.get_resource(RawSerialPort, name="serial_a")
        r_b = t.get_resource(RawSerialPort, name="serial_b")
        assert r_a is not r_b
        d_a = t.get_driver(ConsoleProtocol, name="serial_a", activate=False)
        d_b = t.get_driver(ConsoleProtocol, name="serial_b", activate=False)
        assert d_a is not d_b

        assert d_a.port is r_a
        assert d_b.port is r_b

    def test_usbserialport_warning(self, tmpdir):
        p = tmpdir.join("config.yaml")
        p.write(
            """
        targets:
          test1:
            resources:
            - USBSerialPort:
                port: /dev/ttyS0
            drivers:
            - SerialDriver: {}
        """
        )
        e = Environment(str(p))
        with pytest.warns(UserWarning):
            t = e.get_target("test1")

    def test_usbserialport_no_warning(self, tmpdir):
        p = tmpdir.join("config.yaml")
        p.write(
            """
        targets:
          test1:
            resources:
            - USBSerialPort: {}
            drivers:
            - SerialDriver: {}
        """
        )
        e = Environment(str(p))
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            t = e.get_target("test1")

    def test_tiva(self, tmpdir):
        p = tmpdir.join("config.yaml")
        p.write("""
targets:
  main:
    drivers:
      FakeConsoleDriver:
        name: 'TivaSerial'
      FakePowerDriver: 
        name: 'FakePowerDriver'
        bindings: { console: 'TivaSerial' }
      FakeResetDriver: 
        name: 'FakePorDriver'
        bindings: { console: 'TivaSerial' }        
      FakeSysbootDriver: 
        name: 'FakeSysbootDriver'
        bindings: { console: 'TivaSerial' }
      FakeConfigDriver: 
        name: 'FakeConfigDriver'
        bindings: { console: 'TivaSerial' }
      FakePowerMeterDriver: 
        name: 'FakePowerMeterDriver'
        bindings: { console: 'TivaSerial' }
      TAIDriver:
        name: "BoardAutomation"
        bindings: {
          power_meter_handle: 'FakePowerMeterDriver',
          por_handle: 'FakePorDriver',
          power_handle: 'FakePowerDriver',
          sysboot_handle: 'FakeSysbootDriver',
          config_handle: 'FakeConfigDriver',}""")
        e = Environment(str(p))
        target=e.get_target()
        for driver in target.drivers:
            print(driver) # for debug, pass -s to pytest
        automation_handle=target.get_driver('TAIProtocol')
        assert(automation_handle is not None)
