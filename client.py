import sys
import socket
import pickle
import time
import threading
from threading import Thread
from common import *

buff_size = 1024
pid = 0

c2c_connections = {}
outgoing = []
incoming = []


class ClientConnections(Thread):
	def __init__(self,connection):
		Thread.__init__(self)
		self.connection = connection

	def run(self):
		while(True):
			pass
		'''
		while True:
			response = self.connection.recv(buff_size)
			data = pickle.loads(response)
			myQueueLock.acquire()
			myQueue.append(data)
			myQueueLock.release()
		'''



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
		client2client.listen(5)
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
		client2client.listen(5)


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
		client2client.listen(2)


		i = 4
		while i <= 4:
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
		

		i = 5
		while i <= 5:
			connection, client_address = client2client.accept()
			print('Connected to: ' + client_address[0] + ':' + str(client_address[1]))
			new_client= ClientConnections(connection)
			new_client.start()
			c2c_connections[i] = connection
			i+=1

		incoming.append(2)
		outgoing.append(5)
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

	#masterHandler = MasterHandler()
	#masterHandler.start()
	
	while True:
		print("=======================================================")
		print("| For Balance type 'BAL'                              |")
		print("| For Start token  'T' 								 |")
		print("| For Snapshot type 'SNAP'                            |")
		print("=======================================================")
		user_input = input()
		if user_input == "BAL":
			print("Balance is $" + str(currentBalance))
		elif user_input == "SNAP":
			markerId = incrementMarker()
			print("Initiating snapshot "+ str(markerId))
			sendMarkers(markerId, pid)
		elif user_input=="T":
			'''
			reciever, amount = user_input.split()
			if int(reciever) in outgoing:
				if int(amount) > currentBalance:
					print("Insufficient Balance")
				else:
					balanceLock.acquire()
					currentBalance -= int(amount)
					balanceLock.release()
					message = Messages("TRANSACTION", pid, "", amount)
					sleep()
					print("=====================================================")
					print("Sending $"+str(amount)+" to "+str(reciever))
					c2c_connections[int(reciever)].send(pickle.dumps(message))
					print("Updated balance is $" + str(currentBalance))
					print("=====================================================")
			else:
				print("Client " + str(reciever) + " is not connected")
			'''
		else:
			print("INVALID INPUT")
			continue

if __name__ == "__main__":
    main()

