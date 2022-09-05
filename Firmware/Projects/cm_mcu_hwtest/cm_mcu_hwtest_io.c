// File: cm_mcu_hwtest_io.c
// Auth: M. Fras, Electronics Division, MPI for Physics, Munich
// Mod.: M. Fras, Electronics Division, MPI for Physics, Munich
// Date: 03 Jun 2022
// Rev.: 05 Sep 2022
//
// IO peripheral definitions of the firmware running on the ATLAS MDT Trigger
// Processor (TP) Command Module (CM) prototype MCU.
//



#include <stdbool.h>
#include <stdint.h>
#include "inc/hw_memmap.h"
#include "driverlib/gpio.h"
#include "driverlib/i2c.h"
#include "driverlib/pin_map.h"
#include "driverlib/sysctl.h"
#include "driverlib/uart.h"
#include "cm_mcu_hwtest_io.h"



// ******************************************************************
// UART user inferface (UI).
// ******************************************************************

// UART 1: MCU_UART0 (UART of the IPMC on the SM).
// GPIO Pins:
// - RX: PQ4, 102
// - TX: PQ5, 57
tUartUi g_sUartUi1 = {
    SYSCTL_PERIPH_UART1,
    SYSCTL_PERIPH_GPIOQ,
    GPIO_PORTQ_BASE,
    GPIO_PIN_4,             // RX
    GPIO_PIN_5,             // TX
    GPIO_PQ4_U1RX,          // RX
    GPIO_PQ5_U1TX,          // TX
    UART1_BASE,
    0,                      // ui32SrcClock
    115200,                 // ui32Baud
    1                       // ui32Port
};

// UART 3: MCU_UART1 (Front panel Mini-USB port).
// GPIO Pins:
// - RX: PJ0, 116
// - TX: PJ1, 117
tUartUi g_sUartUi3 = {
    SYSCTL_PERIPH_UART3,
    SYSCTL_PERIPH_GPIOJ,
    GPIO_PORTJ_BASE,
    GPIO_PIN_0,             // RX
    GPIO_PIN_1,             // TX
    GPIO_PJ0_U3RX,          // RX
    GPIO_PJ1_U3TX,          // TX
    UART3_BASE,             // ui32Base
    0,                      // ui32SrcClock
    115200,                 // ui32Baud
    3                       // ui32Port
};

// UART 5: MCU_UART2 (UART of the Zynq SoM on the SM).
// GPIO Pins:
// - RX: PC6/C0+, 23
// - TX: PC7/C0-, 22
tUartUi g_sUartUi5 = {
    SYSCTL_PERIPH_UART5,
    SYSCTL_PERIPH_GPIOC,
    GPIO_PORTC_BASE,
    GPIO_PIN_6,             // RX
    GPIO_PIN_7,             // TX
    GPIO_PC6_U5RX,          // RX
    GPIO_PC7_U5TX,          // TX
    UART5_BASE,
    0,                      // ui32SrcClock
    115200,                 // ui32Baud
    5                       // ui32Port
};



// ******************************************************************
// I2C masters.
// ******************************************************************

// List of valied I2C master ports.
uint8_t g_ui8I2CMasterPorts[I2C_MASTER_NUM] = {1, 2, 3, 4, 5, 6, 7, 8};

// Array of all I2C master ports.
tI2C g_psI2C[I2C_MASTER_NUM] = {
    {
        // I2C master 1: PM (Power Modules: 2 x LTC2977, 2 x LTM4700).
        // GPIO Pins:
        // - SCL: PG0, 49
        // - SDA: PG1, 50
        SYSCTL_PERIPH_I2C1,
        SYSCTL_PERIPH_GPIOG,
        GPIO_PORTG_BASE,
        GPIO_PIN_0,             // SCL
        GPIO_PIN_1,             // SDA
        GPIO_PG0_I2C1SCL,       // SCL
        GPIO_PG1_I2C1SDA,       // SDA
        I2C1_BASE,
        0,                      // ui32I2CClk
        false,                  // false = 100 kbps; true = 400 kbps
        I2C_MASTER_INT_ARB_LOST | I2C_MASTER_INT_STOP | I2C_MASTER_INT_START |
            I2C_MASTER_INT_NACK | I2C_MASTER_INT_TIMEOUT | I2C_MASTER_INT_DATA,
        100                     // ui32Timeout
    },
    {
        // I2C master 2: FF (10 x FireFly modules with 3 x PCA9545APW I2C bus switches).
        // GPIO Pins:
        // - SCL: PG2, 51
        // - SDA: PG3, 52
        SYSCTL_PERIPH_I2C2,
        SYSCTL_PERIPH_GPIOG,
        GPIO_PORTG_BASE,
        GPIO_PIN_2,             // SCL
        GPIO_PIN_3,             // SDA
        GPIO_PG2_I2C2SCL,       // SCL
        GPIO_PG3_I2C2SDA,       // SDA
        I2C2_BASE,
        0,                      // ui32I2CClk
        false,                  // false = 100 kbps; true = 400 kbps
        I2C_MASTER_INT_ARB_LOST | I2C_MASTER_INT_STOP | I2C_MASTER_INT_START |
            I2C_MASTER_INT_NACK | I2C_MASTER_INT_TIMEOUT | I2C_MASTER_INT_DATA,
        100                     // ui32Timeout
    },
    {
        // I2C master 3: CLK (Clock generators and jitter cleaners with PCA9545APW I2C bus switch plus
        //                    their control and status signals via 4 x PCA9535BS I2C GPIO expanders).
        // GPIO Pins:
        // - SCL: PG4, 53
        // - SDA: PG5, 54
        SYSCTL_PERIPH_I2C3,
        SYSCTL_PERIPH_GPIOG,
        GPIO_PORTG_BASE,
        GPIO_PIN_4,             // SCL
        GPIO_PIN_5,             // SDA
        GPIO_PG4_I2C3SCL,       // SCL
        GPIO_PG5_I2C3SDA,       // SDA
        I2C3_BASE,
        0,                      // ui32I2CClk
        false,                  // false = 100 kbps; true = 400 kbps
        I2C_MASTER_INT_ARB_LOST | I2C_MASTER_INT_STOP | I2C_MASTER_INT_START |
            I2C_MASTER_INT_NACK | I2C_MASTER_INT_TIMEOUT | I2C_MASTER_INT_DATA,
        100                     // ui32Timeout
    },
    {
        // I2C master 4: SENS (Serial number chip DS28CM00R and 3 x MCP9902 temperature sensors).
        // GPIO Pins:
        // - SCL: PG6, 55
        // - SDA: PG7, 56
        SYSCTL_PERIPH_I2C4,
        SYSCTL_PERIPH_GPIOG,
        GPIO_PORTG_BASE,
        GPIO_PIN_6,             // SCL
        GPIO_PIN_7,             // SDA
        GPIO_PG6_I2C4SCL,       // SCL
        GPIO_PG7_I2C4SDA,       // SDA
        I2C4_BASE,
        0,                      // ui32I2CClk
        false,                  // false = 100 kbps; true = 400 kbps
        I2C_MASTER_INT_ARB_LOST | I2C_MASTER_INT_STOP | I2C_MASTER_INT_START |
            I2C_MASTER_INT_NACK | I2C_MASTER_INT_TIMEOUT | I2C_MASTER_INT_DATA,
        100                     // ui32Timeout
    },
    {
        // I2C master 5: MISC (Control and status signals of FireFly modules via 4 x PCA9535BS I2C GPIO expanders).
        // GPIO Pins:
        // - SCL: PB0/USB0ID, 95
        // - SDA: PB1/USB0VBUS, 96
        SYSCTL_PERIPH_I2C5,
        SYSCTL_PERIPH_GPIOB,
        GPIO_PORTB_BASE,
        GPIO_PIN_0,             // SCL
        GPIO_PIN_1,             // SDA
        GPIO_PB0_I2C5SCL,       // SCL
        GPIO_PB1_I2C5SDA,       // SDA
        I2C5_BASE,
        0,                      // ui32I2CClk
        false,                  // false = 100 kbps; true = 400 kbps
        I2C_MASTER_INT_ARB_LOST | I2C_MASTER_INT_STOP | I2C_MASTER_INT_START |
            I2C_MASTER_INT_NACK | I2C_MASTER_INT_TIMEOUT | I2C_MASTER_INT_DATA,
        100                     // ui32Timeout
    },
    {
        // I2C master 6: SYSMON (Xilinx System Monitor of the VU13P FPGA via PCA9517ADP level translator).
        // GPIO Pins:
        // - SCL: PA6, 40
        // - SDA: PA7, 41
        SYSCTL_PERIPH_I2C6,
        SYSCTL_PERIPH_GPIOA,
        GPIO_PORTA_BASE,
        GPIO_PIN_6,             // SCL
        GPIO_PIN_7,             // SDA
        GPIO_PA6_I2C6SCL,       // SCL
        GPIO_PA7_I2C6SDA,       // SDA
        I2C6_BASE,
        0,                      // ui32I2CClk
        false,                  // false = 100 kbps; true = 400 kbps
        I2C_MASTER_INT_ARB_LOST | I2C_MASTER_INT_STOP | I2C_MASTER_INT_START |
            I2C_MASTER_INT_NACK | I2C_MASTER_INT_TIMEOUT | I2C_MASTER_INT_DATA,
        100                     // ui32Timeout
    },
    {
        // I2C master 7: SM (SM IPMC).
        // GPIO Pins:
        // - SCL: PD0/AIN15, 1
        // - SDA: PD1/AIN14, 2
        SYSCTL_PERIPH_I2C7,
        SYSCTL_PERIPH_GPIOD,
        GPIO_PORTD_BASE,
        GPIO_PIN_0,             // SCL
        GPIO_PIN_1,             // SDA
        GPIO_PD0_I2C7SCL,       // SCL
        GPIO_PD1_I2C7SDA,       // SDA
        I2C7_BASE,
        0,                      // ui32I2CClk
        false,                  // false = 100 kbps; true = 400 kbps
        I2C_MASTER_INT_ARB_LOST | I2C_MASTER_INT_STOP | I2C_MASTER_INT_START |
            I2C_MASTER_INT_NACK | I2C_MASTER_INT_TIMEOUT | I2C_MASTER_INT_DATA,
        100                     // ui32Timeout
    },
    {
        // I2C master 8: FPGA (VU13P FPGA user logic I2C connection via PCA9517ADP level translator).
        // GPIO Pins:
        // - SCL: PD2/AIN13, 3
        // - SDA: PD3/AIN12, 4
        SYSCTL_PERIPH_I2C8,
        SYSCTL_PERIPH_GPIOD,
        GPIO_PORTD_BASE,
        GPIO_PIN_2,             // SCL
        GPIO_PIN_3,             // SDA
        GPIO_PD2_I2C8SCL,       // SCL
        GPIO_PD3_I2C8SDA,       // SDA
        I2C8_BASE,
        0,                      // ui32I2CClk
        false,                  // false = 100 kbps; true = 400 kbps
        I2C_MASTER_INT_ARB_LOST | I2C_MASTER_INT_STOP | I2C_MASTER_INT_START |
            I2C_MASTER_INT_NACK | I2C_MASTER_INT_TIMEOUT | I2C_MASTER_INT_DATA,
        100                     // ui32Timeout
    }
};



// ******************************************************************
// UARTs.
// ******************************************************************

// UART 1: MCU_UART0 (UART of the IPMC on the SM).
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

// UART 3: MCU_UART1 (Front panel Mini-USB port).
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

// UART 5: MCU_UART2 (UART of the Zynq SoM on the SM).
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

