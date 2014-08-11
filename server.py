from socket import *
from ConfigParser import SafeConfigParser
from threading import Thread, Lock
import sys, json, logging

class Server(Thread):
	#Welcome data is the message sent to clients when they first connect. It is used for sending constants (e.g. window size)
	def __init__(self, address, welcomeData):
		Thread.__init__(self, name = 'Server')
		self.sock = socket()
		self.sock.bind(address)
		self.sock.listen(5)
		self.clients = []
		self.clientLock = Lock()
		self.welcomeData = welcomeData
		self.setDaemon(True)
	def run(self):
		while True:
			(client, clAddr) = self.sock.accept()
			self.addClient(client)
	def send(self, msg):
		with self.clientLock:
			for client in self.clients:
				sendToClient(client, msg)
	def addClient(self, client):
		with self.clientLock:
			sendToClient(client, self.welcomeData)
			self.clients.append(client)
def sendToClient(client, msg):
	try:
		client.send(str(len(msg))) #The client can't recieve all the data in one go, so I have to tell it how much data to wait for
		logging.debug('sending ' + str(len(msg)) + ' bytes')
		client.recv(3)
		client.sendall(msg)
		client.recv(4) #waiting to keep the client and server in sync
	except:
		pass
