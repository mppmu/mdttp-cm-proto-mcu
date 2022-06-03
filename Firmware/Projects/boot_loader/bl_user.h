// File: bl_user.h
// Auth: M. Fras, Electronics Division, MPI for Physics, Munich
// Mod.: M. Fras, Electronics Division, MPI for Physics, Munich
// Date: 27 May 2022
// Rev.: 03 Jun 2022
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
#define BL_VERSION                  "0.0.2"
#define BL_RELEASEDATE              "03 Jun 2022"
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
#define LED_USER_0_GREEN            0x001
#define LED_USER_1_GREEN            0x002
#define LED_USER_2_GREEN            0x004
#define LED_USER_3_BLUE             0x008
#define LED_USER_4_BLUE             0x010
#define LED_USER_5_YELLOW           0x020
#define LED_USER_6_YELLOW           0x040
#define LED_USER_7_RED              0x080
#define LED_USER_8_RED              0x100



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

