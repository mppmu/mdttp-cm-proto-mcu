# File: McuSerial.py
# Auth: M. Fras, Electronics Division, MPI for Physics, Munich
# Mod.: M. Fras, Electronics Division, MPI for Physics, Munich
# Date: 24 Apr 2020
# Rev.: 06 Apr 2023
#
# Python class for communicating with the TM4C1290NCPDT MCU over a serial port
# (UART).
#



import sys
import serial



class McuSerial:

    # MCU-specific variables and parameters.
    mcuCmdPrompt = "> "
    mcuReadLineMax          = 100
    mcuResponse             = ""
    mcuResponseOk           = "OK"
    mcuResponseWarning      = "WARNING"
    mcuResponseError        = "ERROR"
    mcuResponseFatal        = "FATAL"
    mcuResponseCodeOk       = 0
    mcuResponseCodeWarning  = 1
    mcuResponseCodeError    = 2
    mcuResponseCodeFatal    = 3
    mcuResponseCodeUnknown  = -1

    # Message prefixes and separators.
    prefixDetails       = " - "
    separatorDetails    = " - "
    prefixError = "ERROR: {0:s}: ".format(__file__)
    prefixDebug = "DEBUG: {0:s}: ".format(__file__)

    # Debug configuration.
    debugLevel = 0                 # Debug verbosity.

    # Simulated hardware access.
    simulateHwAccess = False       # Only simulate the access to hardware.
    simulateHwAccessMsg = "INFO: {0:s}: Simulated hardware access!".format(__file__)



    # Initialize the serial port for communication with the MCU.
    def __init__(self, port):
        self.ser = serial.Serial()
        self.ser.port = port
        self.ser.baudrate = 115200
        self.ser.bytesize = serial.EIGHTBITS
        self.ser.parity = serial.PARITY_NONE
        self.ser.stopbits = serial.STOPBITS_ONE
        #self.ser.timeout = None             # Blocking read.
        self.ser.timeout = 0.00015          # Non-blocking read. Empiric value based on a Core i7-9700K CPU (min stable value: 0.00013).
        self.ser.xonxoff = False            # Disable software flow control.
        self.ser.rtscts = False             # Disable hardware (RTS/CTS) flow control.
        self.ser.dsrdtr = False             # Disable hardware (DSR/DTR) flow control.
        self.ser.writeTimeout = 2           # Timeout for write.
        self.errorCount = 0
        self.accessRead = 0
        self.accessWrite = 0
        self.bytesRead = 0
        self.bytesWritten = 0

        try:
            if port:
                self.ser.open()
                self.simulateHwAccess = False
            else:
                self.simulateHwAccess = True
                if self.debugLevel >= 3:
                    print("{0:s}: Using simulated hardware access only!".format(__file__))
        except Exception as e:
            self.errorCount += 1
            print(self.prefixError + "Error opening serial port `" + port + "': " + str(e))
            sys.exit(-1)



    # Print details.
    def print_details(self):
        if self.simulateHwAccess:
            print(self.simulateHwAccessMsg)
            return 0
        print(self.prefixDetails, end='')
        print("UART port: " + self.ser.port, end='')
        print(self.separatorDetails + "Baud rate: {0:d}".format(self.ser.baudrate), end='')
        print(self.separatorDetails + "Data bytes: {0:d}".format(self.ser.bytesize), end='')
        print(self.separatorDetails + "Parity: " + self.ser.parity, end='')
        print(self.separatorDetails + "Stop bits: {0:d}".format(self.ser.stopbits), end='')
        print(self.separatorDetails + "Timeout: {0:f}".format(self.ser.timeout), end='')
        if self.debugLevel >= 1:
            print(self.separatorDetails + "Error count: {0:d}".format(self.errorCount), end='')
        if self.debugLevel >= 1:
            print(self.separatorDetails + "Read access count: {0:d}".format(self.accessRead), end='')
            print(self.separatorDetails + "Write access count: {0:d}".format(self.accessWrite), end='')
        if self.debugLevel >= 1:
            print(self.separatorDetails + "Bytes read: {0:d}".format(self.bytesRead), end='')
            print(self.separatorDetails + "Bytes written: {0:d}".format(self.bytesWritten), end='')
        print()
        return 0



    # Clear data from the serial port.
    def clear(self):
        if self.debugLevel >= 2:
            print(self.prefixDebug + "Clearing data from the serial port.")
        if self.simulateHwAccess:
            if self.debugLevel >= 2:
                print(self.simulateHwAccessMsg)
            return 0
        try:
            cnt = 0
            while cnt < self.mcuReadLineMax:
                cnt += 1
                self.ser.readline()
            return 0
        except Exception as e:
            self.errorCount += 1
            print(self.prefixError + "Error reading from serial port `" + self.ser.portstr + "': " + str(e))
            return -1
        return 0



    # Get the full MCU response from the serial port including the status.
    def get_full(self):
        if self.simulateHwAccess:
            return self.simulateHwAccessMsg
        s = self.mcuResponse.rstrip('\n\r')
        if self.debugLevel >= 3:
            print(self.prefixDebug + "Full MCU response:\n" + s)
        return s



    # Get the MCU response from the serial port without the status.
    def get(self):
        if self.simulateHwAccess:
            return self.simulateHwAccessMsg
        if self.mcuResponse.find(self.mcuResponseOk, 0, len(self.mcuResponseOk)) == 0:
            s = self.mcuResponse[len(self.mcuResponseOk) + 1:]
        elif self.mcuResponse.find(self.mcuResponseWarning, 0, len(self.mcuResponseWarning)) == 0:
            s = self.mcuResponse[len(self.mcuResponseWarning) + 1:]
        elif self.mcuResponse.find(self.mcuResponseError, 0, len(self.mcuResponseError)) == 0:
            s = self.mcuResponse[len(self.mcuResponseError) + 1:]
        elif self.mcuResponse.find(self.mcuResponseFatal, 0, len(self.mcuResponseFatal)) == 0:
            s = self.mcuResponse[len(self.mcuResponseFatal) + 1:]
        else:
            s = self.mcuResponse
        # Remove trailing space, newline and carriage return characters.
        s = s.rstrip(' \n\r')
        # Remove leading and trailing white spaces.
        s = s.strip()
        if self.debugLevel >= 3:
            print(self.prefixDebug + "MCU response:\n" + s)
        return s



    # Evaluate the MCU response.
    def eval(self):
        if self.simulateHwAccess:
            if self.debugLevel >= 3:
                print(self.simulateHwAccessMsg)
            return self.mcuResponseCodeOk
        if self.mcuResponse.find(self.mcuResponseOk, 0, len(self.mcuResponseOk)) == 0:
            ret = self.mcuResponseCodeOk
        elif self.mcuResponse.find(self.mcuResponseWarning, 0, len(self.mcuResponseWarning)) == 0:
            ret = self.mcuResponseCodeWarning
        elif self.mcuResponse.find(self.mcuResponseError, 0, len(self.mcuResponseError)) == 0:
            ret = self.mcuResponseCodeError
        elif self.mcuResponse.find(self.mcuResponseFatal, 0, len(self.mcuResponseFatal)) == 0:
            ret = self.mcuResponseCodeFatal
        else:
            ret = self.mcuResponseCodeUnknown
        if self.debugLevel >= 3:
            print(self.prefixDebug + "Evaluation of MCU result: {0:d}".format(ret))
        return ret



    # Send a MCU command to the serial port.
    def send(self, cmd):
        # Clear previous MCU response.
        self.mcuResponse = ""
        if self.simulateHwAccess:
            print(self.simulateHwAccessMsg + " Sending MCU command: " + cmd)
            self.mcuResponse = self.mcuResponseOk + " (simulated hardware access)"
            return self.mcuResponseCodeOk
        try:
            if self.debugLevel >= 2:
                print(self.prefixDebug + "Sending MCU command: " + cmd)
#            self.ser.write((cmd + "\r").encode('utf-8'))
#            self.ser.flush()
            # Work-around for the communication problem seen between the SM SoM and the CM MCU:
            # - Send the carriage return separately from the command with an
            #   additional write command and use a flush command after each
            #   write command.
            # - This method was empirically found and tested on 03 Apr 2023. It
            #   improves the reliability of the communication between the SM
            #   SoM and the CM MCU a lot, but not to 100%.
            # - The root cause of the problem is unclear.
            # - This work-around is not necessary when using the front-panel
            #   UART with a PC.
            self.ser.write(cmd.encode('utf-8'))
            self.ser.flush()
            self.ser.write("\r".encode('utf-8'))
            self.ser.flush()
            self.accessWrite += 1
            self.bytesWritten += len(cmd) + 1
        except Exception as e:
            self.errorCount += 1
            print(self.prefixError + "Error writing to serial port `" + self.ser.portstr + "': " + str(e))
            return -1
        try:
            self.accessRead += 1
            # Remove the echo of the command.
            cnt = 0
            line = ""
            serTimeoutBackup = self.ser.timeout
            # Temporarily set a longer timeout.
            self.ser.timeout = 0.05
            while line.find('\n') < 0:
                cnt += 1
                line = self.ser.readline().decode('utf-8')
                self.bytesRead += len(line)
                if cnt > self.mcuReadLineMax:
                    break
            self.ser.timeout = serTimeoutBackup
            # Read the response of the MCU and check for errors.
            self.mcuResponse = ""
            while line != self.mcuCmdPrompt:
                cnt += 1
                line = self.ser.readline().decode('utf-8')
                self.bytesRead += len(line)
                if line == self.mcuCmdPrompt:
                    return 0
                if cnt > self.mcuReadLineMax:
                    self.errorCount += 1
                    print(self.prefixError + "Incomplete response received from the MCU!")
                    return 1
                if line != "":
                    self.mcuResponse += line.rstrip('\n\r')
                    if line.find('\n') > 0:
                        self.mcuResponse += '\n'
            return 0
        except Exception as e:
            self.errorCount += 1
            print(self.prefixError + "Error reading from serial port `" + self.ser.portstr + "': " + str(e))
            return -1

