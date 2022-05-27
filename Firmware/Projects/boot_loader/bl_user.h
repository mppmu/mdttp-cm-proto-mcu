// File: bl_user.h
// Auth: M. Fras, Electronics Division, MPI for Physics, Munich
// Mod.: M. Fras, Electronics Division, MPI for Physics, Munich
// Date: 27 May 2022
// Rev.: 27 May 2022
//
// Header file of the user functions of the boot loader running on the ATLAS
// MDT Trigger Processor (TP) Command Module (CM) prototype MCU.
//



#ifndef __BL_USER_H__
#define __BL_USER_H__



// ******************************************************************
// Boot loader parameters.
// ******************************************************************

#define BL_NAME                     "boot loader"
#define BL_VERSION                  "0.0.1"
#define BL_RELEASEDATE              "27 May 2022"
// Timeout in seconds to enter the boot loader at startup.
#define BL_ACTIVATION_TIMEOUT       5
// Command prompt of the boot loader.
#define BL_COMMAND_PROMPT           "> "



// ******************************************************************
// System clock settings.
// ******************************************************************

// Use an external 25 MHz crystal or oscillator.
//#define SYSTEM_CLOCK_SETTINGS       (SYSCTL_XTAL_25MHZ | SYSCTL_OSC_MAIN | SYSCTL_USE_PLL | SYSCTL_CFG_VCO_480)
// CAUTION: No external crystal is installed on the Command Module demonstrator!
//          => Only the internal oscillator can be used.
//          The Command Module prototype does feature an external crystal.
//          Nevertheless, for compatibility reasons, the internal oscillator is
//          used as a default.
#define SYSTEM_CLOCK_SETTINGS       (SYSCTL_OSC_INT | SYSCTL_USE_PLL | SYSCTL_CFG_VCO_480)
#define SYSTEM_CLOCK_FREQ           120000000



// ******************************************************************
// Hardware settings.
// ******************************************************************

// User LEDs.
#define LED_USER_RED_0              0x001
#define LED_USER_RED_1              0x002
#define LED_USER_YELLOW_0           0x004
#define LED_USER_YELLOW_1           0x008
#define LED_USER_BLUE_0             0x010
#define LED_USER_BLUE_1             0x020
#define LED_USER_GREEN_0            0x040
#define LED_USER_GREEN_1            0x080
#define LED_USER_GREEN_2            0x100



// ******************************************************************
// Global variables.
// ******************************************************************
extern uint32_t g_ui32SysClock;
extern uint16_t g_ui16Led;



// ******************************************************************
// Function prototypes.
// ******************************************************************
void DelayUs(uint32_t ui32DelayUs);
void UARTprint(uint32_t ui32UartBase, const char* pcStr);
void UARTprintBlInfo(uint32_t ui32UartBase);
int UserHwInit(void);
int BL_UserMenu(uint32_t ui32UartBase);
int BL_UserMenuHelp(uint32_t ui32UartBase);



#endif  // __BL_USER_H__

