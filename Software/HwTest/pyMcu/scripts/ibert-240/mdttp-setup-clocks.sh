#!/bin/sh
# File: mdt-setup-clocks.sh
# modified from: ../ibert-mdttp/setup_ibert_rec-clk.sh
# Auth: R. Rojas, UMass - CERN
# Date: 29 Oct 2024
#
# Simple script to set up the ATLAS MDT Trigger Processor (TP) Command Module
# for Xilinx IBERT tests,
#
# Reference clock path on the CM Prototype:
#   IC12, free-running mode, OUT: 200 MHz (Used for C2C communication)
#   IC11, free-running mode, OUT: 240 MHz (Used for GTY120 TC link)
#   -> IC10, IN0: 120 MHz, OUT: 40 MHz    (Expect recovered clock from TC, usually half of the ref clock. MGTREFCLK0: 240 MHz -> rxoutclock: 128 MHz)
#       -> IC1, IN0: 40 MHz, OUT: 40 MHz
#           -> IC2,4,6,8, IN0:  40 MHz, OUT: 240 MHz (Connected to all MGTREFCLK0, MGTREFCLK1 not used)
#
#



cd `dirname $0`

PYMCU_DIR="/opt/mdttp-cm-proto-mcu/Software/HwTest/pyMcu"

PY_MCU_CM="pyMcuCm.py"
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
BUTool.exe -a --cmd cmpwrup --cmd q

sleep 3
echo "Program the clock synthesizer chip IC11 for clock recovery"
${PY_MCU_CM} -d ${SERIAL_DEVICE} -v ${VERBOSITY} -c clk_setup -p IC11 240

echo "Program the clock synthesizer chip IC1 (Si5345A) to multiplex the 40MHz LHC clock from source IN1."
${PY_MCU_CM} -d ${SERIAL_DEVICE} -v ${VERBOSITY} -c clk_setup -p IC1 ${PYMCU_DIR}/config/clock/IBERT-TEST/IC1_40IN0_40_40_40_40_40_40_40_40_40_FB-Registers.txt

echo "Program the clock synthesizer chip IC2 (Si5345A) for SL communication."
${PY_MCU_CM} -d ${SERIAL_DEVICE} -v ${VERBOSITY} -c clk_setup -p IC2  ${PYMCU_DIR}/scripts/ibert-240/IC2,3,6,7_40-IN0_240-OUT0,1,2,3,4,5,6,7,8_FB-Registers.txt

echo "Program the clock synthesizer chip IC4 (Si5345A) for SL communication."
${PY_MCU_CM} -d ${SERIAL_DEVICE} -v ${VERBOSITY} -c clk_setup -p IC4  ${PYMCU_DIR}/scripts/ibert-240/IC2,3,6,7_40-IN0_240-OUT0,1,2,3,4,5,6,7,8_FB-Registers.txt

echo "Program the clock synthesizer chip IC6 (Si5345A) for SL communication."
${PY_MCU_CM} -d ${SERIAL_DEVICE} -v ${VERBOSITY} -c clk_setup -p IC6  ${PYMCU_DIR}/scripts/ibert-240/IC2,3,6,7_40-IN0_240-OUT0,1,2,3,4,5,6,7,8_FB-Registers.txt

echo "Program the clock synthesizer chip IC8 (Si5345A) for SL communication."
${PY_MCU_CM} -d ${SERIAL_DEVICE} -v ${VERBOSITY} -c clk_setup -p IC8  ${PYMCU_DIR}/scripts/ibert-240/IC2,3,6,7_40-IN0_240-OUT0,1,2,3,4,5,6,7,8_FB-Registers.txt

echo "Program the clock synthesizer chip IC10 (SI5345A) to generate a fixed 40 MHz clock from the 120MHz rec-clock "
echo "WARNING: the recovered clock may be of 128MHz instead of 120, don't worry... the clock will work as free running"
${PY_MCU_CM} -d ${SERIAL_DEVICE} -v ${VERBOSITY} -c clk_setup -p IC10  ${PYMCU_DIR}/config/clock/IBERT-TEST/IC10_120IN0_40_40_40_40_NA_NA_NA_NA_NA_FB-Registers.txt


echo "Program the clock synthesizer chip IC12 (Si5345A) for C2C communication at 200 MHz..."
${PY_MCU_CM} -d ${SERIAL_DEVICE} -v ${VERBOSITY} -c clk_setup -p IC12  ${PYMCU_DIR}/config/clock/IBERT-TEST/IC12_INT_200_200_NA-Registers.txt
