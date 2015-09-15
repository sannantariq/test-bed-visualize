import socket

class Client(object):
	def __init__(self, server_address):
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.server_addr = server_address
		self.BUF_SIZE = 1024
		self.read_buffer = ''

	def connect(self):
		self.socket.connect(self.server_addr)
		self.socket.setblocking(0)

	def read(self):
		try:
			data = self.socket.recv(self.BUF_SIZE)
			# print 'data = ', 
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

	def send_command(self, cmd):
		try:
			self.socket.send(cmd + '\END')
			return 0
		except:
			print "ERROR: Unable to send from client"
			return -1

	def listen(self):
		self.read()
		# print 'read_buffer:', self.read_buffer
		data = self.get()
		# print 'data = ', data
		return data

	def close(self):
		self.socket.close()