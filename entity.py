from vector import *

class Entity:
	def __init__(self, rect):
		self.rect = rect
		self.world = None
	def setWorld(self, world):
		self.world = world

class MovingEntity(Entity):
	def __init__(self, rect, velocity, acceleration):
		Entity.__init__(self, rect)
		self.velocity = velocity
		self.acceleration = acceleration
	def move(self):
		self.velocity.add(self.acceleration)
		distance = self.velocity.copy()
		self.world.move(self, distance)
	def respondToCollision(self, entity, distance):
		otherRect = entity.rect
		difference = Vector(0, 0)
		if distance.y > 0 and abs(distance.y) >= abs(self.rect.bottom - otherRect.top):
			difference.y = otherRect.top - self.rect.bottom
			self.velocity.y = 0
		elif distance.y < 0 and abs(distance.y) >= abs(self.rect.top - otherRect.bottom):
			difference.y = otherRect.bottom - self.rect.top
			self.velocity.y = 0
		elif distance.x > 0 and abs(distance.x) >= abs(self.rect.right - otherRect.left):
			difference.x = otherRect.left - self.rect.right
		elif distance.x < 0 and abs(distance.x) >= abs(self.rect.left - otherRect.right):
			difference.x = otherRect.right - self.rect.left
		self.rect.move_ip(difference.toTuple())
		distance.add(difference)
		return distance
