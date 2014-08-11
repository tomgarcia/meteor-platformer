import pygame
from computer import *
from entity import *
from vector import *
from data import *

LEFT = -1
RIGHT = 1
JUMP = -15
SPEED_MULTIPLIER = 8
GRAVITY = 1

class Player(MovingEntity):
	def __init__(self):
		self.image = pygame.image.load('Player.png')
		MovingEntity.__init__(self, self.image.get_rect(), Vector(0, 0), Vector(0, GRAVITY))
		self.direction = 0
		self.data = None
	def setDirection(self, direction):
		self.direction += direction
	def jump(self):
		if self.velocity.y == 0:
			self.velocity.y = JUMP
	def move(self):
		self.velocity.x = self.direction * SPEED_MULTIPLIER
		MovingEntity.move(self)
	def addData(self, data):
		if not self.data:
			self.data = data
			self.world.remove(self.data)
			self.image = pygame.image.load('PlayerWithData.png')
	def respondToCollision(self, entity, distance):
		if isinstance(entity, Data):
			self.addData(entity)
			entity.player = self
			return distance
		else:
			if isinstance(entity, Computer)and self.data:
				self.data = None
				self.image = pygame.image.load('PlayerWithPaper.png')
			if isinstance(entity, Player):
				if self.data:
					data = self.data
					data.velocity = Vector(-1 * self.velocity.x, -20)
					data.acceleration = Vector(0, GRAVITY)
					self.world.add(data, (self.rect.left, self.rect.top - data.rect.height))
					self.data = None
					self.image = pygame.image.load('Player.png')
				if entity.data:
					data = entity.data
					data.velocity = Vector(self.velocity.x, -20)
					data.acceleration = Vector(0, GRAVITY)
					self.world.add(data, (entity.rect.left, entity.rect.top - data.rect.height))
					entity.data = None
					entity.image = pygame.image.load('Player.png')
			return MovingEntity.respondToCollision(self, entity, distance)
