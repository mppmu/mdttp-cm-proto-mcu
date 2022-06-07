// File: cm_mcu_hwtest_uart.c
// Auth: M. Fras, Electronics Division, MPI for Physics, Munich
// Mod.: M. Fras, Electronics Division, MPI for Physics, Munich
// Date: 03 Jun 2022
// Rev.: 03 Jun 2022
//
// UART functions of the hardware test firmware running on the ATLAS MDT
// Trigger Processor (TP) Command Module (CM) prototype MCU.
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
#include "cm_mcu_hwtest_io.h"
#include "cm_mcu_hwtest_uart.h"



// Global variables.
extern tUartUi *g_psUartUi;



// UART access.
int UartAccess(char *pcCmd, char *pcParam)
{
    int i;
    uint8_t ui8UartPort = 0;
    uint8_t ui8UartRw = 0;  // 0 = write; 1 = read
    uint8_t ui8UartDataNum = 0;
    uint8_t pui8UartData[32];
    tUART *psUart;
    int32_t i32UartStatus;
    // Parse parameters.
    for (i = 0; i < sizeof(pui8UartData) / sizeof(pui8UartData[0]); i++) {
        if (i != 0) pcParam = strtok(NULL, UI_STR_DELIMITER);
        if (i == 0) {
            if (pcParam == NULL) {
                UARTprintf("%s: UART port number required after command `%s'.", UI_STR_ERROR, pcCmd);
                return -1;
            } else {
                ui8UartPort = (uint8_t) strtoul(pcParam, (char **) NULL, 0) & 0xff;
            }
        } else if (i == 1) {
            if (pcParam == NULL) {
                UARTprintf("%s: UART read/write required after command `%s'.", UI_STR_ERROR, pcCmd);
                return -1;
            } else {
                ui8UartRw = (uint8_t) strtoul(pcParam, (char **) NULL, 0) & 0x01;
            }
        } else {
            if (i == 2 && ui8UartRw == 0 && pcParam == NULL) {
                UARTprintf("%s: At least one data byte required after UART write command `%s'.", UI_STR_ERROR, pcCmd);
                return -1;
            }
            if (pcParam == NULL) break;
            else pui8UartData[i-2] = (uint8_t) strtoul(pcParam, (char **) NULL, 0) & 0xff;
        }
    }
    if (i < 2) return -1;
    // Check if the UART port number is valid.
    if (UartPortCheck(ui8UartPort, &psUart)) return -1;
    // UART write.
    if (ui8UartRw == 0) {
        i32UartStatus = UartWrite(psUart, pui8UartData, i - 2);
        // Check the UART status.
        if (i32UartStatus) {
            UARTprintf("%s: Error status from the UART %d: %d", UI_STR_ERROR, ui8UartPort, i32UartStatus);
        } else {
            UARTprintf("%s.", UI_STR_OK);
        }
    // UART read.
    } else {
        if (i == 2) ui8UartDataNum = 1;
        // Read all available data.
        if (i == 2) {
            for (int iCnt = 0; ; iCnt++) {
                i32UartStatus = UartRead(psUart, pui8UartData, 1);
                if (i32UartStatus != 1) {
                    if (iCnt == 0) UARTprintf("%s: No data available.", UI_STR_WARNING);
                    break;
                } else {
                    if (iCnt == 0) UARTprintf("%s. Data:", UI_STR_OK);
                    UARTprintf(" 0x%02x", pui8UartData[0]);
                }
            }
        // Read given number of data.
        } else {
            ui8UartDataNum = pui8UartData[0];
            if (ui8UartDataNum > sizeof(pui8UartData) / sizeof(pui8UartData[0])) {
                ui8UartDataNum = sizeof(pui8UartData) / sizeof(pui8UartData[0]);
            }
            i32UartStatus = UartRead(psUart, pui8UartData, ui8UartDataNum);
            // Check the UART status.
            if (i32UartStatus != ui8UartDataNum) {
                UARTprintf("%s: Could only read %d data bytes from the UART %d instead of %d.", UI_STR_WARNING, i32UartStatus, ui8UartPort, ui8UartDataNum);
            } else {
                UARTprintf("%s.", UI_STR_OK);
            }
            if (i32UartStatus > 0) {
                UARTprintf(" Data:");
                for (i = 0; i < i32UartStatus; i++) UARTprintf(" 0x%02x", pui8UartData[i]);
            }
        }
    }

    return 0;
}



// Check if the UART port number is valid. If so, set the psUart pointer to the
// selected UART port struct.
int UartPortCheck(uint8_t ui8UartPort, tUART **psUart)
{
    // Front-panel USB UART UI on UART3.
    if (g_psUartUi == &g_sUartUi3) {
        switch (ui8UartPort) {
            case 1: *psUart = &g_sUart1; break;
            case 5: *psUart = &g_sUart5; break;
            default:
                *psUart = NULL;
                UARTprintf("%s: Only UART port numbers 1 and 5 are supported!", UI_STR_ERROR);
                return -1;
        }
    // SM SoC UART UI on UART5.
    } else if (g_psUartUi == &g_sUartUi5) {
        switch (ui8UartPort) {
            case 1: *psUart = &g_sUart1; break;
            case 3: *psUart = &g_sUart3; break;
            default:
                *psUart = NULL;
                UARTprintf("%s: Only UART port numbers 1 and 3 are supported!", UI_STR_ERROR);
                return -1;
        }
    // UART UI on UART 1.
    } else {
        switch (ui8UartPort) {
            case 3: *psUart = &g_sUart3; break;
            case 5: *psUart = &g_sUart5; break;
            default:
                *psUart = NULL;
                UARTprintf("%s: Only UART port numbers 3 and 5 are supported!", UI_STR_ERROR);
                return -1;
        }
    }

    return 0;
}



// Set up the UART port.
int UartSetup(char *pcCmd, char *pcParam)
{
    int i;
    uint8_t ui8UartPort = 0;
    uint32_t ui32UartBaud;
    uint32_t ui32UartParity;
    bool bUartLoopback;
    tUART *psUart;
    // Parse parameters.
    for (i = 0; i <= 3; i++) {
        if (i != 0) pcParam = strtok(NULL, UI_STR_DELIMITER);
        if (i == 0) {
            if (pcParam == NULL) {
                UARTprintf("%s: UART port number required after command `%s'.\n", UI_STR_ERROR, pcCmd);
                UartSetupHelp();
                return -1;
            } else {
                ui8UartPort = (uint8_t) strtoul(pcParam, (char **) NULL, 0) & 0xff;
            }
        } else if (i == 1) {
            if (pcParam == NULL) {
                UARTprintf("%s: UART baud rate required after command `%s'.\n", UI_STR_ERROR, pcCmd);
                UartSetupHelp();
                return -1;
            } else {
                ui32UartBaud = (uint32_t) strtoul(pcParam, (char **) NULL, 0);
                if ((ui32UartBaud < UART_BAUD_MIN) || (ui32UartBaud > UART_BAUD_MAX)) {
                    UARTprintf("%s: UART baud rate %d outside of valid range %d..%d.", UI_STR_ERROR, ui32UartBaud, UART_BAUD_MIN, UART_BAUD_MAX);
                    return -1;
                }
            }
        } else if (i == 2) {
            if (pcParam == NULL) {
                ui32UartParity = UART_CONFIG_PAR_NONE;
            } else {
                ui32UartParity = strtoul(pcParam, (char **) NULL, 0) & 0x07;
                switch (ui32UartParity) {
                    case 0: ui32UartParity = UART_CONFIG_PAR_NONE; break;
                    case 1: ui32UartParity = UART_CONFIG_PAR_EVEN; break;
                    case 2: ui32UartParity = UART_CONFIG_PAR_ODD; break;
                    case 3: ui32UartParity = UART_CONFIG_PAR_ONE; break;
                    case 4: ui32UartParity = UART_CONFIG_PAR_ZERO; break;
                    default:
                        UARTprintf("%s: Invalid UART parity setting %d.", UI_STR_ERROR, ui32UartParity);
                        return -1;
                }
            }
        } else if (i == 3) {
            if (pcParam == NULL) {
                bUartLoopback = false;
            } else {
                bUartLoopback = (bool) strtoul(pcParam, (char **) NULL, 0) & 0x01;
            }
        }
    }
    if (i < 1) return -1;
    // Check if the UART port number is valid. If so, set the psUart pointer to the selected UART port struct.
    if (UartPortCheck(ui8UartPort, &psUart)) return -1;
    // Set up the UART.
    psUart->ui32Baud = ui32UartBaud;
    psUart->bLoopback = bUartLoopback;
    UartInit(psUart);
    UARTParityModeSet(psUart->ui32BaseUart, ui32UartParity);

    UARTprintf("%s.", UI_STR_OK);

    return 0;
}



// Show help on the UART setup command.
void UartSetupHelp(void)
{
    UARTprintf("UART setup command:\n");
    UARTprintf("  uart-s  PORT BAUD [PARITY] [LOOP]   Set up the UART port.");
    UARTprintf("UART baud rate: %d..%d\n", UART_BAUD_MIN, UART_BAUD_MAX);
    UARTprintf("UART partiy options:\n");
    UARTprintf("  0: None.\n");
    UARTprintf("  1: Even.\n");
    UARTprintf("  2: Odd.\n");
    UARTprintf("  3: One.\n");
    UARTprintf("  4: Zero.");
    UARTprintf("UART loopback options:\n");
    UARTprintf("  0: No loopback.\n");
    UARTprintf("  1: Enable internal loopback mode.\n");
}

