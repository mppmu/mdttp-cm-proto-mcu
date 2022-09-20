// File: qssi.c
// Auth: M. Fras, Electronics Division, MPI for Physics, Munich
// Mod.: M. Fras, Electronics Division, MPI for Physics, Munich
// Date: 16 Sep 2022
// Rev.: 20 Sep 2022
//
// Quad Synchronous Serial Interface (QSSI) functions on the ATLAS MDT Trigger
// Processor (TP) Command Module (CM) MCU.
//



#include <stdbool.h>
#include <stdint.h>
#include "driverlib/gpio.h"
#include "driverlib/ssi.h"
#include "driverlib/sysctl.h"
#include "qssi.h"



// Initialize a QSSI master.
void QssiMasterInit(tQSSI *psQssi)
{
    // Set up the IO pins for the QSSI master.
    SysCtlPeripheralEnable(psQssi->ui32PeripheralGpioClk);
    SysCtlPeripheralEnable(psQssi->ui32PeripheralGpioFss);
    SysCtlPeripheralEnable(psQssi->ui32PeripheralGpioXdat0);
    SysCtlPeripheralEnable(psQssi->ui32PeripheralGpioXdat1);
    SysCtlPeripheralEnable(psQssi->ui32PeripheralGpioXdat2);
    SysCtlPeripheralEnable(psQssi->ui32PeripheralGpioXdat3);
    GPIOPinConfigure(psQssi->ui32PinConfigClk);
    GPIOPinConfigure(psQssi->ui32PinConfigFss);
    GPIOPinConfigure(psQssi->ui32PinConfigXdat0);
    GPIOPinConfigure(psQssi->ui32PinConfigXdat1);
    GPIOPinConfigure(psQssi->ui32PinConfigXdat2);
    GPIOPinConfigure(psQssi->ui32PinConfigXdat3);
    GPIOPinTypeSSI(psQssi->ui32PortGpioBaseClk, psQssi->ui8PinGpioClk);
    GPIOPinTypeSSI(psQssi->ui32PortGpioBaseFss, psQssi->ui8PinGpioFss);
    GPIOPinTypeSSI(psQssi->ui32PortGpioBaseXdat0, psQssi->ui8PinGpioXdat0);
    GPIOPinTypeSSI(psQssi->ui32PortGpioBaseXdat1, psQssi->ui8PinGpioXdat1);
    GPIOPinTypeSSI(psQssi->ui32PortGpioBaseXdat2, psQssi->ui8PinGpioXdat2);
    GPIOPinTypeSSI(psQssi->ui32PortGpioBaseXdat3, psQssi->ui8PinGpioXdat3);

    // Set up the QSSI master.
    SysCtlPeripheralDisable(psQssi->ui32PeripheralSsi);
    SysCtlPeripheralReset(psQssi->ui32PeripheralSsi);
    SysCtlPeripheralEnable(psQssi->ui32PeripheralSsi);
    while(!SysCtlPeripheralReady(psQssi->ui32PeripheralSsi));
    SSIConfigSetExpClk(psQssi->ui32BaseSsi,
                       psQssi->ui32SsiClk,
                       psQssi->ui32Protocol,
                       psQssi->ui32Mode,
                       psQssi->ui32BitRate,
                       psQssi->ui32DataWidth);
    SSIAdvModeSet(psQssi->ui32BaseSsi, SSI_ADV_MODE_READ_WRITE);
    SSIAdvFrameHoldEnable(psQssi->ui32BaseSsi);
    SSIEnable(psQssi->ui32BaseSsi);
}



// Write data to a QSSI master.
uint32_t QssiMasterWrite(tQSSI *psQssi, uint32_t *pui32Data, uint8_t ui8Length, uint8_t mode, bool bFrameEnd)
{
    uint32_t ui32Timeout = psQssi->ui32Timeout + 10;     // Guarantee some minimum timeout value.

    if (ui8Length < 1) return -1;

    if ((mode & 0x1) == 0) {
        // Set up the SSI advance mode for SSI read/write.
        SSIAdvModeSet(psQssi->ui32BaseSsi, SSI_ADV_MODE_READ_WRITE);
    } else {
        // Set up the SSI advance mode for quad write.
        // Note: When using an advanced mode of operation, the SSI module must have
        //       been configured for eight data bits and the SSI_FRF_MOTO_MODE_0
        //       protocol.
        SSIAdvModeSet(psQssi->ui32BaseSsi, SSI_ADV_MODE_QUAD_WRITE);
    }

    // Send data.
    for (int i = 0; i < ui8Length; i++) {
        if ((i == ui8Length - 1) && bFrameEnd) {
            SSIAdvDataPutFrameEnd(psQssi->ui32BaseSsi, pui32Data[i]);
        } else {
            SSIDataPut(psQssi->ui32BaseSsi, pui32Data[i]);
        }
    }

    // Wait until the transfer is finished.
    if (bFrameEnd) {
        SysCtlDelay(psQssi->ui32SsiClk / 3e5);  // 10 us delay.
                                                // Note: The SysCtlDelay executes a simple 3 instruction cycle loop.
        for (int i = 0; i <= ui32Timeout; i++) {
            if (!SSIBusy(psQssi->ui32BaseSsi)) break;
            SysCtlDelay(psQssi->ui32SsiClk / 3e5);  // 10 us delay.
            // Timeout while waiting for the QSSI master to be free.
            if (i == ui32Timeout) {
                return -1;
            }
        }
    }

    return 0;
}



// Read data from an QSSI master.
int32_t QssiMasterRead(tQSSI *psQssi, uint32_t *pui32Data, uint8_t ui8Length, uint8_t mode, bool bFrameEnd)
{
    uint32_t ui32Timeout = psQssi->ui32Timeout + 10;     // Guarantee some minimum timeout value.
    int32_t i32Cnt = 0;

    if (ui8Length < 1) return -1;

    if ((mode & 0x1) == 0) {
        // Set up the SSI advance mode for SSI read/write.
        SSIAdvModeSet(psQssi->ui32BaseSsi, SSI_ADV_MODE_READ_WRITE);
    } else {
        // Set up the SSI advance mode for quad read.
        // Note: When using an advanced mode of operation, the SSI module must have
        //       been configured for eight data bits and the SSI_FRF_MOTO_MODE_0
        //       protocol.
        SSIAdvModeSet(psQssi->ui32BaseSsi, SSI_ADV_MODE_QUAD_READ);
    }

    // Receive data.
    for (int i = 0; i < ui8Length; i++) {
        i32Cnt += SSIDataGetNonBlocking(psQssi->ui32BaseSsi, &pui32Data[i32Cnt]);
    }

    // Send 0x00 bytes to keep clocking the remaining read data.
    for (int i = i32Cnt; i < ui8Length; i++) {
        if ((i == ui8Length - 1) && bFrameEnd) {
            SSIAdvDataPutFrameEnd(psQssi->ui32BaseSsi, 0x00);
        } else {
            SSIDataPut(psQssi->ui32BaseSsi, 0x00);
        }
        SysCtlDelay(psQssi->ui32SsiClk / 3e5);  // 10 us delay.
        i32Cnt += SSIDataGetNonBlocking(psQssi->ui32BaseSsi, &pui32Data[i32Cnt]);
    }

    // Wait until the transfer is finished.
    if (bFrameEnd) {
        SysCtlDelay(psQssi->ui32SsiClk / 3e5);  // 10 us delay.
        for (int i = 0; i <= ui32Timeout; i++) {
            if (!SSIBusy(psQssi->ui32BaseSsi)) break;
            SysCtlDelay(psQssi->ui32SsiClk / 3e5);  // 10 us delay.
            // Timeout while waiting for the QSSI master to be free.
            if (i == ui32Timeout) {
                return -1;
            }
        }
    }


    return i32Cnt;
}

