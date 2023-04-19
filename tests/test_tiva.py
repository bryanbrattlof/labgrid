import pytest
from labgrid.binding import BindingState
from labgrid.driver.common import Driver
from labgrid.driver.fake import FakeConfigDriver, FakePowerDriver, FakePowerMeterDriver, FakeResetDriver, FakeSysbootDriver
from labgrid.driver import TAIDriver, extract_rail_data
from labgrid.protocol import PowerProtocol, ConsoleProtocol, RailData, PowerResetProtocol, SysbootProtocol, PowerMeterProtocol, ConfigurationProtocol

@pytest.fixture
def fake_rail_data():
    """For future test requiring dummy power measurements"""
    return [
        RailData(index=0, rail_name='vdd_mcu_0v85', shunt_voltage=4707.5, rail_voltage=0.85125, current=470.4, power=412.5),
        RailData(index=1, rail_name='vdd_mcu_ram_0v85', shunt_voltage=56.0, rail_voltage=0.85625, current=5.5, power=0.0),
        RailData(index=2, rail_name='vda_mcu_1v8', shunt_voltage=179.0, rail_voltage=1.79925, current=17.8, power=37.5),
        RailData(index=3, rail_name='vdd_mcuio_3v3', shunt_voltage=140.5, rail_voltage=3.28575, current=13.9, power=37.5)
    ]

def test_extract_rail_data():
    """
    TODO: need to verify the test data will be same i.e. we can supply this as a utf-8 string or as raw bytes
          It depends on what labgrid drivers supply us by default. We can decode bytes if necessary, but this test doesn't do that integration
    """
    input_string = '| Index | Rail Name | Shunt voltage(uV) | Rail voltage(V) | Current(mA) | Power(mW) |\n| 0 | vdd_mcu_0v85 | 4707.50 | 0.851250 | 470.40 | 412.50 |\n| 1 | vdd_mcu_ram_0v85 | 56.00 | 0.856250 | 5.50 | 0.00 |\n| 2 | vda_mcu_1v8 | 179.00 | 1.799250 | 17.80 | 37.50 |\n| 3 | vdd_mcuio_3v3 | 140.50 | 3.285750 | 13.90 | 37.50 |\n'
    expected_output = [
        RailData(index=0, rail_name='vdd_mcu_0v85', shunt_voltage=4707.5, rail_voltage=0.85125, current=470.4, power=412.5),
        RailData(index=1, rail_name='vdd_mcu_ram_0v85', shunt_voltage=56.0, rail_voltage=0.85625, current=5.5, power=0.0),
        RailData(index=2, rail_name='vda_mcu_1v8', shunt_voltage=179.0, rail_voltage=1.79925, current=17.8, power=37.5),
        RailData(index=3, rail_name='vdd_mcuio_3v3', shunt_voltage=140.5, rail_voltage=3.28575, current=13.9, power=37.5)
    ]
    expected_total_power = 487.5
    expected_average_power = 121.875
    measurements = extract_rail_data(input_string)
    total_power = sum(map(lambda x: x.power, measurements))
    average_power = total_power / len(measurements)
    assert measurements == expected_output      # expected data objects
    assert expected_total_power == total_power
    assert average_power == expected_average_power

def test_dummy_tai(target_with_fakeconsole, mocker):
    # pytest.set_trace() -- uncomment to use pdb
    power = FakePowerDriver(target_with_fakeconsole, "power_handle")
    config = FakeConfigDriver(target_with_fakeconsole, "config_handle")
    meter = FakePowerMeterDriver(target_with_fakeconsole, "power_meter_handle")
    por = FakeResetDriver(target_with_fakeconsole, "por_handle")
    sysboot = FakeSysbootDriver(target_with_fakeconsole, "sysboot_handle")
    tai=TAIDriver(target_with_fakeconsole, "tai_handle")
    
    # this step not necessary if not using @Driver.check_active decorator
    tai_driver = target_with_fakeconsole.get_driver("TAIProtocol")
    target_with_fakeconsole.activate(tai_driver)
    
    # apply mock patches
    reset_mock=mocker.patch('labgrid.driver.fake.FakeResetDriver.reset')
    por_mock=mocker.patch('labgrid.driver.fake.FakeResetDriver.por')
    hold_por_mock=mocker.patch('labgrid.driver.fake.FakeResetDriver.hold_por')
    release_por_mock=mocker.patch('labgrid.driver.fake.FakeResetDriver.release_por')
    config_mock=mocker.patch('labgrid.driver.fake.FakeConfigDriver.set_dut')
    meter_mock=mocker.patch('labgrid.driver.fake.FakePowerMeterDriver.measure_power')
    sys_mock=mocker.patch('labgrid.driver.fake.FakeSysbootDriver.set_bootmode')
    power_on_mock=mocker.patch('labgrid.driver.fake.FakePowerDriver.on')
    power_off_mock=mocker.patch('labgrid.driver.fake.FakePowerDriver.off')
    
    # call the functions
    # TODO: add all functions on TAI
    tai_driver.reset()
    tai_driver.por()
    tai_driver.hold_por()
    tai_driver.release_por()
    tai_driver.set_dut("abcd")
    tai_driver.set_bootmode("0243")
    tai_driver.measure_power(5,5)
    tai_driver.power_on()
    tai_driver.power_off()
    
    # assertions - check that each underlying driver was called and with correct data
    power_on_mock.assert_called_once()
    power_off_mock.assert_called_once()
    config_mock.assert_called_once_with("abcd")
    meter_mock.assert_called_once_with(5,5)
    reset_mock.assert_called_once()
    sys_mock.assert_called_once_with("0243")
    por_mock.assert_called_once()
    hold_por_mock.assert_called_once()
    release_por_mock.assert_called_once()
    
    

