from entity import *
import pygame

class Wall(Entity):
	def __init__(self, width, height):
		Entity.__init__(self, pygame.Rect(0, 0, width, height))
