# -*- coding: utf-8 -*-
"""
Created on Thu Jun 27 11:16:27 2019

@author: S.P. van der Linden
@description: Rendering code for righthand bar
"""

import pygame

from renderbase import RenderBase

from util import draw_text

WHITE = (255, 255, 255)
BLACK = (0, 0, 0, 255)

def preload_image(image_path):
    return pygame.image.load(image_path).convert()

class RenderBar(RenderBase):
    def __init__(self):
        self.bar_mode = None
        self.bars = {}
        self.bars[0] = preload_image('./resources/sidebars/milkyway.png')
        self.bars[1] = preload_image('./resources/sidebars/sun.png')
        self.bars[2] = preload_image('./resources/sidebars/moon.png')
        self.bars[3] = preload_image('./resources/sidebars/mars.png')
        self.bars[4] = preload_image('./resources/sidebars/jupiter.png')
        self.bars[None] = preload_image('./resources/sidebars/empty.png')
        
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
                
    def set_body_of_interest(self, body: int):
        if body != self.bar_mode:
            self.bar_mode = body
            self.changed_mode = True
