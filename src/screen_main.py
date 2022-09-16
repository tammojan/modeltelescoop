#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 26 09:41:32 2019

@author: S.P. van der Linden
"""

import pygame

from renderskyplot import RenderSkyPlot, UPDATE_COORDS_EVENT, SPAWN_SATELLITE_EVENT

from screenserver import ScreenServer
from renderbar import RenderBar
import logging
import os
import sys

from util import altaz_to_unit, unit_to_skyxy

SET_STANDBY_EVENT = pygame.USEREVENT+2
STANDBY_TIMEOUT = 120 # Amount of time before the standby screen ('screen saver') is activated

def main():
    os.environ['DISPLAY'] = ':0'
    # Init logger
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(message)s',
                        handlers=[logging.FileHandler("screen_server.log"),
                                 logging.StreamHandler()])

    if len(sys.argv) > 1 and "debug" in sys.argv[1]:
        DEBUG = True
    else:
        DEBUG = False

    # PyGame initialisation
    pygame.init()

    # Start the server for communication between RPis
    server = ScreenServer('', 7272)
    server.listen()
    
    # Create a window or display
    if DEBUG:
        screen = pygame.display.set_mode((1920, 1080), 
                                         pygame.DOUBLEBUF |
                                         pygame.HWACCEL)
    else:
        screen = pygame.display.set_mode((1920, 1080), 
                                         pygame.FULLSCREEN |
                                         pygame.DOUBLEBUF |
                                         pygame.HWACCEL)
            
    # Create the clock object (for FPS control)
    clock = pygame.time.Clock()
    
    # Sky plot creation
    skyplot = RenderSkyPlot()
    
    # Side bar creation
    sidebar = RenderBar()
    sidebar.load_satellite_image()

    sidebar.set_satellite(skyplot.satellite)
    
    # Start the sound mixer
    pygame.mixer.init()

    # Line plot creation
    #data = RadioDataSet()
       
    #linedata = data.get_line_data(data.altaz_to_skycoord(45, 45))
    #linedata = linedata[~np.isnan(linedata)]
    #x = np.arange(0, linedata.shape[0])
    
    #plot_location = pygame.Rect(1100, 50, 700, 500)
    #lineplot = RenderLinePlot(x, linedata, plot_location)
    
    # Set the mouse to invisible
    if not DEBUG:
        pygame.mouse.set_visible(False)
    
    # Spawn a satellite every 3 minutes
    pygame.time.set_timer(SPAWN_SATELLITE_EVENT, 180000)
    # Start a timer (= repeating event) for updating the sky coordinates
    # every 60s
    pygame.time.set_timer(UPDATE_COORDS_EVENT, 60000)
    # And a second one to show the 'screen saver' when the antenna is idle for too long
    pygame.time.set_timer(SET_STANDBY_EVENT, STANDBY_TIMEOUT * 1000)
    
    # Post the event into the queue to make sure it initialises at startup
    pygame.event.post(pygame.event.Event(UPDATE_COORDS_EVENT))
    
    # Quit flag
    quit_attempt = False
    
    # Define list of rects where only these areas are updated
    rects_to_update = []
    
    # A flag which indicates whether we have rendered the first frame
    first_frame = True
    standby_active = False
    
    last_altaz = (0.0, 0.0)
    
    while not quit_attempt:
        
        # Get the events
        pressed_keys = pygame.key.get_pressed()
        filtered_events = []
        
        # First look for general window/program events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_attempt = True
            elif event.type == pygame.KEYDOWN:
                (alt, az) = server.get_last_altaz()
                if event.key == pygame.K_ESCAPE:
                    quit_attempt = True
                if event.key == pygame.K_RETURN:
                    # Press Enter for a quick print of the FPS
                    logging.debug('FPS: {:.0f}'.format(clock.get_fps()))
                if event.key == pygame.K_LEFT:
                    server.set_altaz(alt, az - 2)
                if event.key == pygame.K_RIGHT:
                    server.set_altaz(alt, az + 2)
                if event.key == pygame.K_UP:
                    server.set_altaz(alt + 2, az)
                if event.key == pygame.K_DOWN:
                    server.set_altaz(alt - 2, az)
            if quit_attempt:
                break
            else:
                filtered_events.append(event)
        
        # Pass on other events to the scene object
        #lineplot.process_events(filtered_events, pressed_keys)
        # NOTE: skyplot should go first, because satellite gets created there, used in sidebar.
        # FIXME: this is not a proper design. But it works.
        skyplot.process_events(filtered_events, pressed_keys)
        if SPAWN_SATELLITE_EVENT in [event.type for event in filtered_events]:
            sidebar.set_satellite(skyplot.satellite)
        sidebar.process_events(filtered_events, pressed_keys)
        
        # Let pygame handle its own events
        pygame.event.poll()
        
        # Get the latest altaz values from the antenna interface
        altaz = server.get_last_altaz()
        if abs(last_altaz[0] - altaz[0]) > 1 or abs(last_altaz[1] - altaz[1]) > 1:
            last_altaz = altaz
            
            # Update the data if the AltAz changed
            #coords = data.altaz_to_skycoord(altaz[0], altaz[1])
            #linedata = data.get_line_data(coords)
            #linedata = linedata[~np.isnan(linedata)]
            #x = np.arange(0, linedata.shape[0])
            #lineplot.set_data(x, linedata)
                
        # Set the new location of the target reticle            
        (x_unit, y_unit) = altaz_to_unit(altaz[0], altaz[1])
        (x, y) = unit_to_skyxy(x_unit, y_unit)
        
        # Update all logic (e.g. coordinates)
        #lineplot.update()
        skyplot.update(x, y)
        
        # Check whether the reticle is over a celestial body
        body_of_interest = skyplot.check_body_distances()
        sidebar.set_body_of_interest(body_of_interest)
 
        # Render the scene with the new data
        #rects_to_update.append(lineplot.render(screen))
        #if standby_active:
        #    pass
        #else:
        rects_to_update.append(skyplot.render(screen))
        rects_to_update.append(sidebar.render(screen))
        
        if first_frame:
            # If its the first frame, we need to flip the entire screen buffer
            # to the display
            pygame.display.flip()
        else:
            # If not the first frame, then we only need to flip the changed
            # areas
            pygame.display.update(rects_to_update)
        rects_to_update.clear()
        
        # Block the display for the amount of time required to get max 60 FPS
        clock.tick(60)
       
    # Quit gracefully
    pygame.quit()
    server.finish()

if __name__ == "__main__":
    main()
