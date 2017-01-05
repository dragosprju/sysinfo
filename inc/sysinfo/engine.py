class Engine(object):

	def __init__(self, window, tab):

		self.window = window
		self.tab = tab
		self.bodies = []
		self.functions = []

	def initialize(self):
		pass

	def loadPredefined(self):
		pass

	def createRow(self, header, function):
		body = self.tab.addRow(header, "...")
		self.bodies.append(body)
		self.functions.append(function)

	def createSeparator(self):
		self.tab.addSeparator()