import ctypes

# Extra Functions
class wmi2(object):
	@staticmethod
	def convertArchitecture(number):
		if number == 0:
			return "32-bit"
		elif number == 9:
			return "64-bit"
		else:
			return "Undefined"

	#TODO: Unit test this
	@staticmethod
	def divide(value, divValue, label):
		if label != "":
			label = " " + label
		return str(int(value) / divValue) + label

	@staticmethod
	def divideAuto(value):
		if int(value) < 1024:
			return str(value) + " b/s"
		else:
			divided = float(value) / 1024
			if divided < 1024:
				return "%.1f kB/s" % divided
			else:
				divided = divided / 1024
				return "%.1f MB/s" % (divided)

	@staticmethod
	def totalMemory(memory):
		totalMemory = 0
		for mem in memory:
			totalMemory = totalMemory + int(mem.Capacity)
		return wmi2.divide(totalMemory, 1024*1024, "MB")


	@staticmethod
	def videoCard(gpu):
		gpuName = gpu.Name
		gpuVRAM = str((ctypes.c_uint32(gpu.AdapterRAM).value/1048576)) + " MB"
		return gpuName + " (" + gpuVRAM + ")"

	@staticmethod
	def installDate(installDate):
		year = installDate[0:4]
		month = installDate[4:6]
		day = installDate[6:8]
		hours = installDate[8:10]
		minutes = installDate[10:12]
		seconds = installDate[12:14]

		return "%s.%s.%s %s:%s:%s" % (day, month, year, hours, minutes, seconds)

	@staticmethod
	def checkForTotal(input):
		if (input == "_Total"):
			return "Total"
		else:
			return input

	@staticmethod
	def placeholder():
		pass