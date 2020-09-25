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
FADE_TIME = 500  # Sound fade-in/out time in ms 


class Bar:
    def __init__(self, image, sound):
        if not image:
            self.image = './resources/bar_empty.png'
        else:
            self.image = "./resources/" + image
        self.preloaded_image = preload_image(self.image)
          
        if not sound:
            self.preloaded_sound = None
        else:
            self.sound = './resources/sound/' + sound
            print(self.sound)
            self.preloaded_sound = pygame.mixer.Sound(self.sound)


def preload_image(image_path):
    return pygame.image.load(image_path).convert()

class RenderBar(RenderBase):
    def __init__(self):
        self.bar_mode = None
        self.bars = {}
        self.bars["De Melkweg"] = Bar('bar_milkyway.png', '')
        self.bars[None] = Bar('bar_empty.png', '')

        bodies_yaml = yaml.load(open("bodies.yml", "r"))
        for body in bodies_yaml:
            self.bars[body["title"]] = Bar(body.get("bar_image", "bar_empty.png"), body.get("sound", ""))
        
        self.full_init = True
        self.changed_mode = True
        self.current_sound = None
        
    def render(self, screen: pygame.Surface):
        rects_to_update = []
        
        # Clear the bar
        if self.full_init:
            rects_to_update = screen.fill(BLACK, pygame.Rect(1100, 0, 820, 1080))

        screen.blit(self.bars[self.bar_mode].preloaded_image, (1082, 0))

        if self.changed_mode:
            rects_to_update = screen.fill(BLACK, pygame.Rect(1100, 200, 820, 1080))
            screen.blit(self.bars[self.bar_mode].preloaded_image, (1082, 0))
            
            # Stop playing the current sound (if any)
            if self.current_sound is not None:
                self.current_sound.fadeout(FADE_TIME)
                self.current_sound = None
            
            # Update sounds
            if self.bars[self.bar_mode].preloaded_sound is not None:
                self.current_sound = self.bars[self.bar_mode].preloaded_sound
                self.current_sound.play(fade_ms=FADE_TIME)
            
            self.changed_mode = False
            
        return rects_to_update
                
    def set_body_of_interest(self, body):
        if body != self.bar_mode:
            self.bar_mode = body
            self.changed_mode = True
