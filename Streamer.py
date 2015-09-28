#!/usr/bin/python

import select
import socket
import Plotter as PT
import time
import json


SERVER_IP = '86.36.34.202'
SERVER_PORT = 5996
PLOTLY_USERNAME = 'stariq'
PLOTLY_KEY = '7wakatl28e'
REGISTRY = 'registry.txt'

# #####
# @name:	convert_types(input)

# @description:	takes the type of device and returns the numeral corresponding
# 				to it

# @inputs:	input:	The type if device

# @return_val:	Number corresponding to type, -1 if type not recognized

# #####
def convert_types(input):
	if 'Desktop/Laptop' in input:
		return '0'
	if 'Smartphone/Tablet' == input:
		return '1'
	if 'Embedded/Other' in input:
		return '2'
	return '-1'

# ############################################################################
# 	Class: User

#  	@object variables:

# 		self.server: Stream server that this user is connected to
# 		self.conn_fd: Socket object of this user
# 		self.BUF_SIZE: Maximum size to read in one try
# 		self.read_buffer: Sliding read buffer
# 		self.addr: IP of the user
# 		self.plot: The plot that this user has created


 	#####
 # 	Methods:

	# #####
	# @name:	__init__(self, connfd, conn_addr, parent)

	# @description: Creates the new Collect_User object

	# @inputs: 	connfd: socket object associated with the user
	# 			conn_addr: IP address of the user
	# 			parent: The server this user is connected to

	# @return_val: Collect_User object

	# #####
	# @name:	confirm(self)

	# @description:	Sends a message back to the user, confirming that it is
	# 				connected
	# @inputs:	None

	# @return_val:	None

	# #####
	# @name:	read(self)

	# @description:	recieves data from the user and appends it to the sliding
	# 				buffer

	# @inputs:	None

	# @return_val:	0, if there was data and read was successfull, -1 otherwise

	# #####
	# @name:	get(self)

	# @description:	gets the next valid instruction from the sliding buffer

	# @inputs:	None

	# @return_val:	String containing the next instruction

	# #####
	# @name:	parse(self, line)

	# @description:	Coverts the json string object to a python dict object

	# @inputs:	Json string object

	# @return_val:	python dict if valid json object, otherwise None

	# #####
	# @name:	update_stat(self)

	# @description:	Sends statistical info to the user

	# @inputs:	None

	# @return_val:	None

	# #####
	# @name:	do_cmd(self, command)

	# @description:	performs the command given by the user

	# @inputs:	command: python dictionary containing the command info

	# @return_val:	0 if command performed successfully, -1 otherwise

	# #####
	# @name:	start_plot(self, node_ids, metrics, maxpoints)

	# @description:	creates a new plot object and begins streaming to it

	# @inputs:	node_ids:	The ids of the nodes meant to be plotted
	# 			metrics:	The metrics for each node to plot
	# 			maxpoints:	The maximum points for each stream to show in the
	# 						plot at any single moment. Default is 50

	# @return_val:	None

	# #####
	# @name:	get_node_ids(self, filter_list)

	# @description:	gets the node_ids if the types of devices given in the
	# 				filter list

	# @inputs:	filter_list:	The types of nodes to be added

	# @return_val:	list containing node_ids

	# #####
	# @name:	stop_plot(self)

	# @description:	stops the plot streaming

	# @inputs:	None

	# @return_val:	None

	# #####
	# @name:	close_plots(self)

	# @description:	closes the plot streams

	# @inputs:	None

	# @return_val:	None

	# #####
	# @name:	add_plot(self, new_plot)

	# @description:	assigns a new plot object to the user

	# @inputs:	new_plot: The new plot object to be assigned

	# @return_val:	None

	# #########################################################################
	# @name:	

	# @description:	

	# @inputs:	

	# @return_val:	

	#####


class User(object):

	def __init__(self, conn_fd, conn_addr, parent):
		self.server = parent
		self.conn_fd = conn_fd
		self.BUF_SIZE = 1024
		self.read_buffer = ''
		self.addr = conn_addr
		self.plot = None
		self.confirm()

	def confirm(self):
		self.conn_fd.send('WE HAVE CONNECTED\END')

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

	def parse(self, line):
		try:
			command = json.loads(line)
			return command
		except:
			return None

	def update_stat(self):
		try:
			self.conn_fd.send('STATS:%s\END' % (json.dumps(self.server.total_stats)))
		except:
			pass

	def do_cmd(self, command):
		cmd = command['cmd']
		print "COMMAND "+ cmd
		if cmd not in ['startnew', 'pause', 'resume', 'gotoend', 'goto', 'stop']:
			print "ERROR: Invalid Command"
			return -1
		if cmd == 'goto':
			assert(self.plot != None)
			self.conn_fd.send('OK JUMPING\END')
			line = command['time']
			print "Line to jump_to: " +  line
			# exit()
			self.plot.plot_jump(line)
			return 0
		if cmd == 'startnew':
			assert(self.plot == None)
			self.conn_fd.send('OK STARTING\END')
			start_time = command['time']
			maxpoints = command['maxpoints']
			node_filter = command['node_classes']
			metrics = command['metrics']

			print start_time, maxpoints, node_filter, metrics
			node_ids = self.get_node_ids(node_filter)
			print 'Node IDS:', node_ids

			self.start_plot(node_ids, metrics, maxpoints)
			if start_time != None:
				self.plot.plot_jump(start_time)
			url = self.plot.get_url()
			self.conn_fd.send('URL:'+url+'\END')
			return 0
		if cmd == 'stop':
			assert(self.plot != None)
			self.conn_fd.send('OK STOPPING')
			self.plot.close_stream()
			self.plot = None
			return 0
		if cmd == 'pause':
			assert(self.plot != None)
			self.conn_fd.send('OK PAUSING')
			self.plot.stream_stop()
			return 0
		if cmd == 'resume':
			assert(self.plot != None)
			self.conn_fd.send('OK RESUMING')
			self.plot.stream_start()
			return 0
		if cmd == 'gotoend':
			assert(self.plot != None)
			self.plot.plot_jumptoend()
			self.conn_fd.send('OK GOING TO END')
			return 0
		

	def start_plot(self, node_ids, metrics, maxpoints = 50):
		# print self.plotter.new_plot_stream(src_file, maxpoints)
		# print type(self.addr)
		if (len(node_ids) == 0):
			print "Not enough devices"
			return

		if (len(metrics) == 0):
			print "Not enough metrics"
			return
			
		plot = self.server.plotter.new_plot_stream('%s\'s plot' % (self.addr[0]), node_ids, metrics, self.conn_fd, maxpoints)
		if (plot == None):
			print "Plot could not be created"
			return
		# plot = self.server.plotter.new_plot_stream('Checking', [0], ['CPU', 'MEMORY'], client_fd = 1, maxpoints = 20)
		plot.initialize()
		plot.set_owner((self.addr, self.conn_fd))
		# time.sleep(5)
		plot.init_streams()
		plot.stream_start()
		self.plot = plot

	def get_node_ids(self, filter_list):
		filter_list = [convert_types(i) for i in filter_list]
		# print filter_list
		devices = self.server.reg_file.readlines()
		self.server.reg_file.seek(0, 0)
		node_ids = []
		for device in devices:
			dev_info = json.loads(device)
			# print 'platform = ', str(dev_info['platform'])
			if str(dev_info['platform']) in filter_list:
				node_ids.append(int(dev_info['id']))
		# print node_ids
		# exit()
		return node_ids

	def stop_plot(self):
		if self.plot != None:
			self.plot.stream_stop()

	def close_plots(self):
		if self.plot != None:
			self.plot.close_stream()

	def add_plot(self, new_plot):
		assert(self.plot == None)
		self.plot = new_plot

	# ##########################################################################
	# Class:	Server

	# @object variables:

	# 	self.host:	Address for the server listen socket to bind to
	# 	self.port:	Port for the server listen socket to bind to
	# 	self.listen_sock:	The listen socket object of the server
	# 	self.plotter:	The plotter object for the server
	# 	self.users:	The dictionary containing all the users with client_fd as 
	# 				keys
	# 	self.inputs:	The pool for the select loop to monitor
	# 	self.reg_file:	The path to the registry file containing info for the
	# 					devices
	# 	self.total_stats:	dictionary containing the stats to send to the users
	# 	self.RUNNING:	Boolean variable telling whether the server is running

	# #####
	# @name:	__init__(self, host, port, username, key, reg_file)

	# @description:	Creates a new instance of a Server object

	# @inputs:	host:	Address for the listen socket to bind to
	# 			port:	Port for the listen socket to bind to
	# 			username:	Username to create a new plotter object
	# 			key:	key to create a new plotter object
	# 			reg_file:	The path to the registry file to get device info
	# 						from

	# @return_val:	A Server object

	# #####
	# @name:	listen(self, backlog)

	# @description:	Creates and binds a listen socket and starts listening

	# @inputs:	backlog:	The number of connections to keep in queue

	# @return_val:	None

	# #####
	# @name:	add_client(self, client_fd, client_addr)

	# @description:	Create and add a new client to the pool

	# @inputs:	client_fd:	The socket object associated with the client
	# 			client_addr:	The address of the client

	# @return_val:	None

	# #####
	# @name:	remove_client(self, client_fd)

	# @description:	Removes and closes the connection to the client with
	# 				address client_fd

	# @inputs:	client_fd:	The socket object associated with the client

	# @return_val:	None

	# #####
	# @name:	handle_input(self, client_fd)

	# @description:	if there is input from this client, handles it, otherwise
	# 				closes the connection

	# @inputs:	client_fd:	The socket object associated with the client

	# @return_val:	0 if there was input, -1 otherwise

	# #####
	# @name:	check_inputs(self, active)

	# @description:	Goes throught the active sockets and checks if they have
	# 				input, and handles them, closes them otherwise

	# @inputs:	active:	list of active sockets

	# @return_val:	None

	# #####
	# @name:	send_stat_updates(self)

	# @description:	Sends statistical updates to all the connected clients

	# @inputs:	None

	# @return_val:	None

	# #####
	# @name:	shutdown(self)

	# @description:	Shuts down the Server safely

	# @inputs:	None

	# @return_val:	None

	# #####
	# @name:	run(self)

	# @description:	Starts listening on the listen socket

	# @inputs:	None

	# @return_val:	None

	# #####
	# @name:	get_plot_from_url(self, url)

	# @description:	returns the plot object with the given url

	# @inputs:	url:	The url of the plot to be retrieved

	# @return_val:	plot object if the url exists, -1 otherwise

	# ##########################################################################
class Server(object):
	def __init__(self, host, port, username, key, reg_file):
		self.host = host
		self.port = port
		self.listen_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.plotter = PT.Plotter(username, key)
		self.users = {}
		self.inputs = [self.listen_sock]
		self.reg_file = open(reg_file)
		self.total_stats = {'Laptop/Desktop Nodes' : 0, 'Smartphone/Tablet Nodes' : 0, 'Embedded/Other Nodes' : 0}
		self.RUNNING = False

	def listen(self, backlog):
		self.plotter.initialize()
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
		self.users[client_fd] = User(client_fd, client_addr, self)

	def remove_client(self, client_fd):
		## DEBUG ##
		if client_fd not in self.inputs:
			print "ERROR: adding duplicate clients!!"
			self.RUNNING = False

		if client_fd not in self.users:
			print "ERROR: adding duplicate user!!"
			self.RUNNING = False
		## DEBUG ##

		self.inputs.remove(client_fd)
		user = self.users.pop(client_fd, -1)
		if user != -1:
			user.close_plots()
		try:
			client_fd.close()
			print "INFO: Connection closed"
		except:
			print "Error: Could not close properly"

	def handle_input(self, client_fd):
		user = self.users[client_fd]
		if user.read():
			return -1
		data = user.get()
		if data == '':
			return -1
		command = user.parse(data)
		user.do_cmd(command)

		print data
		# client_fd.send('REPLY: ' + data)
		return 0

	def check_inputs(self, active):
		for sock in active:
			if sock is self.listen_sock:
				(client_fd, client_addr) = self.listen_sock.accept()
				self.add_client(client_fd, client_addr)
			else:
				if self.handle_input(sock):
					self.remove_client(sock)

	def send_stat_updates(self):
		reg_file_lines = self.reg_file.readlines()
		self.reg_file.seek(0, 0)
		self.total_stats = {'Laptop/Desktop Nodes' : 0, 'Smartphone/Tablet Nodes' : 0, 'Embedded/Other Nodes' : 0}
		for line in reg_file_lines:
			line = json.loads(line)
			if str(line.get('platform', '')) == '0':
				self.total_stats['Laptop/Desktop Nodes'] += 1
			if str(line.get('platform', '')) == '1':
				self.total_stats['Smartphone/Tablet Nodes'] += 1
			if str(line.get('platform', '')) == '2':
				self.total_stats['Embedded/Other Nodes'] += 1
		# print self.total_stats
		[user.update_stat() for user in self.users.values()]

	def shutdown(self):
		for sock in self.inputs:
			self.remove_client(sock)
		self.listen_sock.close()
		exit()

	def run(self):
		print "INFO: Listening..."
		self.listen(5)
		self.RUNNING = True
		while self.RUNNING:
			active, b, c = select.select(self.inputs, [], [], 5)
			self.check_inputs(active)
			self.send_stat_updates()
		self.shutdown()

	def get_plot_from_url(self, url):
		for user in self.users.values():
			for plot in user.plots.values():
				print "INFO: Comaring %s == %s" % (plot.get_url(), url)
				if plot.get_url() == url:
					return plot
		print "ERROR: Requested plot not found"
		return -1

if __name__ == "__main__":
	# f = os.popen('hostname -i')
	# HOST_IP = f.read().strip()
	# f.close()
	server = Server(SERVER_IP, SERVER_PORT, PLOTLY_USERNAME, PLOTLY_KEY, REGISTRY)
	server.run()