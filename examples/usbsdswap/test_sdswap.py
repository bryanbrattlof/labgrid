
def test_stick_plugin(target):
    sdmux = target.get_driver("USBSDSwapDriver")
    sdmux.set_mode("target")

    #TODO: assert the drive is active

    sdmux.set_mode("host")
