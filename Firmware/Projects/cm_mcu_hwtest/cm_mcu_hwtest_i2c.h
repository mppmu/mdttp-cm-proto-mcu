// File: cm_mcu_hwtest_i2c.h
// Auth: M. Fras, Electronics Division, MPI for Physics, Munich
// Mod.: M. Fras, Electronics Division, MPI for Physics, Munich
// Date: 03 Jun 2022
// Rev.: 03 Jun 2022
//
// Header file for the I2C functions of the firmware running on the ATLAS MDT
// Trigger Processor (TP) Command Module (CM) prototype MCU.
//



#ifndef __CM_MCU_HWTEST_I2C_H__
#define __CM_MCU_HWTEST_I2C_H__



// ******************************************************************
// Function prototypes.
// ******************************************************************

int I2CAccess(char *pcCmd, char *pcParam);
void I2CAccessHelp(void);
int I2CPortCheck(uint8_t ui8I2CPort, tI2C **psI2C);
int I2CDetect(char *pcCmd, char *pcParam);



#endif  // __CM_MCU_HWTEST_I2C_H__

