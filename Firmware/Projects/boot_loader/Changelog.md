Changelog for the MDT-TP CM Prototype MCU Bootloader
====================================================
Auth: M. Fras, Electronics Division, MPI for Physics, Munich  
Mod.: M. Fras, Electronics Division, MPI for Physics, Munich  
Date: 06 Oct 2022  
Rev.: 03 Jul 2026  



Bootloader Versions
-------------------
* 0.0.1 - 27 May 2022
  - Initial version based on the MCU bootloader of the MDT-TP CM demonstrator.
* 0.0.2 - 03 Jun 2022
  - Updated user LED assignment and added the power control pins.
* 0.0.3 - 03 Jul 2026
  - Added a new command "i" to show information about the boot loader.
  - Included the gcc version as well as the compile date and time in the boot
    loader information.
  - Added warning messages at compile time for non-standard configurations.
  - Added warning messages at runtime for non-standard configurations during
    startup of the bootloader and for the new "i" (information) command.

