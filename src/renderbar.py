# -*- coding: utf-8 -*-
"""
Created on Thu Jun 27 11:16:27 2019

@author: S.P. van der Linden and T.J. Dijkema
@description: Rendering code for righthand bar
"""

import pygame

from renderbase import RenderBase
from numpy.random import choice
from glob import glob
import yaml
from renderskyplot import SPAWN_SATELLITE_EVENT

WHITE = (255, 255, 255)
BLACK = (0, 0, 0, 255)
FADE_TIME = 500  # Sound fade-in/out time in ms 


class Bar:
    def __init__(self, image, sound, soundloop=False):
        if not image:
            self.image = './resources/bar_empty.png'
        else:
            self.image = "./resources/" + image

        if image.endswith(".gif"):
            self.animated_gif = True
        else:
            self.preloaded_image = preload_image(self.image)
          
        if not sound:
            self.preloaded_sound = None
        else:
            self.sound = './resources/sound/' + sound
            self.preloaded_sound = pygame.mixer.Sound(self.sound)
            self.soundloop = -1 if soundloop else 0

def preload_image(image_path):
    return pygame.image.load(image_path).convert()

class RenderBar(RenderBase):
    def __init__(self):
        self.bar_mode = None
        self.bars = {}
        self.bars["De Melkweg"] = Bar('bar_milkyway.png', '')
        self.bars["Satelliet"] = Bar('bar_satelliet.png', '')
        self.bars[None] = Bar('bar_empty.png', '')

        bodies_yaml = yaml.safe_load(open("bodies.yml", "r"))
        for body in bodies_yaml:
            self.bars[body["title"]] = Bar(body.get("bar_image", "bar_empty.png"), body.get("sound", ""), soundloop=body.get("soundloop", False))
        
        self.full_init = True
        self.changed_mode = True
        self.current_sound = None
        
    def render(self, screen: pygame.Surface):
        rects_to_update = []
        
        # Clear the bar
        if self.full_init:
            rects_to_update = [screen.fill(BLACK, pygame.Rect(1100, 0, 820, 1080))]
            self.full_init = False

        if self.changed_mode:
            rect = screen.blit(self.bars[self.bar_mode].preloaded_image, (1082, 0))
            rects_to_update.append(rect)
            
            # Stop playing the current sound (if any)
            if self.current_sound is not None:
                self.current_sound.fadeout(FADE_TIME)
                self.current_sound = None
            
            # Update sounds
            if self.bars[self.bar_mode].preloaded_sound is not None:
                self.current_sound = self.bars[self.bar_mode].preloaded_sound
                self.current_sound.play(fade_ms=FADE_TIME, loops=self.bars[self.bar_mode].soundloop)
            
            self.changed_mode = False

        if self.bar_mode == "Satelliet":
            for row in range(480):
                if self.sat_packets_seen[row] > 0:
                    rect = screen.blit(self.satellite_image, (1082+50, 540+row), pygame.Rect(0, row, 640, 1))
                    rects_to_update.append(rect)

        return rects_to_update
                
    def set_body_of_interest(self, body):
        if body != self.bar_mode:
            self.bar_mode = body
            self.changed_mode = True

    def set_sat_info(self, sat_info):
        self.sat_packets_seen = sat_info

    def load_satellite_image(self):
        all_images = glob("./resources/sat_images/estcube*.png")
        image_path = choice(all_images)
        self.satellite_image = preload_image(image_path)

    def process_events(self, events, pressed_keys):
        if len(events):
            for event in events:
                if event.type == SPAWN_SATELLITE_EVENT:
                    self.load_satellite_image()
