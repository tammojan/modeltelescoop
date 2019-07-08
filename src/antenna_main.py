#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
@author: S.P. van der Linden
"""

from hall_interface import HallInterface

import socket
import json
from time import sleep
import random

def send_altaz(sock: socket, alt: float, az: float):
    """ Send an altaz pair to the connected server through the socket"""
    ob = {'alt': round(alt), 'az': round(az)}
    print(ob)
    try:
        sock.send(bytes(json.dumps(ob), 'utf-8'))
    except IOError:
        print('Error: Broken pipe')


def main():
    sensor_azi = HallInterface(0, 0)
    sensor_alt = HallInterface(0, 1)
    sensor_azi.enable()
    sensor_alt.enable()

    # Create the client socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect to the server via port 7272, with 50 tries
    counter = 1
    while counter <= 50:
        try:
            s.connect(('192.168.4.1', 7272))
            break
        except OSError as e:
            # We got an error, print out what, then sleep and try again
            print("Connection failed (attempt {}): {}".format(counter, e))
            sleep(5)
            counter = counter + 1
            continue
    with s:
        print('Connected')
        try:
            while True:
                print('Transmitting')
                azimuth = sensor_azi.get_angle()
                altitude = sensor_alt.get_angle()
                print(azimuth)
                send_altaz(s, altitude, azimuth)
                sleep(0.2)
        except KeyboardInterrupt:
            print('Quitting...')

    sensor_azi.finish()
    sensor_alt.finish()

if __name__ == "__main__":
    main()
