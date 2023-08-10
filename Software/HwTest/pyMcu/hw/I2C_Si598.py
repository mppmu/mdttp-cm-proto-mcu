# File: I2C_Si598.py
# Auth: Rimsky Rojas
# Date: 04 August 2020
#
# Python class for communicating with Silicon Labs Si598 device.
#



import os
import McuI2C
import I2CDevice
import time


class I2C_Si598:

    # Message prefixes and separators.
    prefixDetails       = " - "
    separatorDetails    = " - "
    prefixDebug         = "DEBUG: {0:s}: ".format(__file__)
    prefixError         = "ERROR: {0:s}: ".format(__file__)

    # Debug configuration.
    debugLevel = 0                 # Debug verbosity.
    _hs_div_table = [4, 5, 6, 7, -1, 9 ,-1, 11]
    instructions = """
    These are the instructions to determine the values of the registers to write and set a new frequency
    These are computed once, and no need to update them unless you require a frequency other than 240MHz
    1) Read start-up frequency configuration (RFREQ, HS_DIV, and N1) from the device after power-up or register reset

     Registers for the Current Configuration 
      Register   Data
          7       0xA1
          8       0x47
          9       0xC1
         10       0x31
         11       0x58
         12       0x08

      RFREQ  = 0x7C1315808
             = 0x7C1315808 / (2^28) = 124,07454684
      HS_DIV = 0x5 = 9
      N1     = 0x5 = 6

2) Calculate the actual nominal crystal frequency where f0 is the start-up output frequency

      fxtal = ( f0 x HS_DIV x N1 ) / RFREQ 
            = (90,000000000 MHz x 9 x 6) / 124,074546844
            = 39,170000000 MHz

3) Choose the new output frequency (f1).
      Output Frequency (f1) = 240,000000000 MHz

4) Choose the output dividers for the new frequency configuration (HS_DIV and N1) by ensuring the DCO oscillation frequency (fdco) is between 4.85 GHz and 5.67 GHz where fdco = f1 x HS_DIV x N1. See the Divider Combinations tab for more options.

      HS_DIV = 0x7 = 11
      N1     = 0x1 = 2
      fdco = f1 x HS_DIV x N1 
           = 240,000000000 MHz x 11 x 2
           = 5,280000000 GHz

5) Calculate the new crystal frequency multiplication ratio (RFREQ) as RFREQ = fdco / fxtal

      RFREQ = fdco / fxtal 
            = 5,280000000 GHz / 39,170000000 MHz
            = 134,79703855
            = 134,79703855 x (2^28) = 0x86CC0AB7E

6) Freeze the DCO by setting Freeze DCO = 1 (bit 4 of register 137).

7) Write the new frequency configuration (RFREQ, HS_DIV, and N1)

     Registers for the New Configuration 
      Register   Data
          7       0xE0
          8       0x48
          9       0x6C
         10       0xC0
         11       0xAB
         12       0x7E

8) Unfreeze the DCO by setting Freeze DCO = 0 and assert the NewFreq bit (bit 6 of register 135) within 10 ms."""
    # Hardware parameters.

    # Initialize the I2C device.
    def __init__(self, mcuI2C, slaveAddr, deviceName):
        self.mcuI2C = mcuI2C
        self.slaveAddr = slaveAddr
        self.deviceName = deviceName
        self.i2cDevice = I2CDevice.I2CDevice(self.mcuI2C, self.slaveAddr, self.deviceName)
        self.i2cDevice.debugLevel = self.debugLevel
        self.prefixDebugDevice = self.prefixDebug + self.deviceName + ": "
        self.prefixErrorDevice = self.prefixError + self.deviceName + ": "

    # Read the current frequency of the clock chip
    def get_freq(self):
        self.i2cDevice.debugLevel = self.debugLevel
        # Debug info.
        if self.debugLevel >= 2:
            print(self.prefixDebugDevice + "Getting frequency from IC11", end='')
            self.i2cDevice.print_details()
        # Write command and read data with repeated start.
        ret, _data = self.i2cDevice.write_read([0x07], 6)
        # Evaluate response.
        if ret:
            print(self.prefixErrorDevice + "Error reading frequency", end='')
            self.i2cDevice.print_details()
            print(self.prefixErrorDevice + "Error code: {0:d}: ".format(ret))
            return -1, 0xff
        if len(_data) != 6:
            print(self.prefixErrorDevice + "Error reading the value of the registers: Incorrect amount of data received!"\
                , end='')
            self.i2cDevice.print_details()
            return -1, 0xff
        # Calculate the value.
        #        r7=int(_data[0],base=16)
        #        r8=int(_data[1],base=16)
        #        r9=int(_data[2],base=16)
        #        r10=int(_data[3],base=16)
        #        r11=int(_data[4],base=16)
        #        r12=int(_data[5],base=16)
        r7=_data[0]
        r8=_data[1]
        r9=_data[2]
        r10=_data[3]
        r11=_data[4]
        r12=_data[5]
        n1=((r7&0x1f)<<2)+(r8>>6) + 1 # = 6 #check the datasheet
        hs_div_table=r7>>5 # = 5
        hs_div = self._hs_div_table[hs_div_table] #check the datasheet table correspondance: 9 corresponds to hs_div_table = 5
        rfreq=(((r8&0x3f)<<32) + (r9<<24) + (r10<<16) + (r11<<8) + r12 )/ 2**28
        f0=90 #fixed by part number
        # In principle fxtal should be always the same value, fixed by part number
        fxtal = 39.17 # ( f0 * hs_div * n1 ) / rfreq 
        freq=fxtal * rfreq / hs_div / n1
        return 0, freq
    
    def prog(self, freq):
        if self.debugLevel >= 2:
            print(self.prefixDebugDevice + "Writing configuration for ic11, 240MHz", end='')

        # 6) Freeze the DCO by setting Freeze DCO = 1 (bit 4 of register 137).
        # note from datasheet: Si598: Write 0x10 to this register to Freeze DCO
        ret = self.i2cDevice.write([0x89, 0x10])
        if ret:
            print(self.prefixErrorDevice + "Error Writing configuration to clock chip")
            return -1            
        
        # 7) Write the new frequency configuration (RFREQ, HS_DIV, and N1)
        if freq == "240":
            ret = self.i2cDevice.write([0x07, 0xE0, 0x48, 0x6C, 0xC0, 0xAB, 0x7E])
        elif freq == "240.474":
            ret = self.i2cDevice.write([0x07, 0xE0, 0x48, 0x71, 0x03, 0x1F, 0xC0])
        else :
            print(self.prefixErrorDevice + "Error frequency not recognized, user 240 or 240.474")
            return -1
        if ret:
            print(self.prefixErrorDevice + "Error Writing configuration to clock chip")
            return -1
        
        # 8) Unfreeze the DCO by setting Freeze DCO = 0 and assert the NewFreq bit (bit 6 of register 135) within 10 ms.
        ret = self.i2cDevice.write([0x89, 0x00])
        if ret:
            print(self.prefixErrorDevice + "Error Writing configuration to clock chip")
            return -1   
        # New Frequency Applied.
        # Alerts the DSPLL that a new frequency configuration has been applied. This bit will
        # clear itself when the new frequency is applied. Write 0x40 to this register to assert NewFreq.
        ret = self.i2cDevice.write([0x87, 0x40])
        if ret:
            print(self.prefixErrorDevice + "Error Writing configuration to clock chip")
            return -1 
        return 0
