#!/usr/bin/python

import sys
import time
import json
import socket
import platform
import multiprocessing

def get_cpu_faster(f):
	#read the first line of the /proc/stat file
	raw = f.readlines()[0].strip().split()[1:] 
	#sum up all the values to get the total time										
	total = sum(float(w) for w in raw)
	#get the 4th value which is the idle time												
	idle = float(raw[3])															
	f.seek(0, 0)
	return (total, idle)

def get_mem_usage(f):
	raw = f.readlines()[:2]
	[total, free] = [float(s.split()[1]) for s in raw]
	f.seek(0, 0)
	return (1 - free / total) * 100

def main(argv):
   # Opening proc files
   usage_file = open('/proc/stat')
   mem_file = open('/proc/meminfo')
   cpu_file = open('/proc/cpuinfo')

   # Parsing command-line arguments
   TCP_IP = argv[0]
   NAME = argv[1]
   PLAT = int(argv[2])
   interval = float(argv[3])
   N = int(argv[4])

   # Establishing connection with server
   TCP_PORT = 4996
   BUFFER_SIZE = 1024
   s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
   print TCP_IP, TCP_PORT
   s.connect((TCP_IP, TCP_PORT))

   # Collecting system info
   # Getting OS name
   OS = platform.dist()
   OS = OS[0] + ' ' + OS[1] + ' ' + OS[2] 

   # Getting Total RAM 
   line = mem_file.readline()
   if 'Total' in line:
       MEM = line.split(':')[1].split()[0].strip() 
   else: 
       print "Error finding the total memory in proc file"
       print "Exiting .. " 
       exit

   # Getting maximum CPU frequency
   k = cpu_file.readlines() 
   cpu_mhz = ''
   for line in k:
       if 'MHz' in line:
           cpu_mhz = line.split(':')[1].strip()
   if cpu_mhz == '': 
       print "Error finding the maximum cpu frequency in proc file"
       print "Exiting .. " 
       exit
   CPU = int(float(cpu_mhz))
   cpu_file.close()

   # Getting number of cores
   CORES = multiprocessing.cpu_count()
   
   # Construct JSON object
   connect = {}
   connect['cmd'] = 'connect'
   connect['name'] = NAME
   connect['os'] = OS
   connect['cpu'] = CPU
   connect['mem'] = MEM 
   connect['cores'] = CORES
   connect['platform'] = PLAT
   connect['metrics'] = ['CPU', 'MEMORY']
   json_data = json.dumps(connect)

   # send connect packet
   s.send(json_data+'\END') 
    
   # initializing values
   update = {}
   update['cmd'] = "update"
   update['info'] = {}
   prev_total = 0 
   prev_idle = 0 
   i = 0

   # if N is negative the script runs forever
   while (i < N):
       i = i + 1
       time.sleep(interval) 
       
       # Get current CPU usage and calculate difference
       (new_total, new_idle) = get_cpu_faster(usage_file)
       (actual_total, actual_idle) = (new_total - prev_total, new_idle - prev_idle)

       # Calculate idle peecentage then update values
       idle = (actual_idle / actual_total) * 100.0
       (prev_total, prev_idle) = (new_total, new_idle)

       # usage is a string with 2 decimal places from 100-idle
       usage = format(100-idle, '.2f')

       # Get Memory Usage 
       # mem is a string with 2 decimal places from the mempry_usage value
       mem = format(get_mem_usage(mem_file), '.2f')

       # Construct JSON
       update['info']['CPU'] = usage
       update['info']['MEMORY'] = mem
       json_data = json.dumps(update)

       # update server
       s.send(json_data+'\END')

   s.close()
   usage_file.close()
   mem_file.close()


       
       
	

if __name__ == "__main__":
   if len(sys.argv) != 6:
       print 'Usage ./update_server [server IP] [device name] [platform int] [interval] [number of iterations]'
       exit
   else: 
       main(sys.argv[1:])
										
