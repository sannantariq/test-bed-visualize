import time

def traverse_line(f):
	c = f.read(1)
	while(c != '\n'):
		c = f.read(1)

def get_file_size(f):
	curr = f.tell()
	f.seek(0, 2)
	size = f.tell()
	f.seek(curr, 0)
	return size

def get_line_len(f):
	curr = f.tell()
	l = len(f.readline())
	f.seek(curr, 0)
	return l

def traverse_to_start(f):
	c = f.read(1)
	# print 'char = ', c
	pos = f.tell()
	while(c != '\n' and pos >= 2):
		f.seek(-2, 1)
		c = f.read(1)
		# print c
		# print 'char = ', c
		pos -=1
	if c != '\n':
		f.seek(-1, 1)
	return f.tell()

def get_secs(string):
	[h, m, s] = string.split(':')
	return (int(h) * 3600) + (int(m) * 60) + int(float(s))

def get_key_from_line(line):
	line = line.split()
	day = line[0].split('-')
	date_key = ''.join(day)
	return (date_key, get_secs(line[1]))

def get_key(f):
	line = f.readline()
	# print "line =="+line
	k = get_key_from_line(line)
	f.seek(- len(line) - 1, 1)
	return k

def key_cmp(k1, k2):
	k1 = k1.split(':')[2]
	k2 = k2.split(':')[2]
	if k1 == k2:
		return 0
	if k1 > k2:
		return 1
	return -1

def compare_dates(d1, d2):
	d1 = str(d1)
	d2 = str(d2)
	y1 = int(d1[:4])
	y2 = int(d2[:4])
	m1 = int(d1[4:6])
	m2 = int(d2[4:6])
	da1 = int(d1[6:8])
	da2 = int(d1[6:8])
	if y1 > y2:
		return 1
	if y1 < y2:
		return -1
	if m1 > m2:
		return 1
	if m1 < m2:
		return -1
	if d1 > d2:
		return 1
	if d1 < d2:
		return -1
	return 0
	
def compare_key(k1, k2):
	(d1, s1) = k1
	(d2, s2) = k2
	date_com = compare_dates(d1, d2)
	# print 'date comp : ', date_com
	if date_com == 0:
		if s1 < s2:
			return -1
		if s1 == s2:
			return 0
		if s1 > s2:
			return 1
	return date_com

def bin_search_prime(low, high, key, fd):
	if high <= low:
		return -1
	mid = (low + high) / 2
	fd.seek(mid, 0)
	line_start = traverse_to_start(fd)
	# print 'low = %d, high = %d, mid = %d, line_start = %d' % (low, high, mid, line_start)
	if line_start < low or line_start >= high:
		return -1
	
	new_key = get_key(fd)
	# cmp = key_cmp(key, new_key)
	cmp = compare_key(key, new_key)
	if cmp == 0:
		return 0
	line_len = get_line_len(fd)
	if cmp == -1:
		return bin_search_prime(low, line_start, key, fd)
	if cmp == 1:
		return bin_search_prime(line_start + line_len, high, key, fd)


def bin_search(key, fd):
	low = 0
	high = get_file_size(fd)
	return bin_search_prime(low, high, key, fd)

def get_prev(fd, n):
	traverse_to_start(fd)
	curr = fd.tell()
	for _ in range(n):
		if fd.tell() == 0:
			break
		fd.seek(-2, 1)
		traverse_to_start(fd)
		

	# traverse_to_start(fd)
	data_list = []
	for _ in range(n):
		# print fd.tell(), curr
		if fd.tell() >= curr:
			print "In line"
			break
		line = fd.readline()
		# xcord = n
		data_list.append(get_data_points(line))

	return data_list

def get_data_points(line):
	line = line.strip().split()
	x_cord = ' '.join(line[:2])
	line = line[2:]
	y_cords = [x.split(':') for x in line]
	y_cords = [(int(id), int(float(val))) for (id, val) in y_cords if val != 'nan']
	y_cords = dict(y_cords)
	return (x_cord, y_cords)



class FileReader(object):
	def __init__(self, filename):
		self.name = filename
		self.initialize()

	def initialize(self):
		self.fd = open(self.name)
	
	def read_line(self):
		return self.fd.readline()

	def read_data(self):
		line = self.read_line()
		return get_data_points(line)
	
	def find(self, time_string):
		key = get_key_from_line(time_string)
		return bin_search(key, self.fd)

	def get_previous_n(self, n):
		return get_prev(self.fd, n)

	def seek_end(self):
		self.fd.seek(-3, 2)

	def close(self):
		self.fd.close()

	def _traversestart(self):
		traverse_to_start(self.fd)


# f = FileReader('guinea_search.txt')

# print f.read_data()

# f.seek_end()
# # f.fd.seek(0, 50)
# # print f.read_data()
# print f.get_previous_n(10)
# f._traversestart()
# print f.read_data()

# # print f.find('2015-06-16 10:20:48')
# # d = f.get_previous_n(10)
# # print d
# # print f.read_data()
# f.close()