#!/usr/bin/python

import select
import socket
import datetime
import thread
import time
import json
import os.path
import signal
import sys

# ############################################################################
# 	Class: Collect_User

# 	@object variables:

# 		self.conn_fd:	socket object of the connection
# 		self.BUF_SIZE:	buffer size, maximum that can be read in a single read
# 		self.read_buffer:	sliding buffer containing data sent by the user
# 		self.addr:	IP Address of the user
# 		self.info:	dictionary containing the info of the user
# 		self.initialized:	boolean var signifying if the client has been
# 							initialized
# 		self.readings:	dictionary containing the readings sent by the user with
# 						the metrics as the keys
# 		self.reg_file:	registry file provided by the server
# 		self.server:	server object this user is connected to
# 		self.metrics:	list of metrics that the user is sending updates for

# 	#####
# 	Methods:

# 	Note: 	client/user/device are used interchangeably and all refer to the
# 			entity that will be sending updates to this server

# 	#####
# 	@name:	__init__(self, connfd, conn_addr, server)

# 	@description: Creates the new Collect_User object

# 	@inputs: 	connfd: socket object associated with the user
# 				conn_addr: IP address of the user
# 				server: Collect_Server object that this user is connected to

# 	@return_val: Collect_User object

# 	#####
# 	@name: read(self):

# 	@description:  Populates the self.read_buffer of the object

# 	@return_val: 0 if the read was successful, -1 otherwise

# 	######
# 	@name: get(self)

# 	@description: Returns json string message sent by the device

# 	@return_val: json string containing the next message from the device

# 	#####

# 	@name: initialize(self, msg_dict)

# 	@description: 	initializes the client, adds it to the registry if required
# 					and prepares to receive updates from the device

# 	@inputs:	msg_dict: Last update sent by the client

# 	#####

# 	@name: get_val(self, metric)

# 	@description: 	get the value associated with key = metric in the
# 					self.readings dictionary

# 	@inputs: metric: the key for which you want to retrieve the value

# 	@return_val: 	empty string if metric does not exist, value of the metric
# 					otherwise

# 	#####

# 	@name: set_val(self, metric, val)

# 	@description: 	set the value associated with key = metric in the
# 					self.readings dictionary

# 	@inputs: 	metric: the key for which you want to set the value
# 				val: the value you want to set the metric at

# 	#####

# 	@name: get_val(self, metric)

# 	@description: 	get the value associated with key = metric in the
# 					self.readings dictionary

# 	@inputs: metric: the key for which you want to retrieve the value

# 	@return_val: 	empty string if metric does not exist, value of the metric
# 					otherwise

# 	#####

# 	@name: parse(self, line)

# 	@description: 	update the self.readings dictionary with the reported 
# 					readings

# 	@inputs: 	line: 	json object containing the update dictionary sent by the
# 						device

# 	##########################################################################

class Collect_User(object):
	def __init__(self, conn_fd, conn_addr, server):
		self.conn_fd = conn_fd
		self.BUF_SIZE = 1024
		self.read_buffer = ''
		self.addr = conn_addr
		self.info = {'os' : '', 'mem' : '', 'cpu' : '', 'cores' : '', 'platform' : '', 'name' : ''}
		self.initialized = False
		self.readings = {}
		self.reg_file = server.reg_file
		self.server = server

	def read(self):
		try:
			data = self.conn_fd.recv(self.BUF_SIZE)
		except:
			return -1
		if data:
			self.read_buffer += data
			return 0
		else:
			return -1

	def get(self):
		split = self.read_buffer.find('\END')
		if split == -1:
			return ''
		line = self.read_buffer[:split]
		self.read_buffer = self.read_buffer[split+4:]
		return line

	def initialize(self, msg_dict):
		print 'INFO: Initializing client'
		if msg_dict.get('cmd') != 'connect':
			print 'ERROR: First message from device was not connect'
			return
		name = msg_dict.get('name', '')
		if not name:
			print 'ERROR: Did not get name from device'
			return
		found = False
		self.reg_file.seek(0, 0)
		lines = self.reg_file.readlines()
		print 'INFO: Searching...'
		for line in lines:
			line = json.loads(line)
			new_name = line.get('name')
			# print 'Comapring', name, new_name
			if new_name == name:
				self.info = line
				found = True
				print 'INFO: Found in the registry'
				break
		if not found:
			self.info['os'] = msg_dict.get('os', 'NA')
			self.info['mem'] = msg_dict.get('mem', 'NA')
			self.info['cpu'] = msg_dict.get('cpu', 'NA')
			self.info['cores'] = msg_dict.get('cores', 'NA')
			self.info['name'] = msg_dict.get('name', 'NA')
			self.info['platform'] = msg_dict.get('platform', 'NA')
			self.info['id'] = self.server.nxt_id
			self.server.nxt_id += 1
			print "Info: self.info: ", self.info
			towrite = json.dumps(self.info)
			print 'Info: About to write:', towrite
			self.reg_file.write(towrite + '\n')
			curr = self.reg_file.tell()
			self.reg_file.seek(0, 0)
			self.reg_file.seek(curr, 0)

		metrics = msg_dict.get('metrics', '')
		if metrics:
			print 'Metrics to monitor:', metrics, 'with type:', type(metrics)
			if isinstance(metrics, str):
				metrics = json.loads(metrics)
			self.metrics = metrics
		else:
			print 'INFO: Did not get any metrics from device'
			self.metrics = []
		self.initialized = True
		self.server.initialized_clients += 1
		print 'INFO: Client Initialized'
		return

	def get_val(self, metric):
		return self.readings.get(metric, '')

	def set_val(self, metric, val):
		if self.readings.has_key(metric):
			self.readings[metric] = val

	def parse(self, line):
		if line == '':
			return
		else:
			# print 'Info: line:', line
			try:
				msg_dict = json.loads(line)
			except:
				print 'ERROR: Did not get Json object from device. Ignoring...'
				return
			if msg_dict.get('cmd', -1) == -1:
				print 'ERROR: Did not get cmd key from device'
				return
			if not self.initialized:
				self.initialize(msg_dict)
			if self.initialized:
				cmd = msg_dict.get('cmd')
				if cmd == 'update':
					readings = msg_dict.get('info', -1)
					if readings == -1:
						return
					else:
						for metric in self.metrics:
							self.readings[metric] = readings.get(metric, 'nan')


# ############################################################################
# 	Class: Collect_User

# 	@object variables:

# 		self.host:	IP address for listening socket to bind to
# 		self.port:	Port for listening socket to bind to
# 		self.listen_sock:	listening socekt object
# 		self.users:	dictioary containing users with there socket objects as keys
# 		self.inputs:	sockets for select to monitor
# 		self.RUNNING:	server running var
# 		self.WRITING:	server writing for a matrix in a file var
# 		self.polling_interval:	interval to poll and write at
# 		self.files:	dictionary with metric as key and file as the value
# 		self.metrics:	list of metrics to check for
# 		self.reg_filename:	name of registry file
# 		self.nxt_id:	next id to assign to a new device
# 		self.initialized_clients:	number of initialized clients

# 	#####
# 	Methods:

# 	Note: 	client/user/device are used interchangeably and all refer to the
# 			entity that will be sending updates to this server

# 	#####
# 	@name:	__init__(self, host, port, polling_interval, metrics, reg_filename)

# 	@description: Creates the new Collect_Server object

# 	@inputs: 	host:	IP for listening socket
# 				port:	port for listening socket
# 				polling_interval:	interval to poll and write (seconds)
# 				metrics:	list of metrics to check for
# 				reg_filename: name of registry file

# 	@return_val: Collect_Server object

# 	#####
# 	@name:	initialize(self)

# 	@description: creates the required files and installs handlers

# 	#####
# 	@name:	listen(self, backlog)

# 	@description: Creates a listening socket with backlog = backlog and listens

# 	@inputs: 	backlog: number of clients to keep in queue

# 	#####
# 	@name:	add_client(self, client_fd, client_addr)

# 	@description: adds new client to the servers pool

# 	@inputs: 	client_fd:	socket object associated with the client
# 				client_addr:	IP address of the client

# 	#####
# 	@name:	remove_client(self, client_fd)

# 	@description: removes client from the servers pool

# 	@inputs: 	client_fd: 	socket object associated with the client to be
# 							removed

# 	#####
# 	@name:	poll_n_write(self)

# 	@description: 	records the latest values present in each clients readings
# 					dictionary with the associated ID in files for each metric

# 	#####
# 	@name:	start_writing(self)

# 	@description: sets self.WRITING to true and calls poll_n_write in a thread

# 	#####
# 	@name:	stop_writing(self)

# 	@description: sets self.WRITING to false, stopping poll_n_write thread

# 	#####
# 	@name:	handle_input(self, client_fd)

# 	@description: reads and parses the updates sent by a user

# 	@inputs: 	client_fd:	socket object associated with the client
	
# 	@return_val:	-1 if unsuccessful, 0 otherwise

# 	#####
# 	@name:	check_inputs(self, active)

# 	@description: check if a socket was active

# 	@inputs: 	active: list containing all active sockets

# 	#####
# 	@name:	shutdown(self)

# 	@description: safely shutdown the server

# 	#####
# 	@name:	handler(self, signum, frame)

# 	@description:	handler for the SIGINT signal

# 	#####
# 	@name:	run(self)

# 	@description:	run the server

# 	##########################################################################				

class Collect_Server(object):
	def __init__(self, host, port, polling_interval, metrics, reg_filename):
		self.host = host
		self.port = port
		self.listen_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.users = {}
		self.inputs = [self.listen_sock]
		self.RUNNING = False
		self.WRITING = False
		self.polling_interval = polling_interval
		self.files = {}
		self.metrics = metrics
		self.reg_filename = reg_filename
		self.nxt_id = 0
		self.initialized_clients = 0
		self.initialize()

	def initialize(self):
		if not os.path.exists('LastID.txt'):
			self.nxt_id = 0
		else:
			f = open('LastID.txt')
			self.nxt_id = int(f.read())
			f.close()

		for metric in self.metrics:
			if not os.path.exists('%s-metric.txt' % metric):
				print 'creating file'
				f = open('%s-metric.txt' % (metric), 'w')
				f.close()
			f = open('%s-metric.txt' % (metric), 'a+')
			self.files[metric] = f

		if not os.path.exists(self.reg_filename):
			print 'Creating new reg File..'
			self.reg_file = open(self.reg_filename, 'w')
			self.reg_file.close()

		self.reg_file = open(self.reg_filename, 'a+')

		print 'INFO: Installing signal'
		signal.signal(signal.SIGINT, self.handler)

	def listen(self, backlog):
		self.listen_sock.bind((self.host, self.port))
		self.listen_sock.setblocking(0)
		self.listen_sock.listen(backlog)

	def add_client(self, client_fd, client_addr):

		## DEBUG ##
		if client_fd in self.inputs:
			print "ERROR: adding duplicate clients!!"
			self.RUNNING = False

		if client_fd in self.users:
			print "ERROR: adding duplicate user!!"
			self.RUNNING = False
		## DEBUG ##
		print "INFO: Adding client", client_addr
		self.inputs.append(client_fd)
		self.users[client_fd] = Collect_User(client_fd, client_addr, self)

	def remove_client(self, client_fd):
		## DEBUG ##
		if client_fd not in self.inputs:
			print "ERROR: removing non-existant clients!!"
			self.RUNNING = False

		if client_fd not in self.users:
			print "ERROR: removing non-existant user!!"
			self.RUNNING = False
		## DEBUG ##

		self.inputs.remove(client_fd)
		user = self.users.pop(client_fd, -1)

		if user.initialized:
			self.initialized_clients -=1
		try:
			client_fd.close()
			print "INFO: Connection closed"
		except:
			print "Error: Could not close properly"
		# client_fd.close()

	def poll_n_write(self):
		print "Started WRITING"
		while self.WRITING:
			write_string = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
			for metric in self.metrics:
				f = self.files[metric]
				f.write(write_string)
				users = [user for user in self.users.values() if user.initialized == True]
				for user in users:
					user_id = user.info['id']
					metric_val = user.get_val(metric)
					if metric_val:
						f.write(' %.4d:%.4s' % (user_id, metric_val))
						user.set_val(metric, 'nan')
				f.write('\n')
				curr = f.tell()
				f.seek(0, 0)
				f.seek(curr, 0)
			time.sleep(self.polling_interval)
		print "Stopped WRITING"

	def start_writing(self):
		self.WRITING = True
		thread.start_new_thread(self.poll_n_write, ())

	def stop_writing(self):
		self.WRITING = False

	def handle_input(self, client_fd):
		user = self.users[client_fd]
		if user.read():
			return -1
		data = user.get()
		user.parse(data)

		# print data
		return 0

	def check_inputs(self, active):
		for sock in active:
			if sock is self.listen_sock:
				(client_fd, client_addr) = self.listen_sock.accept()
				self.add_client(client_fd, client_addr)
			else:
				if self.handle_input(sock):
					self.remove_client(sock)

	def shutdown(self):
		print 'SHUTTING DOWN'
		self.WRITING = False
		for sock in self.inputs:
			if sock is not self.listen_sock:
				self.remove_client(sock)
		self.listen_sock.close()
		# self.file.close()
		f = open('LastID.txt', 'w')
		f.write('%4d' % (self.nxt_id))
		f.close()
		self.reg_file.close()
		for val in self.files.values():
			val.close()
		exit()

	def handler(self, signum, frame):
		print 'Got Signal. Handling...'
		# self.RUNNING = False
		self.shutdown()

	def run(self):
		print "INFO: Listening..."
		self.listen(5)
		self.RUNNING = True
		while self.RUNNING:
			if (self.initialized_clients) >= 1 and self.WRITING == False:
				self.start_writing()
			elif self.initialized_clients == 0:
				self.stop_writing()
			active, b, c = select.select(self.inputs, [], [])
			self.check_inputs(active)

		self.shutdown()


if __name__ == "__main__":
	
	server = Collect_Server('192.168.1.117', 4000, 1, ['CPU', 'MEMORY'], 'registry.txt')
	# if len(sys.argv) != 5:
	# 	print 'Usage: ./Collect_Server [port] [polling interval] [metric1, metric2...] [path to registry file]'
	# 	exit()
	# server = Collect_Server('localhost', sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
	server.run()
