import datetime
import thread
import time
from threading import Event
from Queue import Queue, Empty

import sys
sys.path.append('..')
from wmi2 import *

class GuiEngine(object):
	def __init__(self, window, databaseEngine, tk):
		self.window = window
		self.databaseEngine = databaseEngine
		self.tk = tk

		self.computerSummaryListed = dict()
		self.computerDetailsListed = dict()
		self.averageStatsListed = dict()
		self.currentStatsListed = dict()
		self.processorStatsListed = dict()

		self.stopped = False
		self.queue = Queue()
		self.update = Event()
		self.update.set()

		self.i = 0

		self.tk.bind('<Configure>', self.holdUpdate)

	def holdUpdate(self, e):
		if self.update.isSet():
			self.update.clear()
			self.tk.after(2000, self.update.set)

	def announceReprocess(self):
		self.queue.put("p")

	def processLabels(self):
		self.i = self.i + 1
		self.summaryTab.processLabels("summary")
		self.detailsTab.processLabels("details")
		self.averageTab.processLabels("average")
		self.currentTab.processLabels("current")
		self.processorTab.processLabels("processor")

	def begin(self):
		self.summaryTab = self.window.getTab(1)
		self.detailsTab = self.window.getTab(2)
		self.averageTab = self.window.getTab(3)
		self.currentTab = self.window.getTab(4)
		self.processorTab = self.window.getTab(5)
		self.summaryTab.addRow("ID", "Name", "Manufacturer", "Last Updated")
		self.averageTab.addRow("Computer", "CPU %", "Memory", "Virtual Memory", "Disk R/W (>0)", "Net Dl/Up (>0)")

		thread.start_new_thread(self.begin2, ())
		self.begin3()

	def begin3(self):
		while not self.stopped:
			try:
				self.queue.get(block=False)
			except Empty:
				break
			else:
				self.tk.after_idle(self.processLabels)
			self.tk.after(100, self.begin3)
		self.tk.after(100, self.begin3)


	def begin2(self):
		while not self.stopped:

			# Computers Summary Tab
			computersSummary = self.databaseEngine.queryFor("Computers Summary")
			for c in computersSummary:
				dt = c[3].strftime("%d.%m.%y %H:%M:%S")
				if c[0] not in self.computerSummaryListed:					
					stringVars = self.summaryTab.addRow(c[0], c[1], c[2], str(dt))
					self.computerSummaryListed[c[0]] = stringVars	
					self.announceReprocess()		
				else:
					stringVars = self.computerSummaryListed[c[0]]
					strings = [str(c[0]), str(c[1]), str(c[2]), str(dt)]
					self.updateVars(stringVars, strings)

			# Computers Details Tab
			computersDetailed = self.databaseEngine.queryFor("Computers Detailed")
			for c in computersDetailed:
				computer = c[0]
				videoCards = c[1]
				networkAdapters = c[2]
				stringVars = []
				dt = computer.installDate.strftime("%d.%m.%y %H:%M:%S")
				if computer.os_32bit == True:
					osarch = "32-bit"
				else:
					osarch = "64-bit"

				if computer.proc_32bit == True:
					procarch = "32-bit"
				else:
					procarch = "64-bit"

				if computer.id not in self.computerDetailsListed:
					stringVars.extend(self.detailsTab.addRow(computer.name))
					result = self.addRows(
						tab = self.detailsTab,
						strings = [
							["", "Manufacturer: ", computer.manufacturer],
							["", "Memory: ", str(computer.memory) + " MB"],
							["", "Operating System: ", computer.os],
							["" , "Service Pack: ", computer.os_servicepack],
							["", "Architecture Installed: ", osarch],
							["", "Install Date: ", dt],
							["" , "Processor Name: ", computer.proc],
							["", "Processor Architecture: ", procarch],
							["", "No. Cores: ", str(computer.proc_noCores)],
							["", "No. Logical Processors: ", str(computer.proc_noLogProc)]

						],
						indices = [2])
					stringVars.extend(result)

					i = 1
					for v in videoCards:
						vname = v[0] + " (" + str(v[1]) + " MB)"
						result = self.detailsTab.addRow("", "Video Card #" + str(i) + ": ", vname)
						stringVars.append(result[2])
						i = i + 1

					i = 1
					for n in networkAdapters:
						result = self.detailsTab.addRow("", "Network Adapter #" + str(i) + ": ", n[0])
						stringVars.append(result[2])
						i = i + 1

					self.computerDetailsListed[computer.id] = stringVars
					self.announceReprocess()
				else:
					stringVars = self.computerDetailsListed[computer.id]
					strings = []
					strings.extend([
						computer.name,
						computer.manufacturer,
						str(computer.memory) + " MB",
						computer.os,
						computer.os_servicepack,
						osarch,
						dt,
						computer.proc,
						procarch,
						computer.proc_noCores,
						computer.proc_noLogProc,
						])

					for v in videoCards:
						strings.append(v[0] + " (" + str(v[1]) + " MB)")

					for n in networkAdapters:
						strings.append(n[0])

					self.updateVars(stringVars, strings)

			# Average Stats Tab
			# [ [ID, COMPUTER_NAME, CPU, USEDMEM, TOTMEM, USEDVMEM, TOTVMEM, DISKREAD, DISKWRITE, NETDOWN, NETUP ], ...]
			averageStats = self.databaseEngine.queryFor("Average Stats")
			
			if averageStats != None:
				for s in averageStats:
					computer = s[1]
					cpu_total = str(s[2])
					usedmem = wmi2.divide(s[3], 1024, "MB")
					totmem = wmi2.divide(s[4], 1024, "MB")
					usedvmem = wmi2.divide(s[5], 1024, "MB")
					totvmem = wmi2.divide(s[6], 1024, "MB")
					diskread = wmi2.divideAuto(s[7])
					diskwrite = wmi2.divideAuto(s[8])
					netdown = wmi2.divideAuto(s[9])
					netup = wmi2.divideAuto(s[10])
					args = [s[1], s[2], usedmem + " / " + totmem, usedvmem + " / " + totvmem, diskread + " / " + diskwrite, netdown + " / " + netup]
					if s[0] not in self.averageStatsListed:
						stringVars = self.averageTab.addRow(*args)
						self.averageStatsListed[s[0]] = stringVars
						self.announceReprocess()
					else:
						stringVars = self.averageStatsListed[s[0]]
					 	self.updateVars(stringVars, args)

			# Current Stats Tab
			currentStats = self.databaseEngine.queryFor("Current Stats")
			if currentStats != None:
				for s in currentStats:
					stats = s[3]
					netStats = s[4]
					netAdapters = s[5]
					stringVars = []

					if netAdapters[0] == None:
								break
					
					usedmem = wmi2.divide(int(stats[3]) - int(stats[2]), 1024, "MB")
					totmem = wmi2.divide(stats[3], 1024, "MB")
					usedvmem = wmi2.divide(int(stats[5]) - int(stats[4]), 1024, "MB")
					totvmem = wmi2.divide(stats[5], 1024, "MB")
					diskread = wmi2.divideAuto(stats[6])
					diskwrite = wmi2.divideAuto(stats[7])					

					if s[0] not in self.currentStatsListed:		
						stringVars.extend(self.currentTab.addRow(s[1]))

						rowsToAdd = [
							["", "Total CPU: ", str(stats[1]) + "%"],
							["", "Memory Used / Total: ", usedmem + " / " + totmem],
							["", "Virtual Memory Used / Total: " , usedvmem + " / " + totvmem],
							["", "Disk Reads / Writes: ", diskread + " / " + diskwrite]
						]

						

						for i in range(len(netStats)):
							

							bandwidthText = netAdapters[i][1] + " Bandwidth: "
							bandwidth = wmi2.divide(netStats[i][1], 1000*1000, "Mbps")

							updownText = netAdapters[i][1] + " Dl/Up: "
							down = wmi2.divideAuto(netStats[i][2])
							up = wmi2.divideAuto(netStats[i][3])
							updown = down + " / " + up
							rowsToAdd.append(["", bandwidthText,  bandwidth])
							rowsToAdd.append(["", updownText, updown])

						result = self.addRows(tab=self.currentTab, strings=rowsToAdd, indices=[2])
						stringVars.extend(result)
						self.currentStatsListed[s[0]] = stringVars
						self.announceReprocess()
					else:
						stringVars = self.currentStatsListed[s[0]]
						#print "The stringVars: ", stringVars
						strings = []
						strings.extend([
							s[1],
							str(stats[1]) + '%',
							usedmem + " / " + totmem,
							usedvmem + " / " + totvmem,
							diskread + " / " + diskwrite
							])
						for i in range(len(netStats)):
							bandwidth = wmi2.divide(netStats[i][1], 1000*1000, "Mbps")
							down = wmi2.divideAuto(netStats[i][2])
							up = wmi2.divideAuto(netStats[i][3])
							updown = down + " / " + up	
							strings.extend([bandwidth, updown])
						self.updateVars(stringVars, strings)

			# Processor Stats Tab
			processorStats = self.databaseEngine.queryFor("Processor Stats")
			if processorStats != None:
				for p in processorStats:
					stats = p[2]
					stringVars = []

					if p[0] not in self.processorStatsListed:
						label = self.processorTab.addRow(p[1])
						stringVars.extend(label)
						texts = []
						for cpu in stats:
							texts.append(["", "Processor #" + str(cpu[0] + 1), str(cpu[1]) + "%"])
						stringVars.extend(
							self.addRows(strings = texts, indices = [2], tab = self.processorTab)
							)
						self.processorStatsListed[p[0]] = stringVars
						self.announceReprocess()
					else:
						stringVars = self.processorStatsListed[p[0]]
						strings = [p[1]]
						for cpu in stats:
							strings.append(str(cpu[1]) + "%")
						self.updateVars(stringVars, strings)

	def addRows(self, **args):
		returnList = []
		for s in args["strings"]:
			result = args["tab"].addRow(*s)
			for n in args["indices"]:
				returnList.append(result[n])
		return returnList

	def updateVars(self, labels, withWhats):
		for i in range(len(labels)):
			l = labels[i]
			s = withWhats[i]
			ltext = None
			for i in range(99):
				try:
					ltext = l.cget('text')
					break
				except:
					continue
			if (ltext != s):
				self.update.wait()
				l["text"] = s
			


