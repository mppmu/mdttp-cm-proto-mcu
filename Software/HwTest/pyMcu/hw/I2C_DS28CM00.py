# File: I2C_DS28CM00.py
# Auth: M. Fras, Electronics Division, MPI for Physics, Munich
# Mod.: M. Fras, Electronics Division, MPI for Physics, Munich
# Date: 08 May 2020
# Rev.: 24 Jul 2020
#
# Python class for communicating with the DS28CM00 silicon serial number IC.
#



import McuI2C
import I2CDevice



class I2C_DS28CM00:

    # Message prefixes and separators.
    prefixDetails       = " - "
    separatorDetails    = " - "
    prefixDebug         = "DEBUG: {0:s}: ".format(__file__)
    prefixError         = "ERROR: {0:s}: ".format(__file__)

    # Debug configuration.
    debugLevel          = 0     # Debug verbosity.

    # Hardware parameters.
    hwAdrMin            = 0x00
    hwAdrMax            = 0x08



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
        if regAdr == 0x00:
            regName = "device family code"
        elif regAdr == 0x01:
            regName = "serial number, bits 0 to 7"
        elif regAdr == 0x02:
            regName = "serial number, bits 8 to 15"
        elif regAdr == 0x03:
            regName = "serial number, bits 16 to 23"
        elif regAdr == 0x04:
            regName = "serial number, bits 24 to 31"
        elif regAdr == 0x05:
            regName = "serial number, bits 32 to 29"
        elif regAdr == 0x06:
            regName = "serial number, bits 40 to 47"
        elif regAdr == 0x07:
            regName = "CRC of family code and 48-bit serial number"
        elif regAdr == 0x08:
            regName = "control register"
        else:
            regName = "*other/unknown*"
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



    # Calculate the CRC.
    # Algorithms found at these web pages:
    # - http://www.maximintegrated.com/en/app-notes/index.mvp/id/27
    # - http://www.jechavarria.com/2013/02/04/components-i-usually-use-i-ds28cm00-i2c-serial-number/
    @classmethod
    def crc_calc(cls, deviceFamilyCode, serialNumber, crc):
        crcCheck = (crc << 56) | (serialNumber << 8) | deviceFamilyCode
        crcCalc = 0
        for i in range(0, 56):
            crcBit = (crcCheck >> i) & 0x01
            crcFb = (crcCalc ^ crcBit) & 0x01
            crcCalc >>= 1
            if crcFb != 0:
                crcCalc ^= 0x8c
        return crcCalc



    # Read all information.
    def read_all(self):
        ret, deviceFamilyCode = self.read_reg(0x00)
        serialNumber = 0
        for i in range(0, 6):
            retTmp, snTmp = self.read_reg(i + 1)
            ret |= retTmp
            serialNumber |= (snTmp & 0xff) << (8 * i)
        retTmp, crc = self.read_reg(0x07)
        ret |= retTmp
        crcError = crc != self.crc_calc(deviceFamilyCode, serialNumber, crc)
        return ret, deviceFamilyCode, serialNumber, crc, crcError

