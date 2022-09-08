// File: cm_mcu_hwtest.h
// Auth: M. Fras, Electronics Division, MPI for Physics, Munich
// Mod.: M. Fras, Electronics Division, MPI for Physics, Munich
// Date: 03 Jun 2022
// Rev.: 08 Sep 2022
//
// Header file of the firmware running on the ATLAS MDT Trigger Processor (TP)
// Command Module (CM) prototype MCU.
//



#ifndef __CM_MCU_HWTEST_H__
#define __CM_MCU_HWTEST_H__



// ******************************************************************
// Firmware parameters.
// ******************************************************************

#define FW_NAME                     "cm_mcu_hwtest"
#define FW_VERSION                  "0.0.3"
#define FW_RELEASEDATE              "08 Sep 2022"



// ******************************************************************
// System clock settings.
// ******************************************************************

// Use an external 25 MHz crystal or oscillator.
//#define SYSTEM_CLOCK_SETTINGS       (SYSCTL_XTAL_25MHZ | SYSCTL_OSC_MAIN | SYSCTL_USE_PLL | SYSCTL_CFG_VCO_480)
// CAUTION: No external crystal is installed on the Command Module!
//          => Only the internal oscillator can be used.
#define SYSTEM_CLOCK_SETTINGS       (SYSCTL_OSC_INT | SYSCTL_USE_PLL | SYSCTL_CFG_VCO_480)
#define SYSTEM_CLOCK_FREQ           120000000



// ******************************************************************
// User interface.
// ******************************************************************

#define UI_COMMAND_PROMPT           "> "
#define UI_STR_BUF_SIZE             256
#define UI_STR_DELIMITER            " \t"
#define UI_STR_OK                   "OK"
#define UI_STR_WARNING              "WARNING"
#define UI_STR_ERROR                "ERROR"
#define UI_STR_FATAL                "FATAL"
// Use this to optionally select the front-panel USB UART. Default will be the
// SM SoC UART. If not defined, the default will be the front-panel USB UART.
#define UI_UART_SELECT
#define UI_UART_SELECT_TIMEOUT      10



// ******************************************************************
// Hardware settings.
// ******************************************************************

// I2C parameters.
#define I2C_MASTER_NUM              8

// UART parameters.
#define UART_BAUD_MIN               150
#define UART_BAUD_MAX               15000000

// Status LEDs.
#define LED_CM_STATUS_TEMP_ALERT    0x01

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

// Enable power up/down handshaking between the Service Module and the Command
// Module using the PWR_EN (drive by the SM) and the READY (driven by the CM)
// signals (SM-CM handshaking).
#define SM_CM_POWER_HANDSHAKING_ENABLE
#define SM_CM_POWER_HANDSHAKING_SHOW_MESSAGE



// ******************************************************************
// Function prototypes.
// ******************************************************************



#endif  // __CM_MCU_HWTEST_H__

