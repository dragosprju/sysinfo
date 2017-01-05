from Tkinter import *

from ttk import Notebook

import sys
sys.path.append('..')
from tab import *

WIDTH = 475
HEIGHT = 425

class Window(Frame):
  
	def __init__(self, parent):
		Frame.__init__(self, parent)   
		self.parent = parent        
		self.initUI()
	
	def initUI(self):
		self.parent.geometry(str(WIDTH) + "x" + str(HEIGHT))
		self.parent.resizable(1,1)

		self.pack(expand=Y, fill=BOTH, padx=6, pady=6)

		notebook = Notebook(self)
		notebook.pack(fill=BOTH, expand=Y)

		self.tabOne = Tab(notebook)
		self.tabTwo = Tab(notebook)

		notebook.add(self.tabOne, text="Information")
		notebook.add(self.tabTwo, text="Statistics")

	def getTab(self, which):
		if which == 1:
			return self.tabOne
		elif which == 2:
			return self.tabTwo
		else:
			return None