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
        
        self.stlogo = preload_image('./resources/stlogo.png')
        self.astronlogo = preload_image('./resources/astronlogo.png')
        self.full_init = True
        self.changed_mode = True
        
        # Load fonts
        title_font = pygame.font.Font('resources/font/Now-Bold.otf', 64)
        subtitle_font = pygame.font.Font('resources/font/Now-Regular.otf', 40)
        
        # Sun info
        self.sun_title_text = title_font.render('De Zon', True, WHITE)
        self.sun_mosaic = preload_image('resources/sun_mosaic.jpg')
        
        self.title_text = title_font.render('Verken de radiosterrenhemel',
                                             True, WHITE)
        self.subtitle_text = subtitle_font.render('Beweeg de radiotelescoop om te richten',
                                             True, WHITE)
        
        self.sun_par1 = draw_text("De zon maakt licht op alle 'kleuren', " +\
                                  "dus ook radiogolven. Als de zon extra actief " +\
                                  "is, komen er zulke sterke radiogolven vanaf dat " +\
                                  "die satellieten van slag kunnen brengen. ",
                                  subtitle_font, WHITE, 450)
        self.sun_par2 = draw_text("Daarom is het belangrijk om de radiogolven " +\
                                  "van de zon goed in de gaten te houden en te " +\
                                  "voorspellen.", subtitle_font, WHITE, 800)
        
        # Moon info
        self.moon_title_text = title_font.render('De Maan', True, WHITE)
        self.moon_photo = preload_image('resources/fullmoon.jpg')
        self.moon_par1 = draw_text("Radiozendamateurs gebruiken de maan om " +\
                                   "contact te maken met de andere kant van de " +\
                                   "aarde. Ze gebruiken de maan daarbij als " +\
                                   "spiegel.", subtitle_font, WHITE, 450)
        self.moon_par2 = draw_text("Dit kan alleen met heel gevoelige " +\
                                   "apparatuur, omdat de maan 93% van het " +\
                                   "signaal helemaal niet weerkaatst.\nHet " +\
                                   "duurt 2.5 seconde voor het signaal terug " +\
                                   "is, omdat de maan zo ver weg staat.",
                                   subtitle_font, WHITE, 800)
        
        # Mars info
        self.mars_title_text = title_font.render('Mars', True, WHITE)
        self.mars_photo = preload_image('resources/mars_photo.jpg')
        
        # Jupiter info
        self.jupiter_title_text = title_font.render('Jupiter', True, WHITE)
        self.jupiter_photo = preload_image('resources/jupiter_photo.jpg')
        
    def render(self, screen: pygame.Surface):
        rects_to_update = []
        # Clear the bar
        
        if self.full_init:
            rects_to_update = screen.fill(BLACK, pygame.Rect(1100, 0, 820, 1080))
            screen.blit(self.stlogo, (1200, 970))
            screen.blit(self.astronlogo, (1500, 970))
            
            screen.blit(self.title_text, (1100, 10))
            screen.blit(self.subtitle_text, (1100, 80))
            self.full_init = False
        if self.changed_mode:
            rects_to_update = screen.fill(BLACK, pygame.Rect(1100, 200, 820, 1080))

            if self.bar_mode == 1:
                ### --- Sun --- ###
                screen.blit(self.sun_title_text, (1600, 250))
                pygame.draw.line(screen, WHITE, 
                                 (1100, 295), (1590, 295), 4)
                pygame.draw.line(screen, WHITE, 
                                 (1800, 295), (1910, 295), 4)
                screen.blit(self.sun_mosaic, (1600, 370))
                
                screen.blit(self.sun_par1, (1100, 350))
                screen.blit(self.sun_par2, (1100, 700))
                
                ### --- Moon --- ###
            if self.bar_mode == 2:
                screen.blit(self.moon_title_text, (1570, 250))
                pygame.draw.line(screen, WHITE, 
                                 (1100, 295), (1560, 295), 4)
                pygame.draw.line(screen, WHITE, 
                                 (1820, 295), (1910, 295), 4)
                
                screen.blit(self.moon_photo, (1150, 370))
                
                screen.blit(self.moon_par1, (1500, 350))
                screen.blit(self.moon_par2, (1100, 650))
                
                ### --- Mars --- ###
            if self.bar_mode == 3:
                screen.blit(self.mars_title_text, (1668, 250))
                pygame.draw.line(screen, WHITE, 
                                 (1100, 295), (1650, 295), 4)
                pygame.draw.line(screen, WHITE, 
                                 (1820, 295), (1910, 295), 4)
                
                screen.blit(self.mars_photo, (1200, 330))
                
                ### --- Jupiter --- ###
            if self.bar_mode == 4:
                screen.blit(self.jupiter_title_text, (1610, 250))
                pygame.draw.line(screen, WHITE, 
                                 (1100, 295), (1590, 295), 4)
                pygame.draw.line(screen, WHITE, 
                                 (1820, 295), (1910, 295), 4)
                
                screen.blit(self.jupiter_photo, (1200, 330))
            self.changed_mode = False
            
        return rects_to_update
                
    def set_body_of_interest(self, body: int):
        if body != self.bar_mode:
            self.bar_mode = body
            self.changed_mode = True
