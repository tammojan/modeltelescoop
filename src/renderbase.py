# -*- coding: utf-8 -*-
"""
Created on Fri Jun 14 11:24:57 2019

@author: S.P. van der Linden
@description: Template for all rendering classes. Based on:
              https://nerdparadise.com/programming/pygame/part7
"""

class RenderBase:
    def __init__(self):
        self.next = self
    
    def process_input(self, events):
        pass

    def update(self):
        pass

    def render(self, screen):
        pass
