# File: I2C_Si53xx.py
# Auth: M. Fras, Electronics Division, MPI for Physics, Munich
# Mod.: M. Fras, Electronics Division, MPI for Physics, Munich
# Date: 29 Apr 2020
# Rev.: 20 Apr 2021
#
# Python class for communicating with Silicon Labs Si5341/40 and Si5345/44/42
# devices.
#



import os
import McuI2C
import I2CDevice



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


    # Initialize the I2C device.
    def __init__(self, mcuI2C, slaveAddr, deviceName):
        self.mcuI2C = mcuI2C
        self.slaveAddr = slaveAddr
        self.deviceName = deviceName
        self.i2cDevice = I2CDevice.I2CDevice(self.mcuI2C, self.slaveAddr, self.deviceName)
        self.i2cDevice.debugLevel = self.debugLevel
        self.prefixDebugDevice = self.prefixDebug + self.deviceName + ": "
        self.prefixErrorDevice = self.prefixError + self.deviceName + ": "



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
        with open(fileRegMapName) as fileRegMap:
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

