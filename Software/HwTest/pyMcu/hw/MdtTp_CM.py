#!/usr/bin/env python3
#
# File: MdtTp_CM.py
# Auth: M. Fras, Electronics Division, MPI for Physics, Munich
# Mod.: M. Fras, Electronics Division, MPI for Physics, Munich
# Date: 26 Jul 2022
# Rev.: 26 Jul 2022
#
# Python class for accessing the ATLAS MDT Trigger Processor (TP) Command
# Module (CM) Prototype via the TI Tiva TM4C1290 MCU UART.
#



import os
import McuGpio
import McuI2C
import McuSerial
import McuUart
import I2C_DS28CM00
import I2C_LTC2977
import I2C_LTM4700
import I2C_PCA9545
import I2C_Si53xx
import I2C_FireFly



class MdtTp_CM:

    # Message prefixes and separators.
    prefixStatus        = " - "
    prefixDetails       = " - "
    separatorDetails    = " - "
    prefixWarning       = "WARNING: {0:s}: ".format(__file__)
    prefixError         = "ERROR: {0:s}: ".format(__file__)
    prefixDebug         = "DEBUG: {0:s}: ".format(__file__)

    # Debug configuration.
    debugLevel = 0                 # Debug verbosity.

    # Hardware parameters.
    i2cBusNum           = 8
    fireFlyNum          = 10



    # Initialize the Command Module class.
    def __init__(self, serialDevice, debugLevel):
        self.mcuSer = McuSerial.McuSerial(serialDevice)
        self.debugLevel = debugLevel
        self.warningCount = 0
        self.errorCount = 0
        self.init_hw()



    # Initialize the hardware components.
    def init_hw(self):
        # Define the MCU peripherals.
        self.init_hw_i2c()



    # ===============================================================
    # Auxiliary functions.
    # ===============================================================

    # Extract the integer value from an MCU answer string.
    def mcu_str2int(self, mcuStr):
        data = mcuStr.split(':')
        if not data:
            return -1, 0x0
        if len(data) != 3:
            return -1, 0x0
        if data[0].strip() != "OK":
            return -1, 0x0
        return 0, int(data[2].strip(), 0)



    # ===============================================================
    # Basic monitoring and control functions.
    # ===============================================================

    # Power up the CM.
    def power_up(self):
        if self.debugLevel >= 1:
            print(self.prefixDebug + "Powering up the CM.")
        cmd = "power all 1"
        ret = self.mcu_cmd_raw(cmd)[0]
        if ret:
            self.errorCount += 1
            print(self.prefixError + "CM power up failed!")
        return ret



    # Power down the CM.
    def power_down(self):
        if self.debugLevel >= 1:
            print(self.prefixDebug + "Powering down the CM.")
        cmd = "power all 0"
        ret = self.mcu_cmd_raw(cmd)[0]
        if ret:
            self.errorCount += 1
            print(self.prefixError + "CM power down failed!")
        return ret



    # Read the power status of the CM.
    def power_status(self):
        if self.debugLevel >= 1:
            print(self.prefixDebug + "Reading the power status of the CM.")
        cmd = "power clock"
        ret, powerStatusStr = self.mcu_cmd_raw(cmd)
        print(powerStatusStr)
        cmd = "power fpga"
        ret, powerStatusStr = self.mcu_cmd_raw(cmd)
        print(powerStatusStr)
        cmd = "power firefly"
        ret, powerStatusStr = self.mcu_cmd_raw(cmd)
        print(powerStatusStr)
        cmd = "gpio power-good"
        ret, powerGoodStr = self.mcu_cmd_raw(cmd)
        ret, powerGood = self.mcu_str2int(powerGoodStr)
        print("Power good: 0x{0:03x}".format(powerGood))
        print("    P0V85 (FPGA core, 0.85 V) : " + ("OK" if (powerGood & 0x001) else "-"))
        print("    P1V8_FPGA (FPGA 1.8V)     : " + ("OK" if (powerGood & 0x002) else "-"))
        print("    P1V8_MISC (Misc 1.8V)     : " + ("OK" if (powerGood & 0x004) else "-"))
        print("    P0V9_MGT (MGT 0.9V)       : " + ("OK" if (powerGood & 0x008) else "-"))
        print("    P1V2_MGT (MGT 1.2V)       : " + ("OK" if (powerGood & 0x010) else "-"))
        print("    P3V3_MISC (Misc 3.3V)     : " + ("OK" if (powerGood & 0x020) else "-"))
        print("    P3V3_FF (FireFly 3.3V)    : " + ("OK" if (powerGood & 0x040) else "-"))
        print("    P5V_MISC (Misc 5.0V)      : " + ("OK" if (powerGood & 0x080) else "-"))
        print("    LTC2977_1 (P1V8_FPGA, P1V2_MGT, P0V9_MGT)           : " + ("OK" if (powerGood & 0x100) else "-"))
        print("    LTC2977_2 (P1V8_MISC, P3V3_MISC, P5V_MISC, P3V3_FF) : " + ("OK" if (powerGood & 0x200) else "-"))
        return ret



    # Read the serial number of the board
    def serial_number(self):
        if self.debugLevel >= 1:
            print(self.prefixDebug + "Reading the serial number from the DS28CM00 device.")
        ret, deviceFamilyCode, serialNumber, crc, crcError = self.i2cDevice_IC22_DS28CM00.read_all()
        print("Device family code: 0x{0:02x}".format(deviceFamilyCode))
        print("Serial number: 0x{0:012x}".format(serialNumber))
        print("CRC: 0x{0:02x}".format(crc))
        if crcError:
            self.errorCount += 1
            print(self.prefixError + "CRC error detected!")



    # Print details.
    def print_details(self):
        print(self.prefixDetails, end='')
        print("Command Module on serial device `" + self.mcuSer + "'.")
        if self.debugLevel >= 1:
            print(self.separatorDetails + "Warning count: {0:d}".format(self.warningCount), end='')
            print(self.separatorDetails + "Error count: {0:d}".format(self.errorCount), end='')
        if self.debugLevel >= 1:
            print(self.separatorDetails + "Read access count: {0:d}".format(self.mcuSer.accessRead), end='')
            print(self.separatorDetails + "Write access count: {0:d}".format(self.mcuSer.accessWrite), end='')
        if self.debugLevel >= 1:
            print(self.separatorDetails + "Bytes read: {0:d}".format(self.mcuSer.bytesRead), end='')
            print(self.separatorDetails + "Bytes written: {0:d}".format(self.mcuSer.bytesWritten), end='')
        print()
        return 0



    # ===============================================================
    # I2C bus.
    # ===============================================================

    # Initialize the I2C busses and devices.
    def init_hw_i2c(self):
        # I2C buses.
        self.mcuI2C = []
        for i in range(0, self.i2cBusNum):
            self.mcuI2C.append(McuI2C.McuI2C(self.mcuSer, i))
            self.mcuI2C[i].debugLevel = self.debugLevel
            # Reset the I2C bus.
            self.mcuI2C[i].ms_reset_bus()

        # IC22: DS28CM00 silicon serial number IC.
        # I2C port 4, slave address 0x50.
        self.i2cDevice_IC22_DS28CM00 = I2C_DS28CM00.I2C_DS28CM00(self.mcuI2C[3], 0x50, "IC22 (DS28CM00)")
        self.i2cDevice_IC22_DS28CM00.debugLevel = self.debugLevel



    # Reset all I2C busses.
    def i2c_reset(self):
        for i in range(0, self.i2cBusNum):
            self.mcuI2C[i].ms_reset_bus()



    # Detect devices on all I2C busses.
    def i2c_detect_devices(self):
        print("Devices found on I2C busses:")
        for i in range(0, self.i2cBusNum):
            print("Bus {0:d}: ".format(i), end='')
            ret, devAdr = self.mcuI2C[i].ms_detect_devices()
            for adr in devAdr:
                print(" 0x{0:02x}".format(adr), end='')
            print()



    # ===============================================================
    # MCU.
    # ===============================================================

    # Send a raw command to the MCU.
    def mcu_cmd_raw(self, cmd):
        # Debug: Show command.
        if self.debugLevel >= 2:
            print(self.prefixDebug + "Sending command to the MCU: " + cmd)
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
            print(self.prefixError + "Error sending command to the MCU!")
            if self.debugLevel >= 1:
                print(self.prefixError + "Command sent to MCU: " + cmd)
                print(self.prefixError + "Response from MCU:")
                print(self.mcuSer.get_full())
            return ret, ""
        return 0, self.mcuSer.get()

