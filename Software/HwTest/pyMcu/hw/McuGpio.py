# File: McuGpio.py
# Auth: M. Fras, Electronics Division, MPI for Physics, Munich
# Mod.: M. Fras, Electronics Division, MPI for Physics, Munich
# Date: 15 Jun 2020
# Rev.: 15 Jun 2020
#
# Python class for setting and rading the GPIO pins of a given type.
#



import McuSerial



class McuGpio:

    # Message prefixes.
    prefixError = "ERROR: {0:s}: ".format(__file__)
    prefixDebug = "DEBUG: {0:s}: ".format(__file__)

    # Debug configuration.
    debugLevel = 0                 # Debug verbosity.

    # Hardware parameters.
    hwGpioTypes = ["sm-pwr-en",
                   "cm-ready",
                   "led-status",
                   "led-user",
                   "mux-hs-sel",
                   "mux-hs-pd",
                   "mux-clk-sel",
                   "power",
                   "kup",
                   "zup",
                   "reset",
                   "pe-int",
                   "spare"]
    hwMarkDataPatternWrite = "GPIO {0:s} set to"
    hwMarkDataPatternRead = "Current GPIO {0:s} value:"



    # Initialize the GPIO.
    def __init__(self, mcuSer):
        self.mcuSer = mcuSer
        self.errorCount = 0



    # Check if a GPIO type is valid.
    def check_gpio_type(self, gpioType):
        if not gpioType in self.hwGpioTypes:
            print(self.prefixError + "GPIO type '{0:s}' is not valid!".format(gpioType))
            return True
        return False



    # Set the value of a GPIO type.
    def set(self, gpioType, val):
        if self.check_gpio_type(gpioType):
            return 1
        if self.debugLevel >= 2:
            print(self.prefixDebug + "Setting the GPIO {0:s} to 0x{1:02x}.".format(gpioType, val))
        cmd = "gpio {0:s} 0x{1:02x}".format(gpioType, val)
        # Debug: Show command.
        if self.debugLevel >= 3:
            print(self.prefixDebug + "Sending command for GPIO: " + cmd)
        # Send command.
        self.mcuSer.send(cmd)
        # Debug: Show response.
        if self.debugLevel >= 3:
            print(self.prefixDebug + "Response from MCU:")
            print(self.mcuSer.get_full())
        # Evaluate response.
        ret = self.mcuSer.eval()
        if ret:
            self.errorCount += 1
            print(self.prefixError + "Error sending command for GPIO!")
            if self.debugLevel >= 1:
                print(self.prefixError + "Command sent to MCU: " + cmd)
                print(self.prefixError + "Response from MCU:")
                print(self.mcuSer.get_full())
            return ret
        return 0



    # Get the current value of a GPIO tpye.
    def get(self, gpioType):
        if self.check_gpio_type(gpioType):
            return 1
        if self.debugLevel >= 2:
            print(self.prefixDebug + "Getting the current value of GPIO {0:s}.".format(gpioType))
        cmd = "gpio {0:s}".format(gpioType)
        # Debug: Show command.
        if self.debugLevel >= 3:
            print(self.prefixDebug + "Sending command for GPIO: " + cmd)
        # Send command.
        self.mcuSer.send(cmd)
        # Debug: Show response.
        if self.debugLevel >= 3:
            print(self.prefixDebug + "Response from MCU:")
            print(self.mcuSer.get_full())
        # Evaluate response.
        ret = self.mcuSer.eval()
        if ret:
            self.errorCount += 1
            print(self.prefixError + "Error sending command for GPIO!")
            if self.debugLevel >= 1:
                print(self.prefixError + "Command sent to MCU: " + cmd)
                print(self.prefixError + "Response from MCU:")
                print(self.mcuSer.get_full())
            return ret, 0
        # Get and parse response from MCU.
        hwMarkData = self.hwMarkDataPatternRead.format(gpioType)
        dataStr = self.mcuSer.get()
        dataPos = dataStr.find(hwMarkData)
        if dataPos < 0:
            self.errorCount += 1
            print(self.prefixError + "Error parsing data read from the GPIO {0:s}!".format(gpioType))
            if self.debugLevel >= 1:
                print(self.prefixError + "Command sent to MCU: " + cmd)
                print(self.prefixError + "Response from MCU:")
                print(self.mcuSer.get_full())
            return -1, 0
        # Get sub-string containing the data. Add the length of hwMarkData to
        # point beyond the data mark.
        dataStr = dataStr[dataPos+len(hwMarkData):].strip()
        # Convert data string to list of data bytes.
        data = [int(i, 0) for i in filter(None, dataStr.split(" "))]
        if self.debugLevel >= 2:
            print(self.prefixDebug + "Data read:", end='')
            for datum in data:
                print(" 0x{0:02x}".format(datum), end='')
            print()
        if not data:
            self.errorCount += 1
            print(self.prefixError + "No data received from the GPIO {0:s}!".format(gpioType))
            return -1, 0
        return 0, data[0]



    # Modify the bits of a GPIO type.
    def bits_mod(self, gpioType, bitsClr, bitsSet):
        if self.check_gpio_type(gpioType):
            return 1
        if self.debugLevel >= 2:
            print(self.prefixDebug + "Modifying the GPIO {0:s} bits: Clear = 0x{1:02x}, set = 0x{2:02x}.".format(gpioType, bitsClr, bitsSet))
        ret, gpioVal = self.get(gpioType)
        if ret:
            self.errorCount += 1
            print(self.prefixError + "Error modifying the GPIO {0:s} bits!".format(gpioType))
            return ret
        gpioVal &= ~bitsClr
        gpioVal |= bitsSet
        ret = self.set(gpioType, gpioVal)
        if ret:
            self.errorCount += 1
            print(self.prefixError + "Error modifying the GPIO {0:s} bits!".format(gpioType))
            return ret
        return 0



    # Clear bits of a GPIO type.
    def bits_clr(self, gpioType, bitsClr):
        return self.bits_mod(gpioType, bitsClr, 0)



    # Set bits of a GPIO type.
    def bits_set(self, gpioType, bitsSet):
        return self.bits_mod(gpioType, 0, bitsSet)

