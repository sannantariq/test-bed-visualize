import datetime
import random

n = 500;
c = 10;
filename = 'CPU-metric.txt';

with open(filename, 'w') as f:
	for _ in range(n):
		write_string = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
		f.write(write_string);
		for i in range(c):
			metric_val = str(random.random() * 100);
			f.write(' %.4d:%.4s' % (i, metric_val));
		f.write('\n');
