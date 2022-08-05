#!/usr/bin/env python3
#
# File: MdtTp_CM.py
# Auth: M. Fras, Electronics Division, MPI for Physics, Munich
# Mod.: M. Fras, Electronics Division, MPI for Physics, Munich
# Date: 26 Jul 2022
# Rev.: 04 Aug 2022
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
import I2C_MCP9902
import I2C_PCA9545
import I2C_Si53xx
import I2C_FireFly



class MdtTp_CM:

    # Message prefixes and separators.
    prefixStatus        = "    "
    prefixDetails       = "    "
    separatorDetails    = " - "
    prefixWarning       = "WARNING: {0:s}: ".format(__file__)
    prefixError         = "ERROR: {0:s}: ".format(__file__)
    prefixDebug         = "DEBUG: {0:s}: ".format(__file__)

    # Debug configuration.
    debugLevel = 0                 # Debug verbosity.

    # Hardware parameters.
    i2cBusNum           = 10
    i2cBusActive        = [1, 2, 3, 4, 5, 6, 7, 8]
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
        data = mcuStr.split(' ')
        if not data:
            return -1, 0x0
        if len(data) < 2:
            return -1, 0x0
        if data[0].strip(':') != "OK":
            return -1, 0x0
        return 0, int(data[-1].strip(), 0)



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
        print(self.prefixStatus + "P0V85 (FPGA core, 0.85 V) : " + ("OK" if (powerGood & 0x001) else "-"))
        print(self.prefixStatus + "P1V8_FPGA (FPGA 1.8V)     : " + ("OK" if (powerGood & 0x002) else "-"))
        print(self.prefixStatus + "P1V8_MISC (Misc 1.8V)     : " + ("OK" if (powerGood & 0x004) else "-"))
        print(self.prefixStatus + "P0V9_MGT (MGT 0.9V)       : " + ("OK" if (powerGood & 0x008) else "-"))
        print(self.prefixStatus + "P1V2_MGT (MGT 1.2V)       : " + ("OK" if (powerGood & 0x010) else "-"))
        print(self.prefixStatus + "P3V3_MISC (Misc 3.3V)     : " + ("OK" if (powerGood & 0x020) else "-"))
        print(self.prefixStatus + "P3V3_FF (FireFly 3.3V)    : " + ("OK" if (powerGood & 0x040) else "-"))
        print(self.prefixStatus + "P5V_MISC (Misc 5.0V)      : " + ("OK" if (powerGood & 0x080) else "-"))
        print(self.prefixStatus + "LTC2977_1 (P1V8_FPGA, P1V2_MGT, P0V9_MGT)           : " + ("OK" if (powerGood & 0x100) else "-"))
        print(self.prefixStatus + "LTC2977_2 (P1V8_MISC, P3V3_MISC, P5V_MISC, P3V3_FF) : " + ("OK" if (powerGood & 0x200) else "-"))
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



    # Monitor the temperatures.
    def mon_temp(self):
        # Power modules.
        # LTM47000 core power.
        if self.debugLevel >= 1:
            print(self.prefixDebug + "Reading the temperatures of the LTM4700 power modules for the VU13P core power.")
        print("VU13P core power 1 (ext) - {0:15s}: {1:6.3f} degC".format(self.i2cDevice_IC26_LTM4700.deviceName, self.i2cDevice_IC26_LTM4700.read_temp_ext()[1]))
        print("VU13P core power 1 (int) - {0:15s}: {1:6.3f} degC".format(self.i2cDevice_IC26_LTM4700.deviceName, self.i2cDevice_IC26_LTM4700.read_temp_int()[1]))
        print("VU13P core power 2 (ext) - {0:15s}: {1:6.3f} degC".format(self.i2cDevice_IC27_LTM4700.deviceName, self.i2cDevice_IC27_LTM4700.read_temp_ext()[1]))
        print("VU13P core power 2 (int) - {0:15s}: {1:6.3f} degC".format(self.i2cDevice_IC27_LTM4700.deviceName, self.i2cDevice_IC27_LTM4700.read_temp_int()[1]))
        # LTM4662 MGT power.
        if self.debugLevel >= 1:
            print(self.prefixDebug + "Reading the temperatures of the power modules providing the MGT power.")
        if self.debugLevel >= 2:
            # Read the product ID, the manufacturer ID and the revision.
            print(self.prefixDebug + "{0:s} product ID: 0x{1:02x}".format(self.i2cDevice_IC61_MCP9902.deviceName, self.i2cDevice_IC61_MCP9902.read_product_id()[1]))
            print(self.prefixDebug + "{0:s} manufacturer ID: 0x{1:02x}".format(self.i2cDevice_IC61_MCP9902.deviceName, self.i2cDevice_IC61_MCP9902.read_manufacturer_id()[1]))
            print(self.prefixDebug + "{0:s} revision: 0x{1:02x}".format(self.i2cDevice_IC61_MCP9902.deviceName, self.i2cDevice_IC61_MCP9902.read_revision()[1]))
        # Read the temperature.
        print("MGT 0.9 V power          - {0:15s}: {1:6.3f} degC".format(self.i2cDevice_IC61_MCP9902.deviceName, self.i2cDevice_IC61_MCP9902.read_temp_ext()[1]))
        if self.debugLevel >= 2:
            # Read the product ID, the manufacturer ID and the revision.
            print(self.prefixDebug + "{0:s} product ID: 0x{1:02x}".format(self.i2cDevice_IC62_MCP9902.deviceName, self.i2cDevice_IC62_MCP9902.read_product_id()[1]))
            print(self.prefixDebug + "{0:s} manufacturer ID: 0x{1:02x}".format(self.i2cDevice_IC62_MCP9902.deviceName, self.i2cDevice_IC62_MCP9902.read_manufacturer_id()[1]))
            print(self.prefixDebug + "{0:s} revision: 0x{1:02x}".format(self.i2cDevice_IC62_MCP9902.deviceName, self.i2cDevice_IC62_MCP9902.read_revision()[1]))
        # Read the temperature.
        print("MGT 1.2 V power          - {0:15s}: {1:6.3f} degC".format(self.i2cDevice_IC62_MCP9902.deviceName, self.i2cDevice_IC62_MCP9902.read_temp_ext()[1]))
        # VU13P FPGA temperature.
        if self.debugLevel >= 1:
            print(self.prefixDebug + "Reading the temperatures of the VU13P.")
        if self.debugLevel >= 2:
            # Read the product ID, the manufacturer ID and the revision.
            print(self.prefixDebug + "{0:s} product ID: 0x{1:02x}".format(self.i2cDevice_IC60_MCP9902.deviceName, self.i2cDevice_IC60_MCP9902.read_product_id()[1]))
            print(self.prefixDebug + "{0:s} manufacturer ID: 0x{1:02x}".format(self.i2cDevice_IC60_MCP9902.deviceName, self.i2cDevice_IC60_MCP9902.read_manufacturer_id()[1]))
            print(self.prefixDebug + "{0:s} revision: 0x{1:02x}".format(self.i2cDevice_IC60_MCP9902.deviceName, self.i2cDevice_IC60_MCP9902.read_revision()[1]))
        # Read the temperature.
        print("VU13P FPGA               - {0:15s}: {1:6.3f} degC".format(self.i2cDevice_IC60_MCP9902.deviceName, self.i2cDevice_IC60_MCP9902.read_temp_ext()[1]))
        # Board temperatures.
        boardTempSensors = [self.i2cDevice_IC60_MCP9902, self.i2cDevice_IC61_MCP9902, self.i2cDevice_IC62_MCP9902]
        sensorNum = 1
        for sensor in boardTempSensors:
            if self.debugLevel >= 1:
                print(self.prefixDebug + "Reading the temperatures from local sensors on the board.")
            if self.debugLevel >= 2:
                # Read the manufacturer and device ID.
                print(self.prefixDebug + "{0:s} product ID: 0x{1:02x}".format(sensor.deviceName, sensor.read_product_id()[1]))
                print(self.prefixDebug + "{0:s} manufacturer ID: 0x{1:02x}".format(sensor.deviceName, sensor.read_manufacturer_id()[1]))
                print(self.prefixDebug + "{0:s} revision: 0x{1:02x}".format(sensor.deviceName, sensor.read_revision()[1]))
            print("Board {0:d}                  - {1:15s}: {2:6.3f} degC".format(sensorNum, sensor.deviceName, sensor.read_temp_int()[1]))
            sensorNum += 1



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
        self.i2cDevice_IC22_DS28CM00 = I2C_DS28CM00.I2C_DS28CM00(self.mcuI2C[4], 0x50, "IC22 (DS28CM00)")
        self.i2cDevice_IC22_DS28CM00.debugLevel = self.debugLevel

        # MCP9902 low-temperature remote diode sensor IC.
        # IC60: I2C port 4, slave address 0x3c, VU13P temperature.
        self.i2cDevice_IC60_MCP9902 = I2C_MCP9902.I2C_MCP9902(self.mcuI2C[4], 0x3c, "IC60 (MCP9902)")
        self.i2cDevice_IC60_MCP9902.debugLevel = self.debugLevel
        # IC61: I2C port 4, slave address 0x1c, clock generator ICs column 1.
        self.i2cDevice_IC61_MCP9902 = I2C_MCP9902.I2C_MCP9902(self.mcuI2C[4], 0x1c, "IC61 (MCP9902)")
        self.i2cDevice_IC61_MCP9902.debugLevel = self.debugLevel
        # IC62: I2C port 4, slave address 0x7c, clock generator ICs column 1.
        self.i2cDevice_IC62_MCP9902 = I2C_MCP9902.I2C_MCP9902(self.mcuI2C[4], 0x7c, "IC62 (MCP9902)")
        self.i2cDevice_IC62_MCP9902.debugLevel = self.debugLevel
        # Set up the configuration registers.
        self.i2cDevice_IC60_MCP9902.write_config_0(0x00)
        self.i2cDevice_IC60_MCP9902.write_config_1(0x00)
        self.i2cDevice_IC61_MCP9902.write_config_0(0x00)
        self.i2cDevice_IC61_MCP9902.write_config_1(0x00)
        self.i2cDevice_IC62_MCP9902.write_config_0(0x00)
        self.i2cDevice_IC62_MCP9902.write_config_1(0x00)

        # Power modules.
        # IC58: LTC2977 8-channel PMBus power system manager IC (1.8 V FPGA, 1.2 V MGT, 0.9 V MGT).
        self.i2cDevice_IC58_LTC2977 = I2C_LTC2977.I2C_LTC2977(self.mcuI2C[1], 0x5c, "IC58 (LTC2977)")
        # IC59: LTC2977 8-channel PMBus power system manager IC (1.8 V misc, 3.3 V misc, 5.0 V misc, 3.3. V FireFly).
        self.i2cDevice_IC59_LTC2977 = I2C_LTC2977.I2C_LTC2977(self.mcuI2C[1], 0x5d, "IC59 (LTC2977)")
        # IC26: LTM4700 regulator with digital power system management IC (VU13P core voltage).
        self.i2cDevice_IC26_LTM4700 = I2C_LTM4700.I2C_LTM4700(self.mcuI2C[1], 0x40, "IC26 (LTM4700)")
        # IC27: LTM4700 regulator with digital power system management IC (VU13P core voltage).
        self.i2cDevice_IC27_LTM4700 = I2C_LTM4700.I2C_LTM4700(self.mcuI2C[1], 0x41, "IC27 (LTM4700)")



    # Reset all I2C busses.
    def i2c_reset(self):
        for i in range(0, self.i2cBusNum):
            if i in self.i2cBusActive:
                self.mcuI2C[i].ms_reset_bus()



    # Detect devices on all I2C busses.
    def i2c_detect_devices(self):
        print("Devices found on I2C busses:")
        for i in range(0, self.i2cBusNum):
            if i in self.i2cBusActive:
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



    # Get the MCU user LEDs.
    def mcu_led_user_get(self):
        if self.debugLevel >= 1:
            print(self.prefixDebug + "Reading the MCU user LEDs.")
        # Send command.
        self.mcuSer.send("gpio led-user")
        # Evaluate response.
        ret = self.mcuSer.eval()
        if ret:
            self.errorCount += 1
            print(self.prefixError + "Error reading the MCU user LEDs!")
            return ret, 0
        return 0, self.mcu_str2int(self.mcuSer.get())[1]



    # Set the MCU user LEDs.
    def mcu_led_user_set(self, value):
        if self.debugLevel >= 1:
            print(self.prefixDebug + "Setting the MCU user LEDs to 0x{0:03x}.".format(value))
        # Send command.
        self.mcuSer.send("gpio led-user 0x{0:03x}".format(value))
        # Evaluate response.
        ret = self.mcuSer.eval()
        if ret:
            self.errorCount += 1
            print(self.prefixError + "Error setting the MCU user LEDs!")
            return ret
        return 0



    # ===============================================================
    # Power modules.
    # ===============================================================

    # Define the measurement names and the values of the shunt resistors.
    IC58_LTC2977_measurementNames =     ["P1V8_FPGA", "P1V8_FPGA", "<unused>", "<unused>", "P1V2_MGT", "P1V2_MGT", "P0V9_MGT", "P0V9_MGT"]
    IC58_LTC2977_currentSenseShunts =   [0, 0.005 / 2, 0, 0, 0, 0.003 / 2, 0, 0.005 / 2]
    IC59_LTC2977_measurementNames =     ["P1V8_MISC", "P1V8_MISC", "P3V3_MISC", "P3V3_MISC", "P5V_MISC", "P5V_MISC", "P3V3_FF", "P3V3_FF"]
    IC59_LTC2977_currentSenseShunts =   [0, 0.01 / 2, 0, 0.025 / 2, 0, 0.25 / 2, 0, 0.005 / 2]
    IC26_LTM4700_measurementNames =     ["FPGA 0.85V core 1/4", "FPGA 0.85V core 2/4"]
    IC27_LTM4700_measurementNames =     ["FPGA 0.85V core 3/4", "FPGA 0.85V core 4/4"]



    # Print the raw status of an LTC2977 8-channel PMBus power system manager IC.
    def power_ltc2977_status_raw(self, i2cDevice):
        if self.debugLevel >= 1:
            print(self.prefixDebug + "Reading the status of the power module {0:s} on I2C port {1:d}.".format(i2cDevice.deviceName, i2cDevice.mcuI2C.port))
        ret, data = i2cDevice.read_status()
        if ret:
            self.errorCount += 1
            print(self.prefixError + "Error reading the raw status of the power module {0:s} on I2C port {1:d}!".format(i2cDevice.deviceName, i2cDevice.mcuI2C.port))
            return -1
        print("Status of the power module {0:s} on I2C port {1:d}:".format(i2cDevice.deviceName, i2cDevice.mcuI2C.port))
        print(self.prefixStatus + "{0:18s}: {1:5.2f} degC".format("Temperature", data[0]))
        print(self.prefixStatus + "{0:18s}: {1:5.2f} V".format("V_in", data[1]))
        for channel in range(i2cDevice.hwChannels):
            print(self.prefixStatus + "Channel {0:d}: {1:7s}: {2:5.2f} V".format(channel, "V_out", data[2][channel]))
        return 0



    # Print the status of an LTC2977 8-channel PMBus power system manager IC.
    def power_ltc2977_status(self, i2cDevice, measurementNames, currentSenseShunts):
        if len(measurementNames) != i2cDevice.hwChannels:
            self.errorCount += 1
            print(self.prefixError + "Error reading the status of the power module {0:s} on I2C port {1:d}: {2:d} measurement names must be provided, but only {3:d} were given!".format(i2cDevice.deviceName, i2cDevice.mcuI2C.port, i2cDevice.hwChannels, len(measurementNames)))
            return -1
        if len(currentSenseShunts) != i2cDevice.hwChannels:
            self.errorCount += 1
            print(self.prefixError + "Error reading the status of the power module {0:s} on I2C port {1:d}: {2:d} current sense values must be provided, but only {3:d} were given!".format(i2cDevice.deviceName, i2cDevice.mcuI2C.port, i2cDevice.hwChannels, len(currentSenseShunts)))
            return -1
        if self.debugLevel >= 1:
            print(self.prefixDebug + "Reading the status of the power module {0:s} on I2C port {1:d}.".format(i2cDevice.deviceName, i2cDevice.mcuI2C.port))
        ret, data = i2cDevice.read_status()
        if ret:
            self.errorCount += 1
            print(self.prefixError + "Error reading the status of the power module {0:s} on I2C port {1:d}!".format(i2cDevice.deviceName, i2cDevice.mcuI2C.port))
            return -1
        print("Status of the power module {0:s} on I2C port {1:d}:".format(i2cDevice.deviceName, i2cDevice.mcuI2C.port))
        print(self.prefixStatus + "{0:26s}: {1:5.2f} degC".format("Temperature", data[0]))
        print(self.prefixStatus + "{0:26s}: {1:5.2f} V".format("V_in", data[1]))
        for channel in range(i2cDevice.hwChannels):
            if currentSenseShunts[channel] != 0:
                value = data[2][channel] / currentSenseShunts[channel]
                unit = "A"
            else:
                value = data[2][channel]
                unit = "V"
            print(self.prefixStatus + "{0:d}: {1:23s}: {2:5.2f} {3:s}".format(channel, measurementNames[channel], value, unit))
        return 0



    # Print the raw status of an LTM4700 regulator with digital power system management IC.
    def power_ltm4700_status_raw(self, i2cDevice):
        if self.debugLevel >= 1:
            print(self.prefixDebug + "Reading the status of the power module {0:s} on I2C port {1:d}.".format(i2cDevice.deviceName, i2cDevice.mcuI2C.port))
        ret, data = i2cDevice.read_status()
        if ret:
            self.errorCount += 1
            print(self.prefixError + "Error reading the raw status of the power module {0:s} on I2C port {1:d}!".format(i2cDevice.deviceName, i2cDevice.mcuI2C.port))
            return -1
        print("Status of the power module {0:s} on I2C port {1:d}:".format(i2cDevice.deviceName, i2cDevice.mcuI2C.port))
        # Measurement of the external temperature is not supported on the CM demonstrator.
        #print(self.prefixStatus + "{0:18s}: {1:5.2f} degC".format("Temperature (ext)", data[0]))
        print(self.prefixStatus + "{0:18s}: {1:5.2f} degC".format("Temperature (int)", data[1]))
        print(self.prefixStatus + "{0:18s}: {1:5.2f} V".format("V_in", data[2]))
        # Measurement of the input current is not supported on the CM demonstrator.
        #print(self.prefixStatus + "{0:18s}: {1:5.2f} A".format("I_in", data[3]))
        for channel in range(i2cDevice.hwChannels):
            print(self.prefixStatus + "Channel {0:d}: {1:7s}: {2:5.2f} V".format(channel, "V_out", data[4][channel]))
            print(self.prefixStatus + "Channel {0:d}: {1:7s}: {2:5.2f} A".format(channel, "I_out", data[5][channel]))
        return 0



    # Print the status of an LTM4700 regulator with digital power system management IC.
    def power_ltm4700_status(self, i2cDevice, measurementNames):
        if len(measurementNames) != i2cDevice.hwChannels:
            self.errorCount += 1
            print(self.prefixError + "Error reading the status of the power module {0:s} on I2C port {1:d}: {2:d} measurement names must be provided, but only {3:d} were given!".format(i2cDevice.deviceName, i2cDevice.mcuI2C.port, i2cDevice.hwChannels, len(measurementNames)))
            return -1
        if self.debugLevel >= 1:
            print(self.prefixDebug + "Reading the status of the power module {0:s} on I2C port {1:d}.".format(i2cDevice.deviceName, i2cDevice.mcuI2C.port))
        ret, data = i2cDevice.read_status()
        if ret:
            self.errorCount += 1
            print(self.prefixError + "Error reading the status of the power module {0:s} on I2C port {1:d}!".format(i2cDevice.deviceName, i2cDevice.mcuI2C.port))
            return -1
        print("Status of the power module {0:s} on I2C port {1:d}:".format(i2cDevice.deviceName, i2cDevice.mcuI2C.port))
        # Measurement of the external temperature is not supported on the CM demonstrator.
        #print(self.prefixStatus + "{0:18s}: {1:5.2f} degC".format("Temperature (ext)", data[0]))
        print(self.prefixStatus + "{0:18s}: {1:5.2f} degC".format("Temperature (int)", data[1]))
        print(self.prefixStatus + "{0:18s}: {1:5.2f} V".format("V_in", data[2]))
        # Measurement of the input current is not supported on the CM demonstrator.
        #print(self.prefixStatus + "{0:18s}: {1:5.2f} A".format("I_in", data[3]))
        for channel in range(i2cDevice.hwChannels):
            print(self.prefixStatus + "{0:d}: {1:23s}: {2:5.2f} V".format(channel, measurementNames[channel], data[4][channel]))
            print(self.prefixStatus + "{0:d}: {1:23s}: {2:5.2f} A".format(channel, measurementNames[channel], data[5][channel]))
        return 0



    # Print the raw status of all power modules.
    def power_module_status_raw(self):
        self.power_ltc2977_status_raw(self.i2cDevice_IC58_LTC2977)
        self.power_ltc2977_status_raw(self.i2cDevice_IC59_LTC2977)
        self.power_ltm4700_status_raw(self.i2cDevice_IC26_LTM4700)
        self.power_ltm4700_status_raw(self.i2cDevice_IC27_LTM4700)



    # Print the status of all power modules.
    def power_module_status(self):
        self.power_ltc2977_status(self.i2cDevice_IC58_LTC2977, self.IC58_LTC2977_measurementNames, self.IC58_LTC2977_currentSenseShunts)
        self.power_ltc2977_status(self.i2cDevice_IC59_LTC2977, self.IC59_LTC2977_measurementNames, self.IC59_LTC2977_currentSenseShunts)
        self.power_ltm4700_status(self.i2cDevice_IC26_LTM4700, self.IC26_LTM4700_measurementNames)
        self.power_ltm4700_status(self.i2cDevice_IC27_LTM4700, self.IC27_LTM4700_measurementNames)



    # Calculate the current from the voltage across a shunt resistor by the
    # power module and the shunt resistor value.
    def pm_get_current(self, i2cDevice, i2cDeviceChannel, currentSenseShunt):
        if currentSenseShunt <= 0:
            return -1, -1
        ret, voltage = i2cDevice.read_vout(i2cDeviceChannel)
        if ret:
            self.errorCount += 1
            print(self.prefixError + "Error reading the voltage of channel {0:d} of the power module {1:s} on I2C port {2:d}!".format(i2cDeviceChannel, i2cDevice.deviceName, i2cDevice.mcuI2C.port))
            return -1, -1
        return 0, voltage / currentSenseShunt



    # Detailed power status of the CM.
    def power_status_detail(self):
        if self.debugLevel >= 1:
            print(self.prefixDebug + "Reading the detailed power status of the CM.")
        # IC58: LTC2977 8-channel PMBus power system manager IC (P1V8_FPGA, P1V2_MGT, P0V9_MGT).
        ret, P1V8_FPGA_Voltage  = self.i2cDevice_IC58_LTC2977.read_vout(0)
        ret, P1V8_FPGA_Current  = self.pm_get_current(self.i2cDevice_IC58_LTC2977, 1, self.IC58_LTC2977_currentSenseShunts[1])
        # Channels 2 .. 3 are unused.
        ret, P1V2_MGT_Voltage   = self.i2cDevice_IC58_LTC2977.read_vout(4)
        ret, P1V2_MGT_Current   = self.pm_get_current(self.i2cDevice_IC58_LTC2977, 5, self.IC58_LTC2977_currentSenseShunts[5])
        ret, P0V9_MGT_Voltage   = self.i2cDevice_IC58_LTC2977.read_vout(6)
        ret, P0V9_MGT_Current   = self.pm_get_current(self.i2cDevice_IC58_LTC2977, 7, self.IC58_LTC2977_currentSenseShunts[7])
        # IC59: LTC2977 8-channel PMBus power system manager IC (P1V8_MISC, P3V3_MISC, P5V_MISC, P3V3_FF).
        ret, P1V8_MISC_Voltage  = self.i2cDevice_IC59_LTC2977.read_vout(0)
        ret, P1V8_MISC_Current  = self.pm_get_current(self.i2cDevice_IC59_LTC2977, 1, self.IC59_LTC2977_currentSenseShunts[1])
        ret, P3V3_MISC_Voltage  = self.i2cDevice_IC59_LTC2977.read_vout(2)
        ret, P3V3_MISC_Current  = self.pm_get_current(self.i2cDevice_IC59_LTC2977, 3, self.IC59_LTC2977_currentSenseShunts[3])
        ret, P5V_MISC_Voltage   = self.i2cDevice_IC59_LTC2977.read_vout(4)
        ret, P5V_MISC_Current   = self.pm_get_current(self.i2cDevice_IC59_LTC2977, 5, self.IC59_LTC2977_currentSenseShunts[5])
        ret, P3V3_FF_Voltage    = self.i2cDevice_IC59_LTC2977.read_vout(6)
        ret, P3V3_FF_Current    = self.pm_get_current(self.i2cDevice_IC59_LTC2977, 7, self.IC59_LTC2977_currentSenseShunts[5])
        # IC26: LTM4700 regulator with digital power system management IC (FPGA core voltage).
        ret, fpgaCoreVoltage = self.i2cDevice_IC26_LTM4700.read_vout(0)
        fpgaCoreCurrent = 0
        ret, data = self.i2cDevice_IC26_LTM4700.read_iout(0)
        fpgaCoreCurrent += data
        ret, data = self.i2cDevice_IC26_LTM4700.read_iout(1)
        fpgaCoreCurrent += data
        # IC27: LTM4700 regulator with digital power system management IC (FPGA core voltage).
        ret, data = self.i2cDevice_IC27_LTM4700.read_iout(0)
        fpgaCoreCurrent += data
        ret, data = self.i2cDevice_IC27_LTM4700.read_iout(1)
        fpgaCoreCurrent += data

        # Calculate power.
        fpgaPower = abs(fpgaCoreVoltage     * fpgaCoreCurrent    ) + \
                    abs(P1V8_FPGA_Voltage   * P1V8_FPGA_Current  ) + \
                    abs(P1V2_MGT_Voltage    * P1V2_MGT_Current   ) + \
                    abs(P0V9_MGT_Voltage    * P0V9_MGT_Current   )
        clockMiscPower = abs(P1V8_MISC_Voltage * P1V8_MISC_Current) + abs(P3V3_MISC_Voltage * P3V3_MISC_Current)
        fireflyPower = abs(P3V3_FF_Voltage * P3V3_FF_Current)
        miscPower = abs(P5V_MISC_Voltage * P3V3_FF_Current)

        # Show overview.
        print("VU13P")
        print(self.prefixStatus + "{0:18s}: {1:5.2f} V, {2:5.2f} A".format("0.85V core",        fpgaCoreVoltage,    fpgaCoreCurrent     ))
        print(self.prefixStatus + "{0:18s}: {1:5.2f} V, {2:5.2f} A".format("1.8V IO",           P1V8_FPGA_Voltage,  P1V8_FPGA_Current   ))
        print(self.prefixStatus + "{0:18s}: {1:5.2f} V, {2:5.2f} A".format("1.2V MGT",          P1V2_MGT_Voltage,   P1V2_MGT_Current    ))
        print(self.prefixStatus + "{0:18s}: {1:5.2f} V, {2:5.2f} A".format("0.9V MGT",          P0V9_MGT_Voltage,   P0V9_MGT_Current    ))
        print(self.prefixStatus + "{0:18s}: {1:5.1f} W".format("Total power",  fpgaPower))
        print("Clock / Miscellaneous")
        print(self.prefixStatus + "{0:18s}: {1:5.2f} V, {2:5.2f} A".format("1.8V clock/misc",   P1V8_MISC_Voltage,  P1V8_MISC_Current   ))
        print(self.prefixStatus + "{0:18s}: {1:5.2f} V, {2:5.2f} A".format("3.3V clock/misc",   P3V3_MISC_Voltage,  P3V3_MISC_Current   ))
        print(self.prefixStatus + "{0:18s}: {1:5.1f} W".format("Total power",  clockMiscPower))
        print("FireFly Modules")
        print(self.prefixStatus + "{0:18s}: {1:5.2f} V, {2:5.2f} A".format("3.3V FireFly",      P3V3_FF_Voltage,    P3V3_FF_Current     ))
        print(self.prefixStatus + "{0:18s}: {1:5.1f} W".format("Total power",  fireflyPower))
        print("Miscellaneous")
        print(self.prefixStatus + "{0:18s}: {1:5.2f} V, {2:5.2f} A".format("5.0V",              P5V_MISC_Voltage,   P5V_MISC_Current    ))
        print(self.prefixStatus + "{0:18s}: {1:5.1f} W".format("Total power",  miscPower))

