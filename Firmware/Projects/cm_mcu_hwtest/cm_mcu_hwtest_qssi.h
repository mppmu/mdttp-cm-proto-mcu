// File: cm_mcu_hwtest_qssi.h
// Auth: M. Fras, Electronics Division, MPI for Physics, Munich
// Mod.: M. Fras, Electronics Division, MPI for Physics, Munich
// Date: 16 Sep 2022
// Rev.: 16 Sep 2022
//
// Header file for the QSSI functions of the firmware running on the ATLAS MDT
// Trigger Processor (TP) Command Module (CM) prototype MCU.
//



#ifndef __CM_MCU_HWTEST_QSSI_H__
#define __CM_MCU_HWTEST_QSSI_H__



// ******************************************************************
// Function prototypes.
// ******************************************************************

int QssiAccess(char *pcCmd, char *pcParam);
int QssiPortCheck(uint8_t ui8QssiPort, tQSSI **psQssi);
int QssiSetup(char *pcCmd, char *pcParam);
void QssiSetupHelp(void);


#endif  // __CM_MCU_HWTEST_QSSI_H__

