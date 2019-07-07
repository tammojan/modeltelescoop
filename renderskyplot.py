# -*- coding: utf-8 -*-
"""
Created on Fri Apr 26 09:01:59 2019

@author: S.P. van der Linden
@description: This class contains the main code for rendering the panorama,
              given x,y coordinates of the antenna's target. Loosely based on:
              https://nerdparadise.com/programming/pygame/part7
"""

import pygame

from renderbase import RenderBase
from radiodataset import get_body_skyxy

from math import sqrt
from enum import Enum

import datetime
import threading


# Some common colours
TRANSPARANT = (0, 0, 0, 0)
BLACK = (0, 0, 0, 255)
RED = (255, 0, 0)

# Reference ID for the pygame event to update the celestial body locations
UPDATE_COORDS_EVENT = pygame.USEREVENT+1


# Enums to refer to specific celestial bodies within the application
class Bodies(Enum):
    SUN = 1
    MOON = 2
    MARS = 3
    JUPITER = 4

# Utility functions to load images correctly
def preload_image(image_path):
    return pygame.image.load(image_path).convert()


def preload_image_alpha(image_path):
    return pygame.image.load(image_path).convert_alpha()


# Main class
class RenderSkyPlot(RenderBase):
    def __init__(self):
        """ Create a RenderScene object """
        # Variable Initialisation
        self.x = 0
        self.y = 0
        self.full_init = True
        
        # Pre-load the external resources
        self.background = preload_image('resources/panorama.png')
        self.sun = preload_image_alpha('resources/sun.png')
        self.moon = preload_image_alpha('resources/moon.png')
        self.mars = preload_image_alpha('resources/mars.png')
        self.jupiter = preload_image_alpha('resources/jupiter.png')

        # Create a transparent overlay
        self.overlay = pygame.Surface(self.background.get_size(), 
                                      pygame.SRCALPHA)
        self.overlay.fill(BLACK)
        
        self.sun_xy = (0, 0)
        self.moon_xy = (0, 0)
        self.mars_xy = (0, 0)
        self.jupiter_xy = (0, 0)
        
        self.time_font = pygame.font.SysFont('Arial', 18)
        self.time_font.set_bold(True)
        
        self.last_updated_rects = [ [], [], [], [], [] ]

    def process_events(self, events, pressed_keys):
        if len(events):
            for event in events:
                if event.type == UPDATE_COORDS_EVENT:
                    # Get the locations of all the bodies of interest
                    self.update_thread = threading.Thread(target = self.__update_bodies__)
                    self.update_thread.daemon = True
                    self.update_thread.start()
                    #self.__update_bodies__()
            
    def update(self, x, y):
        """ Update the position of the search light (circular window) """
        self.x = int(x)
        self.y = int(y)
        
    def render(self, screen):
        """ Render all elements and copy to the screen """
        rects_to_update = []
        
        # First, clear the entire overlay
        self.overlay.fill(TRANSPARANT)
        
        if self.full_init:
            # We're doing a full screen update
            # (i.e. first frame to be rendered)
            
            # Draw the circular 'window' on the overlay layer
            reticle = pygame.draw.circle(self.overlay, RED, 
                                              (self.x, self.y), 20, 2)
            # Slightly inflate the reticle, as otherwise it does not account
            # for the last pixel column (off-by-one bug in pygame?)
            reticle.inflate_ip(10, 10)
            rects_to_update.append(reticle)
            
            # Draw the sun (we don't really care about the location in 
            # the first frame)
            rects_to_update.append(self.overlay.blit(
                    self.sun, (0, 0)))
            
            # Draw the moon
            rects_to_update.append(self.overlay.blit(
                    self.moon, (0, 0)))
            
            # Draw Mars
            rects_to_update.append(self.overlay.blit(
                    self.mars, (0, 0)))
            
            # Draw jupiter
            rects_to_update.append(self.overlay.blit(
                    self.jupiter, (0, 0)))

            # Blit the background image
            screen.blit(self.background, (0, 0))            

            # Blit the overlay to the screen
            screen.blit(self.overlay, (0, 0))
            
            self.full_init = False
        else:
            # This is not the first frame, and we need to update the location
            # of the circular window.

            # Draw the reticle
            reticle = pygame.draw.circle(self.overlay, RED,
                                         (self.x, self.y), 20, 2)
            
            # Slightly inflate the reticle rect, as otherwise it does not
            # account for the last pixel column (off-by-one bug in pygame?)
            reticle.inflate_ip(10, 10)
            
            # Create a union'd rect to limit the amount of redrawing of pixels
            reticle = reticle.union(self.last_updated_rects[0])
            
            rects_to_update.append(reticle)
            
            # Compute the entire updated area: the bounding box of the circle's
            # last location and the circle's current location.
            #rect_to_update = updated_rect.union(self.last_updated_rect)

            # Draw the sun
            if self.sun_xy[0] >= 0 and self.sun_xy[1] >= 0:
                sun = self.overlay.blit(self.sun, 
                                        (self.sun_xy[0]-self.sun.get_width()/2,
                                         self.sun_xy[1]-self.sun.get_height()/2))
                if len(self.last_updated_rects[1]):
                    sun = sun.union(self.last_updated_rects[1])
                rects_to_update.append(sun)
            else:
                rects_to_update.append([])
            
            # Draw the moon
            if self.moon_xy[0] >= 0 and self.moon_xy[1] >= 0:
                moon = self.overlay.blit(self.moon, 
                                        (self.moon_xy[0]-self.moon.get_width()/2,
                                         self.moon_xy[1]-self.moon.get_height()/2))
                if len(self.last_updated_rects[2]):
                    moon = moon.union(self.last_updated_rects[2])
                rects_to_update.append(moon)
            else:
                rects_to_update.append([])
            
            # Draw mars
            if self.mars_xy[0] >= 0 and self.mars_xy[1] >= 0:
                mars = self.overlay.blit(self.mars, 
                                        (self.mars_xy[0]-self.mars.get_width()/2,
                                         self.mars_xy[1]-self.mars.get_height()/2))
                if len(self.last_updated_rects[3]):
                    mars = mars.union(self.last_updated_rects[3])
                rects_to_update.append(mars)
            else:
                rects_to_update.append([])
            
            # Draw jupiter
            if self.jupiter_xy[0] >= 0 and self.jupiter_xy[1] >= 0:
                jupiter = self.overlay.blit(self.jupiter, 
                                        (self.jupiter_xy[0]-self.jupiter.get_width()/2,
                                         self.jupiter_xy[1]-self.jupiter.get_height()/2))
                if len(self.last_updated_rects[4]):
                    jupiter = jupiter.union(self.last_updated_rects[4])
                rects_to_update.append(jupiter)
            else:
                rects_to_update.append([])
            
            # Finally, redraw the circle again to make sure it is on top
            pygame.draw.circle(self.overlay, RED, (self.x, self.y), 20, 2)
            
            now = datetime.datetime.now()
            time_text = self.time_font.render("LIVE: " + now.strftime('%T %d-%m-%Y'), True, RED)
            rects_to_update.append(self.overlay.blit(time_text, (830, 1050)))
            
            # Update only the changed areas for performance
            for rect_to_update in rects_to_update:
                if len(rect_to_update):
                    screen.blit(self.background, rect_to_update, area=rect_to_update)
                    screen.blit(self.overlay, rect_to_update, area=rect_to_update)
        
        
        if len(self.last_updated_rects):
            result = self.last_updated_rects.copy() + rects_to_update.copy()
        else:
            result = rects_to_update.copy()
            
        self.last_updated_rects = rects_to_update.copy()
        return result

    def terminate(self):
        pass
    
    def check_body_distances(self):
        """ Check distances between all celestial bodies and the reticle.
            Return a reference to the closest one. """
        # Threshold for minimum amount of pixels to consider being 'over' a body
        THRESHOLD = 20.0
        
        closest = None
        closest_dist = 0.0
        
        dist_sun = sqrt((self.x-self.sun_xy[0])**2 + (self.y-self.sun_xy[1])**2)
        dist_moon = sqrt((self.x-self.moon_xy[0])**2 + (self.y-self.moon_xy[1])**2)
        dist_mars = sqrt((self.x-self.mars_xy[0])**2 + (self.y-self.mars_xy[1])**2)
        dist_jupiter = sqrt((self.x-self.jupiter_xy[0])**2 + (self.y-self.jupiter_xy[1])**2)
        
        if dist_sun <= THRESHOLD:
            closest = Bodies.SUN
            closest_dist = dist_sun
        if dist_moon <= THRESHOLD and \
            (dist_moon < closest_dist or closest_dist == 0.0):
            closest = Bodies.MOON
            closest_dist = dist_moon
        if dist_mars <= THRESHOLD and \
            (dist_mars < closest_dist or closest_dist == 0.0):
            closest = Bodies.MARS
            closest_dist = dist_mars
        if dist_jupiter <= THRESHOLD and \
            (dist_jupiter < closest_dist or closest_dist == 0.0):
            closest = Bodies.JUPITER
            closest_dist = dist_jupiter
            
        return closest
        
    def __update_bodies__(self):
        self.sun_xy = get_body_skyxy('sun')
        self.moon_xy = get_body_skyxy('moon')
        self.mars_xy = get_body_skyxy('mars')
        self.jupiter_xy = get_body_skyxy('jupiter')
        return
