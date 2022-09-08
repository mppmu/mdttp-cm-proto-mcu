// File: gpio_pins.c
// Auth: M. Fras, Electronics Division, MPI for Physics, Munich
// Mod.: M. Fras, Electronics Division, MPI for Physics, Munich
// Date: 27 May 2022
// Rev.: 08 Sep 2022
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
    GpioInit_SmPsReset();
    GpioInit_SmGpio();
    GpioSet_SmGpio(GPIO_DEFAULT_SM_GPIO);
    GpioInit_LedCmStatus();
    GpioSet_LedCmStatus(GPIO_DEFAULT_LED_CM_STATUS);    
    GpioInit_LedMcuUser();
    GpioSet_LedMcuUser(GPIO_DEFAULT_LED_CM_USER);
    GpioInit_PowerCtrl();
    GpioSet_PowerCtrl(GPIO_DEFAULT_POWER_CTRL);
    GpioInit_PowerGood();
    GpioInit_PowerFault();
    GpioInit_PowerI2CAlert();
    GpioInit_PowerReservedCtrl();
    GpioSet_PowerReservedCtrl(GPIO_DEFAULT_POWER_RESERVED_CTRL);
    GpioInit_TempAlert();
    GpioInit_FPGACtrlStat();
    GpioSet_FPGACtrlStat(GPIO_DEFAULT_FPGA_CTRL_STAT);
    GpioInit_I2CReset();
    GpioSet_I2CReset(GPIO_DEFAULT_I2C_RESET);
    GpioInit_I2CInt();
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
// Service Module PS reset.
// ******************************************************************

// SM_PS_RST: PA2, 35
tGPIO g_sGpio_SmPsReset = {
    SYSCTL_PERIPH_GPIOA,
    GPIO_PORTA_BASE,
    GPIO_PIN_2,             // ui8Pins
    GPIO_STRENGTH_2MA,      // ui32Strength
    GPIO_PIN_TYPE_STD_WPD,  // ui32PinType
    true,                   // bInput: false = output, true = input
    GPIO_BOTH_EDGES         // ui32IntType
};

void GpioInit_SmPsReset(void)
{
    GpioInit(&g_sGpio_SmPsReset);
}

uint32_t GpioGet_SmPsReset(void)
{
    uint32_t ui32Val = 0;

    ui32Val |= (GpioOutputGetBool(&g_sGpio_SmPsReset) & 0x1) << 0;

    return ui32Val;
}



// ******************************************************************
// Service Module spare GPIO.
// ******************************************************************

// SM_GPIO1: PN4, 111
tGPIO g_sGpio_SmGpio0 = {
    SYSCTL_PERIPH_GPION,
    GPIO_PORTN_BASE,
    GPIO_PIN_4,             // ui8Pins
    GPIO_STRENGTH_2MA,      // ui32Strength
    GPIO_PIN_TYPE_OD,       // ui32PinType
    false,                  // bInput: false = output, true = input
    0                       // ui32IntType
};
// SM_GPIO2: PN5, 112
tGPIO g_sGpio_SmGpio1 = {
    SYSCTL_PERIPH_GPION,
    GPIO_PORTN_BASE,
    GPIO_PIN_5,             // ui8Pins
    GPIO_STRENGTH_2MA,      // ui32Strength
    GPIO_PIN_TYPE_OD,       // ui32PinType
    false,                  // bInput: false = output, true = input
    0                       // ui32IntType
};

void GpioInit_SmGpio(void)
{
    GpioInit(&g_sGpio_SmGpio0);
    GpioInit(&g_sGpio_SmGpio1);
}

void GpioSet_SmGpio(uint32_t ui32Val)
{
    GpioOutputSetBool(&g_sGpio_SmGpio0, (bool) (ui32Val & 0x01));
    GpioOutputSetBool(&g_sGpio_SmGpio1, (bool) (ui32Val & 0x02));
}

uint32_t GpioGet_SmGpio(void)
{
    uint32_t ui32Val = 0;

    ui32Val |= (GpioOutputGetBool(&g_sGpio_SmGpio0) & 0x1) << 0;
    ui32Val |= (GpioOutputGetBool(&g_sGpio_SmGpio1) & 0x1) << 1;

    return ui32Val;
}



// ******************************************************************
// Command Module status LEDs.
// ******************************************************************

// TEMP_ERROR: PQ1, 6
tGPIO g_sGpio_LedCmStatus0 = {
    SYSCTL_PERIPH_GPIOQ,
    GPIO_PORTQ_BASE,
    GPIO_PIN_1,             // ui8Pins
    GPIO_STRENGTH_2MA,      // ui32Strength
    GPIO_PIN_TYPE_STD,      // ui32PinType
    false,                  // bInput: false = output, true = input
    0                       // ui32IntType
};

void GpioInit_LedCmStatus(void)
{
    GpioInit(&g_sGpio_LedCmStatus0);
}

void GpioSet_LedCmStatus(uint32_t ui32Val)
{
    GpioOutputSetBool(&g_sGpio_LedCmStatus0, (bool) (ui32Val & 0x01));
}

uint32_t GpioGet_LedCmStatus(void)
{
    uint32_t ui32Val = 0;

    ui32Val |= (GpioOutputGetBool(&g_sGpio_LedCmStatus0) & 0x1) << 0;

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
    GpioOutputSetBool(&g_sGpio_LedMcuUser0, ! (bool) (ui32Val & 0x001));
    GpioOutputSetBool(&g_sGpio_LedMcuUser1, ! (bool) (ui32Val & 0x002));
    GpioOutputSetBool(&g_sGpio_LedMcuUser2, ! (bool) (ui32Val & 0x004));
    GpioOutputSetBool(&g_sGpio_LedMcuUser3, ! (bool) (ui32Val & 0x008));
    GpioOutputSetBool(&g_sGpio_LedMcuUser4, ! (bool) (ui32Val & 0x010));
    GpioOutputSetBool(&g_sGpio_LedMcuUser5, ! (bool) (ui32Val & 0x020));
    GpioOutputSetBool(&g_sGpio_LedMcuUser6, ! (bool) (ui32Val & 0x040));
    GpioOutputSetBool(&g_sGpio_LedMcuUser7, ! (bool) (ui32Val & 0x080));
    GpioOutputSetBool(&g_sGpio_LedMcuUser8, ! (bool) (ui32Val & 0x100));
}

// Read back the MCU user LEDs.
uint32_t GpioGet_LedMcuUser(void)
{
    uint32_t ui32Val = 0;

    ui32Val |= (!(GpioOutputGetBool(&g_sGpio_LedMcuUser0) & 0x1)) << 0;
    ui32Val |= (!(GpioOutputGetBool(&g_sGpio_LedMcuUser1) & 0x1)) << 1;
    ui32Val |= (!(GpioOutputGetBool(&g_sGpio_LedMcuUser2) & 0x1)) << 2;
    ui32Val |= (!(GpioOutputGetBool(&g_sGpio_LedMcuUser3) & 0x1)) << 3;
    ui32Val |= (!(GpioOutputGetBool(&g_sGpio_LedMcuUser4) & 0x1)) << 4;
    ui32Val |= (!(GpioOutputGetBool(&g_sGpio_LedMcuUser5) & 0x1)) << 5;
    ui32Val |= (!(GpioOutputGetBool(&g_sGpio_LedMcuUser6) & 0x1)) << 6;
    ui32Val |= (!(GpioOutputGetBool(&g_sGpio_LedMcuUser7) & 0x1)) << 7;
    ui32Val |= (!(GpioOutputGetBool(&g_sGpio_LedMcuUser8) & 0x1)) << 8;

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



// ******************************************************************
// Power good signals.
// ******************************************************************

// P0V85_PGOOD: PL0, 81
tGPIO g_sGpio_PowerGood0 = {
    SYSCTL_PERIPH_GPIOL,
    GPIO_PORTL_BASE,
    GPIO_PIN_0,             // ui8Pins
    GPIO_STRENGTH_2MA,      // ui32Strength
    GPIO_PIN_TYPE_STD_WPU,  // ui32PinType
    true,                   // bInput: false = output, true = input
    GPIO_BOTH_EDGES         // ui32IntType
};
// P1V8_FPGA_PGOOD: PL1, 82
tGPIO g_sGpio_PowerGood1 = {
    SYSCTL_PERIPH_GPIOL,
    GPIO_PORTL_BASE,
    GPIO_PIN_1,             // ui8Pins
    GPIO_STRENGTH_2MA,      // ui32Strength
    GPIO_PIN_TYPE_STD_WPU,  // ui32PinType
    true,                   // bInput: false = output, true = input
    GPIO_BOTH_EDGES         // ui32IntType
};
// P1V8_MISC_PGOOD: PL2, 83
tGPIO g_sGpio_PowerGood2 = {
    SYSCTL_PERIPH_GPIOL,
    GPIO_PORTL_BASE,
    GPIO_PIN_2,             // ui8Pins
    GPIO_STRENGTH_2MA,      // ui32Strength
    GPIO_PIN_TYPE_STD_WPU,  // ui32PinType
    true,                   // bInput: false = output, true = input
    GPIO_BOTH_EDGES         // ui32IntType
};
// P0V9_MGT_PGOOD: PL3, 84
tGPIO g_sGpio_PowerGood3 = {
    SYSCTL_PERIPH_GPIOL,
    GPIO_PORTL_BASE,
    GPIO_PIN_3,             // ui8Pins
    GPIO_STRENGTH_2MA,      // ui32Strength
    GPIO_PIN_TYPE_STD_WPU,  // ui32PinType
    true,                   // bInput: false = output, true = input
    GPIO_BOTH_EDGES         // ui32IntType
};
// P1V2_MGT_PGOOD: PL4, 85
tGPIO g_sGpio_PowerGood4 = {
    SYSCTL_PERIPH_GPIOL,
    GPIO_PORTL_BASE,
    GPIO_PIN_4,             // ui8Pins
    GPIO_STRENGTH_2MA,      // ui32Strength
    GPIO_PIN_TYPE_STD_WPU,  // ui32PinType
    true,                   // bInput: false = output, true = input
    GPIO_BOTH_EDGES         // ui32IntType
};
// P3V3_MISC_PGOOD: PL5, 86
tGPIO g_sGpio_PowerGood5 = {
    SYSCTL_PERIPH_GPIOL,
    GPIO_PORTL_BASE,
    GPIO_PIN_5,             // ui8Pins
    GPIO_STRENGTH_2MA,      // ui32Strength
    GPIO_PIN_TYPE_STD_WPU,  // ui32PinType
    true,                   // bInput: false = output, true = input
    GPIO_BOTH_EDGES         // ui32IntType
};
// P3V3_FF_PGOOD: PL6, 94
tGPIO g_sGpio_PowerGood6 = {
    SYSCTL_PERIPH_GPIOL,
    GPIO_PORTL_BASE,
    GPIO_PIN_6,             // ui8Pins
    GPIO_STRENGTH_2MA,      // ui32Strength
    GPIO_PIN_TYPE_STD_WPU,  // ui32PinType
    true,                   // bInput: false = output, true = input
    GPIO_BOTH_EDGES         // ui32IntType
};
// P5V_MISC_PGOOD: PL7, 93
tGPIO g_sGpio_PowerGood7 = {
    SYSCTL_PERIPH_GPIOL,
    GPIO_PORTL_BASE,
    GPIO_PIN_7,             // ui8Pins
    GPIO_STRENGTH_2MA,      // ui32Strength
    GPIO_PIN_TYPE_STD_WPU,  // ui32PinType
    true,                   // bInput: false = output, true = input
    GPIO_BOTH_EDGES         // ui32IntType
};
// LTC2977_1_PGOOD: PK6, 60
tGPIO g_sGpio_PowerGood8 = {
    SYSCTL_PERIPH_GPIOK,
    GPIO_PORTK_BASE,
    GPIO_PIN_6,             // ui8Pins
    GPIO_STRENGTH_2MA,      // ui32Strength
    GPIO_PIN_TYPE_STD_WPU,  // ui32PinType
    true,                   // bInput: false = output, true = input
    GPIO_BOTH_EDGES         // ui32IntType
};
// LTC2977_2_PGOOD: PK7, 59
tGPIO g_sGpio_PowerGood9 = {
    SYSCTL_PERIPH_GPIOK,
    GPIO_PORTK_BASE,
    GPIO_PIN_7,             // ui8Pins
    GPIO_STRENGTH_2MA,      // ui32Strength
    GPIO_PIN_TYPE_STD_WPU,  // ui32PinType
    true,                   // bInput: false = output, true = input
    GPIO_BOTH_EDGES         // ui32IntType
};

void GpioInit_PowerGood(void)
{
    GpioInit(&g_sGpio_PowerGood0);
    GpioInit(&g_sGpio_PowerGood1);
    GpioInit(&g_sGpio_PowerGood2);
    GpioInit(&g_sGpio_PowerGood3);
    GpioInit(&g_sGpio_PowerGood4);
    GpioInit(&g_sGpio_PowerGood5);
    GpioInit(&g_sGpio_PowerGood6);
    GpioInit(&g_sGpio_PowerGood7);
    GpioInit(&g_sGpio_PowerGood8);
    GpioInit(&g_sGpio_PowerGood9);
}

uint32_t GpioGet_PowerGood(void)
{
    uint32_t ui32Val = 0;

    ui32Val |= (GpioOutputGetBool(&g_sGpio_PowerGood0) & 0x1) << 0;
    ui32Val |= (GpioOutputGetBool(&g_sGpio_PowerGood1) & 0x1) << 1;
    ui32Val |= (GpioOutputGetBool(&g_sGpio_PowerGood2) & 0x1) << 2;
    ui32Val |= (GpioOutputGetBool(&g_sGpio_PowerGood3) & 0x1) << 3;
    ui32Val |= (GpioOutputGetBool(&g_sGpio_PowerGood4) & 0x1) << 4;
    ui32Val |= (GpioOutputGetBool(&g_sGpio_PowerGood5) & 0x1) << 5;
    ui32Val |= (GpioOutputGetBool(&g_sGpio_PowerGood6) & 0x1) << 6;
    ui32Val |= (GpioOutputGetBool(&g_sGpio_PowerGood7) & 0x1) << 7;
    ui32Val |= (GpioOutputGetBool(&g_sGpio_PowerGood8) & 0x1) << 8;
    ui32Val |= (GpioOutputGetBool(&g_sGpio_PowerGood9) & 0x1) << 9;

    return ui32Val;
}



// ******************************************************************
// Power fault signals.
// ******************************************************************

// P0V85_FAULTn: PF4, 46
tGPIO g_sGpio_PowerFault0 = {
    SYSCTL_PERIPH_GPIOF,
    GPIO_PORTF_BASE,
    GPIO_PIN_4,             // ui8Pins
    GPIO_STRENGTH_2MA,      // ui32Strength
    GPIO_PIN_TYPE_STD_WPU,  // ui32PinType
    true,                   // bInput: false = output, true = input
    GPIO_BOTH_EDGES         // ui32IntType
};

void GpioInit_PowerFault(void)
{
    GpioInit(&g_sGpio_PowerFault0);
}

uint32_t GpioGet_PowerFault(void)
{
    uint32_t ui32Val = 0;

    ui32Val |= (GpioOutputGetBool(&g_sGpio_PowerFault0) & 0x1) << 0;

    return ui32Val;
}



// ******************************************************************
// Power I2C alert signals.
// ******************************************************************

// I2C_PM_ALERTn: PF3, 45
tGPIO g_sGpio_PowerI2CAlert0 = {
    SYSCTL_PERIPH_GPIOF,
    GPIO_PORTF_BASE,
    GPIO_PIN_3,             // ui8Pins
    GPIO_STRENGTH_2MA,      // ui32Strength
    GPIO_PIN_TYPE_STD_WPU,  // ui32PinType
    true,                   // bInput: false = output, true = input
    GPIO_BOTH_EDGES         // ui32IntType
};

void GpioInit_PowerI2CAlert(void)
{
    GpioInit(&g_sGpio_PowerI2CAlert0);
}

uint32_t GpioGet_PowerI2CAlert(void)
{
    uint32_t ui32Val = 0;

    ui32Val |= (GpioOutputGetBool(&g_sGpio_PowerI2CAlert0) & 0x1) << 0;

    return ui32Val;
}



// ******************************************************************
// Reserved power control.
// ******************************************************************

// P1V8_FPGA_EN: PP0, 118
tGPIO g_sGpio_PowerReservedCtrl0 = {
    SYSCTL_PERIPH_GPIOP,
    GPIO_PORTP_BASE,
    GPIO_PIN_0,             // ui8Pins
    GPIO_STRENGTH_2MA,      // ui32Strength
    GPIO_PIN_TYPE_STD_WPD,  // ui32PinType
    false,                  // bInput: false = output, true = input
    0                       // ui32IntType
};
// P1V2_MGT_EN: PP1, 119
tGPIO g_sGpio_PowerReservedCtrl1 = {
    SYSCTL_PERIPH_GPIOP,
    GPIO_PORTP_BASE,
    GPIO_PIN_1,             // ui8Pins
    GPIO_STRENGTH_2MA,      // ui32Strength
    GPIO_PIN_TYPE_STD_WPD,  // ui32PinType
    false,                  // bInput: false = output, true = input
    0                       // ui32IntType
};
// P0V9_MGT_EN: PP2, 103
tGPIO g_sGpio_PowerReservedCtrl2 = {
    SYSCTL_PERIPH_GPIOP,
    GPIO_PORTP_BASE,
    GPIO_PIN_2,             // ui8Pins
    GPIO_STRENGTH_2MA,      // ui32Strength
    GPIO_PIN_TYPE_STD_WPD,  // ui32PinType
    false,                  // bInput: false = output, true = input
    0                       // ui32IntType
};
// P3V3_MISC_EN: PP3, 104
tGPIO g_sGpio_PowerReservedCtrl3 = {
    SYSCTL_PERIPH_GPIOP,
    GPIO_PORTP_BASE,
    GPIO_PIN_3,             // ui8Pins
    GPIO_STRENGTH_2MA,      // ui32Strength
    GPIO_PIN_TYPE_STD_WPD,  // ui32PinType
    false,                  // bInput: false = output, true = input
    0                       // ui32IntType
};
// P5V_MISC_EN: PP4, 105
tGPIO g_sGpio_PowerReservedCtrl4 = {
    SYSCTL_PERIPH_GPIOP,
    GPIO_PORTP_BASE,
    GPIO_PIN_4,             // ui8Pins
    GPIO_STRENGTH_2MA,      // ui32Strength
    GPIO_PIN_TYPE_STD_WPD,  // ui32PinType
    false,                  // bInput: false = output, true = input
    0                       // ui32IntType
};
// P1V8_MISC_EN: PP5, 106
tGPIO g_sGpio_PowerReservedCtrl5 = {
    SYSCTL_PERIPH_GPIOP,
    GPIO_PORTP_BASE,
    GPIO_PIN_5,             // ui8Pins
    GPIO_STRENGTH_2MA,      // ui32Strength
    GPIO_PIN_TYPE_STD_WPD,  // ui32PinType
    false,                  // bInput: false = output, true = input
    0                       // ui32IntType
};

void GpioInit_PowerReservedCtrl(void)
{
    GpioInit(&g_sGpio_PowerReservedCtrl0);
    GpioInit(&g_sGpio_PowerReservedCtrl1);
    GpioInit(&g_sGpio_PowerReservedCtrl2);
    GpioInit(&g_sGpio_PowerReservedCtrl3);
    GpioInit(&g_sGpio_PowerReservedCtrl4);
    GpioInit(&g_sGpio_PowerReservedCtrl5);
}

void GpioSet_PowerReservedCtrl(uint32_t ui32Val)
{
    GpioOutputSetBool(&g_sGpio_PowerReservedCtrl0, (bool) (ui32Val & 0x01));
    GpioOutputSetBool(&g_sGpio_PowerReservedCtrl1, (bool) (ui32Val & 0x02));
    GpioOutputSetBool(&g_sGpio_PowerReservedCtrl2, (bool) (ui32Val & 0x04));
    GpioOutputSetBool(&g_sGpio_PowerReservedCtrl3, (bool) (ui32Val & 0x08));
    GpioOutputSetBool(&g_sGpio_PowerReservedCtrl4, (bool) (ui32Val & 0x10));
    GpioOutputSetBool(&g_sGpio_PowerReservedCtrl5, (bool) (ui32Val & 0x20));
}

uint32_t GpioGet_PowerReservedCtrl(void)
{
    uint32_t ui32Val = 0;

    ui32Val |= (GpioOutputGetBool(&g_sGpio_PowerReservedCtrl0) & 0x1) << 0;
    ui32Val |= (GpioOutputGetBool(&g_sGpio_PowerReservedCtrl1) & 0x1) << 1;
    ui32Val |= (GpioOutputGetBool(&g_sGpio_PowerReservedCtrl2) & 0x1) << 2;
    ui32Val |= (GpioOutputGetBool(&g_sGpio_PowerReservedCtrl3) & 0x1) << 3;
    ui32Val |= (GpioOutputGetBool(&g_sGpio_PowerReservedCtrl4) & 0x1) << 4;
    ui32Val |= (GpioOutputGetBool(&g_sGpio_PowerReservedCtrl5) & 0x1) << 5;

    return ui32Val;
}



// ******************************************************************
// Temperature sensor alert signals.
// ******************************************************************

// I2C_SENS_0x1C_ALERTn: PH0, 29
tGPIO g_sGpio_TempAlert0 = {
    SYSCTL_PERIPH_GPIOH,
    GPIO_PORTH_BASE,
    GPIO_PIN_0,             // ui8Pins
    GPIO_STRENGTH_2MA,      // ui32Strength
    GPIO_PIN_TYPE_STD_WPU,  // ui32PinType
    true,                   // bInput: false = output, true = input
    GPIO_BOTH_EDGES         // ui32IntType
};
// I2C_SENS_0x3C_ALERTn: PH1, 30
tGPIO g_sGpio_TempAlert1 = {
    SYSCTL_PERIPH_GPIOH,
    GPIO_PORTH_BASE,
    GPIO_PIN_1,             // ui8Pins
    GPIO_STRENGTH_2MA,      // ui32Strength
    GPIO_PIN_TYPE_STD_WPU,  // ui32PinType
    true,                   // bInput: false = output, true = input
    GPIO_BOTH_EDGES         // ui32IntType
};
// I2C_SENS_0x7C_ALERTn: PH2, 31
tGPIO g_sGpio_TempAlert2 = {
    SYSCTL_PERIPH_GPIOH,
    GPIO_PORTH_BASE,
    GPIO_PIN_2,             // ui8Pins
    GPIO_STRENGTH_2MA,      // ui32Strength
    GPIO_PIN_TYPE_STD_WPU,  // ui32PinType
    true,                   // bInput: false = output, true = input
    GPIO_BOTH_EDGES         // ui32IntType
};

void GpioInit_TempAlert(void)
{
    GpioInit(&g_sGpio_TempAlert0);
    GpioInit(&g_sGpio_TempAlert1);
    GpioInit(&g_sGpio_TempAlert2);
}

uint32_t GpioGet_TempAlert(void)
{
    uint32_t ui32Val = 0;

    ui32Val |= (GpioOutputGetBool(&g_sGpio_TempAlert0) & 0x1) << 0;
    ui32Val |= (GpioOutputGetBool(&g_sGpio_TempAlert1) & 0x1) << 1;
    ui32Val |= (GpioOutputGetBool(&g_sGpio_TempAlert2) & 0x1) << 2;

    return ui32Val;
}



// ******************************************************************
// Control/status of the FPGA.
// ******************************************************************

// FPGA_PROG_B: PF0, 42
tGPIO g_sGpio_FPGACtrlStat0 = {
    SYSCTL_PERIPH_GPIOF,
    GPIO_PORTF_BASE,
    GPIO_PIN_0,             // ui8Pins
    GPIO_STRENGTH_2MA,      // ui32Strength
    GPIO_PIN_TYPE_OD,       // ui32PinType
    false,                  // bInput: false = output, true = input
    0                       // ui32IntType
};
// FPGA_INIT_B: PF1, 43
tGPIO g_sGpio_FPGACtrlStat1 = {
    SYSCTL_PERIPH_GPIOF,
    GPIO_PORTF_BASE,
    GPIO_PIN_1,             // ui8Pins
    GPIO_STRENGTH_2MA,      // ui32Strength
    GPIO_PIN_TYPE_OD,       // ui32PinType
    false,                  // bInput: false = output, true = input
    0                       // ui32IntType
};
// FPGA_DONE: PF2, 44
tGPIO g_sGpio_FPGACtrlStat2 = {
    SYSCTL_PERIPH_GPIOF,
    GPIO_PORTF_BASE,
    GPIO_PIN_2,             // ui8Pins
    GPIO_STRENGTH_2MA,      // ui32Strength
    GPIO_PIN_TYPE_STD,      // ui32PinType
    true,                   // bInput: false = output, true = input
    0                       // ui32IntType
};

void GpioInit_FPGACtrlStat(void)
{
    GpioInit(&g_sGpio_FPGACtrlStat0);
    GpioInit(&g_sGpio_FPGACtrlStat1);
    GpioInit(&g_sGpio_FPGACtrlStat2);
}

void GpioSet_FPGACtrlStat(uint32_t ui32Val)
{
    GpioOutputSetBool(&g_sGpio_FPGACtrlStat0, (bool) (ui32Val & 0x01));
    GpioOutputSetBool(&g_sGpio_FPGACtrlStat1, (bool) (ui32Val & 0x02));
}

uint32_t GpioGet_FPGACtrlStat(void)
{
    uint32_t ui32Val = 0;

    ui32Val |= (GpioOutputGetBool(&g_sGpio_FPGACtrlStat0) & 0x1) << 0;
    ui32Val |= (GpioOutputGetBool(&g_sGpio_FPGACtrlStat1) & 0x1) << 1;
    ui32Val |= (GpioInputGetBool(&g_sGpio_FPGACtrlStat2) & 0x1) << 2;

    return ui32Val;
}



// ******************************************************************
// I2C reset signals.
// ******************************************************************

// I2C_CLK_0x20_RSTn: PD7, 128
tGPIO g_sGpio_I2CReset0 = {
    SYSCTL_PERIPH_GPIOD,
    GPIO_PORTD_BASE,
    GPIO_PIN_7,             // ui8Pins
    GPIO_STRENGTH_2MA,      // ui32Strength
    GPIO_PIN_TYPE_STD,      // ui32PinType
    false,                  // bInput: false = output, true = input
    0                       // ui32IntType
};
// I2C_FF_0x20_RSTn: PC4, 25
tGPIO g_sGpio_I2CReset1 = {
    SYSCTL_PERIPH_GPIOC,
    GPIO_PORTC_BASE,
    GPIO_PIN_4,             // ui8Pins
    GPIO_STRENGTH_2MA,      // ui32Strength
    GPIO_PIN_TYPE_STD,      // ui32PinType
    false,                  // bInput: false = output, true = input
    0                       // ui32IntType
};
// I2C_FF_0x21_RSTn: PC5, 24
tGPIO g_sGpio_I2CReset2 = {
    SYSCTL_PERIPH_GPIOC,
    GPIO_PORTC_BASE,
    GPIO_PIN_5,             // ui8Pins
    GPIO_STRENGTH_2MA,      // ui32Strength
    GPIO_PIN_TYPE_STD,      // ui32PinType
    false,                  // bInput: false = output, true = input
    0                       // ui32IntType
};
// I2C_FF_0x22_RSTn: PD6, 127
tGPIO g_sGpio_I2CReset3 = {
    SYSCTL_PERIPH_GPIOD,
    GPIO_PORTD_BASE,
    GPIO_PIN_6,             // ui8Pins
    GPIO_STRENGTH_2MA,      // ui32Strength
    GPIO_PIN_TYPE_STD,      // ui32PinType
    false,                  // bInput: false = output, true = input
    0                       // ui32IntType
};

void GpioInit_I2CReset(void)
{
    GpioInit(&g_sGpio_I2CReset0);
    GpioInit(&g_sGpio_I2CReset1);
    GpioInit(&g_sGpio_I2CReset2);
    GpioInit(&g_sGpio_I2CReset3);
}

void GpioSet_I2CReset(uint32_t ui32Val)
{
    GpioOutputSetBool(&g_sGpio_I2CReset0, ! (bool) (ui32Val & 0x01));
    GpioOutputSetBool(&g_sGpio_I2CReset1, ! (bool) (ui32Val & 0x02));
    GpioOutputSetBool(&g_sGpio_I2CReset2, ! (bool) (ui32Val & 0x04));
    GpioOutputSetBool(&g_sGpio_I2CReset3, ! (bool) (ui32Val & 0x08));
}

uint32_t GpioGet_I2CReset(void)
{
    uint32_t ui32Val = 0;

    ui32Val |= (!(GpioOutputGetBool(&g_sGpio_PowerReservedCtrl0) & 0x1)) << 0;
    ui32Val |= (!(GpioOutputGetBool(&g_sGpio_PowerReservedCtrl1) & 0x1)) << 1;
    ui32Val |= (!(GpioOutputGetBool(&g_sGpio_PowerReservedCtrl2) & 0x1)) << 2;
    ui32Val |= (!(GpioOutputGetBool(&g_sGpio_PowerReservedCtrl3) & 0x1)) << 3;

    return ui32Val;
}



// ******************************************************************
// I2C interrupt signals.
// ******************************************************************

// I2C_MISC_0x20_INTn: PA3, 36
tGPIO g_sGpio_I2CInt0 = {
    SYSCTL_PERIPH_GPIOA,
    GPIO_PORTA_BASE,
    GPIO_PIN_3,             // ui8Pins
    GPIO_STRENGTH_2MA,      // ui32Strength
    GPIO_PIN_TYPE_STD_WPU,  // ui32PinType
    true,                   // bInput: false = output, true = input
    GPIO_BOTH_EDGES         // ui32IntType
};
// I2C_MISC_0x21_INTn: PA4, 37
tGPIO g_sGpio_I2CInt1 = {
    SYSCTL_PERIPH_GPIOA,
    GPIO_PORTA_BASE,
    GPIO_PIN_4,             // ui8Pins
    GPIO_STRENGTH_2MA,      // ui32Strength
    GPIO_PIN_TYPE_STD_WPU,  // ui32PinType
    true,                   // bInput: false = output, true = input
    GPIO_BOTH_EDGES         // ui32IntType
};
// I2C_MISC_0x22_INTn: PA5, 38
tGPIO g_sGpio_I2CInt2 = {
    SYSCTL_PERIPH_GPIOA,
    GPIO_PORTA_BASE,
    GPIO_PIN_5,             // ui8Pins
    GPIO_STRENGTH_2MA,      // ui32Strength
    GPIO_PIN_TYPE_STD_WPU,  // ui32PinType
    true,                   // bInput: false = output, true = input
    GPIO_BOTH_EDGES         // ui32IntType
};
// I2C_MISC_0x23_INTn: PB3, 92
tGPIO g_sGpio_I2CInt3 = {
    SYSCTL_PERIPH_GPIOB,
    GPIO_PORTB_BASE,
    GPIO_PIN_3,             // ui8Pins
    GPIO_STRENGTH_2MA,      // ui32Strength
    GPIO_PIN_TYPE_STD_WPU,  // ui32PinType
    true,                   // bInput: false = output, true = input
    GPIO_BOTH_EDGES         // ui32IntType
};
// I2C_CLK_0x21_INTn: PE0, 15
tGPIO g_sGpio_I2CInt4 = {
    SYSCTL_PERIPH_GPIOE,
    GPIO_PORTE_BASE,
    GPIO_PIN_0,             // ui8Pins
    GPIO_STRENGTH_2MA,      // ui32Strength
    GPIO_PIN_TYPE_STD_WPU,  // ui32PinType
    true,                   // bInput: false = output, true = input
    GPIO_BOTH_EDGES         // ui32IntType
};
// I2C_CLK_0x22_INTn: PE1, 14
tGPIO g_sGpio_I2CInt5 = {
    SYSCTL_PERIPH_GPIOE,
    GPIO_PORTE_BASE,
    GPIO_PIN_1,             // ui8Pins
    GPIO_STRENGTH_2MA,      // ui32Strength
    GPIO_PIN_TYPE_STD_WPU,  // ui32PinType
    true,                   // bInput: false = output, true = input
    GPIO_BOTH_EDGES         // ui32IntType
};
// I2C_CLK_0x23_INTn: PE2, 13
tGPIO g_sGpio_I2CInt6 = {
    SYSCTL_PERIPH_GPIOE,
    GPIO_PORTE_BASE,
    GPIO_PIN_2,             // ui8Pins
    GPIO_STRENGTH_2MA,      // ui32Strength
    GPIO_PIN_TYPE_STD_WPU,  // ui32PinType
    true,                   // bInput: false = output, true = input
    GPIO_BOTH_EDGES         // ui32IntType
};
// I2C_CLK_0x24_INTn: PE3, 12
tGPIO g_sGpio_I2CInt7 = {
    SYSCTL_PERIPH_GPIOE,
    GPIO_PORTE_BASE,
    GPIO_PIN_3,             // ui8Pins
    GPIO_STRENGTH_2MA,      // ui32Strength
    GPIO_PIN_TYPE_STD_WPU,  // ui32PinType
    true,                   // bInput: false = output, true = input
    GPIO_BOTH_EDGES         // ui32IntType
};


void GpioInit_I2CInt(void)
{
    GpioInit(&g_sGpio_I2CInt0);
    GpioInit(&g_sGpio_I2CInt1);
    GpioInit(&g_sGpio_I2CInt2);
    GpioInit(&g_sGpio_I2CInt3);
    GpioInit(&g_sGpio_I2CInt4);
    GpioInit(&g_sGpio_I2CInt5);
    GpioInit(&g_sGpio_I2CInt6);
    GpioInit(&g_sGpio_I2CInt7);
}

uint32_t GpioGet_I2CInt(void)
{
    uint32_t ui32Val = 0;

    ui32Val |= (GpioOutputGetBool(&g_sGpio_I2CInt0) & 0x1) << 0;
    ui32Val |= (GpioOutputGetBool(&g_sGpio_I2CInt1) & 0x1) << 1;
    ui32Val |= (GpioOutputGetBool(&g_sGpio_I2CInt2) & 0x1) << 2;
    ui32Val |= (GpioOutputGetBool(&g_sGpio_I2CInt3) & 0x1) << 3;
    ui32Val |= (GpioOutputGetBool(&g_sGpio_I2CInt4) & 0x1) << 4;
    ui32Val |= (GpioOutputGetBool(&g_sGpio_I2CInt5) & 0x1) << 5;
    ui32Val |= (GpioOutputGetBool(&g_sGpio_I2CInt6) & 0x1) << 6;
    ui32Val |= (GpioOutputGetBool(&g_sGpio_I2CInt7) & 0x1) << 7;

    return ui32Val;
}

