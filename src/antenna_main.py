#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: S.P. van der Linden
"""

from hall_interface import HallInterface

import socket
import json
from time import sleep
import numpy as np
import sys


def send_altaz(sock: socket, alt: float, az: float):
    """ Send an altaz pair to the connected server through the socket"""
    ob = {'alt': round(alt), 'az': round(az)}
    sock.send(bytes(json.dumps(ob), 'utf-8'))


def convert_azimuth(az_in: float):
    """Convert azimuth sensor readout to actual calibrated azimuth

    Args:
        az_in (float): Input azimuth, 0<=az_in<360

    Returns:
        float: calibrated azimuth, 0<=az<360
    """
    # TODO: calibrate this
    return az_in


def convert_altitude(alt_in: float):
    """Convert altitude sensor readout to actual calibrated altitude

    Args:
        az_in (float): Input altitude, 0<=alt_in<360

    Returns:
        float: calibrated altitude, 0<=alt<=90
    """
    # TODO: calibrate this
    return np.interp(alt_in, np.array([131.5, 216.5]), np.array([0., 90.]))


def main():
    sensor_azi = HallInterface(0, 0)
    sensor_alt = HallInterface(0, 1)
    sensor_azi.enable()
    sensor_alt.enable()

    sleep(30) # Wait for screen to start

    # Create the client socket
    s = None

    # Connect to the server via port 7272, with 50 tries
    counter = 1
    while True:
        if s:
            s.close()
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
        try:
            print("Trying to connect")
            s.connect(('192.168.178.68', 7272))
        except (OSError, ConnectionRefusedError) as e:
            # We got an error, print out what, then sleep and try again
            print("Connection failed (attempt {}): {}".format(counter, e))
            sleep(5)
            counter = counter + 1
            continue
        with s:
            print('Connected, starting normal operation.')
            while True:
                try:
                    azimuth = convert_azimuth(sensor_azi.get_angle())
                    altitude = convert_altitude(sensor_alt.get_angle())
                    #print(int(altitude), int(azimuth))
                    send_altaz(s, altitude, azimuth)
                    sleep(0.1)
                except KeyboardInterrupt:
                    print('Quitting...')
                    sys.exit(1)

    sensor_azi.finish()
    sensor_alt.finish()

if __name__ == "__main__":
    main()
