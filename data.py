import pygame
from entity import *

class Data(Entity):
	def __init__(self):
		Entity.__init__(self, pygame.Rect(0, 0, 10, 10), False)
