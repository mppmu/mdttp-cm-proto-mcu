// File: gpio_pins.c
// Auth: M. Fras, Electronics Division, MPI for Physics, Munich
// Mod.: M. Fras, Electronics Division, MPI for Physics, Munich
// Date: 27 May 2022
// Rev.: 03 Jun 2022
//
// GPIO pin definitions and functions for the TI Tiva TM4C1290 MCU on the ATLAS
// MDT Trigger Processor (TP) Command Module (CM) prototype.
//



#include <stdbool.h>
#include <stdint.h>
#include "inc/hw_memmap.h"
#include "driverlib/gpio.h"
#include "driverlib/sysctl.h"
#include "gpio.h"
#include "gpio_pins.h"



// ******************************************************************
// Initialize all GPIO pins.
// ******************************************************************

void GpioInit_All(void)
{
    GpioInit_SmPowerEna();
    GpioInit_CmReady();
    GpioSet_CmReady(GPIO_DEFAULT_CM_READY);
    GpioInit_LedMcuUser();
    GpioSet_LedMcuUser(GPIO_DEFAULT_LED_CM_USER);
    GpioInit_PowerCtrl();
    GpioSet_PowerCtrl(GPIO_DEFAULT_POWER_CTRL);
}



// ******************************************************************
// Service Module power enable.
// ******************************************************************

// SM_PWR_ENA: PN3, 110
tGPIO g_sGpio_SmPowerEna = {
    SYSCTL_PERIPH_GPION,
    GPIO_PORTN_BASE,
    GPIO_PIN_3,             // ui8Pins
    GPIO_STRENGTH_2MA,      // ui32Strength
    // Note: The Servie Module CM_PWR_EN signal is active high, so implement a
    //       weak pull-down on the MCU input pin.
    GPIO_PIN_TYPE_STD_WPD,  // ui32PinType
    true,                   // bInput: false = output, true = input
    GPIO_BOTH_EDGES         // ui32IntType
};

// Initialize the Service Module power enable GPIO.
void GpioInit_SmPowerEna(void)
{
    GpioInit(&g_sGpio_SmPowerEna);
}

// Read the Service Module power enable GPIO.
uint32_t GpioGet_SmPowerEna(void)
{
    uint32_t ui32Val = 0;

    ui32Val |= (GpioInputGetBool(&g_sGpio_SmPowerEna) & 0x1) << 0;

    return ui32Val;
}



// ******************************************************************
// Command Module ready.
// ******************************************************************

// CM_READY: PN2, 109
tGPIO g_sGpio_CmReady = {
    SYSCTL_PERIPH_GPION,
    GPIO_PORTN_BASE,
    GPIO_PIN_2,             // ui8Pins
    GPIO_STRENGTH_2MA,      // ui32Strength
    GPIO_PIN_TYPE_STD,      // ui32PinType
    false,                  // bInput: false = output, true = input
    0                       // ui32IntType
};

void GpioInit_CmReady(void)
{
    GpioInit(&g_sGpio_CmReady);
}

void GpioSet_CmReady(uint32_t ui32Val)
{
    GpioOutputSetBool(&g_sGpio_CmReady, (bool) (ui32Val & 0x01));
}

uint32_t GpioGet_CmReady(void)
{
    uint32_t ui32Val = 0;

    ui32Val |= (GpioOutputGetBool(&g_sGpio_CmReady) & 0x1) << 0;

    return ui32Val;
}



// ******************************************************************
// MCU user LEDs.
// ******************************************************************

// MCU_USER_LED0: PM0, 78 (LED green 0)
tGPIO g_sGpio_LedMcuUser0 = {
    SYSCTL_PERIPH_GPIOM,
    GPIO_PORTM_BASE,
    GPIO_PIN_0,             // ui8Pins
    GPIO_STRENGTH_2MA,      // ui32Strength
    GPIO_PIN_TYPE_STD,      // ui32PinType
    false,                  // bInput: false = output, true = input
    0                       // ui32IntType
};
// MCU_USER_LED1: PM1, 77 (LED green 1)
tGPIO g_sGpio_LedMcuUser1 = {
    SYSCTL_PERIPH_GPIOM,
    GPIO_PORTM_BASE,
    GPIO_PIN_1,             // ui8Pins
    GPIO_STRENGTH_2MA,      // ui32Strength
    GPIO_PIN_TYPE_STD,      // ui32PinType
    false,                  // bInput: false = output, true = input
    0                       // ui32IntType
};
// MCU_USER_LED2: PM2, 76 (LED green 2)
tGPIO g_sGpio_LedMcuUser2 = {
    SYSCTL_PERIPH_GPIOM,
    GPIO_PORTM_BASE,
    GPIO_PIN_2,             // ui8Pins
    GPIO_STRENGTH_2MA,      // ui32Strength
    GPIO_PIN_TYPE_STD,      // ui32PinType
    false,                  // bInput: false = output, true = input
    0                       // ui32IntType
};
// MCU_USER_LED3: PM3, 75 (LED blue 0)
tGPIO g_sGpio_LedMcuUser3 = {
    SYSCTL_PERIPH_GPIOM,
    GPIO_PORTM_BASE,
    GPIO_PIN_3,             // ui8Pins
    GPIO_STRENGTH_2MA,      // ui32Strength
    GPIO_PIN_TYPE_STD,      // ui32PinType
    false,                  // bInput: false = output, true = input
    0                       // ui32IntType
};
// MCU_USER_LED4: PM4, 74 (LED blue 1)
tGPIO g_sGpio_LedMcuUser4 = {
    SYSCTL_PERIPH_GPIOM,
    GPIO_PORTM_BASE,
    GPIO_PIN_4,             // ui8Pins
    GPIO_STRENGTH_2MA,      // ui32Strength
    GPIO_PIN_TYPE_STD,      // ui32PinType
    false,                  // bInput: false = output, true = input
    0                       // ui32IntType
};
// MCU_USER_LED5: PM5,73 (LED yellow 0)
tGPIO g_sGpio_LedMcuUser5 = {
    SYSCTL_PERIPH_GPIOM,
    GPIO_PORTM_BASE,
    GPIO_PIN_5,             // ui8Pins
    GPIO_STRENGTH_2MA,      // ui32Strength
    GPIO_PIN_TYPE_STD,      // ui32PinType
    false,                  // bInput: false = output, true = input
    0                       // ui32IntType
};
// MCU_USER_LED6: PM6, 72 (LED yellow 1)
tGPIO g_sGpio_LedMcuUser6 = {
    SYSCTL_PERIPH_GPIOM,
    GPIO_PORTM_BASE,
    GPIO_PIN_6,             // ui8Pins
    GPIO_STRENGTH_2MA,      // ui32Strength
    GPIO_PIN_TYPE_STD,      // ui32PinType
    false,                  // bInput: false = output, true = input
    0                       // ui32IntType
};
// MCU_USER_LED7: PM7, 71 (LED red 0)
tGPIO g_sGpio_LedMcuUser7 = {
    SYSCTL_PERIPH_GPIOM,
    GPIO_PORTM_BASE,
    GPIO_PIN_7,             // ui8Pins
    GPIO_STRENGTH_2MA,      // ui32Strength
    GPIO_PIN_TYPE_STD,      // ui32PinType
    false,                  // bInput: false = output, true = input
    0                       // ui32IntType
};
// MCU_USER_LED8: PN0, 107 (LED red 1)
tGPIO g_sGpio_LedMcuUser8 = {
    SYSCTL_PERIPH_GPION,
    GPIO_PORTN_BASE,
    GPIO_PIN_0,             // ui8Pins
    GPIO_STRENGTH_2MA,      // ui32Strength
    GPIO_PIN_TYPE_STD,      // ui32PinType
    false,                  // bInput: false = output, true = input
    0                       // ui32IntType
};

// Initialize the MCU user LEDs.
void GpioInit_LedMcuUser(void)
{
    GpioInit(&g_sGpio_LedMcuUser0);
    GpioInit(&g_sGpio_LedMcuUser1);
    GpioInit(&g_sGpio_LedMcuUser2);
    GpioInit(&g_sGpio_LedMcuUser3);
    GpioInit(&g_sGpio_LedMcuUser4);
    GpioInit(&g_sGpio_LedMcuUser5);
    GpioInit(&g_sGpio_LedMcuUser6);
    GpioInit(&g_sGpio_LedMcuUser7);
    GpioInit(&g_sGpio_LedMcuUser8);
}

// Set the MCU user LEDs.
void GpioSet_LedMcuUser(uint32_t ui32Val)
{
    GpioOutputSetBool(&g_sGpio_LedMcuUser0, (bool) (ui32Val & 0x001));
    GpioOutputSetBool(&g_sGpio_LedMcuUser1, (bool) (ui32Val & 0x002));
    GpioOutputSetBool(&g_sGpio_LedMcuUser2, (bool) (ui32Val & 0x004));
    GpioOutputSetBool(&g_sGpio_LedMcuUser3, (bool) (ui32Val & 0x008));
    GpioOutputSetBool(&g_sGpio_LedMcuUser4, (bool) (ui32Val & 0x010));
    GpioOutputSetBool(&g_sGpio_LedMcuUser5, (bool) (ui32Val & 0x020));
    GpioOutputSetBool(&g_sGpio_LedMcuUser6, (bool) (ui32Val & 0x040));
    GpioOutputSetBool(&g_sGpio_LedMcuUser7, (bool) (ui32Val & 0x080));
    GpioOutputSetBool(&g_sGpio_LedMcuUser8, (bool) (ui32Val & 0x100));
}

// Read back the MCU user LEDs.
uint32_t GpioGet_LedMcuUser(void)
{
    uint32_t ui32Val = 0;

    ui32Val |= (GpioOutputGetBool(&g_sGpio_LedMcuUser0) & 0x1) << 0;
    ui32Val |= (GpioOutputGetBool(&g_sGpio_LedMcuUser1) & 0x1) << 1;
    ui32Val |= (GpioOutputGetBool(&g_sGpio_LedMcuUser2) & 0x1) << 2;
    ui32Val |= (GpioOutputGetBool(&g_sGpio_LedMcuUser3) & 0x1) << 3;
    ui32Val |= (GpioOutputGetBool(&g_sGpio_LedMcuUser4) & 0x1) << 4;
    ui32Val |= (GpioOutputGetBool(&g_sGpio_LedMcuUser5) & 0x1) << 5;
    ui32Val |= (GpioOutputGetBool(&g_sGpio_LedMcuUser6) & 0x1) << 6;
    ui32Val |= (GpioOutputGetBool(&g_sGpio_LedMcuUser7) & 0x1) << 7;
    ui32Val |= (GpioOutputGetBool(&g_sGpio_LedMcuUser8) & 0x1) << 8;

    return ui32Val;
}



// ******************************************************************
// Power control.
// ******************************************************************

// PD_FPGA_CORE_EN: PK0, 18
tGPIO g_sGpio_PowerCtrl0 = {
    SYSCTL_PERIPH_GPIOK,
    GPIO_PORTK_BASE,
    GPIO_PIN_0,             // ui8Pins
    GPIO_STRENGTH_2MA,      // ui32Strength
    GPIO_PIN_TYPE_STD,      // ui32PinType
    false,                  // bInput: false = output, true = input
    0                       // ui32IntType
};
// PD_FPGA_IO_EN: PK1, 19
tGPIO g_sGpio_PowerCtrl1 = {
    SYSCTL_PERIPH_GPIOK,
    GPIO_PORTK_BASE,
    GPIO_PIN_1,             // ui8Pins
    GPIO_STRENGTH_2MA,      // ui32Strength
    GPIO_PIN_TYPE_STD,      // ui32PinType
    false,                  // bInput: false = output, true = input
    0                       // ui32IntType
};
// PD_MISC_EN: PK2, 20
tGPIO g_sGpio_PowerCtrl2 = {
    SYSCTL_PERIPH_GPIOK,
    GPIO_PORTK_BASE,
    GPIO_PIN_2,             // ui8Pins
    GPIO_STRENGTH_2MA,      // ui32Strength
    GPIO_PIN_TYPE_STD,      // ui32PinType
    false,                  // bInput: false = output, true = input
    0                       // ui32IntType
};
// PD_FF_EN: PK3, 21
tGPIO g_sGpio_PowerCtrl3 = {
    SYSCTL_PERIPH_GPIOK,
    GPIO_PORTK_BASE,
    GPIO_PIN_3,             // ui8Pins
    GPIO_STRENGTH_2MA,      // ui32Strength
    GPIO_PIN_TYPE_STD,      // ui32PinType
    false,                  // bInput: false = output, true = input
    0                       // ui32IntType
};
// PM1_CONTROL0: PQ0, 5
tGPIO g_sGpio_PowerCtrl4 = {
    SYSCTL_PERIPH_GPIOQ,
    GPIO_PORTQ_BASE,
    GPIO_PIN_0,             // ui8Pins
    GPIO_STRENGTH_2MA,      // ui32Strength
    GPIO_PIN_TYPE_STD,      // ui32PinType
    false,                  // bInput: false = output, true = input
    0                       // ui32IntType
};
// PM1_CONTROL1: PQ2, 11
tGPIO g_sGpio_PowerCtrl5 = {
    SYSCTL_PERIPH_GPIOQ,
    GPIO_PORTQ_BASE,
    GPIO_PIN_2,             // ui8Pins
    GPIO_STRENGTH_2MA,      // ui32Strength
    GPIO_PIN_TYPE_STD,      // ui32PinType
    false,                  // bInput: false = output, true = input
    0                       // ui32IntType
};
// PM2_CONTROL0: PQ3, 27
tGPIO g_sGpio_PowerCtrl6 = {
    SYSCTL_PERIPH_GPIOQ,
    GPIO_PORTQ_BASE,
    GPIO_PIN_3,             // ui8Pins
    GPIO_STRENGTH_2MA,      // ui32Strength
    GPIO_PIN_TYPE_STD,      // ui32PinType
    false,                  // bInput: false = output, true = input
    0                       // ui32IntType
};
// PM2_CONTROL1: PQ6, 58
tGPIO g_sGpio_PowerCtrl7 = {
    SYSCTL_PERIPH_GPIOQ,
    GPIO_PORTQ_BASE,
    GPIO_PIN_6,             // ui8Pins
    GPIO_STRENGTH_2MA,      // ui32Strength
    GPIO_PIN_TYPE_STD,      // ui32PinType
    false,                  // bInput: false = output, true = input
    0                       // ui32IntType
};

void GpioInit_PowerCtrl(void)
{
    GpioInit(&g_sGpio_PowerCtrl0);
    GpioInit(&g_sGpio_PowerCtrl1);
    GpioInit(&g_sGpio_PowerCtrl2);
    GpioInit(&g_sGpio_PowerCtrl3);
    GpioInit(&g_sGpio_PowerCtrl4);
    GpioInit(&g_sGpio_PowerCtrl5);
    GpioInit(&g_sGpio_PowerCtrl6);
    GpioInit(&g_sGpio_PowerCtrl7);
}

void GpioSet_PowerCtrl(uint32_t ui32Val)
{
    GpioOutputSetBool(&g_sGpio_PowerCtrl0, (bool) (ui32Val & 0x01));
    GpioOutputSetBool(&g_sGpio_PowerCtrl1, (bool) (ui32Val & 0x02));
    GpioOutputSetBool(&g_sGpio_PowerCtrl2, (bool) (ui32Val & 0x04));
    GpioOutputSetBool(&g_sGpio_PowerCtrl3, (bool) (ui32Val & 0x08));
    GpioOutputSetBool(&g_sGpio_PowerCtrl4, (bool) (ui32Val & 0x10));
    GpioOutputSetBool(&g_sGpio_PowerCtrl5, (bool) (ui32Val & 0x20));
    GpioOutputSetBool(&g_sGpio_PowerCtrl6, (bool) (ui32Val & 0x40));
    GpioOutputSetBool(&g_sGpio_PowerCtrl7, (bool) (ui32Val & 0x80));
}

uint32_t GpioGet_PowerCtrl(void)
{
    uint32_t ui32Val = 0;

    ui32Val |= (GpioOutputGetBool(&g_sGpio_PowerCtrl0) & 0x1) << 0;
    ui32Val |= (GpioOutputGetBool(&g_sGpio_PowerCtrl1) & 0x1) << 1;
    ui32Val |= (GpioOutputGetBool(&g_sGpio_PowerCtrl2) & 0x1) << 2;
    ui32Val |= (GpioOutputGetBool(&g_sGpio_PowerCtrl3) & 0x1) << 3;
    ui32Val |= (GpioOutputGetBool(&g_sGpio_PowerCtrl4) & 0x1) << 4;
    ui32Val |= (GpioOutputGetBool(&g_sGpio_PowerCtrl5) & 0x1) << 5;
    ui32Val |= (GpioOutputGetBool(&g_sGpio_PowerCtrl6) & 0x1) << 6;
    ui32Val |= (GpioOutputGetBool(&g_sGpio_PowerCtrl7) & 0x1) << 7;

    return ui32Val;
}

