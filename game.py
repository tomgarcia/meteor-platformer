import sys, pygame, json
from player import *
from wall import *
from world import *
from data import *
from pygame.locals import *
from socket import *
from server import *
from computer import *
from ConfigParser import SafeConfigParser
from random import *

#Constants- Edit game.conf to change
parser = SafeConfigParser()
parser.read('game.conf')
port = parser.getint('connection', 'port')

server = None #Acts as flag for servermode, and as the actual server object
if raw_input('Server (y/n)? ') == 'y':
	address = ('', port)
	WIN_SIZE = WIN_WIDTH, WIN_HEIGHT = parser.getint('window', 'width'), parser.getint('window', 'height')
	ROWS = parser.getint('window', 'rows')
	COLS = parser.getint('window', 'cols')
	seed = randint(0, 100000)
	constants = {'width': WIN_WIDTH, 'height': WIN_HEIGHT, 'rows': ROWS, 'cols': COLS, 'seed': seed}
	server = Server(address, json.dumps(constants))
	server.start()
else:
	address = (parser.get('connection', 'address'), port)
	sock = socket()
	sock.connect(address)
	length = int(sock.recv(1024))
	sock.send('ACK')
	s = sock.recv(2048)
	#Calls recv multiple times to get the entire message
	while len(s) < length:
		s += sock.recv(2048)
	sock.send('done')
	s = s[0:length]#cut off the extra bytes
	constants = json.loads(s)
	WIN_SIZE = WIN_WIDTH, WIN_HEIGHT = constants['width'], constants['height'] 
	ROWS = constants['rows']
	COLS = constants['cols']
	seed = constants['seed']

size = width, height = WIN_WIDTH * COLS, WIN_HEIGHT * ROWS
coords = (int(raw_input('x: ')), int(raw_input('y: '))) #Which window of the world to show
pygame.init()
screen = pygame.display.set_mode(WIN_SIZE)
clock = pygame.time.Clock()
world = World(width, height, seed)
player = world.player1
player2 = world.player2

#Method for pygame events, for both server and client
def handleEvents(events):
	for event in events:
		if event.type == QUIT:
			pygame.quit()
			sys.exit()
		elif event.type == KEYDOWN:
			if event.key == K_LEFT:
				player.setDirection(LEFT)
			elif event.key == K_RIGHT:
				player.setDirection(RIGHT)
			elif event.key == K_UP:
				player.jump()
			elif event.key == K_a:
				player2.setDirection(LEFT)
			elif event.key == K_d:
				player2.setDirection(RIGHT)
			elif event.key == K_w:
				player2.jump()
		elif event.type == KEYUP:
			if event.key == K_LEFT:
				player.setDirection(RIGHT)
			elif event.key == K_RIGHT:
				player.setDirection(LEFT)
			elif event.key == K_a:
				player2.setDirection(RIGHT)
			elif event.key == K_d:
				player2.setDirection(LEFT)

while True:
	if server:
		events = pygame.event.get()
		eventsJson = json.dumps([(event.type, event.__dict__) for event in events])
		server.send(eventsJson)
	else:
		pygame.event.pump()
		length = int(sock.recv(1024))
		sock.send('ACK')
		s = sock.recv(2048)
		#Calls recv multiple times to get the entire message
		while len(s) < length:
			s += sock.recv(2048)
		sock.send('done')
		s = s[0:length]#cut off the extra bytes
		events = [pygame.event.Event(event[0], event[1]) for event in json.loads(s)]
	handleEvents(events)
	world.update()
	area = pygame.Rect(coords[0] * screen.get_width(), coords[1] * screen.get_height(), screen.get_width(), screen.get_height()) #The area of the world to get
	screen.blit(world.getSurface(area), (0, 0))
	pygame.display.update()
	clock.tick(60)
