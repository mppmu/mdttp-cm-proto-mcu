#!/bin/bash

set -e

if [ $# -eq 0 ]; then
    echo "Usage: $0 UART"
    echo "  e.g. $0 /dev/ttyUSB0"
    exit -1
fi

clock_ics="CLK_FF_TD_0"

# Reset all clock ICs
./pyMcuCm.py -d $1 -c i2c_io_exp_init
for ic in $clock_ics; do
    reset=${ic}_RSTb
    ./pyMcuCm.py -d $1 -c i2c_io_exp_set_output -p $reset 0
done
for ic in $clock_ics; do
    reset=${ic}_RSTb
    ./pyMcuCm.py -d $1 -c i2c_io_exp_set_output -p $reset 1
done

sleep 2

./pyMcuCm.py -d $1 -c clk_setup -p IC10 "IC10_INT_400_10_100_100_NA_NA_NA_NA_NA-Registers.txt"

# No lock checking since crystal is used
#
#echo "Checking LOL signals...."
#
#no_lock=0
#for ic in $clock_ics; do
#
#    # Skip FF_CLK since this chip will report LOL due to the crystal usage.
#    if [ "$ic" == "FF_CLK" ]; then
#        continue
#    fi
#    
#    lol=${ic}_LOLb
#    state=`./pyMcuCm.py -d $1 -c i2c_io_exp_get_input | grep $lol | cut -d: -f2`
#    if [ "$state" != " 1" ]; then
#        echo "ERROR: LOL on $lol"
#        no_lock=1
#    fi
#done
#
#if [ "$no_lock" != "0" ]; then
#    exit -1
#fi

echo "Run clock test with"
echo "  ./clock_test -t /dev/ttyUSB1 115200 -C TC_ALTREV"
