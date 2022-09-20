// File: qssi.h
// Auth: M. Fras, Electronics Division, MPI for Physics, Munich
// Mod.: M. Fras, Electronics Division, MPI for Physics, Munich
// Date: 16 Sep 2022
// Rev.: 20 Sep 2022
//
// Header file for the Quad Synchronous Serial Interface (QSSI) functions on
// the ATLAS MDT Trigger Processor (TP) Command Module (CM) MCU.
//



#ifndef __QSSI_H__
#define __QSSI_H__



// Types.
typedef struct {
    uint32_t ui32PeripheralSsi;
    uint32_t ui32PeripheralGpioClk;
    uint32_t ui32PeripheralGpioFss;
    uint32_t ui32PeripheralGpioXdat0;
    uint32_t ui32PeripheralGpioXdat1;
    uint32_t ui32PeripheralGpioXdat2;
    uint32_t ui32PeripheralGpioXdat3;
    uint32_t ui32PortGpioBaseClk;
    uint32_t ui32PortGpioBaseFss;
    uint32_t ui32PortGpioBaseXdat0;
    uint32_t ui32PortGpioBaseXdat1;
    uint32_t ui32PortGpioBaseXdat2;
    uint32_t ui32PortGpioBaseXdat3;
    uint8_t  ui8PinGpioClk;
    uint8_t  ui8PinGpioFss;
    uint8_t  ui8PinGpioXdat0;
    uint8_t  ui8PinGpioXdat1;
    uint8_t  ui8PinGpioXdat2;
    uint8_t  ui8PinGpioXdat3;
    uint32_t ui32PinConfigClk;
    uint32_t ui32PinConfigFss;
    uint32_t ui32PinConfigXdat0;
    uint32_t ui32PinConfigXdat1;
    uint32_t ui32PinConfigXdat2;
    uint32_t ui32PinConfigXdat3;
    uint32_t ui32BaseSsi;
    uint32_t ui32SsiClk;
    uint32_t ui32Protocol;
    uint32_t ui32Mode;
    uint32_t ui32BitRate;
    uint32_t ui32DataWidth;
    uint32_t ui32Timeout;
} tQSSI;


// Function prototypes.
void QssiMasterInit(tQSSI *psQssi);
uint32_t QssiMasterWrite(tQSSI *psQssi, uint32_t *pui32Data, uint8_t ui8Length, uint8_t mode, bool bFrameEnd);
int32_t QssiMasterRead(tQSSI *psQssi, uint32_t *pui32Data, uint8_t ui8Length, uint8_t mode, bool bFrameEnd);



#endif  // __QSSI_H__

