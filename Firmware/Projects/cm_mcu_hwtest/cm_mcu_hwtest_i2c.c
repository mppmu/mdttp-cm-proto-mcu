// File: cm_mcu_hwtest_i2c.c
// Auth: M. Fras, Electronics Division, MPI for Physics, Munich
// Mod.: M. Fras, Electronics Division, MPI for Physics, Munich
// Date: 03 Jun 2022
// Rev.: 11 Aug 2022
//
// I2C functions of the hardware test firmware running on the ATLAS MDT Trigger
// Processor (TP) Command Module (CM) prototype MCU.
//



#include <stdbool.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <strings.h>
#include "driverlib/i2c.h"
#include "driverlib/rom_map.h"
#include "driverlib/sysctl.h"
#include "driverlib/uart.h"
#include "utils/uartstdio.h"
#include "utils/ustdlib.h"
#include "hw/gpio/gpio.h"
#include "hw/gpio/gpio_pins.h"
#include "hw/i2c/i2c.h"
#include "hw/uart/uart.h"
#include "uart_ui.h"
#include "power_control.h"
#include "sm_cm.h"
#include "cm_mcu_hwtest.h"
#include "cm_mcu_hwtest_i2c.h"
#include "cm_mcu_hwtest_io.h"



// I2C access.
int I2CAccess(char *pcCmd, char *pcParam)
{
    int i;
    tI2C *psI2C;
    uint8_t ui8I2CPort = 0;
    uint8_t ui8I2CSlaveAddr = 0;
    uint8_t ui8I2CAccMode = 0;
    uint8_t ui8I2CRw = 0;           // 0 = write; 1 = read
    bool bI2CRepeatedStart = false; // Repeated start.
    bool bI2CStop = true;           // Generate stop condition.
    bool bI2CQuickCmd = false;      // Quick command.
    uint8_t ui8I2CDataNum = 0;
    uint8_t pui8I2CData[32];
    uint32_t ui32I2CMasterStatus;
    // Parse parameters.
    for (i = 0; i < sizeof(pui8I2CData) / sizeof(pui8I2CData[0]); i++) {
        if (i != 0) pcParam = strtok(NULL, UI_STR_DELIMITER);
        if (i == 0) {
            if (pcParam == NULL) {
                UARTprintf("%s: I2C port number required after command `%s'.\n", UI_STR_ERROR, pcCmd);
                I2CAccessHelp();
                return -1;
            } else {
                ui8I2CPort = (uint8_t) strtoul(pcParam, (char **) NULL, 0) & 0xff;
            }
        } else if (i == 1) {
            if (pcParam == NULL) {
                UARTprintf("%s: I2C slave address required after command `%s'.\n", UI_STR_ERROR, pcCmd);
                I2CAccessHelp();
                return -1;
            } else {
                ui8I2CSlaveAddr = (uint8_t) strtoul(pcParam, (char **) NULL, 0) & 0xff;
            }
        } else if (i == 2) {
            if (pcParam == NULL) {
                UARTprintf("%s: I2C access mode required after command `%s'.\n", UI_STR_ERROR, pcCmd);
                I2CAccessHelp();
                return -1;
            } else {
                ui8I2CAccMode = (uint8_t) strtoul(pcParam, (char **) NULL, 0) & 0x0f;
                ui8I2CRw = ui8I2CAccMode & 0x1;
                bI2CRepeatedStart = (ui8I2CAccMode & 0x2) ? true : false;
                bI2CStop = (ui8I2CAccMode & 0x4) ? false : true;
                bI2CQuickCmd = (ui8I2CAccMode & 0x8) ? true : false;
            }
        } else {
            if (i == 3 && ui8I2CRw == 0 && !bI2CQuickCmd && pcParam == NULL) {
                UARTprintf("%s: At least one data byte required after I2C write command `%s'.\n", UI_STR_ERROR, pcCmd);
                I2CAccessHelp();
                return -1;
            }
            if (pcParam == NULL) break;
            else pui8I2CData[i-3] = (uint8_t) strtoul(pcParam, (char **) NULL, 0) & 0xff;
        }
    }
    if (i < 3) return -1;
    // Check if the I2C port number is valid. If so, set the psI2C pointer to the selected I2C port struct.
    if (I2CPortCheck(ui8I2CPort, &psI2C)) return -1;
    // I2C quick command.
    if (bI2CQuickCmd) {
        ui32I2CMasterStatus = I2CMasterQuickCmdAdv(psI2C, ui8I2CSlaveAddr, ui8I2CRw, bI2CRepeatedStart);
    // Standard I2C access.
    } else {
        // I2C write.
        if (ui8I2CRw == 0) {
            ui32I2CMasterStatus = I2CMasterWriteAdv(psI2C, ui8I2CSlaveAddr, pui8I2CData, i - 3, bI2CRepeatedStart, bI2CStop);
        // I2C read.
        } else {
            if (i == 3) ui8I2CDataNum = 1;
            else ui8I2CDataNum = pui8I2CData[0];
            if (ui8I2CDataNum > sizeof(pui8I2CData) / sizeof(pui8I2CData[0])) {
                ui8I2CDataNum = sizeof(pui8I2CData) / sizeof(pui8I2CData[0]);
            }
            ui32I2CMasterStatus = I2CMasterReadAdv(psI2C, ui8I2CSlaveAddr, pui8I2CData, ui8I2CDataNum, bI2CRepeatedStart, bI2CStop);
        }
    }
    // Check the I2C status.
    if (ui32I2CMasterStatus) {
        UARTprintf("%s: Error flags from I2C the master %d: 0x%08x", UI_STR_ERROR, ui8I2CPort, ui32I2CMasterStatus);
        if (ui32I2CMasterStatus & I2C_MASTER_INT_TIMEOUT) UARTprintf("\n%s: I2C timeout.", UI_STR_ERROR);
        if (ui32I2CMasterStatus & I2C_MASTER_INT_NACK) UARTprintf("\n%s: NACK received.", UI_STR_ERROR);
        if (ui32I2CMasterStatus & I2C_MASTER_INT_ARB_LOST) UARTprintf("\n%s: I2C bus arbitration lost.", UI_STR_ERROR);
        if (ui32I2CMasterStatus & 0x1) UARTprintf("\n%s: Unknown error.", UI_STR_ERROR);
    } else {
        UARTprintf("%s.", UI_STR_OK);
        if (ui8I2CRw && !bI2CQuickCmd) {
            UARTprintf(" Data:");
            for (i = 0; i < ui8I2CDataNum; i++) UARTprintf(" 0x%02x", pui8I2CData[i]);
        }
    }

    return 0;
}



// Show help on I2C access command.
void I2CAccessHelp(void)
{
    UARTprintf("I2C access command:\n");
    UARTprintf("  i2c     PORT SLV-ADR ACC NUM|DATA   I2C access (ACC bits: R/W, Sr, nP, Q).\n");
    UARTprintf("I2C access mode (ACC) bits:\n");
    UARTprintf("  0: Read/write (R/W)                 0 = write, 1 = read\n");
    UARTprintf("  1: Repeated start (Sr)              0 = no Sr, 1 = Sr\n");
    UARTprintf("  2: No stop condition (nP)           0 = generate stop cond. P, 1 = omit P\n");
    UARTprintf("  3: Quick command (Q)                0 = no Q, 1 = Q");
}



// Check if the I2C port number is valid. If so, set the psI2C pointer to the selected I2C port struct.
int I2CPortCheck(uint8_t ui8I2CPort, tI2C **psI2C)
{
    int i;
    bool bI2CPortValid = false;
    uint8_t ui8I2CPortIdx;

    // Valid I2C ports on the CM prototype: 1 .. 8
    // The ports 0 and 9 are unused.
    for (i = 0; i < I2C_MASTER_NUM; i++) {
        if (ui8I2CPort == g_ui8I2CMasterPorts[i]) {
            bI2CPortValid = true;
            ui8I2CPortIdx = i;
            break;
        }
    }
    if (!bI2CPortValid) {
        *psI2C = NULL;
        UARTprintf("%s: Invalid I2C port number %d! Valid I2C ports are:", UI_STR_ERROR, ui8I2CPort);
        for (i = 0; i < I2C_MASTER_NUM; i++) {
            UARTprintf(" %d", g_ui8I2CMasterPorts[i]);
        }
        return -1;
    } else {
        *psI2C = &g_psI2C[ui8I2CPortIdx];
    }
    return 0;
}



// Detect I2C devices.
int I2CDetect(char *pcCmd, char *pcParam)
{
    int i;
    tI2C *psI2C;
    uint8_t ui8I2CPort = 0;
    uint8_t ui8I2CSlaveAddr = 0;
    uint8_t ui8I2CDetectMode = 0;   // 0 = auto; 1 = quick command; 2 = read
    uint8_t pui8I2CData[1];
    uint32_t ui32I2CMasterStatus;
    // Parse parameters.
    for (i = 0; i < 4; i++) {
        if (i != 0) pcParam = strtok(NULL, UI_STR_DELIMITER);
        if (i == 0) {
            if (pcParam == NULL) {
                UARTprintf("%s: I2C port number required after command `%s'.", UI_STR_ERROR, pcCmd);
                return -1;
            } else {
                ui8I2CPort = (uint8_t) strtoul(pcParam, (char **) NULL, 0) & 0xff;
            }
        } else if (i == 1 && pcParam != NULL) {
            ui8I2CDetectMode = (uint8_t) strtoul(pcParam, (char **) NULL, 0) & 0x0f;
        } else {
            break;
        }
    }
    if (i < 1) return -1;
    // Check if the I2C port number is valid. If so, set the psI2C pointer to the selected I2C port struct.
    if (I2CPortCheck(ui8I2CPort, &psI2C)) return -1;
    // Detect I2C devices based on the i2cdetect program of the i2c-tools.
    // Please see: https://github.com/mozilla-b2g/i2c-tools/blob/master/tools/i2cdetect.c
    UARTprintf("%s. I2C device(s) found at slave address:", UI_STR_OK);
    for (ui8I2CSlaveAddr = 1; ui8I2CSlaveAddr <= 0x7f; ui8I2CSlaveAddr++) {
        switch (ui8I2CDetectMode) {
            // Detection mode using I2C quick command.
            case 1:
                ui32I2CMasterStatus = I2CMasterQuickCmd(psI2C, ui8I2CSlaveAddr, false);   // false = write; true = read
            // Detection mode using I2C read command.
            case 2:
                ui32I2CMasterStatus = I2CMasterRead(psI2C, ui8I2CSlaveAddr, pui8I2CData, 1);
            // Automatic mode. Use I2C quick command or I2C read based on the slave address.
            default:
                if ((ui8I2CSlaveAddr >= 0x30 && ui8I2CSlaveAddr <= 0x37)
                    || (ui8I2CSlaveAddr >= 0x50 && ui8I2CSlaveAddr <= 0x5F)) {
                    ui32I2CMasterStatus = I2CMasterRead(psI2C, ui8I2CSlaveAddr, pui8I2CData, 1);
                } else {
                    ui32I2CMasterStatus = I2CMasterQuickCmd(psI2C, ui8I2CSlaveAddr, false);   // false = write; true = read
                }
        }
        if (!ui32I2CMasterStatus) UARTprintf(" 0x%02x", ui8I2CSlaveAddr);
    }

    return 0;
}

