import pygame
from entity import *

class Computer(Entity):
	def __init__(self, width, height):
		Entity.__init__(self, pygame.Rect(0, 0, width, height))
		
