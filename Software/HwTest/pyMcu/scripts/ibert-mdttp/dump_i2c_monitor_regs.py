#!/usr/bin/env python3                                                                                            
#                                                                                                                 
# File: dump_i2c_monitor_regs.py
# Author: Rimsky Rojas
#
# Requirements: needs to be used with special firmware to monitor the clocks using I2C
# Description
#
# the script reads data from 64 registers using the 
# pyMcuCm.py script via a JSON file containing pin, multiplexer, 
# and address information for each register.
#
# The Python script reads data from 64 registers connected through a 64:8 multiplexer 
# by calling another script called pyMcuCm.py. The script takes each of the 
# register's mux and address values from a JSON file, and uses them to read four bytes
# of data for each register. The JSON file contains an array of entries, where each 
# entry represents a single register, and has the package_pin, reg_mux, and reg fields 
# to identify the register's pin, multiplexer value, and address, respectively.



import json
import subprocess
import re

# Load the data from the JSON file                                                                               
#
device='/dev/ttyUL1'
          
with open('regs_to_mon.json', 'r') as f:
    data = json.load(f)
previous_mux=-1
# Loop through each pin and read its register                                                                              
for pin_name, pin_data in data.items():
    package_pin = pin_data['package_pin']
    reg_mux = pin_data['reg_mux']
    reg = int(pin_data['reg'], 16)

    # Set the multiplexer                                                                                                  
    if previous_mux != reg_mux:
        subprocess.run(['../../pyMcuCm.py', '-d', device, '-c', 'mcu_cmd_raw', '-p', f"i2c 8 0x08 0x0 0x00 0x00 0x00 0x00 0x{reg_mux}0" ], stdout=subprocess.PIPE)

    # Set the address to read from                                                                                         
    subprocess.run(['../../pyMcuCm.py', '-d', device, '-c', 'mcu_cmd_raw', '-p', f"i2c 8 0x08 0x4 " + '0x{:02X}'.format(reg) ], stdout=subprocess.PIPE)

    # Read four bytes                                                                                                      
    result = subprocess.run(['../../pyMcuCm.py', '-d', device, '-c', 'mcu_cmd_raw', '-p', f"i2c 8 0x08 0x3 4 "], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output_hex = result.stdout.strip().decode('utf-8')

    # Define a regular expression pattern to match the relevant part of the output
    res = output_hex.split(" ") 
    # Extract the matched string and remove any spaces
    result = f" {res[1]}{res[2][2:4]}{res[3][2:4]}{res[4][2:4]}"

    # Print the result
    print(pin_name, result, "value in MHz:", int(result,16)/1e6)
    previous_mux = reg_mux
    # Print the result                                                                                                     
#    print(f"{pin_name}: {output_hex}")
