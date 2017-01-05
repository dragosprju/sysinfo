from threading import Event
import thread
#import time
import pythoncom
import wmi

import sys
sys.path.append('..')
from constants import *
from engine import *
from wmi2 import *

class StatsEngine(Engine):

	def __init__(self, window, infoTab):
		super(StatsEngine, self).__init__(window, infoTab)
		self.stopped = False
		self.physicalAdapterNames = []
		self.physicalAdapterStats = []
		self.toReport = []
		self.updateEvent = Event()
	def initialize(self):
		pythoncom.CoInitialize()
		self.initialize2()
		pythoncom.CoUninitialize()

	def initialize2(self):
		self.w = wmi.WMI()
		queryCPU = "SELECT Name, PercentProcessorTime FROM Win32_PerfFormattedData_PerfOS_Processor"
		queryOS = "SELECT FreePhysicalMemory, FreeVirtualMemory, TotalVisibleMemorySize, TotalVirtualMemorySize FROM Win32_OperatingSystem"
		queryDisk = "SELECT DiskReadBytesPersec, DiskWriteBytesPersec FROM Win32_PerfFormattedData_PerfDisk_PhysicalDisk WHERE Name = '_Total'"
		self.cpu = self.w.query(queryCPU)
		self.os = self.w.query(queryOS)
		self.disk = self.w.query(queryDisk)[0]
		self.net = self.initializeNetwork()

	def initializeNetwork(self):
		if self.physicalAdapterNames == []:
			#print "=== NEW!!! ==="
			query = "SELECT Name FROM Win32_NetworkAdapter WHERE MACAddress IS NOT NULL AND PhysicalAdapter = True"
			self.physicalAdapterNames = self.w.query(query)

		self.physicalAdapterStats = []
		self.toReport = []
		for adapter in self.physicalAdapterNames:
			adapterName = adapter.Name.replace("(R)","[R]")
			query = "SELECT Name, CurrentBandwidth, BytesReceivedPersec, BytesSentPersec FROM Win32_PerfFormattedData_Tcpip_NetworkInterface WHERE Name = '%s'" % (adapterName)
			queryResult = self.w.query(query)
			self.physicalAdapterStats.extend(queryResult)
			if len(queryResult) > 0:
				self.toReport.append(queryResult[0])
		#print self.physicalAdapterStats
		return self.physicalAdapterStats


	def loadPredefined(self):
		self.initialize2()
		for c in self.cpu:
			self.createRow("CPU " + wmi2.checkForTotal(c.Name) + " Usage", wmi2.placeholder)
		self.createSeparator()

		self.createRow("Free Memory / Total Memory", wmi2.placeholder)
		self.createRow("Free Virtual Memory / Total Virtual Memory", wmi2.placeholder)

		self.createRow("Disk Reads / Writes", wmi2.placeholder)

		for n in self.net:
			self.createRow(n.Name + " Bandwidth", wmi2.placeholder)
			self.createRow(n.Name + " Received / Sent", wmi2.placeholder)

	def setI(self, value):
		self.i = value - 1

	def getI(self):
		self.i = self.i + 1
		return self.i

	def update(self):
		self.toReport2 = []

		self.setI(0)
		for c in self.cpu:
			value = str(c.PercentProcessorTime)
			self.bodies[self.getI()].set(value)
			self.toReport2.append(value)

		self.toReport2.append(STATS_SEPARATOR_KEYWORD)

		freePhMem = self.os[0].FreePhysicalMemory
		totVisMem = self.os[0].TotalVisibleMemorySize
		freeViMem = self.os[0].FreeVirtualMemory
		totVirMem = self.os[0].TotalVirtualMemorySize
		diskReads = self.disk.DiskReadBytesPersec
		diskWrite = self.disk.DiskWriteBytesPersec

		self.bodies[self.getI()].set(wmi2.divide(freePhMem, 1024, "MB") + " / " + wmi2.divide(totVisMem, 1024, "MB"))
		self.bodies[self.getI()].set(wmi2.divide(freeViMem, 1024, "MB") + " / " + wmi2.divide(totVirMem, 1024, "MB"))
		self.bodies[self.getI()].set(wmi2.divideAuto(diskReads) + " / " + wmi2.divideAuto(diskWrite))

		self.toReport2.extend([freePhMem, totVisMem, freeViMem, totVirMem, diskReads, diskWrite, STATS_SEPARATOR_KEYWORD])

		for n in self.net:
			currBandw = n.CurrentBandwidth
			bytesRecv = n.BytesReceivedPersec
			bytesSent = n.BytesSentPersec
			self.bodies[self.getI()].set(wmi2.divide(currBandw, 1000*1000, "Mbps"))
			self.bodies[self.getI()].set(wmi2.divideAuto(bytesRecv) + " | " +
				wmi2.divideAuto(bytesSent))
			self.toReport2.extend([currBandw, bytesRecv, bytesSent])

		self.updateEvent.set()

	def populate2(self):
		while not self.stopped:
			self.initialize()
			self.update()

	def populate(self):
		thread.start_new_thread(self.populate2, ())

	def stop(self):
		self.stopped = True