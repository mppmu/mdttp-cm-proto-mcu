# File: I2C_Si53xx.py
# Auth: M. Fras, Electronics Division, MPI for Physics, Munich
# Mod.: M. Fras, Electronics Division, MPI for Physics, Munich
# Date: 29 Apr 2020
# Rev.: 09 Sep 2022
#
# Python class for communicating with Silicon Labs Si5341/40 and Si5345/44/42
# devices.
#



import os
import McuI2C
import I2CDevice
import time


class I2C_Si53xx:

    # Message prefixes and separators.
    prefixDetails       = " - "
    separatorDetails    = " - "
    prefixDebug         = "DEBUG: {0:s}: ".format(__file__)
    prefixError         = "ERROR: {0:s}: ".format(__file__)

    # Debug configuration.
    debugLevel = 0                 # Debug verbosity.

    # Hardware parameters.
    fileRegMapMarkComment = "#"
    hwAdrMin            = 0x0C
    hwAdrMax            = 0x12
    
    #definition
    # in reg 0x000C
    SYSINCAL_b = 0x1
    LOSXAXB_b = 0x2
#    LOSREF_b = 0x4
    # in reg 0x000E
    LOL_b = 0x2

    #SMBUS_TIMEOUT_b = 0x20
    # in reg 0x000D
    LOSIN_b = 0xF #Loss of Signal for the FB_IN, IN2, IN1, IN0 inputs

    # Initialize the I2C device.
    def __init__(self, mcuI2C, slaveAddr, deviceName):
        self.mcuI2C = mcuI2C
        self.slaveAddr = slaveAddr
        self.deviceName = deviceName
        self.i2cDevice = I2CDevice.I2CDevice(self.mcuI2C, self.slaveAddr, self.deviceName)
        self.i2cDevice.debugLevel = self.debugLevel
        self.prefixDebugDevice = self.prefixDebug + self.deviceName + ": "
        self.prefixErrorDevice = self.prefixError + self.deviceName + ": "


    def check_adr(self, regAdr):
        if regAdr < self.hwAdrMin or regAdr > self.hwAdrMax:
            print(self.prefixErrorDevice + "Data word register value {0:d} out of valid range {1:d}..{2:d}!".\
                format(regAdr, self.hwAdrMin, self.hwAdrMax))
            return -1
        return 0
    
    # Load the configuration of an Si53xx IC from a register map file produced
    # with the ClockBuilder Pro software.
    def config_file(self, fileRegMapName):
        # Check if fileRegMapName exists.
        if not os.path.exists(fileRegMapName):
            print(self.prefixErrorDevice + "The register map file `{0:s}' does not exist!".format(fileRegMapName))
            return -1
        # Check if fileRegMapName is a file.
        if not os.path.isfile(fileRegMapName):
            print(self.prefixErrorDevice + "The register map file `{0:s}' is not a file!".format(fileRegMapName))
            return -1
        # Check if the register map file is readable.
        if not os.access(fileRegMapName, os.R_OK):
            print(self.prefixErrorDevice + "Cannot open the register map file `{0:s}'!".format(fileRegMapName))
            return -1

        fileRegMapLineCount = 0
        # Read and process the register map file.
        with open(fileRegMapName, encoding='UTF-8') as fileRegMap:
            for fileRegMapLine in fileRegMap:
                fileRegMapLineCount += 1
                if self.debugLevel >= 3:
                    print(self.prefixDebugDevice + "Processing line {0:d} of the register map file `{1:s}':".\
                        format(fileRegMapLineCount, fileRegMapName))
                    print(self.prefixDebugDevice + fileRegMapLine.strip('\n\r'))
                # Strip all leading and trailing white spaces, tabs, line feeds and carriage returns.
                lineStripped = fileRegMapLine.strip(' \t\n\r')
                # Remove comments.
                if lineStripped.find(self.fileRegMapMarkComment) >= 0:
                    lineCommentRemoved = lineStripped[0:lineStripped.find(self.fileRegMapMarkComment)].strip(' \t')
                else:
                    lineCommentRemoved = lineStripped
                # if line includes word Delay in pos 2, then delay
                if lineStripped.find("Delay") == 2:
                    if self.debugLevel >= 3:
                        print(self.prefixDebugDevice + "Delay found, delaying 300ms")
                    time.sleep(0.3)
                    continue
                    # Get list of elements.
                lineElements = list(filter(None, lineCommentRemoved.split(",")))
                lineElements = list(el.strip(' \t\n\r') for el in lineElements)
                # Ignore lines without data.
                if not lineElements:
                    continue
                # Ignore lines with content "Address,Data".
                if lineElements[0].lower() == "address":
                    continue
                # Convert hexadecimal values from ??h to 0x??.
                lineElements = list("0x" + el.strip("h") if el.find("h") >= 0 else el for el in lineElements)
                # Convert to integers.
                lineData = [int(i, 0) for i in lineElements]
                # Extract page, register address and data from lineData.
                # For details, see "AN926: Reading and Writing Registers with
                # SPI and I2C", "an926-reading-writing-registers-spi-i2c.pdf".
                pageByte = (lineData[0] >> 8) & 0xff
                adrByte = lineData[0] & 0xff
                dataByte = lineData[1] & 0xff
                # Set the page register with the upper byte of the 2-byte address.
                ret = self.i2cDevice.write([0x01, pageByte])
                # Send second byte of the addresse and the data byte.
                ret = self.i2cDevice.write([adrByte, dataByte])
                if ret:
                    print(self.prefixErrorDevice + "Error sending data of register map file `{0:s}'! Line number: {1:d}, Data: {2:s}".\
                        format(fileRegMapName, fileRegMapLineCount, lineCommentRemoved))
                    return -1
        return 0

    # Return the name of a register address.
    def adr_to_name(self, regAdr):
        regName = "*other/unknown*"
        if regAdr == 0xC:
            regName = "Status regs 0xC"
        elif regAdr == 0xD:
            regName = "Status reg: LOSIN"
        elif regAdr == 0xE:
            regName = "Status reg: LOL"
        elif regAdr == 0x11:
            regName = "Sticky Status regs _FLG"
        elif regAdr == 0x12:
            regName = "Sticky Status reg: LOSIN_FLG"
        elif regAdr == 0x13:
            regName = "Sticky Status reg: LOL_FLG"
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
        # Set the page register to 0x00
        ret = self.i2cDevice.write([0x01, 0x00])        # status to readback only on pgae 0x00
        
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

    def read_status_regs(self):
        ret1, stats = self.read_reg(0xC)
        ret2, LOSIN = self.read_reg(0xD)
        ret3, LOL = self.read_reg(0xE)
        return ret1+ret2+ret3, stats & 0x2F, LOSIN & 0x0F, LOL & self.LOL_b
    
    def read_sticky_status_regs(self):
        ret1, s_stats = self.read_reg(0x11)
        ret2, s_LOSIN = self.read_reg(0x12)
        ret3, s_LOL = self.read_reg(0x13)
        return ret1+ret2+ret3, s_stats & 0x2F, s_LOSIN & 0x0F, s_LOL & self.LOL_b
    
    def print_status_str(self):
        ret, stats, LOSIN, LOL = self.read_status_regs()
        if ret:
            print(self.prefixErrorDevice + "Error reading status!", end='')
            self.i2cDevice.print_details()
            print(self.prefixErrorDevice + "Error code: {0:d}: ".format(ret))
            return -1, "ERROR"
        string = ""
        string += "\t" + str((stats & self.SYSINCAL_b)==self.SYSINCAL_b)
        string += "\t" + str((stats & self.LOSXAXB_b)==self.LOSXAXB_b)
        string += "\t" + str(LOL == self.LOL_b)
        string += "\t\t" + str(LOSIN)
        return 0, string
        
    def print_sticky_status_str(self):
        ret, s_stats, s_LOSIN, s_LOL= self.read_sticky_status_regs()
        if ret:
            print(self.prefixErrorDevice + "Error reading sticky status!", end='')
            self.i2cDevice.print_details()
            print(self.prefixErrorDevice + "Error code: {0:d}: ".format(ret))
            return -1, "ERROR"
        string = ""
        string += " " + str((s_stats & self.SYSINCAL_b)==self.SYSINCAL_b)
        string += " " + str((s_stats & self.LOSXAXB_b)==self.LOSXAXB_b)
        string += " " + str(s_LOL == self.LOL_b)
        string += " " + str(s_LOSIN)
        return 0, string
