// File: power_control.h
// Auth: M. Fras, Electronics Division, MPI for Physics, Munich
// Mod.: M. Fras, Electronics Division, MPI for Physics, Munich
// Date: 03 Jun 2022
// Rev.: 11 Jun 2026
//
// Header file of the power control functions for the hardware test firmware
// running on the ATLAS MDT Trigger Processor (TP) Command Module (CM)
// prototype MCU.
//
// Hint on LTC2977 8-channel PMBus power system manager (PM) ICs:
// - Two LTC2977 channels are used per managed power.
//   - The even channels (0..6) are used for voltage monitoring.
//   - The odd channels (1..7) are used for current monitoring.
// - There are two LTC2977 managers on the CM servicing the FPGA_IO,
//   CLK_MISC, and FIREFLY power domains.
//   - IC58: FPGA_IO
//     - P1V8_FPGA
//     - <unused>
//     - P1V2_MGT
//     - P0V9_MGT
//   - IC59: CLK_MISC
//     - P1V8_MISC
//     - P3V3_MISC
//     - P5V_MISC
//     - P3V3_FF
// - The modules get activated, when VIN_SNS is above the programmable
//   threshold VIN_ON. They get de-activated when it drops below VIN_OFF. The
//   threshold values are set by the global commands 0x35 and 0x36 of the
//   LTC2977 modules. The are set to 3.0 V and 2.0 V.
// - Both modules are linked together using bit 3 (vin_share_enable) of the
//   global configuration MFR_CONFIG_ALL_LTC2977. In this case, when one module
//   gets deactivated by driving VIN_SNS low, the other module will also get
//   deactivated. This is the factory default setting.
//   CAUTION: In order to switch on the logical power domains FPGA_IO,
//            CLK_MISC, and FIREFLY, both VIN_SNS pins must be high!
//            I.e. both POWER_PD_FPGA_IO_EN (0x02) and POWER_PD_MISC_EN (0x04)
//            must be set to 1!
// - The logical power domain FPGA_IO is switched on with POWER_PM1_CONTROL0
//   (0x10).
//   CAUTION: Both VIN_SNS pins must be high, i.e. 0x06, otherwise the power
//            does not turn on!
//   Note: POWER_PM1_CONTROL1 is not used and does not have any effect.
// - The logical power domain CLK_MISC is switched on with POWER_PM2_CONTROL0
//   (0x40).
//   CAUTION: Both VIN_SNS pins must be high, i.e. 0x06, otherwise the power
//            does not turn on!
// - The logical power domain FIREFLY is switched on with POWER_PM2_CONTROL1
//   (0x80).
//   CAUTION: Both VIN_SNS pins must be high, i.e. 0x06, otherwise the power
//            does not turn on!
// - Summary: The FPGA_IO and CLK_MISC power domains are switched with on/off
//            with the PM control pins instead of the power domain pins!
//            However, both power domain pins for FPGA_IO and MISC power must
//            be on so that the LTC2977 power modules are activated. Only then
//            can the logical power domains FPGA_IO, CLK_MISC, and FIREFLY be
//            switched on.
//            E.g.:
//            0x00 - All power is off.
//            0x06 - All power is off.
//            0xf0 - All power is off.
//            0xf2 - All power is off.
//            0xf4 - All power is off.
//            0xf6 - FPGA_IO and MISC power is on.
//            0xf7 - FPGA_CORE, FPGA_IO, and MISC power is on.
//            0xff - FPGA_CORE, FPGA_IO, MISC, and FIREFLY power is on.
//            0xce - MISC and FIREFLY power is on.
//            0x36 - FPGA_IO power is on.
//            0x37 - FPGA_CORE and FPGA_IO power is on.
//            0xc6 - MISC power is on.
//            0xc7 - FPGA_CORE and MISC power is on.
// - The FPGA core power can be switched on/off independently with
//   POWER_PD_FPGA_IO_EN.
//



#ifndef __POWER_CONTROL_H__
#define __POWER_CONTROL_H__



// Hardware constants.
#define POWER_PD_FPGA_CORE_EN           0x01
#define POWER_PD_FPGA_IO_EN             0x02
#define POWER_PD_MISC_EN                0x04
#define POWER_PD_FIREFLY_EN             0x08
#define POWER_PM1_CONTROL0              0x10
#define POWER_PM1_CONTROL1              0x20
#define POWER_PM2_CONTROL0              0x40
#define POWER_PM2_CONTROL1              0x80
// Logical power settings.
#define POWER_PM_ACTIVE                 (POWER_PD_FPGA_IO_EN | POWER_PD_MISC_EN)
#define POWER_FPGA_CORE                 (POWER_PD_FPGA_CORE_EN)
#define POWER_FPGA_IO                   (POWER_PM1_CONTROL0 | POWER_PM1_CONTROL1)
#define POWER_FPGA                      (POWER_FPGA_CORE | POWER_FPGA_IO)
#define POWER_CLK_MISC                  (POWER_PM2_CONTROL0)
#define POWER_FIREFLY                   (POWER_PD_FIREFLY_EN | POWER_PM2_CONTROL1)
#define POWER_ALL                       (POWER_FPGA | POWER_CLK_MISC | POWER_FIREFLY)



// Function prototypes.
int PowerControl(char *pcCmd, char *pcParam);
void PowerControlHelp(void);
int PowerControl_All(bool bPowerSet, uint32_t ui32PowerVal);
int PowerControl_ClockMisc(bool bPowerSet, uint32_t ui32PowerVal);
int PowerControl_FPGA(bool bPowerSet, uint32_t ui32PowerVal);
int PowerControl_FireFly(bool bPowerSet, uint32_t ui32PowerVal);



#endif  // __POWER_CONTROL_H__

