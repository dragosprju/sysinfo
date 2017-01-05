import pika
import re
import thread
from threading import Event

import sys
import os
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parentdir)
from constants import *

class ReceivingEngine(object):

	def __init__(self, dataEngine):
		self.ip = "localhost"
		self.computers = {}
		self.stopped = False
		self.dataEngine = dataEngine
		self.i = 0 

		self.connection = pika.BlockingConnection(pika.ConnectionParameters(self.ip, heartbeat_interval=20))
		self.channel = self.connection.channel()
		self.channel.basic_qos(prefetch_count=1)

		self.channel.exchange_declare(exchange='sysinfo_exchg', type='direct')
		self.channel.queue_declare(queue="sysinfo_stats")
		self.channel.queue_declare(queue="sysinfo_info")
		#self.channel.queue_declare(queue=self.mac+"_req")

		self.channel.queue_bind(exchange='sysinfo_exchg',
								queue='sysinfo_stats',
								routing_key='stats')
		self.channel.queue_bind(exchange='sysinfo_exchg',
								queue='sysinfo_info',
								routing_key='info')
		#self.channel.queue_bind(exchange='sysinfo_exchg',
		#						queue=self.mac+"_req",
		#						routing_key='req')

		self.channel.basic_consume(self.consumeStats, queue='sysinfo_stats')
		self.channel.basic_consume(self.consumeInfo, queue='sysinfo_info')
		#self.channel.basic_consume(self.checkRequests,
		#						   queue=self.mac+"_req")		

	def countMessages(self, queue):
		strStats = self.channel.queue_declare(queue=queue)
		intStats = re.findall("\d+", str(strStats))
		return int(intStats[3])

	def requestInfo(self, mac):
		count = self.countMessages(mac+"_req")
		if count == 0 and self.i == 0:
			self.i = self.i + 1
			print "Requesting info for " + mac
			self.channel.basic_publish(exchange='sysinfo_exchg',
										   routing_key=mac,
										   body='req')
			thread.start_new_thread(self.preventReRequest, ())

	def preventReRequest(self):
		self.connection.sleep(1)
		self.i = self.i - 1

	def consumeStats(self, ch, method, properties, body):
		bodylist = str.split(body, " : ")
		mac = bodylist[0]
		message = bodylist[1]

		if mac not in self.computers:
			if self.countMessages(mac) == 0:
		 		self.requestInfo(mac)
		 	else:
		 		return
		else:
		 	self.computers[mac][1].append(message)
		 	if message == STATS_STOP_KEYWORD:
		 		self.shipAwayStats(mac, self.computers[mac][1])

		ch.basic_ack(delivery_tag = method.delivery_tag)

	def consumeInfo(self, ch, method, properties, body):
		bodylist = str.split(body, " : ")
		mac = bodylist[0]
		message = bodylist[1]

		if mac not in self.computers:
			self.computers[mac]=([], [])
		self.computers[mac][0].append(message)
		if message == INFO_STOP_KEYWORD:
			self.shipAwayInfo(mac, self.computers[mac][0])
		ch.basic_ack(delivery_tag = method.delivery_tag)

	def begin(self):
		thread.start_new_thread(self.channel.start_consuming, ())

	def shipAwayInfo(self, mac, info):
		#print "INFO BEFORE SHIP: " + str(info)
		self.dataEngine.processInfo(mac, list(info))
		del self.computers[mac][0][:]

	def shipAwayStats(self, mac, stats):
		self.dataEngine.processStats(mac, list(stats))
		del self.computers[mac][1][:]

	def stop(self):
		self.channel.stop_consuming()
		self.stopped = True
