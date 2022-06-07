// File: power_control.h
// Auth: M. Fras, Electronics Division, MPI for Physics, Munich
// Mod.: M. Fras, Electronics Division, MPI for Physics, Munich
// Date: 03 Jun 2022
// Rev.: 07 Jun 2022
//
// Header file of the power control functions for the hardware test firmware
// running on the ATLAS MDT Trigger Processor (TP) Command Module (CM)
// prototype MCU.
//



#ifndef __POWER_CONTROL_H__
#define __POWER_CONTROL_H__



// Hardware constants.
#define POWER_FPGA_CORE                 0x01
#define POWER_FPGA_IO                   0x02
#define POWER_FPGA                      (POWER_FPGA_CORE | POWER_FPGA_IO)
#define POWER_MISC                      0x04
#define POWER_FIREFLY                   0x08
#define POWER_PM1_CONTROL0              0x10
#define POWER_PM1_CONTROL1              0x20
#define POWER_PM2_CONTROL0              0x40
#define POWER_PM2_CONTROL1              0x80
#define POWER_PM                        (POWER_PM1_CONTROL0 | POWER_PM1_CONTROL1 | POWER_PM2_CONTROL0 | POWER_PM2_CONTROL1)
#define POWER_CLK_MISC                  (POWER_MISC | POWER_PM)
#define POWER_ALL                       (POWER_FPGA | POWER_CLK_MISC | POWER_FIREFLY)



// Function prototypes.
int PowerControl(char *pcCmd, char *pcParam);
void PowerControlHelp(void);
int PowerControl_All(bool bPowerSet, uint32_t ui32PowerVal);
int PowerControl_ClockMisc(bool bPowerSet, uint32_t ui32PowerVal);
int PowerControl_FPGA(bool bPowerSet, uint32_t ui32PowerVal);
int PowerControl_FireFly(bool bPowerSet, uint32_t ui32PowerVal);



#endif  // __POWER_CONTROL_H__

