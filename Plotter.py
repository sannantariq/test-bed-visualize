import plotly.plotly as py
import plotly.tools as tls
from plotly.graph_objs import *
import numpy as np
import thread
import File_Reader as FR
import time

# #####

# @name:	generate_layout(data_list)

# @description:	Creates a dictionary conataining the layout options for the plot

# @inputs:	data_list:	list conataining the x and y coordiantes to place each
# 						plot

# @return_val:	dictionary conataining the layout

# #####
def generate_layout(data_list):
	(xlist, ylist) = data_list
	i = 1
	fd = {}
	dom_list = [(x, y) for y in ylist for x in xlist]
	for (x, y) in dom_list:
		if i == 1:
			number = ''
		else:
			number = str(i)
		xkey = 'xaxis'+number
		ykey = 'yaxis'+number
		anchorx = 'y' + number
		anchory = 'x' + number
		fd[xkey] = {'domain' : x, 'anchor' : anchorx}
		fd[ykey] = {'domain' : y, 'anchor' : anchory}
		i += 1
	# print fd
	# exit()
	return fd

# #####

# @name:	gen_closest_square(plots)

# @description:	returns the closes square dimensions for the given number

# @inputs:	plots:	The number of plots that need to be shown

# @return_val:	tuple conataining the closes square dimensions

# #####
def gen_closest_square(plots):
	root = plots ** 0.5
	if root == int(root):
		xlen = int(root)
		ylen = int(root)
	else:
		root = int(root)
		while plots % root != 0:
			root -= 1
		xlen = root
		ylen = plots / root
		print xlen, ylen
	return (float(xlen), float(ylen))

# #####

# @name:	get_linspace(num)

# @description:	creates a list of num values with equal distance between them

# @inputs:	num:	The number of values needed

# @return_val:	list of tuples with start and end values for each plot position

# #####
def get_linspace(num):
	inv = np.linspace(0, 1, num + 1)
	in1 = inv[:len(inv)]
	in2 = inv[1:]
	in2 = [w - 0.1 for w in in2]
	return zip(in1, in2)

# #####

# @name:	gen_domains

# @description:	generates the domains to be used for the layouts of the plot

# @inputs:	plots:	The number of plots that need to be shown

# @return_val:	tuple conataining the domain list for the plot

# #####
def gen_domains(plots):
	(x, y) = gen_closest_square(plots)
	inv_x = get_linspace(x)
	inv_y = get_linspace(y)
	return (inv_x, inv_y)

# #####

# @name:	get_tokens_from_plots(plot_list)

# @description:	gets the list of tokens used by the plots given by plot_list

# @inputs:	plot_list:	The list of plots to get the tokens from

# @return_val:	list conataining all the used tokens

# #####
def get_tokens_from_plots(plot_list):
	return [token for plot in plot_list for token in plot.get_tokens()]


#############################################################################

# Class:	Plot

# @object variables:
class Plot(object):
	def __init__(self, title, node_ids, params, client_fd, tokens, maxpoints = 50):
		self.ids = node_ids
		self.client_fd = client_fd
		self.nodes = len(node_ids)
		self.params = params
		self.tokens = tokens
		self.title = title
		self.maxpoints = maxpoints
		self.stream_dict = {}
		self.owner = client_fd
		self.files = {k : FR.FileReader('%s-metric.txt' % (k)) for k in params}

	def get_tokens(self):
		return self.tokens

	def create_layout(self):
		layout = generate_layout(gen_domains(self.nodes))
		layout['title'] = self.title
		layout['showlegend'] = True
		return layout

	def create_traces(self):
		print self.maxpoints
		trace_dict = {}
		numlist = ['' if w == 1 else str(w) for w in range(1, self.nodes + 1)]
		axis_list = [('x'+w, 'y'+w) for w in numlist]
		# for name in range(self.nodes):
		for name in self.ids:
			trace_dict[name] = {}
		for (key, (xa, ya)) in zip(trace_dict.keys(), axis_list):
			for metric in self.params:
				token = self.tokens.pop()
				trace_dict[key][metric] = (Scatter(x = [], y = [], name = 'Node %d - %s' % (key, metric), xaxis = xa, yaxis = ya, stream = Stream(token = token, maxpoints = self.maxpoints), connectgaps = True), token)
		assert(len(self.tokens) == 0)
		return trace_dict

	def get_trace_list(self):
		trace_list = []
		temp = [self.trace_dict[key].values() for key in self.trace_dict.keys()]
		[trace_list.append(val) for values in temp for (val, token) in values]
		return trace_list

	def get_stream_dict(self):
		stream_dict = {}
		for k in self.trace_dict.keys():
			stream_dict[k] = {}
			for m in self.params:
				(_, t) = self.trace_dict[k][m]
				stream_dict[k][m] = py.Stream(t)

		return stream_dict

	def isOwned(self):
		return self.owner == self.client_fd

	def initialize(self):
		
		self.trace_dict  = self.create_traces()
		self.trace_list = self.get_trace_list()
		
		data = Data(self.trace_list)
		self.stream_dict = self.get_stream_dict()
		# print self.stream_dict.values()
		fig = Figure(data = data, layout = self.create_layout())
		self.url = py.plot(fig, filename = 'User View', auto_open = False)
		# self.url = py.plot(fig, filename = 'User View')

	def init_streams(self):
		for node_id in self.stream_dict.keys():
			for metric in self.stream_dict[node_id].keys():
				self.stream_dict[node_id][metric].open()

	def stream_run(self):
		while self.STREAM:
			self.plot_next()
			time.sleep(0.1)
		# print "I have been stopped"

	def stream_start(self):
		self.STREAM = True
		# print "Starting Thread..."
		thread.start_new_thread(self.stream_run, ())

	def stream_stop(self):
		# print "Stopping Thread..."
		self.STREAM = False

	def plot_next(self):
		for metric in self.params:
			file_obj = self.files[metric]
			data = file_obj.read_data()
			# print 'stream dictionary:', self.stream_dict
			# print metric
			# print self.ids
			if data[0] != '':
				[x, ys] = data
				# print 'data', data
				# print 'ys:', ys
				for node in self.ids:
					y = ys.get(node, '')
					# print node, y
					self.stream_dict[node][metric].write(dict(x = x, y = y))
		# time.sleep(0.5)

	def plot_jump(self, time_string):
		for f in self.files.values():
			f.find(time_string)
		for metric in self.params:
			file_obj = self.files[metric]
			prev_data = file_obj.get_previous_n(self.maxpoints)
			for node in self.ids:
				data_list = [(x, ys.get(node, '')) for (x, ys) in prev_data]
				(xlist, ylist) = zip(*data_list)
				self.stream_dict[node][metric].write(dict(x = xlist, y = ylist))

	def plot_jumptoend(self):
		for metric in self.params:
			file_obj = self.files[metric]
			file_obj.seek_end()
			prev_data = file_obj.get_previous_n(self.maxpoints)
			print prev_data
			for node in self.ids:
				data_list = [(x, ys.get(node, '')) for (x, ys) in prev_data]
				(xlist, ylist) = zip(*data_list)
				self.stream_dict[node][metric].write(dict(x = xlist, y = ylist))

	def close_stream(self):
		self.stream_stop()
		[files.close() for files in self.files.values()]
		for node_id in self.stream_dict.keys():
			for metric in self.stream_dict[node_id].keys():
				self.stream_dict[node_id][metric].close()

	def get_url(self):
		return self.url

	def set_owner(self, owner):
		self.owner = owner


class Plotter(object):
	def __init__(self, username, password):
		self.username = username
		self.password = password
		self.stream_ids = [] 
		self.plots = {}
		self.initialize()

	def initialize(self):
		py.sign_in(self.username, self.password)
		self.stream_ids = tls.get_credentials_file()['stream_ids']
		# print len(self.stream_ids)

	def get_used_tokens(self):
		return [token for plot in self.plots.values() for token in plot.get_tokens() if plot.isOwned()]

	def new_plot_stream(self, title, node_ids, params, client_fd, maxpoints = 50):
		print "INFO: Starting new plot"
		nodes = len(node_ids)
		used_keys = self.get_used_tokens()
		# print len(self.stream_ids) - len(used_keys)
		# print nodes
		# print params
		# print (nodes * params)
		if (len(self.stream_ids) - len(used_keys)) < (nodes * len(params)):
			print 'ERROR: Not enough keys'
			return None
		tokens = []
		[tokens.append(key) for key in self.stream_ids if key not in used_keys and len(tokens) < (nodes * len(params))]
		plot = Plot(title, node_ids, params, client_fd, tokens, maxpoints = maxpoints)
		self.plots[client_fd] = plot
		return plot

	def remove_plot(self, plot):
		self.plots.remove(plot)


# username = "stariq"
# password = "7wakatl28e"
# newPlotter = Plotter(username, password)
# p = newPlotter.new_plot_stream('Checking', [0], ['CPU'], client_fd = 1, maxpoints = 20)
# p.initialize()
# print 'stream dictionary', p.stream_dict
# p.init_streams()
# # time.sleep(3)
# p.stream_start()
# # time.sleep(5)
# p.plot_jump('2015-07-05 10:30:36')
# # time.sleep(10)
# p.stream_stop()