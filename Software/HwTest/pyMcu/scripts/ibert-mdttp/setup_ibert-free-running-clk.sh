#!/bin/bash
# File: setup_ibert_rec-clk.sh
# Auth: Davide Cieri (davide.cieri@cern.ch), MPI for Physics, Munich
# Mod.: Davide Cieri (davide.cieri@cern.ch), MPI for Physics, Munich
# Date: 25 Apr 2023
# Rev.: 24 Apr 2023
#
# Simple script to set up the ATLAS MDT Trigger Processor (TP) Command Module Prototype V1
# for Xilinx IBERT tests, using the on-board generated clock
#
# Reference clock path on the CM prototype V1:
#   IC10, free-running mode, OUT: 40 MHz
#   -> IC1, IN1: 40 MHz, OUT: 40 MHz
#   -> IC2
#   -> Multiplexer for recovered LHC clock (IC57)
#   -> IC56, IN2/IN3 (*): 120 MHz, OUT: 40 MHz
#   -> IC83, IN2:  40 MHz, OUT: 40 MHz
#       +-> IC84, IN0: 40 MHz, OUT: 320 MHz -> KU15P FE IBERT, MGTREFCLK0: 320 MHz
#       +-> IC85, IN0: 40 MHz, OUT: 320 MHz -> ZU11EG FE IBERT, MGTREFCLK0: 320 MHz
#
# (*) IN3 on the CM demonstrator V1, IN2 on the CM demonstrator V2. IN3 is used
#     for the zero-delay mode on V2.
#


set -e

cd `dirname $0`
cd ../..

PY_MCU_CM="./pyMcuCm.py"
SERIAL_DEVICE="/dev/ttyUSB0"
VERBOSITY="0"

# Parse command line arguments.
usage() {
    echo "Usage: `basename $0` [-d SERIAL_DEVICE] [-v VERBOSITY]" 1>&2; exit 1;
}

while getopts ":d:v:" o; do
    case "${o}" in
        d)
            SERIAL_DEVICE=${OPTARG}
            ;;
        v)
            VERBOSITY=${OPTARG}
            ;;
        *)
            usage
            ;;
    esac
done


# All clock ICs used here
clock_ics="CLK_FF_135_0 CLK_FF_135_1 CLK_FF_79_0 CLK_FF_79_1 CLK_FF_024_0 CLK_FF_024_1 CLK_FF_68_0 CLK_FF_68_1 FF_CLK CLK_FF_TD_0"

# Power up the Command Module.
echo "Power up the Command Module."
echo "${PY_MCU_CM} -d ${SERIAL_DEVICE} -v ${VERBOSITY} -c power_up"
${PY_MCU_CM} -d ${SERIAL_DEVICE} -v ${VERBOSITY} -c power_up

# Reset all clock ICs
# ${PY_MCU_CM} -d ${SERIAL_DEVICE} -c i2c_io_exp_init
# for ic in $clock_ics; do
#     reset=${ic}_RSTb
#     ${PY_MCU_CM} -d ${SERIAL_DEVICE} -c i2c_io_exp_set_output -p $reset 0
# done

# for ic in $clock_ics; do
#     reset=${ic}_RSTb
#     ${PY_MCU_CM} -d ${SERIAL_DEVICE} -c i2c_io_exp_set_output -p $reset 1
# done

if [ "$2" == "reset" ]; then
    exit 0
fi

sleep 2

echo "${PY_MCU_CM} -d ${SERIAL_DEVICE} -v ${VERBOSITY} -c clk_setup -p IC10 config/clock/IBERT-TEST/IC10_INT-FR_OUT-40-40-40-40-Registers.txt"
${PY_MCU_CM} -d ${SERIAL_DEVICE} -v ${VERBOSITY} -c clk_setup -p IC10 config/clock/IBERT-TEST/IC10_INT-FR_OUT-40-40-40-40-Registers.txt
${PY_MCU_CM} -d ${SERIAL_DEVICE} -v ${VERBOSITY} -c clk_setup -p IC1 config/clock/IBERT-TEST/IC1_40IN0_40_40_40_40_40_40_40_40_40_FB-Registers.txt
${PY_MCU_CM} -d ${SERIAL_DEVICE} -v ${VERBOSITY} -c clk_setup -p IC2 config/clock/IBERT-TEST/IC2,3,6,7_40IN0_240_240_240_240_240_240_320_320_320_FB-Registers.txt
${PY_MCU_CM} -d ${SERIAL_DEVICE} -v ${VERBOSITY} -c clk_setup -p IC3 config/clock/IBERT-TEST/IC2,3,6,7_40IN0_240_240_240_240_240_240_320_320_320_FB-Registers.txt
${PY_MCU_CM} -d ${SERIAL_DEVICE} -v ${VERBOSITY} -c clk_setup -p IC6 config/clock/IBERT-TEST/IC2,3,6,7_40IN0_240_240_240_240_240_240_320_320_320_FB-Registers.txt
${PY_MCU_CM} -d ${SERIAL_DEVICE} -v ${VERBOSITY} -c clk_setup -p IC7 config/clock/IBERT-TEST/IC2,3,6,7_40IN0_240_240_240_240_240_240_320_320_320_FB-Registers.txt
${PY_MCU_CM} -d ${SERIAL_DEVICE} -v ${VERBOSITY} -c clk_setup -p IC4 config/clock/IBERT-TEST/IC4,5,8,9_40IN0_240_240_240_320_320_320_NA_NA_NA_FB-Registers.txt
${PY_MCU_CM} -d ${SERIAL_DEVICE} -v ${VERBOSITY} -c clk_setup -p IC5 config/clock/IBERT-TEST/IC4,5,8,9_40IN0_240_240_240_320_320_320_NA_NA_NA_FB-Registers.txt
${PY_MCU_CM} -d ${SERIAL_DEVICE} -v ${VERBOSITY} -c clk_setup -p IC8 config/clock/IBERT-TEST/IC4,5,8,9_40IN0_240_240_240_320_320_320_NA_NA_NA_FB-Registers.txt
${PY_MCU_CM} -d ${SERIAL_DEVICE} -v ${VERBOSITY} -c clk_setup -p IC9 config/clock/IBERT-TEST/IC4,5,8,9_40IN0_240_240_240_320_320_320_NA_NA_NA_FB-Registers.txt

echo "Checking LOL signals...."

no_lock=0
for ic in $clock_ics; do
    lol=${ic}_LOLb
    state=`${PY_MCU_CM} -d ${SERIAL_DEVICE} -c i2c_io_exp_get_input | grep $lol | cut -d: -f2`
    if [ "$state" != " 1" ]; then
        echo "ERROR: LOL on $lol"
        no_lock=1
    fi
done

if [ "$no_lock" != "0" ]; then
    exit -1
fi

echo "Run clock test with"
echo "  ./clock_test -t /dev/ttyUSB1 115200 -C FF_ALT"
