import pygame, pygame.font
from wall import *
from data import *
from player import *
from entity import *

white = 255, 255, 255
black = 0, 0, 0
red = 255, 0, 0
green = 0, 255, 0
blue = 0, 0, 255
SPRITE_LENGTH = 25
pygame.font.init()
scoreFont = pygame.font.SysFont(pygame.font.get_default_font(), 40)

class World:
	def __init__(self, width, height):
		self.entityList = []
		self.movingList = []
		self.size = self.width, self.height = width, height
		leftWall = Wall(0, self.height)
		rightWall = Wall(0, self.height)
		floor = Wall(self.width, self.height) #The floor is extra tall so that players cannot accidently fall through
		self.add(leftWall, (-1, 0))
		self.add(rightWall, (self.width + 1, 0))
		self.add(floor, (0, self.height + 1))
		self.player1 = Player()
		self.player2 = Player()
		self.fillLevel('level.map')
	def fillLevel(self, mapname):
		f = file(mapname, 'r')
		loc = [0, 0]
		for line in f:
			for char in line:
				e = self.newEntity(char)
				if e:
					self.add(e, loc)
				loc[0] += SPRITE_LENGTH
			loc[0] = 0
			loc[1] += SPRITE_LENGTH
	def newEntity(self, char):
		if char == 'P':
			return self.player1
		elif char == 'p':
			return self.player2
		elif char == 'W':
			return Wall(25, 25)
		elif char == 'D':
			return Data()
		elif char == 'C':
			return Computer(25, 25)
		else:
			return None
	def update(self):
		for e in self.movingList:
			e.move()
	def add(self, entity, loc):
		entity.rect.topleft = loc
		entity.setWorld(self)
		self.entityList.append(entity)
		if isinstance(entity, MovingEntity):
			self.movingList.append(entity)
	def remove(self, entity):
		if entity in self.entityList:
			self.entityList.remove(entity)
		if entity in self.movingList:
			self.movingList.remove(entity)
	#Gets the surface showing all entities within the given area rectangle
	def getSurface(self, area):
		surf = pygame.Surface((self.width / 2, self.height / 2))
		surf.fill(white)
		for entity in self.entityList:
			if entity.rect.colliderect(area): #Entities outside the rectangle aren't even drawn
				if isinstance(entity, Player):
					surf.blit(entity.image, entity.rect.move(-1 * area.left, -1 * area.top))
				elif isinstance(entity, Wall):
					surf.fill(black, entity.rect.move(-1 * area.left, -1 * area.top))
				elif isinstance(entity, Data):
					surf.fill(blue, entity.rect.move(-1 * area.left, -1 * area.top))
				else:
					surf.fill(red, entity.rect.move(-1 * area.left, -1 * area.top))
		if area.topleft == (0, 0):
			score = scoreFont.render('Player 1: ' + str(self.player1.score), 1, black)
			surf.blit(score, (0, 0))
		if area.topright == (self.width, 0):
			score = scoreFont.render('Player 2: ' + str(self.player2.score), 1, black)
			surf.blit(score, (surf.get_width() - 10 - score.get_width(), 0))
		return surf
	#Moves entities within the world, and handles collision detection and response. Use this instead of Rect.move for entities
	def move(self, entity, distance):
		entity.rect.move_ip(distance.toTuple())
		entities = [e for e in self.entityList if e is not entity]
		rects = [e.rect for e in entities]
		index = entity.rect.collidelist(rects)
		indices = []
		while index > -1 and index not in indices:
				indices.append(index)
				distance = entity.respondToCollision(entities[index], distance)
				index = entity.rect.collidelist(rects)
