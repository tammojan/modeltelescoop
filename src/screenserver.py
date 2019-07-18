# -*- coding: utf-8 -*-
"""
Created on Mon Jun 24 14:21:33 2019

@author: S.P. van der Linden
"""

import socket
import threading
import json
import select
import logging

from json.decoder import JSONDecodeError

# The alt az to be modified (global to be used in all threads)
alt = 0.0
az = 0.0

# Flags to indicate when the threads need to stop
run_thread1 = True
run_thread2 = True

class ScreenServer(object):
        
    def __init__(self, host, port):
        """ Initialise all basic socket parameters """
        self.host = host
        self.port = port
        # Open a UDP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))
        
        # Handles for the threads
        self.listen_thread = None
        self.data_thread = None
        
        global alt, az, run_thread1, run_thread2
        alt = 58.0
        az = 90.0
        run_thread1 = True
        run_thread2 = True
        
    def listen(self):
        """ Start to listen to incoming connections """
        #self.sock.listen(10)
        logging.info('Waiting for client...')
        self.listen_thread = threading.Thread(target = self.listen_to_client)
        self.listen_thread.daemon = True
        self.listen_thread.start()
        
    def wait_for_client(self):
        """ This method monitors the socket and starts up a 'data thread' once
            we get a connection."""
        global run_thread2
        while run_thread2:
            # Accept a client once it tries to connect
            #client, address = self.sock.accept()
            #client.settimeout(60)
            logging.info('Client connected.')
            
            # Start the thread containing the listener
            self.data_thread = threading.Thread(target = self.listen_to_client,args = (s))
            self.data_thread.daemon = True
            self.data_thread.start()
        self.sock.close()
        return False
            
    def listen_to_client(self):
        """ This method takes a connected client and waits for incoming data """
        
        global alt, az, run_thread1
        
        # Loop to continuously listen
        while run_thread1:
            try:
                received = self.sock.recv(128).decode('utf-8')
                if received:
                    try:
                        received_json = json.loads(received)
                        alt = received_json.get('alt', 0.0)
                        az = received_json.get('az', 0.0)
                    except JSONDecodeError as e:
                        logger.exception(e)
                        pass
                else:
                    logging.exception('Nothing received')
                    raise Exception('Client disconnected')
            except Exception as e:
                logging.exception(e)
                client.close()
        return False
            
    def get_last_altaz(self):
        """ Return the last received AltAz pair (floats in degrees).  """
        global alt, az
        return (alt, az)
    
    def finish(self):
        """ Close the socket gracefully """
        # Stop the threads by toggling the run_threads flag
        global run_thread1, run_thread2
        run_thread1 = False
        run_thread2 = False

        

