// File: cm_mcu_hwtest_qssi.c
// Auth: M. Fras, Electronics Division, MPI for Physics, Munich
// Mod.: M. Fras, Electronics Division, MPI for Physics, Munich
// Date: 16 Sep 2022
// Rev.: 20 Sep 2022
//
// QSSI functions of the hardware test firmware running on the ATLAS MDT
// Trigger Processor (TP) Command Module (CM) prototype MCU.
//



#include <stdbool.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include "utils/uartstdio.h"
#include "hw/qssi/qssi.h"
#include "cm_mcu_hwtest_qssi.h"
#include "cm_mcu_hwtest_io.h"



// QSSI access.
int QssiAccess(char *pcCmd, char *pcParam)
{
    int i;
    uint8_t ui8QssiPort = 0;
    uint8_t ui8QssiMode = 0;    // 0 = SSI; 1 = QSSI
    uint8_t ui8QssiRw = 0;      // 0 = write; 1 = read
    bool bQssiFrameEnd = true;  // true = end frame; false = do not end frame
    uint8_t ui8QssiDataNum = 0;
    uint32_t pui32QssiData[32];
    tQSSI *psQssi;
    int32_t i32QssiStatus;
    // Parse parameters.
    for (i = 0; i < sizeof(pui32QssiData) / sizeof(pui32QssiData[0]); i++) {
        if (i != 0) pcParam = strtok(NULL, UI_STR_DELIMITER);
        if (i == 0) {
            if (pcParam == NULL) {
                UARTprintf("%s: QSSI port number required after command `%s'.", UI_STR_ERROR, pcCmd);
                return -1;
            } else {
                ui8QssiPort = (uint8_t) strtoul(pcParam, (char **) NULL, 0) & 0xff;
            }
        } else if (i == 1) {
            if (pcParam == NULL) {
                UARTprintf("%s: QSSI mode required after command `%s'.", UI_STR_ERROR, pcCmd);
                return -1;
            } else {
                ui8QssiMode = (uint8_t) strtoul(pcParam, (char **) NULL, 0) & 0x01;
            }
        } else if (i == 2) {
            if (pcParam == NULL) {
                UARTprintf("%s: QSSI read/write required after command `%s'.", UI_STR_ERROR, pcCmd);
                return -1;
            } else {
                ui8QssiRw = (uint8_t) strtoul(pcParam, (char **) NULL, 0) & 0x01;
            }
        } else if (i == 3) {
            if (pcParam == NULL) {
                UARTprintf("%s: QSSI end frame required after command `%s'.", UI_STR_ERROR, pcCmd);
                return -1;
            } else {
                bQssiFrameEnd = (bool) strtoul(pcParam, (char **) NULL, 0) & 0x01;
            }
        } else {
            if (i == 4 && ui8QssiRw == 0 && pcParam == NULL) {
                UARTprintf("%s: At least one data byte required after QSSI write command `%s'.", UI_STR_ERROR, pcCmd);
                return -1;
            }
            if (i == 4 && ui8QssiRw == 1 && pcParam == NULL) {
                UARTprintf("%s: Number of data to read required after QSSI read command `%s'.", UI_STR_ERROR, pcCmd);
                return -1;
            }
            if (pcParam == NULL) break;
            else pui32QssiData[i-4] = (uint32_t) strtoul(pcParam, (char **) NULL, 0) & 0xffff;
        }
    }
    if (i < 5) return -1;
    // Check if the QSSI port number is valid. If so, set the psQssi pointer to the selected QSSI port struct.
    if (QssiPortCheck(ui8QssiPort, &psQssi)) return -1;
    // QSSI write.
    if (ui8QssiRw == 0) {
        i32QssiStatus = QssiMasterWrite(psQssi, pui32QssiData, i - 4, ui8QssiMode, bQssiFrameEnd);
        // Check the QSSI status.
        if (i32QssiStatus) {
            UARTprintf("%s: Error status from the QSSI master %d: %d", UI_STR_ERROR, ui8QssiPort, i32QssiStatus);
        } else {
            UARTprintf("%s.", UI_STR_OK);
        }
    // QSSI read.
    } else {
        // Read given number of data.
        ui8QssiDataNum = pui32QssiData[0];
        if (ui8QssiDataNum > sizeof(pui32QssiData) / sizeof(pui32QssiData[0])) {
            ui8QssiDataNum = sizeof(pui32QssiData) / sizeof(pui32QssiData[0]);
        }
        i32QssiStatus = QssiMasterRead(psQssi, pui32QssiData, ui8QssiDataNum, ui8QssiMode, bQssiFrameEnd);
        // Check the QSSI status.
        if (i32QssiStatus < 0) {
            UARTprintf("%s: Error status from the QSSI master %d: %d", UI_STR_ERROR, ui8QssiPort, i32QssiStatus);
        } else if (i32QssiStatus != ui8QssiDataNum) {
            UARTprintf("%s: Could only read %d data bytes from the QSSI master %d instead of %d.", UI_STR_WARNING, i32QssiStatus, ui8QssiPort, ui8QssiDataNum);
        } else {
            UARTprintf("%s.", UI_STR_OK);
        }
        if (i32QssiStatus > 0) {
            UARTprintf(" Data:");
            for (i = 0; i < i32QssiStatus; i++) UARTprintf(" 0x%02x", pui32QssiData[i]);
        }
    }

    return 0;
}



// Check if the QSSI port number is valid. If so, set the psQssi pointer to the
// selected QSSI port struct.
int QssiPortCheck(uint8_t ui8QssiPort, tQSSI **psQssi)
{
    switch (ui8QssiPort) {
        case 1: *psQssi = &g_sQssi1; break;
        default:
            *psQssi = NULL;
            UARTprintf("%s: Only QSSI port number 1 is supported!", UI_STR_ERROR);
            return -1;
    }
    return 0;
}



// Set up the QSSI interface.
int QssiSetup(char *pcCmd, char *pcParam)
{
    int i;
    uint8_t ui8QssiPort = 0;
    uint32_t ui32QssiBitRate;
    tQSSI *psQssi;
    // Parse parameters.
    for (i = 0; i <= 1; i++) {
        if (i != 0) pcParam = strtok(NULL, UI_STR_DELIMITER);
        if (i == 0) {
            if (pcParam == NULL) {
                UARTprintf("%s: QSSI port number required after command `%s'.\n", UI_STR_ERROR, pcCmd);
                QssiSetupHelp();
                return -1;
            } else {
                ui8QssiPort = (uint8_t) strtoul(pcParam, (char **) NULL, 0) & 0xff;
            }
        } else if (i == 1) {
            if (pcParam == NULL) {
                UARTprintf("%s: QSSI bit rate required after command `%s'.\n", UI_STR_ERROR, pcCmd);
                QssiSetupHelp();
                return -1;
            } else {
                ui32QssiBitRate = (uint32_t) strtoul(pcParam, (char **) NULL, 0);
                if ((ui32QssiBitRate < QSSI_FREQ_MIN) || (ui32QssiBitRate > QSSI_FREQ_MAX)) {
                    UARTprintf("%s: QSSI bit rate %d outside of valid range %d..%d.", UI_STR_ERROR, ui32QssiBitRate, QSSI_FREQ_MIN, QSSI_FREQ_MAX);
                    return -1;
                }
            }
        }
    }
    if (i != 2) return -1;
    // Check if the QSSI port number is valid. If so, set the psQssi pointer to the selected QSSI port struct.
    if (QssiPortCheck(ui8QssiPort, &psQssi)) return -1;
    // Set up the QSSI port.
    psQssi->ui32BitRate = ui32QssiBitRate;
    QssiMasterInit(psQssi);

    UARTprintf("%s.", UI_STR_OK);

    return 0;
}



// Show help on the QSSI setup command.
void QssiSetupHelp(void)
{
    UARTprintf("QSSI setup command:\n");
    UARTprintf("  qssi-s  PORT FREQ                   Set up the QSSI port.\n");
    UARTprintf("QSSI bit rate: %d..%d\n", QSSI_FREQ_MIN, QSSI_FREQ_MAX);
}

