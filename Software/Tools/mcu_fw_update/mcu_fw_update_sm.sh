#!/bin/sh
#
# File: mcu_fw_update_sm.sh
# Auth: M. Fras, Electronics Division, MPI for Physics, Munich
# Mod.: M. Fras, Electronics Division, MPI for Physics, Munich
# Date: 17 Jun 2026
# Rev.: 18 Jun 2026
#
# Script to update the MCU firmware of the ATLAS MDT Trigger Processor (TP)
# Command Module (CM) from the Service Module (SM) SoM.
#
# CAUTION: The sflash utility which comes with the SM will *not* work, as it
#          is adapted to the MCU software and firmware of the Cornell CM!
#          Make sure to use the sflash utility that comes with MCU firmware
#          repository of the ATLAS MDT TP Command Module.
#



BUTOOL=/opt/BUTool/bin/BUTool/BUTool.exe
SFLASH=../../TivaWare/SW-TM4C-2.2.0.295/tools/sflash/sflash
UART_FW_UPDATE=/dev/ttyUL1
MCU_FW_FILE="../../../Firmware/Projects/cm_mcu_hwtest/gcc/cm_mcu_hwtest.bin"



# Change to script directory for defined paths.
cd `dirname $0`



# Evaluate command line arguments.
if [ $# -ne 1 ]; then
    echo "Usage: `basename $0` <mcu_fw_file.bin>"
    exit 1
else
    MCU_FW_FILE="$1"
fi



# Check if the MCU firmware file is available.
if [ ! -r ${MCU_FW_FILE} ]; then
    echo "ERROR: MCU firmware file \`${MCU_FW_FILE}' is not available!"
    echo "MCU firmware update aborted!"
    exit 2
fi

# Check if BUTool is available.
if [ ! -x ${BUTOOL} ]; then
    echo "ERROR: BUTool is not available!"
    echo "MCU firmware update aborted!"
    exit 3
fi

# Build sflash utility if it is not available.
if [ ! -x ${SFLASH} ]; then
    cd `dirname ${SFLASH}`
    make
    cd -
fi
if [ ! -x ${SFLASH} ]; then
    echo "ERROR: The sflash utility is not available!"
    echo "MCU firmware update aborted!"
    exit 4
fi



# Check is the l0mdt_service is running. It must be stopped, as it interferes
# with the firmware update.
check_l0mdt_service() {
    systemctl is-active --quiet l0mdt_service
    STATUS=$?
    if [ ${STATUS} -eq 0 ]; then
        return 1
    else
        return 0
    fi
}
check_l0mdt_service
L0MDT_SERVICE_ACTIVE=$?
L0MDT_SERVICE_RESTART=${L0MDT_SERVICE_ACTIVE}
while [ ${L0MDT_SERVICE_ACTIVE} -eq 1 ]; do
    echo "CAUTION:"
    echo "The l0mdt_service *must* be stopped before the MCU firmware update!"
    # Check for root privileges.
    if [ `whoami` == "root" ]; then
        read -p "Do you want to stop it now (y/n)?: " confirm
        if [[ $confirm != [yY] && $confirm != [yY][eE][sS] ]]; then
            echo "MCU firmware update aborted!"
            exit 5
        fi
        echo "Stopping the l0mdt_service."
        systemctl stop l0mdt_service
    # Display message and exit if no root privileges are available.
    else
        echo "Use this command to stop it:"
        echo "    sudo systemctl stop l0mdt_service"
        echo "MCU firmware update aborted!"
        exit 6
    fi
    check_l0mdt_service
    L0MDT_SERVICE_ACTIVE=$?
done



# Create temporary script file for BUTool.
BUTOOL_SCRIPT_FILE=`mktemp -p /tmp BUTool_script.tmp.XXXXX`
echo "restartCMuC 1"    >  ${BUTOOL_SCRIPT_FILE}
echo "cmpwrup"          >> ${BUTOOL_SCRIPT_FILE}
echo "quit"             >> ${BUTOOL_SCRIPT_FILE}

# Call BUTool to reset the MCU.
echo "Calling BUTool to reset the MCU."
${BUTOOL} -a --script ${BUTOOL_SCRIPT_FILE}
sleep 2

# Delete temporary script file for BUTool.
rm -f ${BUTOOL_SCRIPT_FILE}

# Set correct baud rate.
stty -F ${UART_FW_UPDATE} sane 2>/dev/null
stty 115200 < ${UART_FW_UPDATE}

# Enter the MCU bootloader.
echo "Entering the MCU bootloader."
echo -ne " " > ${UART_FW_UPDATE}
sleep 2

# Enter the firmware download mode of the MCU bootloader.
echo "Entering the firmware download mode of the MCU bootloader."
echo -ne "f" > ${UART_FW_UPDATE}
sleep 2

# Update the MCU firmware.
echo "Updating the MCU firmware with file \`${MCU_FW_FILE}'."
${SFLASH} -c ${UART_FW_UPDATE} -p 0x4000 -b 115200 -d -s 252 ${MCU_FW_FILE}
STATUS=$?

if [ ${STATUS} -eq 0 ]; then
    echo "MCU firmware update finished."
else
    echo "MCU firmware update FAILED."
fi

# Restart the l0mdt_service if running as root and if it had been running in
# the beginning.
if [ ${L0MDT_SERVICE_RESTART} -eq 1 ]; then
    # Check for root privileges.
    if [ `whoami` == "root" ]; then
        echo "Starting the l0mdt_service."
        systemctl start l0mdt_service
    fi
fi

