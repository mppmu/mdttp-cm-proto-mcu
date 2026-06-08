#!/bin/bash
while true
do
    # Commands to execute while the condition is true
    #
    date +"%Y-%m-%d %H:%M:%S"
    sudo ./pyMcuCm.py -d /dev/ttyUSB0 -c mcu_cmd_raw -p i2c 4 0x7c 0 0x00 | grep "0x"
    sudo ./pyMcuCm.py -d /dev/ttyUSB0 -c mcu_cmd_raw -p i2c 4 0x7c 1 1 | grep "0x"
    sudo ./pyMcuCm.py -d /dev/ttyUSB0 -c mcu_cmd_raw -p i2c 4 0x7c 0 0x29 | grep "0x"
    sudo ./pyMcuCm.py -d /dev/ttyUSB0 -c mcu_cmd_raw -p i2c 4 0x7c 1 1 | grep "0x"
    sudo ./pyMcuCm.py -d /dev/ttyUSB0 -c mcu_cmd_raw -p i2c 4 0x7c 0 0x01 | grep "0x"
    sudo ./pyMcuCm.py -d /dev/ttyUSB0 -c mcu_cmd_raw -p i2c 4 0x7c 1 1 | grep "0x"
    sudo ./pyMcuCm.py -d /dev/ttyUSB0 -c mcu_cmd_raw -p i2c 4 0x7c 0 0x10 | grep "0x"
    sudo ./pyMcuCm.py -d /dev/ttyUSB0 -c mcu_cmd_raw -p i2c 4 0x7c 1 1 | grep "0x"
    sudo ./pyMcuCm.py -d /dev/ttyUSB0 -c mcu_cmd_raw -p i2c 4 0x7c 0 0x02 | grep "0x"
    sudo ./pyMcuCm.py -d /dev/ttyUSB0 -c mcu_cmd_raw -p i2c 4 0x7c 1 1 | grep "0x"

    echo "================="
done

