class Entity:
	def __init__(self, rect, solid = True):
		self.rect = rect
		self.isSolid = solid
		self.world = None
	def setWorld(self, world):
		self.world = world
