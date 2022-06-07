// File: uart_ui.h
// Auth: M. Fras, Electronics Division, MPI for Physics, Munich
// Mod.: M. Fras, Electronics Division, MPI for Physics, Munich
// Date: 07 Feb 2020
// Rev.: 10 Apr 2020
//
// Header file for the UART user interface (UI) for the ATLAS MDT Trigger
// Processor (TP) Command Module (CM) MCU.
//



#ifndef __UART_UI_H__
#define __UART_UI_H__



// Types.
typedef struct {
    uint32_t ui32PeripheralUart;
    uint32_t ui32PeripheralGpio;
    uint32_t ui32PortGpioBase;
    uint8_t  ui8PinGpioRx;
    uint8_t  ui8PinGpioTx;
    uint32_t ui32PinConfigRx;
    uint32_t ui32PinConfigTx;
    uint32_t ui32Base;
    uint32_t ui32SrcClock;
    uint32_t ui32Baud;
    uint32_t ui32Port;
} tUartUi;



// Function prototypes.
void UartUiInit(tUartUi *psUartUi);



#endif  // __UART_UI_H__

