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
	seed = randint(0, 99999999999)
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
paused = False
gameOver = False
time = 0

#Method for pygame events, for both server and client
def handleEvents(events):
	global time, paused, gameOver, world, player, player2
	for event in events:
		if event.type == QUIT:
			pygame.quit()
			sys.exit()
		elif event.type == USEREVENT and event.code == "GAME_OVER":
			gameOver = True
		elif event.type == KEYDOWN:
			if event.key == K_p:
				paused = not paused
			elif event.key == K_r:
				paused = False
				gameOver = False
				time = 0
				world = World(width, height, seed)
				player = world.player1
				player2 = world.player2
			elif event.key == K_LEFT:
				player2.setDirection(LEFT)
			elif event.key == K_RIGHT:
				player2.setDirection(RIGHT)
			elif event.key == K_UP and not paused:
				player2.jump()
			elif event.key == K_a:
				player.setDirection(LEFT)
			elif event.key == K_d:
				player.setDirection(RIGHT)
			elif event.key == K_w and not paused:
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
		if time >= 60000 and not gameOver:
			gameOver = True
			events.append(pygame.event.Event(USEREVENT, {'code': 'GAME_OVER'}))
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
	if gameOver:
		if player.score > player2.score:
			text = 'Player 1 won'
		elif player2.score > player.score:
			text = 'Player 2 won'
		else:
			text = 'Tie'
		msg = pausedFont.render('Game Over', 1, (0, 0, 0))
		winnermsg = pausedFont.render(text, 2, (0, 0, 0))
		words = pygame.Surface((max(msg.get_width(), winnermsg.get_width()), msg.get_height() + winnermsg.get_height()))
		words.fill((255, 255, 255))
		words.blit(msg, [0, 0])
		words.blit(winnermsg, [0, msg.get_height()])
		loc = (screen.get_width() / 2 - words.get_width() / 2, screen.get_height() / 2 - words.get_height() / 2)
		screen.blit(words, loc)
	elif not paused:
		world.update()
		area = pygame.Rect(coords[0] * screen.get_width(), coords[1] * screen.get_height(), screen.get_width(), screen.get_height()) #The area of the world to get
		screen.blit(world.getSurface(area), (0, 0))
	elif paused:
		words = pausedFont.render('Paused', 1, (0, 0, 0))
		loc = (screen.get_width() / 2 - words.get_width() / 2, screen.get_height() / 2 - words.get_height() / 2)
		screen.blit(words, loc)
	pygame.display.update()
	ctr = clock.tick(60)
	if not paused:
		time += ctr
