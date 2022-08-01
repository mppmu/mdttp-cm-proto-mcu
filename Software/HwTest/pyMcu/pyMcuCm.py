#!/usr/bin/env python3
#
# File: pyMcuCm.py
# Auth: M. Fras, Electronics Division, MPI for Physics, Munich
# Mod.: M. Fras, Electronics Division, MPI for Physics, Munich
# Date: 26 Jul 2022
# Rev.: 01 Aug 2022
#
# Python script to access the ATLAS MDT Trigger Processor (TP) Command Module
# (CM) Prototype via the TI Tiva TM4C1290 MCU.
#



# Append hardware classes folder to Python path.
import os
import sys
sys.path.append(os.path.relpath(os.path.join(os.path.dirname(__file__), 'hw')))



# System modules.
import time



# Hardware classes.
import MdtTp_CM



# Message prefixes and separators.
prefixDebug             = "DEBUG: {0:s}: ".format(__file__)
prefixError             = "ERROR: {0:s}: ".format(__file__)



# ===================================================================
# Access the Command Module.
# ===================================================================

if __name__ == "__main__":
    # Command line arguments.
    import argparse
    parser = argparse.ArgumentParser(description='Run an automated set of MCU tests.')
    parser.add_argument('-c', '--command', action='store', type=str,
                        choices=['power_up', 'power_down', 'sn', 'status', 'mon_temp',
                                 'mcu_cmd_raw', 'mcu_led_user',
                                 'i2c_reset', 'i2c_detect'],
                        dest='command', default='status',
                        help='Command to execute on the CM.')
    parser.add_argument('-d', '--device', action='store', type=str,
                        dest='serialDevice', default='/dev/ttyUL1', metavar='SERIAL_DEVICE',
                        help='Serial device to access the MCU. Hint: An empty device string ("") enables simulated access.')
    parser.add_argument('-p', '--parameters', action='store', type=str, nargs='*',
                        dest='commandParameters', default=None, metavar='PARAMETER',
                        help='Parameter(s) for the selected command.')
    parser.add_argument('-v', '--verbosity', action='store', type=int,
                        dest='verbosity', default="1", choices=range(0, 5),
                        help='Set the verbosity level. The default is 1.')
    args = parser.parse_args()

    command = args.command
    commandParameters = args.commandParameters
    serialDevice = args.serialDevice
    verbosity = args.verbosity

    # Define the Command Module object.
    mdtTp_CM = MdtTp_CM.MdtTp_CM(serialDevice, verbosity)

    # Execute requested command.
    if not command:
        print("Please specify a command using the `-c' option.")
    elif command == "power_up":
        mdtTp_CM.power_up()
    elif command == "power_down":
        mdtTp_CM.power_down()
    elif command == "sn":
        mdtTp_CM.serial_number()
    elif command == "status":
        print("Board Serial Number")
        print("===================")
        mdtTp_CM.serial_number()
        print()
        print("Power Status")
        print("============")
        mdtTp_CM.power_status()
        print()
        print("Temperatures")
        print("============")
        mdtTp_CM.mon_temp()
    elif command == "mon_temp":
        mdtTp_CM.mon_temp()
    elif command == "mcu_cmd_raw":
        if commandParameters:
            ret, response = mdtTp_CM.mcu_cmd_raw(" ".join(commandParameters))
            print(response)
        else:
            print(prefixError, "Please specify the raw MCU command.")
    elif command == "mcu_led_user":
        if commandParameters:
            value = int(commandParameters[0], 0)
            ret = mdtTp_CM.mcu_led_user_set(value)
            if ret:
                print(prefixError, "Error setting the MCU user LED value!")
        else:
            ret, value = mdtTp_CM.mcu_led_user_get()
            if ret:
                print(prefixError, "Error reading the MCU user LED value!")
            else:
                print("MCU user LED value: 0x{0:03x}".format(value))
    elif command == "i2c_reset":
        mdtTp_CM.i2c_reset()
    elif command == "i2c_detect":
        mdtTp_CM.i2c_detect_devices()
    else:
        print(prefixError + "Command `{0:s}' not supported!".format(command))

    print("\nBye-bye!")

