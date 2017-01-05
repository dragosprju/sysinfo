from datetime import datetime
from Queue import *
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy import create_engine, distinct
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.orm import sessionmaker, relationship, backref
from threading import Lock
from time import mktime
from threading import Event
import thread
import time
import uuid

Engine = create_engine('sqlite:///sysinfo.db')
Session = sessionmaker()
Session.configure(bind = Engine)
Base = declarative_base()

import sys
sys.path.append('..')
from constants import *

class Computer(Base):
	__tablename__ = 'computers'

	id = 				Column(Integer, primary_key=True)
	mac = 				Column(String)
	name = 				Column(String)
	manufacturer = 		Column(String)
	memory = 			Column(Integer)
	os = 				Column(String)
	os_servicepack = 	Column(String)
	os_32bit = 			Column(Boolean) # False = 32bit, True = 64bit
	installDate = 		Column(DateTime)
	proc = 				Column(String)
	proc_32bit =		Column(Boolean)
	proc_noCores = 		Column(Integer)
	proc_noLogProc = 	Column(Integer)

	videoCards = relationship("VideoCard", cascade="save-update, delete, delete-orphan")
	networkAdapters = relationship("NetworkAdapter", cascade="save-update, delete, delete-orphan")
	statsEntries = relationship("StatsEntry")

	def __repr__(self):
		ret = 		"--- Computer %d\n" % (self.id)
		ret = ret + "Name: %s\n" % (self.name)
		ret = ret + "MAC: %s\n" % (self.mac)
		ret = ret + "Manufacturer: %s\n" % (self.manufacturer)
		ret = ret + "Memory: %d\n" % (self.memory)
		ret = ret + "Operating System: %s\n" % (self.os)
		ret = ret + "Service Pack: %s\n" % (self.os_servicepack)
		ret = ret + "32bit?: " + str(self.os_32bit) + "\n"
		ret = ret + "Install Date: " + str(self.installDate) + "\n"
		ret = ret + "Processor: %s\n" % (self.proc)
		ret = ret + "32bit?: " + str(self.proc_32bit) + "\n"
		ret = ret + "No cores: %d\n" % (self.proc_noCores)
		ret = ret + "No log proc: %d\n" % (self.proc_noLogProc)
		ret = ret + "\n"
		return ret

class VideoCard(Base):
	__tablename__ = 'videocards'

	id =				Column(Integer, primary_key=True)
	id_computer = 		Column(Integer, ForeignKey('computers.id'))
	name =				Column(String)
	memory = 			Column(Integer)

	def __repr__(self):
		if self.id != None:
			ret = 		"--- Video Card #%d\n" % (self.id)
		else:
			ret =       "--- Video Card\n"
		ret = ret + "Name: %s\n" % (self.name)
		ret = ret + "Memory: %d\n" % (self.memory)
		ret = ret + "\n"
		return ret

class NetworkAdapter(Base):
	__tablename__ = 'networkadapters'
	id =				Column(Integer, primary_key=True)
	id_computer = 		Column(Integer, ForeignKey('computers.id'))
	name = 				Column(String)

	#netStatsEntries = relationship("NetStatsEntry")

	def __repr__(self):
		if self.id != None:
			ret = 		"--- Network Adapter #%d\n" % (self.id)
		else:
			ret =       "--- Network Adapter\n"
		ret = ret + "Computer ID: %d\n" % (self.id_computer)
		ret = ret + "Name: %s\n" % (self.name)
		ret = ret + "\n"
		return ret

class StatsEntry(Base):
	__tablename__ = 'stats'

	id = 				Column(Integer, primary_key=True)
	id_computer =		Column(Integer, ForeignKey('computers.id'))
	timestamp =			Column(DateTime)
	proc_total =		Column(Integer)
	memory_phys_free = 	Column(Integer)
	memory_phys_total = Column(Integer)
	memory_virt_free =	Column(Integer)
	memory_virt_total = Column(Integer)
	disk_reads =		Column(Integer)
	disk_writes = 		Column(Integer)

	netStatsEntries = relationship("NetStatsEntry", cascade="save-update, delete, delete-orphan")
	procStatsEntries = relationship("ProcStatsEntry", cascade="save-update, delete, delete-orphan")

	def __repr__(self):
		ret = 		"--- Stat entry #%d\n" % (self.id)
		ret = ret + "Computer ID: %d\n" % (self.id_computer)
		ret = ret + "Timestamp: " + str(self.timestamp) + "\n"
		ret = ret + "CPU Total %: " + str(self.proc_total) + "\n"
		ret = ret + "Phys mem free/tot: %d / %d" % (self.memory_phys_free, self.memory_phys_total)
		ret = ret + "Virt mem free/tot: %d / %d" % (self.memory_virt_free, self.memory_virt_total)
		ret = ret + "Disk reads/writes: %d / %d" % (self.disk_reads, disk.writes)
		ret = ret + "\n"
		return ret

class NetStatsEntry(Base):
	__tablename__ = 'netstats'

	id = 				Column(Integer, primary_key=True)
	id_stats = 			Column(Integer, ForeignKey("stats.id"))
	id_netadapter = 	Column(Integer)#, ForeignKey("networkadapters.id"))
	bandwidth =			Column(Integer)
	received =			Column(Integer)
	sent = 				Column(Integer)

	def __repr__(self):
		if self.id != None:
			ret = 		"--- NETstat entry #%d\n" % (self.id)
		else:
			ret =       "--- NETstat entry\n"
		if self.id_stats != None:
			ret = ret + "Stat entry ID: %d\n" % (self.id_stats)
		else:
			ret = ret + "Stat entry ID: MISSING!\n"
		ret = ret + "Net adapter ID: %d\n" % (self.id_netadapter)
		ret = ret + "Bandwidth: %s\n" % (self.bandwidth)
		ret = ret + "Recv / Sent: %s / %s\n" % (self.received, self.sent)
		ret = ret + "\n"
		return ret

class ProcStatsEntry(Base):
	__tablename__ = 'procstats'

	id = 				Column(Integer, primary_key=True)
	id_stats = 			Column(Integer, ForeignKey("stats.id"))
	no =				Column(Integer)
	usage = 			Column(Integer)

	def __repr__(self):
		ret = 		"--- NETstat entry #%d\n" % (self.id)
		ret = ret + "Stat entry ID: %d\n" % (self.id_stats)
		ret = ret + "Net adapter ID: %d\n" % (self.id_netadapter)
		ret = ret + "CPU No: %d\n" % (self.no)
		ret = ret + "CPU Usage %: %d\n" % (self.usage)
		ret = ret + "\n"
		return ret

class DatabaseEngine():
	def __init__(self):
		Base.metadata.create_all(Engine)
		self.session = Session()
		self.session.autoflush = False		
		self.infoQueue = Queue()
		self.statsQueue = Queue()
		self.queryQueue = Queue()
		self.results = dict()
		self.stopped = False
		#self.i = 0

	def processInfo(self, mac, info):
		self.infoQueue.put((mac, info))

	def processStats(self, mac, stats):
		self.statsQueue.put((mac, stats))

	def begin2(self):
		while not self.stopped:
			if not self.infoQueue.empty():
				info = self.infoQueue.get()

				if INFO_START_KEYWORD not in info[1] or \
					INFO_SEPARATOR_KEYWORD not in info[1] or \
					INFO_STOP_KEYWORD not in info[1]:
					continue

				mac = info[0]
				info = info[1]

				modify = False
				if self.session.query(Computer.mac).filter(Computer.mac==mac).first() != None:
					modify = True

				if info[6] == '32-bit':
					os_arch = True
				else:
					os_arch = False

				if info[9] == '32-bit':
					proc_arch = True
				else:
					proc_arch = False


				#'28.09.2014 19:18:34'
				struct = time.strptime(info[7], "%d.%m.%Y %H:%M:%S")
				dt = datetime.fromtimestamp(mktime(struct))

				if not modify:
					computer = Computer(
						mac = mac,
						name = info[1],
						manufacturer = info[2],
						memory = int(info[3][:-3]),
						os = info[4],
						os_servicepack = info[5],
						os_32bit = os_arch,
						installDate = dt,
						proc = info[8],
						proc_32bit = proc_arch,
						proc_noCores = int(info[10]),
						proc_noLogProc = int(info[11])
						)

					self.session.add(computer)
				else:
					computer = self.session.query(Computer).filter(Computer.mac==mac).one()
					computer.name = info[1]
					computer.manufacturer = info[2]
					computer.memory = int(info[3][:-3])
					computer.os = info[4]
					computer.os_servicepack = info[5]
					computer.os_32bit = os_arch
					computer.installDate = dt
					computer.proc = info[8]
					computer.proc_32bit = proc_arch
					computer.proc_noCores = int(info[10])
					computer.proc_noLogProc = int(info[11])

				#self.session.commit()

				i = 12
				while info[i] != INFO_SEPARATOR_KEYWORD:
					memoryStr = info[i].rsplit(' ', 2)[1]
					info[i] = info[i].rsplit(' ', 2)[0]
					memory = int(memoryStr[1:])		
					videoCard = VideoCard(
						name =  info[i],
						memory = memory
						)
					i = i + 1
					if not modify:
						computer.videoCards.append(videoCard)
					elif len(computer.videoCards) != 0:
						computer.videoCards[i-13] = videoCard
				i = i + 1

				savei = i
				while info[i] != INFO_STOP_KEYWORD:
					networkAdapter = NetworkAdapter(
						id_computer = computer.id,
						name = info[i]
						)
					i = i + 1
					if not modify:
						computer.networkAdapters.append(networkAdapter)
					elif len(computer.networkAdapters) != 0:
						computer.networkAdapters[i-(savei+1)] = networkAdapter

				self.session.commit()
				#print computer.networkAdapters
				#print "Commited info"

			if not self.statsQueue.empty():
				stats = self.statsQueue.get()

				if STATS_START_KEYWORD not in stats[1] or \
					STATS_SEPARATOR_KEYWORD not in stats[1] or \
					STATS_STOP_KEYWORD not in stats[1]:
					continue

				mac = stats[0]
				stats = stats[1]

				computer = self.session.query(Computer).filter(Computer.mac==mac).first()

				if computer == None:
					continue
				networkAdapters = self.session.query(NetworkAdapter).filter(NetworkAdapter.id_computer==computer.id).all()

				i = 0
				cpu = []
				while stats[i] != STATS_SEPARATOR_KEYWORD:
					cpu.append(stats[i])
					i = i + 1

				statsEntry = StatsEntry(
						id_computer = computer.id,
				 		timestamp = datetime.now(),
				 		proc_total = cpu[-1],
				 		memory_phys_free = stats[11],
				 		memory_phys_total = stats[12],
				 		memory_virt_free = stats[13],
				 		memory_virt_total = stats[14],
				 		disk_reads = stats[15],
				 		disk_writes = stats[16]
					)

				self.session.add(statsEntry)
				#self.session.commit()				

				i = 18
				j = 0
				while stats[i] != STATS_STOP_KEYWORD:
					netStatsEntry = NetStatsEntry(
						id_stats = statsEntry.id,
						id_netadapter = networkAdapters[j].id,
						bandwidth = stats[i],
						received = stats[i+1],
						sent = stats[i+2]
					)
					i = i + 3
					j=j+1
					statsEntry.netStatsEntries.append(netStatsEntry)
					#print netStatsEntry

				cpu = cpu[1:-1]
				i = 0
				for c in cpu:
					procStatsEntry = ProcStatsEntry(
						id_stats = statsEntry.id,
						no = i,
						usage = c
						)
					i = i + 1
					statsEntry.procStatsEntries.append(procStatsEntry)

				self.session.commit()
				#print "Commited stats"

			if not self.queryQueue.empty():
				requestTuple = self.queryQueue.get()

				identifier = requestTuple[0]
				event = requestTuple[1]
				request = requestTuple[2]
				computerQuery = None

				for i in range(99):
					try:
						if request != "Computers Detailed":
							computerQuery = self.session.query(Computer.id, Computer.name, Computer.manufacturer).all() 
						else:
							computerQuery = self.session.query(Computer).all()
						break
					except:
						continue

				if request == "Computers Summary":
					result = self.getComputersSummary(computerQuery)
				elif request == "Computers Detailed":
					result = self.getComputersDetailed(computerQuery)
				elif request == "Average Stats":
					result = self.getAverageStats(computerQuery)
				elif request == "Current Stats":
					result = self.getCurrentStats(computerQuery)
				elif request == "Processor Stats":
					result = self.getProcessorStats(computerQuery)

				self.results[identifier] = result
				event.set()


	def queryFor(self, queryForWhat):
		identifier = uuid.uuid1()
		event = Event()
		self.queryQueue.put((identifier, event, queryForWhat))

		event.wait()

		result = self.results[identifier]
		del self.results[identifier]

		return result

	def getComputersSummary(self, computerQuery):
	 	actualQuery = []
	 	#computerQuery = []
	 	#computerQuery = self.session.query(Computer.id, Computer.name, Computer.manufacturer).all()
	 	for c in computerQuery:
	 		statsQuery = self.session.query(StatsEntry.timestamp).filter(StatsEntry.id_computer == c[0]).order_by(StatsEntry.timestamp.desc()).first()
	 		if statsQuery != None:
	 			actualQuery.append([c[0], c[1], c[2], statsQuery[0]])
	 	return actualQuery

	def getComputersDetailed(self, computerQuery):
	 	actualQuery = []
	 	computers = []
	 	#computerQuery = []
	 	#computerQuery = self.session.query(Computer).all()
	 	for c in computerQuery:
	 		computer = [c]
	 		videoCardQuery = self.session.query(VideoCard.name, VideoCard.memory).filter(VideoCard.id_computer == c.id).all()
	 		networkAdapterQuery = self.session.query(NetworkAdapter.name).filter(NetworkAdapter.id_computer == c.id).all()
	 		computer.append(videoCardQuery)
	 		computer.append(networkAdapterQuery)
	 		comp = Computer(
	 			)
	 		computers.append(computer)
	 	return computers

	def getAverageStats(self, computerQuery):
		# [ [COMPUTER_NAME, CPU, USEDMEM, TOTMEM, USEDVMEM, TOTVMEM, DISKREAD, DISKWRITE, NETDOWN, NETUP ], ...]
		averageStatsActualQuery = []

		# Computer name
		#computerQuery = self.session.query(Computer.id, Computer.name).all()
		if type(computerQuery[0]) is Computer:
			print "Average got computer type"
			return []

		for c in computerQuery:
			averageStats = [c[0], c[1]]
			statsQuery = self.session.query(
				StatsEntry.proc_total,
				StatsEntry.memory_phys_free, 
				StatsEntry.memory_phys_total, 
				StatsEntry.memory_virt_free, 
				StatsEntry.memory_virt_total, 
				StatsEntry.disk_reads, 
				StatsEntry.disk_writes,
				StatsEntry.id).filter(
				StatsEntry.id_computer == c[0]).all()

			if statsQuery == []:
				continue

			totAvgCpu = 0
			avgMem = 0
			avgVMem = 0
			diskReads = 0
			diskWrites = 0
			download = 0
			upload = 0

			r = 0
			w = 0
			d = 0
			u = 0
			for entry in statsQuery:
				totAvgCpu = totAvgCpu + entry[0]
				avgMem = avgMem + entry[1]
				avgVMem = avgVMem + entry[3]
				if entry[5] != 0:
					diskReads = diskReads + entry[5]
					r = r + 1
				if entry[6] != 0:
					diskWrites = diskWrites + entry[6]
					w = w + 1
				netStatsQuery = self.session.query(NetStatsEntry.received, NetStatsEntry.sent).filter(NetStatsEntry.id_stats == entry[7]).all()
				for n in netStatsQuery:
					if n.received > 0:
						download = download + n.received
						d = d + 1
					if n.sent > 0:
						upload = upload + n.sent 
						u = u + 1

			# Total Average CPU
			if len(statsQuery) != 0:
				totAvgCpu = totAvgCpu / len(statsQuery)
			averageStats.append(totAvgCpu)

			# Memory Used / Total Memory
			totMem = statsQuery[0][2]
			if len(statsQuery) != 0:
				avgMem = avgMem / len(statsQuery)
			avgMem = totMem - avgMem
			averageStats.extend([avgMem, totMem])

			# Virtual Memory Used / Total Memory
			totVMem = statsQuery[0][4]
			if len(statsQuery) != 0:
				avgVMem = avgVMem / len(statsQuery)
			avgVMem = totVMem - avgVMem
			averageStats.extend([avgVMem, totVMem])

			# Disk reads + writes
			if r != 0:
				diskReads = diskReads / r
			if w != 0:
				diskWrites = diskWrites / w
			averageStats.extend([diskReads, diskWrites])

			# Internet download + upload
			if d != 0:
				download = download / d
			if u != 0:
				upload = upload / u
			averageStats.extend([download, upload])

			averageStatsActualQuery.append(averageStats)

		return averageStatsActualQuery

	def getCurrentStats(self, computerQuery):
		currentStatsActualQuery = []

		#computerQuery = []
		#computerQuery = self.session.query(Computer.id, Computer.name).all()
		for c in computerQuery:
			currentStats = []
			statsQuery = self.session.query(
				StatsEntry.id,
				StatsEntry.proc_total,
				StatsEntry.memory_phys_free,
				StatsEntry.memory_phys_total,
				StatsEntry.memory_virt_free,
				StatsEntry.memory_virt_total,
				StatsEntry.disk_reads,
				StatsEntry.disk_writes,
				).filter(StatsEntry.id_computer == c[0]
				).order_by(StatsEntry.timestamp.desc()).first()
			if statsQuery == None:
				continue
			netStatsQuery = self.session.query(
				NetStatsEntry.id_netadapter,
				NetStatsEntry.bandwidth,
				NetStatsEntry.received,
				NetStatsEntry.sent,
				).filter(NetStatsEntry.id_stats == statsQuery[0]).all()
			netAdapterQuery = []
			for n in netStatsQuery:
				netAdapterQuery.append(self.session.query(
					NetworkAdapter.id,
					NetworkAdapter.name
					).filter(NetworkAdapter.id == n[0]).first())

			currentStats.extend(c)
			currentStats.append(statsQuery)
			currentStats.append(netStatsQuery)
			currentStats.append(netAdapterQuery)

			currentStatsActualQuery.append(currentStats)

		return currentStatsActualQuery

	def getProcessorStats(self, computerQuery):
		processorStatsActualQuery = []

		#computerQuery = self.session.query(Computer.id, Computer.name).all()
		for c in computerQuery:
			processorStats = [c[0], c[1]]
			recentStat = self.session.query(StatsEntry.id).filter(StatsEntry.id_computer == c[0]
				).order_by(StatsEntry.timestamp.desc()).first()
			if recentStat == None:
				continue
			processorStats.append(self.session.query(
				ProcStatsEntry.no,
				ProcStatsEntry.usage
				).filter(ProcStatsEntry.id_stats == recentStat[0]).all())
			processorStatsActualQuery.append(processorStats)

		return processorStatsActualQuery


	def begin(self):
		thread.start_new_thread(self.begin2, ())

	

