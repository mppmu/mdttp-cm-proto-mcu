# File: I2C_MCP9902.py
# Auth: M. Fras, Electronics Division, MPI for Physics, Munich
# Mod.: M. Fras, Electronics Division, MPI for Physics, Munich
# Date: 01 Aug 2022
# Rev.: 23 Jan 2023
#
# Python class for communicating with the MCP9902 low-temperature remote diode
# sensor IC.
#



import McuI2C
import I2CDevice



class I2C_MCP9902:

    # Message prefixes and separators.
    prefixDetails       = " - "
    separatorDetails    = " - "
    prefixDebug         = "DEBUG: {0:s}: ".format(__file__)
    prefixError         = "ERROR: {0:s}: ".format(__file__)

    # Debug configuration.
    debugLevel          = 0     # Debug verbosity.

    # Hardware parameters.
    hwAdrMin            = 0x00
    hwAdrMax            = 0xff



    # Initialize the I2C device.
    def __init__(self, mcuI2C, slaveAddr, deviceName):
        self.mcuI2C = mcuI2C
        self.slaveAddr = slaveAddr
        self.deviceName = deviceName
        self.i2cDevice = I2CDevice.I2CDevice(self.mcuI2C, self.slaveAddr, self.deviceName)
        self.i2cDevice.debugLevel = self.debugLevel
        self.prefixDebugDevice = self.prefixDebug + self.deviceName + ": "
        self.prefixErrorDevice = self.prefixError + self.deviceName + ": "



    # Check the register address value.
    def check_adr(self, regAdr):
        if regAdr < self.hwAdrMin or regAdr > self.hwAdrMax:
            print(self.prefixErrorDevice + "Pointer register value {0:d} out of valid range {1:d}..{2:d}!".\
                format(regAdr, self.hwAdrMin, self.hwAdrMax))
            return -1
        return 0



    # Return the name of a register address.
    @classmethod
    def adr_to_name(cls, regAdr):
        # Internal diode temperature.
        if regAdr == 0x00:
            regName = "integer value of the internal diode temperature"
        elif regAdr == 0x29:
            regName = "fractional portion of the internal diode temperature"
        # External diode temperature.
        elif regAdr == 0x01:
            regName = "integer value of the external diode temperature"
        elif regAdr == 0x10:
            regName = "fractional portion of the external diode temperature"
        # Status register.
        elif regAdr == 0x02:
            regName = "status register"
        # Configuration registers.
        elif regAdr == 0x03:
            regName = "configuration register 0"
        elif regAdr == 0x09:
            regName = "configuration register 1"
        # Temperature conversion rate register.
        elif regAdr == 0x04:
            regName = "temperature conversion rate register 0"
        elif regAdr == 0x0a:
            regName = "temperature conversion rate register 1"
        # Product ID.
        elif regAdr == 0xfd:
            regName = "product ID"
        # Manufacturer ID.
        elif regAdr == 0xfe:
            regName = "manufacturer ID"
        # Revision register.
        elif regAdr == 0xff:
            regName = "revision register"
        # Other registers.
        else:
            regName = "other/unknown"
        return regName



    # Read a register value.
    def read_reg(self, regAdr):
        self.i2cDevice.debugLevel = self.debugLevel
        if self.check_adr(regAdr):
            return -1, 0xff
        regName = self.adr_to_name(regAdr)
        # Debug info.
        if self.debugLevel >= 2:
            print(self.prefixDebugDevice + "Reading the value of the {0:s}, register address 0x{1:02x}.".format(regName, regAdr), end='')
            self.i2cDevice.print_details()
        # Assemble command to write.
        dataWr = []
        dataWr.append(regAdr)
        # Write command and read data with repeated start.
        ret, dataRd = self.i2cDevice.write_read(dataWr, 1)
        # Evaluate response.
        if ret:
            print(self.prefixErrorDevice + "Error reading the value of the {0:s}, register address 0x{1:02x}!".format(regName, regAdr), end='')
            self.i2cDevice.print_details()
            print(self.prefixErrorDevice + "Error code: {0:d}: ".format(ret))
            return -1, 0xff
        if len(dataRd) != 1:
            print(self.prefixErrorDevice + "Error reading the value of the {0:s}, register address 0x{1:02x}: Incorrect amount of data received!".\
                format(regName, regAdr), end='')
            self.i2cDevice.print_details()
            return -1, 0xff
        # Calculate the value.
        value = dataRd[0] & 0xff
        # Debug info.
        if self.debugLevel >= 2:
            print(self.prefixDebugDevice + "Read the value of the {0:s}, register address 0x{1:02x}: 0x{2:02x}.".format(regName, regAdr, value), end='')
            self.i2cDevice.print_details()
        return 0, value



    # Write a register value.
    def write_reg(self, regAdr, value):
        self.i2cDevice.debugLevel = self.debugLevel
        if self.check_adr(regAdr):
            return -1
        regName = self.adr_to_name(regAdr)
        value &= 0xff       # Limit to 8 bits.
        # Debug info.
        if self.debugLevel >= 2:
            print(self.prefixDebugDevice + "Writing 0x{0:02x} to the {1:s}, register address 0x{2:02x}.".format(value, regName, regAdr), end='')
            self.i2cDevice.print_details()
        # Assemble command and data to write.
        dataWr = []
        dataWr.append(regAdr)
        dataWr.append(value & 0xff)         # Data byte 0.
        # Write command and data.
        ret = self.i2cDevice.write(dataWr)
        # Evaluate response.
        if ret:
            print(self.prefixErrorDevice + "Error writing 0x{0:02x} to the {1:s}, register address 0x{2:02x}!".\
                format(value, regName, regAdr), end='')
            self.i2cDevice.print_details()
            print(self.prefixErrorDevice + "Error code: {0:d}: ".format(ret))
            return -1
        return 0



    # Convert a raw value to a temperature value.
    @classmethod
    def raw_to_temperature(cls, rawInt, rawFract):
        raw = ((rawInt & 0xff) << 3) | ((rawFract & 0xe0) >> 5)
        temperature = raw * 0.125
        return temperature



    # Convert a raw value to a temperature value for the extended range.
    @classmethod
    def raw_to_temperature_extended(cls, rawInt, rawFract):
        raw = ((rawInt & 0xff) << 3) | ((rawFract & 0xe0) >> 5)
        temperature = raw * 0.125 - 64
        return temperature



    # Read the internal diode temperature.
    def read_temp_int(self):
        retCfg, valueCfg = self.read_reg(0x03)  # Educated guess: The configuration register with address 0x03 is for the internal diode.
        if retCfg:
            return retCfg, -128.0
        retInt, valueInt = self.read_reg(0x00)
        retFract, valueFract = self.read_reg(0x29)
        # Check if the measurement range is default (0 .. 127 °C) or extended (-64 .. 191 °C).
        if valueCfg & 0x04:
            temperature = self.raw_to_temperature_extended(valueInt, valueFract)
        else:
            temperature = self.raw_to_temperature(valueInt, valueFract)
        return retInt | retFract, temperature



    # Read the external diode temperature.
    def read_temp_ext(self):
        retCfg, valueCfg = self.read_reg(0x09)  # Educated guess: The configuration register with address 0x09 is for external diodes.
        if retCfg:
            return retCfg, -128.0
        retInt, valueInt = self.read_reg(0x01)
        retFract, valueFract = self.read_reg(0x10)
        # Check if the measurement range is default (0 .. 127 °C) or extended (-64 .. 191 °C).
        if valueCfg & 0x04:
            temperature = self.raw_to_temperature_extended(valueInt, valueFract)
        else:
            temperature = self.raw_to_temperature(valueInt, valueFract)
        return retInt | retFract, temperature



    # Read the status register.
    def read_status(self):
        ret, value = self.read_reg(0x02)
        return ret, value



    # Read the configuration register 0.
    def read_config_0(self):
        ret, value = self.read_reg(0x03)
        return ret, value



    # Read the configuration register 1.
    def read_config_1(self):
        ret, value = self.read_reg(0x09)
        return ret, value



    # Read the temperature conversion rate register 0.
    def read_temp_conv_0(self):
        ret, value = self.read_reg(0x04)
        return ret, value



    # Read the temperature conversion rate register 1.
    def read_temp_conv_1(self):
        ret, value = self.read_reg(0x0a)
        return ret, value



    # Read the product ID.
    def read_product_id(self):
        ret, value = self.read_reg(0xfd)
        return ret, value



    # Read the manufacturer ID.
    def read_manufacturer_id(self):
        ret, value = self.read_reg(0xfe)
        return ret, value



    # Read the revision register.
    def read_revision(self):
        ret, value = self.read_reg(0xff)
        return ret, value



    # Write the configuration register 0.
    def write_config_0(self, value):
        ret = self.write_reg(0x03, value)
        return ret



    # Write the configuration register 1.
    def write_config_1(self, value):
        ret = self.write_reg(0x09, value)
        return ret



    # Write the temperature conversion rate register 0.
    def write_temp_conv_0(self, value):
        ret = self.write_reg(0x04, value)
        return ret



    # Write the temperature conversion rate register 1.
    def write_temp_conv_1(self, value):
        ret = self.write_reg(0x0a, value)
        return ret

