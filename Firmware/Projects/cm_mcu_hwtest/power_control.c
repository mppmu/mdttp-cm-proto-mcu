// File: power_control.c
// Auth: M. Fras, Electronics Division, MPI for Physics, Munich
// Mod.: M. Fras, Electronics Division, MPI for Physics, Munich
// Date: 03 Jun 2022
// Rev.: 06 Oct 2022
//
// Power control functions for the hardware test firmware running on the ATLAS
// MDT Trigger Processor (TP) Command Module (CM) prototype MCU.
//



#include <stdbool.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <strings.h>
#include "utils/uartstdio.h"
#include "hw/gpio/gpio_pins.h"
#include "power_control.h"
#include "cm_mcu_hwtest.h"



// Control power domains.
int PowerControl(char *pcCmd, char *pcParam)
{
    char *pcPowerDomain = pcParam;
    bool bPowerSet = false;
    uint32_t ui32PowerVal = 0;
    int status = 0;

    if (pcPowerDomain == NULL) {
        UARTprintf("%s: Power domain required after command `%s'.\n", UI_STR_ERROR, pcCmd);
        PowerControlHelp();
        return -1;
    }
    pcParam = strtok(NULL, UI_STR_DELIMITER);
    // Read the current value of a power domain if no parameter is given.
    if (pcParam == NULL) {
        bPowerSet = false;
    } else {
        bPowerSet = true;
        ui32PowerVal = strtol(pcParam, (char **) NULL, 0);
    }
    // Power domain.
    if (!strcasecmp(pcPowerDomain, "help")) {
        PowerControlHelp();
        return 0;
    } else if (!strcasecmp(pcPowerDomain, "all")) {
        status = PowerControl_All(bPowerSet, ui32PowerVal);
    } else if (!strcasecmp(pcPowerDomain, "clock")) {
        status = PowerControl_ClockMisc(bPowerSet, ui32PowerVal);
    } else if (!strcasecmp(pcPowerDomain, "fpga")) {
        status = PowerControl_FPGA(bPowerSet, ui32PowerVal);
    } else if (!strcasecmp(pcPowerDomain, "firefly")) {
        status = PowerControl_FireFly(bPowerSet, ui32PowerVal);
    } else {
        UARTprintf("%s: Unknown power domain `%s'!\n", UI_STR_ERROR, pcPowerDomain);
        PowerControlHelp();
        return -1;
    }

    if (bPowerSet && !status) {
        UARTprintf("%s.", UI_STR_OK);
    }

    return status;
}



// Show help on power control command.
void PowerControlHelp(void)
{
    UARTprintf("Available domains:\n");
    UARTprintf("  help                                Show this help text.\n");
    UARTprintf("  all                                 All switchable power domains.\n");
    UARTprintf("  clock                               Clock and miscellaneous power domain.\n");
    UARTprintf("  firefly                             FireFly power domain.\n");
    UARTprintf("  fpga                                FPGA power, incl. clock domain.\n");
}



// Power control for all power domains.
int PowerControl_All(bool bPowerSet, uint32_t ui32PowerVal)
{
    uint32_t ui32GpioGet;
    int status;

    // Get the power status of all power domains.
    if (!bPowerSet) {
        ui32GpioGet = GpioGet_PowerCtrl();
        if ((ui32GpioGet & POWER_ALL) == POWER_ALL) {
            UARTprintf("%s: All power domains are completely ON. GPIO power control = 0x%02x", UI_STR_OK, ui32GpioGet);
            return 0;
        } else if ((ui32GpioGet & POWER_ALL) == 0) {
            UARTprintf("%s: All power domains are completely OFF. GPIO power control = 0x%02x", UI_STR_OK, ui32GpioGet);
            return 0;
        } else {
            UARTprintf("%s: The power domains are PARTIALLY ON. GPIO power control = 0x%02x", UI_STR_ERROR, ui32GpioGet);
            return -1;
        }
    // Set the power status of all power domains.
    } else {
        // Power up the clock domain first.
        if (ui32PowerVal != 0) {
            // Set the power of the clock and miscellaneous domain.
            status = PowerControl_ClockMisc(bPowerSet, ui32PowerVal);
            if (status) return status;
        }
        // Set the power of the FPGA.
        status = PowerControl_FPGA(bPowerSet, ui32PowerVal);
        if (status) return status;
        // Set the power of the FireFly domain.
        status = PowerControl_FireFly(bPowerSet, ui32PowerVal);
        if (status) return status;
        // Power down the clock domain last.
        if (ui32PowerVal == 0) {
            // Set the power of the clock and miscellaneous domain.
            status = PowerControl_ClockMisc(bPowerSet, ui32PowerVal);
            if (status) return status;
        }
    }

    return 0;
}



// Power control for the clock and miscellaneous domain.
int PowerControl_ClockMisc(bool bPowerSet, uint32_t ui32PowerVal)
{
    uint32_t ui32GpioGet = 0, ui32GpioSet = 0;

    // Get the power status of the clock and miscellaneous domain.
    if (!bPowerSet) {
        ui32GpioGet = GpioGet_PowerCtrl();
        if ((ui32GpioGet & POWER_CLK_MISC) == POWER_CLK_MISC) {
            UARTprintf("%s: The clock and miscellaneous power is completely ON. GPIO power = 0x%02x", UI_STR_OK, ui32GpioGet);
            return 0;
        } else if ((ui32GpioGet & POWER_CLK_MISC) == 0) {
            UARTprintf("%s: The clock and miscellaneous power is completely OFF. GPIO power = 0x%02x", UI_STR_OK, ui32GpioGet);
            return 0;
        } else {
            UARTprintf("%s: The clock and miscellaneous power is PARTIALLY ON. GPIO power = 0x%02x", UI_STR_ERROR, ui32GpioGet);
            return -1;
        }
    }

    // Power down the clock and miscellaneous domain.
    if (ui32PowerVal == 0) {
        ui32GpioGet = GpioGet_PowerCtrl();
        // Check if the FPGA is powered.
        if ((ui32GpioGet & POWER_FPGA) != 0) {
            UARTprintf("%s: Cannot power off the clock and miscellaneous domain while the FPGA is powered. Turn it off first.", UI_STR_ERROR);
            return -1;
        } else {
            ui32GpioSet = ui32GpioGet & (~POWER_CLK_MISC);
            GpioSet_PowerCtrl(ui32GpioSet);
            ui32GpioGet = GpioGet_PowerCtrl();
            if (ui32GpioGet != ui32GpioSet) {
                UARTprintf("%s: Could not power down the clock and miscellaneous domain.\n", UI_STR_ERROR);
                return -1;
            }
        }
    // Power up the clock and miscellaneous domain.
    } else {
        ui32GpioGet = GpioGet_PowerCtrl();
        ui32GpioSet = ui32GpioGet | POWER_CLK_MISC;
        GpioSet_PowerCtrl(ui32GpioSet);
        ui32GpioGet = GpioGet_PowerCtrl();
        if (ui32GpioGet != ui32GpioSet) {
            UARTprintf("%s: Could not power up the clock and miscellaneous domain.\n", UI_STR_ERROR);
            return -1;
        }
    }

    return 0;
}



// Power control for the FPGA.
int PowerControl_FPGA(bool bPowerSet, uint32_t ui32PowerVal)
{
    uint32_t ui32GpioGet = 0, ui32GpioSet = 0;

    // Get the power status of the FPGA.
    if (!bPowerSet) {
        ui32GpioGet = GpioGet_PowerCtrl();
        if ((ui32GpioGet & POWER_FPGA) == POWER_FPGA) {
            UARTprintf("%s: The FPGA power is completely ON. GPIO power = 0x%02x", UI_STR_OK, ui32GpioGet);
            return 0;
        } else if ((ui32GpioGet & POWER_FPGA) == 0) {
            UARTprintf("%s: The FPGA power is completely OFF. GPIO power = 0x%02x", UI_STR_OK, ui32GpioGet);
            return 0;
        } else {
            UARTprintf("%s: The FPGA power is PARTIALLY ON. GPIO power = 0x%02x", UI_STR_ERROR, ui32GpioGet);
            return -1;
        }
    }

    // Power down the FPGA.
    if (ui32PowerVal == 0) {
        // Power down the IO voltage first.
        ui32GpioGet = GpioGet_PowerCtrl();
        ui32GpioSet = ui32GpioGet & (~POWER_FPGA_IO);
        GpioSet_PowerCtrl(ui32GpioSet);
        ui32GpioGet = GpioGet_PowerCtrl();
        if (ui32GpioGet != ui32GpioSet) {
            UARTprintf("%s: Could not power down the FPGA IO voltage.", UI_STR_ERROR);
            return -1;
        }
        // Then power down the core.
        ui32GpioGet = GpioGet_PowerCtrl();
        ui32GpioSet = ui32GpioGet & (~POWER_FPGA_CORE);
        GpioSet_PowerCtrl(ui32GpioSet);
        ui32GpioGet = GpioGet_PowerCtrl();
        if (ui32GpioGet != ui32GpioSet) {
            UARTprintf("%s: Could not power down the FPGA core.", UI_STR_ERROR);
            return -1;
        }
    // Power up the FPGA.
    } else {
        // Power up the core first.
        ui32GpioGet = GpioGet_PowerCtrl();
        ui32GpioSet = ui32GpioGet | POWER_FPGA_CORE;
        GpioSet_PowerCtrl(ui32GpioSet);
        ui32GpioGet = GpioGet_PowerCtrl();
        if (ui32GpioGet != ui32GpioSet) {
          UARTprintf("%s: Could not power up the FPGA core.\n", UI_STR_ERROR);
          return -1;
        }
        // Then power up the FPGA IO voltage.
        ui32GpioGet = GpioGet_PowerCtrl();
        ui32GpioSet = ui32GpioGet | POWER_FPGA_IO;
        GpioSet_PowerCtrl(ui32GpioSet);
        ui32GpioGet = GpioGet_PowerCtrl();
        if (ui32GpioGet != ui32GpioSet) {
            UARTprintf("%s: Could not power up the FPGA IO voltage.\n", UI_STR_ERROR);
            return -1;
        }
    }

    return 0;
}



// Power control for the FireFly domain.
int PowerControl_FireFly(bool bPowerSet, uint32_t ui32PowerVal)
{
    uint32_t ui32GpioGet = 0, ui32GpioSet = 0;

    // Get the power status of the FireFly domain.
    if (!bPowerSet) {
        ui32GpioGet = GpioGet_PowerCtrl();
        if ((ui32GpioGet & POWER_FIREFLY) == POWER_FIREFLY) {
            UARTprintf("%s: The FireFly power is completely ON. GPIO power = 0x%02x", UI_STR_OK, ui32GpioGet);
            return 0;
        } else if ((ui32GpioGet & POWER_FIREFLY) == 0) {
            UARTprintf("%s: The FireFly power is completely OFF. GPIO power = 0x%02x", UI_STR_OK, ui32GpioGet);
            return 0;
        } else {
            UARTprintf("%s: The clock power is PARTIALLY ON. GPIO power = 0x%02x", UI_STR_ERROR, ui32GpioGet);
            return -1;
        }
    }

    // Power down the FireFly domain.
    if (ui32PowerVal == 0) {
        ui32GpioGet = GpioGet_PowerCtrl();
        ui32GpioSet = ui32GpioGet & (~POWER_FIREFLY);
        GpioSet_PowerCtrl(ui32GpioSet);
        ui32GpioGet = GpioGet_PowerCtrl();
        if (ui32GpioGet != ui32GpioSet) {
            UARTprintf("%s: Could not power down the FireFly domain.\n", UI_STR_ERROR);
            return -1;
        }
    // Power up the FireFly domain.
    } else {
        ui32GpioGet = GpioGet_PowerCtrl();
        ui32GpioSet = ui32GpioGet | POWER_FIREFLY;
        GpioSet_PowerCtrl(ui32GpioSet);
        ui32GpioGet = GpioGet_PowerCtrl();
        if (ui32GpioGet != ui32GpioSet) {
            UARTprintf("%s: Could not power up the FireFly domain.\n", UI_STR_ERROR);
            return -1;
        }
    }

    return 0;
}

