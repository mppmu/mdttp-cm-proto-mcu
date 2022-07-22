# File: I2C_PCA9545.py
# Auth: M. Fras, Electronics Division, MPI for Physics, Munich
# Mod.: M. Fras, Electronics Division, MPI for Physics, Munich
# Date: 22 Jul 2022
# Rev.: 22 Jul 2022
#
# Python class for communicating with the PCA9545 4-channel I2C-bus switch with
# interrupt logic and reset.
#



import I2CDevice



class I2C_PCA9545:

    # Message prefixes and separators.
    prefixDetails       = " - "
    separatorDetails    = " - "
    prefixDebug         = "DEBUG: {0:s}: ".format(__file__)
    prefixError         = "ERROR: {0:s}: ".format(__file__)

    # Debug configuration.
    debugLevel          = 0     # Debug verbosity.

    # Hardware parameters.
    hwChannelMin        = 0     # Lowest hardware channel number.
    hwChannelMax        = 3     # Highest hardware channel number.



    # Initialize the I2C device.
    def __init__(self, mcuI2C, slaveAddr, deviceName):
        self.mcuI2C = mcuI2C
        self.slaveAddr = slaveAddr
        self.deviceName = deviceName
        self.i2cDevice = I2CDevice.I2CDevice(self.mcuI2C, self.slaveAddr, self.deviceName)
        self.i2cDevice.debugLevel = self.debugLevel
        self.prefixDebugDevice = self.prefixDebug + self.deviceName + ": "
        self.prefixErrorDevice = self.prefixError + self.deviceName + ": "



    # Check the channel number.
    def check_channel_number(self, channel):
        if channel < self.hwChannelMin or channel > self.hwChannelMax:
            print(self.prefixErrorDevice + "Hardware channel number {0:d} out of valid range {1:d}..{2:d}!".\
                format(channel, self.hwChannelMin, self.hwChannelMax))
            return -1
        return 0



    # Set the multiplexer channel(s).
    def set_channels(self, channels):
        self.i2cDevice.debugLevel = self.debugLevel
        control_reg = 0x0
        for channel in channels:
            if self.check_channel_number(channel):
                return -1
            control_reg |= 0x1 << channel
        control_reg &= 0x0f
        # Debug info.
        if self.debugLevel >= 2:
            print(self.prefixDebugDevice + "Setting the control register to 0x{0:02x}.".format(control_reg), end='')
            self.i2cDevice.print_details()
        # Write data.
        ret = self.i2cDevice.write([control_reg])
        # Evaluate response.
        if ret:
            print(self.prefixErrorDevice + "Error setting the control register to 0x{0:02x}!".format(control_reg), end='')
            self.i2cDevice.print_details()
            print(self.prefixErrorDevice + "Error code: {0:d}: ".format(ret))
            return -1
        return 0



    # Disable the multiplexer.
    def disable(self):
        self.i2cDevice.debugLevel = self.debugLevel
        # Debug info.
        if self.debugLevel >= 2:
            print(self.prefixDebugDevice + "Disabling all channels.", end='')
            self.i2cDevice.print_details()
        # Write data.
        ret = self.i2cDevice.write([0x00])
        # Evaluate response.
        if ret:
            print(self.prefixErrorDevice + "Error disabling all channels!", end='')
            self.i2cDevice.print_details()
            print(self.prefixErrorDevice + "Error code: {0:d}: ".format(ret))
            return -1
        return 0



    # Get the current multiplexer channel(s).
    def get_channels(self):
        self.i2cDevice.debugLevel = self.debugLevel
        # Debug info.
        if self.debugLevel >= 2:
            print(self.prefixDebugDevice + "Reading the current multiplexer channels.", end='')
            self.i2cDevice.print_details()
        # Read the multiplexer control register.
        ret, data = self.i2cDevice.read(1)
        # Evaluate response.
        if ret or len(data) != 1:
            print(self.prefixErrorDevice + "Error reading the multiplexer channels!", end='')
            self.i2cDevice.print_details()
            if ret:
                print(self.prefixErrorDevice + "Reading of data returned error code {0:d}.".format(ret))
            return -1, []
        # Fill list with active channels.
        channels = []
        for i in range(self.hwChannelMin, self.hwChannelMax + 1):
            if data[0] & (0x01 << i):
                channels.append(i)
        return 0, channels



    # Get the current multiplexer interrupts.
    def get_interrups(self):
        self.i2cDevice.debugLevel = self.debugLevel
        # Debug info.
        if self.debugLevel >= 2:
            print(self.prefixDebugDevice + "Reading the current multiplexer interrupts.", end='')
            self.i2cDevice.print_details()
        # Read the multiplexer control register.
        ret, data = self.i2cDevice.read(1)
        # Evaluate response.
        if ret or len(data) != 1:
            print(self.prefixErrorDevice + "Error reading the multiplexer interrupts!", end='')
            self.i2cDevice.print_details()
            if ret:
                print(self.prefixErrorDevice + "Reading of data returned error code {0:d}.".format(ret))
            return -1, []
        # Fill list with active interrupts.
        interrupts = []
        for i in range(self.hwChannelMin, self.hwChannelMax + 1):
            if data[0] & (0x10 << i):
                interrupts.append(i)
        return 0, interrupts

