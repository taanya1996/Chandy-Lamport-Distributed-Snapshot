import sys
import socket
import pickle
import time
import threading
import random
from threading import Thread
from common import *
import datetime as dt


buff_size = 1024
pid = 0

c2c_connections = {}
outgoing = []
incoming = []
myQueue=[]
tQueue=[]
myQueueLock = threading.RLock()
tQueueLock= threading.RLock()
TokenLock = threading.RLock()
snapLock = threading.RLock()
markerLock= threading.RLock()
token=False

markerCount=0
markersInProgress = {}
markersDone=[]

prob=0
toggle=""

def sleep():
	time.sleep(3)

def incrementMarker():
	global markerCount
	markerCount += 1
	return str(pid) + "|" + str(markerCount)

def getRandomIndex():
	randNo=random.randint(0, 100)
	if(randNo<prob):
		return None
	ind=random.randint(0, len(outgoing)-1)
	return ind

class MasterHandler(Thread):
	def __init__(self):
		Thread.__init__(self)

	def run(self):
		global token
		token=False
		while True:
			if len(myQueue) != 0:
				myQueueLock.acquire()
				data = myQueue.pop(0)
				dataTime=tQueue.pop(0)
				delta=time.time()-dataTime
				if(delta<3):
					time.sleep(3-delta)
				if data.reqType == "TOKEN":
					#print("=====================================================")
					print("Recieved Token from " + str(data.fromClient)+ " ",dt.datetime.now())
					for markerId in markersInProgress:
						if(markersInProgress[markerId].listenToChannel[data.fromClient] == True):
							markersInProgress[markerId].channelMessages[data.fromClient].append("T")
					TokenLock.acquire()
					#ind=random.randint(0, len(outgoing)-1)
					token=True
					time.sleep(1)
					ind=getRandomIndex()
					if(ind==None):
						print("Token is lost")
						token=False
						TokenLock.release()
						continue
					
					receiver=outgoing[ind]
					token=False
					TokenLock.release()
					message=Messages("TOKEN",pid,"")
					#print("=====================================================")
					print("Sending token to ", receiver)
					c2c_connections[receiver].send(pickle.dumps(message))
					#print("=====================================================")
					
				elif data.reqType == "MARKER":
					snapLock.acquire()
					print("Recieved MARKER for "+ str(data.markerId) +" from " + str(data.fromClient)+ " at ", dt.datetime.now())

					for markerId in markersInProgress:
						if(data.markerId != markerId and markersInProgress[markerId].listenToChannel[data.fromClient] == True):
							markersInProgress[markerId].channelMessages[data.fromClient].append(data.markerId)

					if ((data.markerId in markersInProgress) and (data.markerId not in markersDone)) :
						#print("entering into channel data addition step")
						if markersInProgress[data.markerId].listenToChannel[data.fromClient] == True:
							markersInProgress[data.markerId].listenToChannel[data.fromClient] = False
							#print(" Appending recieved markers : " + str(data.fromClient))
							markersInProgress[data.markerId].recievedMarkers.append(data.fromClient)
							self.handleRecievedMarkers(data)
					else:
						if(data.markerId in markersDone):
							#print("SNAP already sent for {}".format(data.markerId))
							pass
						else:
							print("marker received for the first time")
							markerLock.acquire()
							sendMarkers(data.markerId, data.fromClient)
							self.handleRecievedMarkers(data)
							markerLock.release()
					snapLock.release()

				elif data.reqType == "SNAP":
					#print("MarkerId:", data.markerId)
					#print("MarkersDone",markersDone)
					if(data.markerId not in markersDone):
						print("Recieved SNAPSHOT for "+ str(data.markerId) +" from " + str(data.fromClient)+ " ", dt.datetime.now())
						self.handleLocalSnaps(data)
				myQueueLock.release()



	def handleRecievedMarkers(self, data):
		#print("Recieved markers for " + str(data.markerId)+":")
		'''
		for i in markersInProgress[data.markerId].recievedMarkers:
			print(str(i))
		
		print("Incoming: ")
		for i in incoming:
			print(i)
		'''

		initiator = int(data.markerId.split("|")[0])
		if len(markersInProgress[data.markerId].recievedMarkers) == len(incoming):
			channelState = {}
			for i in incoming:
				channelState[i] = markersInProgress[data.markerId].channelMessages[i]
			locState = State("SNAP", pid, data.markerId, markersInProgress[data.markerId].tokenState, channelState)
			if initiator == pid:
				print("Sending myself local snap for global snap i have initiated")
				self.handleLocalSnaps(locState)
			else:
				try:
					c2c_connections[initiator].send(pickle.dumps(locState))
					print("Sending SNAPSHOT for "+ str(data.markerId) +" to " + str(initiator))
				except:
					print("Failed to send SNAPSHOT for {} to {}".format(data.markerId, initiator))
				markersDone.append(data.markerId)

	def handleLocalSnaps(self, data):
		if(data.fromClient not in markersInProgress[data.markerId].recievedSnaps):
			markersInProgress[data.markerId].recievedSnaps[data.fromClient] = data
			markersInProgress[data.markerId].snapshotCount += 1
			print("Received local snap from {} and waiting for {} more".format(data.fromClient, 5 - markersInProgress[data.markerId].snapshotCount))

		if markersInProgress[data.markerId].snapshotCount == 5:
			markersDone.append(data.markerId)
			self.printGlobalSnap(data.markerId)


	def printGlobalSnap(self, markerId):
		print("=====================================================")
		print("Client States")
		for client in range(1,6):
			print("Token state of "+ str(client) +": " + str(markersInProgress[markerId].recievedSnaps[client].tokenState))
		print("Channel states: ")
		for client in range(1,6):
			#print("State of "+str(client)+": ")
			#print("Token state of "+ str(client) +": " + str(markersInProgress[markerId].recievedSnaps[client].tokenState))
			#print("Channel states: ")
			for channel in markersInProgress[markerId].recievedSnaps[client].channelState:
				print(channel,"-->",client,":",str(markersInProgress[markerId].recievedSnaps[client].channelState[channel]))
				#print(str(channel) + " : " + str(markersInProgress[markerId].recievedSnaps[client].channelState[channel]))
		print("=====================================================")

class ClientConnections(Thread):
	def __init__(self,connection):
		Thread.__init__(self)
		self.connection = connection

	def run(self):
		while True:
			response = self.connection.recv(buff_size)
			data = pickle.loads(response)
			#print("Message {} received from {}".format(data.reqType,data.fromClient))
			myQueue.append(data)
			tQueue.append(time.time())
		

class MarkerThread(Thread):
	def __init__(self, markerId):
		Thread.__init__(self)
		self.markerId = markerId

	def run(self):		
		#time.sleep(2.5)
		#sleep()
		markerLock.acquire()
		for i in outgoing:
			message = Messages("MARKER", pid, self.markerId)
			c2c_connections[i].send(pickle.dumps(message))
			print("Sending MARKER for {} to {} at {}".format(self.markerId, i, dt.datetime.now()))
		markerLock.release()
		

def sendMarkers(markerId, fromClient):
	print("Creating a channel tracking object post first receival from {}".format(fromClient))
	trackChannels = TrackChannels(markerId)

	markersInProgress[markerId] = trackChannels
	markersInProgress[markerId].tokenState = token
	
	markerThread = MarkerThread(markerId)
	markerThread.start()

	for i in incoming:
		if i != fromClient:
			markersInProgress[markerId].listenToChannel[i] = True
		else:
			markersInProgress[markerId].recievedMarkers.append(fromClient)



def main():
	ip = '127.0.0.1'
	client_port = 0
	global pid
	global currentBalance

	if sys.argv[1] == "p1":
		client_port = 7001
		pid = 1
	elif sys.argv[1] == "p2":
		client_port = 7002
		pid = 2
	elif sys.argv[1] == "p3":
		client_port = 7003
		pid = 3
	elif sys.argv[1] == "p4":
		client_port = 7004
		pid = 4
	elif sys.argv[1] =="p5":
		client_port = 7005
		pid = 5


	if client_port == 7001: 
		client2client = socket.socket()
		client2client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		client2client.bind((ip, client_port))
		client2client.listen(20)
		print('Waiting for a Connection..')

		i = 2
		while i <= 5:
			connection, client_address = client2client.accept()
			print('Connected to: ' + client_address[0] + ':' + str(client_address[1]))
			new_client = ClientConnections(connection)
			new_client.start()
			c2c_connections[i] = connection
			i+=1
		incoming.append(2)
		incoming.append(4)
		outgoing.append(2)

	if client_port == 7002:
		client2client = socket.socket()
		client2client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		client2client.bind((ip, 7021))
		
		try:
			client2client.connect((ip, 7001))
			print('Connected to: ' + ip + ':' + str(7001))
		except socket.error as e:
			print(str(e))

		c2c_connections[1] = client2client
		new_connection = ClientConnections(client2client)
		new_connection.start()

		client2client = socket.socket()
		client2client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		client2client.bind((ip, client_port))
		client2client.listen(20)


		i = 3
		while i <= 5:
			connection, client_address = client2client.accept()
			print('Connected to: ' + client_address[0] + ':' + str(client_address[1]))
			new_client= ClientConnections(connection)
			new_client.start()
			c2c_connections[i] = connection
			i+=1

		incoming.append(1)
		incoming.append(3)
		incoming.append(4)
		incoming.append(5)

		outgoing.append(1)
		outgoing.append(4)

	if client_port == 7003:

		client2client = socket.socket()
		client2client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		client2client.bind((ip, 7031))
		
		try:
			client2client.connect((ip, 7001))
			print('Connected to: ' + ip + ':' + str(7001))
		except socket.error as e:
			print(str(e))

		c2c_connections[1] = client2client
		new_connection = ClientConnections(client2client)
		new_connection.start()

		client2client = socket.socket()
		client2client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		client2client.bind((ip, 7032))
		
		try:
			client2client.connect((ip, 7002))
			print('Connected to: ' + ip + ':' + str(7002))
		except socket.error as e:
			print(str(e))

		c2c_connections[2] = client2client
		new_connection = ClientConnections(client2client)
		new_connection.start()

		client2client = socket.socket()
		client2client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		client2client.bind((ip, client_port))
		client2client.listen(20)


		i = 4
		while i <= 5:
			connection, client_address = client2client.accept()
			print('Connected to: ' + client_address[0] + ':' + str(client_address[1]))
			new_client= ClientConnections(connection)
			new_client.start()
			c2c_connections[i] = connection
			i+=1

		incoming.append(4)
		outgoing.append(2)

	if client_port == 7004:

		client2client = socket.socket()
		client2client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		client2client.bind((ip, 7041))
		
		try:
			client2client.connect((ip, 7001))
			print('Connected to: ' + ip + ':' + str(7001))
		except socket.error as e:
			print(str(e))

		c2c_connections[1] = client2client
		new_connection = ClientConnections(client2client)
		new_connection.start()

		client2client = socket.socket()
		client2client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		client2client.bind((ip, 7042))
		
		try:
			client2client.connect((ip, 7002))
			print('Connected to: ' + ip + ':' + str(7002))
		except socket.error as e:
			print(str(e))

		c2c_connections[2] = client2client
		new_connection = ClientConnections(client2client)
		new_connection.start()

		client2client = socket.socket()
		client2client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		client2client.bind((ip, 7043))
		
		try:
			client2client.connect((ip, 7003))
			print('Connected to: ' + ip + ':' + str(7003))
		except socket.error as e:
			print(str(e))

		c2c_connections[3] = client2client
		new_connection = ClientConnections(client2client)
		new_connection.start()
		
		client2client = socket.socket()
		client2client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		client2client.bind((ip, client_port))
		client2client.listen(20)

		i = 5
		while i <= 5:
			connection, client_address = client2client.accept()
			print('Connected to: ' + client_address[0] + ':' + str(client_address[1]))
			new_client= ClientConnections(connection)
			new_client.start()
			c2c_connections[i] = connection
			i+=1

		incoming.append(2)
		incoming.append(5)
		outgoing.append(1)
		outgoing.append(2)
		outgoing.append(3)
		outgoing.append(5)

	if client_port == 7005:
			#need to add here.
		client2client = socket.socket()
		client2client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		client2client.bind((ip, 7051))

		for i in range(1,5):
			client2client = socket.socket()
			client2client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			client2client.bind((ip, 7050+i))
			try:
				client2client.connect((ip, 7000+i))
				print('Connected to: ' + ip + ':' + str(7000+i))
			except socket.error as e:
				print(str(e))
			
			c2c_connections[i] = client2client
			new_connection = ClientConnections(client2client)
			new_connection.start()

		incoming.append(4)
		outgoing.append(2)
		outgoing.append(4)


	incoming.sort()
	outgoing.sort()

	print("IncomingChannels:",incoming)
	print("OutgoingChannels:",outgoing)

	masterHandler = MasterHandler()
	masterHandler.start()
	
	while True:
		print("=======================================================")
		print("| For Start token  'TOKEN' 						     |")
		print("| To specify probability/change of Loosing - C probVal Eg.(P 10)")
		print("| For Snapshot type 'SNAP'                            |")
		print("=======================================================")
		user_input = input()
		if user_input == "BAL":
			print("Balance is $" + str(currentBalance))
		elif user_input == "SNAP":
			markerId = incrementMarker()
			print("Initiating snapshot "+ str(markerId))
			markerLock.acquire()
			sendMarkers(markerId, pid)
			markerLock.release()
		elif user_input=="TOKEN":
			TokenLock.acquire()
			token=True
			message=Messages("TOKEN",pid,"")
			#choose a dest
			#ind=random.randint(0, len(outgoing)-1)
			ind=getRandomIndex()
			if(ind==None):
				print("Token is lost")
			else:
				print("random Index",ind)
				receiver=outgoing[ind]
				#print("=====================================================")
				print("Sending token to ", receiver)
				c2c_connections[receiver].send(pickle.dumps(message))
				#print("=====================================================")
			TokenLock.release()
		elif len(user_input.split()) == 2:
			global toggle
			global prob
			toggle,prob = user_input.split()
			prob=int(prob)
			print("Probability of Losing updated to ",prob)
		else:
			print("INVALID INPUT")
			continue

if __name__ == "__main__":
    main()

