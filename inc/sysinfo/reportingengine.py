import socket
import pika
import pythoncom
import re
import tkMessageBox
import thread
import time
import wmi

import sys
sys.path.append('..')
from constants import *

class ReportingEngine(object):

	def __init__(self, argv, infoEngine, statsEngine):
		self.infoEngine = infoEngine
		self.statsEngine = statsEngine
		self.stopped = False

		if len(argv) > 1 and ReportingEngine.validIP(argv[1]):
			self.valid = True
			self.warningMessage = False
			self.ip = argv[1]
		elif len(argv) > 1 and not ReportingEngine.validIP(argv[1]):
			self.valid = False
			self.warningMessage = True
			self.ip = argv[1]
		else:
			self.valid = False
			self.warningMessage = False
			self.ip = None

	@staticmethod
	def validIP(address):
		if address == "localhost":
			return True
		try:
			socket.inet_aton(address)
			return True
		except socket.error:
			return False

	def status(self):
		return self.valid

	def initialize(self):
		self.w = wmi.WMI()

	def begin2(self):
		self.getMACAddress()
		self.packageInfo() # needs to stay before basic_consume

		# connect
		self.credentials = pika.PlainCredentials("sysinfo", "sysinfo")
		self.connection = pika.BlockingConnection(pika.ConnectionParameters(credentials=self.credentials, host=self.ip, heartbeat=20))
		self.channel = self.connection.channel()
		self.channel.basic_qos(prefetch_size=0, prefetch_count=1, global_qos=True)

		self.channel.exchange_declare(exchange='sysinfo_exchg', exchange_type='direct')
		#self.channel.queue_declare(queue="sysinfo_stats")
		#self.channel.queue_declare(queue="sysinfo_info")
		self.channel.queue_declare(queue=self.mac+"_req")

		#self.channel.queue_bind(exchange='sysinfo_exchg',
		#						queue='sysinfo_stats',
		#						routing_key='stats')
		#self.channel.queue_bind(exchange='sysinfo_exchg',
		#						queue='sysinfo_info',
		#						routing_key='info')
		self.channel.queue_bind(exchange='sysinfo_exchg',
								queue=self.mac+"_req",
								routing_key=self.mac)

		#self.channel.basic_consume(self.consumeStats, queue='sysinfo_stats')
		#self.channel.basic_consume(self.consumeInfo, queue='sysinfo_info')
		self.channel.basic_consume(self.mac+"_req", self.handleRequests)
		
		#self.sendInfo()

		thread.start_new_thread(self.channel.start_consuming, ())

		self.connection_stats = pika.BlockingConnection(pika.ConnectionParameters(credentials=self.credentials, host=self.ip, heartbeat=20))
		self.channel_stats = self.connection_stats.channel()
		#self.channel_stats.basic_qos(prefetch_count=1)
		self.channel_stats.exchange_declare(exchange='sysinfo_exchg', exchange_type='direct')

		thread.start_new_thread(self.packageAndSendStats, ())

	def begin(self):
		if self.warningMessage == True:
			tkMessageBox.showwarning('Invalid IP', 'The first argument (' + self.ip + ') you have entered is not a valid IP. Reporting is not enabled in this session.')
		elif self.warningMessage == False and self.valid == True:
			thread.start_new_thread(self.begin2, ())
		else:
			pass

	def getMACAddress2(self):
		query = "SELECT MACAddress FROM Win32_NetworkAdapter WHERE MACAddress IS NOT NULL AND PhysicalAdapter = True"
		MACAddresses = self.w.query(query)
		self.mac = MACAddresses[0].MACAddress

	def getMACAddress(self):
		pythoncom.CoInitialize()
		self.initialize()
		self.getMACAddress2()
		pythoncom.CoUninitialize()

	def packageInfo(self):
		infoMessage = [self.mac + " : " + INFO_START_KEYWORD]
		infoEngineReport = self.infoEngine.toReport

		for i in range(len(infoEngineReport)):
			infoEngineReport[i] = self.mac + " : " + infoEngineReport[i]

		infoMessage.extend(infoEngineReport)
		infoMessage.append(self.mac + " : %s" % INFO_SEPARATOR_KEYWORD)

		self.statsEngine.updateEvent.wait()
		statsReport = self.statsEngine.toReport
		self.statsEngine.updateEvent.clear()
		for i in range(len(statsReport)):
			statsReport[i] = unicode(statsReport[i])
			statsReport[i] = statsReport[i].encode('ascii')
			statsReport[i] = self.mac + " : " + statsReport[i]
		infoMessage.extend(statsReport)
		infoMessage.append(self.mac + " : %s" % INFO_STOP_KEYWORD)
		self.info = infoMessage

	def sendInfo(self):
		for i in self.info:
			self.channel.basic_publish(exchange='sysinfo_exchg',
									   routing_key='info',
									   body=i)

	def packageStats(self):
		statsMessage = [self.mac + " : " + STATS_START_KEYWORD]

		statsReport = self.statsEngine.toReport2
		for i in range(len(statsReport)):
			statsReport[i] = self.mac + " : " + statsReport[i]

		statsMessage.extend(statsReport)
		statsMessage.append(self.mac + " : " + STATS_STOP_KEYWORD)

		self.stats = statsMessage

	def sendStats(self):
		for s in self.stats:
			self.channel_stats.basic_publish(exchange='sysinfo_exchg',
										   routing_key='stats',
										   body=s)

	def handleRequests(self, ch, method, properties, body):
		print "Sending info per request"
		self.sendInfo()
		ch.basic_ack(delivery_tag = method.delivery_tag)

	def packageAndSendStats(self):
		while not self.stopped:
			self.statsEngine.updateEvent.wait()
			self.statsEngine.updateEvent.clear()

			self.packageStats()
			self.sendStats()
			#print "Packaged and sent stats"
