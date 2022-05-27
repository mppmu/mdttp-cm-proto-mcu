// File: gpio_pins.h
// Auth: M. Fras, Electronics Division, MPI for Physics, Munich
// Mod.: M. Fras, Electronics Division, MPI for Physics, Munich
// Date: 27 May 2022
// Rev.: 27 May 2022
//
// Header file for the GPIO pin definitions and functions for the TI Tiva
// TM4C1290 MCU on the ATLAS MDT Trigger Processor (TP) Command Module (CM)
// prototype.
//



#ifndef __GPIO_PINS_H__
#define __GPIO_PINS_H__



// Default values.
#define GPIO_DEFAULT_CM_READY       0x0
#define GPIO_DEFAULT_LED_CM_USER    0x00    // 0..7: LED_USER_BLUE_0, LED_USER_BLUE_1 LED_USER_ORANGE_0, LED_USER_ORANGE_1, LED_USER_GREEN_0, LED_USER_GREEN_1, LED_USER_RED_0, LED_USER_RED_1



// Function prototypes.
void GpioInit_All(void);
void GpioInit_SmPowerEna(void);
uint32_t GpioGet_SmPowerEna(void);
void GpioInit_CmReady(void);
void GpioSet_CmReady(uint32_t ui32Val);
uint32_t GpioGet_CmReady(void);
void GpioInit_LedMcuUser(void);
void GpioSet_LedMcuUser(uint32_t ui32Val);
uint32_t GpioGet_LedMcuUser(void);



#endif  // __GPIO_PINS_H__

