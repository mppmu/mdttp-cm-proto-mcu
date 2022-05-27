// File: bl_user_io.c
// Auth: M. Fras, Electronics Division, MPI for Physics, Munich
// Mod.: M. Fras, Electronics Division, MPI for Physics, Munich
// Date: 27 Aug 2020
// Rev.: 28 Aug 2020
//
// IO peripheral definitions of the boot loader running on the ATLAS MDT
// Trigger Processor (TP) Command Module (CM) MCU.
//



#include <stdbool.h>
#include <stdint.h>
#include "inc/hw_memmap.h"
#include "driverlib/gpio.h"
#include "driverlib/pin_map.h"
#include "driverlib/sysctl.h"
#include "driverlib/uart.h"
#include "bl_user_io.h"



// ******************************************************************
// UARTs.
// ******************************************************************

// UART 1: MCU_UART0 (Front panel Mini-USB port and UART 0 of ZU11EG PS (console)).
// GPIO Pins:
// - RX: PQ4, 102
// - TX: PQ5, 57
tUART g_sUart1 = {
    SYSCTL_PERIPH_UART1,
    SYSCTL_PERIPH_GPIOQ,
    GPIO_PORTQ_BASE,
    GPIO_PIN_4,             // RX
    GPIO_PIN_5,             // TX
    GPIO_PQ4_U1RX,          // RX
    GPIO_PQ5_U1TX,          // TX
    UART1_BASE,
    0,                      // ui32UartClk
    115200,                 // ui32Baud
    UART_CONFIG_WLEN_8 | UART_CONFIG_STOP_ONE | UART_CONFIG_PAR_NONE,
    false                   // bLoopback
};

// UART 3: MCU_UART1 (Front panel Mini-USB port and UART UART of IPMC).
// GPIO Pins:
// - RX: PJ0, 116
// - TX: PJ1, 117
tUART g_sUart3 = {
    SYSCTL_PERIPH_UART3,
    SYSCTL_PERIPH_GPIOJ,
    GPIO_PORTJ_BASE,
    GPIO_PIN_0,             // RX
    GPIO_PIN_1,             // TX
    GPIO_PJ0_U3RX,          // RX
    GPIO_PJ1_U3TX,          // TX
    UART3_BASE,             // ui32Base
    0,                      // ui32UartClk
    115200,                 // ui32Baud
    UART_CONFIG_WLEN_8 | UART_CONFIG_STOP_ONE | UART_CONFIG_PAR_NONE,
    false                   // bLoopback
};

// UART 5: MCU_UART2 (UART of Zynq SoM on SM and UART 1 of ZU11EG PS).
// GPIO Pins:
// - RX: PC6/C0+, 23
// - TX: PC7/C0-, 22
tUART g_sUart5 = {
    SYSCTL_PERIPH_UART5,
    SYSCTL_PERIPH_GPIOC,
    GPIO_PORTC_BASE,
    GPIO_PIN_6,             // RX
    GPIO_PIN_7,             // TX
    GPIO_PC6_U5RX,          // RX
    GPIO_PC7_U5TX,          // TX
    UART5_BASE,
    0,                      // ui32UartClk
    115200,                 // ui32Baud
    UART_CONFIG_WLEN_8 | UART_CONFIG_STOP_ONE | UART_CONFIG_PAR_NONE,
    false                   // bLoopback
};

