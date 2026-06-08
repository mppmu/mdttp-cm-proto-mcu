#!/bin/sh
# File: monitor_power_temp.sh
# Auth: M. Fras, Electronics Division, MPI for Physics, Munich
# Mod.: M. Fras, Electronics Division, MPI for Physics, Munich
# Date: 02 Sep 2020
# Rev.: 23 Mar 2021
#
# Simple script to monitor power and temperatures of the ATLAS MDT Trigger
# Processor (TP) Command Module.
#



cd `dirname $0`
cd ..



PY_MCU_CM="./pyMcuCm.py"
#SERIAL_DEVICE="/dev/ttyUL1"
SERIAL_DEVICE="/dev/ttyUSB1"
VERBOSITY="0"



while [ 1 ]; do
#    date +"%Y%m%d %H%M%S"
    date +"%d.%m.%Y %H:%M:%S"
#    ipmitool -H 192.168.0.2 -P "" -t 0x92 sensor | grep "PIM400KZ Current"
    ${PY_MCU_CM} -d ${SERIAL_DEVICE} -v ${VERBOSITY} -c mon_temp | grep "degC"
    ${PY_MCU_CM} -d ${SERIAL_DEVICE} -v ${VERBOSITY} -c power_detail
    echo
done

