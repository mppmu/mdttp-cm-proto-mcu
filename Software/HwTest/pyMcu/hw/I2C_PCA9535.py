# File: I2C_PCA9535.py
# Auth: M. Fras, Electronics Division, MPI for Physics, Munich
# Mod.: M. Fras, Electronics Division, MPI for Physics, Munich
# Date: 08 Sep 2022
# Rev.: 16 Sep 2022
#
# Python class for communicating with the PCA9535 I2C and SMBus I/O expander
# IC.
#
# Hints:
# - See datasheet "PCA9535_PCA9535C.pdf" for details.
# - Input port registers:
#   This register is an input-only port. It reflects the incoming logic levels
#   of the pins, regardless of whether the pin is defined as an input or an
#   output by Register 3. Writes to this register have no effect.
# - Output port registers:
#   This register is an output-only port. It reflects the outgoing logic levels
#   of the pins defined as outputs by Registers 6 and 7. Bit values in this
#   register have no effect on pins defined as inputs. In turn, reads from this
#   register reflect the value that is in the flip-flop controlling the output
#   selection, not the actual pin value.
# - Polarity inversion registers:
#   This register allows the user to invert the polarity of the Input port
#   register data. If a bit in this register is set (written with ‘1’), the
#   Input port data polarity is inverted. If a bit in this register is cleared
#   (written with a ‘0’), the Input port data polarity is retained.
# - Configuration registers:
#   This register configures the directions of the I/O pins. If a bit in this
#   register is set (written with ‘1’), the corresponding port pin is enabled
#   as an input with high-impedance output driver. If a bit in this register is
#   cleared (written with ‘0’), the corresponding port pin is enabled as an
#   output. At reset, the device's ports are inputs.
#



import McuI2C
import I2CDevice



class I2C_PCA9535:

    # Message prefixes and separators.
    prefixDetails       = " - "
    separatorDetails    = " - "
    prefixDebug         = "DEBUG: {0:s}: ".format(__file__)
    prefixError         = "ERROR: {0:s}: ".format(__file__)

    # Debug configuration.
    debugLevel          = 0     # Debug verbosity.

    # Hardware parameters.
    hwPortMin           = 0     # Lowest hardware port number.
    hwPortMax           = 1     # Highest hardware port number.
    hwRegTypes          = { "input"         : 0x0,
                            "output"        : 0x2,
                            "polarity"      : 0x4,
                            "configuration" : 0x6 }
    hwIoInput           = 1     # The I/O port is an input.
    hwIoOutput          = 0     # The I/O port is an output.



    # Initialize the I2C device.
    def __init__(self, mcuI2C, slaveAddr, deviceName):
        self.mcuI2C = mcuI2C
        self.slaveAddr = slaveAddr
        self.deviceName = deviceName
        self.i2cDevice = I2CDevice.I2CDevice(self.mcuI2C, self.slaveAddr, self.deviceName)
        self.i2cDevice.debugLevel = self.debugLevel
        self.prefixDebugDevice = self.prefixDebug + self.deviceName + ": "
        self.prefixErrorDevice = self.prefixError + self.deviceName + ": "



    # Return the name of a register.
    @classmethod
    def reg_to_name(cls, regAdr):
        if regAdr in (0x00, 0x01):
            regName = "input logic levels register"
        elif regAdr in (0x02, 0x03):
            regName = "output port register"
        elif regAdr in (0x04, 0x05):
            regName = "polarity inversion register"
        elif regAdr in (0x06, 0x07):
            regName = "configuration register"
        else:
            regName = "*reserved*"
        return regName



    # ===============================================================
    # Single port operations.
    # ===============================================================

    # Check the register type.
    def check_reg_type(self, regType):
        if not regType in self.hwRegTypes:
            print(self.prefixErrorDevice + "Register type `{0:s}' not valid!", regType)
            return -1
        return 0



    # Check the port number.
    def check_port_number(self, port):
        if port < self.hwPortMin or port > self.hwPortMax:
            print(self.prefixErrorDevice + "Hardware port number {0:d} out of valid range {1:d}..{2:d}!".\
                format(port, self.hwPortMin, self.hwPortMax))
            return -1
        return 0



    # Return the register address for a given register type and port.
    def type_port_to_adr(self, regType, port):
        if self.check_reg_type(regType):
            return -1, 0xff
        if self.check_port_number(port):
            return -1, 0xff
        adr = self.hwRegTypes[regType] + port
        return 0, adr



    # Read register value of a port.
    def read_reg_port(self, regType, port):
        self.i2cDevice.debugLevel = self.debugLevel
        ret, regAdr = self.type_port_to_adr(regType, port)
        if ret:
            return -1, 0xff
        regName = self.reg_to_name(regAdr)
        # Debug info.
        if self.debugLevel >= 2:
            print(self.prefixDebugDevice + "Reading the {0:s} of port {1:d}.".format(regName, port), end='')
            self.i2cDevice.print_details()
        # Assemble command to write.
        dataWr = []
        dataWr.append(regAdr)
        # Write command and read data with repeated start.
        ret, dataRd = self.i2cDevice.write_read(dataWr, 1)
        # Evaluate response.
        if ret:
            print(self.prefixErrorDevice + "Error reading the {0:s} of port {1:d}!".format(regName, port), end='')
            self.i2cDevice.print_details()
            print(self.prefixErrorDevice + "Error code: {0:d}: ".format(ret))
            return -1, 0xff
        if not dataRd:
            print(self.prefixErrorDevice + "Error reading the {0:s} of port {1:d}: No data received!".format(regName, port), end='')
            self.i2cDevice.print_details()
            return -1, 0xff
        # Debug info.
        if self.debugLevel >= 2:
            print(self.prefixDebugDevice + "Read the {0:s} of port {1:d}: 0x{2:02x}.".format(regName, port, dataRd[0]), end='')
            self.i2cDevice.print_details()
        return 0, dataRd[0]



    # Write register value of a port.
    def write_reg_port(self, regType, port, value):
        self.i2cDevice.debugLevel = self.debugLevel
        ret, regAdr = self.type_port_to_adr(regType, port)
        if ret:
            return -1, 0xff
        regName = self.reg_to_name(regAdr)
        value &= 0xff       # Limit to 8 bits.
        # Debug info.
        if self.debugLevel >= 2:
            print(self.prefixDebugDevice + "Writing value 0x{0:02x} to the {1:s} of port {2:d}.".format(value, regName, port), end='')
            self.i2cDevice.print_details()
        # Assemble command and data to write.
        dataWr = []
        dataWr.append(regAdr)
        dataWr.append(value)
        # Write command and data.
        ret = self.i2cDevice.write(dataWr)
        # Evaluate response.
        if ret:
            print(self.prefixErrorDevice + "Error writing value 0x{0:02x} to the {1:s} of port {2:d}!".format(value ,regName, port), end='')
            self.i2cDevice.print_details()
            print(self.prefixErrorDevice + "Error code: {0:d}: ".format(ret))
            return -1
        return 0



    # Read the input logic levels of a port.
    def read_input_port(self, port):
        ret, value = self.read_reg_port("input", port)
        return ret, value



    # Read the output logic levels of a port.
    def read_output_port(self, port):
        ret, value = self.read_reg_port("output", port)
        return ret, value



    # Read the polarity inversion register of a port.
    def read_polarity_port(self, port):
        ret, value = self.read_reg_port("polarity", port)
        return ret, value



    # Read the configuration register of a port.
    def read_config_port(self, port):
        ret, value = self.read_reg_port("configuration", port)
        return ret, value



    # Write the output logic levels of a port.
    def write_output_port(self, port, value):
        ret = self.write_reg_port("output", port, value)
        return ret



    # Write the polarity inversion register of a port.
    def write_polarity_port(self, port, value):
        ret = self.write_reg_port("polarity", port, value)
        return ret



    # Write the configuration register of a port.
    def write_config_port(self, port, value):
        ret = self.write_reg_port("configuration", port, value)
        return ret



    # ===============================================================
    # Operations for all ports at once.
    # ===============================================================

    # Read register value of all ports.
    def read_reg(self, regType):
        self.i2cDevice.debugLevel = self.debugLevel
        ret, regAdr = self.type_port_to_adr(regType, 0)
        if ret:
            return -1, 0xff
        regName = self.reg_to_name(regAdr)
        # Debug info.
        if self.debugLevel >= 2:
            print(self.prefixDebugDevice + "Reading the {0:s} of all ports.".format(regName), end='')
            self.i2cDevice.print_details()
        # Assemble command to write.
        dataWr = []
        dataWr.append(regAdr)               # Register address.
        # Write command and read data with repeated start.
        ret, dataRd = self.i2cDevice.write_read(dataWr, 2)
        # Evaluate response.
        if ret:
            print(self.prefixErrorDevice + "Error reading the {0:s} of all ports!".format(regName), end='')
            self.i2cDevice.print_details()
            print(self.prefixErrorDevice + "Error code: {0:d}: ".format(ret))
            return -1, 0xffffff
        if len(dataRd) != 2:
            print(self.prefixErrorDevice + "Error reading the {0:s} of all ports: Incorrect amount of data received ({1:d} instead of 2)!".format(regName, len(dataRd)), end='')
            self.i2cDevice.print_details()
            return -1, 0xffffff
        # Calculate value for all ports.
        value  =  0xff & dataRd[0]          # Port 0.
        value |= (0xff & dataRd[1]) << 8    # Port 1.
        # Debug info.
        if self.debugLevel >= 2:
            print(self.prefixDebugDevice + "Read the {0:s} of all ports: 0x{1:06x}.".format(regName, value), end='')
            self.i2cDevice.print_details()
        return 0, value



    # Write register value of all ports.
    def write_reg(self, regType, value):
        self.i2cDevice.debugLevel = self.debugLevel
        ret, regAdr = self.type_port_to_adr(regType, 0)
        if ret:
            return -1, 0xff
        regName = self.reg_to_name(regAdr)
        value &= 0xffff     # Limit to 16 bits.
        # Debug info.
        if self.debugLevel >= 2:
            print(self.prefixDebugDevice + "Writing value 0x{0:04x} to the {1:s} of all ports.".format(value, regName), end='')
            self.i2cDevice.print_details()
        # Assemble command and data to write.
        dataWr = []
        dataWr.append(regAdr)               # Register address.
        dataWr.append(value & 0xff)         # Port 0.
        dataWr.append((value >> 8) & 0xff)  # Port 1.
        # Write command and data.
        ret = self.i2cDevice.write(dataWr)
        # Evaluate response.
        if ret:
            print(self.prefixErrorDevice + "Error writing value 0x{0:04x} to the {1:s} of all ports!".format(value, regName), end='')
            self.i2cDevice.print_details()
            print(self.prefixErrorDevice + "Error code: {0:d}: ".format(ret))
            return -1
        return 0



    # Read the input logic levels of all ports.
    def read_input(self):
        ret, value = self.read_reg("input")
        return ret, value



    # Read the output logic levels of all ports.
    def read_output(self):
        ret, value = self.read_reg("output")
        return ret, value



    # Read the polarity inversion register of all ports.
    def read_polarity(self):
        ret, value = self.read_reg("polarity")
        return ret, value



    # Read the configuration register of all ports.
    def read_config(self):
        ret, value = self.read_reg("configuration")
        return ret, value



    # Write the output logic levels of all ports.
    def write_output(self, value):
        ret = self.write_reg("output", value)
        return ret



    # Write the polarity inversion register of all ports.
    def write_polarity(self, value):
        ret = self.write_reg("polarity", value)
        return ret



    # Write the configuration register of all ports.
    def write_config(self, value):
        ret = self.write_reg("configuration", value)
        return ret

