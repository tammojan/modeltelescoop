# -*- coding: utf-8 -*-
"""
Created on Tue May 21 10:00:52 2019

@author: S.P. van der Linden
"""

import pygame
import numpy as np
from scipy.interpolate import interp1d

from renderbase import RenderBase

BLACK = (0, 0, 0)
PADDING = 20
THICKNESS = 3

class RenderLinePlot(RenderBase):
    def __init__(self, x: np.array, y: np.array, location: pygame.Rect):
        """ Create a RenderPlot object """
        # Variable Initialisation
        self.location = location
        self.x = x
        self.y = y
        self.canvas = pygame.Surface((location.width, location.height))
        self.in_animation = False
            
    def set_data(self, x:np.array, y: np.array):
        self.x = x
        self.y = y
      
    def process_events(self, events, pressed_keys):
        pass
    
    def update(self):
        pass
    
    def render(self, screen: pygame.Surface):
        """ Render all elements and copy to the screen """
        
        width = self.location.width
        height = self.location.height
        
        # Reset the background
        self.canvas.fill(BLACK)
        
        x_shift = self.x - self.x.min()
        y_shift = self.y - self.y.min()
        
        # Flip the y-coordinates, as pygame's origin is top-left
        y_shift = y_shift.max() - y_shift
        
        # Interpolate the points
        y_interp = interp1d(x_shift, y_shift, kind='cubic')
        
        # Create the pixel coordinates on the x-axis
        x_render = np.linspace(PADDING, width - PADDING, width - 2*PADDING)
        x_interp = np.linspace(x_shift.min(), x_shift.max(), x_render.size)
        
        # Get the interpolated values for every pixel on the x-axis
        y_render = y_interp(x_interp)
        y_render = np.round(y_render / y_render.max() * (height - 2*PADDING))
        
        last_xy = np.array([])
        
        # Draw lines between all the points in the dataset
        for (x, y) in zip(x_render.astype(int), y_render.astype(int)):
            this_xy = np.array([x, y+PADDING])
            if last_xy.size:# and np.linalg.norm(last_xy-this_xy) > THICKNESS:
                pygame.draw.line(self.canvas, (255, 0, 0), last_xy, this_xy, THICKNESS)
            
            last_xy = this_xy
            
        # Draw X-axis
        pygame.draw.line(self.canvas, (255, 0, 0), 
                         (PADDING, height-PADDING),
                         (width-PADDING, height-PADDING))
        
        # Draw Y-axis
        pygame.draw.line(self.canvas, (255, 0, 0), 
                         (PADDING, PADDING),
                         (PADDING, height-PADDING))
        
        screen.blit(self.canvas, self.location)
        
        return self.location
        
    
    def terminate(self):
        pass
