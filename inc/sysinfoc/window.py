from Tkinter import *
from ttk import Notebook

import sys
sys.path.append('..')
from tab import *

WIDTHC = 650
HEIGHTC = 425

class Window(Frame):
  
	def __init__(self, parent):
		Frame.__init__(self, parent)   
		self.parent = parent        
		self.initUI()
	
	def initUI(self):
		self.parent.geometry(str(WIDTHC) + "x" + str(HEIGHTC))
		self.parent.resizable(1,1)

		self.pack(expand=Y, fill=BOTH, padx=6, pady=6)

		notebook = Notebook(self)
		notebook.pack(fill=BOTH, expand=Y)

		self.summaryTab = Tab(notebook, 4, True)
		self.detailsTab = Tab(notebook, 3, False)
		self.averageStatsTab = Tab(notebook, 6, True)
		self.currentStatsTab = Tab(notebook, 3, False)
		self.processorUsageTab = Tab(notebook, 3, False) 

		notebook.add(self.summaryTab, text="Summary")
		notebook.add(self.detailsTab, text="Details")
		notebook.add(self.averageStatsTab, text="Average Stats")
		notebook.add(self.currentStatsTab, text="Current Stats")
		notebook.add(self.processorUsageTab, text="Processor Usage")

	def getTab(self, which):
		if which == 1:
			return self.summaryTab
		elif which == 2:
			return self.detailsTab
		elif which == 3:
			return self.averageStatsTab
		elif which == 4:
			return self.currentStatsTab
		elif which == 5:
			return self.processorUsageTab
		else:
			return None