import pygame, pygame.font
from wall import *
from data import *
from player import *
from entity import *
from random import *

white = 255, 255, 255
black = 0, 0, 0
red = 255, 0, 0
green = 0, 255, 0
blue = 0, 0, 255
SPRITE_LENGTH = 25
pygame.font.init()
scoreFont = pygame.font.SysFont(pygame.font.get_default_font(), 40)
pausedFont = pygame.font.SysFont('helvetica', 100)

class World:
	def __init__(self, width, height, randomseed):
		self.entityList = []
		self.movingList = []
		self.size = self.width, self.height = width, height
		seed(randomseed)
		leftWall = Wall(0, self.height)
		rightWall = Wall(0, self.height)
		floor = Wall(self.width, self.height) #The floor is extra tall so that players cannot accidently fall through
		self.boundaries = [leftWall, rightWall, floor]
		self.add(leftWall, (-1, 0))
		self.add(rightWall, (self.width + 1, 0))
		self.add(floor, (0, self.height + 1))
		self.player1 = Player()
		self.player2 = Player()
		self.fillLevel('level.map')
		self.paused = False
		self.gameOver = False
	def pause(self):
		self.paused = not self.paused
	def end(self):
		self.gameOver = True
	def fillLevel(self, mapname):
		f = file(mapname, 'r')
		lines = f.read().split('\n')
		loc = [0, self.height]
		for line in reversed(lines):
			for char in line:
				e = self.newEntity(char)
				if e:
					self.add(e, loc)
				loc[0] += SPRITE_LENGTH
			loc[0] = 0
			loc[1] -= SPRITE_LENGTH
	def newEntity(self, char):
		if char == 'P':
			return self.player1
		elif char == 'p':
			return self.player2
		elif char == 'W':
			return Wall(SPRITE_LENGTH, SPRITE_LENGTH)
		elif char == 'D':
			return Data()
		elif char == 'C':
			return Computer(SPRITE_LENGTH, SPRITE_LENGTH)
		else:
			return None
	def randomData(self):
		data = Data()
		walls = [entity for entity in self.entityList if isinstance(entity, Wall) and entity not in self.boundaries]
		wall = choice(walls)
		x = wall.rect.left
		y = wall.rect.top - 100
		self.add(data, (x, y))
	def update(self):
		if not self.paused:
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
		if self.gameOver:
			if self.player1.score > self.player2.score:
				text = 'Player 1 won'
			elif self.player2.score > self.player1.score:
				text = 'Player 2 won'
			else:
				text = 'Tie'
			msg = pausedFont.render('Game Over', 1, black)
			winnermsg = pausedFont.render(text, 2, black)
			words = pygame.Surface((max(msg.get_width(), winnermsg.get_width()), msg.get_height() + winnermsg.get_height()))
			words.fill(white)
			words.blit(msg, [0, 0])
			words.blit(winnermsg, [0, msg.get_height()])
			loc = (self.width / 2 - words.get_width() / 2 - area.left, self.height / 2 - words.get_height() / 2 - area.top)
			surf.blit(words, loc)
		elif self.paused:
			words = pausedFont.render('Paused', 1, black)
			surf.blit(words, (self.width / 2 - words.get_width() / 2 - area.left, self.height / 2 - words.get_height() / 2 - area.top))
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
