// File: sm_cm.c
// Auth: M. Fras, Electronics Division, MPI for Physics, Munich
// Mod.: M. Fras, Electronics Division, MPI for Physics, Munich
// Date: 03 Jun 2022
// Rev.: 03 Jun 2022
//
// Header file for interfacing the Service Module and the Command Module in the
// hardware test firmware running on the ATLASfirmware running on the ATLAS MDT
// Trigger Processor (TP) Command Module (CM) prototype MCU.
//



#ifndef __SM_CM_H__
#define __SM_CM_H__



// Globals.
extern tGPIO g_sGpio_SmPowerEna;


// Function prototypes.
int SmCm_PowerHandshakingInit(void);
void SmCm_IntHandlerSmPowerEna(void);



#endif  // __SM_CM_H__

