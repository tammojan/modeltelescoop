# -*- coding: utf-8 -*-
"""
Created on Mon Jun 24 14:21:33 2019

@author: S.P. van der Linden
"""

import zmq
import threading
import json
import select
import logging

from json.decoder import JSONDecodeError

# The alt az to be modified (global to be used in all threads)
alt = 0.0
az = 0.0

# Flags to indicate when the threads need to stop
run_thread = True

class ScreenServer(object):
        
    def __init__(self, host, port):
        """ Initialise all basic socket parameters """
        context = zmq.Context()
        self.socket = context.socket(zmq.SUB)
        self.socket.connect(f"tcp://{host}:{port}")
        self.socket.setsockopt_string(zmq.SUBSCRIBE, "")
        self.socket.setsockopt(zmq.CONFLATE, 1)
        
        # Handles for the threads
        self.listen_thread = None
        self.data_thread = None
        
        global alt, az, run_thread
        alt = 58.0
        az = 90.0
        run_thread = True
        
    def listen(self):
        """ Start to listen to incoming connections """
        logging.info('Waiting for client...')
        self.listen_thread = threading.Thread(target = self.listen_to_client)
        self.listen_thread.daemon = True
        self.listen_thread.start()
        
    def wait_for_client(self):
        """ This method monitors the socket and starts up a 'data thread' once
            we get a connection."""
        while True:
            # Start the thread containing the listener
            self.data_thread = threading.Thread(target = self.listen_to_client,args = (s))
            self.data_thread.daemon = True
            self.data_thread.start()
        self.socket.close()
        return False
            
    def listen_to_client(self):
        """ This method takes a connected client and waits for incoming data """
        
        global alt, az, run_thread
        
        # Loop to continuously listen
        while run_thread:
            try:
                received = self.socket.recv_string()
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
        # Stop the thread by toggling the run_threads flag
        global run_thread
        run_thread = False

        
    def set_altaz(self, override_alt, override_az):
        """ For debugging: just set alt and az """
        global alt, az
        alt = max(min(override_alt, 90), 0)
        az = override_az
