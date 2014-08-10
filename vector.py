class Vector:
	def __init__(self, x, y):
		self.x = x
		self.y = y
	def add(self, vector):
		self.x += vector.x
		self.y += vector.y
	def subtract(self, vector):
		self.x -= vector.x
		self.y -= vector.y
	def toTuple(self):
		return (self.x, self.y)
	def copy(self):
		return Vector(self.x, self.y)
