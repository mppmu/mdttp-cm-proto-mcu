// File: sm_ipmc_i2c.h
// Auth: M. Fras, Electronics Division, MPI for Physics, Munich
// Mod.: M. Fras, Electronics Division, MPI for Physics, Munich
// Date: 26 Jun 2026
// Rev.: 26 Jun 2026
//
// Header file for providing slow control data for the Service Module IPMC from
// the Command Module MCU as an I2C slave in the hardware test firmware running
// on the ATLAS MDT Trigger Processor (TP) Command Module (CM) prototype MCU.
//



#ifndef __SM_IPMC_I2C_H__
#define __SM_IPMC_I2C_H__


// I2C configuration.
#define I2C_SLAVE_IPMC_BASE             I2C7_BASE
#define I2C_SLAVE_IPMC_SLAVE_ADR        0x40
#define I2C_SLAVE_IPMC_DATA_NUM         6
// Register addresses for the I2C slave connected to the SM IPMC.
#define I2C_SLAVE_IPMC_REG_STATUS       0x00
#define I2C_SLAVE_IPMC_REG_MCU_TEMP     0x10
#define I2C_SLAVE_IPMC_REG_FPGA1_TEMP   0x12
#define I2C_SLAVE_IPMC_REG_FPGA2_TEMP   0x14
#define I2C_SLAVE_IPMC_REG_FIREFLY_TEMP 0x16
#define I2C_SLAVE_IPMC_REG_POWER_TEMP   0x18
// Special data words.
#define I2C_SLAVE_IPMC_DATA_STALE       0xfe
#define I2C_SLAVE_IPMC_DATA_UNAVAILABLE 0xff



// Globals.
extern uint8_t g_ui8I2cIpmcData[I2C_SLAVE_IPMC_DATA_NUM];



// Function prototypes.
int SmIpmcI2cInit(void);
int SmIpmcI2cData(char *pcCmd, char *pcParam);
void IntHandlerSmIpmcI2c(void);



#endif  // __SM_IPMC_I2C_H__

