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
    ob = {'alt': alt, 'az': az}
    print(ob)
    sock.send(bytes(json.dumps(ob), 'utf-8')) 


def main():
    sensor_0 = HallInterface(0, 0)
    sensor_0.enable()
    
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
        except KeyboardInterrupt:
            print('Quitting...')
                    
    sensor_0.finish()

if __name__ == "__main__":
    main()
