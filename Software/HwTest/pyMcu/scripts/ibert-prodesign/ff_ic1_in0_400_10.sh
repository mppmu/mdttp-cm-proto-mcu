#!/bin/bash

set -e

if [ $# -eq 0 ]; then
    echo "Usage: $0 UART"
    echo "  e.g. $0 /dev/ttyUSB0 [reset|reset0]"
    exit -1
fi

# All clock ICs used here
clock_ics="CLK_FF_135_0 CLK_FF_135_1 CLK_FF_79_0 CLK_FF_79_1 CLK_FF_024_0 CLK_FF_024_1 CLK_FF_68_0 CLK_FF_68_1 FF_CLK"

# Reset all clock ICs
./pyMcuCm.py -d $1 -c i2c_io_exp_init
for ic in $clock_ics; do
    reset=${ic}_RSTb
    ./pyMcuCm.py -d $1 -c i2c_io_exp_set_output -p $reset 0
done

if [ "$2" == "reset0" ]; then
    exit 0
fi

for ic in $clock_ics; do
    reset=${ic}_RSTb
    ./pyMcuCm.py -d $1 -c i2c_io_exp_set_output -p $reset 1
done

if [ "$2" == "reset" ]; then
    exit 0
fi

sleep 2

./pyMcuCm.py -d $1 -c clk_setup -p IC1 "IC1_100IN0_100_100_100_100_100_100_100_100_100_FB-Registers.txt"
./pyMcuCm.py -d $1 -c clk_setup -p IC2 "IC2,3,6,7_100IN0_400_10_400_10_400_10_400_10_400_FB-Registers.txt"
./pyMcuCm.py -d $1 -c clk_setup -p IC3 "IC2,3,6,7_100IN0_400_10_400_10_400_10_400_10_400_FB-Registers.txt"
./pyMcuCm.py -d $1 -c clk_setup -p IC6 "IC2,3,6,7_100IN0_400_10_400_10_400_10_400_10_400_FB-Registers.txt"
./pyMcuCm.py -d $1 -c clk_setup -p IC7 "IC2,3,6,7_100IN0_400_10_400_10_400_10_400_10_400_FB-Registers.txt"
./pyMcuCm.py -d $1 -c clk_setup -p IC4 "IC4,5,8,9_100IN0_400_10_400_10_400_10_NA_NA_NA_FB-Registers.txt"
./pyMcuCm.py -d $1 -c clk_setup -p IC5 "IC4,5,8,9_100IN0_400_10_400_10_400_10_NA_NA_NA_FB-Registers.txt"
./pyMcuCm.py -d $1 -c clk_setup -p IC8 "IC4,5,8,9_100IN0_400_10_400_10_400_10_NA_NA_NA_FB-Registers.txt"
./pyMcuCm.py -d $1 -c clk_setup -p IC9 "IC4,5,8,9_100IN0_400_10_400_10_400_10_NA_NA_NA_FB-Registers.txt"

echo "Checking LOL signals...."

no_lock=0
for ic in $clock_ics; do
    lol=${ic}_LOLb
    state=`./pyMcuCm.py -d $1 -c i2c_io_exp_get_input | grep $lol | cut -d: -f2`
    if [ "$state" != " 1" ]; then
        echo "ERROR: LOL on $lol"
        no_lock=1
    fi
done

if [ "$no_lock" != "0" ]; then
    exit -1
fi

echo "Run clock test with"
echo "  ./clock_test -t /dev/ttyUSB1 115200 -C FF_ALTREV"
