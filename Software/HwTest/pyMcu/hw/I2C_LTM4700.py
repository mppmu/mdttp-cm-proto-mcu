# File: I2C_LTM4700.py
# Auth: M. Fras, Electronics Division, MPI for Physics, Munich
# Mod.: M. Fras, Electronics Division, MPI for Physics, Munich
# Date: 28 Apr 2021
# Rev.: 28 Apr 2021
#
# Python class for communicating with the LTM4700 dual 50A or single 100A
# uModule regulator with digital power system management IC.
#
# Hints:
# - See datasheet "ltm4700.pdf" for details.
#



import McuI2C
import I2CDevice



class I2C_LTM4700:

    # Message prefixes and separators.
    prefixDetails       = " - "
    separatorDetails    = " - "
    prefixDebug         = "DEBUG: {0:s}: ".format(__file__)
    prefixError         = "ERROR: {0:s}: ".format(__file__)

    # Debug configuration.
    debugLevel          = 0     # Debug verbosity.

    # Hardware parameters.
    hwCmdCodePage           = 0x00  # Command code for channel/page number.
    hwCmdCodeOperation      = 0x01
    hwCmdCodeOnOffConfig    = 0x02
    hwCmdCodeClearFaults    = 0x03
    hwCmdCodeWriteProtect   = 0x10
    hwCmdCodeReadVin        = 0x88
    hwCmdCodeReadIin        = 0x89
    hwCmdCodeReadVout       = 0x8b
    hwCmdCodeReadIout       = 0x8c
    hwCmdCodeReadTempExt    = 0x8d
    hwCmdCodeReadTempInt    = 0x8e
    hwCmdCodeMfrConfigChan  = 0xd0
    hwDataLenMin            = 1
    hwDataLenMax            = 2
    hwPageMin               = 0     # Lowest hardware channel/page number.
    hwPageMax               = 1     # Highest hardware channel/page number.
    hwPage                  = 0     # Current hardware channel/page number.
    hwChannels              = 2



    # Initialize the I2C device.
    def __init__(self, mcuI2C, slaveAddr, deviceName):
        self.mcuI2C = mcuI2C
        self.slaveAddr = slaveAddr
        self.deviceName = deviceName
        self.i2cDevice = I2CDevice.I2CDevice(self.mcuI2C, self.slaveAddr, self.deviceName)
        self.i2cDevice.debugLevel = self.debugLevel
        self.prefixDebugDevice = self.prefixDebug + self.deviceName + ": "
        self.prefixErrorDevice = self.prefixError + self.deviceName + ": "
        self.errorCount = 0



    # Return the name of a command code.
    @classmethod
    def cmd_to_name(cls, cmdCode):
        if cmdCode == cls.hwCmdCodePage:
            cmdName = "PAGE"
        elif cmdCode == cls.hwCmdCodeOperation:
            cmdName = "OPERATION"
        elif cmdCode == cls.hwCmdCodeOnOffConfig:
            cmdName = "ON_OFF_CONFIG"
        elif cmdCode == cls.hwCmdCodeClearFaults:
            cmdName = "CLEAR_FAULTS"
        elif cmdCode == cls.hwCmdCodeWriteProtect:
            cmdName = "WRITE_PROTECT"
        elif cmdCode == cls.hwCmdCodeReadVin:
            cmdName = "READ_VIN"
        elif cmdCode == cls.hwCmdCodeReadIin:
            cmdName = "READ_IIN"
        elif cmdCode == cls.hwCmdCodeReadVout:
            cmdName = "READ_VOUT"
        elif cmdCode == cls.hwCmdCodeReadIout:
            cmdName = "READ_IOUT"
        elif cmdCode == cls.hwCmdCodeReadTempExt:
            cmdName = "READ_TEMPERATURE_1"
        elif cmdCode == cls.hwCmdCodeReadTempInt:
            cmdName = "READ_TEMPERATURE_2"
        elif cmdCode == cls.hwCmdCodeMfrConfigChan:
            cmdName = "MFR_CHAN_CONFIG"
        elif cmdCode <= 0xfd:
            cmdName = "unknown"
        else:
            cmdName = "*reserved*"
        return cmdName



    # Check the data length.
    def check_data_len(self, dataLen):
        if dataLen < self.hwDataLenMin or dataLen > self.hwDataLenMax:
            print(self.prefixErrorDevice + "Data length {0:d} out of valid range {1:d}..{2:d}!".\
                format(dataLen, self.hwDataLenMin, self.hwDataLenMax))
            return -1
        return 0



    # Check the page number.
    def check_page_number(self, page):
        if (page < self.hwPageMin or page > self.hwPageMax) and page != 0xff:
            print(self.prefixErrorDevice + "Hardware page number {0:d} out of valid range {1:d}..{2:d}!".\
                format(page, self.hwPageMin, self.hwPageMax))
            return -1
        return 0



    # Read command data.
    def read(self, cmdCode, dataLen):
        self.i2cDevice.debugLevel = self.debugLevel
        cmdCode &= 0xff
        cmdName = self.cmd_to_name(cmdCode)
        if self.check_data_len(dataLen):
            self.errorCount += 1
            return -1
        # Debug info.
        if self.debugLevel >= 2:
            print(self.prefixDebugDevice + "Reading the command 0x{0:02x} ({1:s}) data.".format(cmdCode, cmdName), end='')
            self.i2cDevice.print_details()
        # Assemble command to write.
        dataWr = []
        dataWr.append(cmdCode)
        # Write command and read data with repeated start.
        ret, dataRd = self.i2cDevice.write_read(dataWr, dataLen)
        # Evaluate response.
        if ret:
            self.errorCount += 1
            print(self.prefixErrorDevice + "Error reading the command 0x{0:02x} ({1:s}) data!".format(cmdCode, cmdName), end='')
            self.i2cDevice.print_details()
            print(self.prefixErrorDevice + "Error code: {0:d}: ".format(ret))
            return -1, 0xff
        if not dataRd:
            self.errorCount += 1
            print(self.prefixErrorDevice + "Error reading the command 0x{0:02x} ({1:s}) data: No data received!".format(cmdCode, cmdName), end='')
            self.i2cDevice.print_details()
            return -1, 0xff
        # Debug info.
        if self.debugLevel >= 2:
            print(self.prefixDebugDevice + "Read the command 0x{0:02x} ({1:s}) data: ".format(cmdCode, cmdName), end='')
            for datum in dataRd:
                print("0x{0:02x} ".format(datum), end='')
            self.i2cDevice.print_details()
        return 0, dataRd



    # Write command data.
    def write(self, cmdCode, data):
        self.i2cDevice.debugLevel = self.debugLevel
        cmdCode &= 0xff
        cmdName = self.cmd_to_name(cmdCode)
        if self.check_data_len(len(data)):
            self.errorCount += 1
            return -1
        # Debug info.
        if self.debugLevel >= 2:
            print(self.prefixDebugDevice + "Writing command 0x{0:02x} ({1:s}) data: ".format(cmdCode, cmdName), end='')
            for datum in data:
                print("0x{0:02x} ".format(datum & 0xff), end='')
            self.i2cDevice.print_details()
        # In case of "page" command, check the page number and update the page number variable.
        if cmdCode == self.hwCmdCodePage:
            if self.check_page_number(data[0]):
                self.errorCount += 1
                return -1
            self.hwPage = data[0]
        # Assemble command and data to write.
        dataWr = []
        dataWr.append(cmdCode)
        for datum in data:
            dataWr.append(datum & 0xff)
        # Write command and data.
        ret = self.i2cDevice.write(dataWr)
        # Evaluate response.
        if ret:
            print(self.prefixErrorDevice + "Error writing command 0x{0:02x} ({1:s}) data!".format(cmdCode, cmdName), end='')
            self.i2cDevice.print_details()
            print(self.prefixErrorDevice + "Error code: {0:d}: ".format(ret))
            return -1
        return 0



    # Set the channel/page numer.
    def set_page(self, page):
        if self.check_page_number(page):
            self.errorCount += 1
            return -1
        self.hwPage = page
        self.write(self.hwCmdCodePage, [page])
        return 0



    # Get the channel/page numer.
    def get_page(self):
        ret, data = self.read(self.hwCmdCodePage, 1)
        if ret:
            self.errorCount += 1
            print(self.prefixErrorDevice + "Error reading the page number. Error code: 0x{0:02x}: ".format(ret))
            return -1, 0xff
        if self.check_page_number(page):
            self.errorCount += 1
            return -1, 0xff
        page = data[0]
        self.hwPage = page
        return 0, page



    # Calculate a float value from an L11 (Linear_5s_11s) value.
    def l11_to_float(self, b):
        # PMBus data field b[15:0]
        # Value = Y * 2**N
        # where N = b[15:11] is a 5-bit two’s complement integer
        #   and Y = b[10:0] is an 11-bit two’s complement integer.
        n = (b >> 11) & 0x1f
        if n & 0x10:
            n = -((~n & 0xf) + 1)
        y = b & 0x7ff
        if y & 0x400:
            y = -((~y & 0x3ff) + 1)
        return float(y * 2**n)



    # Calculate a float value from an L16 (Linear_16u) value.
    def l16_to_float(self, b):
        # PMBus data field b[15:0]
        # Value = Y * 2**N
        # where Y = b[15:0] is an unsigned integer
        #   and N = Vout_mode_parameter is a 5-bit two’s complement exponent that is hardwired to –13 decimal.
        y = b & 0xffff
        return float(y * 2**(-12))



    # Read the write protection status.
    def read_wp(self):
        ret, data = self.read(self.hwCmdCodeWriteProtect, 1)
        if ret:
            return -1, 0xff
        return 0, data[0]



    # Clear the write protection.
    def wp_clear(self):
        return self.write(self.hwCmdCodeWriteProtect, [0x00])



    # Set the write protection to level 1:
    # Disable all writes except to the WRITE_PROTECT, PAGE, MFR_EE_UNLOCK, and
    # STORE_USER_ALL commands.
    def wp_level_1(self):
        return self.write(self.hwCmdCodeWriteProtect, [0x80])



    # Set the write protection to level 2:
    # Disable all writes except to the WRITE_PROTECT, PAGE, MFR_EE_UNLOCK,
    # MFR_CLEAR_PEAKS, STORE_USER_ALL, OPERATION and CLEAR_FAULTS command.
    def wp_level_2(self):
        return self.write(self.hwCmdCodeWriteProtect, [0x40])



    # Set the write protection to level 3:
    # Disable all writes except to the WRITE_PROTECT, OPERATION, MFR_EE_UNLOCK,
    # MFR_CLEAR_PEAKS, CLEAR_FAULTS, PAGE, ON_OFF_CONFIG, VOUT_COMMAND and
    # STORE_USER_ALL.
    def wp_level_2(self):
        return self.write(self.hwCmdCodeWriteProtect, [0x20])



    # Switch off all power channles simultaneously.
    def power_off_all(self):
        # Save the current write protection level.
        ret, wpSave = self.read_wp()
        # Set the write protection level to 2.
        ret |= self.wp_level_2()
        # Write to all channels simultaneously.
        ret |= self.write(self.hwCmdCodePage, [0xff])
        # Configure the on/off behavior.
        ret |= self.write(self.hwCmdCodeOnOffConfig, [0x1e])
        # Switch on all channels.
        ret |= self.write(self.hwCmdCodeOperation, [0x00])
        # Restore the original write protection level.
        ret |= self.write(self.hwCmdCodeWriteProtect, [wpSave])
        return ret



    # Switch on all power channles simultaneously.
    def power_on_all(self):
        # Save the current write protection level.
        ret, wpSave = self.read_wp()
        # Set the write protection level to 2.
        ret |= self.wp_level_2()
        # Write to all channels simultaneously.
        ret |= self.write(self.hwCmdCodePage, [0xff])
        # Configure the on/off behavior.
        ret |= self.write(self.hwCmdCodeOnOffConfig, [0x1e])
        # Switch on all channels.
        ret |= self.write(self.hwCmdCodeOperation, [0x80])
        # Restore the original write protection level.
        ret |= self.write(self.hwCmdCodeWriteProtect, [wpSave])
        return ret



    # Read the measured input supply voltage.
    def read_vin(self):
        ret, data = self.read(self.hwCmdCodeReadVin, 2)
        if ret:
            self.errorCount += 1
            print(self.prefixErrorDevice + "Error reading the input supply voltage. Error code: 0x{0:02x}: ".format(ret))
            return -1, float(-1)
        vinRaw = (data[1] << 8) + data[0]
        return 0, self.l11_to_float(vinRaw)



    # Read the measured input supply current.
    def read_iin(self):
        ret, data = self.read(self.hwCmdCodeReadIin, 2)
        if ret:
            self.errorCount += 1
            print(self.prefixErrorDevice + "Error reading the input supply current. Error code: 0x{0:02x}: ".format(ret))
            return -1, float(-1)
        iinRaw = (data[1] << 8) + data[0]
        return 0, self.l11_to_float(iinRaw)



    # Read the measured output voltage.
    def read_vout(self, channel):
        if self.set_page(channel):
            self.errorCount += 1
            return -1, float(-1)
        # Read the VOUT value.
        ret, data = self.read(self.hwCmdCodeReadVout, 2)
        if ret:
            self.errorCount += 1
            print(self.prefixErrorDevice + "Error reading the output voltage of channel {0:d}. Error code: 0x{0:02x}: ".format(channel, ret))
            return -1, float(-1)
        voutRaw = (data[1] << 8) + data[0]
        return 0, self.l16_to_float(voutRaw)



    # Read the average output current in amperes.
    def read_iout(self, channel):
        if self.set_page(channel):
            self.errorCount += 1
            return -1, float(-1)
        # Read the IOUT value.
        ret, data = self.read(self.hwCmdCodeReadIout, 2)
        if ret:
            self.errorCount += 1
            print(self.prefixErrorDevice + "Error reading the output current of channel {0:d}. Error code: 0x{0:02x}: ".format(channel, ret))
            return -1, float(-1)
        ioutRaw = (data[1] << 8) + data[0]
        return 0, self.l11_to_float(ioutRaw)



    # Read the external temperature sensor temperature.
    def read_temp_ext(self):
        ret, data = self.read(self.hwCmdCodeReadTempExt, 2)
        if ret:
            self.errorCount += 1
            print(self.prefixErrorDevice + "Error reading the external temperature sensor temperature. Error code: 0x{0:02x}: ".format(ret))
            return -1, float(-1)
        temperatureRaw = (data[1] << 8) + data[0]
        return 0, self.l11_to_float(temperatureRaw)



    # Read the internal die junction temperature.
    def read_temp_int(self):
        ret, data = self.read(self.hwCmdCodeReadTempInt, 2)
        if ret:
            self.errorCount += 1
            print(self.prefixErrorDevice + "Error reading the internal die junction temperature. Error code: 0x{0:02x}: ".format(ret))
            return -1, float(-1)
        temperatureRaw = (data[1] << 8) + data[0]
        return 0, self.l11_to_float(temperatureRaw)



    # Read the channel specific configuration register MFR_CONFIG_LTM4700.
    def read_mfr_config(self, channel):
        if self.set_page(channel):
            self.errorCount += 1
            return -1, 0xffff
        ret, data = self.read(self.hwCmdCodeMfrConfigChan, 2)
        if ret:
            self.errorCount += 1
            print(self.prefixErrorDevice + "Error reading the channel specific configuration register. Error code: 0x{0:02x}: ".format(ret))
            return -1, 0xffff
        return 0, (data[1] << 8) + data[0]



    # Read status information.
    def read_status(self):
        # External temperature.
        ret, temperatureExt = self.read_temp_ext()
        if ret:
            return -1, [-1]
        # Internal temperature.
        ret, temperatureInt = self.read_temp_int()
        if ret:
            return -1, [-1]
        # Vin.
        ret, vin = self.read_vin()
        if ret:
            return -1, [-1]
        # Iin.
        ret, iin = self.read_iin()
        if ret:
            return -1, [-1]
        # Output voltages and currents.
        vout = []
        for channel in range(self.hwChannels):
            ret, voutChannel = self.read_vout(channel)
            if ret:
                return -1, [-1]
            vout.append(voutChannel)
        # Output currents.
        iout = []
        for channel in range(self.hwChannels):
            ret, ioutChannel = self.read_iout(channel)
            if ret:
                return -1, [-1]
            iout.append(ioutChannel)
        return 0, [temperatureExt, temperatureInt, vin, iin, vout, iout]

