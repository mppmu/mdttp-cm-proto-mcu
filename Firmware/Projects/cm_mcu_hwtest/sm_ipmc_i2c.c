// File: sm_ipmc_i2c.c
// Auth: M. Fras, Electronics Division, MPI for Physics, Munich
// Mod.: M. Fras, Electronics Division, MPI for Physics, Munich
// Date: 26 Jun 2026
// Rev.: 02 Jul 2026
//
// Functions for providing slow control data for the Service Module IPMC from
// the Command Module MCU as an I2C slave in the hardware test firmware running
// on the ATLAS MDT Trigger Processor (TP) Command Module (CM) prototype MCU.
//



#include <stdbool.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <strings.h>
#include "inc/hw_memmap.h"
#include "driverlib/i2c.h"
#include "utils/uartstdio.h"
#include "cm_mcu_hwtest.h"
#include "sm_ipmc_i2c.h"



// Globals.
uint8_t g_ui8I2cIpmcData[I2C_SLAVE_IPMC_DATA_NUM];



// Initialize power up/down handshaking between the Service Module and the Command
// Module using the PWR_EN (drive by the SM) and the READY (driven by the CM)
// signals.
int SmIpmcI2cInit(void)
{
    // Enable the I2C slave module.
    I2CSlaveEnable(I2C_SLAVE_IPMC_BASE);

    // Initialize the I2C slave functionality.
    I2CSlaveInit(I2C_SLAVE_IPMC_BASE, I2C_SLAVE_IPMC_SLAVE_ADR);

    // Register the interrupt handler routine.
    I2CIntRegister(I2C_SLAVE_IPMC_BASE, IntHandlerSmIpmcI2c);

    // Enable the I2C slave data interrupt source.
    I2CSlaveIntEnableEx(I2C_SLAVE_IPMC_BASE, I2C_SLAVE_INT_DATA);

    // Disable the I2C master interrupts, as they will interfere with the slave
    // interrupts and cause an infinite jump into the ISR function
    // IntHandlerSmIpmcI2c, which will cause the MCU to hang!
    I2CMasterIntDisable(I2C_SLAVE_IPMC_BASE);

    // Check if the I2C slave connected to the SM IPMC is enabled.
    #ifndef I2C_SLAVE_IPMC_ENABLE
    #warning "The I2C slave connected to the SM IPMC is turned OFF!"
    #warning "Turn it ON for normal operation!"
    #endif

    // Check if the messages for the I2C access from the SM IPMC are enabled.
    #ifdef SM_IPMC_I2C_ACCESS_SHOW_MESSAGE
    #warning "Messages for the I2C access from the SM IPMC are turned ON!"
    #warning "This is only for testing and debugging. Turn it OFF for normal operation!"
    #endif

    // Enable internal loopback routing (bypasses GPIO pins) for testing and
    // debugging.
    // CAUTION: This must be *OFF* for normal operation!
    #ifdef I2C_SLAVE_IPMC_LOOPBACK
    I2CLoopbackEnable(I2C_SLAVE_IPMC_BASE);
    #warning "Internal I2C loopback is turned ON for the I2C bus connected to the SM IPMC!"
    #warning "This is only for testing and debugging. Turn it OFF for normal operation!"
    #warning "CAUTION: The I2C bus connected to the SM IPMC *WILL NOT WORK*!"
    #endif

    // Initialize the IPMC data.
    for (int i = 0; i < I2C_SLAVE_IPMC_DATA_NUM; i++) {
        g_ui8I2cIpmcData[i] = 0;
    }

    return 0;
}



// Get or set the data provided to the SM IPMC via I2C.
int SmIpmcI2cData(char *pcCmd, char *pcParam)
{
    char *pcIpmcData = pcParam;
    uint32_t ui32IpmcDataVal = 0;
    int i;
    int status = 0;

    // Get the current SM IPMC data values.
    if (pcIpmcData == NULL) {
        UARTprintf("%s: Current SM IPMC data values:", UI_STR_OK);
        for (i = 0; i < I2C_SLAVE_IPMC_DATA_NUM; i++) {
            UARTprintf(" 0x%02x", g_ui8I2cIpmcData[i]);
        }
    // Set new SM IPMC data values.
    } else {
        i = 0;
        // Loop over all provided data.
        while (pcParam != NULL) {
            ui32IpmcDataVal = strtol(pcParam, (char **) NULL, 0);
            g_ui8I2cIpmcData[i] = ui32IpmcDataVal & 0xff;
            pcParam = strtok(NULL, UI_STR_DELIMITER);
            i++;
            // Stop when the total number of supported data values is reached.
            if (i >= I2C_SLAVE_IPMC_DATA_NUM) {
                break;
            }
        }
        UARTprintf("%s: SM IPMC data values set to:", UI_STR_OK);
        for (i = 0; i < I2C_SLAVE_IPMC_DATA_NUM; i++) {
            UARTprintf(" 0x%02x", g_ui8I2cIpmcData[i]);
        }
    }
    return status;
}



// Interrupt service routine (ISR) for the I2C slave connected to the SM IPMC.
void IntHandlerSmIpmcI2c(void)
{
    uint32_t ui32Status;

    // Read the slave interrupt status.
    ui32Status = I2CSlaveIntStatus(I2C_SLAVE_IPMC_BASE, true);

    // Clear the interrupted flag.
    I2CSlaveIntClear(I2C_SLAVE_IPMC_BASE);

    // Check if the master requested a data transfer (write or read request).
    if(ui32Status & I2C_SLAVE_INT_DATA) {
        uint32_t ui32Req;
        uint8_t ui8ReceivedByte;
        uint8_t ui8TransmitByte;
        static uint8_t ui8RegAdr = 0;

        ui32Req = I2CSlaveStatus(I2C_SLAVE_IPMC_BASE);

        // Case 1: Master sent data to the slave (receive).
        if ((ui32Req == I2C_SLAVE_ACT_RREQ) || (ui32Req == I2C_SLAVE_ACT_RREQ_FBR)) {
            ui8ReceivedByte = I2CSlaveDataGet(I2C_SLAVE_IPMC_BASE);
            #ifdef SM_IPMC_I2C_ACCESS_SHOW_MESSAGE
            UARTprintf("I2C write access from the SM IPMC. Data = 0x%02x.\n", ui8ReceivedByte);
            #endif
            // Use only the first byte received (FBR) and ignore the other bytes.
            if (ui32Req == I2C_SLAVE_ACT_RREQ_FBR) {
                ui8RegAdr = ui8ReceivedByte;
            }
        // Case 2: Master requested data from the slave (transmit).
        } else if (ui32Req == I2C_SLAVE_ACT_TREQ) {
            switch (ui8RegAdr) {
                case I2C_SLAVE_IPMC_REG_STATUS:
                    ui8TransmitByte = g_ui8I2cIpmcData[0];
                    break;
                case I2C_SLAVE_IPMC_REG_MCU_TEMP:
                    ui8TransmitByte = g_ui8I2cIpmcData[1];
                    break;
                case I2C_SLAVE_IPMC_REG_FPGA1_TEMP:
                    ui8TransmitByte = g_ui8I2cIpmcData[2];
                    break;
                case I2C_SLAVE_IPMC_REG_FPGA2_TEMP:
                    ui8TransmitByte = g_ui8I2cIpmcData[3];
                    break;
                case I2C_SLAVE_IPMC_REG_FIREFLY_TEMP:
                    ui8TransmitByte = g_ui8I2cIpmcData[4];
                    break;
                case I2C_SLAVE_IPMC_REG_POWER_TEMP:
                    ui8TransmitByte = g_ui8I2cIpmcData[5];
                    break;
                default:
                    ui8TransmitByte = I2C_SLAVE_IPMC_DATA_UNAVAILABLE;
                    break;
            }
            #ifdef SM_IPMC_I2C_ACCESS_SHOW_MESSAGE
            UARTprintf("I2C read access from the SM IPMC. Register address = 0x%02x, data = 0x%02x.\n", ui8RegAdr, ui8TransmitByte);
            #endif

            // Send the requested data to the CM IPMC.
            I2CSlaveDataPut(I2C_SLAVE_IPMC_BASE, ui8TransmitByte);

            // Increment register address for consecutive read operations.
            ui8RegAdr++;
        }
    }
}

