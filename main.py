# -*- coding: utf-8 -*-
"""
Created on Fri Apr 26 09:41:32 2019

@author: S.P. van der Linden
"""

import pygame
import numpy as np
from renderskyplot import RenderSkyPlot
from renderlineplot import RenderLinePlot
from radiodataset import RadioDataSet

from astropy.coordinates import SkyCoord

from math import sqrt

from util import skyxy_to_unit, unit_to_skyxy, xy_to_altaz

def main():
    # PyGame initialisation
    pygame.init()
    
    # Create a window or display
    screen = pygame.display.set_mode((1920, 1080), 
                                     #pygame.FULLSCREEN |
                                     pygame.DOUBLEBUF |
                                     pygame.HWACCEL)
            
    # Create the clock object (for FPS control)
    clock = pygame.time.Clock()
    
    # Sky plot creation
    skyplot = RenderSkyPlot()
    
    # Line plot creation
    data = RadioDataSet()
       
    linedata = data.get_line_data(SkyCoord.from_name("M31"))
    linedata = linedata[~np.isnan(linedata)]
    x = np.arange(0, linedata.shape[0])
    
    plot_location = pygame.Rect(1100, 50, 700, 500)
    scene = RenderLinePlot(x, linedata, plot_location)
    
    # Set the mouse to invisible
    pygame.mouse.set_visible(False)
    
    # Main loop
    quit_attempt = False
    
    # Define a rect where only this area is updated
    rects_to_update = []
    
    # A flag which indicates whether we have rendered the first frame
    first_frame = True
    
    while not quit_attempt:
        
        # Get the events
        pressed_keys = pygame.key.get_pressed()
        filtered_events = []
        
        # First look for general window/program events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_attempt = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    quit_attempt = True
                if event.key == pygame.K_RETURN:
                    # Press Enter for a quick print of the FPS
                    print('FPS: {:.0f}'.format(clock.get_fps()))
            if quit_attempt:
                break
            else:
                filtered_events.append(event)
        
        # Pass on other events to the scene object
        scene.process_events(filtered_events, pressed_keys)
        
        # Let pygame handle its own events
        pygame.event.poll()
        
        # Update all logic (e.g. coordinates)
        scene.update()
        skyplot.update()
        
        # Convert mouse x,y coordinates to antenna AltAz
        mouse_position = pygame.mouse.get_pos()
        mouse_x = mouse_position[0]
        mouse_y = mouse_position[1]
        xy_unit = skyxy_to_unit(mouse_x, mouse_y)
        R = sqrt(xy_unit[0]**2 + xy_unit[1]**2)
        if R <= 1.0:
            altaz = xy_to_altaz(xy_unit[0], xy_unit[1])
            print("AltAz: ({:.1f}, {:.1f})".format(altaz[0], altaz[1]))
                
        # Render the scene with the new data
        rects_to_update.append(scene.render(screen))
        rects_to_update.append(skyplot.render(screen))
        
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

if __name__ == "__main__":
    main()
