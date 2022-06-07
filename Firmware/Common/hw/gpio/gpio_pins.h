// File: gpio_pins.h
// Auth: M. Fras, Electronics Division, MPI for Physics, Munich
// Mod.: M. Fras, Electronics Division, MPI for Physics, Munich
// Date: 27 May 2022
// Rev.: 07 Jun 2022
//
// Header file for the GPIO pin definitions and functions for the TI Tiva
// TM4C1290 MCU on the ATLAS MDT Trigger Processor (TP) Command Module (CM)
// prototype.
//



#ifndef __GPIO_PINS_H__
#define __GPIO_PINS_H__



// Default values.
#define GPIO_DEFAULT_CM_READY               0x0
#define GPIO_DEFAULT_SM_GPIO                0x0     // 1..0: 
#define GPIO_DEFAULT_LED_CM_USER            0x000   // 8..0: MCU_USER_LED8 (red) .. MCU_USER_LED0 (green)
#define GPIO_DEFAULT_LED_CM_STATUS          0x0     //    0: TEMP_ERR
#define GPIO_DEFAULT_POWER_CTRL             0x00    // 7..0: PM2_CONTROL1, PM2_CONTROL0, PM1_CONTROL1, PM1_CONTROL0, PD_FF_EN, PD_MISC_EN, PD_FPGA_IO_EN, PD_FPGA_CORE_EN
#define GPIO_DEFAULT_FPGA_CTRL_STAT         0x3     // 2..0: FPGA_DONE, FPGA_INIT_B, FPGA_PROG_B
#define GPIO_DEFAULT_POWER_RESERVED_CTRL    0x000   // 5..0: P1V8_MISC_EN, P5V_MISC_EN, P3V3_MISC_EN, P0V9_MGT_EN, P1V2_MGT_EN, P1V8_FPGA_EN
#define GPIO_DEFAULT_I2C_RESET              0x0     // 3..0: I2C_FF_0x22_RSTn, I2C_FF_0x21_RSTn, I2C_FF_0x20_RSTn, I2C_CLK_0x20_RSTn



// Function prototypes.
void GpioInit_All(void);
void GpioInit_SmPowerEna(void);
uint32_t GpioGet_SmPowerEna(void);
void GpioInit_CmReady(void);
void GpioSet_CmReady(uint32_t ui32Val);
uint32_t GpioGet_CmReady(void);
void GpioInit_SmPsReset(void);
uint32_t GpioGet_SmPsReset(void);
void GpioInit_SmGpio(void);
void GpioSet_SmGpio(uint32_t ui32Val);
uint32_t GpioGet_SmGpio(void);
void GpioInit_LedCmStatus(void);
void GpioSet_LedCmStatus(uint32_t ui32Val);
uint32_t GpioGet_LedCmStatus(void);
void GpioInit_LedMcuUser(void);
void GpioSet_LedMcuUser(uint32_t ui32Val);
uint32_t GpioGet_LedMcuUser(void);
void GpioInit_PowerCtrl(void);
void GpioSet_PowerCtrl(uint32_t ui32Val);
uint32_t GpioGet_PowerCtrl(void);
void GpioInit_PowerGood(void);
uint32_t GpioGet_PowerGood(void);
void GpioInit_PowerFault(void);
uint32_t GpioGet_PowerFault(void);
void GpioInit_PowerI2CAlert(void);
uint32_t GpioGet_PowerI2CAlert(void);
void GpioInit_PowerReservedCtrl(void);
void GpioSet_PowerReservedCtrl(uint32_t ui32Val);
uint32_t GpioGet_PowerReservedCtrl(void);
void GpioInit_TempAlert(void);
uint32_t GpioGet_TempAlert(void);
void GpioInit_FPGACtrlStat(void);
void GpioSet_FPGACtrlStat(uint32_t ui32Val);
uint32_t GpioGet_FPGACtrlStat(void);
void GpioInit_I2CReset(void);
void GpioSet_I2CReset(uint32_t ui32Val);
uint32_t GpioGet_I2CReset(void);
void GpioInit_I2CInt(void);
uint32_t GpioGet_I2CInt(void);



#endif  // __GPIO_PINS_H__

