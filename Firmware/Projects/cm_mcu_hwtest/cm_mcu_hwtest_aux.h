// File: cm_mcu_hwtest_aux.h
// Auth: M. Fras, Electronics Division, MPI for Physics, Munich
// Mod.: M. Fras, Electronics Division, MPI for Physics, Munich
// Date: 03 Jun 2022
// Rev.: 03 Jun 2022
//
// Header file for the auxiliary functions of the firmware running on the ATLAS
// MDT Trigger Processor (TP) Command Module (CM) prototype MCU.
//



#ifndef __CM_MCU_HWTEST_AUX_H__
#define __CM_MCU_HWTEST_AUX_H__



// ******************************************************************
// Function prototypes.
// ******************************************************************

int DelayUs(uint32_t ui32DelayUs);
int DelayUsCmd(char *pcCmd, char *pcParam);
int McuReset(char *pcCmd, char *pcParam);
int JumpToBootLoader(char *pcCmd, char *pcParam);
int LedCmStatusUpdated(void);



#endif  // __CM_MCU_HWTEST_AUX_H__

