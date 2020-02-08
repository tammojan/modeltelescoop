#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Interface to control the model telescope screen from a keyboard on a remote computer
(only for testing purposes). Address of model telescope screen is hardcoded.

@author: S.P. van der Linden and T.J. Dijkema
"""


import socket
import json
from time import sleep
import numpy as np
import curses

def send_altaz(sock: socket, alt: float, az: float):
    """ Send an altaz pair to the connected server through the socket"""
    ob = {'alt': round(alt), 'az': round(az)}
    sock.send(bytes(json.dumps(ob), 'utf-8'))


def main(win):
    win.nodelay(True)
    win.clear()
    azimuth = 0
    altitude = 0
    # Create the client socket
    s = None

    # Connect to the server via port 7272, with 50 tries
    counter = 1
    while True:
      if s:
          win.addstr("Socket exists, closing")
          s.close()
      else:
          s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
      try:
        try:
            win.addstr("Trying to connect")
            s.connect(('127.0.0.1', 7272))
        except OSError as e:
            # We got an error, print out what, then sleep and try again
            win.addstr("Connection failed (attempt {}): {}".format(counter, e))
            sleep(5)
            counter = counter + 1
            continue
        with s:
          while True:
              try:
                  key = win.getkey()
                  if key == 'KEY_LEFT':
                      azimuth -= 2
                  elif key == 'KEY_RIGHT':
                      azimuth += 2
                  elif key == 'KEY_UP':
                      altitude += 2
                  elif key == 'KEY_DOWN':
                      altitude -= 2
                  if azimuth > 360:
                      azimuth -= 360
                  if azimuth < 0:
                      azimuth += 360
                  if altitude < 0:
                      altitude = 0
                  if altitude > 90:
                      altitude = 90
                  send_altaz(s, altitude, azimuth)
                  win.clear()
                  win.addstr(f"Azimuth: {azimuth}   Altitude: {altitude}")
              except Exception as e:
                  pass
              sleep(0.1)
      except IOError as e:
          print(e)
          print("Broken pipe, reconnecting")
      except KeyboardInterrupt:
          print('Quitting...')
          break

if __name__ == "__main__":
    curses.wrapper(main)
