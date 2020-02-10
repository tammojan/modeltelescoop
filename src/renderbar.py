# -*- coding: utf-8 -*-
"""
Created on Thu Jun 27 11:16:27 2019

@author: S.P. van der Linden and T.J. Dijkema
@description: Rendering code for righthand bar
"""

import pygame

from renderbase import RenderBase
import yaml

WHITE = (255, 255, 255)
BLACK = (0, 0, 0, 255)

def preload_image(image_path):
    return pygame.image.load(image_path).convert()

class RenderBar(RenderBase):
    def __init__(self):
        self.bar_mode = None
        self.bars = {}
        self.bars["De Melkweg"] = preload_image('./resources/bar_milkyway.png')
        self.bars[None] = preload_image('./resources/bar_empty.png')

        bodies_yaml = yaml.load(open("bodies.yml", "r"))
        for body in bodies_yaml:
            self.bars[body["title"]] = preload_image("./resources/" + body["bar_image"])
        
        self.full_init = True
        self.changed_mode = True
        
    def render(self, screen: pygame.Surface):
        rects_to_update = []
        # Clear the bar
        
        if self.full_init:
            rects_to_update = screen.fill(BLACK, pygame.Rect(1100, 0, 820, 1080))

        screen.blit(self.bars[self.bar_mode], (1082, 0))

        if self.changed_mode:
            rects_to_update = screen.fill(BLACK, pygame.Rect(1100, 200, 820, 1080))
            screen.blit(self.bars[self.bar_mode], (1082, 0))

            self.changed_mode = False
            
        return rects_to_update
                
    def set_body_of_interest(self, body):
        if body != self.bar_mode:
            self.bar_mode = body
            self.changed_mode = True
