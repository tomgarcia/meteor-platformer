import pygame
from entity import *
from data import *
from vector import *

LEFT = -1
RIGHT = 1
JUMP = -15
SPEED_MULTIPLIER = 8
GRAVITY = 1

class Player(Entity):
	def __init__(self):
		self.image = pygame.image.load('Player.png')
		Entity.__init__(self, self.image.get_rect())
		self.direction = 0
		self.velocity = Vector(0, 0)
		self.acceleration = Vector(0, GRAVITY)
		self.data = None
	def setDirection(self, direction):
		self.direction += direction
	def jump(self):
		if self.velocity.y == 0:
			self.velocity.y = JUMP
	def move(self):
		self.velocity.x = self.direction * SPEED_MULTIPLIER
		self.velocity.add(self.acceleration)
		distance = self.velocity.copy()
		dataList = self.world.move(self, distance)
		if len(dataList) > 0 and not self.data:
			self.data = dataList[0]
			self.world.remove(self.data)
			self.image = pygame.image.load('PlayerWithData.png')
