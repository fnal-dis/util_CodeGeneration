#!/usr/bin/env sh

cd src
VENDOR_LIB_PATH=/home/javierc/xilinx-vivado/

find . -name \*.cf -exec rm -rf {} \;
find . -name pkg\*.vhd -exec ghdl -a {} \;
find . -name \*.vhd -not -name top\* -exec ghdl -a {} \;
find . -name top\*.vhd -exec ghdl -a -P${VENDOR_LIB_PATH} {} \;
