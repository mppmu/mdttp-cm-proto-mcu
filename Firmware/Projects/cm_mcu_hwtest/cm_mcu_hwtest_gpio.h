// File: cm_mcu_hwtest_gpio.h
// Auth: M. Fras, Electronics Division, MPI for Physics, Munich
// Mod.: M. Fras, Electronics Division, MPI for Physics, Munich
// Date: 03 Jun 2022
// Rev.: 03 Jun 2022
//
// Header file for the FPIO functions of the firmware running on the ATLAS MDT
// Trigger Processor (TP) Command Module (CM) prototype MCU.
//



#ifndef __CM_MCU_HWTEST_GPIO_H__
#define __CM_MCU_HWTEST_GPIO_H__



// ******************************************************************
// Function prototypes.
// ******************************************************************

int GpioGetSet(char *pcCmd, char *pcParam);
void GpioGetSetHelp(void);



#endif  // __CM_MCU_HWTEST_GPIO_H__

