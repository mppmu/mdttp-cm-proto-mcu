# File: I2C_FireFly.py.py
# Auth: M. Fras, Electronics Division, MPI for Physics, Munich
# Mod.: M. Fras, Electronics Division, MPI for Physics, Munich
# Date: 10 Nov 2020
# Rev.: 10 Nov 2020
#
# Python class for communicating with a Samtec FireFly optical assembly.
#



import McuI2C
import I2CDevice



class I2C_FireFly:

    # Message prefixes and separators.
    prefixDetails       = " - "
    separatorDetails    = " - "
    prefixDebug         = "DEBUG: {0:s}: ".format(__file__)
    prefixError         = "ERROR: {0:s}: ".format(__file__)

    # Debug configuration.
    debugLevel          = 0     # Debug verbosity.

    # Hardware parameters.
    deviceTypeRX        = 'rx'
    deviceTypeTX        = 'tx'
    hwAdrMin            = 0x00
    hwAdrMax            = 0xff



    # Initialize the I2C device.
    def __init__(self, mcuI2C, slaveAddr, deviceName, deviceType):
        self.mcuI2C = mcuI2C
        self.slaveAddr = slaveAddr
        self.deviceName = deviceName
        if deviceType == self.deviceTypeRX:
            self.deviceType = self.deviceTypeRX
        else:
            self.deviceType = self.deviceTypeTX
        self.i2cDevice = I2CDevice.I2CDevice(self.mcuI2C, self.slaveAddr, self.deviceName)
        self.i2cDevice.debugLevel = self.debugLevel
        self.prefixDebugDevice = self.prefixDebug + self.deviceName + ": "
        self.prefixErrorDevice = self.prefixError + self.deviceName + ": "



    # Check the data word address value.
    def check_adr(self, regAdr):
        if regAdr < self.hwAdrMin or regAdr > self.hwAdrMax:
            print(self.prefixErrorDevice + "Data word register value {0:d} out of valid range {1:d}..{2:d}!".\
                format(regAdr, self.hwAdrMin, self.hwAdrMax))
            return -1
        return 0



    # Return the name of a register address.
    def adr_to_name(self, regAdr):
        regName = "*other/unknown*"
        if self.deviceType == self.deviceTypeRX:
            if regAdr == 2:
                regName = "Status"
            elif regAdr == 6:
                regName = "Status Summaries"
            elif regAdr >= 7 and regAdr <= 8:
                regName = "Latched LOS Alarms"
            elif regAdr >= 14 and regAdr <= 16:
                regName = "Latched RX Power Alarms"
            elif regAdr == 17:
                regName = "Latched Alarms- Temperature"
            elif regAdr == 18:
                regName = "Latched Alarms- Vcc3.3"
            elif regAdr >= 20 and regAdr <= 21:
                regName = "Latched CDR LOL Alarms"
            elif regAdr == 22:
                regName = "Internal Temperature Monitor"
            elif regAdr >= 26 and regAdr <= 27:
                regName = "Vcc Monitor"
            elif regAdr >= 38 and regAdr <= 39:
                regName = "Elapsed Operating Time"
            elif regAdr == 51:
                regName = "Reset"
            elif regAdr >= 52 and regAdr <= 53:
                regName = "Channel Disable"
            elif regAdr >= 54 and regAdr <= 55:
                regName = "Output Disable"
            elif regAdr >= 58 and regAdr <= 59:
                regName = "Rx Polarity Invert"
            elif regAdr >= 62 and regAdr <= 67:
                regName = "Output Amplitude"
            elif regAdr >= 68 and regAdr <= 73:
                regName = "De-emphasis"
            elif regAdr >= 74 and regAdr <= 75:
                regName = "CDR Enable"
            elif regAdr >= 95 and regAdr <= 96:
                regName = "Mask LOS Flags"
            elif regAdr >= 102 and regAdr <= 104:
                regName = "Mask RX Power Alarms"
            elif regAdr ==  105:
                regName = "Mask Temperature Alarms"
            elif regAdr ==  106:
                regName = "Mask Vcc3.3 Alarms"
            elif regAdr >= 108 and regAdr <= 109:
                regName = "Mask CDR LOL Alarms"
            elif regAdr >= 111 and regAdr <= 114:
                regName = "Firmware Version"
            elif regAdr ==  127:
                regName = "Page Select Byte"
        else:
            if regAdr == 2:
                regName = "Status"
            elif regAdr == 6:
                regName = "Status Summaries"
            elif regAdr >= 7 and regAdr <= 8:
                regName = "Latched TX LOS Alarms"
            elif regAdr >= 9 and regAdr <= 10:
                regName = "Latched Alarm – Laser Fault"
            elif regAdr == 17:
                regName = "Latched Alarms- Temperature"
            elif regAdr == 18:
                regName = "Latched Alarms- Vcc3.3"
            elif regAdr >= 20 and regAdr <= 21:
                regName = "Latched CDR LOL Alarms"
            elif regAdr == 22:
                regName = "Internal Temperature Monitor"
            elif regAdr >= 26 and regAdr <= 27:
                regName = "Vcc Monitor"
            elif regAdr >= 38 and regAdr <= 39:
                regName = "Elapsed Operating Time"
            elif regAdr == 51:
                regName = "Reset"
            elif regAdr >= 52 and regAdr <= 53:
                regName = "Transmit Channel Disable"
            elif regAdr >= 54 and regAdr <= 55:
                regName = "Transmit Output Disable"
            elif regAdr >= 56 and regAdr <= 57:
                regName = "Transmit Squelch Disable"
            elif regAdr >= 58 and regAdr <= 59:
                regName = "Transmit Polarity Invert"
            elif regAdr >= 62 and regAdr <= 67:
                regName = "Transmit Input Equalization"
            elif regAdr >= 74 and regAdr <= 75:
                regName = "CDR Enable"
            elif regAdr >= 95 and regAdr <= 96:
                regName = "Mask TX LOS Alarms"
            elif regAdr >= 97 and regAdr <= 98:
                regName = "Mask Fault Flags"
            elif regAdr ==  105:
                regName = "Mask Temperature Alarms"
            elif regAdr ==  106:
                regName = "Mask Vcc3.3 Alarms"
            elif regAdr >= 108 and regAdr <= 109:
                regName = "Mask CDR LOL Alarms"
            elif regAdr >= 111 and regAdr <= 114:
                regName = "Firmware Version"
            elif regAdr ==  127:
                regName = "Page Select Byte"
        return regName



    # Read a register value.
    def read_reg(self, regAdr):
        self.i2cDevice.debugLevel = self.debugLevel
        if self.check_adr(regAdr):
            return -1, 0xff
        regName = self.adr_to_name(regAdr)
        # Debug info.
        if self.debugLevel >= 2:
            print(self.prefixDebugDevice + "Reading the value of the \"{0:s}\", register address 0x{1:02x}.".format(regName, regAdr), end='')
            self.i2cDevice.print_details()
        # Assemble command to write.
        dataWr = []
        dataWr.append(regAdr)
        # Write command and read data with repeated start.
        ret, dataRd = self.i2cDevice.write_read(dataWr, 1)
        # Evaluate response.
        if ret:
            print(self.prefixErrorDevice + "Error reading the value of the \"{0:s}\", register address 0x{1:02x}!".format(regName, regAdr), end='')
            self.i2cDevice.print_details()
            print(self.prefixErrorDevice + "Error code: {0:d}: ".format(ret))
            return -1, 0xff
        if len(dataRd) != 1:
            print(self.prefixErrorDevice + "Error reading the value of the \"{0:s}\", register address 0x{1:02x}: Incorrect amount of data received!".\
                format(regName, regAdr), end='')
            self.i2cDevice.print_details()
            return -1, 0xff
        # Calculate the value.
        value = dataRd[0] & 0xff
        # Debug info.
        if self.debugLevel >= 2:
            print(self.prefixDebugDevice + "Read the value of the \"{0:s}\", register address 0x{1:02x}: 0x{2:02x}.".format(regName, regAdr, value), end='')
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
            print(self.prefixDebugDevice + "Writing 0x{0:02x} to the \"{1:s}\" register, register address 0x{2:02x}.".format(value, regName, regAdr), end='')
            self.i2cDevice.print_details()
        # Assemble command and data to write.
        dataWr = []
        dataWr.append(regAdr)
        dataWr.append(value & 0xff)         # Data byte 0.
        # Write command and data.
        ret = self.i2cDevice.write(dataWr)
        # Evaluate response.
        if ret:
            print(self.prefixErrorDevice + "Error writing 0x{0:02x} to the \"{1:s}\" register, register address 0x{2:02x}!".\
                format(value, regName, regAdr), end='')
            self.i2cDevice.print_details()
            print(self.prefixErrorDevice + "Error code: {0:d}: ".format(ret))
            return -1
        return 0



    # Read a register range as integer.
    def read_reg_range_int(self, regAdrStart, regAdrEnd):
        if regAdrStart > regAdrEnd:
            print(self.prefixErrorDevice + "Error reading register range: Start address {0:d} larger than end address {1:d}!".\
                format(regAdrStart, regAdrEnd))
            return -1, -1
        ret = 0
        value = 0
        for i in range(regAdrStart, regAdrEnd + 1):
            retTmp, valueTmp = self.read_reg(i)
            ret |= retTmp
            value |= (valueTmp & 0xff) << (8 * (regAdrEnd - i))
        return ret, value



    # Read a register range as string.
    def read_reg_range_str(self, regAdrStart, regAdrEnd):
        if regAdrStart > regAdrEnd:
            print(self.prefixErrorDevice + "Error reading register range: Start address {0:d} larger than end address {1:d}!".\
                format(regAdrStart, regAdrEnd))
            return -1, ""
        ret = 0
        string = ""
        for i in range(regAdrStart, regAdrEnd + 1):
            retTmp, valueTmp = self.read_reg(i)
            ret |= retTmp
            string += chr(valueTmp)
        return ret, string



    # Read device temperature.
    def read_temperature(self):
        ret, temperatureTmp = self.read_reg(22)
        # Convert to signed value.
        temperature = temperatureTmp - 256 * (temperatureTmp > 128)
        return ret, temperature



    # Read device supply voltage.
    def read_vcc(self):
        ret, vcc = self.read_reg_range_int(26, 27)
        # Calculate value in volts.
        vcc = vcc * 0.0001
        return ret, vcc



    # Read device elapsed operating time in hours.
    def read_operating_time(self):
        ret, operatingTime = self.read_reg_range_int(38, 39)
        # Calculate value in hours.
        operatingTime = deviceOperatingTime * 2
        return ret, operatingTime



    # Read device firmware version.
    def read_firmware_version(self):
        ret, firmwareVersionTmp = self.read_reg_range_int(111, 114)
        firmwareVersion = "{0:d}.{1:d}.{2:d}.{3:d}".format(
            (firmwareVersionTmp >> 24) & 0xff,
            (firmwareVersionTmp >> 16) & 0xff,
            (firmwareVersionTmp >>  8) & 0xff,
            (firmwareVersionTmp >>  0) & 0xff)
        return ret, firmwareVersion



    # Read vendor name.
    def read_vendor_name(self):
        # Set the page select byte.
        self.write_reg(127, 0x00)
        ret, vendorName = self.read_reg_range_str(152, 161)
        return ret, vendorName



    # Read vendor part number.
    def read_vendor_part_number(self):
        # Set the page select byte.
        self.write_reg(127, 0x00)
        ret, vendorPartNumber = self.read_reg_range_str(171, 186)
        return ret, vendorPartNumber



    # Read vendor serial number.
    def read_vendor_serial_number(self):
        # Set the page select byte.
        self.write_reg(127, 0x00)
        ret, vendorSerialNumber = self.read_reg_range_str(189, 198)
        return ret, vendorSerialNumber



    # Read device time at temperature.
    def read_time_at_temperature(self, temperaturSlot):
        # Set the page select byte.
        self.write_reg(127, 0x0b)
        ret, timeAtTemperatureTmp = self.read_reg_range_int(128 + (3 * temperaturSlot), 130 + (3 * temperaturSlot))
        # Convert to hours.
        timeAtTemperature = timeAtTemperatureTmp * 5 / 60
        return ret, timeAtTemperature



    # Read device information.
    def read_device_info(self):
        # Temperature.
        ret, deviceTemperature = relf.read_temperature()
        return ret, deviceTemperature

