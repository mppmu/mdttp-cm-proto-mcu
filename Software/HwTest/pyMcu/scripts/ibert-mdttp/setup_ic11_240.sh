echo "CAUTION: this script assumes many things, just use if the python configuration is not available"

cd ../..
USB_DEV=/dev/ttyUL1
# set the i2c mux to channel 3
./pyMcuCm.py -d ${USB_DEV} -c mcu_cmd_raw -p "i2c 3 0x70 0x0 0x08"
# 6) Freeze the DCO by setting Freeze DCO = 1 (bit 4 of register 137).
#  read before
./pyMcuCm.py -d ${USB_DEV} -c mcu_cmd_raw -p "i2c 3 0x10 0x4 0x89"
./pyMcuCm.py -d ${USB_DEV} -c mcu_cmd_raw -p "i2c 3 0x10 0x3 1"
# I got... Data: 0x08, so write 0x18
./pyMcuCm.py -d ${USB_DEV} -c mcu_cmd_raw -p "i2c 3 0x10 0x0 0x89 0x18"
# 7) Write the new frequency configuration (RFREQ, HS_DIV, and N1)
# note. no need to write the 6 regs if no precision is required
./pyMcuCm.py -d ${USB_DEV} -c mcu_cmd_raw -p "i2c 3 0x10 0x0 0x07 0xE0 0x48 0x6C 0xC0 0xAB 0x7E"
./pyMcuCm.py -d ${USB_DEV} -c mcu_cmd_raw -p "i2c 3 0x10 0x4 0x07"
./pyMcuCm.py -d ${USB_DEV} -c mcu_cmd_raw -p "i2c 3 0x10 0x3 6"
# 8) Unfreeze the DCO by setting Freeze DCO = 0 and assert the NewFreq bit (bit 6 of register 135) within 10 ms. 
# first read reg 135
./pyMcuCm.py -d ${USB_DEV} -c mcu_cmd_raw -p "i2c 3 0x10 0x4 0x87"; ./pyMcuCm.py -d ${USB_DEV} -c mcu_cmd_raw -p "i2c 3 0x10 0x3 1"
# I got... Data: 0x00 make sure that bit6 is in 0.

# here we do it as fast as we can
./pyMcuCm.py -d ${USB_DEV} -c mcu_cmd_raw -p "i2c 3 0x10 0x0 0x89 0x08"; ./pyMcuCm.py -d ${USB_DEV} -c mcu_cmd_raw -p "i2c 3 0x10 0x0 0x87 0x40"

# reset the NewFreq bit
sleep 1
./pyMcuCm.py -d ${USB_DEV} -c mcu_cmd_raw -p "i2c 3 0x10 0x0 0x87 0x00"
