#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
@author: S.P. van der Linden
"""

import spidev
from time import sleep


class HallInterface:
    def __init__(self, bus, cs):
        """ Create the HallInterface object """
        # Configure the SPI bus
    	# We're choosing the SPI bus with corresponding chip select (CS/SS)
        self.bus = bus
        self.chip_select = cs
        self.spi = spidev.SpiDev()
        
    def __del__(self):
        """ Ensure a safe clean up (otherwise the bus may lock up) """
        self.finish()
    	
    def enable(self):
        """ Enable the bus """
        self.spi.open(self.bus, self.chip_select)
        self.spi.max_speed_hz = 1000000 # 1 MHz
        self.spi.mode = 1
        self.spi.cshigh = False
        
    def finish(self):
        """ Ensure a safe clean up (otherwise the bus may lock up) """
        self.spi.close()
        
    def get_angle(self):
        # Read 2x 2 bytes: the first is to update the register in 
        # the sensor
        self.spi.readbytes(2)
        result = self.spi.readbytes(2)
        result_m = (result[0] << 8) + result[1]
        result_m = result_m & 0x3FFF
        result_angle = result_m / 16384.0 * 360.0
        return result_angle

if __name__ == "__main__":
    spi = HallInterface(0, 1)
    spi.enable()
    try:
        while True:
            print(spi.get_angle())
            sleep(0.1)
    except KeyboardInterrupt:
        spi.finish()
