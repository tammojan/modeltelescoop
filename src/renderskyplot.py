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
from radiodataset import get_dist_milkyway

from satellite import Satellite
from util import altaz_to_unit, unit_to_skyxy

from math import sqrt

import yaml

import datetime
import threading

import numpy as np

# Some common colours
TRANSPARANT = (0, 0, 0, 0)
BLACK = (0, 0, 0, 255)
RED = (255, 0, 0)

# Reference ID for the pygame event to update the celestial body locations
UPDATE_COORDS_EVENT = pygame.USEREVENT+1

SPAWN_SATELLITE_EVENT = pygame.USEREVENT+3


# Utility functions to load images correctly
def preload_image(image_path):
    return pygame.image.load(image_path).convert()


def preload_image_alpha(image_path):
    return pygame.image.load(image_path).convert_alpha()


class Body:
    def __init__(self, name, title, xy, img_url, sound):
        self.name = name
        self.title = title
        self.xy = xy
        self.img_url = img_url
        self.img = preload_image_alpha(img_url)
        self.sound = sound


# Main class
class RenderSkyPlot(RenderBase):
    def __init__(self):
        """ Create a RenderScene object """
        # Variable Initialisation
        self.x = 0
        self.y = 0
        self.sat_x = 0
        self.sat_y = 0
        self.full_init = True
        self.satellite = Satellite()
        
        # Pre-load the external resources
        self.background = preload_image('resources/panorama.png')
        # pygame.draw.circle(self.background, pygame.Color(150, 150, 150), (530, 540), 420, 0)
        self.reticle_surface = preload_image_alpha('resources/reticle.png')
        self.satellite_image = preload_image_alpha('resources/cubesat.png')

        bodies_yaml = yaml.safe_load(open("bodies.yml", "r"))
        self.bodies = [Body(body_dict.get("coordinates", "altaz(45, 45)"),
                            body_dict.get("title", "<< No Title >>"),
                            (0,0),
                            "resources/" + body_dict["sky_image"],
                            body_dict.get("sound", "")
                            )
                        for body_dict in bodies_yaml]

        # Create a transparent overlay
        self.overlay = pygame.Surface(self.background.get_size(), 
                                      pygame.SRCALPHA)
        self.overlay.fill(BLACK)
        
        self.time_font = pygame.font.SysFont('Arial', 28)
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
                elif event.type == SPAWN_SATELLITE_EVENT:
                    self.satellite = Satellite()
            
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
            #reticle.inflate_ip(10, 10)
            rects_to_update.append(reticle)
            
            # Draw the objects (we don't really care about the location in 
            # the first frame)
            for body in self.bodies:
                rects_to_update.append(self.overlay.blit(body.img, (0, 0)))

            # Blit the background image
            screen.blit(self.background, (0, 0))            

            # Blit the overlay to the screen
            screen.blit(self.overlay, (0, 0))
            
            self.full_init = False
        else:
            # This is not the first frame, and we need to update the location
            # of the circular window.
 
            sat_alt, sat_az = self.satellite.position()
            if sat_alt >= 0:
                (sat_x_unit, sat_y_unit) = altaz_to_unit(sat_alt, sat_az)
                (self.sat_x, self.sat_y) = unit_to_skyxy(sat_x_unit, sat_y_unit)

                # Compute the new area for the satellite
                satellite_rect = pygame.Rect(self.sat_x - self.satellite_image.get_width()/2,
                                      self.sat_y- self.satellite_image.get_height()/2,
                                      self.satellite_image.get_width(),
                                      self.satellite_image.get_height());

                # Slightly inflate the reticle rect, as otherwise it does not
                # account for the last pixel column (off-by-one bug in pygame?)
                satellite_rect.inflate_ip(2, 2)

                # Save the changed area for blitting (updating)
                rects_to_update.append(satellite_rect)

            # Compute the new area for the reticle
            reticle = pygame.Rect(self.x - self.reticle_surface.get_width()/2,
                                  self.y - self.reticle_surface.get_height()/2,
                                  self.reticle_surface.get_width(),
                                  self.reticle_surface.get_height());

            # Slightly inflate the reticle rect, as otherwise it does not
            # account for the last pixel column (off-by-one bug in pygame?)
            reticle.inflate_ip(2, 2)
            
            # Save the changed area for blitting (updating)
            rects_to_update.append(reticle)
            
            for body_num, body in enumerate(self.bodies):
                if body.xy[0] >= 0 and body.xy[1] >= 0:
                    rect = self.overlay.blit(body.img,
                                            (body.xy[0]-body.img.get_width()/2,
                                             body.xy[1]-body.img.get_height()/2))
                    rects_to_update.append(rect)
                else:
                    rects_to_update.append([])
            
            if sat_alt >= 0:
                self.overlay.blit(self.satellite_image, satellite_rect)
            self.overlay.blit(self.reticle_surface, reticle)
 
            #now = datetime.datetime.now()
            #time_text = self.time_font.render(now.strftime('%T %d-%m-%Y'), True, RED)
            #rects_to_update.append(self.overlay.blit(time_text, (820, 1050)))
            
            # Update only the changed areas for performance
            for rect_to_update in rects_to_update+self.last_updated_rects:
                if len(rect_to_update):
                    screen.blit(self.background, rect_to_update, area=rect_to_update)
                    screen.blit(self.overlay, rect_to_update, area=rect_to_update)
        
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
        THRESHOLD_SATELLITE_IN_VIEW = 80.0
        THRESHOLD_SATELLITE_DETECTED = 20.0
        THRESHOLD_MILKYWAY = 20.0
        
        closest_dist = 0.0
        
        dists = np.array([sqrt((self.x - body.xy[0])**2 + (self.y - body.xy[1])**2) for body in self.bodies])
        dist_sat = 1e6
        dist_sat = sqrt((self.x - self.sat_x)**2 + (self.y - self.sat_y)**2)

        dist_milkyway = get_dist_milkyway(self.x, self.y)

        closest_dist = np.min(dists)

        if dist_sat < THRESHOLD_SATELLITE_DETECTED:
            self.satellite.set_seen()
            return "Satelliet"
        if closest_dist <= THRESHOLD:
            return self.bodies[np.argmin(dists)].title
        elif closest_dist <= THRESHOLD_SATELLITE_IN_VIEW:
            return "Satelliet"
        elif dist_milkyway <= THRESHOLD_MILKYWAY:
            return "De Melkweg"
        else:
            return None

    def get_sat_info(self):
        return self.satellite.packets_seen
        
    def __update_bodies__(self):
        for body in self.bodies:
            body.xy = get_body_skyxy(body.name)
        return
