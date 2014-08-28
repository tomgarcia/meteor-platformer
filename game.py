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
pausedFont = pygame.font.SysFont('helvetica', 100)

server = None #Acts as flag for servermode, and as the actual server object
if raw_input('Server (y/n)? ') == 'y':
	address = ('', port)
	WIN_SIZE = WIN_WIDTH, WIN_HEIGHT = parser.getint('window', 'width'), parser.getint('window', 'height')
	ROWS = parser.getint('window', 'rows')
	COLS = parser.getint('window', 'cols')
	BORDER = parser.getint('window', 'border')
	seed = randint(0, 99999999999)
	constants = {'width': WIN_WIDTH, 'height': WIN_HEIGHT, 'rows': ROWS, 'cols': COLS, 'border': BORDER, 'seed': seed}
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
	BORDER = constants['border']
	seed = constants['seed']

size = width, height = WIN_WIDTH * COLS + BORDER * (COLS - 1), WIN_HEIGHT * ROWS + BORDER * (ROWS - 1)
coords = (int(raw_input('x: ')), int(raw_input('y: '))) #Which window of the world to show
pygame.init()
screen = pygame.display.set_mode(WIN_SIZE)
clock = pygame.time.Clock()
world = World(width, height, seed)
player = world.player1
player2 = world.player2
time = 0

#Method for pygame events, for both server and client
def handleEvents(events):
	global time, world, player, player2
	for event in events:
		if event.type == QUIT:
			pygame.quit()
			sys.exit()
		elif event.type == USEREVENT and event.code == "GAME_OVER":
			world.end()
		elif event.type == KEYDOWN:
			if event.key == K_p:
				world.pause()
			elif event.key == K_r:
				time = 0
				world = World(width, height, randint(0, 99999999999))
				player = world.player1
				player2 = world.player2
			elif event.key == K_LEFT:
				player2.setDirection(LEFT)
			elif event.key == K_RIGHT:
				player2.setDirection(RIGHT)
			elif event.key == K_UP and not world.paused:
				player2.jump()
			elif event.key == K_a:
				player.setDirection(LEFT)
			elif event.key == K_d:
				player.setDirection(RIGHT)
			elif event.key == K_w and not world.paused:
				player.jump()
		elif event.type == KEYUP:
			if event.key == K_LEFT:
				player2.setDirection(RIGHT)
			elif event.key == K_RIGHT:
				player2.setDirection(LEFT)
			elif event.key == K_a:
				player.setDirection(RIGHT)
			elif event.key == K_d:
				player.setDirection(LEFT)

while True:
	if server:
		events = pygame.event.get()
		if time >= 60000 and not world.gameOver:
			world.end()
			events.append(pygame.event.Event(USEREVENT, {'code': 'GAME_OVER'}))
		eventsJson = []
		for event in events:
			if event.type == USEREVENT:
				eventsJson.append((event.type, {'code': event.code}))
			elif event.type == KEYDOWN:
				eventsJson.append((event.type, {'key': event.key, 'mod': event.mod, 'unicode': event.unicode}))
			elif event.type == KEYUP:
				eventsJson.append((event.type, {'key': event.key, 'mod': event.mod}))
			else:
				eventsJson.append((event.type, {}))
		server.send(json.dumps(eventsJson))
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
	area = pygame.Rect(coords[0] * (screen.get_width() + BORDER), coords[1] * (screen.get_height() + BORDER), screen.get_width(), screen.get_height()) #The area of the world to get
	screen.blit(world.getSurface(area), (0, 0))
	pygame.display.update()
	ctr = clock.tick(60)
	if not world.paused:
		time += ctr
