import wmi

import sys
sys.path.append('..')
from engine import *
from wmi2 import *

class InfoEngine(Engine):

	def __init__(self, window, infoTab):
		super(InfoEngine, self).__init__(window, infoTab)
		self.toReport = []

	def initialize(self):
		w = wmi.WMI()
		self.os = w.Win32_OperatingSystem()[0]
		self.cpu = w.Win32_Processor()[0]	
		self.mb = w.Win32_BaseBoard()[0] # Motherboard
		self.mem = w.Win32_PhysicalMemory()
		self.gpu = w.Win32_VideoController()

	def loadPredefined(self):
		self.initialize()
		self.createRow("Computer Name", self.cpu.SystemName)
		self.createRow("Motherboard Manufacturer", self.mb.Manufacturer)
		self.createRow("Total Memory", wmi2.totalMemory(self.mem))
		self.createSeparator()

		self.createRow("Operating System", self.os.Caption)
		self.createRow("Service Pack", self.os.CSDVersion)
		self.createRow("Architecture", self.os.OSArchitecture)
		self.createRow("Install Date", wmi2.installDate(self.os.InstallDate))
		self.createSeparator()

		self.createRow("Processor Name", self.cpu.Name)
		self.createRow("Processor Architecture", wmi2.convertArchitecture(self.cpu.Architecture))
		self.createRow("Number of Cores", self.cpu.NumberOfCores)
		self.createRow("Number of Logical Processors", self.cpu.NumberOfLogicalProcessors)
		self.createSeparator()

		i = 1
		for g in self.gpu:
			self.createRow("Video Card #" + str(i), wmi2.videoCard(g))
			i = i + 1

	def populate(self):
		self.initialize()
		for i in range(len(self.bodies)):
			body = str(self.functions[i])
			self.bodies[i].set(body)
			self.toReport.append(body)