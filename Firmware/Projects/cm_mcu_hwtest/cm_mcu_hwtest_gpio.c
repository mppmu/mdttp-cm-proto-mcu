// File: cm_mcu_hwtest_gpio.c
// Auth: M. Fras, Electronics Division, MPI for Physics, Munich
// Mod.: M. Fras, Electronics Division, MPI for Physics, Munich
// Date: 03 Jun 2022
// Rev.: 24 Feb 2024
//
// GPIO functions of the hardware test firmware running on the ATLAS MDT
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
#include "cm_mcu_hwtest_gpio.h"
#include "cm_mcu_hwtest_io.h"



// Get/Set the value of a GPIO type.
int GpioGetSet(char *pcCmd, char *pcParam)
{
    char *pcGpioType = pcParam;
    bool bGpioWrite;
    uint32_t ui32GpioSet = 0, ui32GpioGet = 0;

    if (pcGpioType == NULL) {
        UARTprintf("%s: GPIO type required after command `%s'.\n", UI_STR_ERROR, pcCmd);
        GpioGetSetHelp();
        return -1;
    }
    pcParam = strtok(NULL, UI_STR_DELIMITER);
    // Read the current value of the user GPIO pins if no parameter is given.
    if (pcParam == NULL) {
        bGpioWrite = false;
    } else {
        bGpioWrite = true;
        ui32GpioSet = strtol(pcParam, (char **) NULL, 0);
    }
    // GPIO type.
    if (!strcasecmp(pcGpioType, "help")) {
        GpioGetSetHelp();
        return 0;
    } else if (!strcasecmp(pcGpioType, "sm-pwr-en")) {
        if (bGpioWrite) {
            UARTprintf("%s: GPIO %s is read-only!", UI_STR_WARNING, pcGpioType);
            return 1;
        }
        ui32GpioGet = GpioGet_SmPowerEna();
    } else if (!strcasecmp(pcGpioType, "cm-ready")) {
        if (bGpioWrite) GpioSet_CmReady(ui32GpioSet);
        ui32GpioGet =  GpioGet_CmReady();
    } else if (!strcasecmp(pcGpioType, "sm-ps-rst")) {
        if (bGpioWrite) {
            UARTprintf("%s: GPIO %s is read-only!", UI_STR_WARNING, pcGpioType);
            return 1;
        }
        ui32GpioGet = GpioGet_SmPsReset();
    } else if (!strcasecmp(pcGpioType, "sm-gpio")) {
        if (bGpioWrite) GpioSet_SmGpio(ui32GpioSet);
        ui32GpioGet =  GpioGet_SmGpio();
    } else if (!strcasecmp(pcGpioType, "led-status")) {
        if (bGpioWrite) GpioSet_LedCmStatus(ui32GpioSet);
        ui32GpioGet = GpioGet_LedCmStatus();
    } else if (!strcasecmp(pcGpioType, "led-user")) {
        if (bGpioWrite) GpioSet_LedMcuUser(ui32GpioSet);
        ui32GpioGet = GpioGet_LedMcuUser();
    } else if (!strcasecmp(pcGpioType, "power-ctrl")) {
        if (bGpioWrite) GpioSet_PowerCtrl(ui32GpioSet);
        ui32GpioGet = GpioGet_PowerCtrl();
    } else if (!strcasecmp(pcGpioType, "power-good")) {
        if (bGpioWrite) {
            UARTprintf("%s: GPIO %s is read-only!", UI_STR_WARNING, pcGpioType);
            return 1;
        }
        ui32GpioGet = GpioGet_PowerGood();
    } else if (!strcasecmp(pcGpioType, "power-fault")) {
        if (bGpioWrite) {
            UARTprintf("%s: GPIO %s is read-only!", UI_STR_WARNING, pcGpioType);
            return 1;
        }
        ui32GpioGet = GpioGet_PowerFault();
    } else if (!strcasecmp(pcGpioType, "power-i2c-alert")) {
        if (bGpioWrite) {
            UARTprintf("%s: GPIO %s is read-only!", UI_STR_WARNING, pcGpioType);
            return 1;
        }
        ui32GpioGet = GpioGet_PowerI2CAlert();
    } else if (!strcasecmp(pcGpioType, "power-reserved-ctrl")) {
        if (bGpioWrite) GpioSet_PowerReservedCtrl(ui32GpioSet);
        ui32GpioGet = GpioGet_PowerReservedCtrl();
    } else if (!strcasecmp(pcGpioType, "temp-alert")) {
        if (bGpioWrite) {
            UARTprintf("%s: GPIO %s is read-only!", UI_STR_WARNING, pcGpioType);
            return 1;
        }
        ui32GpioGet = GpioGet_TempAlert();
    } else if (!strcasecmp(pcGpioType, "fpga")) {
        if (bGpioWrite) GpioSet_FPGACtrlStat(ui32GpioSet);
        ui32GpioGet = GpioGet_FPGACtrlStat();
    } else if (!strcasecmp(pcGpioType, "i2c-reset")) {
        if (bGpioWrite) GpioSet_I2CReset(ui32GpioSet);
        ui32GpioGet = GpioGet_I2CReset();
    } else if (!strcasecmp(pcGpioType, "i2c-int")) {
        if (bGpioWrite) {
            UARTprintf("%s: GPIO %s is read-only!", UI_STR_WARNING, pcGpioType);
            return 1;
        }
        ui32GpioGet = GpioGet_I2CInt();
    } else {
        UARTprintf("%s: Unknown GPIO type `%s'!\n", UI_STR_ERROR, pcGpioType);
        GpioGetSetHelp();
        return -1;
    }
    if (bGpioWrite) {
        if (ui32GpioGet == ui32GpioSet) {
            UARTprintf("%s: GPIO %s set to 0x%02x.", UI_STR_OK, pcGpioType, ui32GpioGet);
        } else {
            UARTprintf("%s: Setting GPIO %s to 0x%02x failed!", UI_STR_ERROR, pcGpioType, ui32GpioSet);
            UARTprintf(" It was set to 0x%02x instead.", ui32GpioGet);
        }
    } else {
        UARTprintf("%s: Current GPIO %s value: 0x%02x", UI_STR_OK, pcGpioType, ui32GpioGet);
    }
    return 0;
}



// Show help on GPIO command.
void GpioGetSetHelp(void)
{
    UARTprintf("Available GPIO types:\n");
    UARTprintf("  help                        Show this help text.\n");
    UARTprintf("  sm-pwr-en                   SM power enable driven to CM.\n");
    UARTprintf("  cm-ready                    CM ready signal driven to SM.\n");
    UARTprintf("  sm-ps-rst                   SM PS reset signal.\n");
    UARTprintf("  sm-gpio                     GPIO signals between SM and CM.\n");
    UARTprintf("  led-status                  CM status LEDs.\n");
    UARTprintf("  led-user                    User LEDs.\n");
    UARTprintf("  power-ctrl                  Switch on/off physical power domains.\n");
    UARTprintf("  power-good                  Read the status of physical power domains.\n");
    UARTprintf("  power-fault                 Check for faults on physical power domains.\n");
    UARTprintf("  power-i2c-alert             Check for I2C alerts on physical power domains.\n");
    UARTprintf("  power-reserved-ctrl         Switch on/off reserved physical power domains.\n");
    UARTprintf("  temp-alert                  Alert signals of the temperature sensors.\n");
    UARTprintf("  fpga                        Control/status of the FPGA.\n");
    UARTprintf("  i2c-reset                   Reset signals of I2C bus switches.\n");
    UARTprintf("  i2c-int                     Interrupt signals of I2C GPIO expanders.\n");
}

