#!/usr/bin/env python3
#
# File: MdtTp_CM.py
# Auth: M. Fras, Electronics Division, MPI for Physics, Munich
# Mod.: M. Fras, Electronics Division, MPI for Physics, Munich
# Date: 26 Jul 2022
# Rev.: 16 Sep 2022
#
# Python class for accessing the ATLAS MDT Trigger Processor (TP) Command
# Module (CM) Prototype via the TI Tiva TM4C1290 MCU UART.
#



import os
import time
import McuGpio
import McuI2C
import McuSerial
import McuUart
import I2C_DS28CM00
import I2C_LTC2977
import I2C_LTM4700
import I2C_MCP9902
import I2C_PCA9535
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
        self.define_hw()



    # Define the hardware components.
    def define_hw(self):
        # Define the MCU I2C peripherals.
        self.define_hw_i2c()



    # Initialize the hardware components.
    def init_hw(self):
        # Initialize the MCU I2C peripherals.
        self.init_hw_i2c()



    # ===============================================================
    # Auxiliary functions.
    # ===============================================================

    # Extract the integer value from an MCU answer string.
    @classmethod
    def mcu_str2int(cls, mcuStr):
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



    # Read the serial number of the board.
    def serial_number(self):
        if self.debugLevel >= 1:
            print(self.prefixDebug + "Reading the serial number from {0:s}.", self.i2cDevice_IC22_DS28CM00.deviceName)
        ret, deviceFamilyCode, serialNumber, crc, crcError = self.i2cDevice_IC22_DS28CM00.read_all()
        if ret:
            print(self.prefixError + "Error reading the serial number from {0:s}!", self.i2cDevice_IC22_DS28CM00.deviceName)
            return ret
        print("Device family code: 0x{0:02x}".format(deviceFamilyCode))
        print("Serial number: 0x{0:012x}".format(serialNumber))
        print("CRC: 0x{0:02x}".format(crc))
        if crcError:
            self.errorCount += 1
            print(self.prefixError + "CRC error detected!")
            return 1
        return 0

    # Read the serial number of the SM.
    def serial_number_sm(self):
        if self.debugLevel >= 1:
            print(self.prefixDebug + "Reading the serial number from {0:s}.", self.i2cDevice_SM_DS28CM00.deviceName)
        ret, deviceFamilyCode, serialNumber, crc, crcError = self.i2cDevice_SM_DS28CM00.read_all()
        if ret:
            print(self.prefixError + "Error reading the serial number from {0:s}!", self.i2cDevice_SM_DS28CM00.deviceName)
            return ret
        print("Device family code: 0x{0:02x}".format(deviceFamilyCode))
        print("Serial number: 0x{0:012x}".format(serialNumber))
        print("CRC: 0x{0:02x}".format(crc))
        if crcError:
            self.errorCount += 1
            print(self.prefixError + "CRC error detected!")
            return 1
        return 0



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

    # Define the I2C buses and devices.
    def define_hw_i2c(self):
        # Define all I2C buses.
        self.mcuI2C = []
        for i in range(0, self.i2cBusNum):
            self.mcuI2C.append(McuI2C.McuI2C(self.mcuSer, i))
            self.mcuI2C[i].debugLevel = self.debugLevel

        # IC22: DS28CM00 silicon serial number IC.
        # I2C port 4, slave address 0x50.
        self.i2cDevice_IC22_DS28CM00 = I2C_DS28CM00.I2C_DS28CM00(self.mcuI2C[4], 0x50, "IC22 (DS28CM00)")
        self.i2cDevice_IC22_DS28CM00.debugLevel = self.debugLevel

        # S;: DS28CM00 silicon serial number IC.
        # I2C port 7, slave address 0x50.
        self.i2cDevice_SM_DS28CM00 = I2C_DS28CM00.I2C_DS28CM00(self.mcuI2C[7], 0x50, "SM (DS28CM00)")
        self.i2cDevice_SM_DS28CM00.debugLevel = self.debugLevel

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

        # Power modules.
        # IC26: LTM4700 regulator with digital power system management IC (VU13P core voltage).
        self.i2cDevice_IC26_LTM4700 = I2C_LTM4700.I2C_LTM4700(self.mcuI2C[1], 0x40, "IC26 (LTM4700)")
        # IC27: LTM4700 regulator with digital power system management IC (VU13P core voltage).
        self.i2cDevice_IC27_LTM4700 = I2C_LTM4700.I2C_LTM4700(self.mcuI2C[1], 0x41, "IC27 (LTM4700)")
        # IC58: LTC2977 8-channel PMBus power system manager IC (1.8 V FPGA, 1.2 V MGT, 0.9 V MGT).
        self.i2cDevice_IC58_LTC2977 = I2C_LTC2977.I2C_LTC2977(self.mcuI2C[1], 0x5c, "IC58 (LTC2977)")
        # IC59: LTC2977 8-channel PMBus power system manager IC (1.8 V misc, 3.3 V misc, 5.0 V misc, 3.3. V FireFly).
        self.i2cDevice_IC59_LTC2977 = I2C_LTC2977.I2C_LTC2977(self.mcuI2C[1], 0x5d, "IC59 (LTC2977)")

        # Define the I2C clock devices.
        self.i2c_clk_define()

        # Define the I2C I/O expander devices.
        self.i2c_io_exp_define()
 
        # Firefly's
        self.i2cDevice_FF_I2CMUX_0x70 = I2C_PCA9545.I2C_PCA9545(self.mcuI2C[2], 0x70, "FF_MUX_0x70");
        self.i2cDevice_FF_I2CMUX_0x71 = I2C_PCA9545.I2C_PCA9545(self.mcuI2C[2], 0x71, "FF_MUX_0x71");
        self.i2cDevice_FF_I2CMUX_0x72 = I2C_PCA9545.I2C_PCA9545(self.mcuI2C[2], 0x72, "FF_MUX_0x72");
        self.i2cDevice_FF_tx = I2C_FireFly.I2C_FireFly(self.mcuI2C[2], 0x50, "FF_TX", 'tx'); 
        self.i2cDevice_FF_rx = I2C_FireFly.I2C_FireFly(self.mcuI2C[2], 0x54, "FF_RX", 'rx'); 

    # Read FF status
    def read_ff(self, ff):
        iret, temp = self.i2cDevice_FF_tx.read_temperature();
        iret, vcc = self.i2cDevice_FF_tx.read_vcc();
        print("FF%d TX: %d debC %.2f V" % (ff, temp, vcc));
        iret, temp = self.i2cDevice_FF_rx.read_temperature();
        iret, vcc = self.i2cDevice_FF_rx.read_vcc();
        print("FF%d RX: %d degC %.2f V" % (ff,temp, vcc));
    def read_ff_status(self):
        self.i2cDevice_FF_I2CMUX_0x70.disable();
        self.i2cDevice_FF_I2CMUX_0x71.disable();
        self.i2cDevice_FF_I2CMUX_0x72.disable();
        self.i2cDevice_FF_I2CMUX_0x70.set_channels([0]);
        self.read_ff(0);
        self.i2cDevice_FF_I2CMUX_0x70.set_channels([1]);
        self.read_ff(2);
        self.i2cDevice_FF_I2CMUX_0x70.set_channels([2]);
        self.read_ff(4);
        self.i2cDevice_FF_I2CMUX_0x70.set_channels([3]);
        self.read_ff(6);
        self.i2cDevice_FF_I2CMUX_0x70.disable();
        self.i2cDevice_FF_I2CMUX_0x71.set_channels([0]);
        self.read_ff(1);
        self.i2cDevice_FF_I2CMUX_0x71.set_channels([1]);
        self.read_ff(3);
        self.i2cDevice_FF_I2CMUX_0x71.set_channels([2]);
        self.read_ff(5);
        self.i2cDevice_FF_I2CMUX_0x71.set_channels([3]);
        self.read_ff(7);
        self.i2cDevice_FF_I2CMUX_0x71.disable();
        self.i2cDevice_FF_I2CMUX_0x72.set_channels([0]);
        self.read_ff(8);
        self.i2cDevice_FF_I2CMUX_0x72.set_channels([1]);
        self.read_ff(9);
        self.i2cDevice_FF_I2CMUX_0x72.disable();


    # Initialize the I2C buses and devices.
    def init_hw_i2c(self):
        # Reset all active I2C buses.
        for i in self.i2cBusActive:
            self.mcuI2C[i].ms_reset_bus()

        # MCP9902 low-temperature remote diode sensor IC.
        # Set up the configuration registers.
        self.i2cDevice_IC60_MCP9902.write_config_0(0x00)
        self.i2cDevice_IC60_MCP9902.write_config_1(0x00)
        self.i2cDevice_IC61_MCP9902.write_config_0(0x00)
        self.i2cDevice_IC61_MCP9902.write_config_1(0x00)
        self.i2cDevice_IC62_MCP9902.write_config_0(0x00)
        self.i2cDevice_IC62_MCP9902.write_config_1(0x00)

        # Initialize the I2C I/O expander devices.
        self.i2c_io_exp_init()



    # Reset all I2C buses.
    def i2c_reset(self):
        if self.debugLevel >= 1:
            print(self.prefixDebug + "Resetting all I2C buses.")
        for i in self.i2cBusActive:
            self.mcuI2C[i].ms_reset_bus()



    # Detect devices on all I2C buses.
    def i2c_detect_devices(self):
        if self.debugLevel >= 1:
            print(self.prefixDebug + "Detecting devices on all I2C buses.")
        print("Devices found on I2C buses:")
        for i in self.i2cBusActive:
            print("Bus {0:d}: ".format(i), end='')
            ret, devAdr = self.mcuI2C[i].ms_detect_devices()
            if ret:
                print(self.prefixError + "Error detecting devices on I2C bus {0:d}!".format(i))
            for adr in devAdr:
                print(" 0x{0:02x}".format(adr), end='')
            print()



    # Reset I2C multiplexers.
    def i2c_mux_reset(self, resetMask):
        resetMask &= 0x0f   # Only 4 reset signals are available.
        if self.debugLevel >= 1:
            print(self.prefixDebug + "Resetting the I2C bus multiplexers with reset bit mask 0x{0:x}.".format(resetMask))
        # Assert reset.
        cmd = "gpio i2c-reset 0x{0:x}".format(resetMask)
        ret = self.mcu_cmd_raw(cmd)[0]
        # Wait some time.
        time.sleep(0.1)
        # De-assert reset.
        cmd = "gpio i2c-reset 0x0"
        ret |= self.mcu_cmd_raw(cmd)[0]
        if ret:
            print(self.prefixError + "Error resetting the I2C bus multiplexers with reset bit mask 0x{0:x}!".format(resetMask))
        return ret



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
    IC58_LTC2977_currentSenseShunts =   [0, 0.005, 0, 0, 0, 0.003, 0, 0.005]
    IC59_LTC2977_measurementNames =     ["P1V8_MISC", "P1V8_MISC", "P3V3_MISC", "P3V3_MISC", "P5V_MISC", "P5V_MISC", "P3V3_FF", "P3V3_FF"]
    IC59_LTC2977_currentSenseShunts =   [0, 0.01, 0, 0.025, 0, 0.025, 0, 0.005]
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



    # ===============================================================
    # Silicon labs clock ICs.
    # ===============================================================

    # Define the I2C clock devices.
    def i2c_clk_define(self):
        # I2C mux for clock I2C bus:
        # IC36 (PCA9545APW): I2C port 3, slave address 0x70.
        self.i2cDevice_IC36_PCA9545APW = I2C_PCA9545.I2C_PCA9545(self.mcuI2C[3], 0x70, "IC36 (PCA9545APW)")
        self.i2cDevice_IC36_PCA9545APW.debugLevel = self.debugLevel
        # I2C clock devices.
        # IC1 (Si5345A): I2C port 3, slave address 0x68, clock I2C mux port 2.
        self.i2cDevice_IC1_Si5345A = I2C_Si53xx.I2C_Si53xx(self.mcuI2C[3], 0x68, "IC1 (Si5345A)")
        self.i2cDevice_IC1_Si5345A.muxChannel = 2
        self.i2cDevice_IC1_Si5345A.regMapFile = os.path.join("config", "clock", "Pro_Design", "IC1_0x68_100IN0_100_100_100_100_100_100_100_100_NA_FB-Registers.txt")
        self.i2cDevice_IC1_Si5345A.debugLevel = self.debugLevel
        # IC2 (Si5345A): I2C port 3, slave address 0x68, clock I2C mux port 0.
        self.i2cDevice_IC2_Si5345A = I2C_Si53xx.I2C_Si53xx(self.mcuI2C[3], 0x68, "IC2 (Si5345A)")
        self.i2cDevice_IC2_Si5345A.muxChannel = 0
        self.i2cDevice_IC2_Si5345A.regMapFile = os.path.join("config", "clock", "Pro_Design", "IC2_0x68_100IN0_10_400_10_400_10_400_10_400_10_FB-Registers.txt")
        self.i2cDevice_IC2_Si5345A.debugLevel = self.debugLevel
        # IC3 (Si5345A): I2C port 3, slave address 0x69, clock I2C mux port 0.
        self.i2cDevice_IC3_Si5345A = I2C_Si53xx.I2C_Si53xx(self.mcuI2C[3], 0x69, "IC3 (Si5345A)")
        self.i2cDevice_IC3_Si5345A.muxChannel = 0
        self.i2cDevice_IC3_Si5345A.regMapFile = os.path.join("config", "clock", "Pro_Design", "IC3_0x69_100IN0_10_400_10_400_10_400_10_400_10_FB-Registers.txt")
        self.i2cDevice_IC3_Si5345A.debugLevel = self.debugLevel
        # IC4 (Si5345A): I2C port 3, slave address 0x6a, clock I2C mux port 0.
        self.i2cDevice_IC4_Si5345A = I2C_Si53xx.I2C_Si53xx(self.mcuI2C[3], 0x6a, "IC4 (Si5345A)")
        self.i2cDevice_IC4_Si5345A.muxChannel = 0
        self.i2cDevice_IC4_Si5345A.regMapFile = os.path.join("config", "clock", "Pro_Design", "IC4_0x6A_100IN0_10_400_10_400_10_400_NA_NA_NA_FB-Registers.txt")
        self.i2cDevice_IC4_Si5345A.debugLevel = self.debugLevel
        # IC5 (Si5345A): I2C port 3, slave address 0x6b, clock I2C mux port 0.
        self.i2cDevice_IC5_Si5345A = I2C_Si53xx.I2C_Si53xx(self.mcuI2C[3], 0x6b, "IC5 (Si5345A)")
        self.i2cDevice_IC5_Si5345A.muxChannel = 0
        self.i2cDevice_IC5_Si5345A.regMapFile = os.path.join("config", "clock", "Pro_Design", "IC5_0x6B_100IN0_10_400_10_400_10_400_NA_NA_NA_FB-Registers.txt")
        self.i2cDevice_IC5_Si5345A.debugLevel = self.debugLevel
        # IC6 (Si5345A): I2C port 3, slave address 0x68, clock I2C mux port 1.
        self.i2cDevice_IC6_Si5345A = I2C_Si53xx.I2C_Si53xx(self.mcuI2C[3], 0x68, "IC6 (Si5345A)")
        self.i2cDevice_IC6_Si5345A.muxChannel = 1
        self.i2cDevice_IC6_Si5345A.regMapFile = os.path.join("config", "clock", "Pro_Design", "IC6_0x68_100IN0_10_400_10_400_10_400_10_400_10_FB-Registers.txt")
        self.i2cDevice_IC6_Si5345A.debugLevel = self.debugLevel
        # IC7 (Si5345A): I2C port 3, slave address 0x69, clock I2C mux port 1.
        self.i2cDevice_IC7_Si5345A = I2C_Si53xx.I2C_Si53xx(self.mcuI2C[3], 0x69, "IC7 (Si5345A)")
        self.i2cDevice_IC7_Si5345A.muxChannel = 1
        self.i2cDevice_IC7_Si5345A.regMapFile = os.path.join("config", "clock", "Pro_Design", "IC7_0x69_100IN0_10_400_10_400_10_400_10_400_10_FB-Registers.txt")
        self.i2cDevice_IC7_Si5345A.debugLevel = self.debugLevel
        # IC8 (Si5345A): I2C port 3, slave address 0x6a, clock I2C mux port 1.
        self.i2cDevice_IC8_Si5345A = I2C_Si53xx.I2C_Si53xx(self.mcuI2C[3], 0x6a, "IC8 (Si5345A)")
        self.i2cDevice_IC8_Si5345A.muxChannel = 1
        self.i2cDevice_IC8_Si5345A.regMapFile = os.path.join("config", "clock", "Pro_Design", "IC8_0x6A_100IN0_10_400_10_400_10_400_NA_NA_NA_FB-Registers.txt")
        self.i2cDevice_IC8_Si5345A.debugLevel = self.debugLevel
        # IC9 (Si5345A): I2C port 3, slave address 0x6b, clock I2C mux port 1.
        self.i2cDevice_IC9_Si5345A = I2C_Si53xx.I2C_Si53xx(self.mcuI2C[3], 0x6b, "IC9 (Si5345A)")
        self.i2cDevice_IC9_Si5345A.muxChannel = 1
        self.i2cDevice_IC9_Si5345A.regMapFile = os.path.join("config", "clock", "Pro_Design", "IC9_0x6B_100IN0_10_400_10_400_10_400_NA_NA_NA_FB-Registers.txt")
        self.i2cDevice_IC9_Si5345A.debugLevel = self.debugLevel
        # IC10 (Si5345A): I2C port 3, slave address 0x69, clock I2C mux port 2.
        self.i2cDevice_IC10_Si5345A = I2C_Si53xx.I2C_Si53xx(self.mcuI2C[3], 0x69, "IC10 (Si5345A)")
        self.i2cDevice_IC10_Si5345A.muxChannel = 2
        self.i2cDevice_IC10_Si5345A.regMapFile = os.path.join("config", "clock", "Pro_Design", "IC10_0x69_100IN1_NA_NA_200_NA_NA_NA_NA_NA_NA_FB-Registers.txt")
        self.i2cDevice_IC10_Si5345A.debugLevel = self.debugLevel
        # IC12 (Si5345A): I2C port 3, slave address 0x6a, clock I2C mux port 2.
        self.i2cDevice_IC12_Si5345A = I2C_Si53xx.I2C_Si53xx(self.mcuI2C[3], 0x6a, "IC12 (Si5345A)")
        self.i2cDevice_IC12_Si5345A.muxChannel = 2
        self.i2cDevice_IC12_Si5345A.regMapFile = os.path.join("config", "clock", "Pro_Design", "IC12_0x6A_100IN2_10_400_NA_FB-Registers.txt")
        self.i2cDevice_IC12_Si5345A.debugLevel = self.debugLevel



    # Program a single Silicon Labs clock IC from a register map file.
    def clk_prog_device_file(self, i2cDevice):
        i2cDevice.debugLevel = self.debugLevel
        muxChannel = i2cDevice.muxChannel
        if self.debugLevel >= 1:
            print(self.prefixDebug + "Setting I2C mux for clock chips {0:s} to channel {1:d}.".format(self.i2cDevice_IC36_PCA9545APW.deviceName, muxChannel))
        self.i2cDevice_IC36_PCA9545APW.set_channels([muxChannel])
        self.i2cDevice_IC36_PCA9545APW.debugLevel = self.debugLevel
        regMapFile = i2cDevice.regMapFile
        print("Initialitzing {0:s} on I2C port {1:d} with register map file `{2:s}'.".\
            format(i2cDevice.deviceName, i2cDevice.mcuI2C.port, regMapFile))
        i2cDevice.debugLevel = self.debugLevel
        i2cDevice.config_file(regMapFile)



    # Program a single Silicon Labs clock IC from a register map file by its name.
    def clk_prog_device_by_name(self, clkDevName, regMapFile):
        clkDeviceList = [self.i2cDevice_IC1_Si5345A,
                         self.i2cDevice_IC2_Si5345A,
                         self.i2cDevice_IC3_Si5345A,
                         self.i2cDevice_IC4_Si5345A,
                         self.i2cDevice_IC5_Si5345A,
                         self.i2cDevice_IC6_Si5345A,
                         self.i2cDevice_IC7_Si5345A,
                         self.i2cDevice_IC8_Si5345A,
                         self.i2cDevice_IC9_Si5345A,
                         self.i2cDevice_IC10_Si5345A,
                         self.i2cDevice_IC12_Si5345A]
        clkDevice = None
        for dev in clkDeviceList:
            if clkDevName.lower() == dev.deviceName.split(' ')[0].lower():
                clkDevice = dev
                clkDevice.regMapFile = regMapFile
        if not clkDevice:
            print(self.prefixError + "Clock device '{0:s}' not valid!".format(clkDevName))
            print(self.prefixError + "Valid clock devices: ", end='')
            for dev in clkDeviceList:
                print(dev.deviceName.split(' ')[0] + " ", end='')
            print()
            return -1
        self.clk_prog_device_file(clkDevice)
        return 0



    # Program all clock devices.
    def clk_prog_all(self):
        if self.debugLevel >= 1:
            print(self.prefixDebug + "Initialitzing all clock chips.")
        self.clk_prog_device_file(self.i2cDevice_IC1_Si5345A)
        self.clk_prog_device_file(self.i2cDevice_IC2_Si5345A)
        self.clk_prog_device_file(self.i2cDevice_IC3_Si5345A)
        self.clk_prog_device_file(self.i2cDevice_IC4_Si5345A)
        self.clk_prog_device_file(self.i2cDevice_IC5_Si5345A)
        self.clk_prog_device_file(self.i2cDevice_IC6_Si5345A)
        self.clk_prog_device_file(self.i2cDevice_IC7_Si5345A)
        self.clk_prog_device_file(self.i2cDevice_IC8_Si5345A)
        self.clk_prog_device_file(self.i2cDevice_IC9_Si5345A)
        self.clk_prog_device_file(self.i2cDevice_IC10_Si5345A)
        self.clk_prog_device_file(self.i2cDevice_IC12_Si5345A)

    # Program a single Silicon Labs clock IC from a register map file.
    def clk_print_status(self, i2cDevice):
        i2cDevice.debugLevel = self.debugLevel
        muxChannel = i2cDevice.muxChannel
        if self.debugLevel >= 1:
            print(self.prefixDebug + "Setting I2C mux for clock chips {0:s} to channel {1:d}.".format(self.i2cDevice_IC36_PCA9545APW.deviceName, muxChannel))
        self.i2cDevice_IC36_PCA9545APW.set_channels([muxChannel])
        self.i2cDevice_IC36_PCA9545APW.debugLevel = self.debugLevel
        i2cDevice.debugLevel = self.debugLevel
        ret, status = i2cDevice.print_status_str()
        if ret:
            print("Failed reading status of {0:s} on I2C port {1:d} ".\
            format(i2cDevice.deviceName, i2cDevice.mcuI2C.port))
        else:
            print("reading status of {0:s} on I2C port {1:d} is {}".\
            format(i2cDevice.deviceName, i2cDevice.mcuI2C.port, status))

    def clk_print_status_all(self):
        if self.debugLevel >= 1:
            print(self.prefixDebug + "printing status for all clock chips.")
        self.clk_print_status(self.i2cDevice_IC1_Si5345A)
        self.clk_print_status(self.i2cDevice_IC2_Si5345A)
        self.clk_print_status(self.i2cDevice_IC3_Si5345A)
        self.clk_print_status(self.i2cDevice_IC4_Si5345A)
        self.clk_print_status(self.i2cDevice_IC5_Si5345A)
        self.clk_print_status(self.i2cDevice_IC6_Si5345A)
        self.clk_print_status(self.i2cDevice_IC7_Si5345A)
        self.clk_print_status(self.i2cDevice_IC8_Si5345A)
        self.clk_print_status(self.i2cDevice_IC9_Si5345A)
        self.clk_print_status(self.i2cDevice_IC10_Si5345A)
        self.clk_print_status(self.i2cDevice_IC12_Si5345A)

    # ===============================================================
    # I2C I/O expander devices.
    # ===============================================================

    # Define the I2C I/O expander devices.
    def i2c_io_exp_define(self):
        # I2C I/O expander devices.
        # IC39 (PCA9535BS): I2C port 3, slave address 0x21.
        self.i2cDevice_IC39_PCA9535BS = I2C_PCA9535.I2C_PCA9535(self.mcuI2C[3], 0x21, "IC39 (PCA9535BS)")
        self.i2cDevice_IC39_PCA9535BS.debugLevel = self.debugLevel
        self.i2cDevice_IC39_PCA9535BS.ioMap = [
            # signal name                   input / output                            default   pol.    comment
            ["CLK_EXT_DBG_CLEAN_nRST",      self.i2cDevice_IC39_PCA9535BS.hwIoOutput,   1,      0,      ""],
            ["CLK_EXT_DBG_CLEAN_FRQTBL",    self.i2cDevice_IC39_PCA9535BS.hwIoOutput,   0,      0,      ""],
            ["CLK_EXT_DBG_CLEAN_FRQSEL0",   self.i2cDevice_IC39_PCA9535BS.hwIoOutput,   0,      0,      ""],
            ["CLK_EXT_DBG_CLEAN_FRQSEL1",   self.i2cDevice_IC39_PCA9535BS.hwIoOutput,   0,      0,      ""],
            ["CLK_EXT_DBG_CLEAN_FRQSEL2",   self.i2cDevice_IC39_PCA9535BS.hwIoOutput,   0,      0,      ""],
            ["CLK_EXT_DBG_CLEAN_FRQSEL3",   self.i2cDevice_IC39_PCA9535BS.hwIoOutput,   0,      0,      ""],
            ["CLK_EXT_DBG_CLEAN_BWSEL1",    self.i2cDevice_IC39_PCA9535BS.hwIoOutput,   0,      0,      ""],
            ["CLK_EXT_DBG_CLEAN_BWSEL0",    self.i2cDevice_IC39_PCA9535BS.hwIoOutput,   0,      0,      ""],
            ["CLK_EXT_DBG_CLEAN_LOS",       self.i2cDevice_IC39_PCA9535BS.hwIoInput,    0,      0,      ""],
            ["CLK_EXT_DBG_CLEAN_LOL",       self.i2cDevice_IC39_PCA9535BS.hwIoInput,    0,      0,      ""],
            ["",                            self.i2cDevice_IC39_PCA9535BS.hwIoInput,    0,      0,      ""],
            ["",                            self.i2cDevice_IC39_PCA9535BS.hwIoInput,    0,      0,      ""],
            ["",                            self.i2cDevice_IC39_PCA9535BS.hwIoInput,    0,      0,      ""],
            ["",                            self.i2cDevice_IC39_PCA9535BS.hwIoInput,    0,      0,      ""],
            ["CLK_EXT_DBG_CLEAN_INC",       self.i2cDevice_IC39_PCA9535BS.hwIoOutput,   0,      0,      ""],
            ["CLK_EXT_DBG_CLEAN_DEC",       self.i2cDevice_IC39_PCA9535BS.hwIoOutput,   0,      0,      ""]
        ]
        # IC40 (PCA9535BS): I2C port 3, slave address 0x23(!).
        self.i2cDevice_IC40_PCA9535BS = I2C_PCA9535.I2C_PCA9535(self.mcuI2C[3], 0x23, "IC40 (PCA9535BS)")
        self.i2cDevice_IC40_PCA9535BS.debugLevel = self.debugLevel
        self.i2cDevice_IC40_PCA9535BS.ioMap = [
            # signal name                   input / output                            default   pol.    comment
            ["CLK_FF_135_0_INTRb",          self.i2cDevice_IC40_PCA9535BS.hwIoInput,    0,      0,      ""],
            ["CLK_FF_135_0_RSTb",           self.i2cDevice_IC40_PCA9535BS.hwIoOutput,   1,      0,      ""],
            ["CLK_FF_135_0_LOLb",           self.i2cDevice_IC40_PCA9535BS.hwIoInput,    0,      0,      ""],
            ["",                            self.i2cDevice_IC40_PCA9535BS.hwIoInput,    0,      0,      ""],
            ["CLK_FF_135_1_INTRb",          self.i2cDevice_IC40_PCA9535BS.hwIoInput,    0,      0,      ""],
            ["CLK_FF_135_1_RSTb",           self.i2cDevice_IC40_PCA9535BS.hwIoOutput,   1,      0,      ""],
            ["CLK_FF_135_1_LOLb",           self.i2cDevice_IC40_PCA9535BS.hwIoInput,    0,      0,      ""],
            ["",                            self.i2cDevice_IC40_PCA9535BS.hwIoInput,    0,      0,      ""],
            ["CLK_FF_79_0_INTRb",           self.i2cDevice_IC40_PCA9535BS.hwIoInput,    0,      0,      ""],
            ["CLK_FF_79_0_RSTb",            self.i2cDevice_IC40_PCA9535BS.hwIoOutput,   1,      0,      ""],
            ["CLK_FF_79_0_LOLb",            self.i2cDevice_IC40_PCA9535BS.hwIoInput,    0,      0,      ""],
            ["",                            self.i2cDevice_IC40_PCA9535BS.hwIoInput,    0,      0,      ""],
            ["CLK_FF_79_1_INTRb",           self.i2cDevice_IC40_PCA9535BS.hwIoInput,    0,      0,      ""],
            ["CLK_FF_79_1_RSTb",            self.i2cDevice_IC40_PCA9535BS.hwIoOutput,   1,      0,      ""],
            ["CLK_FF_79_1_LOLb",            self.i2cDevice_IC40_PCA9535BS.hwIoInput,    0,      0,      ""],
            ["",                            self.i2cDevice_IC40_PCA9535BS.hwIoInput,    0,      0,      ""]
        ]
        # IC41 (PCA9535BS): I2C port 3, slave address 0x22(!).
        self.i2cDevice_IC41_PCA9535BS = I2C_PCA9535.I2C_PCA9535(self.mcuI2C[3], 0x22, "IC41 (PCA9535BS)")
        self.i2cDevice_IC41_PCA9535BS.debugLevel = self.debugLevel
        self.i2cDevice_IC41_PCA9535BS.ioMap = [
            # signal name                   input / output                            default   pol.    comment
            ["CLK_FF_024_0_INTRb",          self.i2cDevice_IC41_PCA9535BS.hwIoInput,    0,      0,      ""],
            ["CLK_FF_024_0_RSTb",           self.i2cDevice_IC41_PCA9535BS.hwIoOutput,   1,      0,      ""],
            ["CLK_FF_024_0_LOLb",           self.i2cDevice_IC41_PCA9535BS.hwIoInput,    0,      0,      ""],
            ["",                            self.i2cDevice_IC41_PCA9535BS.hwIoInput,    0,      0,      ""],
            ["CLK_FF_024_1_INTRb",          self.i2cDevice_IC41_PCA9535BS.hwIoInput,    0,      0,      ""],
            ["CLK_FF_024_1_RSTb",           self.i2cDevice_IC41_PCA9535BS.hwIoOutput,   1,      0,      ""],
            ["CLK_FF_024_1_LOLb",           self.i2cDevice_IC41_PCA9535BS.hwIoInput,    0,      0,      ""],
            ["",                            self.i2cDevice_IC41_PCA9535BS.hwIoInput,    0,      0,      ""],
            ["CLK_FF_68_0_INTRb",           self.i2cDevice_IC41_PCA9535BS.hwIoInput,    0,      0,      ""],
            ["CLK_FF_68_0_RSTb",            self.i2cDevice_IC41_PCA9535BS.hwIoOutput,   1,      0,      ""],
            ["CLK_FF_68_0_LOLb",            self.i2cDevice_IC41_PCA9535BS.hwIoInput,    0,      0,      ""],
            ["",                            self.i2cDevice_IC41_PCA9535BS.hwIoInput,    0,      0,      ""],
            ["CLK_FF_68_1_INTRb",           self.i2cDevice_IC41_PCA9535BS.hwIoInput,    0,      0,      ""],
            ["CLK_FF_68_1_RSTb",            self.i2cDevice_IC41_PCA9535BS.hwIoOutput,   1,      0,      ""],
            ["CLK_FF_68_1_LOLb",            self.i2cDevice_IC41_PCA9535BS.hwIoInput,    0,      0,      ""],
            ["",                            self.i2cDevice_IC41_PCA9535BS.hwIoInput,    0,      0,      ""]
        ]
        # IC42 (PCA9535BS): I2C port 3, slave address 0x24.
        self.i2cDevice_IC42_PCA9535BS = I2C_PCA9535.I2C_PCA9535(self.mcuI2C[3], 0x24, "IC42 (PCA9535BS)")
        self.i2cDevice_IC42_PCA9535BS.debugLevel = self.debugLevel
        self.i2cDevice_IC42_PCA9535BS.ioMap = [
            # signal name                   input / output                            default   pol.    comment
            ["FF_CLK_INTRb",                self.i2cDevice_IC42_PCA9535BS.hwIoInput,    0,      0,      ""],
            ["FF_CLK_RSTb",                 self.i2cDevice_IC42_PCA9535BS.hwIoOutput,   1,      0,      ""],
            ["FF_CLK_LOLb",                 self.i2cDevice_IC42_PCA9535BS.hwIoInput,    0,      0,      ""],
            ["",                            self.i2cDevice_IC42_PCA9535BS.hwIoInput,    0,      0,      ""],
            ["CLK_FF_TD_0_INTRb",           self.i2cDevice_IC42_PCA9535BS.hwIoInput,    0,      0,      ""],
            ["CLK_FF_TD_0_RSTb",            self.i2cDevice_IC42_PCA9535BS.hwIoOutput,   1,      0,      ""],
            ["CLK_FF_TD_0_LOLb",            self.i2cDevice_IC42_PCA9535BS.hwIoInput,    0,      0,      ""],
            ["",                            self.i2cDevice_IC42_PCA9535BS.hwIoInput,    0,      0,      ""],
            ["SM_INTRb",                    self.i2cDevice_IC42_PCA9535BS.hwIoInput,    0,      0,      ""],
            ["SM_RSTb",                     self.i2cDevice_IC42_PCA9535BS.hwIoOutput,   1,      0,      ""],
            ["SM_LOLb",                     self.i2cDevice_IC42_PCA9535BS.hwIoInput,    0,      0,      ""],
            ["SM_LOSb",                     self.i2cDevice_IC42_PCA9535BS.hwIoInput,    0,      0,      ""],
            ["",                            self.i2cDevice_IC42_PCA9535BS.hwIoInput,    0,      0,      ""],
            ["",                            self.i2cDevice_IC42_PCA9535BS.hwIoInput,    0,      0,      ""],
            ["",                            self.i2cDevice_IC42_PCA9535BS.hwIoInput,    0,      0,      ""],
            ["",                            self.i2cDevice_IC42_PCA9535BS.hwIoInput,    0,      0,      ""]
        ]
        # IC43 (PCA9535BS): I2C port 5, slave address 0x20.
        self.i2cDevice_IC43_PCA9535BS = I2C_PCA9535.I2C_PCA9535(self.mcuI2C[5], 0x20, "IC43 (PCA9535BS)")
        self.i2cDevice_IC43_PCA9535BS.debugLevel = self.debugLevel
        self.i2cDevice_IC43_PCA9535BS.ioMap = [
            # signal name                   input / output                            default   pol.    comment
            ["FF0_TX_PRESENTL",             self.i2cDevice_IC43_PCA9535BS.hwIoInput,    0,      0,      ""],
            ["FF0_TX_INTL",                 self.i2cDevice_IC43_PCA9535BS.hwIoInput,    0,      0,      ""],
            ["FF0_TX_ResetL",               self.i2cDevice_IC43_PCA9535BS.hwIoOutput,   1,      0,      ""],
            ["FF0_RX_PRESENTL",             self.i2cDevice_IC43_PCA9535BS.hwIoInput,    0,      0,      ""],
            ["FF0_RX_INTL",                 self.i2cDevice_IC43_PCA9535BS.hwIoInput,    0,      0,      ""],
            ["FF0_RX_ResetL",               self.i2cDevice_IC43_PCA9535BS.hwIoOutput,   1,      0,      ""],
            ["FF2_TX_PRESENTL",             self.i2cDevice_IC43_PCA9535BS.hwIoInput,    0,      0,      ""],
            ["FF2_TX_INTL",                 self.i2cDevice_IC43_PCA9535BS.hwIoInput,    0,      0,      ""],
            ["FF2_TX_ResetL",               self.i2cDevice_IC43_PCA9535BS.hwIoOutput,   1,      0,      ""],
            ["FF2_RX_PRESENTL",             self.i2cDevice_IC43_PCA9535BS.hwIoInput,    0,      0,      ""],
            ["FF2_RX_INTL",                 self.i2cDevice_IC43_PCA9535BS.hwIoInput,    0,      0,      ""],
            ["FF2_RX_ResetL",               self.i2cDevice_IC43_PCA9535BS.hwIoOutput,   1,      0,      ""],
            ["FF4_TX_PRESENTL",             self.i2cDevice_IC43_PCA9535BS.hwIoInput,    0,      0,      ""],
            ["FF4_TX_INTL",                 self.i2cDevice_IC43_PCA9535BS.hwIoInput,    0,      0,      ""],
            ["FF4_TX_ResetL",               self.i2cDevice_IC43_PCA9535BS.hwIoOutput,   1,      0,      ""],
            ["",                            self.i2cDevice_IC43_PCA9535BS.hwIoInput,    0,      0,      ""]
        ]
        # IC44 (PCA9535BS): I2C port 5, slave address 0x21.
        self.i2cDevice_IC44_PCA9535BS = I2C_PCA9535.I2C_PCA9535(self.mcuI2C[5], 0x21, "IC44 (PCA9535BS)")
        self.i2cDevice_IC44_PCA9535BS.debugLevel = self.debugLevel
        self.i2cDevice_IC44_PCA9535BS.ioMap = [
            # signal name                   input / output                            default   pol.    comment
            ["FF4_RX_PRESENTL",             self.i2cDevice_IC44_PCA9535BS.hwIoInput,    0,      0,      ""],
            ["FF4_RX_INTL",                 self.i2cDevice_IC44_PCA9535BS.hwIoInput,    0,      0,      ""],
            ["FF4_RX_ResetL",               self.i2cDevice_IC44_PCA9535BS.hwIoOutput,   1,      0,      ""],
            ["FF6_TX_PRESENTL",             self.i2cDevice_IC44_PCA9535BS.hwIoInput,    0,      0,      ""],
            ["FF6_TX_INTL",                 self.i2cDevice_IC44_PCA9535BS.hwIoInput,    0,      0,      ""],
            ["FF6_TX_ResetL",               self.i2cDevice_IC44_PCA9535BS.hwIoOutput,   1,      0,      ""],
            ["FF6_RX_PRESENTL",             self.i2cDevice_IC44_PCA9535BS.hwIoInput,    0,      0,      ""],
            ["FF6_RX_INTL",                 self.i2cDevice_IC44_PCA9535BS.hwIoInput,    0,      0,      ""],
            ["FF6_RX_ResetL",               self.i2cDevice_IC44_PCA9535BS.hwIoOutput,   1,      0,      ""],
            ["FF8_TX_PRESENTL",             self.i2cDevice_IC44_PCA9535BS.hwIoInput,    0,      0,      ""],
            ["FF8_TX_INTL",                 self.i2cDevice_IC44_PCA9535BS.hwIoInput,    0,      0,      ""],
            ["FF8_TX_ResetL",               self.i2cDevice_IC44_PCA9535BS.hwIoOutput,   1,      0,      ""],
            ["FF8_RX_PRESENTL",             self.i2cDevice_IC44_PCA9535BS.hwIoInput,    0,      0,      ""],
            ["FF8_RX_INTL",                 self.i2cDevice_IC44_PCA9535BS.hwIoInput,    0,      0,      ""],
            ["FF8_RX_ResetL",               self.i2cDevice_IC44_PCA9535BS.hwIoOutput,   1,      0,      ""],
            ["",                            self.i2cDevice_IC44_PCA9535BS.hwIoInput,    0,      0,      ""]
        ]
        # IC45 (PCA9535BS): I2C port 5, slave address 0x22.
        self.i2cDevice_IC45_PCA9535BS = I2C_PCA9535.I2C_PCA9535(self.mcuI2C[5], 0x22, "IC45 (PCA9535BS)")
        self.i2cDevice_IC45_PCA9535BS.debugLevel = self.debugLevel
        self.i2cDevice_IC45_PCA9535BS.ioMap = [
            # signal name                   input / output                            default   pol.    comment
            ["FF1_TX_PRESENTL",             self.i2cDevice_IC45_PCA9535BS.hwIoInput,    0,      0,      ""],
            ["FF1_TX_INTL",                 self.i2cDevice_IC45_PCA9535BS.hwIoInput,    0,      0,      ""],
            ["FF1_TX_ResetL",               self.i2cDevice_IC45_PCA9535BS.hwIoOutput,   1,      0,      ""],
            ["FF1_RX_PRESENTL",             self.i2cDevice_IC45_PCA9535BS.hwIoInput,    0,      0,      ""],
            ["FF1_RX_INTL",                 self.i2cDevice_IC45_PCA9535BS.hwIoInput,    0,      0,      ""],
            ["FF1_RX_ResetL",               self.i2cDevice_IC45_PCA9535BS.hwIoOutput,   1,      0,      ""],
            ["FF3_TX_PRESENTL",             self.i2cDevice_IC45_PCA9535BS.hwIoInput,    0,      0,      ""],
            ["FF3_TX_INTL",                 self.i2cDevice_IC45_PCA9535BS.hwIoInput,    0,      0,      ""],
            ["FF3_TX_ResetL",               self.i2cDevice_IC45_PCA9535BS.hwIoOutput,   1,      0,      ""],
            ["FF3_RX_PRESENTL",             self.i2cDevice_IC45_PCA9535BS.hwIoInput,    0,      0,      ""],
            ["FF3_RX_INTL",                 self.i2cDevice_IC45_PCA9535BS.hwIoInput,    0,      0,      ""],
            ["FF3_RX_ResetL",               self.i2cDevice_IC45_PCA9535BS.hwIoOutput,   1,      0,      ""],
            ["FF5_TX_PRESENTL",             self.i2cDevice_IC45_PCA9535BS.hwIoInput,    0,      0,      ""],
            ["FF5_TX_INTL",                 self.i2cDevice_IC45_PCA9535BS.hwIoInput,    0,      0,      ""],
            ["FF5_TX_ResetL",               self.i2cDevice_IC45_PCA9535BS.hwIoOutput,   1,      0,      ""],
            ["",                            self.i2cDevice_IC45_PCA9535BS.hwIoInput,    0,      0,      ""]
        ]
        # IC46 (PCA9535BS): I2C port 5, slave address 0x23.
        self.i2cDevice_IC46_PCA9535BS = I2C_PCA9535.I2C_PCA9535(self.mcuI2C[5], 0x23, "IC46 (PCA9535BS)")
        self.i2cDevice_IC46_PCA9535BS.debugLevel = self.debugLevel
        self.i2cDevice_IC46_PCA9535BS.ioMap = [
            # signal name                   input / output                            default   pol.    comment
            ["FF5_RX_PRESENTL",             self.i2cDevice_IC46_PCA9535BS.hwIoInput,    0,      0,      ""],
            ["FF5_RX_INTL",                 self.i2cDevice_IC46_PCA9535BS.hwIoInput,    0,      0,      ""],
            ["FF5_RX_ResetL",               self.i2cDevice_IC46_PCA9535BS.hwIoOutput,   1,      0,      ""],
            ["FF7_TX_PRESENTL",             self.i2cDevice_IC46_PCA9535BS.hwIoInput,    0,      0,      ""],
            ["FF7_TX_INTL",                 self.i2cDevice_IC46_PCA9535BS.hwIoInput,    0,      0,      ""],
            ["FF7_TX_ResetL",               self.i2cDevice_IC46_PCA9535BS.hwIoOutput,   1,      0,      ""],
            ["FF7_RX_PRESENTL",             self.i2cDevice_IC46_PCA9535BS.hwIoInput,    0,      0,      ""],
            ["FF7_RX_INTL",                 self.i2cDevice_IC46_PCA9535BS.hwIoInput,    0,      0,      ""],
            ["FF7_RX_ResetL",               self.i2cDevice_IC46_PCA9535BS.hwIoOutput,   1,      0,      ""],
            ["FF9_TX_PRESENTL",             self.i2cDevice_IC46_PCA9535BS.hwIoInput,    0,      0,      ""],
            ["FF9_TX_INTL",                 self.i2cDevice_IC46_PCA9535BS.hwIoInput,    0,      0,      ""],
            ["FF9_TX_ResetL",               self.i2cDevice_IC46_PCA9535BS.hwIoOutput,   1,      0,      ""],
            ["FF9_RX_PRESENTL",             self.i2cDevice_IC46_PCA9535BS.hwIoInput,    0,      0,      ""],
            ["FF9_RX_INTL",                 self.i2cDevice_IC46_PCA9535BS.hwIoInput,    0,      0,      ""],
            ["FF9_RX_ResetL",               self.i2cDevice_IC46_PCA9535BS.hwIoOutput,   1,      0,      ""],
            ["",                            self.i2cDevice_IC46_PCA9535BS.hwIoInput,    0,      0,      ""]
        ]

        # List of all I2C I/O expander devices.
        self.i2cIOExpDevs = [
            self.i2cDevice_IC39_PCA9535BS,
            self.i2cDevice_IC40_PCA9535BS,
            self.i2cDevice_IC41_PCA9535BS,
            self.i2cDevice_IC42_PCA9535BS,
            self.i2cDevice_IC43_PCA9535BS,
            self.i2cDevice_IC44_PCA9535BS,
            self.i2cDevice_IC45_PCA9535BS,
            self.i2cDevice_IC46_PCA9535BS
        ]
        return 0



    # Initialize the I2C I/O expander devices.
    def i2c_io_exp_init(self):
        # Load the default setup for all I2C I/O expander devices.
        ret = self.i2c_io_exp_setup_default()
        return ret



    # Load the default setup for all I2C I/O expander devices.
    def i2c_io_exp_setup_default(self):
        for dev in self.i2cIOExpDevs:
            regConfig = 0
            regOutput = 0
            regPolarity = 0
            # Assemble the output, polarity inversion and configuration registers.
            for ioIdx, ioMap in enumerate(dev.ioMap):
                regConfig   |= (ioMap[1] & 0x1) << ioIdx    # Configuration register.
                regOutput   |= (ioMap[2] & 0x1) << ioIdx    # Output register.
                regPolarity |= (ioMap[3] & 0x1) << ioIdx    # Polarity inversion register.
            # Load the settings into the device.
            if self.debugLevel >= 2:
                print(self.prefixDebug + "Setting up the I2C I/O expander {0:s}:".format(dev.deviceName))
                print(self.prefixDebug + "    Configuration register      : 0x{0:04x}".format(regConfig))
                print(self.prefixDebug + "    Output register             : 0x{0:04x}".format(regOutput))
                print(self.prefixDebug + "    Polarity inversion register : 0x{0:04x}".format(regPolarity))
            dev.write_config(regConfig)
            dev.write_output(regOutput)
            dev.write_polarity(regPolarity)
        return 0



    # Get the I2C I//O expander device and the I/O number from the signal name.
    def i2c_io_exp_signal2dev_io(self, signalName):
        if self.debugLevel >= 2:
            print(self.prefixDebug + "Getting the I2C I/O expander device and the I/O number from the signal name `" + signalName + "'.")
        for dev in self.i2cIOExpDevs:
            for ioIdx, ioMap in enumerate(dev.ioMap):
                if ioMap[0] == signalName:
                    return 0, dev, ioIdx
        print(self.prefixError + "Signal name `{0:s}' not valid!".format(signalName))
        return 1, None, -1



    # Get the status of all I2C I/O expander devices:
    # - input level
    # - configuration register
    # - output register
    # - polarity inversion register
    def i2c_io_exp_get_status_all(self):
        if self.debugLevel >= 1:
            print(self.prefixDebug + "Reading the status of all I2C I/O expander devices.")
        for dev in self.i2cIOExpDevs:
            print("Status of the I2C I/O expander {0:s}:".format(dev.deviceName))
            ret, regInput = dev.read_input()
            ret, regConfig = dev.read_config()
            ret, regOutput = dev.read_output()
            ret, regPolarity = dev.read_polarity()
            print(self.prefixDetails + "Input level register        : 0x{0:04x}".format(regInput))
            print(self.prefixDetails + "Configuration register      : 0x{0:04x}".format(regConfig))
            print(self.prefixDetails + "Output register             : 0x{0:04x}".format(regOutput))
            print(self.prefixDetails + "Polarity inversion register : 0x{0:04x}".format(regPolarity))
        return 0



    # Get the status of one I/O by the signal name.
    # - input level
    # - configuration register
    # - output register
    # - polarity inversion register
    def i2c_io_exp_get_status(self, signalName):
        if self.debugLevel >= 1:
            print(self.prefixDebug + "Reading the status of signal `" + signalName + "'.")
        ret, dev, ioIdx = self.i2c_io_exp_signal2dev_io(signalName)
        if ret:
            return ret
        ret, regInput = dev.read_input()
        ret, regConfig = dev.read_config()
        ret, regOutput = dev.read_output()
        ret, regPolarity = dev.read_polarity()
        if ret:
            print(self.prefixError + "Error reading the status of signal `" + signalName + "'!")
            return ret
        print("Status of {0:s}, I/O {1:2d}, {2:s}:".format(dev.deviceName, ioIdx, '"' + signalName + '"'))
        print(self.prefixDetails + "Input level register        : {0:d}".format((regInput >> ioIdx) & 0x1))
        print(self.prefixDetails + "Configuration register      : {0:d}".format((regConfig >> ioIdx) & 0x1))
        print(self.prefixDetails + "Output register             : {0:d}".format((regOutput >> ioIdx) & 0x1))
        print(self.prefixDetails + "Polarity inversion register : {0:d}".format((regPolarity >> ioIdx) & 0x1))
        return 0



    # Get the input level of all ports of all I2C I/O expander devices.
    def i2c_io_exp_get_input_all(self):
        if self.debugLevel >= 1:
            print(self.prefixDebug + "Reading the input levels of all ports of all I2C I/O expander devices.")
        for dev in self.i2cIOExpDevs:
            print("Input levels of the I2C I/O expander {0:s}:".format(dev.deviceName))
            ret, regInput = dev.read_input()
            for ioIdx, ioMap in enumerate(dev.ioMap):
                print(self.prefixDetails + "I/O {0:2d}, {1:28s} : {2:d}".format(ioIdx, "`" + ioMap[0] + "'", (regInput >> ioIdx) & 0x1))
        return 0



    # Get the input level of one I/O by the signal name.
    def i2c_io_exp_get_input(self, signalName):
        if self.debugLevel >= 1:
            print(self.prefixDebug + "Reading the input level of signal `" + signalName + "'.")
        ret, dev, ioIdx = self.i2c_io_exp_signal2dev_io(signalName)
        if ret:
            return ret
        ret, regInput = dev.read_input()
        if ret:
            print(self.prefixError + "Error reading the input level of signal `" + signalName + "'!")
            return ret
        print("Input level of {0:s}, I/O {1:2d}, {2:s}: {3:d}".format(dev.deviceName, ioIdx, '"' + signalName + '"', (regInput >> ioIdx) & 0x1))
        return 0



    # Get the output value of all ports of all I2C I/O expander devices.
    def i2c_io_exp_get_output_all(self):
        if self.debugLevel >= 1:
            print(self.prefixDebug + "Reading the output values of all ports of all I2C I/O expander devices.")
        for dev in self.i2cIOExpDevs:
            print("Output values of the I2C I/O expander {0:s}:".format(dev.deviceName))
            ret, regOutput = dev.read_output()
            for ioIdx, ioMap in enumerate(dev.ioMap):
                print(self.prefixDetails + "I/O {0:2d}, {1:28s} : {2:d}".format(ioIdx, "`" + ioMap[0] + "'", (regOutput >> ioIdx) & 0x1))
        return 0



    # Get the output value of one I/O by the signal name.
    def i2c_io_exp_get_output(self, signalName):
        if self.debugLevel >= 1:
            print(self.prefixDebug + "Reading the output value of signal `" + signalName + "'.")
        ret, dev, ioIdx = self.i2c_io_exp_signal2dev_io(signalName)
        if ret:
            return ret
        ret, regOutput = dev.read_output()
        if ret:
            print(self.prefixError + "Error reading the output value of signal `" + signalName + "'!")
            return ret
        print("Output value of {0:s}, I/O {1:2d}, {2:s}: {3:d}".format(dev.deviceName, ioIdx, '"' + signalName + '"', (regOutput >> ioIdx) & 0x1))
        return 0



    # Set the output value of all ports of all I2C I/O expander devices.
    def i2c_io_exp_set_output_all(self, values):
        if self.debugLevel >= 1:
            print(self.prefixDebug + "Setting the output values of all ports of all I2C I/O expander devices.")
        if len(self.i2cIOExpDevs) != len(values):
            print(self.prefixError + "The size of the list of values does not match the size of the list of I2C I/O expander devices!")
            return 1
        for devIdx, dev in enumerate(self.i2cIOExpDevs):
            regOutput = values[devIdx] & 0xffff
            ret = dev.write_output(regOutput)
            if ret:
                print(self.prefixError + "Error writing value 0x{0:04x} the output register of device `{1:s}'!".format(regOutput, dev))
                return ret
        return 0



    # Set the output value of one I/O by the signal name.
    def i2c_io_exp_set_output(self, signalName, value):
        value &= 0x1
        if self.debugLevel >= 1:
            print(self.prefixDebug + "Setting the output value of signal `" + signalName + "' to {0:d}.".format(value))
        ret, dev, ioIdx = self.i2c_io_exp_signal2dev_io(signalName)
        if ret:
            return ret
        ret, regOutput = dev.read_output()
        if ret:
            print(self.prefixError + "Error reading the output value of signal `" + signalName + "'!")
            return ret
        regOutput &= ~(0x1 << ioIdx)
        regOutput |= value << ioIdx
        ret = dev.write_output(regOutput)
        if ret:
            print(self.prefixError + "Error setting the output value of signal `" + signalName + "' to {0:d}!".format(value))
            return ret
        return 0



    # Reset all clock chips using the I2C I/O expander devices.
    def i2c_io_exp_reset_clk(self):
        clkResetSignals = [
            "CLK_EXT_DBG_CLEAN_nRST",
            "CLK_FF_135_0_RSTb",
            "CLK_FF_135_1_RSTb",
            "CLK_FF_79_0_RSTb",
            "CLK_FF_79_1_RSTb",
            "CLK_FF_024_0_RSTb",
            "CLK_FF_024_1_RSTb",
            "CLK_FF_68_0_RSTb",
            "CLK_FF_68_1_RSTb",
            "FF_CLK_RSTb",
            "CLK_FF_TD_0_RSTb",
            "SM_RSTb"
        ]
        # Assert reset (active low).
        for signal in clkResetSignals:
            self.i2c_io_exp_set_output(signal, 0)
        # Wait some time.
        time.sleep(0.1)
        # De-assert reset (active low).
        for signal in clkResetSignals:
            self.i2c_io_exp_set_output(signal, 1)

    def i2c_io_exp_status_clk(self):
        clkstatusSignals = {
            "IC1":"FF_CLK_LOLb",
            "IC2":"CLK_FF_024_0_LOLb",
            "IC3":"CLK_FF_024_1_LOLb",
            "IC4":"CLK_FF_68_0_LOLb",
            "IC5":"CLK_FF_68_1_LOLb",
            "IC6":"CLK_FF_135_0_LOLb",
            "IC7":"CLK_FF_135_1_LOLb",
            "IC8":"CLK_FF_79_0_LOLb",
            "IC9":"CLK_FF_79_1_LOLb",
            "IC10":"CLK_FF_TD_0_LOLb",
            "IC12":"SM_LOLb"}
        
        # read LOL for all clock chips
        for ic in clkstatusSignals.keys():
            print(ic)
            self.i2c_io_exp_get_input(clkstatusSignals[ic])

