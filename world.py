import pygame
from wall import *
from data import *
from player import *

white = 255, 255, 255
black = 0, 0, 0
blue = 0, 0, 255

class World:
	def __init__(self, width, height):
		self.entityList = []
		self.solidList = []
		self.dataList = []
		self.size = self.width, self.height = width, height
		leftWall = Wall(0, self.height)
		rightWall = Wall(0, self.height)
		floor = Wall(self.width, self.height) #The floor is extra tall so that players cannot accidently fall through
		self.add(leftWall, (-1, 0))
		self.add(rightWall, (self.width + 1, 0))
		self.add(floor, (0, self.height + 1))
	def add(self, entity, loc):
		entity.rect.move_ip(loc)
		entity.setWorld(self)
		self.entityList.append(entity)
		if entity.isSolid:
			self.solidList.append(entity)
		elif isinstance(entity, Data):
			self.dataList.append(entity)
	def remove(self, entity):
		if entity in self.entityList:
			self.entityList.remove(entity)
		if entity in self.solidList:
			self.solidList.remove(entity)
		if entity in self.dataList:
			self.dataList.remove(entity)
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
				else:
					surf.fill(blue, entity.rect.move(-1 * area.left, -1 * area.top))
		return surf
	#Moves entities within the world, and handles collision detection and response. Use this instead of Rect.move for entities
	def move(self, entity, distance):
		entity.rect.move_ip(distance.toTuple())
		if entity.isSolid:
			rects = [e.rect for e in self.solidList if e is not entity]
			index = entity.rect.collidelist(rects)
			while index > -1:
					distance = respondToCollision(entity, rects[index], distance)
					index = entity.rect.collidelist(rects)
		rects = [data.rect for data in self.dataList]
		indexes = entity.rect.collidelistall(rects)
		return [self.dataList[index] for index in indexes] #Returns a list of data the player intersects with, so that the player class can collect the data
def respondToCollision(entity, otherRect, distance):
	difference = Vector(0, 0)
	if distance.y > 0 and abs(distance.y) >= abs(entity.rect.bottom - otherRect.top):
		difference.y = otherRect.top - entity.rect.bottom
		entity.velocity.y = 0
	elif distance.y < 0 and abs(distance.y) >= abs(entity.rect.top - otherRect.bottom):
		difference.y = otherRect.bottom - entity.rect.top
		entity.velocity.y = 0
	if distance.x > 0 and abs(distance.x) >= abs(entity.rect.right - otherRect.left):
		difference.x = otherRect.left - entity.rect.right
	elif distance.x < 0 and abs(distance.x) >= abs(entity.rect.left - otherRect.right):
		difference.x = otherRect.right - entity.rect.left
	entity.rect.move_ip(difference.toTuple())
	distance.add(difference)
	return distance
