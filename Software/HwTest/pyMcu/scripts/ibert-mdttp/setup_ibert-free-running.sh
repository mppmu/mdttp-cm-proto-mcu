#!/bin/sh
# File: setup_ibert_rec-clk.sh
# Auth: M. Fras, Electronics Division, MPI for Physics, Munich
# Mod.: M. Fras, Electronics Division, MPI for Physics, Munich
# Date: 23 Mar 2021
# Rev.: 27 Feb 2023
#
# Simple script to set up the ATLAS MDT Trigger Processor (TP) Command Module
# for Xilinx IBERT tests, using the recovered clock from the FELIX IBERT module
# for the front-end IBERT module.
#
# Reference clock path on the CM demonstrator V1/V2:
#   IC54, free-running mode, OUT: 40 MHz
#   -> IC82, IN0: 40 MHz, OUT: 240 MHz
#   -> KU15P FELIX IBERT, MGTREFCLK0: 240 MHz -> rxoutclock: 120 MHz
#   -> Multiplexer for recovered LHC clock (IC57)
#   -> IC56, IN2/IN3 (*): 120 MHz, OUT: 40 MHz
#   -> IC83, IN2:  40 MHz, OUT: 40 MHz
#       +-> IC84, IN0: 40 MHz, OUT: 320 MHz -> KU15P FE IBERT, MGTREFCLK0: 320 MHz
#       +-> IC85, IN0: 40 MHz, OUT: 320 MHz -> ZU11EG FE IBERT, MGTREFCLK0: 320 MHz
#
# (*) IN3 on the CM demonstrator V1, IN2 on the CM demonstrator V2. IN3 is used
#     for the zero-delay mode on V2.
#



cd `dirname $0`
cd ../..


PY_MCU_CM="./pyMcuCm.py"
SERIAL_DEVICE="/dev/ttyUL1"
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



# Power up the Command Module.
echo "Power up the Command Module."
${PY_MCU_CM} -d ${SERIAL_DEVICE} -v ${VERBOSITY} -c power_up

sleep 5

echo "Program the clock synthesizer chip IC10 (SI5345A) in free-running mode to generate a fixed 40 MHz clock."
${PY_MCU_CM} -d ${SERIAL_DEVICE} -v ${VERBOSITY} -c clk_setup -p IC10 config/clock/IBERT-TEST/IC10_INT-FR_OUT-40-40-40-40-Registers.txt

echo "Program the clock synthesizer chip IC1 (Si5345A) to multiplex the 40MHz LHC clock from source IN1."
${PY_MCU_CM} -d ${SERIAL_DEVICE} -v ${VERBOSITY} -c clk_setup -p IC1 config/clock/IBERT-TEST/IC1_40IN1_40_40_40_40_40_40_40_40_40_FB-Registers.txt

echo "Program the clock synthesizer chip IC2 (Si5345A) for CSM communication."
${PY_MCU_CM} -d ${SERIAL_DEVICE} -v ${VERBOSITY} -c clk_setup -p IC3 config/clock/IBERT-TEST/IC2,3,6,7_40IN0_320-Registers.txt

echo "Program the clock synthesizer chip IC3 (Si5345A) for CSM communication."
${PY_MCU_CM} -d ${SERIAL_DEVICE} -v ${VERBOSITY} -c clk_setup -p IC3 config/clock/IBERT-TEST/IC2,3,6,7_40IN0_320-Registers.txt

echo "Program the clock synthesizer chip IC6 (Si5345A) for FELIX communication."
${PY_MCU_CM} -d ${SERIAL_DEVICE} -v ${VERBOSITY} -c clk_setup -p IC6 config/clock/IBERT-TEST/IC2,3,6,7_40IN0_320-Registers.txt

echo "Program the clock synthesizer chip IC12 (Si5345A) for C2C communication."
${PY_MCU_CM} -d ${SERIAL_DEVICE} -v ${VERBOSITY} -c clk_setup -p IC12 config/clock/IBERT-TEST/IC12_INT_200_200_NA-Registers.txt

