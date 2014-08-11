import pygame, player
from entity import *
from computer import *

class Data(MovingEntity):
	def __init__(self, velocity = Vector(0, 0), acceleration = Vector(0, 0)):
		MovingEntity.__init__(self, pygame.Rect(0, 0, 10, 10), velocity, acceleration)
		self.player = None
	def respondToCollision(self, entity, distance):
		if isinstance(entity, player.Player):
			entity.addData(self)
			self.player = entity
			return distance
		elif isinstance(entity, Computer):
			self.world.remove(self)
			if self.player:
				self.player.image = pygame.image.load('PlayerWithPaper.png')
		else:
			if distance.y > 0:
				self.velocity.x = 0
			return MovingEntity.respondToCollision(self, entity, distance)
