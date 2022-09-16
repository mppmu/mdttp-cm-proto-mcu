// File: cm_mcu_hwtest_io.h
// Auth: M. Fras, Electronics Division, MPI for Physics, Munich
// Mod.: M. Fras, Electronics Division, MPI for Physics, Munich
// Date: 03 Jun 2022
// Rev.: 16 Sep 2022
//
// Header file for the IO peripheral definitions of the firmware running on the
// ATLAS MDT Trigger Processor (TP) Command Module (CM) prototype MCU.
//



#ifndef __CM_MCU_HWTEST_IO_H__
#define __CM_MCU_HWTEST_IO_H__



#include "hw/i2c/i2c.h"
#include "hw/qssi/qssi.h"
#include "hw/uart/uart.h"
#include "Common/uart_ui.h"
#include "cm_mcu_hwtest.h"



// ******************************************************************
// Global variables for IO peripherals.
// ******************************************************************

// UART user inferface (UI).
extern tUartUi g_sUartUi1;
extern tUartUi g_sUartUi3;
extern tUartUi g_sUartUi5;

// I2C masters.
extern tI2C g_psI2C[I2C_MASTER_NUM];
extern uint8_t g_ui8I2CMasterPorts[I2C_MASTER_NUM];

// QSSI master.
extern tQSSI g_sQssi1;

// UARTs.
extern tUART g_sUart1;
extern tUART g_sUart3;
extern tUART g_sUart5;



#endif  // __CM_MCU_HWTEST_IO_H__

