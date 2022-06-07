// File: cm_mcu_hwtest_aux.c
// Auth: M. Fras, Electronics Division, MPI for Physics, Munich
// Mod.: M. Fras, Electronics Division, MPI for Physics, Munich
// Date: 03 Jun 2022
// Rev.: 03 Jun 2022
//
// Auxiliary functions of the hardware test firmware running on the ATLAS MDT
// Trigger Processor (TP) Command Module (CM) prototype MCU.
//



#include <stdbool.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <strings.h>
#include "inc/hw_nvic.h"
#include "inc/hw_types.h"
#include "driverlib/i2c.h"
#include "driverlib/rom.h"
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
#include "cm_mcu_hwtest_aux.h"
#include "cm_mcu_hwtest_io.h"



// Global variables.
extern uint32_t g_ui32SysClock;
extern tUartUi *g_psUartUi;



// Delay execution for a given number of microseconds.
int DelayUs(uint32_t ui32DelayUs)
{
    // Limit the delay to max. 10 seconds.
    if (ui32DelayUs > 1e7) ui32DelayUs = 1e7;
    // CAUTION: Calling SysCtlDelay(0) will hang the system.
    if (ui32DelayUs > 0)
        // Note: The SysCtlDelay executes a simple 3 instruction cycle loop.
        SysCtlDelay((g_ui32SysClock / 3e6) * ui32DelayUs);

    return 0;
}



// Delay execution for a given number of microseconds.
int DelayUsCmd(char *pcCmd, char *pcParam)
{
    uint32_t ui32DelayUs;

    if (pcParam == NULL) {
        UARTprintf("%s: Parameter required after command `%s'.", UI_STR_ERROR, pcCmd);
        return -1;
    }
    ui32DelayUs = strtoul(pcParam, (char **) NULL, 0);
    // Limit the delay to max. 10 seconds.
    if (ui32DelayUs > 1e7) ui32DelayUs = 1e7;
    // CAUTION: Calling SysCtlDelay(0) will hang the system.
    if (ui32DelayUs > 0)
        // Note: The SysCtlDelay executes a simple 3 instruction cycle loop.
        SysCtlDelay((g_ui32SysClock / 3e6) * ui32DelayUs);

    UARTprintf("%s.", UI_STR_OK);

    return 0;
}



// Reset the MCU.
int McuReset(char *pcCmd, char *pcParam)
{
    char pcUartStr[4];

    UARTprintf("Do you really want to reset the MCU (yes/no)? ");
    UARTgets(pcUartStr, 4);

    if (!strcasecmp(pcUartStr, "yes")) {
        UARTprintf("%s. Resetting the MCU.", UI_STR_OK);
        // Wait some time for the UART to send out the last message.
        SysCtlDelay((g_ui32SysClock / 3e6) * 1e5);

        SysCtlReset();
    } else {
        UARTprintf("Reset aborted.");
    }

    return 0;
}



// Passes control to the boot loader and initiates a remote software update.
// This function is based on the EK-TM4C1294XL boot_demo1 example.
int JumpToBootLoader(char *pcCmd, char *pcParam)
{
    char pcUartStr[4];

    UARTprintf("Do you really want to jump to the serial boot loader (yes/no)? ");
    UARTgets(pcUartStr, 4);

    if (!strcasecmp(pcUartStr, "yes")) {
        UARTprintf("%s. Entering the serial boot loader on UART %d.\n", UI_STR_OK, g_psUartUi->ui32Port);
        // Wait some time for the UART to send out the last message.
        SysCtlDelay((g_ui32SysClock / 3e6) * 1e5);

        // Code copied from the EK-TM4C1294XL boot_demo1 example.

        // We must make sure we turn off SysTick and its interrupt before entering 
        // the boot loader!
        MAP_SysTickIntDisable(); 
        MAP_SysTickDisable(); 

        // Disable all processor interrupts.  Instead of disabling them
        // one at a time, a direct write to NVIC is done to disable all
        // peripheral interrupts.
        HWREG(NVIC_DIS0) = 0xffffffff;
        HWREG(NVIC_DIS1) = 0xffffffff;
        HWREG(NVIC_DIS2) = 0xffffffff;
        HWREG(NVIC_DIS3) = 0xffffffff;

        // Return control to the boot loader.  This is a call to the SVC
        // handler in the boot loader.
        (*((void (*)(void))(*(uint32_t *)0x2c)))();
    } else {
        UARTprintf("Operation aborted.");
    }

    return 0;
}



// Update the status LEDs.
int LedCmStatusUpdated(void)
{
    uint32_t ui32LedCmStatus = 0;

    // Temperature alert.
    // TODO.
    ui32LedCmStatus &= ~LED_CM_STATUS_TEMP_ALERT;
    GpioSet_LedCmStatus(ui32LedCmStatus);

    return 0;
}

