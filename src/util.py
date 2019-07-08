# -*- coding: utf-8 -*-
"""
Created on Fri Jun 14 13:52:10 2019

@author: S.P. van der Linden
"""

#TODO: refactor for more straightforward usage (e.g. factory model)

from math import cos, sin, acos, atan2, degrees, radians, sqrt
from typing import Tuple

import pygame

SKY_CENTER = (530.0, 540.0)
SKY_RADIUS = 420.0 # Orig: 450.0


def altaz_to_unit(alt: float, az:float):
    """Convert alt,az coordinates to coordinates on the projected skydome
    
    Args:
        alt, az: float angle coordinates
        
    Returns:
        Tuple[float, float]: x and y coordinates on the unit circle
        (i.e. normalised to +/-1)
    
    """
    az = -(az + 90) % 360
    
    R = cos(radians(alt))
    x = R*cos(radians(az))
    y = R*sin(radians(az))
    return (x, y)


def unit_to_altaz(x, y):
    """Convert coordinates on the projected skydome to alt,az coordinates
    
    Args:
        x, y: float coordinates, normalised to the unit circle
        
    Returns:
        Tuple[float, float]: alt, az coordinates in degrees
    """
    R = sqrt(x**2 + y**2)
    alt = degrees(acos(R))
    az = (degrees(atan2(y, x)) + 270.0) % 360
    return (alt, az)


def skyxy_to_unit(sky_x: int, sky_y: int):
     """ Convert coordinates of a position on the plotted skydome to normalised
         x,y values
     
     Args:
         sky_x, sky_y: int coordinates on the sky image
             
     Returns:
         Tuple[float, float]: x, y normalised coordinates on the unit circle
     """
     
     x = (float(sky_x) - SKY_CENTER[0]) / SKY_RADIUS
     y = -((float(sky_y) - SKY_CENTER[1]) / SKY_RADIUS)
     
     return (x, y)


def unit_to_skyxy(x: float, y: float):
     """ Convert normalised x,y values on a unit circle to coordinates of a
         position on the plotted skydome
     
     Args:
         x, y: float coordinates on the unit circle
             
     Returns:
         Tuple[float, float]: x, y coordinates on the plotted skydome
     """
     sky_x = x * SKY_RADIUS + SKY_CENTER[0]
     sky_y = y * SKY_RADIUS + SKY_CENTER[1]
     return (sky_x, sky_y)
 

def draw_text(text: str, font: pygame.font, color: Tuple[int, int, int],
              width: int, background: Tuple[int, int, int] = None):
     """ Renders a pygame surface containing word-wrapped text
     
     Args:
         text: the text to be rendered
         font: the pygame font object to use
         width: the maximum width of the text block (height is considered unlimited)
             
     Returns:
         Pygame surface containing the rendered text
     """
     if width == 0:
         return font.render(text, True, color, background)
     
     lines = []
     # First loop: determine which words are placed in each line
     for in_line in text.split('\n'):

         line = ""
         words = in_line.split(' ')
         for word in words:
             if not line == "":
                 line += " "
                
             if (font.size(line + word)[0] > width):
                 lines.append(line)
                 line = word.replace('\n', '')
             else:
                 line += word
         lines.append(line)
     
     # Second loop: render each line individually
     rendered_lines = []
     total_height = 0
     for line in lines:
         rendered_line = font.render(line, True, color, background)
         total_height += rendered_line.get_height()
         rendered_lines.append(rendered_line)
         
     # Third loop: bring everything together into one surface object
     final_surface = pygame.Surface((width, total_height))
     y = 0
     for rendered_line in rendered_lines:
         final_surface.blit(rendered_line, (0, y))
         y += rendered_line.get_height() - 10
     
     return final_surface